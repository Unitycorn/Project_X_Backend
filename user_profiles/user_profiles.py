from sqlalchemy import create_engine, text

# Define the database URL
DB_URL = "sqlite:///./data/database.db"

# Create the engine
engine = create_engine(DB_URL, echo=False)


def load_users():
    """Retrieve all users from the database."""
    with engine.connect() as connection:
        result = connection.execute(text("SELECT id, name FROM users"))
        users = result.fetchall()
        return users


def add_new_user():
    """Add a new user to the database."""
    new_user = input("Enter new user name: ").capitalize()
    with engine.connect() as connection:
        try:
            connection.execute(text("INSERT INTO users (name) VALUES (:name)"),
                               {"name": new_user})
            connection.commit()
            print(f"User '{new_user}' added successfully.")
            return new_user
        except Exception as e:
            print(f"Error: {e}")


def get_user():
    """
    Retrieve all users from the database, list them in a menu for choosing a profile or adds a new user to the database.
    """
    users = load_users()
    user_counter = 0
    print("\nSelect a user:")
    for i, user in enumerate(users):
        print(f"{i+1}. {user[1]}")
        user_counter += 1
    print(f"{user_counter+1}. Create new user")
    selection = int(input("\nYour choice: "))
    if selection < user_counter + 1:  # only when existing user was selected
        return users[selection-1][1]
    else:
        user = add_new_user()
        return user
