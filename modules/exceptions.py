from disnake.ext.commands import CommandError


class DateConversionFailure(CommandError):
    def __init__(self, date: str):
        super().__init__(
            f"Could not convert {date} to date. Please follow the following format: DD.MM.YYYY (eg. 24.09.2001)"
        )


class ShortDateConversionFailure(DateConversionFailure):
    def __init__(self, date: str):
        super().__init__(
            f"Could not convert {date} to date. Please follow the following format: DD.MM (eg. 24.09)"
        )
