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
import subprocess

token = "1084976464:AAGj6yatNDYgQIi1eoqlNrzUPxRqRreQ318"
# token = "941639396:AAFPJMdmcMhXWtniZbJeE0DeuBvykLu6Ve8" #test_token

bot = telebot.TeleBot(token)

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
	bot.delete_message(group_id, getInviteID(group_id))
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
		key.add(types.InlineKeyboardButton("Начать игру", callback_data=str(group_id) + 'skipinvite'))
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
	key.add(types.InlineKeyboardButton("Я знаю локацию", callback_data='answerfromspy'))
	bot.send_message(cursor.fetchone()[0], "<b>Ты – шпион!</b>\nПостарайся понять, о какой локации говорят местные и напиши ее мне после нажатия на кнопку.", parse_mode='html', reply_markup=key)
	conn.close()

def gameStarting(group_id):
	if getSpyID(group_id) != None:
		return
	first_invite_id = getInviteID(group_id)
	if gameIsExisted(group_id) == 0 and first_invite_id != None:
		# first_invite_id = getInviteID(group_id)
		try:
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
	while timing <= endTime and len(getGamersByGroupId(group_id)) <= getNumberOfGamersByGroupIdFromSettings(group_id) and len(getGamersByGroupId(group_id)) < bot.get_chat_members_count(group_id) - 1 and gameIsExisted(group_id) == 0:
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
		key.add(types.InlineKeyboardButton("Я знаю локацию", callback_data="answerfromspy"))
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
	key.add(types.InlineKeyboardButton("Изменить максимальное число игроков", callback_data=str(group_id) + "maxgamers"))
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
	while word != None:
		text += str(word[0]) + '_' + str(word[1]) + '_' + word[2] + "\n"
		key.add(types.InlineKeyboardButton(word[0], callback_data=str(word[0]) + "cleancache"))
		word = cursor.fetchone()
	conn.close()
	if message_id == 0:
		bot.send_message(message.chat.id, "<b>gameroom\n</b>" + text, reply_markup=key ,parse_mode="html")
	else:
		try:
			bot.edit_message_text("<b>gameroom\n</b>" + text, message.chat.id, message_id=message_id, reply_markup=key ,parse_mode="html")
		except Exception:
			pass

def admsendmsg(message):
	if message.text == "/cancel":
		return
	bot.send_message(message.from_user.id, "Теперь пришлите сообщение для юзера\n\n/cancel для отмены")
	bot.register_next_step_handler(message, admsendingmsg, int(message.text))

def admsendingmsg(message, user_id):
	if message.text == "/cancel":
		return
	key = types.InlineKeyboardMarkup()
	key.add(types.InlineKeyboardButton("Ответить", callback_data="feedback"))
	try:
		bot.send_message(user_id, message.text, reply_markup=key, parse_mode='html')
		bot.send_message(message.from_user.id, "Сообщение отправлено")
	except Exception:
		bot.send_message(message.from_user.id, "Ошибка")

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

def control_linux_keys():
	key = types.InlineKeyboardMarkup()
	key.add(types.InlineKeyboardButton("git pull", callback_data="gitpull"))
	key.add(types.InlineKeyboardButton("restart", callback_data="restartbot"))
	key.add(types.InlineKeyboardButton("Back", callback_data="admpanel"))
	return key

###########################
###### Group Handler ######
###########################

@bot.message_handler(content_types=["group_chat_created", "supergroup_chat_created"])
def groupChatCreated(message):
	start(message)

@bot.message_handler(content_types=["new_chat_members"])
def newChatMember(message):
	if (message.chat.type == 'group' or message.chat.type == 'supergroup') and (message.new_chat_member.id == bot.get_me().id): #or find_all_by_key(message.new_chat_members, "id", bot.get_me().id)):
		start(message)

@bot.message_handler(content_types=['text', 'voice', 'video', 'photo', 'document'])
def AllHandler(message):
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
	key.add(types.InlineKeyboardButton("Send message", callback_data="admsendmsg"))
	key.add(types.InlineKeyboardButton("Linux controlling", callback_data="controlinux"))
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
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute('SELECT * FROM users')
	row = cursor.fetchone()
	while row is not None:
		bot.send_message(row[0], message.text, parse_mode="html")
		row = cursor.fetchone()
	conn.close()

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
		bot.send_message(c.message.chat.id, "Рассылка\n\n/cancel для отмены")
		bot.register_next_step_handler(c.message, admrass)
	elif c.data == 'admsendmsg':
		bot.send_message(c.message.chat.id, "Пришлите user_id\n\n/cancel для отмены")
		bot.register_next_step_handler(c.message, admsendmsg)
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
	elif c.data == "controlinux":
		key = control_linux_keys()
		bot.edit_message_text("linux controlling", c.message.chat.id, c.message.message_id, reply_markup=key)
	elif c.data == "gitpull":
		key = control_linux_keys()
		subprocess.run("git pull", shell=True)
		try:
			bot.edit_message_text("Git pulled", c.message.chat.id, c.message.message_id, reply_markup=key)
		except Exception as e:
			bot.edit_message_text(str(e), c.message.chat.id, c.message.message_id, reply_markup=key)
	elif c.data == "restartbot":
		key = control_linux_keys()
		subprocess.run("systemctl restart tgbot.service", shell=True)
		try:
			bot.edit_message_text("Restarted", c.message.chat.id, c.message.message_id, reply_markup=key)
		except Exception as e:
			bot.edit_message_text(str(e), c.message.chat.id, c.message.message_id, reply_markup=key)
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



# try:
#     bot.polling(none_stop=True, interval=0)
# except Exception:
#     pass
try:
	bot.send_message(144589481, "polling restart")
	bot.polling(none_stop=True)
except Exception as e:
	bot.send_message(144589481, e)
