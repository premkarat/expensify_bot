import logging
import os

import tempfile
import telebot

from database import DB
import pdfplumber

logger = telebot.logger
logger.setLevel(logging.INFO)
db = DB()
tmpdir = tempfile.TemporaryDirectory(dir=os.getcwd())