import customtkinter as ctk
from bot import MarketBot, price_update_loop
from threading import Thread, Event, Lock
from prettytable import PrettyTable
import time


class MarketCSGOBotApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('MarketCSGO Bot')
        self.geometry(f'{910}x{380}')
        self.protocol('WM_DELETE_WINDOW', self.on_closing)  # call on_closing() when app gets closed

        self.items_textbox = ctk.CTkTextbox(self, width=700, height=300, font=('Consolas', 12), undo=False)
        self.items_textbox.grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 0))

        # ----- Control frame -----
        self.control_frame = ctk.CTkFrame(self, width=180, height=300)
        self.control_frame.grid(row=0, column=3, padx=0, pady=(10, 0))
        self.control_frame.grid_propagate(0)

        self.bot = MarketBot()  # initialize bot for items menu

        self.item_menu = ctk.CTkOptionMenu(self.control_frame, width=160,
                                           values=self.bot.items, command=self.item_menu_callback)
        self.item_menu.grid(row=0, column=0, padx=10, pady=(10, 0))
        self.item_menu.set('Select item by id')

        self.min_label = ctk.CTkLabel(self.control_frame, text='Min price (1USD = 1000):')
        self.min_label.grid(row=1, column=0, padx=10, pady=(10, 0), sticky='w')

        self.min_price_entry = ctk.CTkEntry(self.control_frame, width=160, placeholder_text='min')
        self.min_price_entry.grid(row=2, column=0, padx=10, pady=0)

        self.target_label = ctk.CTkLabel(self.control_frame, text='Target price (1USD = 1000):')
        self.target_label.grid(row=3, column=0, padx=10, pady=(10, 0), sticky='w')

        self.target_price_entry = ctk.CTkEntry(self.control_frame, width=160, placeholder_text='target')
        self.target_price_entry.grid(row=4, column=0, padx=10, pady=0)

        self.save_user_prices_button = ctk.CTkButton(self.control_frame, text='Save and refresh list', width=160,
                                                     command=self.save_input_prices)
        self.save_user_prices_button.grid(row=5, column=0, padx=10, pady=(10, 10), sticky='ns')
        # -------------------------

        # ----- Updater frame -----
        self.updater_frame = ctk.CTkFrame(self, width=700, height=50)
        self.updater_frame.grid(row=1, column=0, columnspan=3, padx=0, pady=(10, 10))
        self.updater_frame.grid_propagate(0)

        self.stop_loop_button = ctk.CTkButton(self.updater_frame, command=self.stop_loop_thread, text='Stop',
                                              state='disabled')
        self.stop_loop_button.grid(row=0, column=0, padx=(10, 0), pady=10)

        self.start_loop_button = ctk.CTkButton(self.updater_frame, command=self.start_loop_thread,
                                               text='Start updating prices')
        self.start_loop_button.grid(row=0, column=1, padx=20, pady=10)

        self.loop_progressbar = ctk.CTkProgressBar(self.updater_frame, width=200, height=10, mode='indeterminate')
        self.loop_progressbar.grid(row=0, column=2, padx=0, pady=0)

        self.update_menu_and_list_button = ctk.CTkButton(self.updater_frame, command=self.update_item_menu_and_list,
                                                         text='Refresh list')
        self.update_menu_and_list_button.grid(row=0, column=3, padx=20, pady=10)
        # --------------------------

        self.appearance_mode_switch_var = ctk.StringVar(value=self._get_appearance_mode())
        self.appearance_mode_switch = ctk.CTkSwitch(
            self, onvalue='dark', offvalue='light', command=self.change_appearance_mode_event,
            variable=self.appearance_mode_switch_var, text='Dark Mode'
        )
        self.appearance_mode_switch.grid(row=1, column=3, padx=20, pady=(0, 0))

        self.stop_event = Event()
        self.finish_event = Event()
        self.stopping_thread = None

        self.bot.initialize_db()
        self.finish_event.set()  # On app start update loop inactive, so finish is possible

    def start_loop_thread(self):
        self.start_loop_button.configure(state='disabled')
        self.stop_loop_button.configure(state='normal')
        self.loop_progressbar.start()

        self.finish_event.clear()

        worker_thread = Thread(
            target=price_update_loop, args=(self.bot, self.stop_event, self.finish_event))
        worker_thread.start()

    def stop_update_loop_and_toggle_buttons(self):
        self.stop_event.set()
        self.stop_loop_button.configure(state='disabled')
        self.update()
        self.finish_event.wait()
        self.start_loop_button.configure(state='normal')
        self.loop_progressbar.stop()
        print('stopping thread finished')

    def stop_loop_thread(self):
        self.stopping_thread = Thread(target=self.stop_update_loop_and_toggle_buttons)
        self.stopping_thread.start()

    def update_item_menu_and_list(self):
        self.refresh_item_list()
        self.refresh_item_menu()

    # Wait until current iteration is completed, then destroy all widgets
    def on_closing(self):
        if self.stopping_thread is None or not self.stopping_thread.is_alive():
            self.stop_event.set()
            self.finish_event.wait()
            self.destroy()
        else:
            # If stopper thread is currently working then wait for it to finish
            while self.stopping_thread.is_alive():
                self.update_idletasks()
                self.update()
                time.sleep(0.04)
            self.destroy()

    def save_input_prices(self):
        if not self.bot.items:
            return

        select_text = self.item_menu.get()
        if select_text == 'Select item by id':
            return

        selected_item_id = select_text.split(':')[1]
        for item in self.bot.items:
            if item.item_id == selected_item_id:
                entry_min_text = self.min_price_entry.get().strip()
                if entry_min_text.isdigit():
                    item.user_min_price = int(float(entry_min_text))

                entry_target_text = self.target_price_entry.get().strip()
                if entry_target_text.isdigit():
                    item.user_target_price = int(float(entry_target_text))

                # Save new user prices
                self.bot.save_item_user_prices_to_db(
                    item.item_id, item.user_min_price, item.user_target_price
                )
                break

        self.refresh_item_list()

    def refresh_item_list(self):
        if not self.bot.items:
            self.items_textbox.delete('0.0', ctk.END)
            self.items_textbox.insert('0.0', 'Items list empty or no internet connection \n'
                                             'Start updating prices to get items list if available')
            return

        item_table = [['#', 'item_id', 'item title', 'current p.', 'pos', 'minimum', 'target']]
        for idx, item in enumerate(self.bot.items, 1):
            title = str(item.market_hash_name[:32]).replace('★', '*') + ' '
            position = f'n/l' if item.position == 0 else item.position
            item_table.append([
                idx, item.item_id, title, f'{item.price/1000:.3f} {item.currency}',
                position, item.user_min_price, item.user_target_price
            ])
        pretty_table = PrettyTable(item_table[0])
        pretty_table.add_rows(item_table[1:])

        self.items_textbox.delete('0.0', ctk.END)
        self.items_textbox.insert('0.0', pretty_table.get_string())

    def refresh_item_menu(self):
        choices = (f'#{idx} id:{item.item_id}' for idx, item in enumerate(self.bot.items, 1))
        self.item_menu.configure(values=tuple(choices))

    def item_menu_callback(self, choice):
        selected_item_id = choice.split(':')[1]
        for item in self.bot.items:
            if item.item_id == selected_item_id:
                self.min_price_entry.delete(0, ctk.END)
                self.target_price_entry.delete(0, ctk.END)
                self.min_price_entry.insert(0, item.user_min_price)
                self.target_price_entry.insert(0, item.user_target_price)

    def change_appearance_mode_event(self):
        ctk.set_appearance_mode(self.appearance_mode_switch_var.get())


def main():
    app = MarketCSGOBotApp()
    app.mainloop()


if __name__ == "__main__":
    main()
