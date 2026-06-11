import hashlib
import os
from cryptography.fernet import Fernet
from datetime import datetime

def write_log(action):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("data/activity.log", "a") as file:
        file.write(f"{timestamp} - {action}\n")

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

def is_strong_password(password):

    has_upper = False
    has_lower = False
    has_digit = False
    has_special = False

    for char in password:

        if char.isupper():
            has_upper = True

        elif char.islower():
            has_lower = True

        elif char.isdigit():
            has_digit = True

        elif not char.isalnum():
            has_special = True

    return (
        len(password) >= 8
        and has_upper
        and has_lower
        and has_digit
        and has_special
    )

def setup_password():
    print("\n=== FIRST TIME SETUP ===")

    while True:

        password = input("Create a master password: ")

        if is_strong_password(password):

            hashed_password = hash_password(password)

            with open("data/password.txt", "w") as file:
                file.write(hashed_password)

            print("Master password created successfully!")
            break

        else:
            print("\nPassword is too weak.")
            print("Requirements:")
            print("- At least 8 characters")
            print("- At least 1 uppercase letter")
            print("- At least 1 lowercase letter")
            print("- At least 1 digit")
            print("- At least 1 special character")
    
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
            write_log("FAILED LOGIN")
            print("Access Denied!")

    print("Too many failed attempts. Exiting.")
    return False
    
def password_exists():
    return (
        os.path.exists("data/password.txt")
        and os.path.getsize("data/password.txt") > 0
    )
    
def view_logs():

    print("\n===== ACTIVITY LOGS =====\n")

    try:

        with open("data/activity.log", "r") as file:

            logs = file.read()

            if logs.strip() == "":
                print("No logs found.")

            else:
                print(logs)

    except FileNotFoundError:
        print("No log file found.")

def menu():
    print("\n=====^v^=== SECURE FILE VAULT ===^v^=====")
    print("1. Add Secret")
    print("2. View All Secrets")
    print("3. Search Secrets")
    print("4. Change Master Password")
    print("5. View Activity Logs")
    print("6. Exit")
    
    
def add_secret():
    secret = input("\nEnter your secret: ")

    encrypted_secret = encrypt_data(secret)

    with open("data/notes.txt", "a") as file:
        file.write(encrypted_secret + "\n")

    write_log("SECRET ADDED")
    print("Secret encrypted and saved successfully!")
    
    
def view_secrets():
    print("\n=====^v^=== STORED SECRETS ===^v^=====\n")

    try:
        with open("data/notes.txt", "r") as file:
            lines = file.readlines()

            if not lines:
                print("No secrets found.")
                return

            write_log("SECRETS VIEWED")
            for line in lines:
                encrypted_line = line.strip()
                decrypted_line = decrypt_data(encrypted_line)
                print(decrypted_line)

    except FileNotFoundError:
        print("No file found. Add a secret first.")
        
    
def change_master_password():

    print("\n===== CHANGE MASTER PASSWORD =====")

    # Step 1: verify old password
    old_password = input("Enter current password: ")
    old_hash = hash_password(old_password)

    with open("data/password.txt", "r") as file:
        stored_hash = file.read().strip()

    if old_hash != stored_hash:
        write_log("FAILED PASSWORD CHANGE")
        print("Incorrect password. Access denied.")
        return

    # Step 2: set new password
    while True:
        new_password = input("Enter new master password: ")

        if is_strong_password(new_password):

            new_hash = hash_password(new_password)

            with open("data/password.txt", "w") as file:
                file.write(new_hash)

            write_log("MASTER PASSWORD CHANGED")
            print("Master password updated successfully!")
            break

        else:
            print("\nPassword too weak. Try again.")
            
def search_secrets():
    print("\n===== SEARCH SECRETS =====")

    keyword = input("Enter keyword to search: ").lower()
    

    try:
        with open("data/notes.txt", "r") as file:
            lines = file.readlines()

            found = False

            write_log("SECRET SEARCH PERFORMED")
            for line in lines:
                decrypted = decrypt_data(line.strip())

                if keyword in decrypted.lower():
                    print("🔎 Found:", decrypted)
                    found = True

            if not found:
                print("No matching secrets found.")

    except FileNotFoundError:
        print("No secrets file found.")
        

def main():
    while True:
        menu()
        choice = input("\nChoose an option: ")

        if choice == "1":
            add_secret()

        elif choice == "2":
            view_secrets()
            
        elif choice == "3":
            search_secrets()

        elif choice == "4":
            change_master_password()

        elif choice == "5":
            view_logs()

        elif choice == "6":
            print("Goodbye!")
            break
 
        else:
            print("Invalid choice. Try again.")
            

            

if __name__ == "__main__":

    if not password_exists():
        setup_password()

    if not key_exists():
        generate_key()

    if login():
        write_log("LOGIN SUCCESS")
        main()

    else:
        print("Exiting program.")