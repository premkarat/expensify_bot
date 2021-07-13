from datetime import datetime
import json
import requests
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webbot import Browser

from config import Config, bot, logger
from  database import Expense
import util
import merchants


class Expensify:
    def __init__(self) -> None:
        self._url = Config.EXPENSIFY.API_URL
        self._userid = Config.EXPENSIFY.USERID
        self._secret = Config.EXPENSIFY.SECRET
        self._emailid = Config.EXPENSIFY.EMP_MAILID
        self._policyid = Config.EXPENSIFY.POLICYID
        self.chatid = Config.TELEGRAM.CHAT_ID
        self.web = None

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

    def login(self):
        logger.info('Opening Expensify...')
        self.web = Browser(showWindow=False)
        self.web.go_to(Config.EXPENSIFY.URL)

        if not self._wait_for('Email'):
            return self.__raise_login_error()
        self.web.click(text="Email")
        self.web.type(self._emailid, into="email", id="login")
        self.web.click(text="Next")

        if not self._wait_for('Sign In'):
            return self.__raise_login_error()
        logger.info('Signing in...')
        self.web.type(Config.OKTA.USERNAME, into="username")
        self.web.type(Config.OKTA.PASSWORD, into="password")
        self.web.click(text="Sign In")

        if not self._wait_for('Send Push'):
            return self.__raise_login_error()
        util.send_message(Config.TELEGRAM.MESSAGE.OKTA_APPROVAL)
        self.web.click(text="Send Push")
        logger.info('Waiting for OKTA approval...')

        return True

    def open_report(self, report):
        if not self._wait_for('Inbox', tag='a', id='page_inbox'):
            return self.__raise_open_report_error(report)
        util.send_message(Config.TELEGRAM.MESSAGE.OKTA_APPROVED)
        self.web.click('Inbox', tag='a', id='page_inbox')

        logger.info('Opening report {}...'.format(report))
        if not self._wait_for(report):
            return self.__raise_open_report_error(report)
        self.web.click(text=report)
        logger.info('Report {} opened'.format(report))

        return True

    def upload_receipt(self, report, reportid):
        util.send_message('Uploading receipts...')
        receipts = Expense.get_all_receipts()
        for receipt in receipts:
            if not self._wait_for(label='::before', xpath=Config.EXPENSIFY.XPATH.EXPENSES):
                return self.__raise_upload_receipt_error(report)

            expense = self.web.driver.find_element_by_xpath(Config.EXPENSIFY.XPATH.EXPENSES)
            if not expense:
                return self.__raise_upload_receipt_error(report)

            try:
                expense.click()
                attach = self.web.driver.find_element_by_xpath(Config.EXPENSIFY.XPATH.ATTACH)
                self.web.driver.switch_to.active_element
                logger.info('Uploading receipt: {}'.format(receipt))
                attach.send_keys(receipt)

                WebDriverWait(self.web.driver, 60).until_not(
                    EC.visibility_of_element_located((By.ID, Config.EXPENSIFY.XPATH.LOAD_IMAGE)))
                WebDriverWait(self.web.driver, 60).until(
                    EC.element_to_be_clickable((By.XPATH, Config.EXPENSIFY.XPATH.DELETE)))
            except Exception:
                return self.__raise_upload_receipt_error(report)

        return self.__send_success_message(report, reportid)

    def logout(self):
        self.web.driver.quit()
        self.web.driver.stop_client()

    def _wait_for(self, label='', tag='button', classname='',
                  id='', number=1, xpath='', timeout=60):
        for _ in range(timeout):
            if self.web.exists(text=label, id=id, classname=classname,
                               tag=tag, number=number, xpath=xpath):
                return True
            time.sleep(1)
        return False

    def __send_success_message(self, report, reportid):
        logger.info('Uploading all receipts: [OK]')
        util.delete_all_previous_messages()
        bot.send_message(
            self.chatid,
            Config.TELEGRAM.MESSAGE.REPORT_CREATED.format(reportid, report),
            parse_mode="HTML")
        return True

    def __raise_create_report_error(self, response):
        util.delete_all_previous_messages()
        logger.error(Config.EXPENSIFY.ERR.CREATE + ':' + response.content)
        bot.send_message(self.chatid, Config.EXPENSIFY.ERR.CREATE)
        return None

    def __raise_login_error(self):
        util.delete_all_previous_messages()
        logger.error(Config.EXPENSIFY.ERR.LOGIN)
        bot.send_message(self.chatid, Config.EXPENSIFY.ERR.LOGIN)
        return False

    def __raise_open_report_error(self, report):
        util.delete_all_previous_messages()
        logger.error(Config.EXPENSIFY.ERR.REPORT)
        bot.send_message(self.chatid,
                         Config.EXPENSIFY.ERR.REPORT.format(report))
        return False

    def __raise_upload_receipt_error(self, report):
        util.delete_all_previous_messages()
        logger.error(Config.EXPENSIFY.ERR.RECEIPT)
        bot.send_message(self.chatid,
                         Config.EXPENSIFY.ERR.RECEIPT.format(report))
        return False


def create_expensify_report():
    logger.info('Generating expensify report...')
    expenses = Expense.get_all()

    pdfs = [e.pdf for e in expenses]
    logger.info('List of PDFs: {}'.format(pdfs))

    for expense in expenses:
        expense.txt = util.pdf2txt(expense.pdf)
    Expense.save_all(expenses)

    txts = [e.txt for e in expenses]
    logger.info('List of TXTs: {}'.format(txts))

    report = _create_expensify_report(expenses)

    util.cleanup(expenses)

    return report


def _create_expensify_report(expenses):
    expensify = Expensify()

    logger.info('Generating expensify payload...')
    payload = _generate_expensify_payload(expenses, expensify)
    if not payload:
        return None

    logger.info('Expensify Payload: {}'.format(payload))
    report, reportid = expensify.create(payload)
    if report is None:
        return None

    if not expensify.login():
        expensify.logout()
        return None

    if not expensify.open_report(report):
        expensify.logout()
        return None

    if not expensify.upload_receipt(report, reportid):
        report = None

    expensify.logout()
    return report


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