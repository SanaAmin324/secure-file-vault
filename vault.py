import os
import hashlib
import base64
import hmac
import time
from datetime import datetime

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# =========================
# CONFIG
# =========================
DATA_DIR = "data"
PASSWORD_FILE = f"{DATA_DIR}/password.txt"
SALT_FILE = f"{DATA_DIR}/salt.bin"
NOTES_FILE = f"{DATA_DIR}/notes.txt"
LOG_FILE = f"{DATA_DIR}/activity.log"
LOCK_FILE = f"{DATA_DIR}/lock.txt"

PBKDF2_ITERATIONS = 100000


# =========================
# SETUP
# =========================
def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


# =========================
# LOGGING (UPGRADED)
# =========================
def write_log(action, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{level}] {timestamp} - {action}\n")


# =========================
# SALT MANAGEMENT
# =========================
def generate_salt():
    salt = os.urandom(16)
    with open(SALT_FILE, "wb") as f:
        f.write(salt)
    return salt


def load_salt():
    if not os.path.exists(SALT_FILE):
        return generate_salt()
    with open(SALT_FILE, "rb") as f:
        return f.read()


# =========================
# KEY DERIVATION
# =========================
def derive_key(password: str) -> bytes:
    salt = load_salt()

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )

    return kdf.derive(password.encode())


# =========================
# PASSWORD SECURITY
# =========================
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def is_strong_password(password: str) -> bool:
    return (
        len(password) >= 8
        and any(c.isupper() for c in password)
        and any(c.islower() for c in password)
        and any(c.isdigit() for c in password)
        and any(not c.isalnum() for c in password)
    )


# =========================
# LOGIN LOCK SYSTEM
# =========================
def is_locked():
    if not os.path.exists(LOCK_FILE):
        return False

    with open(LOCK_FILE, "r") as f:
        unlock_time = float(f.read())

    if time.time() < unlock_time:
        print("System locked. Try again later.")
        return True

    return False


def lock_system():
    with open(LOCK_FILE, "w") as f:
        f.write(str(time.time() + 30))  # 30 sec lock


# =========================
# SETUP PASSWORD
# =========================
def setup_password():
    print("\n=== FIRST TIME SETUP ===")

    while True:
        password = input("Create master password: ")

        if not is_strong_password(password):
            print("Weak password. Try again.")
            continue

        with open(PASSWORD_FILE, "w") as f:
            f.write(hash_password(password))

        write_log("PASSWORD CREATED")
        print("Master password set.")
        return


# =========================
# LOGIN
# =========================
def login():
    if is_locked():
        return None

    attempts = 3

    while attempts > 0:
        print(f"\nAttempts remaining: {attempts}")

        password = input("Enter master password: ")
        entered_hash = hash_password(password)

        with open(PASSWORD_FILE, "r") as f:
            stored_hash = f.read().strip()

        if entered_hash == stored_hash:
            write_log("LOGIN SUCCESS", "SECURITY")
            return password

        attempts -= 1
        write_log("FAILED LOGIN", "WARNING")

    lock_system()
    write_log("SYSTEM LOCKED", "SECURITY")
    print("Too many failed attempts.")
    return None


# =========================
# HMAC (INTEGRITY LAYER)
# =========================
def generate_hmac_key(password):
    return hashlib.sha256((password + "HMAC").encode()).digest()


def create_signature(data, password):
    key = generate_hmac_key(password)
    return hmac.new(key, data.encode(), hashlib.sha256).hexdigest()


def verify_signature(data, signature, password):
    key = generate_hmac_key(password)
    expected = hmac.new(key, data.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


# =========================
# ENCRYPTION
# =========================
def encrypt_data(data: str, password: str) -> str:
    key = derive_key(password)

    iv = os.urandom(12)
    aesgcm = AESGCM(key)

    ciphertext = aesgcm.encrypt(iv, data.encode(), None)

    payload = base64.b64encode(iv + ciphertext).decode()

    signature = create_signature(payload, password)

    return f"{payload}::{signature}"


def decrypt_data(record: str, password: str) -> str:
    try:
        payload, signature = record.split("::")

        if not verify_signature(payload, signature, password):
            return "[TAMPERED DATA DETECTED]"

        raw = base64.b64decode(payload.encode())

        iv = raw[:12]
        ciphertext = raw[12:]

        key = derive_key(password)
        aesgcm = AESGCM(key)

        return aesgcm.decrypt(iv, ciphertext, None).decode()

    except Exception:
        return "[DECRYPTION FAILED]"


# =========================
# FEATURES
# =========================
def add_secret(password):
    secret = input("Enter secret: ")

    encrypted = encrypt_data(secret, password)

    with open(NOTES_FILE, "a") as f:
        f.write(encrypted + "\n")

    write_log("SECRET ADDED")
    print("Saved securely.")


def view_secrets(password):
    try:
        with open(NOTES_FILE, "r") as f:
            lines = f.readlines()

        if not lines:
            print("No secrets found.")
            return

        write_log("VIEW SECRETS")

        for line in lines:
            print("-", decrypt_data(line.strip(), password))

    except FileNotFoundError:
        print("No file found.")


def search_secrets(password):
    keyword = input("Keyword: ").lower()

    try:
        with open(NOTES_FILE, "r") as f:
            lines = f.readlines()

        found = False
        write_log("SEARCH")

        for line in lines:
            text = decrypt_data(line.strip(), password)

            if keyword in text.lower():
                print("FOUND:", text)
                found = True

        if not found:
            print("No matches.")

    except FileNotFoundError:
        print("No file found.")


# =========================
# MENU
# =========================
def menu():
    print("\n=== SECURE VAULT V9 ===")
    print("1. Add Secret")
    print("2. View Secrets")
    print("3. Search")
    print("4. Exit")


def main(password):
    while True:
        menu()
        choice = input("Choice: ")

        if choice == "1":
            add_secret(password)
        elif choice == "2":
            view_secrets(password)
        elif choice == "3":
            search_secrets(password)
        elif choice == "4":
            print("Goodbye")
            break
        else:
            print("Invalid")


# =========================
# START
# =========================
if __name__ == "__main__":
    ensure_data_dir()

    if not os.path.exists(SALT_FILE):
        generate_salt()

    if not os.path.exists(PASSWORD_FILE):
        setup_password()

    master_password = login()

    if master_password:
        main(master_password)
    else:
        print("Exit")