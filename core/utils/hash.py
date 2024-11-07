import secrets
import string
from .repr import NiceRepr

def create_hash(n=64, numbers=True, letters=True, symbols=False):
    characters = ''
    if numbers:
        characters += string.digits
    if letters:
        characters += string.ascii_letters
    if symbols:
        characters += string.punctuation

    lower_bound = 10**(n-1)
    upper_bound = 10**n - 1
    random_number = secrets.randbelow(upper_bound - lower_bound + 1) + lower_bound

    hash_value = ''.join(secrets.choice(characters) for _ in range(n))
    return hash_value


class HashDict(dict):
    def __init__(self, values=None, hash_size=3):
        self.hash_size = hash_size
        if values is not None:
            self.__dict__.update(values)

    def put(self, value):
        while True:
            key = create_hash(self.hash_size)
            if key not in self:
                break
            graph.hash_size += 1
        self[key] = value
        return key
