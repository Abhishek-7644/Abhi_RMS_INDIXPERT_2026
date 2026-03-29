from rich.console import Console
from rich.panel import Panel

from APP.AUTH.signup import Signup
from APP.AUTH.login import Login
from APP.LOGS.error_handler import error_handler
from APP.DASHBOARD.dashboard_manager import DashboardManager


console = Console(force_terminal=True, color_system="truecolor")


class AuthMenu:
    def __init__(self):
        self.signup = Signup()
        self.login = Login()
        self.dashboard = DashboardManager()

    def start(self):
        while True:
            try:
                console.print(Panel(
                    "[bold yellow]🍽️ RESTAURANT MANAGEMENT SYSTEM[/bold yellow]\n\n"
                    "[bold green]1. Signup [/bold green]\n"
                    "[bold cyan]2.Login [/bold cyan]\n"
                    "[bold red]3.Exit [bold red]",
                    border_style="green"
                ))

                ch = input("Enter choice: ")

                if ch == "1":
                    self.signup.run()

                elif ch == "2":
                    user = self.login.run()
                    if user:

                        self.dashboard.redirect(user)

                elif ch == "3":
                    console.print("[bold red]Exiting...[/bold red]")
                    break

                else:
                    console.print("[red]Invalid choice![/red]")

            except Exception as e:
                error_handler.log_exception("AuthMenu", "start", e)


def start_menu():
    AuthMenu().start()