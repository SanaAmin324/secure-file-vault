import hashlib
import os

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def setup_password():
    print("\n=== FIRST TIME SETUP ===")

    password = input("Create a master password: ")

    hashed_password = hash_password(password)

    with open("data/password.txt", "w") as file:
        file.write(hashed_password)

    print("Master password created successfully!")
    
def login():
    password = input("Enter master password: ")

    entered_hash = hash_password(password)

    with open("data/password.txt", "r") as file:
        stored_hash = file.read().strip()

    if entered_hash == stored_hash:
        print("Access Granted!")
        return True

    else:
        print("Access Denied!")
        return False
    
def password_exists():
    return (
        os.path.exists("data/password.txt")
        and os.path.getsize("data/password.txt") > 0
    )

def menu():
    print("\n=====^v^=== SECURE FILE VAULT ===^v^=====")
    print("1. Add Secret")
    print("2. View Secrets")
    print("3. Exit")
    
    
def add_secret():
    secret = input("\nEnter your secret: ")

    with open("data/notes.txt", "a") as file:
        file.write(secret + "\n")

    print("Secret saved successfully!")
    
    
def view_secrets():
    print("\n=====^v^=== STORED SECRETS ===^v^=====\n")

    try:
        with open("data/notes.txt", "r") as file:
            data = file.read()

            if data.strip() == "":
                print("No secrets found.")
            else:
                print(data)

    except FileNotFoundError:
        print("No file found. Add a secret first.")
        

def main():
    while True:
        menu()
        choice = input("\nChoose an option: ")

        if choice == "1":
            add_secret()

        elif choice == "2":
            view_secrets()

        elif choice == "3":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Try again.")
            

if __name__ == "__main__":

    if not password_exists():
        setup_password()

    if login():
        main()
    else:
        print("Exiting program.")