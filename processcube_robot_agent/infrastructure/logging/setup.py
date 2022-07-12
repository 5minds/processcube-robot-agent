import logging


def setup_logging(log_level=logging.INFO):
    
    format_template = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=log_level, format=format_template)

    return logging.getLogger()