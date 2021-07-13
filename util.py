import os

import pdfplumber

from config import logger


def pdf2txt(pdf):
    with pdfplumber.open(pdf) as pdf:
        page = pdf.pages[0]
        return page.extract_text()


def cleanup(expenses):
    for expense in expenses:
        os.remove(expense.pdf)
        expense.delete()

    logger.info('Remove PDFs: [OK]')