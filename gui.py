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
        self.geometry(f'{900}x{600}')
        self.protocol('WM_DELETE_WINDOW', self.on_closing)  # call on_closing() when app gets closed

        self.items_frame = ctk.CTkFrame(self, width=900, height=530, corner_radius=0)
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

        self.refresh_list_button = ctk.CTkButton(self, command=self.refresh_item_list, text='Save and refresh items')
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

    def save_input_prices(self):
        if self.bot.items and self.item_widgets:
            for idx, item in enumerate(self.bot.items):
                entry_min_text = self.item_widgets[idx][1].get().strip()
                if entry_min_text.isdigit():
                    item.user_min_price = int(float(entry_min_text))
                entry_target_text = self.item_widgets[idx][2].get().strip()
                if entry_target_text.isdigit():
                    item.user_target_price = int(float(entry_target_text))

    def refresh_item_list(self):
        self.save_input_prices()

        for label, min_entry, target_entry in self.item_widgets:
            label.grid_forget()
            min_entry.grid_forget()
            target_entry.grid_forget()
        self.item_widgets.clear()

        if not self.bot.items:
            return

        for idx, item in enumerate(self.bot.items, 1):
            item_info_text = repr(item)[11:-1]  # Limit title size
            label = ctk.CTkLabel(self.items_frame, text=item_info_text)
            label.grid(row=idx, column=0, padx=20, pady=2)

            min_price_entry = ctk.CTkEntry(self.items_frame, width=60)
            min_price_entry.insert(0, str(item.user_min_price))
            min_price_entry.grid(row=idx, column=1, padx=20, pady=2)

            target_price_entry = ctk.CTkEntry(self.items_frame, width=60)
            target_price_entry.insert(0, str(item.user_target_price))
            target_price_entry.grid(row=idx, column=2, padx=20, pady=2)

            self.item_widgets.append((label, min_price_entry, target_price_entry))

    # Wait before current iteration completes, then destroy
    def on_closing(self, event=0):
        self.stop_event.set()
        self.finish_event.wait()
        self.destroy()


def main():
    app = MarketCSGOBotApp()
    app.mainloop()


if __name__ == "__main__":
    main()
