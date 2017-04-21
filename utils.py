import logging
import sys


def init_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S')
    file_handler = logging.FileHandler(name + ".log")
    file_handler.setFormatter(formatter)
    std_handler = logging.StreamHandler(sys.stdout)
    std_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(std_handler)
    return logger