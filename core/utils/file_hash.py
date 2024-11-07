import sys
import os
import hashlib

def hash_file(filename):
    h = hashlib.sha256()
    with open(filename, 'rb') as file:
        chunk = 0
        while chunk != b'':
            chunk = file.read(1024)
            h.update(chunk)
    return h.hexdigest()

def recursive_hashing(file_path, unique_hash, ignore_list):
    # Skip if the file or directory is in ignore_list
    if os.path.basename(file_path) in ignore_list:
        return

    if os.path.isfile(file_path):
        unique_hash.update(hash_file(file_path).encode('utf-8'))
    elif os.path.isdir(file_path):
        for child in sorted(os.listdir(file_path)):  # Sort the filenames
            recursive_hashing(os.path.join(file_path, child), unique_hash, ignore_list)
            

def main():
    unique_hash = hashlib.sha256()
    ignore_list = ['__pycache__']  # List of files and directories to ignore

    for file_path in sys.argv[1:]:
        if os.path.exists(file_path):
            recursive_hashing(file_path, unique_hash, ignore_list)
        else:
            continue

    print(unique_hash.hexdigest())

if __name__ == "__main__":
    main()
