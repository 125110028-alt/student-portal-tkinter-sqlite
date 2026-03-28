from database import create_tables, insert_default_admin
from login import start_login

from navigation import App

if __name__ == "__main__":
    app = App()
    app.mainloop()

