from config import *

def dbConnect():
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	return conn

def getWord():
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT word FROM words ORDER BY RANDOM() LIMIT 1")
	word = cursor.fetchone()[0]
	conn.close()
	return word

def newGame(group_id, user_id, name):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT userID FROM gameRoom WHERE userID = '%d'" % (user_id))
	if cursor.fetchone() != None:
		conn.close()
		return 1
	cursor.execute("SELECT userID FROM users WHERE userID = '%d'" % (user_id))
	if cursor.fetchone() == None:
		conn.close()
		return 2
	numFromSettings = getNumberOfGamersByGroupIdFromSettings(group_id)
	gamersFromGameRoom = getGamersByGroupId(group_id)
	if numFromSettings != None and gamersFromGameRoom != None:
		if len(gamersFromGameRoom) == numFromSettings:
			conn.close()
			return
	cursor.execute("INSERT INTO gameRoom (grpID,userID, name) VALUES ('%d','%d', '%s')" % (group_id, user_id, name))
	conn.commit()
	conn.close()
	return 0

def addUserToGame(group_id, user_id, name):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT grpID FROM gameRoom WHERE grpID = '%d'" % (group_id))
	if cursor.fetchone() == None:
		conn.close()
		return 3
	cursor.execute("SELECT userID FROM gameRoom WHERE userID = '%d'" % (user_id))
	if cursor.fetchone() != None:
		conn.close()
		return 1
	cursor.execute("SELECT userID FROM users WHERE userID = '%d'" % (user_id))
	if cursor.fetchone() == None:
		conn.close()
		return 2
	numFromSettings = getNumberOfGamersByGroupIdFromSettings(group_id)
	gamersFromGameRoom = getGamersByGroupId(group_id)
	if numFromSettings != None and gamersFromGameRoom != None:
		if len(gamersFromGameRoom) == numFromSettings:
			conn.close()
			return
	try:
		bot.send_message(user_id, 'Вы присоединились к игре в {}'.format(bot.get_chat(group_id).title))
	except Exception:
		return 4
	cursor.execute("INSERT INTO gameRoom (grpID,userID, name) VALUES ('%d','%d', '%s')" % (group_id, user_id, name))
	conn.commit()
	conn.close()
	return 0

def gameIsExisted(group_id):
	if group_id == None:
		return
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM gameRoom WHERE grpID = '%d'" % (group_id))
	if cursor.fetchone() != None:
		conn.close()
		return 0
	conn.close()
	return 1

def addUser(user_id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT userID FROM users WHERE userID = '%d'" % (user_id))
	row = cursor.fetchone()
	if row != None:
		conn.close()
		return 1
	cursor.execute("INSERT INTO users (userID) VALUES ('%d')" % (user_id))
	conn.commit()
	conn.close()
	return 0

def addGroup(group_id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT grpID FROM groups WHERE grpID = '%d'" % (group_id))
	if cursor.fetchone() != None:
		conn.close()
		return 1
	cursor.execute("INSERT INTO groups (grpID) VALUES ('%d')" % (group_id))
	conn.commit()
	conn.close()
	return 0

def givingRoles(group_id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT userID FROM gameRoom WHERE grpID = '%d'" % (group_id))
	row = cursor.fetchall()
	numOfGamers = len(row)
	if numOfGamers < 4:#####################################################################################
		conn.close()
		return 1
	randomNumber = random.randint(0, numOfGamers - 1)
	for i in row:
		if i[0] == row[randomNumber][0]:
			cursor.execute("UPDATE gameroom SET role = 1 WHERE userID = '%d'" % (i[0]))
			continue
		cursor.execute("UPDATE gameroom SET role = 0 WHERE userID = '%d'" % (i[0]))
	conn.commit()
	conn.close()
	return 0

def endGame(group_id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	try:
		bot.delete_message(group_id, getInviteID(group_id))
	except Exception:
		pass
	cursor.execute("DELETE FROM gameRoom WHERE grpID = '%d'" % (group_id))
	# cursor.execute("DELETE FROM pieceID WHERE grpID = '%d'" % (group_id))
	# cursor.execute("DELETE FROM spyID WHERE grpID = '%d'" % (group_id))
	cursor.execute("DELETE FROM messages WHERE grpID = '%d'" % (group_id))
	cursor.execute("DELETE FROM poll WHERE grpID = '%d'" % (group_id))
	cursor.execute("UPDATE groups SET word = NULL WHERE grpID = '%d'" % (group_id))
	# cursor.execute("DELETE FROM groupsWord WHERE grpID = '%d'" % (group_id))
	conn.commit()
	conn.close()

def admSettings(group_id):
	adms = bot.get_chat_administrators(group_id)
	for i in adms:
		if i.status == 'creator':
			conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
			cursor = conn.cursor()
			cursor.execute("INSERT INTO settings (grpID, userID, time, gamers, inviteTime) VALUES ('%d', '%d', '%d', '%d', '%d')" % (group_id, i.user.id, 5, 12, 45))
			conn.commit()
			conn.close()
			return 0
	return 1

def getCreator(group_id):
	adms = bot.get_chat_administrators(group_id)
	for i in adms:
		if i.status == 'creator':
			return i.user.id
	return 1

def getAdmins(group_id):
	adms = bot.get_chat_administrators(group_id)
	admins = []
	for i in adms:
		if i.status == 'administrator' or i.status == 'creator':
			admins.append(i.user.id)
	return admins

def checkPermissions(group_id):
	bot_id = bot.get_me().id
	botPermissions = bot.get_chat_member(group_id, bot_id)
	if botPermissions.can_restrict_members == True and botPermissions.can_delete_messages == True and botPermissions.can_pin_messages == True:
		# bot.send_message(group_id, "Отлично, права администратора получил. Для начала игры просто напишите /game")
		return 0
	else:
		return 1

def inviteID(group_id, invite_id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM messages WHERE grpID = '%d'" % (group_id))
	if cursor.fetchone() != None:
		return 1
	cursor.execute("INSERT INTO messages (grpID,inviteID,poll) VALUES ('%d','%d','%d')" % (group_id, invite_id, 0))
	conn.commit()
	conn.close()
	return 0

def getPollStatus(group_id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT poll FROM messages WHERE grpID = '%d'" % (group_id))
	row = cursor.fetchone()
	conn.close()
	if row != None:
		return row[0]

def getInviteID(group_id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT inviteID FROM messages WHERE grpID = '%d'" % (group_id))
	row = cursor.fetchone()
	if row != None:
		return row[0]

def getGamersByGroupId(group_id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT userID FROM gameRoom WHERE grpID = '%d'" % (group_id))
	row = cursor.fetchall()
	conn.close()
	return row

def getInviteTime(group_id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT inviteTime FROM settings WHERE grpID = '%d'" % (group_id))
	row = cursor.fetchone()
	conn.close()
	if row != None:
		return row[0]

def getNumberOfGamersByGroupIdFromSettings(group_id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT gamers FROM settings WHERE grpID = '%d'" % (group_id))
	row = cursor.fetchone()
	# print("grpid = " + str(group_id))
	conn.close()
	if row != None:
		return row[0]

def editInvite(group_id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	invite_id = getInviteID(group_id)
	key = types.InlineKeyboardMarkup()
	key.add(types.InlineKeyboardButton("Присоединиться", callback_data='connect'))
	text = "Жми на кнопку, чтобы присоединиться к игре!\n\n    Игроки: "
	cursor.execute("SELECT userID FROM gameRoom WHERE grpID = '%d'" % (group_id))
	row = cursor.fetchall()
	numOfGamers = len(row)
	if numOfGamers > 3:#####################################################################################
		key.add(types.InlineKeyboardButton("Начать игру", callback_data='skipinvite'))
	cursor.execute("SELECT * FROM gameRoom WHERE grpID = '%d'" % (group_id))
	row = cursor.fetchone()
	i = False
	while row != None:
		if i == False:
			i = True
			text += "<a href='tg://user?id={}'>{}</a>".format(row[1], row[2])
			row = cursor.fetchone()
			continue
		text += ", <a href='tg://user?id={}'>{}</a>".format(row[1], row[2])
		row = cursor.fetchone()
	conn.close()
	try:
		bot.edit_message_text(text, group_id, invite_id, parse_mode='html', reply_markup=key)
	except Exception:
		pass

def waitingUsers(group_id, timing):
	print("I wait")
	time.sleep(timing)
	# bot.delete_message(group_id, getInviteID(group_id))

def givingWords(group_id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT userID FROM gameroom WHERE grpID = '%d' and role = 0" % (group_id))
	gamers = cursor.fetchall()
	word = getWord()
	for i in gamers:
		bot.send_message(i[0], "<b>Ты – местный.</b>\nТвоя локация – {}.\nВсе игроки, кроме Шпиона, знают эту локацию. Задавай вопросы другим игрокам, чтобы вычислить Шпиона!".format(word), parse_mode='html')
	# cursor.execute("INSERT INTO groupsWord (grpID, word) VALUES ('%d', '%s')" % (group_id, word))
	cursor.execute("UPDATE groups SET word = '%s' WHERE grpID = '%d'" % (word, group_id))
	conn.commit()
	cursor.execute("SELECT userID FROM gameroom WHERE grpID = '%d' and role = 1" % (group_id))
	key = types.InlineKeyboardMarkup()
	key.add(types.InlineKeyboardButton("Проверить локацию", callback_data='answerfromspy'))
	bot.send_message(cursor.fetchone()[0], "<b>Ты – шпион!</b>\nПостарайся понять, о какой локации говорят местные и напиши ее мне после нажатия на кнопку.", parse_mode='html', reply_markup=key)
	conn.close()

def gameStarting(group_id):
	if getSpyID(group_id) != None:
		return
	first_invite_id = getInviteID(group_id)
	if gameIsExisted(group_id) == 0 and first_invite_id != None:
		# first_invite_id = getInviteID(group_id)
		try:
			bot.unpin_chat_message(group_id)
			bot.delete_message(group_id, first_invite_id)
		except Exception:
			pass
		if givingRoles(group_id) == 1:
			bot.send_message(group_id, "Недостаточно игроков для начала игры.")
			endGame(group_id)
			return 1
		givingWords(group_id)
		key = types.InlineKeyboardMarkup()
		key.add(types.InlineKeyboardButton("Локация здесь", url="t.me/findspy_bot"))
		random_user_id = whoIsTheFirst(group_id)
		sendGamers(group_id)
		bot.send_message(group_id, "Итак, первым поиски шпиона начинает <a href='tg://user?id={}'>{}</a>.\n\n<i>Выберите игрока и задайте ему вопрос, следующий вопрос задает предыдущий ответивший.</i>".format(random_user_id, getNameFromGameRoom(random_user_id)), reply_markup=key, parse_mode='html')
		t = threading.Thread(target=whenToStartPoll, name="Thread2Poll{}".format(str(group_id)), args=(group_id, getTimeForGame(group_id)))###################################################################################################################
		t.start()
		# t.join()
		# t = threading.Thread(target=whenToEndPoll, name="Thread2EndPoll{}".format(str(group_id), args=(group_id, 120)))###################################################################################################################
		# t = threading.Thread(target=whenToEndPoll, name="Thread2EndPoll{}".format(str(group_id)), args=(group_id, 120))###################################################################################################################
		# t.start()
	elif first_invite_id == None:
		bot.send_message(group_id, "Недостаточно игроков для начала игры.")
		endGame(group_id)
		return 1

def whoIsTheFirst(group_id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT userID FROM gameRoom WHERE grpID = '%d'" % (group_id))
	row = cursor.fetchall()
	numOfGamers = len(row)
	randomNumber = random.randint(0, numOfGamers - 1)
	conn.close()
	if row != None:
		return row[randomNumber][0]
	else:
		return None


def whenToEndPoll(group_id, endTime):
	timing = 0
	while timing <= endTime and len(pollResult(group_id)) < len(getGamersByGroupId(group_id)):
		time.sleep(3)
		timing += 3
		if endTime - timing == 28 or endTime - timing == 29 or endTime - timing == 30:
			bot.send_message(group_id, "<i>До окончания голосования осталось " + str(endTime-timing)+" секунд.</i>", parse_mode="html")
		print("whenToEndPoll")
	startGameResult(group_id)

def whenToStartPoll(group_id, endTime):
	timing = 0
	while timing <= endTime and gameIsExisted(group_id) == 0 and getPollStatus(group_id) != 1:
		time.sleep(3)
		timing += 3
		if endTime - timing == 28 or endTime - timing == 29 or endTime - timing == 30:
			bot.send_message(group_id, "<i>До начала голосования осталось " + str(endTime-timing)+" секунд.</i>", parse_mode="html")
		print("whenToStartPoll")
	individualPoll(group_id)
	t = threading.Thread(target=whenToEndPoll, name="Thread2EndPoll{}".format(str(group_id)), args=(group_id, getTimeAfterPoll(group_id)))###################################################################################################################
	t.start()

def whenToEndInvite(group_id, endTime):
	# print(endTime)
	# print(len(getGamersByGroupId(group_id)))
	# print(getNumberOfGamersByGroupIdFromSettings(group_id))
	# print(bot.get_chat_members_count(group_id) - 1)
	timing = 0
	while timing <= endTime and len(getGamersByGroupId(group_id)) <= getNumberOfGamersByGroupIdFromSettings(group_id) and len(getGamersByGroupId(group_id)) < bot.get_chat_members_count(group_id) - 1 and gameIsExisted(group_id) == 0 and getSpyID(group_id) == None:
		time.sleep(3)
		timing += 3
		if endTime - timing == 28 or endTime - timing == 29 or endTime - timing == 30:
			bot.send_message(group_id, "<i>До окончания регистрации осталось " + str(endTime-timing)+" секунд.</i>", parse_mode="html")
		print("whenToEndInvite")
	# gameStarting(group_id)

def individualPoll(group_id):
	if getPollStatus(group_id) == 1:
		return
	row = getGamersByGroupId(group_id)
	key = types.InlineKeyboardMarkup()
	for i in row:
		key = types.InlineKeyboardMarkup()
		for j in row:
			if i[0] == j[0]:
				continue
			key.add(types.InlineKeyboardButton(text=getNameFromGameRoom(j[0]), callback_data=str(j[0]) + "poll"))
		bot.send_message(i[0], "Выбери предполагаемого шпиона!\nПомни, у тебя только одна попытка.", reply_markup=key)
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("UPDATE messages SET poll = 1 WHERE grpID = '%d'" % (group_id))
	conn.commit()
	conn.close()
	group_key = types.InlineKeyboardMarkup()
	group_key.add(types.InlineKeyboardButton("Проголосовать", url="t.me/findspy_bot"))
	bot.send_message(group_id, "Вычислил предполагаемого шпиона? Проголосуй против него в личном чате со мной.", reply_markup=group_key)

def getNumberFromCall(data, letter):
	num = ""
	for i in data:
		if i == letter:
			break
		else:
			num += i
	return int(num)

def getNumberFromLetterToCall(data, fromLetter, toLetter):
	num = ""
	n = False
	for i in data:
		if n == False and i == fromLetter:
			n = True
		elif n == True:
			if i == toLetter:
				break
			else:
				num += i
	return int(num)

def pollResult(group_id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT onUserID FROM poll WHERE grpID = '%d'" % (group_id))
	row = cursor.fetchall()
	conn.close()
	return row

def maxdb(group_id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("Select onUserID, count(*) FROM poll WHERE grpID = ('%d') GROUP BY onUserID" % (group_id))
	row = cursor.fetchall()
	conn.close()
	maxPolls = 0
	pollUsers = []
	for i in row:
		if i[1] > maxPolls:
			maxPolls = i[1]
	for i in row:
		if i[1] == maxPolls:
			pollUsers.append(i[0])
	return pollUsers

def pollHandler(group_id, user_id, poll_data):
	userPoll = getNumberFromCall(poll_data, 'p')
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT whoUserID FROM poll WHERE whoUserID = '%d'" % (user_id))
	row = cursor.fetchone()
	if row != None:
		cursor.execute("UPDATE poll SET onUserID = '%d' WHERE whoUserID = '%d'" % (userPoll,user_id))
	else:
		bot.send_message(group_id, "<a href='tg://user?id={}'>{}</a> сделал свой выбор.".format(user_id, getNameFromGameRoom(user_id)), parse_mode='html')
		cursor.execute("INSERT INTO poll (grpID,whoUserID,onUserID) VALUES ('%d','%d', '%d')" % (group_id, user_id, userPoll))
	conn.commit()
	conn.close()
	if len(pollResult(group_id)) == len(getGamersByGroupId(group_id)):
		startGameResult(group_id)

def getSpyID(group_id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT userID FROM gameroom WHERE grpID = '%d' and role = 1" % (group_id))
	row = cursor.fetchone()
	conn.close()
	if row != None:
		return row[0]

def isSpy(group_id, user_id):
	if getSpyID(group_id) == user_id:
		return user_id

def startGameResult(group_id):
	if gameIsExisted(group_id) != 0:
		return
	row = maxdb(group_id)
	realSpy = getSpyID(group_id)
	word = getGroupsWord(group_id)
	if len(row) > 1:
		randomNumber = random.randint(1, len(row))
		spy = isSpy(group_id, row[randomNumber - 1])
		if spy == None:
			bot.send_message(group_id, "<b>Шпион не был обнаружен!</b>\n\n    Место: {}\n\n    Шпион: <a href='tg://user?id={}'>{}</a>.".format(word, realSpy, getNameFromGameRoom(realSpy)), parse_mode='html')
		else:
			bot.send_message(group_id, "<b>Поздравляю, вы нашли шпиона!</b>\n\n    Место: {}\n\n    Шпион: <a href='tg://user?id={}'>{}</a>.".format(word, realSpy, getNameFromGameRoom(realSpy)), parse_mode='html')
	else:
		spy = isSpy(group_id, row[0])
		if spy == None:
			bot.send_message(group_id, "<b>Шпион не был обнаружен!</b>\n\n    Место: {}\n\n    Шпион: <a href='tg://user?id={}'>{}</a>.".format(word, realSpy, getNameFromGameRoom(realSpy)), parse_mode='html')
		else:
			bot.send_message(group_id, "<b>Поздравляю, вы нашли шпиона!</b>\n\n    Место: {}\n\n    Шпион: <a href='tg://user?id={}'>{}</a>.".format(word, realSpy, getNameFromGameRoom(realSpy)), parse_mode='html')
	endGame(group_id)

def getGroupbByUsersIDInGame(user_id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT grpID FROM gameRoom WHERE userID = '%d'" % (user_id))
	row = cursor.fetchone()
	conn.close()
	if row != None:
		return row[0]

def getNameFromGameRoom(user_id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT name FROM gameRoom WHERE userID = '%d'" % (user_id))
	row = cursor.fetchone()
	conn.close()
	if row != None:
		return row[0]

def wordsPercent(string1, string2):
	s1 = string1.lower()
	s2 = string2.lower()
	text = ""
	percent = 0

	if len(s2)/len(s1) * 100 <= 100:
		percent = len(s2)/len(s1) * 100
		text = "Совпадение по длине " + str(int(len(s2)/len(s1) * 100))+'%.'
	else:
		percent = len(s1)/len(s2) * 100
		text =  "Совпадение по длине " + str(int(len(s1)/len(s2) * 100))+'%.'
	if percent == 100:
		p = 0
		for i in range(len(s1)):
			if s1[i] == s2[i] and ((s1[i].isalpha() and s2[i].isalpha()) or s1[i] == " "):
				p += 1
		return text + "\nСовпадение по буквам " + str(int(p/len(s1)*100))+'%.'
	else:
		return text

def getGroupsWord(group_id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT word FROM groups WHERE grpID = '%d'" % (group_id))
	row = cursor.fetchone()
	conn.close()
	if row != None:
		return row[0]

def checkingAnswer(message, group_id):
	word = getGroupsWord(group_id)
	if message.text.lower() == word.lower():
		bot.send_message(message.from_user.id, "Абсолютно верно, победа за Вами!")
		SpyWins(group_id)
	else:
		key = types.InlineKeyboardMarkup()
		key.add(types.InlineKeyboardButton("Проверить локацию", callback_data="answerfromspy"))
		bot.send_message(message.from_user.id, wordsPercent(message.text, word) + "\nМожешь попробовать еще раз.", reply_markup=key)

def SpyWins(group_id):
	key = types.InlineKeyboardMarkup()
	# key.add(types.InlineKeyboardButton("Сыграть еще раз!", callback_data="game"))
	bot.send_message(group_id, "Поздравляю шпиона <a href='tg://user?id={}'>{}</a> с победой!\n\n    Место: {}\n\nСыграем еще раз?".format(getSpyID(group_id), getNameFromGameRoom(getSpyID(group_id)), getGroupsWord(group_id)), parse_mode='html', reply_markup=key)
	endGame(group_id)

def getMyAdmins():
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT userID FROM admin")
	row = cursor.fetchall()
	conn.close()
	if row != None:
		return row

def isMyAdmin(user_id):
	admins = getMyAdmins()
	for i in admins:
		if user_id == i[0]:
			return True
	return False

def getAllCreators():
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT userID FROM settings")
	row = cursor.fetchall()
	conn.close()
	if row != None:
		return row

def isCreatorForSettings(user_id):
	creators = getAllCreators()
	for i in creators:
		if user_id == i[0]:
			return True
	return False

def getCreatorsGroups(user_id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT grpID FROM settings WHERE userID = '%d'" % (user_id))
	row = cursor.fetchall()
	conn.close()
	if row != None:
		return row

def editToGroupSettings(data, user_id, message_id):
	group_id = getNumberFromCall(data, 's')
	key = types.InlineKeyboardMarkup()
	key.add(types.InlineKeyboardButton("Изменить максимальное количество игроков", callback_data=str(group_id) + "maxgamers"))
	key.add(types.InlineKeyboardButton("Изменить длительность игры", callback_data=str(group_id) + "time"))
	key.add(types.InlineKeyboardButton("Изменить длительность регистрации", callback_data=str(group_id) + "inviting"))
	key.add(types.InlineKeyboardButton("⬅️Обратно к выбору группы", callback_data="groupsettings"))
	try:
		bot.edit_message_text("Настройки", user_id, message_id, reply_markup=key)
	except Exception:
		pass

def changeMaxGamers(message, data, user_id, message_id):
	group_id = getNumberFromCall(data, 'm')
	try:
		bot.edit_message_text("Введите максимальное количество игроков.\n\n/cancel для отмены.", user_id, message_id)
	except Exception:
		pass	
	bot.register_next_step_handler(message, maxGamers, old_message_id=message_id, group_id=group_id)

def maxGamers(message, old_message_id, group_id):
	if message.text == '/cancel':
		bot.delete_message(message.chat.id, old_message_id)
		changeToSettings("Количество игроков не было изменено.", message.chat.id, old_message_id)
		return
	try:
		bot.delete_message(message.chat.id, message.message_id)
	except Exception:
		pass
	if message.text.isdigit() and int(message.text) < bot.get_chat_members_count(group_id):
		conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
		cursor = conn.cursor()
		cursor.execute("UPDATE settings SET gamers = '%d' WHERE grpID = '%d'" % (int(message.text), group_id))
		conn.commit()
		conn.close()
		changeToSettings("Максимальное количество игроков изменено.", message.chat.id, old_message_id)
	elif message.text.isdigit():
		changeToSettings("Максимальное количество не может быть больше количества участников беседы.", message.chat.id, old_message_id)
	else:
		changeToSettings("Количество игроков не было изменено.", message.chat.id, old_message_id)

def changeInviteTime(message, data, user_id, message_id):
	group_id = getNumberFromCall(data, 'i')
	key = types.InlineKeyboardMarkup()
	key.add(types.InlineKeyboardButton(text="45 секунд", callback_data="45_" + str(group_id) + "chinvite"), types.InlineKeyboardButton(text="1 минута", callback_data="60_" + str(group_id) + "chinvite"), types.InlineKeyboardButton(text="2 минуты", callback_data="120_" + str(group_id) + "chinvite"))
	try:
		bot.edit_message_text("Выберите длительность регистрации", user_id, message_id, reply_markup=key)
	except Exception:
		pass

def changeMaxTime(message, data, user_id, message_id):
	group_id = getNumberFromCall(data, 't')
	key = types.InlineKeyboardMarkup()
	key.add(types.InlineKeyboardButton(text="5 минут", callback_data="5_" + str(group_id) + "chtime"), types.InlineKeyboardButton(text="10 минут", callback_data="10_" + str(group_id) + "chtime"), types.InlineKeyboardButton(text="15 минут", callback_data="15_" + str(group_id) + "chtime"))
	try:
		bot.edit_message_text("Выберите длительность игры", user_id, message_id, reply_markup=key)
	except Exception:
		pass

def changeToSettings(text, user_id, message_id):
	key = types.InlineKeyboardMarkup()
	for i in getCreatorsGroups(user_id):
		key.add(types.InlineKeyboardButton(text=bot.get_chat(i[0]).title, callback_data=str(i[0]) + "settings"))
	try:
		bot.edit_message_text(text, user_id, message_id, reply_markup=key)
	except Exception:
		pass

def getTimeForGame(group_id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT time FROM settings WHERE grpID = '%d'" % (group_id))
	row = cursor.fetchone()
	conn.close()
	if row != None:
		return row[0] * 40

def getTimeAfterPoll(group_id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT time FROM settings WHERE grpID = '%d'" % (group_id))
	row = cursor.fetchone()
	conn.close()
	if row != None:
		return row[0] * 20

def feedback(message):
	if message.text == "/cancel":
		bot.send_message(message.from_user.id, "Отмена.")
		return
	key = types.InlineKeyboardMarkup()
	key.add(types.InlineKeyboardButton("Ответить {}".format(message.from_user.first_name), callback_data=str(message.from_user.id) + "answer2user"))
	bot.send_message(144589481, "<i>Feedback</i>\n\nuser_id = {}\n\n{}".format(message.from_user.id, message.text), reply_markup=key, parse_mode='html')

def answerToUser(message, data):
	if message.text == "/cancel":
		bot.send_message(message.from_user.id, "Отмена.")
		return
	user_id = getNumberFromCall(data, 'a')
	key = types.InlineKeyboardMarkup()
	key.add(types.InlineKeyboardButton("Ответить", callback_data="feedback"))
	bot.send_message(user_id, "<i>Обратная связь</i>\n\n{}".format(message.text), reply_markup=key, parse_mode='html')

def showgameroom(message, message_id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM gameRoom")
	cursor2 = conn.cursor()
	cursor2.execute("SELECT DISTINCT grpID FROM gameRoom")
	word = cursor.fetchone()
	text = ""
	key = types.InlineKeyboardMarkup()
	key.add(types.InlineKeyboardButton("Update", callback_data="updategameroom"))
	key.add(types.InlineKeyboardButton("Back", callback_data="admpanel"))
	if (word == None or word[0] == None) and message_id == 0:
		bot.send_message(message.chat.id, "<b>gameroom is clean\n</b>", reply_markup=key, parse_mode="html")
		return
	elif word == None or word[0] == None:
		try:
			bot.edit_message_text("<b>gameroom is clean\n</b>", message.chat.id, message_id=message_id, reply_markup=key, parse_mode="html")
		except Exception:
			pass
		finally:
			return
	groups = cursor2.fetchone()
	while word != None:
		text += str(word[0]) + '_' + str(word[1]) + '_' + word[2] + "\n"
		if groups != None:
			key.add(types.InlineKeyboardButton(groups[0], callback_data=str(groups[0]) + "cleancache"))
			groups = cursor2.fetchone()
		word = cursor.fetchone()
	conn.close()
	if message_id == 0:
		bot.send_message(message.chat.id, "<b>gameroom\n</b>" + text, reply_markup=key ,parse_mode="html")
	else:
		try:
			bot.edit_message_text("<b>gameroom\n</b>" + text, message.chat.id, message_id=message_id, reply_markup=key ,parse_mode="html")
		except Exception:
			pass

def numGamersForOFflineGame(message, chat_id, old_message_id):
	if message.text == '/cancel':
		try:
			bot.delete_message(message.chat.id, message.message_id)
		except Exception:
			pass
		try:
			bot.edit_message_text("Игра отменена.", chat_id, old_message_id)
		except Exception:
			pass
		return
	if message.text.isdigit() and int(message.text) >= 4:
		try:
			bot.delete_message(message.chat.id, message.message_id)
		except Exception:
			pass
		numOfGamers = int(message.text)
		conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
		cursor = conn.cursor()
		cursor.execute("INSERT INTO offlineGame (userID, gamers, word) VALUES ('%d', '%d', '%s')" % (message.chat.id, numOfGamers, getWord()))
		conn.commit()
		conn.close()
		key = types.InlineKeyboardMarkup()
		key.add(types.InlineKeyboardButton(text="5 минут", callback_data="5offlinetime"), types.InlineKeyboardButton(text="10 минут", callback_data="10offlinetime"), types.InlineKeyboardButton(text="15 минут", callback_data="15offlinetime"))
		try:
			bot.edit_message_text("Выберите длительность игры", chat_id, old_message_id, reply_markup=key)
		except Exception:
			pass
	elif message.text.isdigit():
		try:
			bot.delete_message(message.chat.id, message.message_id)
		except Exception:
			pass
		try:
			bot.edit_message_text("<b>Оффлайн игра</b>\nНедостаточно игроков для начала игры.", message.chat.id, message_id=old_message_id, parse_mode='html')
		except Exception:
			pass
	else:
		try:
			bot.delete_message(message.chat.id, message.message_id)
		except Exception:
			pass
		try:
			bot.edit_message_text("<b>Оффлайн игра</b>\nВведите только количество игроков.\n\n/cancel для отмены.", message.chat.id, message_id=old_message_id, parse_mode='html')
		except Exception:
			pass
		bot.register_next_step_handler(message, numGamersForOFflineGame, chat_id, old_message_id)

def setOfflineSpy(user_id, message_id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT spy FROM offlineGame WHERE userID = '%d'" % (user_id))
	row = cursor.fetchone()
	if row[0] != None:
		conn.close()
		return row[0]
	cursor.execute("SELECT gamers FROM offlineGame WHERE userID = '%d'" % (user_id))
	numOfGamers = cursor.fetchone()[0]
	randomNumber = random.randint(1, numOfGamers)
	cursor.execute("UPDATE offlineGame SET spy = '%d' WHERE userID = '%d'" % (randomNumber, user_id))
	conn.commit()
	conn.close()
	key = types.InlineKeyboardMarkup()
	key.add(types.InlineKeyboardButton(text="Поехали", callback_data="1offlinerole"))
	try:
		bot.edit_message_text("<b>Оффлайн игра</b>\nВсе готово, можем начинать.\nДержи телефон так, чтобы твои друзья не видели место, в которое мы сейчас переместимся.", user_id, message_id=message_id, reply_markup=key, parse_mode='html')
	except Exception:
		pass
	
def startOfflineGame(user_id, message_id, id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT gamers,spy,word FROM offlineGame WHERE userID = '%d'" % (user_id))
	row = cursor.fetchone()
	key = types.InlineKeyboardMarkup()
	if id == row[1] and id == row[0]:
		key.add(types.InlineKeyboardButton("OK", callback_data="rolesgiven"))
		bot.edit_message_text("<b>Ты – шпион!</b>\nПостарайся понять, о какой локации говорят местные.\n\nЖми \"ОК\" для начала игры.", user_id, message_id, parse_mode='html', reply_markup=key)
	elif id == row[0]:
		key.add(types.InlineKeyboardButton("OK", callback_data="rolesgiven"))
		bot.edit_message_text("<b>Ты – местный.</b>\nТвоя локация – <i>{}</i>.\nВсе игроки, кроме Шпиона, знают эту локацию. Задавай вопросы другим игрокам, чтобы вычислить Шпиона!\n\nЖми \"ОК\" для начала игры.".format(row[2]), user_id, message_id, parse_mode='html', reply_markup=key)
	elif id == row[1]:
		key.add(types.InlineKeyboardButton("OK", callback_data=str(id + 1)+"waitrole"))
		bot.edit_message_text("<b>Ты – шпион!</b>\nПостарайся понять, о какой локации говорят местные\n\nЖми \"ОК\" и передавай телефон следующему игроку.", user_id, message_id, parse_mode='html', reply_markup=key)
	else:
		key.add(types.InlineKeyboardButton("OK", callback_data=str(id + 1)+"waitrole"))
		bot.edit_message_text("<b>Ты – местный.</b>\nТвоя локация – <i>{}</i>.\nВсе игроки, кроме Шпиона, знают эту локацию. Задавай вопросы другим игрокам, чтобы вычислить Шпиона!\n\nЖми \"ОК\" и передавай телефон следующему игроку.".format(row[2]), user_id, message_id, parse_mode='html', reply_markup=key)

def offlineGameEnd(user_id, message_id, date):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	if date == None:
		try:
			bot.delete_message(user_id, message_id)
		except Exception:
			pass
		key = types.InlineKeyboardMarkup()
		key.add(types.InlineKeyboardButton("Новая игра", callback_data="edittooffline"))
		bot.send_message(user_id, "<b>Игра окончена!</b>\n*Никогда не поздно сыграть еще раз*", reply_markup=key, parse_mode='html')
		cursor.execute("DELETE FROM offlineGame WHERE userID = '%d'" % (user_id))
		conn.commit()
		conn.close()
		return
	cursor.execute("SELECT startTime FROM offlineGame WHERE userID = '%d'" % (user_id))
	startTime = cursor.fetchone()
	if startTime == None or startTime[0] != date:
		return
	try:
		bot.delete_message(user_id, message_id)
	except Exception:
		pass
	key = types.InlineKeyboardMarkup()
	key.add(types.InlineKeyboardButton("Новая игра", callback_data="edittooffline"))
	bot.send_message(user_id, "<b>Игра окончена!</b>\n*Никогда не поздно сыграть еще раз*", reply_markup=key, parse_mode='html')
	cursor.execute("DELETE FROM offlineGame WHERE userID = '%d'" % (user_id))
	conn.commit()
	conn.close()

def getOfflineGameStartTime(user_id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT startTime FROM offlineGame WHERE userID = '%d'" % (user_id))
	startTime = cursor.fetchone()
	if startTime != None:
		return startTime[0]
	conn.close()

def whenToEndOfflineGame(user_id, date, endTime):
	timing = 0
	while timing <= endTime and getOfflineGameStartTime(user_id) == date:
		time.sleep(3)
		timing += 3
		if endTime - timing == 28 or endTime - timing == 29 or endTime - timing == 30:
			bot.send_message(user_id, "<i>До окончания игры осталось " + str(endTime-timing)+" секунд</i>.", parse_mode="html")
		print("whenToEndOfflineGame")

def find_all_by_key(iterable, key, value):
	list = [value for index, dict_ in enumerate(iterable)
			if key in dict_ and dict_[key] == value]
	if len(list) != 0:
		return True
	else:
		return False

def getMessageCallback(message, text):
	if message.text == '/cancel':
		return
	if ' ➖ ' in message.text:
		try:
			key = types.InlineKeyboardMarkup()
			callback_data = message.text.split('\n')
			for i in callback_data:
				splitter = i.split(' ➖ ')
				if validators.url(splitter[1]):
					key.add(types.InlineKeyboardButton(splitter[0], url=splitter[1]))
				else:
					key.add(types.InlineKeyboardButton(splitter[0], callback_data=splitter[1]))
		except:
			bot.send_message(message.from_user.id, "Ошибка подбора кнопок")
			return
	else:
		return
	bot.send_message(message.from_user.id, text, reply_markup=key)
	bot.send_message(message.from_user.id, "Отправляем всем/отмена/user_id")
	bot.register_next_step_handler(message, mailing, key, text)

def mailing(message, key, text):
	if message.text.lower() == 'всем':
		conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
		cursor = conn.cursor()
		cursor.execute('SELECT userID FROM users')
		row = cursor.fetchall()
		users = 0
		conn.close()
		for user in row:
			try:
				bot.send_message(user[0], text, parse_mode="html", reply_markup=key)
				users += 1
			except:
				pass
		bot.send_message(message.from_user.id, "Отправлено {}".format(users), parse_mode="html", reply_markup=key)
	elif message.text.lower() == 'Отмена':
		return
	elif message.text.isdigit():
		bot.send_message(str(message.text), text, parse_mode="html", reply_markup=key)
	else:
		bot.send_message(message.from_user.id, "Отмена", parse_mode="html", reply_markup=key)


def checkNewWord(message):
	if message.text == '/cancel':
		bot.send_message(message.from_user.id, "Отмена.")
		return
	bot.send_message(message.from_user.id, "Cпасибо, что помогаешь в развитии!")
	key = types.InlineKeyboardMarkup()
	key.add(types.InlineKeyboardButton("Добавить", callback_data="{}_addingword".format(message.text)), types.InlineKeyboardButton("Отмена", callback_data="delete_message"))
	bot.send_message(144589481, "Новое слово от пользователя {}({}) – {}".format(message.from_user.first_name, message.from_user.id, message.text), reply_markup=key)

def sendGamers(group_id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	text = "<b>Участники игры:</b>\n    "
	cursor.execute("SELECT * FROM gameRoom WHERE grpID = '%d'" % (group_id))
	row = cursor.fetchone()
	text += "<a href='tg://user?id={}'>{}</a>".format(row[1], row[2])
	row = cursor.fetchone()
	while row != None:
		text += ", <a href='tg://user?id={}'>{}</a>".format(row[1], row[2])
		row = cursor.fetchone()
	conn.close()
	message = bot.send_message(group_id, text, parse_mode='html')
	return message.message_id
