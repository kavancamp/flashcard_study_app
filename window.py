from pathlib import Path
import tkinter as tk
from tkinter import Tk, Canvas, Entry, Button, PhotoImage, ttk, messagebox, Label, Toplevel
import random
from database import init_db, add_new_stack, add_new_card, get_stacks, get_cards, delete_set, update_card, delete_card

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / "assets/images"

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)
    
class FlashcardApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("420x538")
        self.root.configure(bg="white")
        self.root.title("Flashcard App")
        self.root.resizable(False, False)
        self.custom_font = "Bell Gothic Std Black"
                
        self.active_tab_index = None
        self.tab_buttons = []
        self.tab_images = []

        self.stack_name = tk.StringVar()
        self.word = tk.StringVar()
        self.definition = tk.StringVar()

        init_db()
        
        self.current_cards = []
        self.card_index = 0
        
        # persistent header above the notebook
        self.header_canvas = tk.Canvas(
            self.root,
            bg = "#FFFFFF",
            height = 100,
            width = 419,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )
        self.header_canvas.pack(side="top", fill="x")
        self.header_canvas.create_rectangle(0.0, 7, 419.0, 538.0, fill="#FFFFFF", outline="")
        
        self.header_image = PhotoImage(file=relative_to_assets("header_images/header_image.png"))
        tk.Label(self.header_canvas, image=self.header_image, bg="white").pack(padx=0, pady=0)

        #Load images for each tab
        self.tabs = [
            {
                "base": PhotoImage(file=relative_to_assets("header_images/new_set.png")),
                "hover": PhotoImage(file=relative_to_assets("header_images/new_set_hover.png")),
                "command": self.load_create_set

            },
            {
                "base": PhotoImage(file=relative_to_assets("header_images/my_sets.png")),
                "hover": PhotoImage(file=relative_to_assets("header_images/my_sets_hover.png")),
                "command": self.load_my_sets
            },
            {
                "base": PhotoImage(file=relative_to_assets("header_images/practice.png")),
                "hover": PhotoImage(file=relative_to_assets("header_images/practice_hover.png")),
                "command": self.load_practice
            }
        ]

        # Create header tab bar
        self.tab_bar = tk.Frame(self.root, bg="white")
        self.tab_bar.pack(pady=10)

        for index, tab in enumerate(self.tabs):
            btn = tk.Label(self.tab_bar, image=tab["base"], bg="white", cursor="hand2")
            btn.grid(row=0, column=index, padx=10)
            btn.bind("<Enter>", lambda e, i=index: self.on_hover(i))
            btn.bind("<Leave>", lambda e, i=index: self.on_leave(i))
            btn.bind("<Button-1>", lambda e, i=index: self.select_tab(i))
            self.tab_buttons.append(btn)
            
        # Create content area
        self.content_frame = tk.Frame(self.root, bg="white")
        self.content_frame.pack(fill="both", expand=True)
        
        # Select first tab by default
        self.select_tab(0)
        
        self.root.mainloop()
        
    def on_hover(self, index):
        if index != self.active_tab_index:
            self.tab_buttons[index].configure(image=self.tabs[index]["hover"])

    def on_leave(self, index):
        if index != self.active_tab_index:
            self.tab_buttons[index].configure(image=self.tabs[index]["base"])

    def select_tab(self, index):
        # Reset previous active
        if self.active_tab_index is not None:
            self.tab_buttons[self.active_tab_index].configure(image=self.tabs[self.active_tab_index]["base"])

        # Set new active
        self.active_tab_index = index
        self.tab_buttons[index].configure(image=self.tabs[index]["hover"])

        # Clear and load new content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        self.tabs[index]["command"]()
        
    def fade_text(self, text, steps=10, delay=30):
        def fade(step):
            # Calculate a grayscale value (from white to black)
            gray_value = int(255 * (step / steps))
            hex_color = f"#{gray_value:02x}{gray_value:02x}{gray_value:02x}"
            # Update the fill color for the canvas text item
            self.canvas.itemconfig(self.word_label, fill=hex_color)
            if step < steps:
                self.root.after(delay, fade, step + 1)
            else:
                # Once faded out, change the text and fade in
                self.canvas.itemconfig(self.word_label, text=text)
                self.fade_in(steps=steps, delay=delay)
        fade(0)

    def fade_in(self, steps=10, delay=30):
        def appear(step):
            gray_value = int(255 * (1 - step / steps))
            hex_color = f"#{gray_value:02x}{gray_value:02x}{gray_value:02x}"
            self.canvas.itemconfig(self.word_label, fill=hex_color)
            if step < steps:
                self.root.after(delay, appear, step + 1)
            else:
                self.canvas.itemconfig(self.word_label, fill="#000000")
        appear(0)
        
    def clear_flashcard_display(self):
        if hasattr(self, 'canvas') and self.canvas.winfo_exists():
            self.canvas.itemconfig(self.word_label, text="")
            
    def clear_content_frame(self):
        if hasattr(self, 'canvas') and self.canvas.winfo_exists():
            self.canvas.destroy()
                # Destroy any previous practice-specific widgets
        if hasattr(self, 'practice_widgets'):
            for widget in self.practice_widgets:
                if widget.winfo_exists():
                    widget.destroy()
            self.practice_widgets.clear()
        else:
            self.practice_widgets = [] 
            
    def fill_combobox(self):
        sets = get_stacks()
        if hasattr(self, 'sets_combobox') and self.sets_combobox.winfo_exists():
            self.sets_combobox['values'] = tuple(sets.keys())
            self.sets_combobox.set('')  # Clear current selection
                    
    # ---------------------------- Frames -----------------------------------------------
        
    def load_create_set(self):   
        self.clear_content_frame()    
        # title images
        self.word_image = PhotoImage(file=relative_to_assets("new_set_images/word_image.png"))
        tk.Label(self.content_frame, image=self.word_image, bg="white",).place(x=100, y=0)
        
        self.def_image = PhotoImage(file=relative_to_assets("new_set_images/def_image.png"))
        tk.Label(self.content_frame, image=self.def_image, text="Definition:", bg="white").place(x=100, y=80)
        
        self.set_name_image = PhotoImage(file=relative_to_assets("new_set_images/set_name_image.png"))
        tk.Label(self.content_frame, image=self.set_name_image, text="Stack Name:", bg="white").place(x=100, y=160)
        
         # Input fields
        self.entry_1 = Entry(self.content_frame, textvariable=self.word, bd=0, bg="#F1F5FF", fg="#000716", highlightthickness=0)
        self.entry_1.place(x=65, y=55, width=280, height=34)

        self.entry_2 = Entry(self.content_frame, textvariable=self.definition, bd=0, bg="#F1F5FF", fg="#000716", highlightthickness=0)
        self.entry_2.place(x=65, y=140, width=280, height=34)

        self.entry_3 = Entry(self.content_frame, textvariable=self.stack_name, bd=0, bg="#F1F5FF", fg="#000716", highlightthickness=0)
        self.entry_3.place(x=65, y=220, width=280, height=34)
        
        #Save word
        self.button_image_save_word = PhotoImage(file=relative_to_assets("new_set_images/save_word.png"))
        self.button_hover_save_word = PhotoImage(file=relative_to_assets("new_set_images/save_word_hover.png"))

        save_word_button = Button(
            self.content_frame,
            image=self.button_image_save_word,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.save_word(),
            relief="flat"
        )
        save_word_button.place(x=50, y=270, width=151, height=69)
        save_word_button.bind("<Enter>", lambda e: save_word_button.config(image=self.button_hover_save_word))
        save_word_button.bind("<Leave>", lambda e: save_word_button.config(image=self.button_image_save_word)) 
        
        # Save set button
        self.button_image_save_set = PhotoImage(file=relative_to_assets("new_set_images/save_set.png"))
        self.button_hover_save_set = PhotoImage(file=relative_to_assets("new_set_images/save_set_hover.png"))

        save_set_button = Button(
            self.content_frame,
            image=self.button_image_save_set,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.save_set(),
            relief="flat"
        )
        save_set_button.place(x=200, y=270, width=151, height=69)
        save_set_button.bind("<Enter>", lambda e: save_set_button.config(image=self.button_hover_save_set))
        save_set_button.bind("<Leave>", lambda e: save_set_button.config(image=self.button_image_save_set)) 
       
    def load_my_sets(self):
        self.clear_content_frame() #clear previous data    
        tk.Label(self.content_frame, text="" ).pack()
        # Combobox  for selecting card sets
        self.sets_combobox = ttk.Combobox(self.content_frame, state='readonly', width=30)
        self.sets_combobox.pack(padx=5, pady=20)
        self.fill_combobox()
        
        load_btn = tk.Button(self.content_frame, text="Edit Set", command=self.handle_edit_set)
        load_btn.pack(pady=10)
        load_btn.config(bg='#8DD0A0')
        
        self.button_image_select = PhotoImage(file=relative_to_assets("my_set_images/select.png"))
        self.button_hover_select = PhotoImage(file=relative_to_assets("my_set_images/select_hover.png"))
        select_button = Button(
            self.content_frame,
            image=self.button_image_select,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.select_set(),
            relief="flat"
        )
        select_button.place(x=50.0, y=200.0, width=151.0, height=69.0)
        select_button.bind("<Enter>", lambda e: select_button.config(image=self.button_hover_select))
        select_button.bind("<Leave>", lambda e: select_button.config(image=self.button_image_select))
        
        self.button_image_delete = PhotoImage(file=relative_to_assets("my_set_images/delete.png"))
        self.button_hover_delete = PhotoImage(file=relative_to_assets("my_set_images/delete_hover.png"))  
        delete_button = Button(
            self.content_frame,
            image=self.button_image_delete,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.delete_selected_set(),
            relief="flat"
        )
        delete_button.place(x=210, y=200.0, width=151.0, height=69.0)
        delete_button.bind('<Enter>', lambda e: delete_button.config(image=self.button_hover_delete))
        delete_button.bind('<Leave>', lambda e: delete_button.config(image=self.button_image_delete))
        
    def load_practice(self, show_first_card=False):
        self.clear_content_frame() #clear previous data
        # Initialize variables for tracking card index and current cards
        self.card_index = 0
        self.current_tabs = []

        # # Label to display the word on flashcards
        self.canvas = tk.Canvas(self.content_frame, width=400, height=300, bd=0, highlightthickness=0, bg="white")
        self.canvas.place(x=20,y=0)

        self.card_img = PhotoImage(file=relative_to_assets("practice_images/card_background.png"))
        self.canvas.create_image(0, 0, image=self.card_img, anchor="nw")
        self.practice_widgets.append(self.canvas)
        
        self.word_label = self.canvas.create_text(180, 125, text="", width=280, font=(self.custom_font, 24), fill="black")
        
        # Button to flip the flashcard 
        self.button_image_flip = PhotoImage(file=relative_to_assets("practice_images/flip.png"))
        self.button_hover_flip = PhotoImage(file=relative_to_assets("practice_images/flip_hover.png"))
        flip_button = Button(
            image=self.button_image_flip,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.flip_card(),
            relief="flat"
        )
        flip_button.place(
            x=56.0,
            y=410.0,
            width=137.0,
            height=55.0
        )
        flip_button.bind('<Enter>', lambda e: flip_button.config(image=self.button_hover_flip))
        flip_button.bind('<Leave>', lambda e: flip_button.config(image=self.button_image_flip))
        self.practice_widgets.append(flip_button)
        
        self.button_image_next = PhotoImage(file=relative_to_assets("practice_images/next.png"))
        self.button_hover_next = PhotoImage(file=relative_to_assets("practice_images/next_hover.png"))
        
        next_button = Button(
            image=self.button_image_next,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.next_card(),
            relief="flat"
        )       
        next_button.place(
            x=230.0, y=410.0, width=137.0, height=55.0
        )
        next_button.bind('<Enter>', lambda e: next_button.config(image=self.button_hover_next))
        next_button.bind('<Leave>', lambda e: next_button.config(image=self.button_image_next))
        self.practice_widgets.append(next_button)
        
        self.button_image_back = PhotoImage(file=relative_to_assets("practice_images/back.png"))
        self.button_hover_back = PhotoImage(file=relative_to_assets("practice_images/back_hover.png"))

        back_button = Button(
            image=self.button_image_back,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.prev_card(),
            relief="flat"
        )
        back_button.place(
            x=135.0, y=470.0, width=147.0, height=61.0
        )
        back_button.bind('<Enter>', lambda e: back_button.config(image=self.button_hover_back))
        back_button.bind('<Leave>', lambda e: back_button.config(image=self.button_image_back))
        self.practice_widgets.append(back_button)

        if show_first_card:
            self.show_card()
            
    def handle_edit_set(self):
        selected_stack = self.sets_combobox.get().strip()
        stacks = get_stacks()

        if not selected_stack:
            messagebox.showwarning("Warning", "Please select a set.")
            return

        if selected_stack not in stacks:
            messagebox.showwarning("Warning", "Selected set not found.")
            return

        stack_id = stacks[selected_stack]
        self.stack_id = stack_id 
        cards = get_cards(stack_id)

        if not cards:
            messagebox.showinfo("Info", f"The set '{selected_stack}' has no cards.")
            return

        # If it has cards, show the list
        self.render_card_list(cards)   
        
    def save_word(self):
        stack_name = self.stack_name.get().strip()
        word = self.word.get().strip()
        definition = self.definition.get().strip()

        sets = get_stacks()

        if not stack_name:
            messagebox.showwarning("Warning", "Please enter a set name.")
            return

        if not word or not definition:
            if stack_name in sets:
                messagebox.showwarning("Warning", "Please enter both a word and a definition.")
            else:
                messagebox.showwarning("Warning", "Please enter a word, definition, and set name.")
            return
            # Check for duplicate word

        # If all inputs are valid, proceed to save
        if stack_name not in sets:
            stack_id = add_new_stack(stack_name)
        else:
            stack_id = sets[stack_name]
        # duplicate?
        existing_cards = get_cards(stack_id)
        if any(w.lower() == word.lower() for _, w, _ in existing_cards):
            result = messagebox.askyesno("Duplicate Word", f"The word '{word}' already exists in '{stack_name}'. Add anyway?")
            if not result:
                return  # Don't add the card if user says No
        add_new_card(stack_id, word, definition)

        # Clear fields
        self.word.set('')
        self.definition.set('')
        self.fill_combobox()   
    # def save_word(self):
    #     stack_name = self.stack_name.get().strip()
    #     word = self.word.get().strip()
    #     definition = self.definition.get().strip()

    #     if stack_name and word and definition:
    #         if stack_name not in get_stacks():
    #             stack_id = add_new_stack(stack_name)
    #         else:
    #             stack_id = get_stacks()[stack_name]

    #         add_new_card(stack_id, word, definition)

    #         self.word.set('')
    #         self.definition.set('')

    #         self.fill_combobox() 
    #     else:
    #         messagebox.showwarning("Warning", "Please enter a word, definition and set name.")
    def save_set(self):
        stack_name = self.stack_name.get().strip()
        word = self.word.get().strip()
        definition = self.definition.get().strip()

        sets = get_stacks()

        if not stack_name:
            messagebox.showwarning("Warning", "Please enter a set name.")
            return

        if stack_name in sets:
            if not word or not definition:
                messagebox.showwarning("Warning", "This set already exists. Please enter a word and definition to add a card.")
                return
        else:
            # Create new set
            stack_id = add_new_stack(stack_name)
            self.fill_combobox()
            self.stack_name.set('')
        # Add card if word and definition are present
        if word and definition:
            stack_id = sets.get(stack_name, add_new_stack(stack_name))
            add_new_card(stack_id, word, definition)
            self.word.set('')
            self.definition.set('')
            self.fill_combobox()
            self.entry_1.delete(0, tk.END)
            self.entry_2.delete(0, tk.END)
            self.entry_3.delete(0, tk.END)
        else:
            messagebox.showinfo("Info", "Set saved without cards.")                  
    # def save_set(self):
    #     stack_name = self.stack_name.get().strip()
    #     if stack_name:
    #         if stack_name not in get_stacks():
    #             stack_id = add_new_stack(stack_name)
    #             self.fill_combobox()
    #             self.stack_name.set('')
    #             self.word.set('')
    #             self.definition.set('')
    #             print(f"Saved word: {self.word.get()} with definition: {self.definition.get()} to set: {stack_name}")
    #     else:
    #         messagebox.showwarning("Warning", "Please enter a set name.")
                
    def delete_selected_set(self):
        stack_name = self.sets_combobox.get()
        if stack_name:
            result = messagebox.askyesno(
                'Confirmation', f'Delete "{stack_name}" set?')
            if result == tk.YES:
                stack_id = get_stacks()[stack_name]
                delete_set(stack_id)  
                self.clear_flashcard_display() 
                self.fill_combobox() # GUI update
        else:
            messagebox.showwarning("Warning", "Please select a set.")
                           
    def select_set(self):
        stack_name = self.sets_combobox.get().strip()
        if stack_name:
            stack_id = get_stacks()[stack_name]
            cards = get_cards(stack_id)

            if cards:
                self.tabs[2]["command"] = lambda: self.load_practice(show_first_card=True)
                random.shuffle(cards)
                self.current_cards = cards
                self.card_index = 0
                self.select_tab(2)
                self.show_card()
                self.display_cards(cards)
            else:
                messagebox.showinfo("Info", "This set has no cards.")
        else:
            messagebox.showwarning("Warning", "Please select a set.")
  
    def display_cards(self, cards):
        self. card_index = 0
        self.current_cards = cards
        # Clear the display
        if not cards:
            self.clear_flashcard_display()
        else:
            self.show_card()
        
        self.show_card()
    
    # Function to display the current flashcards word
    def show_card(self):
        if self.current_cards:
            if 0 <= self.card_index < len(self.current_cards):
                _, word, _ = self.current_cards[self.card_index]
                self.canvas.itemconfig(self.word_label, text=word)
                #self.word_label.config(text=word)
                self.card_flipped = False # Track if card is flipped
            else:
                self.clear_flashcard_display()

    # flip the current card and display its definition
    def flip_card(self):
        if self.current_cards:
            _, word, definition = self.current_cards[self.card_index] 
            next_text = definition if not getattr(self, "card_flipped", False) else word
            self.card_flipped = not getattr(self, "card_flipped", False)
            self.fade_text(next_text)
                  
    # Function to move to the next card
    def next_card(self):
        if self.current_cards:
            self.card_index = min(self.card_index + 1, len(self.current_cards) - 1)
            self.show_card()
        else:
            messagebox.showinfo("Info", "This set has no more cards.")

    # Function to move to the previous card
    def prev_card(self):
        if self.current_cards:
            self.card_index = max(self.card_index - 1, 0)
            self.show_card()
        else:
            messagebox.showinfo("Info", "This is the first card.") 
        
    def display_selected_set_cards(self):
        selected_stack = self.sets_combobox.get()
        stacks = get_stacks()

        if selected_stack in stacks:
            stack_id = stacks[selected_stack]
            self.stack_id = stack_id
            cards = get_cards(stack_id)
            self.render_card_list(self.content_frame, cards)
        else:
            messagebox.showinfo("Info", "Please select a valid set.")
             
    def render_card_list(self, cards):
        self.cards = cards  # Save current cards list for use in popups

        list_popup = tk.Toplevel(self.root)
        list_popup.title("Card List")
        list_popup.geometry("200x455")
        list_popup.configure(bg="white")
        list_popup.resizable(False, False)   

        # Frame with canvas and scrollbar inside popup
        scroll_frame = tk.Frame(list_popup, bg="white")
        scroll_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(scroll_frame, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Load pencil icon
        self.pencil_icon = PhotoImage(file=relative_to_assets("my_set_images/pencil.png")).subsample(12, 12)

        # Add cards
        for card_id, word, definition in cards:
            card_frame = tk.Frame(scrollable_frame, bg="white", bd=1, relief="solid", padx=5, pady=5)
            card_frame.pack(fill="x", padx=10, pady=5)

            tk.Label(card_frame, text=f"Word: {word}", bg="white").pack(anchor="w")
            tk.Label(card_frame, text=f"Definition: {definition}", bg="white", wraplength=180, justify="left").pack(anchor="w")

            btn_frame = tk.Frame(card_frame, bg="white")
            btn_frame.pack(anchor="e", pady=(5, 0))

            edit_btn = tk.Button(
                btn_frame,
                image=self.pencil_icon,
                bg="white",
                borderwidth=0,
                command=lambda c_id=card_id, w=word, d=definition: self.edit_card_popup(c_id, w, d, list_popup)
            )
            edit_btn.image = self.pencil_icon  # Prevent garbage collection
            edit_btn.pack(side="left", padx=(0, 10))
            edit_btn.config(bg='#8DD0A0')

            delete_btn = tk.Button(
                btn_frame,
                bg="white",
                text="Delete",
                command=lambda c_id=card_id, popup=list_popup: self.delete_card_and_refresh(c_id, popup)
            )
            delete_btn.pack(side="left")
            delete_btn.config(bg='#8DD0A0')

        # Add close button at the bottom of popup
        close_btn = tk.Button(
            list_popup,
            text="Close",
            bg="white",
            command=list_popup.destroy
        )
        close_btn.pack(pady=10)
        close_btn.config(bg='#8DD0A0')

        
    def edit_card_popup(self, card_id, current_word, current_definition, parent_popup=None):
        if parent_popup:
            parent_popup.destroy()
            popup = tk.Toplevel(self.root)
            popup.title("Edit Card")
            popup.geometry("300x250")
            popup.configure(bg="white")
            popup.resizable(False, False)

            tk.Label(popup, text="Word:", bg="white").pack(pady=(10, 0))
            word_entry = tk.Entry(popup, width=30)
            word_entry.insert(0, current_word)
            word_entry.pack(pady=(0, 10))

            tk.Label(popup, text="Definition:", bg="white").pack()
            def_entry = tk.Entry(popup, width=30)
            def_entry.insert(0, current_definition)
            def_entry.pack(pady=(0, 10))

        def save_changes():
            new_word = word_entry.get().strip()
            new_def = def_entry.get().strip()
            if new_word and new_def:
                update_card(card_id, new_word, new_def)
                messagebox.showinfo("Success", "Card updated successfully!")
                popup.destroy()
                if hasattr(self, 'stack_id'):
                    updated_cards = get_cards(self.stack_id)
                    self.render_card_list(updated_cards)
        save_btn = tk.Button(popup, text="Save", command=save_changes)
        save_btn.pack(pady=(10, 0))
        save_btn.config(bg='#8DD0A0')

    def delete_card_and_refresh(self, card_id, popup=None):
        if messagebox.askyesno("Delete Card", "Are you sure you want to delete this card?"):
            delete_card(card_id)
            if hasattr(self, 'stack_id'):
                updated_cards = get_cards(self.stack_id)
                if popup:
                    popup.destroy()  # Close old popup
                self.render_card_list(updated_cards)

