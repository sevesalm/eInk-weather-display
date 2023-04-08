import logging
import enum


# Custom RGB colors for log output
class CustomColors(str, enum.Enum):
    gray = "\x1b[38;2;150;150;150m"
    blue = "\x1b[38;2;80;150;255m"
    green = "\x1b[38;2;10;255;40m"
    yellow = "\x1b[38;2;255;255;20m"
    orange = "\x1b[38;2;255;155;20m"
    red = "\x1b[38;2;255;50;30m"
    red_reversed = "\x1b[38;2;255;50;30;7m"
    reversed = "\x1b[7m"
    reset = "\x1b[0m"


class LogFormatter(logging.Formatter):
    __formats = {
        logging.DEBUG: CustomColors.blue,
        logging.INFO: CustomColors.green,
        logging.WARNING: CustomColors.yellow,
        logging.ERROR: CustomColors.red,
        logging.CRITICAL: CustomColors.red_reversed,
    }

    def __get_format_string(self, color: str) -> str:
        return f'{CustomColors.orange}%(asctime)s{CustomColors.reset} {color}%(levelname)8s{CustomColors.reset} {CustomColors.gray}%(name)-22s{CustomColors.reset}  %(message)s'

    def format(self, record):
        format_str = self.__get_format_string(self.__formats.get(record.levelno, CustomColors.reversed))
        formatter = logging.Formatter(format_str)
        return formatter.format(record)
