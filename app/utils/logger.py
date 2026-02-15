import logging
import colorlog
import sys

LOG_FORMAT = "%(log_color)s[%(levelname)s] [%(filename)s:%(lineno)d] %(reset)s%(message)s"

def setup_logger():
    if logging.getLogger().hasHandlers():
        return logging.getLogger("regamsa")

    handler = colorlog.StreamHandler(sys.stdout)
    handler.setFormatter(colorlog.ColoredFormatter(
        LOG_FORMAT,
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'blue',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    ))

    logger = colorlog.getLogger("regamsa")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    return logger

# Logger instance
logger = setup_logger()