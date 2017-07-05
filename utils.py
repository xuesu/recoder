import logging
import sys
import traceback

DATE_FORMAT = "%m-%d"
DATETIME_FORMAT = "{} %H:%M".format(DATE_FORMAT)


def init_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)s: %(asctime)s %(levelname)-8s %(filename)s[line:%(lineno)d] %(message)s',
                                  '%a, %d %b %Y %H:%M:%S')
    file_handler = logging.FileHandler(name + ".log")
    file_handler.setFormatter(formatter)
    std_handler = logging.StreamHandler(sys.stdout)
    std_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(std_handler)
    return logger


def describe_error(e):
    traceback.print_exc()
    return '{}_{}'.format(type(e), e.message)
