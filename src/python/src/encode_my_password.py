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
            a=hash_password(arg)
            print(f"Input: {arg}, hash = {a}")
            print(decrypt_password("hy/aFg4=*do3b+KkmL92/uF8NJMQ9vg==*4K2g/VKQOVzz6ZslL92h/g==*6oGAm+No+iLt2gRE8nNPwA=="))


if __name__ == '__main__':
    main()
