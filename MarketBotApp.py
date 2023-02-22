from gui_v2 import MarketCSGOBotApp
from logging import getLogger, StreamHandler

# Application entrypoint
if __name__ == '__main__':
    logger = getLogger('market_bot')
    logger.addHandler(StreamHandler())
    logger.setLevel('INFO')

    app = MarketCSGOBotApp()
    app.mainloop()
