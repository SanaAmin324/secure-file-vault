import hashlib
import os
from cryptography.fernet import Fernet

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_key():
    key = Fernet.generate_key()

    with open("data/key.key", "wb") as file:
        file.write(key)

    print("Encryption key generated successfully!")
    
def key_exists():
    return (
        os.path.exists("data/key.key")
        and os.path.getsize("data/key.key") > 0
    )
    
def load_key():
    with open("data/key.key", "rb") as file:
        return file.read()
    
def encrypt_data(data):
    key = load_key()

    fernet = Fernet(key)

    encrypted_data = fernet.encrypt(data.encode())

    return encrypted_data.decode()

def decrypt_data(encrypted_text):
    key = load_key()
    fernet = Fernet(key)

    decrypted_data = fernet.decrypt(encrypted_text.encode())

    return decrypted_data.decode()

def setup_password():
    print("\n=== FIRST TIME SETUP ===")

    password = input("Create a master password: ")

    hashed_password = hash_password(password)

    with open("data/password.txt", "w") as file:
        file.write(hashed_password)

    print("Master password created successfully!")
    
def login():
    attempt_number=1
    max_attempts=3
    attempts = 3

    while attempts > 0:

        print(f"\nAttempt: {attempt_number}/{max_attempts}")
        attempt_number+=1
        password = input("Enter master password: ")

        entered_hash = hash_password(password)

        with open("data/password.txt", "r") as file:
            stored_hash = file.read().strip()

        if entered_hash == stored_hash:
            print("Access Granted!")
            return True

        else:
            attempts -= 1
            print("Access Denied!")

    print("Too many failed attempts. Exiting.")
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

    encrypted_secret = encrypt_data(secret)

    with open("data/notes.txt", "a") as file:
        file.write(encrypted_secret + "\n")

    print("Secret encrypted and saved successfully!")
    
    
def view_secrets():
    print("\n=====^v^=== STORED SECRETS ===^v^=====\n")

    try:
        with open("data/notes.txt", "r") as file:
            lines = file.readlines()

            if not lines:
                print("No secrets found.")
                return

            for line in lines:
                encrypted_line = line.strip()
                decrypted_line = decrypt_data(encrypted_line)
                print(decrypted_line)

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

        if not key_exists():
            generate_key()

        main()

    else:
        print("Exiting program.")