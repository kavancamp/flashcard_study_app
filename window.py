from pathlib import Path
import tkinter as tk
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, ttk, messagebox, Label
import tkinter.font as Font
from ttkbootstrap import Style
import random
from database import init_db, add_new_stack, add_new_card, get_stacks, get_cards, delete_set

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
        tk.Label(self.header_canvas, image=self.header_image, bg="white",).pack(padx=0, pady=0)

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

    def load_create_set(self):        
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
            command=lambda: [print("saving word..."), self.save_word()],
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
            command=lambda: [print("saving set..."), self.save_set()],
            relief="flat"
        )
        save_set_button.place(x=200, y=270, width=151, height=69)
        save_set_button.bind("<Enter>", lambda e: save_set_button.config(image=self.button_hover_save_set))
        save_set_button.bind("<Leave>", lambda e: save_set_button.config(image=self.button_image_save_set)) 
       
    def load_my_sets(self):
        tk.Label(self.content_frame, text="My Sets", bg="light gray").pack()
        # Combobox  for selecting card sets
        self.sets_combobox = ttk.Combobox(self.content_frame, state='readonly', width=30)
        self.sets_combobox.pack(padx=5, pady=50)
        self.fill_combobox()
        
        self.button_image_select = PhotoImage(file=relative_to_assets("my_set_images/select.png"))
        self.button_hover_select = PhotoImage(file=relative_to_assets("my_set_images/select_hover.png"))
        select_button = Button(
            self.content_frame,
            image=self.button_image_select,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: [print("loading practice screen..."), self.select_set()],
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
            command=lambda: [print("Deleting set..."), self.delete_selected_set()],
            relief="flat"
        )
        delete_button.place(x=210, y=200.0, width=151.0, height=69.0)
        delete_button.bind('<Enter>', lambda e: delete_button.config(image=self.button_hover_delete))
        delete_button.bind('<Leave>', lambda e: delete_button.config(image=self.button_image_delete))
        
    def load_practice(self, show_first_card=False):
        self.card_bg = PhotoImage(file=relative_to_assets("practice_images/card_background.png"))
        card_image = tk.Label(self.content_frame, image=self.card_bg, bg="white")
        card_image.place(x = 20, y=10)
        # Initialize variables for tracking card index and current cards
        self.card_index = 0
        self.current_tabs = []

        # # Label to display the word on flashcards
        self.word_label = tk.Label(self.content_frame, text='word', bg="#F1F5FF", font=('TkDefaultFont', 24))
        self.word_label.pack(padx=5, pady=20)
        
        # # Label to display the definition on flashcards
        self.definition_label = tk.Label(self.content_frame,  text='definition', bg="#F1F5FF")
        self.definition_label.pack(padx=5, pady=30)
        tk.Label(self.content_frame, text="Practice Area", bg="#F1F5FF", font=(self.custom_font, 10)).pack()

        # Button to flip the flashcard 
        self.button_image_flip = PhotoImage(file=relative_to_assets("practice_images/flip.png"))
        self.button_hover_flip = PhotoImage(file=relative_to_assets("practice_images/flip_hover.png"))
        flip_button = Button(
            image=self.button_image_flip,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: [print("Flipping card..."), self.flip_card()],
            relief="flat"
        )
        flip_button.place(
            x=56.0,
            y=405.0,
            width=137.0,
            height=55.0
        )
        flip_button.bind('<Enter>', lambda e: flip_button.config(image=self.button_hover_flip))
        flip_button.bind('<Leave>', lambda e: flip_button.config(image=self.button_image_flip))

        self.button_image_next = PhotoImage(file=relative_to_assets("practice_images/next.png"))
        self.button_hover_next = PhotoImage(file=relative_to_assets("practice_images/next_hover.png"))
        
        next_button = Button(
            image=self.button_image_next,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: [print("Flipping card..."), self.next_card()],
            relief="flat"
        )       
        next_button.place(
            x=230.0, y=405.0, width=137.0, height=55.0
        )
        next_button.bind('<Enter>', lambda e: next_button.config(image=self.button_hover_next))
        next_button.bind('<Leave>', lambda e: next_button.config(image=self.button_image_next))

        
        self.button_image_back = PhotoImage(file=relative_to_assets("practice_images/back.png"))
        self.button_hover_back = PhotoImage(file=relative_to_assets("practice_images/back_hover.png"))

        back_button = Button(

            image=self.button_image_back,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: [print("Flipping card..."), self.prev_card],
            relief="flat"
        )
        back_button.place(
            x=140.0, y=460.0, width=147.0, height=61.0
        )
        back_button.bind('<Enter>', lambda e: back_button.config(image=self.button_hover_back))
        back_button.bind('<Leave>', lambda e: back_button.config(image=self.button_image_back))


        if show_first_card:
            self.show_card()
       
    def fill_combobox(self):
        if hasattr(self, 'sets_combobox'):
            self.sets_combobox['values'] = tuple(get_stacks().keys())   
           
    def save_word(self):
        stack_name = self.stack_name.get().strip()
        word = self.word.get().strip()
        definition = self.definition.get().strip()

        if stack_name and word and definition:
            if stack_name not in get_stacks():
                stack_id = add_new_stack(stack_name)
            else:
                stack_id = get_stacks()[stack_name]

            add_new_card(stack_id, word, definition)

            self.word.set('')
            self.definition.set('')

            self.fill_combobox() 
                       
    def save_set(self):
        stack_name = self.stack_name.get().strip()
        if stack_name:
            if stack_name not in get_stacks():
                stack_id = add_new_stack(stack_name)
                self.fill_combobox()
                self.stack_name.set('')
                print(f"Saved word: {self.word} with definition: {self.definition} to set: {self.stack_name}")
                
                self.entry_1.delete(0, tk.END)
                self.entry_2.delete(0, tk.END)
                self.entry_3.delete(0, tk.END)
                
    def delete_selected_set(self):
        stack_name = self.sets_combobox.get()
        if stack_name:
            result = messagebox.askyesno(
                'Confirmation', f'Delete "{stack_name}" set?')
            if result == tk.YES:
                stack_id = get_stacks()[stack_name]
                delete_set(stack_id)  
                self.fill_combobox()  # GUI update
                #self.clear_flashcard_display()  # GUI update       
                     
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
                print(f"{cards}")
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

    def clear_flashcard_display(self):
        if hasattr(self, 'word_label') and self.word_label.winfo_exists():
            self.word_label.config(text='')
        if hasattr(self, 'definition_label') and self.definition_label.winfo_exists():
            self.definition_label.config(text='')

    # Function to display the current flashcards word
    def show_card(self):
        if self.current_cards:
            if 0 <= self.card_index < len(self.current_cards):
                word, _ = self.current_cards[self.card_index]
                self.word_label.config(text=word)
                self.definition_label.config(text='')
            else:
                self.clear_flashcard_display()

    # flip the current card and display its definition
    def flip_card(self):
        if self.current_cards:
            _, definition = self.current_cards[self.card_index]
            self.definition_label.config(text=definition)

    # Function to move to the next card
    def next_card(self):
        if self.current_cards:
            self.card_index = min(self.card_index + 1, len(self.current_cards) - 1)
            self.show_card()

    # Function to move to the previous card
    def prev_card(self):
        if self.current_cards:
            self.card_index = max(self.card_index - 1, 0)
            self.show_card()
            