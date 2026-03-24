
from getpass import getpass
from rich.console import Console
from rich.panel import Panel
from APP.DATABASE.db import Database
from APP.LOGS.error_handler import error_handler
import random
import string 

console = Console(force_terminal=True, color_system="truecolor")


class Login:
    def __init__(self):
        self.db = Database()

   
    def generate_captcha(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

    def run(self):
        try:
            console.print(Panel("🔐 LOGIN", border_style="cyan"))

            users = self.db.load_users()

            for attempt in range(3):
                try:
                    # ================= USERNAME =================
                    console.print("Enter Username:", style="yellow", end=" ")
                    username = input()

                    # ================= PASSWORD =================
                    console.print("Enter Password:", style="yellow", end=" ")
                    password = getpass("")

                    # ================= CAPTCHA =================
                    captcha = self.generate_captcha()
                    console.print(f"CAPTCHA: {captcha}", style="bold magenta")

                    console.print("Enter CAPTCHA:", style="yellow", end=" ")
                    user_captcha = input()

                    if user_captcha != captcha:
                        console.print("❌ Wrong CAPTCHA!", style="red")
                        continue

                    # ================= LOGIN CHECK =================
                    for user in users:
                        if user["username"] == username and user["password"] == password:
                            console.print("✅ Login Successful", style="bold green")
                            return user

                    console.print(
                        f"❌ Invalid credentials! Attempts left: {2 - attempt}",
                        style="red"
                    )

                except Exception as e:
                    error_handler.log_exception(
                        self.__class__.__name__,
                        "input_login",
                        e
                    )
                    console.print("⚠️ Input error! Try again.", style="red")

            console.print("❌ Too many attempts!", style="bold red")

            error_handler.log_error(
                self.__class__.__name__,
                "run",
                "User failed login 3 times"
            )

            return None

        except Exception as e:
            error_handler.log_exception(
                self.__class__.__name__,
                "run",
                e
            )
            console.print("❌ Login system error!", style="bold red")
            return None