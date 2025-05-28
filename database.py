import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).parent / 'data' / 'flashcards.db'
DB_NAME = "flashcards.db"

# Create database tables if not present
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create flashcard_sets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS card_sets (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT NOT NULL
        )
    ''')

    # table with foreign key reference to card_sets
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stack_id INTEGER NOT NULL,
            word TEXT NOT NULL,
            definition TEXT NOT NULL,
            FOREIGN KEY (stack_id) REFERENCES card_sets(id)               
        )
    ''')
    conn.commit()
    conn.close()
    
# Add a new flashcard set to the database
def add_new_stack(name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO card_sets (name)
        VALUES (?)
    ''', (name,))
    stack_id = cursor.lastrowid
    conn.commit()
    return stack_id

# Function to add a flashcard to the database
def add_new_card(stack_id, word, definition):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # new flashcard into database
    cursor.execute('''
        INSERT INTO cards (stack_id, word, definition)
        VALUES (?, ?, ?)
    ''', (stack_id, word, definition))

    #  ID of the new card
    card_id = cursor.lastrowid
    conn.commit()
    return card_id

# retrieve all flashcard sets from the database
def get_stacks():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Execite SQL query to fetch all card sets
    cursor.execute('''
        SELECT id, name FROM card_sets
    ''')
    rows = cursor.fetchall()
    sets = {row[1]: row[0] for row in rows} # Create a dictionary of sets (name: id)
    return sets

# Function to retrieve all flashcards of a specific set
def get_cards(stack_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT word, definition FROM cards
        WHERE stack_id = ?
    ''', (stack_id,))

    rows = cursor.fetchall()
    # list of cards (word, definition)
    cards = [(row[0], row[1]) for row in rows] 

    return cards

# delete a card set from the database
def delete_set(stack_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # query to delete a card set
    cursor.execute('''
        DELETE FROM card_sets
        WHERE id = ?
    ''', (stack_id,))

    conn.commit()
    global current_cards, card_index
    current_cards = []
    card_index = 0
