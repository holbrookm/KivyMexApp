#!/usr/bin/python/
import time
import sys

global  F_DEBUG
global MAC_FLAG
  
    
F_DEBUG = 1

def sleep(stringarg):
    if F_DEBUG:
        time.sleep(stringarg)
        pass


def p(stringarg):
    if F_DEBUG:
        print stringarg
        pass

def getflag(): return F_DEBUG

def mac(): 
    if sys.platform == 'darwin':
        MAC_FLAG = True
    else:
        MAC_FLAG = False

    return MAC_FLAG
    
