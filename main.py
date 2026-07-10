from database import setup_database
from login import start_login


def main():
    setup_database()
    start_login()


if __name__ == "__main__":
    main()
