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
		return 1
	cursor.execute("SELECT userID FROM users WHERE userID = '%d'" % (user_id))
	if cursor.fetchone() == None:
		return 2
	cursor.execute("INSERT INTO gameRoom (grpID,userID, name) VALUES ('%d','%d', '%s')" % (group_id, user_id, name))
	conn.commit()	
	conn.close()
	return 0

def isGameExisted(group_id):
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
	if cursor.fetchone() != None:
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
	if numOfGamers < 4:
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
	conn.commit()	
	conn.close()

def admSettings(group_id):
	adms = bot.get_chat_administrators(group_id)
	for i in adms:
		if i.status == 'creator':
			conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
			cursor = conn.cursor()
			cursor.execute("INSERT INTO settings (grpID, userID, time) VALUES ('%d', '%d', '%d')" % (group_id, i.user.id, 5))
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

# def waiting
#tg://user?id=<user_id>

###########################
###### Group Handler ######
###########################

@bot.message_handler(commands=['start'])
def start(message):
	if message.chat.type == 'supergroup':
		if addGroup(message.chat.id) == 0:
			admSettings(message.chat.id)
		key = types.InlineKeyboardMarkup()
		key.add(types.InlineKeyboardButton("✔️", callback_data="permissions"))
		key.add(types.InlineKeyboardButton("Познакомимся?", url="t.me/findspy_bot"))
		bot.send_message(message.chat.id, "Привет! Я бот игры Шпион, для начала игры дай мне права администратора и перейдите в лс к боту!", reply_markup=key)
	if message.chat.type == 'private':
		addUser(message.from_user.id)

@bot.message_handler(commands=['game'])
def startGame(message):
	if message.chat.type == 'supergroup' and isGameExisted(message.chat.id) == 1:
		key = types.InlineKeyboardMarkup()
		key.add(types.InlineKeyboardButton("Присоединиться", callback_data='connect'))
		bot.send_message(message.chat.id,"Жми на кнопку, чтобы присоединиться к игре!", reply_markup=key)


@bot.callback_query_handler(func=lambda c:True)
def inline(c):
	if c.data == 'permissions':
		if checkPermissions(c.message.chat.id, c.message.from_user.id) == 0:
			bot.send_message(c.message.chat.id, "Отлично, права администратора получил. Для начала игры просто напишите /game")
	if c.data == 'connect':
		if addUserToGame(c.message.chat.id, c.from_user.id, c.from_user.first_name) == 2:
			key = types.InlineKeyboardMarkup()
			key.add(types.InlineKeyboardButton("Познакомимся?", url="t.me/findspy_bot"))
			bot.send_message(c.message.chat.id, "<a href='tg://user?id={}'>{}</a> все еще не перешел в личный диалог!".format(c.message.from_user.id, c.message.from_user.first_name), parse_mode='html', reply_markup=key)
			return
		inviteID(c.message.chat.id, c.message.message_id)
		editInvite(c.message.chat.id)
		
		

	
bot.polling(none_stop=True)