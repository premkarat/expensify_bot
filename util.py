import os

import pdfplumber

from config import Config, bot, logger


stack = []


def delete_all_previous_messages():
    global stack
    while stack:
        bot.delete_message(Config.TELEGRAM.CHAT_ID, stack.pop())


def send_message(msg, markup=None):
    global stack
    delete_all_previous_messages()
    msg = bot.send_message(Config.TELEGRAM.CHAT_ID, msg, reply_markup=markup)
    stack.append(msg.id)


def reply_to(msg, message):
    global stack
    delete_all_previous_messages()
    msg = bot.reply_to(msg, message)
    stack.append(msg.id)


def pdf2txt(pdf):
    with pdfplumber.open(pdf) as pdf:
        page = pdf.pages[0]
        return page.extract_text()


def cleanup(expenses):
    for expense in expenses:
        os.remove(expense.pdf)
        expense.delete()

    logger.info('Remove PDFs: [OK]')