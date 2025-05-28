from database_cleaned import init_db, add_new_stack, add_new_card

def seed():
    # Initialize DB and tables
    init_db()

    # Create example sets
    vocab_id = add_new_stack("Vocabulary")
    math_id = add_new_stack("Math")

    # Add flashcards to "Vocabulary"
    add_new_card(vocab_id, "Abate", "To lessen in intensity")
    add_new_card(vocab_id, "Eloquent", "Fluent or persuasive in speaking or writing")
    
    # Add flashcards to "Math"
    add_new_card(math_id, "Pi", "Ratio of circumference to diameter of a circle")
    add_new_card(math_id, "Derivative", "The rate at which a function is changing at any given point")

    print("Seed data inserted successfully.")

if __name__ == "__main__":
    seed()
