#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8
from __future__ import unicode_literals
import aiogram
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
# .types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
# import telebot
# from telebot import types
# from telebot import apihelper
import datetime
import json
import sqlite3
from string import ascii_letters
import random				#random.randint(<Начало>, <Конец>)
import time
import threading
import subprocess

TOKEN = "941639396:AAFPJMdmcMhXWtniZbJeE0DeuBvykLu6Ve8" #test_token

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
	await message.reply("Привет!\nНапиши мне что-нибудь!")
	await message.reply("Напиши мне что-нибудь!")
	dp.register_message_handler()



def main():
    executor.start_polling(dp)


if __name__ == '__main__':
    executor.start_polling(dp)