from datetime import datetime
import json
import requests

from config import Config, bot, logger
from  database import Expense
import util
import merchants


class Expensify:
    def __init__(self, chatid) -> None:
        self._url = Config.EXPENSIFY.API_URL
        self._userid = Config.EXPENSIFY.USERID
        self._secret = Config.EXPENSIFY.SECRET
        self._emailid = Config.EXPENSIFY.EMP_MAILID
        self._policyid = Config.EXPENSIFY.POLICYID
        self.chatid = chatid

    def generate_report_payload(self, expenses):
        ts = datetime.now().strftime(Config.EXPENSIFY.REPORT_FMT)
        title = Config.EXPENSIFY.REPORT_NAME + ts
        return {
            "requestJobDescription": json.dumps({
                "type": "create",
                "credentials": {
                    "partnerUserID": self._userid,
                    "partnerUserSecret": self._secret
                    },
                "inputSettings": {
                    "type": "report",
                    "policyID": self._policyid,
                    "report": {"title": title},
                    "employeeEmail": self._emailid,
                    "expenses": expenses
                    }
                })
            }

    def generate_expense_payload(self, date, merchant, amount, category):
        return {
            "date": date,
            "currency": Config.EXPENSIFY.CURRENCY,
            "merchant": merchant,
            "amount": int(amount * 100),
            "tag": "Non-Travel Related Expense",
            "Category": category
            }

    def create(self, payload):
        response = requests.post(self._url, data=payload)
        logger.info('API response: {}'.format(response.json()))
        if response.status_code != 200:
            return self.__raise_create_report_error(response)

        response = response.json()
        report = response.get('reportName')
        reportid = response.get('reportID')
        logger.info("Created report: {}".format(report))

        return report, reportid

    def __raise_create_report_error(self, response):
        logger.error(Config.EXPENSIFY.ERR.CREATE + ':' + response.content)
        bot.send_message(self.chatid, Config.EXPENSIFY.ERR.CREATE)
        return None


def create_expensify_report(chatid):
    logger.info('Generating expensify report...')
    expenses = Expense.get_all()

    pdfs = [e.pdf for e in expenses]
    logger.info('List of PDFs: {}'.format(pdfs))

    for expense in expenses:
        expense.txt = util.pdf2txt(expense.pdf)
    Expense.save_all(expenses)

    txts = [e.txt for e in expenses]
    logger.info('List of TXTs: {}'.format(txts))

    report = _create_expensify_report(chatid, expenses)

    util.cleanup(expenses)

    return report


def _create_expensify_report(chatid, expenses):
    expensify = Expensify(chatid)

    logger.info('Generating expensify payload...')
    payload = _generate_expensify_payload(expenses, expensify)
    if not payload:
        return None

    logger.info('Expensify Payload: {}'.format(payload))
    report, reportid = expensify.create(payload)
    if report is None:
        return None


def _generate_expensify_payload(expenses, expensify):
    logger.info('Extracting expense data...')
    expenses = _extract_expense_data(expenses)
    if not expenses:
        return None
    logger.info('Extracted expenses: [OK]')

    expenses = [expensify.generate_expense_payload(
                    e.date, e.merchant, e.amount, e.category)
                for e in expenses]
    return expensify.generate_report_payload(expenses)


def _extract_expense_data(expenses):
    merchant = None
    for expense in expenses:
        for k, v  in Config.EXPENSIFY.MERCHANTS.items():
            if k in expense.txt:
                merchant = v
                break

        if not merchant:
            return None

        provider = merchants.create_provider(merchant)
        if not provider:
            return None

        date, amount = provider.extract_expense_data(expense.txt)
        if not date or not amount:
            return None

        expense.date = date
        expense.merchant = merchant
        expense.amount = amount

    Expense.save_all(expenses)
    return expenses