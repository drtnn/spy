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
import sys
import validators

conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('SELECT userID FROM users')
row = cursor.fetchall()
conn.close()
for i in row:
	print(i[0])