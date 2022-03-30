import sys

from utils.project.password_hashing import hash_password, decrypt_password

MIN_LENGTH = 5
MAX_LENGTH = 20


def main():
    args = sys.argv[1:]
    for arg in args:
        if not MIN_LENGTH <= len(arg) <= MAX_LENGTH:
            print(f"Password ({arg}) length must be between {MIN_LENGTH} and {MAX_LENGTH}")
        else:
            a = hash_password(arg)
            print(f"Input: {arg}, hash = {a}")


if __name__ == '__main__':
    main()
