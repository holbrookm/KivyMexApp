#!/usr/bin/python

import sys, string, logging, os

try:
  os.remove('./mex.log')
except:
  pass

#logging levels:
CRITICAL=50
ERROR=40
WARNING=30
NOTICE=25
INFO=20
INFO1=15
DEBUG=10
DEBUG1=5


FILE_LEVEL=DEBUG
CONSOLE_LEVEL=ERROR

#FORMAT = "%(levelname)s l: %(lineno)d: %(message)s"
#FORMAT = "%(levelname)s | %(module)s |  %(message)s"
#logging.basicConfig(format=FORMAT)
#FORMAT = "%(levelname)s | %(module)s | %(name)s | %(message)s"
FORMAT = "%(asctime)s %(levelname)s | %(module)s | %(name)s | %(message)s"
#logging.basicConfig(format=FORMAT)
logging.basicConfig(filename='./prov.log',format=FORMAT)
logging.addLevelName(15, "INFO1")
logging.addLevelName(5, "DEBUG1")
logging.addLevelName(25, "NOTICE")

console = logging.StreamHandler()
console.setLevel( CONSOLE_LEVEL )
formatter =logging.Formatter(FORMAT)
console.setFormatter( formatter )
logging.getLogger('').addHandler(console)

logger = logging.getLogger()
logger.setLevel( FILE_LEVEL )
