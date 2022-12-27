import customtkinter as ctk
from bot import MarketBot, price_update_loop
from threading import Thread, Event


class MarketCSGOBotApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.bot = MarketBot()
        self.stop_event = Event()

        self.title('MarketCSGO Bot')
        self.minsize(400, 300)

        self.start_loop_button = ctk.CTkButton(master=self, command=self.start_loop_thread, text='Start updating prices')
        self.start_loop_button.pack(padx=20, pady=20)

        self.stop_loop_button = ctk.CTkButton(master=self, command=self.stop_loop_thread, text='Stop')
        self.stop_loop_button.pack(padx=20, pady=20)

    def start_loop_thread(self):
        worker_thread = Thread(target=price_update_loop, args=(self.bot, self.stop_event))
        worker_thread.start()

    def stop_loop_thread(self):
        self.stop_event.set()


def main():
    app = MarketCSGOBotApp()
    app.mainloop()


if __name__ == "__main__":
    main()
