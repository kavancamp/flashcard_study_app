from database import init_db, add_new_stack, add_new_card

def seed_data():
    init_db()

    sample_data = {
        "French Basics": [
            ("Bonjour", "Hello"),
            ("Merci", "Thank you"),
            ("Au revoir", "Goodbye"),
            ("Chat", "Cat"),
            ("Chien", "Dog")
        ],
        "Python Terms": [
            ("List", "A collection which is ordered and mutable"),
            ("Tuple", "An immutable ordered sequence of items"),
            ("Dictionary", "Key-value pairs in Python"),
            ("Function", "A block of reusable code"),
            ("Loop", "Repeats a block of code")
        ],
        "US Capitals": [
            ("Texas", "Austin"),
            ("California", "Sacramento"),
            ("New York", "Albany"),
            ("Illinois", "Springfield"),
            ("Florida", "Tallahassee")
        ],
        "Anatomy": [
            ("Femur", "Thigh bone"),
            ("Humerus", "Upper arm bone"),
            ("Scapula", "Shoulder blade"),
            ("Cranium", "Skull"),
            ("Tibia", "Shin bone")
        ],
        "Computer Science": [
            ("Algorithm", "Step-by-step instructions for solving a problem"),
            ("Variable", "Named storage for a value"),
            ("Recursion", "Function calling itself"),
            ("Class", "Blueprint for objects"),
            ("Object", "An instance of a class")
        ]
    }

    for stack_name, cards in sample_data.items():
        stack_id = add_new_stack(stack_name)
        for word, definition in cards:
            add_new_card(stack_id, word, definition)

    print("Seed data inserted successfully.")

if __name__ == "__main__":
    seed_data()
