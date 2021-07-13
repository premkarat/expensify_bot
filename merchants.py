from abc import ABCMeta, abstractmethod
from datetime import datetime
import re

from config import Config, logger


_providers = {}
class ProviderMeta(ABCMeta):
    def __init__(cls, clsname, bases, methods):
        super().__init__(clsname, bases, methods)
        if hasattr(cls, 'name'):
            _providers[cls.name] = cls


class Provider(metaclass=ProviderMeta):
    @abstractmethod
    def extract_expense_data(self, expense):
        pass


class Airtel(Provider):
    name = 'Airtel'

    def extract_expense_data(self, expense):
        logger.info('Extacting date & amount from airtel bill...')
        date = re.findall(Config.PATTERN.AIRTEL.DATE, expense)
        for DT_FMT in Config.PATTERN.AIRTEL.DT_FMTS:
            date = datetime.strptime(date[0], DT_FMT) if date else None
            if date:
                break
        date = datetime.strftime(date, Config.PATTERN.DATE_STR_FMT) if date else None
        amount = re.findall(Config.PATTERN.AIRTEL.TOTAL, expense)
        amount = float(amount[0].replace(',', '')) if amount else None
        logger.info('Airtel: Date -> {}, Amount -> {}'.format(date, amount))

        return (date, amount)


class Vodafone(Provider):
    name = 'Vodafone'

    def extract_expense_data(self, expense):
        logger.info('Extacting date & amount from vodafone bill...')
        date = re.findall(Config.PATTERN.VODAFONE.DATE, expense)
        date = datetime.strptime(date[0], Config.PATTERN.VODAFONE.DT_FMT) if date else None
        date = datetime.strftime(date, Config.PATTERN.DATE_STR_FMT) if date else None

        amount = re.findall(Config.PATTERN.VODAFONE.TOTAL, expense)
        amount = float(amount[0].replace(',', '')) if amount else None
        logger.info('Vodafone: Date -> {}, Amount -> {}'.format(date, amount))

        return (date, amount)


def create_provider(name):
    provider = _providers.get(name)
    return provider() if provider else None