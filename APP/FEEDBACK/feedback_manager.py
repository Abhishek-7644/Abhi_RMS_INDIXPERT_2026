from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
import json
import os
from statistics import mean
from APP.LOGS.error_handler import error_handler

console = Console(force_terminal=True, color_system="truecolor")
FILE = "APP/DATABASE/feedback.json"


class FeedbackManager:

    def __init__(self):
        try:
            if not os.path.exists(FILE):
                with open(FILE, "w") as f:
                    json.dump([], f)
        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "__init__", e)

    # ================= LOAD =================
    def load(self):
        try:
            with open(FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "load", e)
            return []

    # ================= SAVE =================
    def save(self, data):
        try:
            with open(FILE, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "save", e)

    # ================= ADD FEEDBACK =================
    def add_feedback(self):
        try:
            console.print(Panel(
                "[bold cyan]⭐ GIVE YOUR FEEDBACK[/bold cyan]",
                border_style="cyan"
            ))

            name = input("Enter your name:  ")

            rating = int(input("Rating (1-5):"))
            if rating < 1 or rating > 5:
                console.print("[bold red]❌ Rating must be between 1 and 5![/bold red]")
                return

            comment = input("Comment: ")

            data = self.load()
            data.append({
                "name": name,
                "rating": rating,
                "comment": comment
            })

            self.save(data)

            console.print(Panel(
                "[bold green]✅ Feedback Added Successfully![/bold green]",
                border_style="green"
            ))

        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "add_feedback", e)
            console.print("[bold red]❌ Failed to add feedback![/bold red]")

    # ================= VIEW FEEDBACK =================
    def view_feedback(self):
        try:
            data = self.load()

            if not data:
                console.print("[red]No feedback found![/red]")
                return

            table = Table(
                title="⭐ USER FEEDBACK",
                box=box.DOUBLE_EDGE,
                show_lines=True
            )

            table.add_column("Name", style="cyan", justify="center")
            table.add_column("Rating", style="yellow", justify="center")
            table.add_column("Comment", style="white")

            for f in data:
                table.add_row(
                    f.get("name"),
                    f"⭐ {f.get('rating')}",
                    f.get("comment")
                )

            console.print(Panel(table, border_style="magenta"))

        
            ratings = [f.get("rating", 0) for f in data]
            avg = round(mean(ratings), 2)

            console.print(Panel(
                f"[bold green]⭐ Average Rating: {avg}/5[/bold green]",
                border_style="green"
            ))

        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "view_feedback", e)

    # ================= SEARCH =================
    def search_feedback(self):
        try:
            name = input("Enter name to search: ").lower()
            data = self.load()

            found = [f for f in data if name in f.get("name", "").lower()]

            if not found:
                console.print("[red]❌ No feedback found[/red]")
                return

            for f in found:
                console.print(Panel(
                    f"[cyan]Name:[/cyan] {f['name']}\n"
                    f"Rating: ⭐ {f['rating']}\n"
                    f"Comment: {f['comment']}",
                    border_style="cyan"
                ))

        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "search_feedback", e)

    # ================= DELETE =================
    def delete_feedback(self):
        try:
            name = input("Enter name to delete feedback: ").lower()
            data = self.load()

            new_data = [f for f in data if f.get("name", "").lower() != name]

            if len(new_data) == len(data):
                console.print("[red]❌ Feedback not found[/red]")
                return

            self.save(new_data)
            console.print("[bold red]🗑️ Feedback Deleted[/bold red]")

        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "delete_feedback", e)

    # ================= SUMMARY =================
    def summary(self):
        try:
            data = self.load()

            if not data:
                console.print("[red]No data[/red]")
                return

            count = {i: 0 for i in range(1, 6)}

            for f in data:
                count[f.get("rating", 0)] += 1

            table = Table(title="📊 RATING SUMMARY", box=box.ROUNDED)
            table.add_column("Rating", style="yellow")
            table.add_column("Count", style="green")

            for k, v in count.items():
                table.add_row(f"{k} ⭐", str(v))

            console.print(Panel(table, border_style="blue"))

        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "summary", e)


# ================= MENU =================
def feedback_menu():
    fm = FeedbackManager()

    while True:
        try:
            console.print(Panel(
                "[bold magenta]⭐ FEEDBACK MENU ⭐[/bold magenta]\n\n"
                "[cyan]1.[/cyan] Add Feedback\n"
                "[cyan]2.[/cyan] View Feedback\n"
                "[cyan]3.[/cyan] Search Feedback\n"
                "[cyan]4.[/cyan] Delete Feedback\n"
                "[cyan]5.[/cyan] Rating Summary\n"
                "[cyan]6.[/cyan] Back",
                border_style="magenta"
            ))

            ch = input("Enter choice: ")

            if ch == "1":
                fm.add_feedback()
            elif ch == "2":
                fm.view_feedback()
            elif ch == "3":
                fm.search_feedback()
            elif ch == "4":
                fm.delete_feedback()
            elif ch == "5":
                fm.summary()
            elif ch == "6":
                break
            else:
                console.print("[red]Invalid![/red]")

        except Exception as e:
            error_handler.log_exception("FeedbackMenu", "menu_loop", e)
            console.print("[red]Menu Error![/red]")