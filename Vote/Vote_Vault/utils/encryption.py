# utils/encryption.py

from cryptography.fernet import Fernet

# Generate a key (Do this once, save it securely)
# key = Fernet.generate_key()
# print(key)

# Replace with your saved key
FERNET_KEY = b'Cg7NNnUe1cV_Sy7JUnSaKBTimIdfKIM4nIiUBHaBbD8='

cipher = Fernet(FERNET_KEY)

def encrypt_vote(vote_data):
    return cipher.encrypt(vote_data.encode()).decode()

def decrypt_vote(encrypted_vote):
    return cipher.decrypt(encrypted_vote.encode()).decode()
