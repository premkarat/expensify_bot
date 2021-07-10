import logging
import signal
import sys
import time

from telebot.types import InlineKeyboardMarkup as IKM
from telebot.types import InlineKeyboardButton as IKB
import telebot

from config import Config
import util


bot = telebot.TeleBot(Config.TELEGRAM.API_KEY)
logger = telebot.logger
logger.setLevel(logging.INFO)


def download_pdf_from_telegram(msg):
    file_info = bot.get_file(msg.document.file_id)
    data = bot.download_file(file_info.file_path)
    pdf = util.tmpdir.name + '/' + file_info.file_unique_id + '.pdf'
    with open(pdf, 'wb') as f:
        f.write(data)
    return pdf


def is_done_reply():
    markup = IKM()
    markup.row_width = 2
    markup.add(IKB("Yes", callback_data="yes"),
               IKB("No", callback_data="no"))
    return markup


def check_response(call):
    return True if call.data in ['yes', 'no'] else False


@bot.callback_query_handler(func=check_response)
def callback_query(call):
    if call.data == "yes":
        bot.send_message(call.message.chat.id, "Generating expensify report")
        #TODO
        #create_expensify_report()
    else:
        bot.send_message(call.message.chat.id, "Upload next expense")


def check_pdf(m):
    return m.document.mime_type == 'application/pdf'


@bot.edited_message_handler(func=check_pdf, content_types=['document'])
@bot.message_handler(func=check_pdf, content_types=['document'])
def expense_handler(msg):
    expense_type = msg.caption.lower() if msg.caption else None
    if not expense_type or expense_type not in Config.TELEGRAM.VALID_CAPTIONS:
        bot.reply_to(msg, "Caption = Phone or Internet?\nEdit msg & provide caption")
    else:
        pdf = download_pdf_from_telegram(msg)
        util.db.save(pdf, expense_type)
        bot.send_message(msg.chat.id, "Done?", reply_markup=is_done_reply())


def signal_handler(signal_number, frame):
    bot.stop_polling()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
while True:
    try:
        bot.polling(none_stop=False, interval=0)
    except Exception as e:
        logger.info(e)
        time.sleep(10)