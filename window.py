from pathlib import Path
import tkinter as tk
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, ttk, messagebox
import tkinter.font as tkFont

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"/home/kvanc/boot_dev/flashcard_study_app/assets/frame1")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)
class Window:
    def __init__(self, width, height):
        self.root = Tk()
        self.root.geometry(f"{width}x{height}")
        self.root.title("Flashcards")
        self.root.configure(bg="white")
        self.root.resizable(False, False)
        
        self.canvas = Canvas(self.root, width=width, height=height, bg='white', bd=0, highlightthickness=0)
        self.canvas.place(x=0, y=0)

        self.stored_words = []  

        self.load_header()  
        self.root.mainloop()
        
    def load_header(self):    
        self.canvas.delete("all")

        self.canvas.create_rectangle(0, 7, 420, 538, fill="#FFFFFF", outline="")
        self.canvas.create_text(55, 13, anchor="nw", text="Flashcard App", fill="#8CD09F", font=("Ribeye", 24))

        self.button_image_1 = PhotoImage(file=relative_to_assets("button_1.png"))
        new_set_button = Button(
            self.root,
            image=self.button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.load_input_screen,
            relief="flat"
        )
        new_set_button.place(
            x=11.0,
            y=91.0,
            width=98,
            height=36
        )
        new_set_button.bind("<Enter>", lambda e: new_set_button.config(image=self.button_image_hover_1))
        new_set_button.bind("<Leave>", lambda e: new_set_button.config(image=self.button_image_1))

        self.button_image_2 = PhotoImage(file=relative_to_assets("button_2.png"))
        my_sets_button = Button(
            self.root,
            image=self.button_image_2,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.load_my_sets_screen,
            relief="flat"
        )
        my_sets_button.place(x=162.0, y=91.0, width=98.0, height=36.0)
        my_sets_button.bind("<Enter>", lambda e: new_set_button.config(image=self.button_image_hover_2))
        my_sets_button.bind("<Leave>", lambda e: new_set_button.config(image=self.button_image_2))
        
        self.button_image_2 = PhotoImage(file=relative_to_assets("button_2.png"))
        self.button_image_hover_2 = PhotoImage( file=relative_to_assets("button_hover_2.png"))
        
        self.button_image_3 = PhotoImage(file=relative_to_assets("button_3.png"))
        self.button_image_hover_3 = PhotoImage(file=relative_to_assets("button_hover_3.png"))

        practice_button = Button(
            self.root,
            image=self.button_image_3,
            borderwidth=0,
            highlightthickness=0,
            command=self.load_practice_screen,
            relief="flat"
        )
        practice_button.place(x=313, y=91, width=98, height=36)
        practice_button.bind("<Enter>", lambda e: practice_button.config(image=self.button_image_hover_3))
        practice_button.bind("<Leave>", lambda e: practice_button.config(image=self.button_image_3))
        
        def load_input_screen(self):
            self.canvas.delete("all")

            self.entry_1 = Entry(self.root, bd=0, bg="#F1F5FF", fg="#000716", highlightthickness=0)
            self.entry_1.place(x=50, y=200, width=300, height=34)

            button_image_save = PhotoImage(file=relative_to_assets("button_4.png"))
            button_hover_save = PhotoImage(file=relative_to_assets("button_hover_4.png"))

            save_button = Button(
                self.root,
                image=button_image_save,
                borderwidth=0,
                highlightthickness=0,
                command=self.save_input,
                relief="flat"
            )
            save_button.image = button_image_save
            save_button.place(x=135, y=260, width=151, height=69)
            save_button.bind("<Enter>", lambda e: save_button.config(image=button_hover_save))
            save_button.bind("<Leave>", lambda e: save_button.config(image=button_image_save))
            
    def save_input(self):
        word = self.entry_1.get()
        if word:
            self.stored_words.append(word)
            print("Saved word:", word)
            self.entry_1.delete(0, tk.END)

    def load_practice_screen(self):
        self.canvas.delete("all")
        self.canvas.create_rectangle(11, 138, 411, 401, fill="#FFFFFF", outline="")

        if self.stored_words:
            word = self.stored_words[0]
        else:
            word = "No words saved"

        self.canvas.create_text(65, 180, anchor="nw", text=word, fill="#000000", font=("Arial", 16))

        button_image_4 = PhotoImage(file=relative_to_assets("button_4.png"))
        flip_button = Button(
            image=self.button_image_4,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.load_practice_screen,
            relief="flat"
        )
        flip_button.place(
            x=56.0,
            y=411.0,
            width=137.0,
            height=55.0
        )
  
        def flip_button_leave(e):
            flip_button.config(
                image=button_image_4
            )

        flip_button.bind('<Enter>', lambda e: flip_button.config(image=button_image_hover_4))
        flip_button.bind('<Leave>', lambda e: flip_button.config(image=button_image_4))

        
        button_image_5 = PhotoImage(file=relative_to_assets("button_5.png"))
        next_button = Button(
            image=button_image_5,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: print("Next button_5 clicked"),
            relief="flat"
        )
        
        button_image_hover_3 = PhotoImage(
            file=relative_to_assets("button_hover_3.png"))


        
        next_button.place(
            x=230.0,
            y=411.0,
            width=137.0,
            height=55.0
        )

        button_image_6 = PhotoImage(file=relative_to_assets("button_6.png"))
        back_button = Button(
            image=button_image_6,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: print("back_button button_6 clicked"),
            relief="flat"
        )
        back_button.place(
            x=140.0,
            y=472.0,
            width=147.0,
            height=61.0
        )
        canvas.create_rectangle(
            11.0,
            138.0,
            411.0,
            401.0,
            fill="#FFFFFF",
            outline="")

        button_image_hover_5 = PhotoImage(
            file=relative_to_assets("button_hover_5.png"))

        def next_button_hover(e):
            next_button.config(
                image=button_image_hover_5
            )
        def next_button_leave(e):
            next_button.config(
                image=button_image_5
            )

        next_button.bind('<Enter>', next_button_hover)
        next_button.bind('<Leave>', next_button_leave)

        button_image_hover_6 = PhotoImage(
            file=relative_to_assets("button_hover_6.png"))

        def back_button_hover(e):
            back_button.config(
                image=button_image_hover_6
            )
        def back_button_leave(e):
            back_button.config(
                image=button_image_6
            )

        back_button.bind('<Enter>', back_button_hover)
        back_button.bind('<Leave>', back_button_leave)

        image_image_1 = PhotoImage(
            file=relative_to_assets("image_1.png"))
        image_1 = canvas.create_image(
            211.0,
            269.0,
            image=image_image_1
        )
        canvas.create_text(
            65.0,
            180.0,
            anchor="nw",
            text="card text goes here",
            fill="#000000",
            font=(ribeye, 16 * -1)
        )
    