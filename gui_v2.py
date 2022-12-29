import customtkinter as ctk
from bot import MarketBot, price_update_loop
from threading import Thread, Event


class MarketCSGOBotApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.bot = MarketBot()
        self.stop_event = Event()
        self.finish_event = Event()
        self.finish_event.set()  # On app start update loop inactive, so finish is possible

        self.title('MarketCSGO Bot')
        self.geometry(f'{900}x{390}')
        self.protocol('WM_DELETE_WINDOW', self.on_closing)  # call on_closing() when app gets closed

        self.items_textbox = ctk.CTkTextbox(self, width=600, height=300)
        self.items_textbox.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 0))

        # ----- Control frame -----
        self.control_frame = ctk.CTkFrame(self, width=220, height=300)
        self.control_frame.grid(row=0, column=3, padx=0, pady=(20, 0))
        self.control_frame.grid_propagate(0)

        self.item_menu = ctk.CTkOptionMenu(self.control_frame, width=180,
                                           values=self.bot.items, command=self.item_menu_callback)
        self.item_menu.grid(row=0, column=0, padx=20, pady=(20, 0))
        self.item_menu.set('Select item by id')

        self.min_label = ctk.CTkLabel(self.control_frame, text='Minimum price (1USD = 1000):')
        self.min_label.grid(row=1, column=0, padx=20, pady=(10, 0), sticky='w')

        self.min_price_entry = ctk.CTkEntry(self.control_frame, width=180, placeholder_text='min')
        self.min_price_entry.grid(row=2, column=0, padx=20, pady=0)

        self.target_label = ctk.CTkLabel(self.control_frame, text='Target price (1USD = 1000):')
        self.target_label.grid(row=3, column=0, padx=20, pady=(10, 0), sticky='w')

        self.target_price_entry = ctk.CTkEntry(self.control_frame, width=180, placeholder_text='target')
        self.target_price_entry.grid(row=4, column=0, padx=20, pady=0)

        self.save_user_prices_button = ctk.CTkButton(self.control_frame, text='Save and refresh list', width=180,
                                                     command=self.save_input_prices)
        self.save_user_prices_button.grid(row=5, column=0, padx=20, pady=20, sticky='ns')
        # -------------------------

        self.start_loop_button = ctk.CTkButton(self, command=self.start_loop_thread, text='Start updating prices')
        self.start_loop_button.grid(row=1, column=1, padx=20, pady=20)

        self.stop_loop_button = ctk.CTkButton(self, command=self.stop_loop_thread, text='Stop', state='disabled')
        self.stop_loop_button.grid(row=1, column=0, padx=20, pady=20)

        self.loop_progressbar = ctk.CTkProgressBar(self, width=200, mode='indeterminate')
        self.loop_progressbar.grid(row=1, column=3, padx=0, pady=0)

        self.refresh_list_button = ctk.CTkButton(self, command=self.refresh_item_list, text='Refresh list')
        self.refresh_list_button.grid(row=1, column=2, padx=20, pady=20)

    def start_loop_thread(self):
        self.start_loop_button.configure(state='disabled')
        self.stop_loop_button.configure(state='normal')

        worker_thread = Thread(target=price_update_loop, args=(self.bot, self.stop_event, self.finish_event))
        worker_thread.start()

        self.loop_progressbar.start()

    def stop_loop_thread(self):
        self.stop_event.set()
        self.stop_loop_button.configure(state='disabled')

        def toggle_buttons_on_finish():
            self.finish_event.wait()
            self.start_loop_button.configure(state='normal')
            self.loop_progressbar.stop()

        toggling_thread = Thread(target=toggle_buttons_on_finish)
        toggling_thread.start()

    def save_input_prices(self):
        if self.bot.items:
            select_text = self.item_menu.get()
            if select_text == 'Select item by id':
                return

            selected_item_id = select_text.split(':')[1]
            print(selected_item_id)
            for item in self.bot.items:
                if item.item_id == selected_item_id:
                    entry_min_text = self.min_price_entry.get().strip()
                    if entry_min_text.isdigit():
                        item.user_min_price = int(float(entry_min_text))

                    entry_target_text = self.target_price_entry.get().strip()
                    if entry_target_text.isdigit():
                        item.user_target_price = int(float(entry_target_text))
                    break
        self.refresh_item_list()

    def update_item_menu(self):
        choices = (f'#{idx} id:{item.item_id}' for idx, item in enumerate(self.bot.items, 1))
        self.item_menu.configure(values=tuple(choices))

    def refresh_item_list(self):
        if not self.bot.items:
            return

        self.update_item_menu()

        item_list_text = ''
        for idx, item in enumerate(self.bot.items, 1):
            item_text = repr(item)[11:-1]  # Limit title size
            item_list_text += f'#{idx} ' + item_text + '\n'

        self.items_textbox.delete('0.0', ctk.END)
        self.items_textbox.insert('0.0', item_list_text)

    def item_menu_callback(self, choice):
        selected_item_id = choice.split(':')[1]
        for item in self.bot.items:
            if item.item_id == selected_item_id:
                self.min_price_entry.delete(0, ctk.END)
                self.target_price_entry.delete(0, ctk.END)
                self.min_price_entry.insert(0, item.user_min_price)
                self.target_price_entry.insert(0, item.user_target_price)

    # Wait before current iteration completes, then destroy
    def on_closing(self, event=0):
        self.stop_event.set()
        self.finish_event.wait(timeout=5)
        self.destroy()


def main():
    app = MarketCSGOBotApp()
    app.mainloop()


if __name__ == "__main__":
    main()
