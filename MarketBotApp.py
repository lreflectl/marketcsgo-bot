from gui_v2 import MarketCSGOBotApp
import logging


def setup_logging():
    logger = logging.getLogger('market_bot')
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%y-%m-%d %H:%M:%S')

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.setLevel('INFO')


# Application entrypoint
if __name__ == '__main__':
    setup_logging()
    app = MarketCSGOBotApp()
    app.mainloop()
