#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8
from config import *
from work import *

@bot.message_handler(content_types=["group_chat_created", "supergroup_chat_created"])
def groupChatCreated(message):
	start(message)

@bot.message_handler(content_types=["new_chat_members"])
def newChatMember(message):
	if (message.chat.type == 'group' or message.chat.type == 'supergroup') and (message.new_chat_member.id == bot.get_me().id): #or find_all_by_key(message.new_chat_members, "id", bot.get_me().id)):
		start(message)

@bot.message_handler(content_types=['text', 'voice', 'video', 'photo', 'document'])
def AllHandler(message):
	if message.chat.type == 'private':
		addUser(message.from_user.id)
	if (message.chat.type == 'supergroup' or message.chat.type == 'group') and gameIsExisted(message.chat.id) == 0 and getSpyID(message.chat.id) != None and (message.from_user.id,) not in getGamersByGroupId(message.chat.id):
		try:
			bot.delete_message(message.chat.id, message.message_id)
		except Exception:
			pass
		if message.chat.type == 'supergroup':
			try:
				bot.restrict_chat_member(message.chat.id, message.from_user.id, message.date + 30, can_send_messages=False, can_send_media_messages=False, can_send_other_messages=False)
			except Exception:
				pass
	elif message.text == '/start' or message.text == '/start@findspy_bot':
		start(message)
	elif message.text == '/end' or message.text == '/end@findspy_bot':
		end(message)
	elif message.text == '/startpoll@findspy_bot' or message.text == '/startpoll':
		startPollNow(message)
	elif message.text == '/rules' or message.text == '/rules@findspy_bot':
		rules(message)
	elif message.text == '/game' or message.text == '/game@findspy_bot':
		game(message)
	elif message.text == '/answer' or message.text == '/answer@findspy_bot':
		answer(message)
	elif message.text == '/admword' and message.chat.type == 'private' and isMyAdmin(message.from_user.id) and getGroupbByUsersIDInGame(message.chat.id) != None:
		bot.send_message(message.chat.id, getGroupsWord(getGroupbByUsersIDInGame(message.chat.id)))
	elif message.text == '/settings' or message.text == '/settings@findspy_bot':
		settings(message)
	elif message.text == '/help' or message.text == '/help@findspy_bot':
		help(message)
	elif message.text == '/leave' or message.text == '/leave@findspy_bot':
		leave(message)
	elif message.text == '/offlinegame' or message.text == '/offlinegame@findspy_bot':
		offlineGame(message)
	elif message.text == '/admpanel' and isMyAdmin(message.from_user.id) and message.chat.type == 'private':
		adminPanel(message)

def adminPanel(message, message_id=0):
	key = types.InlineKeyboardMarkup()
	key.add(types.InlineKeyboardButton("Actual word", callback_data="admword"))
	key.add(types.InlineKeyboardButton("Get groups", callback_data="getgroups"))
	key.add(types.InlineKeyboardButton("Add word", callback_data="addword"))
	key.add(types.InlineKeyboardButton("Show words", callback_data="showords"))
	key.add(types.InlineKeyboardButton("Delete word", callback_data="delword"))
	key.add(types.InlineKeyboardButton("Number of users", callback_data="countgamers"))
	key.add(types.InlineKeyboardButton("GameRoom", callback_data="updategameroom"))
	key.add(types.InlineKeyboardButton("Mailing", callback_data="admrass"))
	if message_id == 0:
		bot.send_message(message.chat.id, "<b>Admin panel</b>", parse_mode='html', reply_markup=key)
	else:
		try:
			bot.edit_message_text("<b>Admin panel</b>", message.chat.id, message_id, parse_mode='html', reply_markup=key)
		except Exception:
			pass

# @bot.message_handler(commands=['start'])
def start(message):
	if message.chat.type == 'supergroup' or message.chat.type == 'group':
		key = types.InlineKeyboardMarkup()
		if addGroup(message.chat.id) == 0:
			admSettings(message.chat.id)
		if checkPermissions(message.chat.id) == 0:
			key.add(types.InlineKeyboardButton("Начать игру", callback_data="startgame"))
			bot.send_message(message.chat.id, "<b>Все готово для того, чтобы начинать.</b>\nЖми на кнопку и стартуем!", reply_markup=key, parse_mode='html')
		else:
			key.add(types.InlineKeyboardButton("✔️", callback_data="permissions"))
			key.add(types.InlineKeyboardButton("Познакомимся?", url="t.me/findspy_bot"))
			bot.send_message(message.chat.id, "Привет! Я бот-ведущий игры 🕵️‍♂️Шпион.\n* Для начала игры выдай мне права администратора!\n* А чтобы я мог с тобой общаться, переходи в личный диалог со мной и жми \"Старт\".", reply_markup=key)
	elif message.chat.type == 'private':
		key = types.InlineKeyboardMarkup()
		key.add(types.InlineKeyboardButton("Добавить игру в свою беседу", url="tg://resolve?domain=findspy_bot&startgroup="))
		if addUser(message.from_user.id) == 0:
			bot.send_message(message.chat.id, "Привет! Я бот-ведущий игры 🕵️‍♂️Шпион. Рад, что мы теперь знакомы!", reply_markup=key)
		else:
			bot.send_message(message.chat.id, "Привет! Я бот-ведущий игры 🕵️‍♂️Шпион.", reply_markup=key)
		help(message)

# @bot.message_handler(commands=['help'])
def help(message):
	key = types.InlineKeyboardMarkup()
	if message.chat.type == 'private':
		key.add(types.InlineKeyboardButton("Обратная связь", callback_data="feedback"))
	bot.send_message(message.chat.id, '<b>Что нужно для начала?￼</b>\n* Добавить меня в актуальную беседу\n* Выдать права администратора\n* Начать игру /game\n\nДля участия в первый раз каждый, желающий играть, должен перейти ко мне в диалог и нажать "Старт".\nПодробные правила можно игры можно найти по команде /rules.\n\nИзменить количество игроков, длительность игры и многое другое может только создатель беседы в личном диалоге по команде /settings.', parse_mode='html', reply_markup=key)

# @bot.message_handler(commands=['startpoll'])
def startPollNow(message):
	if (message.chat.type == 'supergroup'  or message.chat.type == 'group') and gameIsExisted(message.chat.id) == 0 and getPollStatus(message.chat.id) == 0 and getSpyID(message.chat.id) != None:
		individualPoll(message.chat.id)
		t = threading.Thread(target=whenToEndPoll, name="Thread2Poll{}".format(str(message.chat.id), args=(message.chat.id, getTimeAfterPoll(message.chat.id))))
		t.start()
	elif message.chat.type == 'private':
		bot.send_message(message.chat.id, "Команда используется только в беседе во время игры.")

# @bot.message_handler(commands=['game'])
def game(message):
	if (message.chat.type == 'supergroup'  or message.chat.type == 'group') and gameIsExisted(message.chat.id) == 1 and checkPermissions(message.chat.id) == 0 and getInviteID(message.chat.id) == None:
		key = types.InlineKeyboardMarkup()
		try:
			bot.send_message(message.from_user.id, 'Вы создали приглашение в {}'.format(bot.get_chat(message.chat.id).title))
		except Exception:
			key.add(types.InlineKeyboardButton("Возобновим?", url="t.me/findspy_bot"))
			bot.send_message(message.chat.id, "<a href='tg://user?id={}'>{}</a> приостановил личный диалог.".format(message.from_user.id, message.from_user.first_name), parse_mode='html', reply_markup=key)
			return
		key.add(types.InlineKeyboardButton("Присоединиться", callback_data='connect'))
		invite_message = bot.send_message(message.chat.id, "Жми на кнопку, чтобы присоединиться к игре!\n\n    Игроки: <a href='tg://user?id={}'>{}</a>".format(message.from_user.id, message.from_user.first_name), parse_mode="html", reply_markup=key)
		try:
			bot.pin_chat_message(invite_message.chat.id, invite_message.message_id)
		except:
			pass
		inviteID(invite_message.chat.id, invite_message.message_id)
		if newGame(message.chat.id, message.from_user.id, message.from_user.first_name) == 2:
			btn = types.InlineKeyboardMarkup()
			btn.add(types.InlineKeyboardButton("Познакомимся?", url="t.me/findspy_bot"))
			bot.send_message(message.chat.id, "<a href='tg://user?id={}'>{}</a> все еще не перешел в личный диалог!".format(message.from_user.id, message.from_user.first_name), parse_mode='html', reply_markup=btn)
			return
		t = threading.Thread(target=whenToEndInvite, name="Thread4Invite{}".format(str(message.chat.id)), args=(message.chat.id, getInviteTime(message.chat.id)))###################################################################################################################
		t.start()
		t.join()
		t._delete()
		if gameIsExisted(message.chat.id) == 0 and getSpyID(message.chat.id) == None:
			gameStarting(message.chat.id)
	elif message.chat.type == 'private':
		offlineGame(message)
	elif checkPermissions(message.chat.id) == 1:
		key = types.InlineKeyboardMarkup()
		key.add(types.InlineKeyboardButton("✔️", callback_data="permissions"))
		bot.send_message(message.chat.id, "<b>Похоже я еще не получил права администратора.</b>\n* Удалять сообщения\n* Блокировать пользователей\n* Закреплять сообщения", parse_mode='html', reply_markup=key)

# @bot.message_handler(commands=['end'])
def end(message):
	if (message.chat.type == 'supergroup'  or message.chat.type == 'group') and gameIsExisted(message.chat.id) == 0 and (message.from_user.id in getAdmins(message.chat.id) or isMyAdmin(message.from_user.id)):
		bot.send_message(message.chat.id, "Игра окончена!")
		endGame(message.chat.id)
	elif message.chat.type == 'private':
		bot.send_message(message.chat.id, "Команда используется только в беседе во время игры.")

# @bot.message_handler(commands=['rules'])
def rules(message):
	# bot.send_message(message.chat.id, '<b>Правила</b>\nВ игре участвуют местные и шпионы.\nЦель игры:\n* Местным необходимо выявить шпиона.\n* Шпиону необходимо определить локацию.\nВ начале игры в личном диалоге местным будет сообщена локация, Шпиону – нет.\nЗадавайте друг другу вопросы, связанные с данной локацией, чтобы вычислить шпиона. Например: "Когда ты был последний раз в этом месте?"\nПраво задать следующий вопрос переходит отвечающему.\nВы шпион и догадываетесь о какой локации идет речь? Переходите ко мне в личный диалог, жмите /answer и отправляйте ваше слово.\nЕсли же вы местный и сочли чьи-то ответы слишком подозрительными, то вы можете дождаться голосования и выбрать подозреваемого, либо начать голосование прямо сейчас с помощью команды /startpoll.\nИ помните, одна игра – одно голосование!\n\nИзменить количество игроков и время игры может только создатель беседы в личном диалоге по команде /settings.', parse_mode='html')
	bot.send_message(message.chat.id, '<b>Правила</b>\nВ этой игре вашу компанию будет заносить в разные места. Вы можете оказаться работниками отеля или универмага, стать участниками, улететь в космос или очутиться на пиратском корабле. Границы широки!\nЦель шпиона – угадать место.\nЦель остальных – раскрыть шпиона.\nВам нужно будет расспрашивать друг друга о месте, в которое попали, пытаясь вычислить спрятавшегося среди соперников шпиона. Он единственный, кто понятия не имеет где вы все находитесь. Но при этом он будет слышать все ваши переговоры и иногда участвовать в них. Если ему удастся вычислить локацию прежде чем его раскроют – он победил!\n\nЗови друзей, играйте, обвиняйте друг друга, несите чушь и весело проводите время в игре \"Шпион\".', parse_mode='html')

# def admword(message):
# 	if isMyAdmin(message.from_user.id) and getGroupbByUsersIDInGame(message.chat.id) != None:
# 		bot.send_message(message.chat.id, getGroupsWord(getGroupbByUsersIDInGame(message.chat.id)))

def addword(message):
	if isMyAdmin(message.from_user.id):
		conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
		cursor = conn.cursor()
		cursor.execute("INSERT INTO words (word) VALUES ('%s')" % (message.text))
		conn.commit()
		conn.close()
		bot.send_message(message.from_user.id, "Добавлено!")

def leave(message):
	if gameIsExisted(message.chat.id) == 0 and (message.chat.type == 'supergroup' or message.chat.type == 'group'):
		spyID = getSpyID(message.chat.id)
		if spyID == message.from_user.id:
			bot.send_message(message.chat.id, "<b>Игра завершена.</b>\n* Шпион <a href='tg://user?id={}'>{}</a> покидает игру.".format(message.from_user.id, message.from_user.first_name), parse_mode='html')
			endGame(message.chat.id)
		elif spyID == None and len(getGamersByGroupId(message.chat.id)) > 1:
			conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
			cursor = conn.cursor()
			cursor.execute("DELETE FROM gameroom WHERE userID = '%d'" % (message.from_user.id))
			conn.commit()
			conn.close()
			editInvite(message.chat.id)
			bot.send_message(message.chat.id, "* <a href='tg://user?id={}'>{}</a> покидает игру.".format(message.from_user.id, message.from_user.first_name), parse_mode='html')
		elif spyID == None and len(getGamersByGroupId(message.chat.id)) == 1:
			endGame(message.chat.id)
			bot.send_message(message.chat.id, "<b>Игра завершена.</b>\n* <a href='tg://user?id={}'>{}</a> покидает игру.".format(message.from_user.id, message.from_user.first_name), parse_mode='html')
		elif spyID != message.from_user.id and len(getGamersByGroupId(message.chat.id)) == 4:
			bot.send_message(message.chat.id, "<b>Недостаточно игроков для продолжения игры.</b>\n* <a href='tg://user?id={}'>{}</a> покидает игру.".format(message.from_user.id, message.from_user.first_name), parse_mode='html')
			endGame(message.chat.id)
		elif spyID != message.from_user.id and len(getGamersByGroupId(message.chat.id)) > 4:
			conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
			cursor = conn.cursor()
			cursor.execute("DELETE FROM gameRoom WHERE userID = '%d'" % (message.from_user.id))
			# cursor.execute("DELETE FROM pieceID WHERE userID = '%d'" % (message.from_user.id))
			cursor.execute("DELETE FROM poll WHERE userID = '%d'" % (message.from_user.id))
			conn.commit()
			conn.close()
			bot.send_message(message.chat.id, "* <a href='tg://user?id={}'>{}</a> покидает игру.".format(message.from_user.id, message.from_user.first_name), parse_mode='html')
	elif message.chat.type == 'private':
		bot.send_message(message.chat.id, "Команда используется только в беседе во время игры.")

def delword(message):
	if isMyAdmin(message.from_user.id):
		conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
		cursor = conn.cursor()
		cursor.execute("SELECT word FROM words WHERE word = '%s'" % (message.text))
		row = cursor.fetchone()
		if row == None:
			bot.send_message(message.from_user.id, "Нет такого слова!")
			conn.close()
		else:
			cursor.execute("DELETE FROM words WHERE word = '%s'" % (message.text))
			conn.commit()
			conn.close()
			bot.send_message(message.from_user.id, "Удалено!")

# @bot.message_handler(commands=['answer'])
def answer(message):
	group_id = getGroupbByUsersIDInGame(message.from_user.id)
	if message.chat.type == 'private' and gameIsExisted(group_id) == 0 and getSpyID(group_id) != None and getSpyID(group_id) == message.from_user.id:
		bot.send_message(message.from_user.id, "Можешь написать мне слово, а я его проверю!")
		bot.register_next_step_handler(message, checkingAnswer, group_id)
	elif message.chat.type == 'group' or message.chat.type == 'supergroup':
		try:
			bot.delete_message(message.chat.id, message.message_id)
		except Exception:
			pass
		bot.send_message(message.chat.id, "Команда /answer используется только в личном чате.")
	else:
		bot.send_message(message.from_user.id, "Ты не шпион или игра еще не началась!")


def settings(message):
	if message.chat.type == 'private' and isCreatorForSettings(message.chat.id):
		key = types.InlineKeyboardMarkup()
		for i in getCreatorsGroups(message.chat.id):
			key.add(types.InlineKeyboardButton(text=bot.get_chat(i[0]).title, callback_data=str(i[0]) + "settings"))
		bot.send_message(message.chat.id, "Выберите чат", reply_markup=key)
	elif message.chat.type == 'private':
		bot.send_message(message.chat.id, "Вы не являетесь создателем какой-либо беседы!")
	else:
		bot.send_message(message.chat.id, "Команда используется только создателем беседы в личном чате!")

def admrass(message):
	if message.text == "/cancel":
		return
	bot.send_message(message.from_user.id, "Присылай кнопки в формате:\n\nкнопка1 ➖ callback_data1\nкнопка1 ➖ callback_data1\n\n/cancel для отмены")
	bot.register_next_step_handler(message, getMessageCallback, message.text)

# @bot.message_handler(commands=['offlinegame'])
def offlineGame(message):
	if message.chat.type == 'private':
		conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
		cursor = conn.cursor()
		cursor.execute("SELECT * FROM offlineGame WHERE userID = '%d'" % (message.chat.id))
		if cursor.fetchone() != None:
			conn.close()
			key = types.InlineKeyboardMarkup()
			key.add(types.InlineKeyboardButton("Старт", callback_data="edittooffline"))
			# key.add(types.InlineKeyboardButton("Отмена", callback_data="delete_message"))
			old_message = bot.send_message(message.chat.id, "<b>Оффлайн игра</b>\nНачнем новую игру?", reply_markup=key, parse_mode='html')
		else:
			conn.close()
			old_message = bot.send_message(message.chat.id, "<b>Оффлайн игра</b>\nДля начала игры пришли мне количество игроков.\n\n/cancel для отмены.", parse_mode='html')
			bot.register_next_step_handler(message, numGamersForOFflineGame, old_message.chat.id, old_message.message_id)
	else:
		bot.send_message(message.chat.id, "Команда используется только в личном чате.")

@bot.callback_query_handler(func=lambda c:True)
def inline(c):
	print(c.data)
	if c.data == 'permissions':
		key = types.InlineKeyboardMarkup()
		if checkPermissions(c.message.chat.id) == 0:
			key = types.InlineKeyboardMarkup()
			key.add(types.InlineKeyboardButton("Начать игру", callback_data="startgame"))
			bot.send_message(c.message.chat.id, "<b>Все готово для того, чтобы начинать.</b>\nЖми на кнопку и стартуем!", reply_markup=key, parse_mode='html')
		else:
			key.add(types.InlineKeyboardButton("✔️", callback_data="permissions"))
			bot.send_message(c.message.chat.id, "<b>Похоже я еще не получил права администратора.</b>\n* Удалять сообщения\n* Блокировать пользователей\n* Закреплять сообщения", parse_mode='html', reply_markup=key)
	elif c.data == 'connect':
		if checkPermissions(c.message.chat.id) == 0:
			addReturn = addUserToGame(c.message.chat.id, c.from_user.id, c.from_user.first_name)
			if addReturn == 3:
				try:
					bot.delete_message(c.message.chat.id, c.message.message_id)
				except Exception:
					pass
				return
			elif addReturn == 1:
				return
			elif addReturn == 2:
				key = types.InlineKeyboardMarkup()
				key.add(types.InlineKeyboardButton("Познакомимся?", url="t.me/findspy_bot"))
				bot.send_message(c.message.chat.id, "<a href='tg://user?id={}'>{}</a> все еще не перешел в личный диалогю".format(c.from_user.id, c.from_user.first_name), parse_mode='html', reply_markup=key)
				return
			elif addReturn == 4:
				key = types.InlineKeyboardMarkup()
				key.add(types.InlineKeyboardButton("Возобновим?", url="t.me/findspy_bot"))
				bot.send_message(c.message.chat.id, "<a href='tg://user?id={}'>{}</a> приостановил личный диалог.".format(c.from_user.id, c.from_user.first_name), parse_mode='html', reply_markup=key)
				return
			editInvite(c.message.chat.id)
		else:
			key = types.InlineKeyboardMarkup()
			key.add(types.InlineKeyboardButton("✔️", callback_data="permissions"))
			bot.send_message(c.message.chat.id, "<b>Для продолжения игры выдайте мне права администратора.</b>\n* Удалять сообщения\n* Блокировать пользователей\n* Закреплять сообщения", parse_mode='html', reply_markup=key)
			try:
				bot.delete_message(c.message.chat.id, getInviteID(c.message.chat.id))
			except Exception:
				pass
			endGame(c.message.chat.id)
	elif c.data == "groupsettings":
		changeToSettings("Выберите", c.message.chat.id, c.message.message_id)
	elif c.data == "feedback":
		bot.send_message(c.message.chat.id, "Напишите мне сообщение, я передам его администратору.\n\n/cancel для отмены.")
		bot.register_next_step_handler(c.message, feedback)
	elif c.data == "updategameroom":
		showgameroom(c.message, c.message.message_id)
	elif c.data == "skipinvite":
		gameStarting(c.message.chat.id)
	elif c.data == "edittooffline":
		conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
		cursor = conn.cursor()
		cursor.execute("DELETE FROM offlineGame WHERE userID = '%d'" % (c.message.chat.id))
		conn.commit()
		conn.close()
		try:
			bot.edit_message_text("<b>Оффлайн игра</b>\nВведите количество игроков для начала игры.\n\n/cancel для отмены.", c.message.chat.id, c.message.message_id, parse_mode='html')
		except Exception:
			pass
		bot.register_next_step_handler(c.message, numGamersForOFflineGame, c.message.chat.id, c.message.message_id)
	elif c.data == "delete_message":
		try:
			bot.delete_message(c.message.chat.id, c.message.message_id)
		except Exception:
			pass
	elif c.data == "rolesgiven":
		conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
		cursor = conn.cursor()
		cursor.execute("UPDATE offlineGame SET startTime = '%d' WHERE userID = '%d'" % (c.message.date, c.message.chat.id))
		conn.commit()
		cursor.execute("SELECT time FROM offlineGame WHERE userID = '%d'" % (c.message.chat.id))
		endTime = cursor.fetchone()[0]
		conn.close()
		key = types.InlineKeyboardMarkup()
		key.add(types.InlineKeyboardButton("Закончить игру", callback_data="endofflinegame"))
		try:
			bot.edit_message_text("<b>Оффлайн игра</b>\nНачинайте задавать вопросы!\nУспейте вычислить Шпиона прежде, чем истечет время, иначе он победит.", c.message.chat.id, c.message.message_id, reply_markup=key, parse_mode='html')
		except Exception:
			pass
		t = threading.Thread(target=whenToEndOfflineGame, name="Threadoffline{}".format(str(c.message.chat.id)), args=(c.message.chat.id, c.message.date, endTime))###################################################################################################################
		t.start()
		t.join()
		offlineGameEnd(c.message.chat.id, c.message.message_id, c.message.date)
	elif c.data == "endofflinegame":
		offlineGameEnd(c.message.chat.id, c.message.message_id, None)
	elif c.data == 'getgroups':
		conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
		cursor = conn.cursor()
		cursor.execute("SELECT COUNT(*) FROM groups")
		groups = cursor.fetchone()
		cursor.execute("SELECT grpID FROM groups")
		word = cursor.fetchone()
		text = ""
		while word != None:
			try:
				text += (bot.get_chat(word[0]).title + "\n")
			except Exception:
				text += "no title\n"
			word = cursor.fetchone()
		conn.close()
		bot.send_message(c.message.chat.id, "<b>Всего групп – {}</b>\n{}".format(groups[0], text), parse_mode="html")
	elif c.data == 'addword':
		bot.send_message(c.message.chat.id, "Присылай новое слово!")
		bot.register_next_step_handler(c.message, addword)
	elif c.data == 'showords':
		conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
		cursor = conn.cursor()
		cursor.execute("SELECT word FROM words")
		word = cursor.fetchone()
		text = ""
		while word != None:
			text += (word[0] + "\n")
			word = cursor.fetchone()
		conn.close()
		bot.send_message(c.message.chat.id, "<b>Список слов\n</b>" + text, parse_mode="html")
	elif c.data == 'delword':
		bot.send_message(c.message.chat.id, "Присылай слово", parse_mode="html")
		bot.register_next_step_handler(c.message, delword)
	elif c.data == 'countgamers':
		conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
		cursor = conn.cursor()
		cursor.execute("SELECT COUNT(*) FROM users")
		gamers = cursor.fetchone()
		conn.close()
		bot.send_message(c.message.chat.id, "<b>На данный момент в базе – " + str(gamers[0]) + " человек(а)</b>", parse_mode="html")
	elif c.data == 'admrass':
		bot.send_message(c.message.chat.id, "Присылай сообщение для пользователей\n/cancel для отмены")
		bot.register_next_step_handler(c.message, admrass)
	elif c.data == 'admpanel':
		adminPanel(c.message, c.message.message_id)
	elif c.data == "startgame":
		try:
			bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=None)
		except Exception:
			pass
		try:
			bot.delete_message(c.message.chat.id, c.message.message_id)
		except Exception:
			pass
		if getInviteID(c.message.chat.id) == None:
			c.message.from_user = c.from_user
			game(c.message)
	elif c.data == 'answerfromspy':
		group_id = getGroupbByUsersIDInGame(c.from_user.id)
		if c.message.chat.type == 'private' and gameIsExisted(group_id) == 0 and getSpyID(group_id) != None and getSpyID(group_id) == c.from_user.id:
			bot.send_message(c.from_user.id, "Можешь написать мне слово, а я его проверю!")
			bot.register_next_step_handler(c.message, checkingAnswer, group_id)
		else:
			bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=None)
	elif c.data == "newwordfromuser":
		bot.send_message(c.from_user.id, "Присылай новую локацию, а я обсужу ее добавление с администратором.\n\n/cancel для отмены")
		bot.register_next_step_handler(c.message, checkNewWord)
	elif "_addingword" in c.data:
		word = c.data.split('_')[0]
		if isMyAdmin(c.from_user.id):
			conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
			try:
				cursor = conn.cursor()
				cursor.execute("INSERT INTO words (word) VALUES ('%s')" % (word))
				conn.commit()
				bot.send_message(c.from_user.id, "Добавлено!")
			except Exception as e:
				bot.send_message(144589481, str(e))
			conn.close()
	elif "waitrole" in c.data:
		id = getNumberFromCall(c.data, 'w')
		key = types.InlineKeyboardMarkup()
		key.add(types.InlineKeyboardButton("Готов", callback_data=str(id)+"offlinerole"))
		try:
			bot.edit_message_text("Держи телефон так, чтобы твои друзья не видели место, в которое мы сейчас переместимся.", c.message.chat.id, c.message.message_id, reply_markup=key, parse_mode='html')
		except Exception:
			pass
	elif "offlinerole" in c.data:
		startOfflineGame(c.message.chat.id, c.message.message_id, getNumberFromCall(c.data, "o"))
	elif "offlinetime" in c.data:
		offlineTime = getNumberFromCall(c.data, 'o')
		conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
		cursor = conn.cursor()
		cursor.execute("UPDATE offlineGame SET time = '%d' WHERE userID = '%d'" % (offlineTime * 60, c.message.chat.id))
		conn.commit()
		conn.close()
		setOfflineSpy(c.message.chat.id, c.message.message_id)
	elif "answer2user" in c.data:
		bot.send_message(c.message.chat.id, "Ответ пользователю.\n\n/cancel для отмены.")
		bot.register_next_step_handler(c.message, answerToUser, c.data)
	elif "settings" in c.data:
		editToGroupSettings(c.data, c.message.chat.id, c.message.message_id)
	elif "poll" in c.data:
		try:
			bot.edit_message_text("Вы сделали свой выбор!", c.message.chat.id, c.message.message_id)
		except Exception:
			pass
		finally:
			pollHandler(getGroupbByUsersIDInGame(c.from_user.id), c.from_user.id, c.data)
	elif "maxgamers" in c.data:
		changeMaxGamers(c.message, c.data, c.message.chat.id, c.message.message_id)
	elif "inviting" in c.data:
		changeInviteTime(c.message, c.data, c.message.chat.id, c.message.message_id)
	elif "chinvite" in c.data:
		newTime = getNumberFromCall(c.data, "_")
		group_id = getNumberFromLetterToCall(c.data, "_", "c")
		conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
		cursor = conn.cursor()
		cursor.execute("UPDATE settings SET inviteTime = '%d' WHERE grpID = '%d'" % (int(newTime), group_id))
		conn.commit()
		conn.close()
		changeToSettings("Длительность регистрации изменена.", c.message.chat.id, c.message.message_id)
	elif "chtime" in c.data:
		newTime = getNumberFromCall(c.data, "_")
		group_id = getNumberFromLetterToCall(c.data, "_", "c")
		conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
		cursor = conn.cursor()
		cursor.execute("UPDATE settings SET time = '%d' WHERE grpID = '%d'" % (int(newTime), group_id))
		conn.commit()
		conn.close()
		changeToSettings("Длительность игры изменена.", c.message.chat.id, c.message.message_id)
	elif "time" in c.data:
		changeMaxTime(c.message, c.data, c.message.chat.id, c.message.message_id)
	elif "cleancache" in c.data:
		group_id = getNumberFromCall(c.data, "c")
		endGame(group_id)
		showgameroom(c.message, c.message.message_id)


bot.send_message(144589481, "polling restart")
try:
	bot.polling(none_stop=True)
except Exception as e:
	bot.send_message(144589481, e)
