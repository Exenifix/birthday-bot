from datetime import date, datetime

from disnake.ext.commands import Converter, converter_method

from modules.exceptions import DateConversionFailure, ShortDateConversionFailure


class Date(Converter):
    FORMAT = "%d.%m.%Y"
    SHORT_FORMAT = "%d.%m"

    def __init__(self, date: date):
        self._date = date

    @classmethod
    def from_str(cls, arg: str):
        try:
            date = datetime.strptime(arg, Date.FORMAT).date()
            if date is None:
                raise ValueError()

            return cls(date)

        except ValueError:
            raise DateConversionFailure(arg)

    @classmethod
    def now(cls):
        return cls(datetime.now().date())

    @converter_method
    async def convert(cls, _, arg: str):
        return Date.from_str(arg)

    def to_str(self):
        return self.__str__()

    def __str__(self):
        return self._date.strftime(Date.FORMAT)

    def to_short_str(self):
        return self._date.strftime(Date.SHORT_FORMAT)


class ShortDate(Date):
    @classmethod
    def from_str(cls, arg: str):
        try:
            date = datetime.strptime(arg, Date.SHORT_FORMAT).date()
            if date is None:
                raise ValueError()

            return cls(date)

        except ValueError:
            raise ShortDateConversionFailure(arg)

    @converter_method
    async def convert(cls, _, arg: str):
        return ShortDate.from_str(arg)
