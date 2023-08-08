import logging


def setup_logger(name: str, file=None, level='INFO'):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    date_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter('%(asctime)s\t%(name)-16s\t%(levelname)8s:\t%(message)s', datefmt=date_fmt)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if file is not None:
        file_handler = logging.FileHandler(file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
