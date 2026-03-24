import json
import os

class Database:
    def __init__(self):
        self.user_file = "APP/DATABASE/user.json"

    def load_users(self):
        if not os.path.exists(self.user_file):
            return []
        with open(self.user_file, "r") as f:
            try:
                return json.load(f)
            except:
                return []

    def save_users(self, users):
        with open(self.user_file, "w") as f:
            json.dump(users, f, indent=4)