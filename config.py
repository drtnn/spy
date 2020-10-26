import telebot
from telebot import types
from telebot import apihelper
import datetime
import sqlite3
import random				#random.randint(<Начало>, <Конец>)
import time
import threading
import validators
import yadisk

y = yadisk.YaDisk(token="AgAAAAAE0s-AAAapnFNsYjAaokDEhJVgXUo0WGI")
token = "1084976464:AAGj6yatNDYgQIi1eoqlNrzUPxRqRreQ318"
# token = "941639396:AAFPJMdmcMhXWtniZbJeE0DeuBvykLu6Ve8" #test_token
bot = telebot.TeleBot(token)
