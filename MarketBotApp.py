from gui_v2 import MarketCSGOBotApp

# Application entrypoint
if __name__ == '__main__':
    app = MarketCSGOBotApp()
    app.after(100, app.post_init)  # Wait for UI and initialize bot
    app.mainloop()
