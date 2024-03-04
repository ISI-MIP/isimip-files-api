import logging
from pathlib import Path

from flask.logging import default_handler

import colorlog


def configure_logging(app):
    app.logger.removeHandler(default_handler)
    app.logger.setLevel(app.config['LOG_LEVEL'].upper())

    # log to the console in development
    if app.config['ENV'] == 'development':
        formatter = colorlog.ColoredFormatter('%(log_color)s[%(asctime)s] %(levelname)s'
                                              ' %(filename)s:%(funcName)s %(message)s')

        handler = colorlog.StreamHandler()
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)

        app.logger.addHandler(handler)

    # log to a file
    if app.config['LOG_PATH']:
        log_path = Path(app.config['LOG_PATH'])
        if log_path.exists:
            formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')

            handler = logging.FileHandler(log_path / 'app.log', 'a')
            handler.setLevel(logging.DEBUG)
            handler.setFormatter(formatter)

            app.logger.addHandler(handler)
        else:
            raise RuntimeError('LOG_PATH does not exist')

    # disable logger if not handlers are set
    if not app.logger.handlers:
        app.logger.disabled = True
