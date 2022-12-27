import customtkinter as ctk
from bot import MarketBot, price_update_loop
from threading import Thread, Event


class MarketCSGOBotApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.bot = MarketBot()
        self.stop_event = Event()
        self.finish_event = Event()

        self.title('MarketCSGO Bot')
        self.geometry(f'{600}x{400}')

        self.items_frame = ctk.CTkFrame(self, width=600, height=330, corner_radius=0)
        self.items_frame.grid(row=0, column=0, columnspan=2)

        self.start_loop_button = ctk.CTkButton(self, command=self.start_loop_thread, text='Start updating prices')
        self.start_loop_button.grid(row=1, column=1, padx=20, pady=20)

        self.stop_loop_button = ctk.CTkButton(self, command=self.stop_loop_thread, text='Stop', state='disabled')
        self.stop_loop_button.grid(row=1, column=0, padx=20, pady=20)

    def start_loop_thread(self):
        self.start_loop_button.configure(state='disabled')
        self.stop_loop_button.configure(state='normal')

        worker_thread = Thread(target=price_update_loop, args=(self.bot, self.stop_event, self.finish_event))
        worker_thread.start()

    def stop_loop_thread(self):
        self.stop_event.set()

        def toggle_buttons_on_finish():
            self.finish_event.wait()
            self.start_loop_button.configure(state='normal')

        toggling_thread = Thread(target=toggle_buttons_on_finish)
        toggling_thread.start()

        self.stop_loop_button.configure(state='disabled')


def main():
    app = MarketCSGOBotApp()
    app.mainloop()


if __name__ == "__main__":
    main()
