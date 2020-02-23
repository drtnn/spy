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
import random

#random.randint(<Начало>, <Конец>)

token = "1084976464:AAGj6yatNDYgQIi1eoqlNrzUPxRqRreQ318"
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def hello(message):
	# print(message)
	print(bot.get_chat_member(message.chat.id, message.from_user.id).status)#############################
	print(bot.get_chat_administrators(message.chat.id))
	adms = bot.get_chat_administrators(message.chat.id)
	print(adms[1].status)
	print(adms[1].user.id)##################################################


@bot.message_handler(content_types=["text"])
def gg(message):
	key = types.InlineKeyboardMarkup()
	btn = types.InlineKeyboardButton("anything", callback_data="test")
	key.add(btn)
	bot.send_message(message.chat.id, "<a href='tg://user?id={}'>inline mention of a user</a>".format(message.from_user.id), reply_markup=key, parse_mode='html')
	# print(bot.get_chat_administrators(message.chat.id))
	# print(bot.get_chat_member(message.chat.id, message.from_user.id))

	# print(message)
	# print(bot.c)
	# user = types.ChatMember()

# В большинстве случаев целесообразно разбить этот хэндлер на несколько маленьких
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
	# Если сообщение из чата с ботом
	if call.message:
		if call.data == "test":
			print(bot.get_chat_member(call.message.chat.id, call.message.from_user.id))
			print(bot.get_chat(call.message.chat.id))

def admSettings():
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("INSERT INTO settings (grpID, userID, time) VALUES ('%d', '%d', '%d')" % (4, 7, 5))
	# cursor.execute("UPDATE settings SET time = ('%d') WHERE grpID = 10" % (5))############################
	conn.commit()
	conn.close()

bot.polling(none_stop=True)