from time import sleep
from requests import get as rget
from os import environ
from logging import error as logerror

BASE_URL = environ.get('BASE_URL_OF_BOT', None)
try:
    if len(BASE_URL) == 0: raise TypeError
    if BASE_URL.endswith('/'): BASE_URL = BASE_URL.rstrip('/')
except TypeError: BASE_URL = None
PORT = environ.get('PORT', None)
if PORT and BASE_URL:
    while True:
        try:
            rget(BASE_URL).status_code
            sleep(600)
        except Exception as e:
            logerror(f"alive.py: {e}")
            sleep(2)
            continue
