import logging

class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    blue = "\x1b[34;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime).19s - %(levelname)s - %(message)s"

    FORMATS = {
        logging.DEBUG: format.replace("%(levelname)s", grey + "%(levelname)s" + reset),
        logging.INFO: format.replace("%(levelname)s", blue + "%(levelname)s" + reset),
        logging.WARNING: format.replace("%(levelname)s", yellow + "%(levelname)s" + reset),
        logging.ERROR: format.replace("%(levelname)s", red + "%(levelname)s" + reset),
        logging.CRITICAL: format.replace("%(levelname)s", bold_red + "%(levelname)s" + reset)
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
    
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

ch.setFormatter(CustomFormatter())

logger.addHandler(ch)