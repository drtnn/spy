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

class thread_with_trace(threading.Thread): 
  def __init__(self, *args, **keywords): 
    threading.Thread.__init__(self, *args, **keywords) 
    self.killed = False
  
  def start(self): 
    self.__run_backup = self.run 
    self.run = self.__run       
    threading.Thread.start(self) 
  
  def __run(self): 
    sys.settrace(self.globaltrace) 
    self.__run_backup() 
    self.run = self.__run_backup 
  
  def globaltrace(self, frame, event, arg): 
    if event == 'call': 
      return self.localtrace 
    else: 
      return None
  
  def localtrace(self, frame, event, arg): 
    if self.killed: 
      if event == 'line': 
        raise SystemExit() 
    return self.localtrace 
  
  def kill(self): 
    self.killed = True

def ThreadGG():
	t = thread_with_trace(target=control_message, name="Thread2", args=("4", 5))
	# t = threading.Thread(target=control_message, name="Thread2", args=("4", 5))
	t.start()
	print(t.is_alive())
	t.kill()
	print(t.is_alive())

def control_message(mes, timing):
	time.sleep(timing)
	print("ok")

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
	
def maxdb(group_id):
	conn = sqlite3.connect('baza.sqlite', check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("Select onUserID, count(*) FROM poll WHERE grpID = ('%d') GROUP BY onUserID" % (group_id))
	row = cursor.fetchall()
	print(row)
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

def startGameResult(group_id):
	row = maxdb(group_id)
	print(row)
	if len(row) != 1:
		randomNumber = random.randint(1, len(row))
		spy = isSpy(group_id, row[randomNumber - 1])
		if spy == None:
			print(1)
		else:
			print(2)
	else:
		spy = isSpy(group_id, row[0])
		if spy == None:
			print(3)
		else:
			print(4)



def individualPoll(group_id):
	row = [(111,), (222, ),(333,) ,(444, ),(555, )]
	for i in row:
		for j in row:
			if i[0] == j[0]:
				continue
			if i[0] == getSpyID(group_id):
				continue
			print(j[0])

# individualPoll(1)

def fun(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1
    p = 0
    for i in range(len(s1)):
        if s1[i] == s2[i]:
            p += 1
    return str(int(p/len(s1)*100))+'%'


def whenToEndPoll(group_id, endTime):
	print(group_id)
	print(endTime)
	timing = 0
	while timing <= endTime:
		time.sleep(3)
		timing += 3
		print("whenToEndPoll")
	print(group_id)

t = threading.Thread(target=whenToEndPoll, name="Thread2EndPoll{}".format(str(11)), args=(11, 120))###################################################################################################################
t.start()



