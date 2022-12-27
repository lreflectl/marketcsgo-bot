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
        self.geometry(f'{800}x{400}')

        self.items_frame = ctk.CTkFrame(self, width=800, height=330, corner_radius=0)
        self.items_frame.grid(row=0, column=0, columnspan=3)
        self.items_frame.grid_propagate(0)

        self.info_label = ctk.CTkLabel(self.items_frame, width=520, text='Item info')
        self.info_label.grid(row=0, column=0, padx=20, pady=2)
        self.min_label = ctk.CTkLabel(self.items_frame, width=60, text='Min price')
        self.min_label.grid(row=0, column=1, padx=20, pady=2)
        self.target_label = ctk.CTkLabel(self.items_frame, width=60, text='Target price')
        self.target_label.grid(row=0, column=2, padx=20, pady=2)

        self.start_loop_button = ctk.CTkButton(self, command=self.start_loop_thread, text='Start updating prices')
        self.start_loop_button.grid(row=1, column=1, padx=20, pady=20)

        self.stop_loop_button = ctk.CTkButton(self, command=self.stop_loop_thread, text='Stop', state='disabled')
        self.stop_loop_button.grid(row=1, column=0, padx=20, pady=20)

        self.item_widgets = []

        self.refresh_list_button = ctk.CTkButton(self, command=self.refresh_item_list, text='Refresh items')
        self.refresh_list_button.grid(row=1, column=2, padx=20, pady=20)

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

    def refresh_item_list(self):
        for label, min_entry, target_entry in self.item_widgets:
            label.grid_forget()
            min_entry.grid_forget()
            target_entry.grid_forget()

        if not self.bot.items:
            label = ctk.CTkLabel(self.items_frame, text='There is no your items for sale right now')
            label.grid(padx=20, pady=20)
            self.item_widgets.append((label, label, label))
            return

        for idx, item in enumerate(self.bot.items, 1):
            item_info_text = repr(item)[11:-1]  # Limit title size
            label = ctk.CTkLabel(self.items_frame, text=item_info_text)
            label.grid(row=idx, column=0, padx=20, pady=2)
            min_price_entry = ctk.CTkEntry(self.items_frame, width=60, placeholder_text='min')
            min_price_entry.grid(row=idx, column=1, padx=20, pady=2)
            target_price_entry = ctk.CTkEntry(self.items_frame, width=60, placeholder_text='target')
            target_price_entry.grid(row=idx, column=2, padx=20, pady=2)
            self.item_widgets.append((label, min_price_entry, target_price_entry))


def main():
    app = MarketCSGOBotApp()
    app.mainloop()


if __name__ == "__main__":
    main()
