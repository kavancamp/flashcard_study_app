from pathlib import Path
import tkinter as tk
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, ttk, messagebox
from ttkbootstrap import Style

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
        
        self.active_tab_index = None
        self.tab_buttons = []
        self.tab_images = []

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
        self.header_canvas.create_rectangle(
            0.0,
            7,
            419.0,
            538.0,
            fill="#FFFFFF",
            outline="")
        self.header_image = PhotoImage(file=relative_to_assets("header_images/header_image.png"))
        button_1 = Button(
            image=self.header_image,
            borderwidth=0,
            highlightthickness=0,
            relief="flat"
        )
        button_1.place(
            x=0.0,
            y=0.0,
            width=419.0,
            height=82.0
        )
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
        tk.Label(self.content_frame, text="Create Set Screen", bg="white").pack()

    def load_my_sets(self):
        tk.Label(self.content_frame, text="My Sets Screen", bg="white").pack()

    def load_practice(self):
        tk.Label(self.content_frame, text="Practice Screen", bg="white").pack()
    