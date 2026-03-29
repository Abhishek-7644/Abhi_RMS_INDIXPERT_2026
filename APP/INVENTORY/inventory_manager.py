import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from APP.LOGS.error_handler import error_handler

console = Console(force_terminal=True, color_system="truecolor")


class InventoryManager:

    def __init__(self):
        self.file = "APP/DATABASE/inventory.json"

    # ================= LOAD =================
    def load(self):
        try:
            with open(self.file, "r") as f:
                return json.load(f)
        except:
            return []

    # ================= SAVE =================
    def save(self, data):
        try:
            with open(self.file, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "save", e)

    # ================= VIEW =================
    def view(self):
        try:
            data = self.load()

            if not data:
                console.print("[bold red] Inventory Empty[/bold red]")
                return

            categories = {}

            
            for item in data:
                cat = item.get("category", "Other")
                categories.setdefault(cat, []).append(item)

            
            for cat, items in categories.items():

               
                color_map = {
                    "Veg": "green",
                    "Non-Veg": "red",
                    "Grocery": "blue",
                    "Sweets": "magenta"
                }

                border_color = color_map.get(cat, "cyan")

                table = Table(
                    title=f"📦 {cat.upper()} ITEMS",
                    box=box.ROUNDED
                )

                table.add_column("Item", style="bold cyan")
                table.add_column("Qty", style="bold green")
                table.add_column("Status", style="bold yellow")

                for item in items:
                    qty = item.get("qty", 0)

                    if qty < 5:
                        status = "[red]⚠️ Low[/red]"
                    else:
                        status = "[green]✅ OK[/green]"

                    table.add_row(item.get("name"), str(qty), status)

                console.print(Panel(table, border_style=border_color))

        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "view", e)

    # ================= ADD =================
    def add(self):
        try:
            console.print("[yellow]Item Name:[/yellow]", end=" ")
            name = input().strip()

            console.print("[yellow]Quantity:[/yellow]", end=" ")
            qty = int(input())

            
            console.print(
                "\n[bold cyan]Select Category:[/bold cyan]\n"
                "[green]1. Veg[/green]\n"
                "[red]2. Non-Veg[/red]\n"
                "[blue]3. Grocery[/blue]\n"
                "[magenta]4. Sweets[/magenta]"
            )

            console.print("[yellow]Enter choice:[/yellow]", end=" ")
            ch = input()

            category_map = {
                "1": "Veg",
                "2": "Non-Veg",
                "3": "Grocery",
                "4": "Sweets"
            }

            category = category_map.get(ch, "Other")

            data = self.load()

        
            for item in data:
                if item["name"].lower() == name.lower():
                    item["qty"] += qty
                    item["category"] = category
                    self.save(data)
                    console.print("[green]🔄 Item Updated[/green]")
                    return

           
            data.append({
                "name": name,
                "qty": qty,
                "category": category
            })

            self.save(data)

            console.print("[bold green]✅ Item Added[/bold green]")

        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "add", e)

    # ================= REMOVE =================
    def remove(self):
        try:
            console.print("[yellow]Item Name to remove:[/yellow]", end=" ")
            name = input().lower()

            data = self.load()

            new = [i for i in data if i["name"].lower() != name]

            if len(new) == len(data):
                console.print("[red]❌ Item not found[/red]")
                return

            self.save(new)

            console.print("[bold red]🗑️ Item Removed[/bold red]")

        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "remove", e)

    # ================= UPDATE =================
    def update(self):
        try:
            console.print("[yellow]Item Name:[/yellow]", end=" ")
            name = input().lower()

            console.print("[yellow]New Quantity:[/yellow]", end=" ")
            qty = int(input())

            data = self.load()

            for i in data:
                if i["name"].lower() == name:
                    i["qty"] = qty
                    self.save(data)
                    console.print("[bold green]🔄 Updated Successfully[/bold green]")
                    return

            console.print("[red] Item not found[/red]")

        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "update", e)

    # ================= SEARCH =================
    def search(self):
        try:
            console.print("[yellow]Search Item:[/yellow]", end=" ")
            name = input().lower()

            data = self.load()

            found = [i for i in data if name in i["name"].lower()]

            if not found:
                console.print("[red] Item not found[/red]")
                return

            for i in found:
                console.print(Panel(
                    f"[cyan]Item:[/cyan] {i['name']}\n"
                    f"[green]Quantity:[/green] {i['qty']}\n"
                    f"[magenta]Category:[/magenta] {i.get('category','-')}",
                    border_style="cyan"
                ))

        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "search", e)

    # ================= LOW STOCK =================
    def low_stock(self):
        try:
            data = self.load()

            low = [i for i in data if i.get("qty", 0) < 5]

            if not low:
                console.print("[green]✅ No Low Stock Items[/green]")
                return

            table = Table(title="⚠️ LOW STOCK ALERT", box=box.ROUNDED)

            table.add_column("Item", style="red")
            table.add_column("Qty", style="yellow")
            table.add_column("Category", style="cyan")

            for i in low:
                table.add_row(i["name"], str(i["qty"]), i.get("category", "-"))

            console.print(Panel(table, border_style="red"))

        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "low_stock", e)


# ================= MENU =================
def inventory_staff_menu():
    im = InventoryManager()

    while True:
        try:
            console.print(Panel(
                "[bold blue]📦 INVENTORY STAFF MENU[/bold blue]\n\n"
                "[bold cyan]1. View Inventory[/bold cyan]\n"
                "[bold green]2. Add Item[/bold green]\n"
                "[bold yellow]3. Update Item[/bold yellow]\n"
                "[bold red]4. Remove Item[/bold red]\n"
                "[bold magenta]5. Search Item[/bold magenta]\n"
                "[bold white]6. Low Stock Alert[/bold white]\n"
                "[bold blue]7. Back[/bold blue]",
                border_style="blue"
            ))

            console.print("[yellow]Enter choice:[/yellow]", end=" ")
            ch = input()

            if ch == "1":
                im.view()
            elif ch == "2":
                im.add()
            elif ch == "3":
                im.update()
            elif ch == "4":
                im.remove()
            elif ch == "5":
                im.search()
            elif ch == "6":
                im.low_stock()
            elif ch == "7":
                break
            else:
                console.print("[red]❌ Invalid choice[/red]")

        except Exception as e:
            error_handler.log_exception("InventoryMenu", "loop", e)
            console.print("[red]Menu Error![/red]")