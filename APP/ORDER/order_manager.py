import json
import random
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from APP.BILLING.payment_menu import PaymentManager
from APP.LOGS.error_handler import error_handler

console = Console(force_terminal=True, color_system="truecolor")


class OrderManager:

    def __init__(self):
        self.menu_file = "APP/DATABASE/menu.json"
        self.order_file = "APP/DATABASE/orders.json"
        self.inventory_file = "APP/DATABASE/inventory.json"

    # ================= BASIC =================
    def load(self, file):
        try:
            with open(file, "r") as f:
                return json.load(f)
        except:
            return []

    def save(self, file, data):
        with open(file, "w") as f:
            json.dump(data, f, indent=4)

    def generate_order_id(self):
        return random.randint(100000, 999999)

    # ================= MENU =================
    def get_item_by_id(self, item_id):
        menu = self.load(self.menu_file)
        for item in menu:
            if int(item.get("id")) == int(item_id):
                return item
        return None

    def search_item(self, keyword):
        menu = self.load(self.menu_file)
        return [i for i in menu if keyword.lower() in i.get("name", "").lower()]

    def load_combos(self):
        try:
            with open("APP/DATABASE/combo.json", "r") as f:
                return json.load(f)
        except:
            return []

    # ================= INVENTORY =================
    def update_inventory(self, name, qty, add_back=False):
        inv = self.load(self.inventory_file)

        for i in inv:
            if i.get("name") == name:
                stock = i.get("stock", i.get("qty", 0))

                if add_back:
                    i["stock"] = stock + qty
                else:
                    if stock < qty:
                        console.print("[red]❌ Not enough stock[/red]")
                        return False
                    i["stock"] = stock - qty

        self.save(self.inventory_file, inv)
        return True

    # ================= CREATE ORDER =================
    def create_order(self):
        username = input("Enter your name: ").strip().lower()

        order_id = self.generate_order_id()
        items = []
        total = 0

        console.print(Panel("[bold green]🛒 CREATE ORDER[/bold green]", border_style="green"))

        # ================= ONLINE / OFFLINE =================
        console.print("[cyan]1. Online Order\n2. Offline Order[/cyan]")
        mode = input("Choose: ")

        if mode == "1":
                order_type = "ONLINE"

                cities = [
                    "delhi", "mumbai", "bangalore", "chennai", "kolkata",
                    "hyderabad", "ahmedabad", "pune", "surat", "jaipur",
                    "lucknow", "kanpur", "nagpur", "indore", "bhopal",
                    "patna", "varanasi", "agra", "amritsar", "kochi"
                ]

                console.print("[bold yellow]📍 Enter your city:[/bold yellow]")
                city = input().strip().lower()

                if city not in cities:
                    console.print("[red]❌ Delivery not available in your city[/red]")
                    return

                console.print("[green]✅ Delivery available[/green]")

                console.print("1. Home Delivery\n2. Self Pickup")
                d = input("Choose: ")

                if d == "1":
                    delivery_type = "HOME DELIVERY"
                else:
                    delivery_type = "SELF PICKUP"

        elif mode == "2":
                order_type = "OFFLINE"
                delivery_type = "DINE-IN"
                city = ""

        else:
            console.print("[red]Invalid choice[/red]")
            return
        while True:
            console.print("\n[bold yellow]1. Order Item\n2. Order Combo\n0. Finish[/bold yellow]")
            choice = input("Choice: ")

            if choice == "0":
                break

            if choice == "1":
                search = input("Search: ")

                results = self.search_item(search)

                table = Table(
                    title="[bold green]🔍 Search Results[/bold green]",
                    box=box.DOUBLE_EDGE,
                    show_lines=True
                )
                table.add_column("ID", style="bold cyan", justify="center")
                table.add_column("Name", style="bold yellow")
                table.add_column("Price", style="bold green", justify="center")

                for r in results:
                    table.add_row(
                        f"[cyan]{r['id']}[/cyan]",
                        f"[white]{r['name']}[/white]",
                        f"[green]₹{r['price']}[/green]"
                    )

                console.print(table)

                try:
                    item_id = int(input("Enter ID: "))
                    qty = int(input("Qty: "))
                except:
                    continue

                item = self.get_item_by_id(item_id)
                if not item:
                    continue

                if not self.update_inventory(item["name"], qty):
                    continue

                total += item["price"] * qty

                items.append({
                    "order_id": order_id,
                    "name": item["name"],
                    "qty": qty,
                    "price": item["price"]
                })
           
            elif choice == "2":
                combos = self.load_combos()

                console.print("[bold green]🍱 Available Combos[/bold green]")
                for c in combos:
                    console.print(
                        f"[cyan]{c['id']}[/cyan] - [yellow]{c['name']}[/yellow] [green]₹{c['price']}[/green]"
                    )

                try:
                    cid = int(input("Combo ID: "))
                    qty = int(input("Qty: "))
                except:
                    continue

                combo = next((c for c in combos if c["id"] == cid), None)
                if not combo:
                    continue

                total += combo["price"] * qty
                items.append({
                    "order_id": order_id,
                    "name": combo["name"],
                    "qty": qty,
                    "price": combo["price"]
                })

        if not items:
            console.print("[red]No items[/red]")
            return

        order = {
            "user": username,
            "order_id": order_id,
            "items": items,
            "total": total,
            "status": "Preparing",
            "delivery": delivery_type,
            "order_type": order_type,
            "city": city
        }

        data = self.load(self.order_file)
        data.append(order)
        self.save(self.order_file, data)

        
        pm = PaymentManager()
        bill, bills = pm.get_or_create_bill(username)
        bill.setdefault("order_ids",[]).append(order_id)
        bill["subtotal"] += total
        bill.setdefault("items", []).extend(items)
        bill["order_type"] = order_type
        bill["delivery_type"] = delivery_type
        bill["city"] = city
        pm.save(bills)

        console.print("[green]✅ Order Created[/green]")

    # ================= VIEW =================
    def view_orders(self, role="user"):
        data = self.load(self.order_file)

        username = input("Enter your name: ").strip().lower()
        user_orders = [o for o in data if o.get("user") == username]

        if not user_orders:
            console.print("[red]No orders found[/red]")
            return

        for o in user_orders:
            table = Table(
                title=f"[bold magenta]🧾 Order ID: {o['order_id']}[/bold magenta]",
                box=box.DOUBLE_EDGE,
                show_lines=True
            )
            table.add_column("Item", style="bold yellow", justify="center")
            table.add_column("Qty", style="bold cyan", justify="center")
            table.add_column("Price", style="bold green", justify="center")

            for item in o.get("items", []):
                table.add_row(
                    f"[white]{item['name']}[/white]",
                    f"[cyan]{item['qty']}[/cyan]",
                    f"[green]₹{item['price']}[/green]"
                )

            console.print(table)
            console.print(f"[bold blue]Status:[/bold blue] {o['status']}")
            console.print("[dim]" + "-" * 40 + "[/dim]")


            # ================= TRACK ORDER =================
    def track_order(self):
        data = self.load(self.order_file)

        username = input("Enter your name: ").strip().lower()
        order_id = int(input("Enter Order ID: "))

        for o in data:
            if o.get("user") == username and o.get("order_id") == order_id:

                console.print(Panel(
                    f"[bold cyan]📦 ORDER TRACKING[/bold cyan]\n\n"
                    f"🆔 Order ID : {o['order_id']}\n"
                    f"👤 User     : {o['user']}\n"
                    f"📍 Type     : {o['delivery']}\n\n"
                    f"[bold green]🚚 Status : {o['status']}[/bold green]",
                    border_style="cyan"
                ))
                return

        console.print("[red]❌ Order not found[/red]")

    # ================= UPDATE =================
    def update_order(self):
        try:
            data = self.load(self.order_file)

            username = input("Enter your name: ").strip().lower()

            user_orders = [o for o in data if o.get("user") == username]

            if not user_orders:
                console.print("[red]No orders found[/red]")
                return

            order = user_orders[-1]

            console.print(Panel(
                "[bold cyan]🔄 UPDATE ORDER[/bold cyan]\n\n"
                "1. Change Quantity\n"
                "2. Replace Item\n"
                "3. Add New Item",
                border_style="cyan"
            ))

            ch = input("Choice: ")

            # ================= CHANGE QTY =================
            if ch == "1":
                for i, item in enumerate(order["items"], start=1):
                    console.print(f"[cyan]{i}.[/cyan] {item['name']} x{item['qty']}")

                try:
                    idx = int(input("Select item: ")) - 1
                    new_qty = int(input("New Qty: "))
                except:
                    console.print("[red]Invalid input[/red]")
                    return

                old_item = order["items"][idx]
                old_total = old_item["qty"] * old_item["price"]

                order["items"][idx]["qty"] = new_qty
                new_total = new_qty * old_item["price"]

                order["total"] = order["total"] - old_total + new_total

            # ================= REPLACE ITEM =================
            elif ch == "2":
                for i, item in enumerate(order["items"], start=1):
                    console.print(f"[cyan]{i}.[/cyan] {item['name']} x{item['qty']}")

                try:
                    idx = int(input("Select item to replace: ")) - 1
                except:
                    console.print("[red]Invalid input[/red]")
                    return

                search = input("Search new item: ")
                results = self.search_item(search)

                table = Table(box=box.DOUBLE_EDGE, show_lines=True)
                table.add_column("ID", style="cyan")
                table.add_column("Name", style="yellow")
                table.add_column("Price", style="green")

                for r in results:
                    table.add_row(str(r["id"]), r["name"], f"₹{r['price']}")

                console.print(table)

                try:
                    new_id = int(input("Enter new item ID: "))
                    new_qty = int(input("Qty: "))
                except:
                    return

                new_item = self.get_item_by_id(new_id)
                if not new_item:
                    console.print("[red]Item not found[/red]")
                    return

                old_item = order["items"][idx]
                old_total = old_item["qty"] * old_item["price"]

                order["items"][idx] = {
                    "name": new_item["name"],
                    "qty": new_qty,
                    "price": new_item["price"]
                }

                new_total = new_item["price"] * new_qty
                order["total"] = order["total"] - old_total + new_total

            # ================= ADD NEW ITEM =================
            elif ch == "3":
                search = input("Search item: ")
                results = self.search_item(search)

                table = Table(box=box.DOUBLE_EDGE, show_lines=True)
                table.add_column("ID", style="cyan")
                table.add_column("Name", style="yellow")
                table.add_column("Price", style="green")

                for r in results:
                    table.add_row(str(r["id"]), r["name"], f"₹{r['price']}")

                console.print(table)

                try:
                    item_id = int(input("Enter ID: "))
                    qty = int(input("Qty: "))
                except:
                    return

                item = self.get_item_by_id(item_id)
                if not item:
                    return

                order["items"].append({
                    "name": item["name"],
                    "qty": qty,
                    "price": item["price"]
                })

                order["total"] += item["price"] * qty

            else:
                console.print("[red]Invalid choice[/red]")
                return

            # ================= BILL UPDATE FIX =================
            pm = PaymentManager()
            bills = pm.load()

            for b in bills:
                if b.get("user") == username and b.get("payment_status") == "Pending":

                    b["items"] = []

                    for item in order["items"]:
                        b["items"].append({
                            "name": item["name"],
                            "qty": item["qty"],
                            "price": item["price"]
                        })

                    b["subtotal"] = order["total"]

            pm.save(bills)
            self.save(self.order_file, data)

            console.print("[green]✅ Order Updated Successfully[/green]")

        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "update_order", e)
    # ================= CANCEL =================
    

    def cancel_order(self):
        username = input("Enter your name: ").strip().lower()
        data = self.load(self.order_file)

        user_orders = [
            o for o in data
            if o.get("user") == username and o.get("status") != "Cancelled"
        ]

        if not user_orders:
            console.print("[red]❌ No active orders found[/red]")
            return

        console.print("[bold yellow]📦 Your Orders:[/bold yellow]")

        for i, o in enumerate(user_orders, start=1):
            console.print(f"{i}. 🆔 {o['order_id']} | ₹{o['total']} | {o['status']}")

        try:
            ch = int(input("Select order to cancel: ")) - 1
            order = user_orders[ch]
        except:
            console.print("[red]Invalid choice[/red]")
            return

        order["status"] = "Cancelled"
        self.save(self.order_file, data)

        pm = PaymentManager()
        bills = pm.load()

        total_refund = 0

        for bill in bills:
            if bill.get("user") != username:
                continue

            refund = 0

            for item in order.get("items", []):
                for b_item in bill.get("items", [])[:]:
                    if (
                        b_item["name"] == item["name"] and
                        b_item["price"] == item["price"]
                    ):
                        if b_item["qty"] > item["qty"]:
                            b_item["qty"] -= item["qty"]
                        else:
                            bill["items"].remove(b_item)

                        refund += item["price"] * item["qty"]
                        total_refund += item["price"] * item["qty"]
                        break

            bill.setdefault("refund_details", []).append({
                "type": "order",
                "order_id": order.get("order_id"),
                "amount": refund
            })

            new_total = 0

            for item in bill.get("items", []):
                new_total += item["price"] * item["qty"]

            for tb in bill.get("table_booking", []):
                if tb.get("status") != "cancelled":
                    new_total += tb.get("price", 0)

            bill["subtotal"] = new_total

            if bill.get("payment_status") == "Paid" and refund > 0:
                bill["payment_status"] = "Refunded"

        pm.save(bills)

        console.print(Panel(
            f"[bold red]❌ Order Cancelled[/bold red]\n"
            f"🆔 Order ID: {order.get('order_id')}\n"
            f"💸 Refund: ₹{total_refund}",
            border_style="red"
        ))

    def pick_order(self):
        data = self.load(self.order_file)

        name = input("Enter your name: ").strip().lower()

        orders = [o for o in data if o.get("status") in ["Packed", "Picked", "Delivered"]]

        if not orders:
            console.print("[red]❌ No orders available[/red]")
            return

        console.print("[bold yellow]📦 Orders:[/bold yellow]")

        for i, o in enumerate(orders, start=1):
            status = o.get("status")

            if status == "Packed":
                console.print(f"{i}. 🆔 {o['order_id']} | ₹{o['total']} | [green]Ready to Pick[/green]")

            elif status == "Picked":
                console.print(f"{i}. 🆔 {o['order_id']} | ₹{o['total']} | [yellow]Already Picked[/yellow]")

            elif status == "Delivered":
                console.print(f"{i}. 🆔 {o['order_id']} | ₹{o['total']} | [red]Already Delivered[/red]")

        try:
            ch = int(input("Select order: ")) - 1
            order = orders[ch]
        except:
            console.print("[red]Invalid choice[/red]")
            return

        if order.get("status") == "Picked":
            console.print("[yellow]⚠️ Already Picked[/yellow]")
            return

        if order.get("status") == "Delivered":
            console.print("[red]❌ Already Delivered[/red]")
            return

        if order.get("status") != "Packed":
            console.print("[red]❌ Order not ready[/red]")
            return

        order["status"] = "Picked"
        order["delivery_boy"] = name

        self.save(self.order_file, data)

        console.print(Panel(
            f"[bold green]✅ Order Picked[/bold green]\n🆔 {order['order_id']}",
            border_style="green"
        ))
    def confirm_order(self):
        username = input("Enter your name: ").strip().lower()
        data = self.load(self.order_file)

        found = False

        for order in data:
            if order.get("order_type") == "OFFLINE":

                if order.get("status") == "Confirmed":
                    console.print(f"[yellow]⚠️ Already Confirmed: {order['order_id']}[/yellow]")
                    continue

                if order.get("status") != "Preparing":
                    continue

                console.print(f"🆔 Order ID: {order['order_id']}")

                confirm = input("Confirm this order? (y/n): ").lower()

                if confirm == "y":
                    order["status"] = "Confirmed"
                    found = True

                    console.print("[green]✅ Order Confirmed[/green]")
                    self.save(self.order_file, data)
                    return

        if not found:
            console.print("[red]❌ No order found[/red]")
    
    def pack_order(self):
        username = input("Enter your name: ").strip().lower()
        data = self.load(self.order_file)

        found = False

        for order in data:

        
            if order.get("status") == "Cancelled":
                continue

            if order.get("status") == "Delivered":
                console.print(f"[red]❌ Order {order['order_id']} already delivered[/red]")
                continue

            if order.get("status") == "Packed":
                console.print(f"[yellow]⚠️ Order {order['order_id']} already packed[/yellow]")
                continue

            if order.get("status") == "Preparing":
                console.print(f"[red]❌ Order {order['order_id']} not confirmed yet[/red]")
                continue

            if order.get("status") == "Confirmed":

                console.print(f"[cyan]📦 Pack Order ID: {order['order_id']}[/cyan]")

                choice = input("Pack this order? (y/n): ").lower()

                if choice == "y":
                    order["status"] = "Packed"

                    console.print(
                        f"[green]✅ Order {order['order_id']} packed successfully[/green]"
                    )

                    self.save(self.order_file, data)
                    return

                else:
                    console.print("[yellow]Skipped[/yellow]")
                    return

        console.print("[red]❌ No confirmed orders available[/red]")

    
    def view_earnings(self):
        import json

        file = "APP/DATABASE/orders.json"

        try:
            with open(file, "r") as f:
                orders = json.load(f)
        except:
            orders = []

        name = input("Enter your name: ").strip().lower()

        total = 0

        for o in orders:
            if (
                o.get("delivery_boy") == name and
                o.get("status") == "Delivered"
            ):
                total += int(o.get("total", 0) * 0.10)

        console.print(Panel(
            f"[bold green]💰 Total Earnings:[/bold green] ₹{total}",
            border_style="green"
        ))

        

    
    def assign_delivery(self):
        import json

        file = "APP/DATABASE/orders.json"

        try:
            with open(file, "r") as f:
                data = json.load(f)
        except:
            data = []

        name = input("Enter your name: ").strip().lower()
        try:
            order_id = int(input("Enter Order ID: "))
        except:
            console.print("[red]Invalid Order ID[/red]")
            return

        for o in data:

            if o.get("order_id") == order_id:

                if o.get("status") == "Delivered":
                    console.print("[red]❌ Already Delivered[/red]")
                    return

                if o.get("status") == "Out for Delivery":
                    console.print("[yellow]⚠️ Already Assigned[/yellow]")
                    return

                if o.get("status") != "Picked":
                    console.print("[red]❌ Order must be PICKED first[/red]")
                    return

                o["delivery_boy"] = name
                o["status"] = "Out for Delivery"

                with open(file, "w") as f:
                    json.dump(data, f, indent=4)

                console.print("[green]✅ Assigned Successfully[/green]")
                return

        console.print("[red]❌ Order not found[/red]")
    
    def mark_delivered(self):
        import json

        file = "APP/DATABASE/orders.json"

        try:
            with open(file, "r") as f:
                data = json.load(f)
        except:
            data = []

        try:
            order_id = int(input("Enter Order ID: "))
        except:
            console.print("[red]Invalid Order ID[/red]")
            return

        name = input("Enter your name: ").strip().lower()

        for o in data:

            if o.get("order_id") == order_id:

                if o.get("status") == "Delivered":
                    console.print("[yellow]⚠️ Already Delivered[/yellow]")
                    return

                if o.get("status") != "Out for Delivery":
                    console.print("[red]❌ Assign delivery first[/red]")
                    return

                o["status"] = "Delivered"
                o["delivery_boy"] = name

                with open(file, "w") as f:
                    json.dump(data, f, indent=4)

                console.print("[green]✅ Order Delivered[/green]")
                return

        console.print("[red]❌ Order not found[/red]")
            
    def search_order(self):
        import json

        file = "APP/DATABASE/orders.json"

        try:
            with open(file, "r") as f:
                orders = json.load(f)
        except:
            orders = []

        name = input("Enter your name: ").strip().lower()

        found = False

        for o in orders:
            customer = (
                o.get("customer_name") or
                o.get("name") or
                o.get("user") or ""
            ).lower()

            if name in customer:
                print(f"\n🧾 Order ID: {o.get('order_id')}")
                print("Status:", o.get("status"))
                print("-" * 40)
                found = True

        if not found:
            print("❌ No order found")

    
    def chef_workflow(self):
        data = self.load(self.order_file)

        chef_name = input("Enter Chef Name: ").strip().lower()
        username = input("Enter User Name: ").strip().lower()

        orders = [
            o for o in data
            if o.get("user") == username
            and o.get("status") not in ["Delivered", "Cancelled"]
        ]

        if not orders:
            console.print("[red]❌ No active orders found[/red]")
            return

        console.print("\n[bold yellow]📦 Orders:[/bold yellow]\n")

        for o in orders:
            console.print(
                f"\n🆔 {o['order_id']} | Status: {o['status']} | Type: {o.get('order_type')}"
            )

            
            for item in o.get("items", []):
                console.print(f"   • {item['name']} x{item['qty']}")

        
        try:
            oid = int(input("\nEnter Order ID: "))
        except:
            console.print("[red]❌ Invalid ID[/red]")
            return
        
        order = next(
            (o for o in data if o.get("order_id") == oid and o.get("user") == username),
            None
        )

        if not order:
            console.print("[red]❌ Order not found[/red]")
            return

        status = order.get("status")

        
        if status in ["Delivered", "Cancelled"]:
            console.print("[red]❌ Cannot process this order[/red]")
            return

        # ================= FLOW =================

        if status == "Preparing":
            console.print("\n1. 🔥 Start Cooking")
            ch = input("Choose: ")

            if ch == "1":
                order["status"] = "Cooking"
                order["chef"] = chef_name
                order["started_at"] = datetime.now().strftime("%d-%m-%Y %I:%M %p")

                console.print("[green]🔥 Cooking Started[/green]")

        elif status == "Cooking":
            console.print("\n1. ✅ Mark Ready (Packed)")
            ch = input("Choose: ")

            if ch == "1":
                order["status"] = "Packed"
                order["ready_at"] = datetime.now().strftime("%d-%m-%Y %I:%M %p")

                console.print("[green]✅ Order Ready[/green]")

        else:
            console.print("[yellow]⚠️ Order already processed[/yellow]")
            return

        self.save(self.order_file, data)

        console.print("[bold green]✔ Updated Successfully[/bold green]")

    

    def staff_workflow(self):
        data = self.load(self.order_file)

        staff_name = input("Enter Staff Name: ").strip().lower()
        username = input("Enter User Name: ").strip().lower()

        orders = [
            o for o in data
            if o.get("user") == username
            and o.get("status") not in ["Delivered", "Cancelled"]
        ]

        if not orders:
            console.print("[red]❌ No active orders[/red]")
            return

        console.print("\n[bold yellow]📦 Orders for Staff:[/bold yellow]\n")

        for o in orders:
            console.print(
                f"\n🆔 {o['order_id']} | Status: {o['status']} | Type: {o.get('order_type')}"
            )

            for item in o.get("items", []):
                console.print(f"   • {item['name']} x{item['qty']}")

        try:
            oid = int(input("\nEnter Order ID: "))
        except:
            console.print("[red]❌ Invalid ID[/red]")
            return

        order = next(
            (o for o in data if o.get("order_id") == oid and o.get("user") == username),
            None
        )

        if not order:
            console.print("[red]❌ Order not found[/red]")
            return

        status = order.get("status")

        if status in ["Delivered", "Cancelled"]:
            console.print("[red]❌ Cannot process this order[/red]")
            return

        # ================= FLOW =================

        if status == "Packed":
            console.print("\n1. 📦 Pick Order")
            ch = input("Choose: ")

            if ch == "1":
                order["status"] = "Picked"
                order["staff"] = staff_name
                order["picked_at"] = datetime.now().strftime("%d-%m-%Y %I:%M %p")

                console.print("[green]📦 Order Picked[/green]")

        elif status == "Picked":
            console.print("\n1. 🚚 Mark Delivered")
            ch = input("Choose: ")

            if ch == "1":
                order["status"] = "Delivered"
                order["delivered_at"] = datetime.now().strftime("%d-%m-%Y %I:%M %p")

                console.print("[green]🚚 Order Delivered[/green]")

        else:
            console.print("[yellow]⚠️ Order not ready for staff[/yellow]")
            return

        
        self.save(self.order_file, data)

        console.print("[bold green]✔ Updated Successfully[/bold green]")

        
# ================= MENU =================
def order_menu():
    om = OrderManager()

    while True:
        console.print(Panel(
            "[bold green]1. 🛒 Create Order[/bold green]\n"
            "[bold cyan]2. 📦 View Orders[/bold cyan]\n"
            "[bold magenta]3. 🔄 Update Order[/bold magenta]\n"
            "[bold red]4. ❌ Cancel Order[/bold red]\n"
            "[bold blue]5. 📦 Track Order[/bold blue]\n"
            "[bold blue]6. 🔙 Back[/bold blue]",
            border_style="green"
        ))

        ch = input("Choice: ")

        if ch == "1":
            om.create_order()
        elif ch == "2":
            om.view_orders()
        elif ch == "3":
            om.update_order()
        elif ch == "4":
            om.cancel_order()
        elif ch == "5":
            om.track_order()
        elif ch == "6":
            break