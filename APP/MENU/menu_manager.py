import json
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from APP.LOGS.error_handler import error_handler

console = Console(force_terminal=True, color_system="truecolor")


class MenuManager:

    def __init__(self):
        self.file = "APP/DATABASE/menu.json"

    def load(self):
        try:
            with open(self.file, "r") as f:
                return json.load(f)
        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "load", e)
            return []

    def save(self, data):
        try:
            with open(self.file, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "save", e)

    # ================= VIEW MENU =================
    def view_menu(self):
        try:
            data = self.load()

            if not data:
                console.print("[bold red]❌ Menu empty![/bold red]")
                return

            console.print(Panel(
                "🍽️ [bold green]WELCOME TO RESTAURANT MANAGEMENT SYSTEM[/bold green]",
                border_style="cyan"
            ))

            # 🔥 AVAILABLE DELIVERY CITIES
            console.print(Panel(
                "[bold yellow]📍 AVAILABLE DELIVERY CITIES[/bold yellow]\n\n"
                "✔ Delhi     ✔ Mumbai     ✔ Bangalore\n"
                "✔ Chennai   ✔ Kolkata    ✔ Hyderabad\n"
                "✔ Ahmedabad ✔ Pune       ✔ Surat\n"
                "✔ Jaipur    ✔ Lucknow    ✔ Kanpur\n"
                "✔ Nagpur    ✔ Indore     ✔ Bhopal\n"
                "✔ Patna     ✔ Varanasi   ✔ Agra\n"
                "✔ Amritsar  ✔ Kochi",
                border_style="yellow"
            ))

            categories = ["veg", "nonveg", "snacks", "dessert", "drinks"]

            today = datetime.now().strftime("%A")

            for cat in categories:

                table = Table(
                    title=f"[bold yellow]🍴 {cat.upper()} MENU[/bold yellow]",
                    box=box.DOUBLE_EDGE,
                    show_lines=True
                )

                table.add_column("ID", style="bold yellow", justify="center")
                table.add_column("Dish Name", style="bold cyan")
                table.add_column("Price", style="bold green")
                table.add_column("Rating", style="magenta")
                table.add_column("Time", style="blue")
                table.add_column("Status", style="bold white")

                found = False

                for item in data:
                    if item.get("category") == cat:
                        found = True

                        rating = f"⭐ {item.get('rating', 4.0)}"
                        time = f"⏱️ {item.get('time', 10)} min"

                        if item.get("category") == "drinks" and item.get("price_map"):
                            sizes = " | ".join([f"{k}: ₹{v}" for k, v in item["price_map"].items()])
                            price_display = f"[bold green]{sizes}[/bold green]"
                            name = f"{item.get('name')} 🥤"

                        else:
                            price = item.get("price", 0)

                            final_price = int(price * 0.8)

                            if item.get("combo"):
                                name = f"{item.get('name')} 🍱"
                                price_display = f"[yellow]₹{price} (Combo)[/yellow]"
                            else:
                                name = item.get("name")
                                price_display = f"[red]₹{price}[/red] → [green]₹{final_price}[/green] (20% OFF)"

                        if cat == "nonveg" and today in ["Tuesday", "Thursday", "Saturday"]:
                            status = "[red]❌ Blocked Today[/red]"
                        else:
                            status = "[green]✅ Available[/green]" if item.get("available", True) else "[red]❌ Out[/red]"

                        table.add_row(
                            str(item.get("id")),
                            name,
                            price_display,
                            rating,
                            time,
                            status
                        )

                if found:
                    console.print(Panel(table, border_style="magenta"))
                else:
                    console.print(Panel(
                        f"[red]No items in {cat}[/red]",
                        border_style="red"
                    ))

        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "view_menu", e)

    # ================= ADD ITEM =================
    def add_item(self):
        try:
            data = self.load()

            console.print(Panel("➕ [bold green]ADD NEW ITEM[/bold green]", border_style="green"))

            valid_categories = ["veg", "nonveg", "drinks", "dessert", "snacks"]

            item_id = int(input("Enter ID: "))

            for item in data:
                if item.get("id") == item_id:
                    console.print("[red]❌ ID already exists![/red]")
                    return

            name = input("Enter Name: ")
            category = input("Enter Category (veg/nonveg/drinks/dessert/snacks): ").lower()

            if category not in valid_categories:
                console.print("[bold red]❌ Invalid category![/bold red]")
                return
            
            if category == "drinks":
                sizes_input = input("Enter sizes (comma separated): ")
                sizes = [s.strip() for s in sizes_input.split(",")]

                price_dict = {}
                for size in sizes:
                    price_dict[size] = int(input(f"Price for {size}: "))

                price = 0
            else:
                price = int(input("Enter Price: "))
                price_dict = None

            rating = float(input("Enter Rating (1-5): "))
            time = int(input("Preparation Time (min): "))

            item = {
                "id": item_id,
                "name": name,
                "category": category,
                "price": price,
                "price_map": price_dict,
                "rating": rating,
                "time": time,
                "available": True
            }

            combo_choice = input("Is this a combo? (y/n): ").lower()

            if combo_choice == "y":

                combo_items = input("Enter combo items (comma separated): ").split(",")
                combo_items = [i.strip() for i in combo_items]

                combo_price = int(input("Enter Combo Price: "))
                combo_time = int(input("Enter Combo Preparation Time: "))

                try:
                    with open("APP/DATABASE/combo.json", "r") as f:
                        combos = json.load(f)
                except:
                    combos = []

                combo_data = {
                    "id": item_id,
                    "name": name,
                    "items": combo_items,
                    "price": combo_price,
                    "time": combo_time
                }

                combos.append(combo_data)

                with open("APP/DATABASE/combo.json", "w") as f:
                    json.dump(combos, f, indent=4)

                item["combo"] = True
                item["price"] = combo_price
                item["time"] = combo_time
            else:
                item["combo"] = False

            data.append(item)
            self.save(data)

            console.print("[bold green]✅ Item Added Successfully![/bold green]")

        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "add_item", e)

    # ================= UPDATE =================
    def update_item(self):
        try:
            data = self.load()

            item_id = int(input("Enter Item ID to update: "))

            for item in data:
                if item.get("id") == item_id:

                    console.print("[yellow]Leave blank to keep old value[/yellow]")

                    name = input(f"New Name ({item['name']}): ")
                    category = input(f"New Category ({item['category']}): ")
                    price = input(f"New Price ({item['price']}): ")
                    available = input("Available? (y/n): ")

                    if name:
                        item["name"] = name
                    if category:
                        item["category"] = category.lower()
                    if price:
                        item["price"] = int(price)
                    if available:
                        item["available"] = True if available.lower() == "y" else False

                    self.save(data)
                    console.print("[green]Item Updated Successfully![/green]")
                    return

            console.print("[red]Item not found![/red]")

        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "update_item", e)

    # ================= DELETE =================
    def delete_item(self):
        try:
            data = self.load()

            item_id = int(input("Enter Item ID to delete: "))

            new_data = [i for i in data if i.get("id") != item_id]

            if len(new_data) == len(data):
                console.print("[red]Item not found![/red]")
                return

            self.save(new_data)
            console.print("[bold red]🗑️ Item Deleted Successfully![/bold red]")

        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "delete_item", e)


# ================= MENU =================
def menu_manager_menu():
    mm = MenuManager()

    while True:
        try:
            console.print(Panel(
                "[bold blue]📋 MENU MANAGEMENT 📋[/bold blue]\n\n"
                "[bold cyan]1. View Menu [bold cyan]\n"
                "[bold green]2. Add Item [bold green]\n"
                "[bold yellow]3. Update Item [bold yellow]\n"
                "[bold red]4. Delete Item [bold red]\n"
                "[bold magenta]5. Back [bold magenta]",
                border_style="blue"
            ))

            choice = input("Enter choice: ")

            if choice == "1":
                mm.view_menu()
            elif choice == "2":
                mm.add_item()
            elif choice == "3":
                mm.update_item()
            elif choice == "4":
                mm.delete_item()
            elif choice == "5":
                break
            else:
                console.print("[red]Invalid choice![/red]")

        except Exception as e:
            error_handler.log_exception("MenuManager", "menu_loop", e)
            console.print("[red]Menu Error![/red]")