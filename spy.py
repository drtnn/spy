#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8
from __future__ import unicode_literals
import telebot
from telebot import types
from telebot import apihelper
import datetime
import json
import sqlite3
from string import ascii_letters
import random				#random.randint(<Начало>, <Конец>)
import time
import threading

token = "1084976464:AAGj6yatNDYgQIi1eoqlNrzUPxRqRreQ318"
bot = telebot.TeleBot(token)

def getWord():
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT MAX(num) FROM words")
	maxNum = cursor.fetchone()[0]
	randomNumber = random.randint(1, maxNum)
	cursor.execute("SELECT word FROM words WHERE num = '%d'" % (randomNumber))
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
	numFromSettings = getNumberOfGamersByGroupId(group_id)
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
	numFromSettings = getNumberOfGamersByGroupId(group_id)
	gamersFromGameRoom = getGamersByGroupId(group_id)
	if numFromSettings != None and gamersFromGameRoom != None:
		if len(gamersFromGameRoom) == numFromSettings:
			conn.close()
			return 
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
	if numOfGamers < 5:#####################################################################################
		conn.close()
		return 1
	randomNumber = random.randint(0, numOfGamers - 1)
	for i in row:
		if i[0] == row[randomNumber][0]:
			cursor.execute("INSERT INTO spyID (grpID,userID) VALUES ('%d','%d')" % (group_id, i[0]))
			continue
		cursor.execute("INSERT INTO pieceID (grpID,userID) VALUES ('%d','%d')" % (group_id, i[0]))
	conn.commit()	
	conn.close()
	return 0

def endGame(group_id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("DELETE FROM gameRoom WHERE grpID = '%d'" % (group_id))
	cursor.execute("DELETE FROM pieceID WHERE grpID = '%d'" % (group_id))
	cursor.execute("DELETE FROM spyID WHERE grpID = '%d'" % (group_id))
	cursor.execute("DELETE FROM messages WHERE grpID = '%d'" % (group_id))
	cursor.execute("DELETE FROM poll WHERE grpID = '%d'" % (group_id))
	cursor.execute("DELETE FROM groupsWord WHERE grpID = '%d'" % (group_id))
	conn.commit()
	conn.close()

def admSettings(group_id):
	adms = bot.get_chat_administrators(group_id)
	for i in adms:
		if i.status == 'creator':
			conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
			cursor = conn.cursor()
			cursor.execute("INSERT INTO settings (grpID, userID, time, gamers) VALUES ('%d', '%d', '%d', '%d')" % (group_id, i.user.id, 5, 12))
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

def checkPermissions(group_id, bot_id):
	botPermissions = bot.get_chat_member(group_id, bot_id)
	if botPermissions.can_restrict_members == True and botPermissions.can_delete_messages == True and botPermissions.can_pin_messages == True:
		# bot.send_message(group_id, "Отлично, права администратора получил. Для начала игры просто напишите /game")
		return 0
	else:
		key = types.InlineKeyboardMarkup()
		key.add(types.InlineKeyboardButton("✔️", callback_data="permissions"))
		bot.send_message(group_id, "Похоже я еще не получил права администратора!\nЯ не читаю и не отслеживаю ваши сообщения!", reply_markup=key)
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

def getNumberOfGamersByGroupId(group_id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT gamers FROM settings WHERE grpID = '%d'" % (group_id))
	row = cursor.fetchone()
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
	bot.edit_message_text(text, group_id, invite_id, parse_mode='html', reply_markup=key)

def waitingUsers(group_id, timing):
	print("I wait")
	time.sleep(timing)
	# bot.delete_message(group_id, getInviteID(group_id))

def givingWords(group_id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT userID FROM pieceID WHERE grpID = '%d'" % (group_id))
	gamers = cursor.fetchall()
	word = getWord()
	for i in gamers:
		bot.send_message(i[0], "Итак, ваше место - {}".format(word))
	cursor.execute("INSERT INTO groupsWord (grpID, word) VALUES ('%d', '%s')" % (group_id, word))
	conn.commit()
	cursor.execute("SELECT userID FROM spyID WHERE grpID = '%d'" % (group_id))
	bot.send_message(cursor.fetchone()[0], "Ты - шпион! Постарайся угадать место и напиши мне /answer.")
	conn.close()

def gameStarting(group_id):
	if getSpyID(group_id) != None:
		return
	first_invite_id = getInviteID(group_id)
	if gameIsExisted(group_id) == 0 and first_invite_id != None:
		# first_invite_id = getInviteID(group_id)
		bot.delete_message(group_id, first_invite_id)
		if givingRoles(group_id) == 1:
			bot.send_message(group_id, "Недостаточно игроков для начала игры")
			endGame(group_id)
			return 1
		givingWords(group_id)
		key = types.InlineKeyboardMarkup()
		key.add(types.InlineKeyboardButton("Слово тут!", url="t.me/findspy_bot"))
		bot.send_message(group_id, "Начало игры!", reply_markup=key)
		t = threading.Thread(target=whenToStartPoll, name="Thread2Poll{}".format(str(group_id)), args=(group_id, getTimeForGame(group_id)))###################################################################################################################
		t.start()
		# t.join()
		# t = threading.Thread(target=whenToEndPoll, name="Thread2EndPoll{}".format(str(group_id), args=(group_id, 120)))###################################################################################################################
		# t = threading.Thread(target=whenToEndPoll, name="Thread2EndPoll{}".format(str(group_id)), args=(group_id, 120))###################################################################################################################
		# t.start()
	elif first_invite_id == None:
		bot.send_message(group_id, "Недостаточно игроков для начала игры")
		endGame(group_id)
		return 1

def whenToEndPoll(group_id, endTime):
	timing = 0
	while timing <= endTime and len(pollResult(group_id)) < len(getGamersByGroupId(group_id)):
		time.sleep(3)
		timing += 3
		print("whenToEndPoll")
	startGameResult(group_id)

def whenToStartPoll(group_id, endTime):
	timing = 0
	while timing <= endTime and gameIsExisted(group_id) == 0 and getPollStatus(group_id) != 1:
		time.sleep(3)
		timing += 3
		print("whenToStartPoll")
	individualPoll(group_id)
	t = threading.Thread(target=whenToEndPoll, name="Thread2EndPoll{}".format(str(group_id)), args=(group_id, getTimeAfterPoll(group_id)))###################################################################################################################
	t.start()

def whenToEndInvite(group_id, endTime):
	timing = 0
	while timing <= endTime and len(getGamersByGroupId(group_id)) <= getNumberOfGamersByGroupId(group_id) and len(getGamersByGroupId(group_id)) < bot.get_chat_members_count(group_id) - 1:
		time.sleep(3)
		timing += 3
		print("whenToEndInvite")
	gameStarting(group_id)

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
		bot.send_message(i[0], "Выберите предполагаемого шпиона!\nПомни, у тебя только одна попытка.", reply_markup=key)
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("UPDATE messages SET poll = 1 WHERE grpID = '%d'" % (group_id))
	conn.commit()
	conn.close()

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
		bot.send_message(group_id, "<a href='tg://user?id={}'>{}</a> сделал свой выбор".format(user_id, getNameFromGameRoom(user_id)), parse_mode='html')
		cursor.execute("INSERT INTO poll (grpID,whoUserID,onUserID) VALUES ('%d','%d', '%d')" % (group_id, user_id, userPoll))
	conn.commit()
	conn.close()
	if len(pollResult(group_id)) == len(getGamersByGroupId(group_id)):
		startGameResult(group_id)

def getSpyID(group_id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT userID FROM spyID WHERE grpID = '%d'" % (group_id))
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
			bot.send_message(group_id, "Похоже шпион не был обнаружен!\n\n    Место: {}\n\n    Шпион: <a href='tg://user?id={}'>{}</a>".format(word, realSpy, getNameFromGameRoom(realSpy)), parse_mode='html')
		else:
			bot.send_message(group_id, "Поздравляем, вы нашли шпиона!\n\n    Место: {}\n\n    Шпион: <a href='tg://user?id={}'>{}</a>".format(word, realSpy, getNameFromGameRoom(realSpy)), parse_mode='html')
	else:
		spy = isSpy(group_id, row[0])
		if spy == None:
			bot.send_message(group_id, "Похоже шпион не был обнаружен!\n\n    Место: {}\n\n    Шпион: <a href='tg://user?id={}'>{}</a>".format(word, realSpy, getNameFromGameRoom(realSpy)), parse_mode='html')
		else:
			bot.send_message(group_id, "Поздравляем, вы нашли шпиона!\n\n    Место: {}\n\n    Шпион: <a href='tg://user?id={}'>{}</a>".format(word, realSpy, getNameFromGameRoom(realSpy)), parse_mode='html')
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

    if len(s2)/len(s1) * 100 <= 100:

        text = "Совпадение по длине " + str(len(s2)/len(s1) * 100)+'%\n'
    else:
        text =  "Совпадение по длине " + str(len(s1)/len(s2) * 100)+'%\n'
    if len(s1) > len(s2):
        s1, s2 = s2, s1
    p = 0
    for i in range(len(s1)):
        if s1[i] == s2[i] and s1[i].isalpha() and s2[i].isalpha():
            p += 1
    return text + "Совпадение по буквам " + str(int(p/len(s1)*100))+'%'

def getGroupsWord(group_id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT word FROM groupsWord WHERE grpID = '%d'" % (group_id))
	row = cursor.fetchone()
	conn.close()
	if row != None:
		return row[0]

def checkingAnswer(message, group_id):
	word = getGroupsWord(group_id)
	if message.text == word:
		bot.send_message(message.from_user.id, "Браво, абсолютно верно!")
		SpyWins(group_id)
	else:
		bot.send_message(message.from_user.id, "Слово(а) совпадают на " + wordsPercent(message.text, word) + "\nМожешь попробовать еще раз - /answer")

def SpyWins(group_id):
	key = types.InlineKeyboardMarkup()
	# key.add(types.InlineKeyboardButton("Сыграть еще раз!", callback_data="game"))
	bot.send_message(group_id, "Поздравляем шпиона <a href='tg://user?id={}'>{}</a> с победой!\nМесто: {}\n\nСыграем еще раз? /game".format(getSpyID(group_id), getNameFromGameRoom(getSpyID(group_id)), getGroupsWord(group_id)), parse_mode='html', reply_markup=key)
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
	key.add(types.InlineKeyboardButton("Изменить максимальное число игроков", callback_data=str(group_id) + "maxgamers"))
	key.add(types.InlineKeyboardButton("Изменить время игры", callback_data=str(group_id) + "time"))
	key.add(types.InlineKeyboardButton("⬅️Обратно в выбор группы", callback_data="groupsettings"))
	bot.edit_message_text("Настройки", user_id, message_id, reply_markup=key)

def changeMaxGamers(message, data, user_id, message_id):
	group_id = getNumberFromCall(data, 'm')
	bot.edit_message_text("Введите максимальное количество игроков", user_id, message_id)
	bot.register_next_step_handler(message, maxGamers, old_message_id=message_id, group_id=group_id)

def maxGamers(message, old_message_id, group_id):
	bot.delete_message(message.chat.id, message.message_id)
	if message.text.isdigit() and int(message.text) < bot.get_chat_members_count(group_id):
		conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
		cursor = conn.cursor()
		cursor.execute("UPDATE settings SET gamers = '%d' WHERE grpID = '%d'" % (int(message.text), group_id))
		row = cursor.fetchall()
		conn.commit()
		conn.close()
		changeToSettings("Максимальное число игроков изменено", message.chat.id, old_message_id)
	elif message.text.isdigit():
		changeToSettings("Максимальное число не может быть больше числа пользователей", message.chat.id, old_message_id)
	else:
		changeToSettings("Число игроков не было изменено", message.chat.id, old_message_id)

def changeMaxTime(message, data, user_id, message_id):
	group_id = getNumberFromCall(data, 't')
	key = types.InlineKeyboardMarkup()
	key.add(types.InlineKeyboardButton(text="5", callback_data="5_" + str(group_id) + "chtime"), types.InlineKeyboardButton(text="10", callback_data="10_" + str(group_id) + "chtime"), types.InlineKeyboardButton(text="15", callback_data="15_" + str(group_id) + "chtime"))
	bot.edit_message_text("Выберите длительность игры", user_id, message_id, reply_markup=key)

def changeToSettings(text, user_id, message_id):
	key = types.InlineKeyboardMarkup()
	for i in getCreatorsGroups(user_id):
		key.add(types.InlineKeyboardButton(text=bot.get_chat(i[0]).title, callback_data=str(i[0]) + "settings"))
	bot.edit_message_text(text, user_id, message_id, reply_markup=key)

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

###########################
###### Group Handler ######
###########################

@bot.message_handler(content_types=['text', 'voice', 'video', 'photo', 'document'])
def AllHandler(message):
	if (message.chat.type == 'supergroup' or message.chat.type == 'group') and gameIsExisted(message.chat.id) == 0 and getSpyID(message.chat.id) != None and (message.from_user.id,) not in getGamersByGroupId(message.chat.id):
		bot.delete_message(message.chat.id, message.message_id)
		if message.chat.type == 'supergroup':
			bot.restrict_chat_member(message.chat.id, message.from_user.id, message.date + 30, can_send_messages=False, can_send_media_messages=False, can_send_other_messages=False)
	elif message.text == '/start' or message.text == '/start@findspy_bot':
		start(message)
	elif message.text == '/end' or message.text == '/end@findspy_bot':
		end(message)
	elif message.text == '/startpoll@findspy_bot':
		startPollNow(message)
	elif message.text == '/rules' or message.text == '/rules@findspy_bot':
		rules(message)
	elif message.text == '/game' or message.text == '/game@findspy_bot':
		game(message)
	elif message.text == '/answer' or message.text == '/answer@findspy_bot':
		answer(message)
	elif message.text == '/admword':
		admword(message)
	elif message.text == '/settings' or message.text == '/settings@findspy_bot':
		settings(message)
	elif message.text == '/addword' and isMyAdmin(message.chat.id):
		bot.send_message(message.chat.id, "Присылай новое слово!")
		bot.register_next_step_handler(message, addword)

# @bot.message_handler(commands=['start'])
def start(message):
	if (message.chat.type == 'supergroup' or message.chat.type == 'group') and message.text == '/start@findspy_bot':
		if addGroup(message.chat.id) == 0:
			admSettings(message.chat.id)
		key = types.InlineKeyboardMarkup()
		key.add(types.InlineKeyboardButton("✔️", callback_data="permissions"))
		key.add(types.InlineKeyboardButton("Познакомимся?", url="t.me/findspy_bot"))
		bot.send_message(message.chat.id, "Привет! Я бот игры Шпион, для начала игры дай мне права администратора и перейдите в лс к боту!", reply_markup=key)
	if message.chat.type == 'private':
		bot.send_message(message.chat.id, "Привет! Я бот игры Шпион. Рад, что мы теперь знакомы!")
		addUser(message.from_user.id)

# @bot.message_handler(commands=['startpoll'])
def startPollNow(message):
	if (message.chat.type == 'supergroup'  or message.chat.type == 'group') and gameIsExisted(message.chat.id) == 0 and getPollStatus(message.chat.id) == 0 and getSpyID(message.chat.id) != None:
		individualPoll(message.chat.id)
		t = threading.Thread(target=whenToEndPoll, name="Thread2Poll{}".format(str(message.chat.id), args=(message.chat.id, getTimeAfterPoll(message.chat.id))))
		t.start()

# @bot.message_handler(commands=['game'])
def game(message):
	if (message.chat.type == 'supergroup'  or message.chat.type == 'group') and gameIsExisted(message.chat.id) == 1 and checkPermissions(message.chat.id, 1084976464) == 0:
		key = types.InlineKeyboardMarkup()
		key.add(types.InlineKeyboardButton("Присоединиться", callback_data='connect'))
		bot.send_message(message.chat.id, "Жми на кнопку, чтобы присоединиться к игре!\n\n    Игроки: <a href='tg://user?id={}'>{}</a>".format(message.from_user.id, message.from_user.first_name), parse_mode="html", reply_markup=key)
		if newGame(message.chat.id, message.from_user.id, message.from_user.first_name) == 2:
			btn = types.InlineKeyboardMarkup()
			btn.add(types.InlineKeyboardButton("Познакомимся?", url="t.me/findspy_bot"))
			bot.send_message(message.chat.id, "<a href='tg://user?id={}'>{}</a> все еще не перешел в личный диалог!".format(message.from_user.id, message.from_user.first_name), parse_mode='html', reply_markup=btn)
			return
		t = threading.Thread(target=whenToEndInvite, name="Thread4Invite{}".format(str(message.chat.id)), args=(message.chat.id, 45))###################################################################################################################
		t.start()

# @bot.message_handler(commands=['end'])
def end(message):
	if (message.chat.type == 'supergroup'  or message.chat.type == 'group') and gameIsExisted(message.chat.id) == 0 and message.from_user.id in getAdmins(message.chat.id):
		bot.send_message(message.chat.id, "Игра окончена!")
		endGame(message.chat.id)

# @bot.message_handler(commands=['rules'])
def rules(message):
	bot.send_message(message.chat.id, "В начале игры каждый получает в личном диалоге со мной сообщение с локацией или узнает, что он шпион!\nЦель игры:\n    Игрокам необходимо выявить шпиона.\n    Шпиону необходимо определить локацию.\n\nОбсуждения в беседе приветствуются!🤔")

def admword(message):
	if isMyAdmin(message.chat.id) and getGroupbByUsersIDInGame(message.chat.id) != None:
		bot.send_message(message.chat.id, getGroupsWord(getGroupbByUsersIDInGame(message.chat.id)))

def addword(message):
	if isMyAdmin(message.chat.id):
		conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
		cursor = conn.cursor()
		cursor.execute("SELECT MAX(num) FROM words")
		maxNum = cursor.fetchone()[0]
		cursor.execute("INSERT INTO words (num,word) VALUES ('%d','%s')" % (maxNum + 1, message.text))
		conn.commit()
		conn.close()
		bot.send_message(message.from_user.id, "Добавлено!")

# @bot.message_handler(commands=['answer'])
def answer(message):
	group_id = getGroupbByUsersIDInGame(message.from_user.id)
	if message.chat.type == 'private' and gameIsExisted(group_id) == 0 and getSpyID(group_id) != None:
		if getSpyID(group_id) == message.from_user.id:
			bot.send_message(message.from_user.id, "Можешь написать мне слово, а я его проверю!")
			bot.register_next_step_handler(message, checkingAnswer, group_id)
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

@bot.callback_query_handler(func=lambda c:True)
def inline(c):
	print(c.data)
	if c.data == 'permissions':
		if checkPermissions(c.message.chat.id, c.message.from_user.id) == 0:
			bot.send_message(c.message.chat.id, "Отлично, права администратора получил. Для начала игры просто напишите /game")
	# if c.data == 'game':
	# 	game(c.message)
	elif c.data == 'connect' and checkPermissions(c.message.chat.id, c.message.from_user.id) == 0:
		addReturn = addUserToGame(c.message.chat.id, c.from_user.id, c.from_user.first_name)
		if addReturn == 3:
			bot.delete_message(c.message.chat.id, c.message.message_id)
		if addReturn == 1:
			return
		elif addReturn == 2:
			key = types.InlineKeyboardMarkup()
			key.add(types.InlineKeyboardButton("Познакомимся?", url="t.me/findspy_bot"))
			bot.send_message(c.message.chat.id, "<a href='tg://user?id={}'>{}</a> все еще не перешел в личный диалог!".format(c.from_user.id, c.from_user.first_name), parse_mode='html', reply_markup=key)
			return
		inviteID(c.message.chat.id, c.message.message_id)
		editInvite(c.message.chat.id)
	elif c.data == "groupsettings":
		changeToSettings("Выберите", c.message.chat.id, c.message.message_id)
	elif "settings" in c.data:
		editToGroupSettings(c.data, c.message.chat.id, c.message.message_id)
	elif "poll" in c.data:
		bot.edit_message_text("Вы сделали свой выбор!", c.message.chat.id, c.message.message_id)
		pollHandler(getGroupbByUsersIDInGame(c.from_user.id), c.from_user.id, c.data)
	elif "maxgamers" in c.data:
		changeMaxGamers(c.message, c.data, c.message.chat.id, c.message.message_id)
	elif "chtime" in c.data:
		newTime = getNumberFromCall(c.data, "_")
		group_id = getNumberFromLetterToCall(c.data, "_", "c")
		conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
		cursor = conn.cursor()
		cursor.execute("UPDATE settings SET time = '%d' WHERE grpID = '%d'" % (int(newTime), group_id))
		row = cursor.fetchall()
		conn.commit()
		conn.close()
		changeToSettings("Максимальное время игры изменено.", c.message.chat.id, c.message.message_id)
	elif "time" in c.data:
		changeMaxTime(c.message, c.data, c.message.chat.id, c.message.message_id)



# try: 
#     bot.polling(none_stop=True, interval=0)
# except Exception:
#     pass
bot.polling(none_stop=True)