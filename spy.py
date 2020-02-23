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

def addUserToGame(group_id, user_id, name):
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
	cursor.execute("INSERT INTO gameRoom (grpID,userID, name) VALUES ('%d','%d', '%s')" % (group_id, user_id, name))
	conn.commit()	
	conn.close()
	return 0

def gameIsExisted(group_id):
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
	if numOfGamers < 5:
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
	cursor.execute("INSERT INTO messages (grpID,inviteID) VALUES ('%d','%d')" % (group_id, invite_id))
	conn.commit()	
	conn.close()
	return 0

def getInviteID(group_id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT inviteID FROM messages WHERE grpID = '%d'" % (group_id))
	row = cursor.fetchone()[0]
	if row == None:
		return 1
	return row

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
		print(row[0])
		return row[0]
	else:
		return None

def editInvite(group_id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	invite_id = getInviteID(group_id)
	key = types.InlineKeyboardMarkup()
	key.add(types.InlineKeyboardButton("Присоединиться", callback_data='connect'))
	text = "Жми на кнопку, чтобы присоединиться к игре!\nИгроки: "
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
	cursor.execute("SELECT userID FROM spyID WHERE grpID = '%d'" % (group_id))
	bot.send_message(cursor.fetchone()[0], "Ты - шпион! Постарайся угадать место и напиши мне /answer.")
	conn.close()

def gameStarting(group_id):
	if getSpyID(group_id) != None:
		return
	if gameIsExisted(group_id) == 0:
		bot.delete_message(group_id, getInviteID(group_id))
		if givingRoles(group_id) == 1:
			bot.send_message(group_id, "Недостаточно игроков для начала игры")
			endGame(group_id)
			return 1
		givingWords(group_id)
		bot.send_message(group_id, "Начало игры!")
		t = threading.Thread(target=waitingUsers, name="Thread2Poll{}".format(str(group_id)), args=(group_id, 60))###################################################################################################################
		t.start()
		t.join()
		individualPoll(group_id)
		t = threading.Thread(target=waitingUsers, name="Thread2Poll{}".format(str(group_id)), args=(group_id, 60))###################################################################################################################
		t.start()
		t.join()
		if gameIsExisted(group_id) == 1:
			startGameResult(group_id)

def individualPoll(group_id):
	row = getGamersByGroupId(group_id)
	key = types.InlineKeyboardMarkup()
	for i in row:
		key = types.InlineKeyboardMarkup()
		for j in row:
			if i[0] == j[0]:
				continue
			if i[0] == getSpyID(group_id):
				continue
			key.add(types.InlineKeyboardButton(text=getNameFromGameRoom(j[0]), callback_data=str(j[0]) + "poll"))
		bot.send_message(i[0], "Выберите предполагаемого шпиона", reply_markup=key)

def getNumberFromCall(data, letter):
	num = ""
	for i in data:
		if i == letter:
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
	else:
		return None

def isSpy(group_id, user_id):
	if getSpyID(group_id) == user_id:
		return user_id
	else:
		return None

def startGameResult(group_id):
	row = maxdb(group_id)
	if len(row) > 1:
		randomNumber = random.randint(1, len(row))
		spy = isSpy(group_id, row[randomNumber - 1])
		if spy == None:
			bot.send_message(group_id, "Похоже шпион не был обнаружен!\n    Шпион: <a href='tg://user?id={}'>{}</a>".format(spy, getNameFromGameRoom(spy)), parse_mode='html')
		else:
			bot.send_message(group_id, "Поздравляем, вы нашли шпиона!\n    Шпион: <a href='tg://user?id={}'>{}</a>".format(spy, getNameFromGameRoom(spy)), parse_mode='html')
	else:
		spy = isSpy(group_id, row[0])
		if spy == None:
			bot.send_message(group_id, "Похоже шпион не был обнаружен!\n    Шпион: <a href='tg://user?id={}'>{}</a>".format(spy, getNameFromGameRoom(spy)), parse_mode='html')
		else:
			bot.send_message(group_id, "Поздравляем, вы нашли шпиона!\n    Шпион: <a href='tg://user?id={}'>{}</a>".format(spy, getNameFromGameRoom(spy)), parse_mode='html')
	endGame(group_id)

def getGroupbByUsersIDInGame(user_id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT grpID FROM gameRoom WHERE userID = '%d'" % (user_id))
	row = cursor.fetchone()
	conn.close()
	if row != None:
		return row[0]
	else:
		return None

def getNameFromGameRoom(user_id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT name FROM gameRoom WHERE userID = '%d'" % (user_id))
	row = cursor.fetchone()
	conn.close()
	if row != None:
		return row[0]
	else:
		return None

###########################
###### Group Handler ######
###########################

@bot.message_handler(commands=['start'])
def start(message):
	print(message)
	if message.chat.type == 'supergroup':
		print(1)
		if addGroup(message.chat.id) == 0:
			admSettings(message.chat.id)
		key = types.InlineKeyboardMarkup()
		key.add(types.InlineKeyboardButton("✔️", callback_data="permissions"))
		key.add(types.InlineKeyboardButton("Познакомимся?", url="t.me/findspy_bot"))
		bot.send_message(message.chat.id, "Привет! Я бот игры Шпион, для начала игры дай мне права администратора и перейдите в лс к боту!", reply_markup=key)
	if message.chat.type == 'private':
		addUser(message.from_user.id)

@bot.message_handler(commands=['game'])
def game(message):
	if message.chat.type == 'supergroup' and gameIsExisted(message.chat.id) == 1:
		key = types.InlineKeyboardMarkup()
		key.add(types.InlineKeyboardButton("Присоединиться", callback_data='connect'))
		bot.send_message(message.chat.id,"Жми на кнопку, чтобы присоединиться к игре!", reply_markup=key)
		t = threading.Thread(target=waitingUsers, name="Thread4Invite{}".format(str(message.chat.id)), args=(message.chat.id, 25))###################################################################################################################
		t.start()
		t.join()
		gameStarting(message.chat.id)

@bot.message_handler(commands=['game'])
def end(message):
	if message.chat.type == 'supergroup' and gameIsExisted(message.chat.id) == 1:
		endGame(message.chat.id)

@bot.callback_query_handler(func=lambda c:True)
def inline(c):
	print(c.data)
	if c.data == 'permissions':
		if checkPermissions(c.message.chat.id, c.message.from_user.id) == 0:
			bot.send_message(c.message.chat.id, "Отлично, права администратора получил. Для начала игры просто напишите /game")
	if c.data == 'connect':
		if str(c.from_user.id) in c.message.text:
			return
		if addUserToGame(c.message.chat.id, c.from_user.id, c.from_user.first_name) == 2:
			key = types.InlineKeyboardMarkup()
			key.add(types.InlineKeyboardButton("Познакомимся?", url="t.me/findspy_bot"))
			bot.send_message(c.message.chat.id, "<a href='tg://user?id={}'>{}</a> все еще не перешел в личный диалог!".format(c.message.from_user.id, c.message.from_user.first_name), parse_mode='html', reply_markup=key)
			return
		if getGamersByGroupId(c.message.chat.id) != None and getNumberOfGamersByGroupId(c.message.chat.id) != None:
			if len(getGamersByGroupId(c.message.chat.id)) == getNumberOfGamersByGroupId(c.message.chat.id) - 1:
				inviteID(c.message.chat.id, c.message.message_id)
				editInvite(c.message.chat.id)
				gameStarting(c.message.chat.id)
		inviteID(c.message.chat.id, c.message.message_id)
		editInvite(c.message.chat.id)
	if "poll" in c.data:
		bot.edit_message_text("Вы сделали свой выбор!", c.message.chat.id, c.message.message_id)
		pollHandler(getGroupbByUsersIDInGame(c.from_user.id), c.from_user.id, c.data)
		
		

	
bot.polling(none_stop=True)