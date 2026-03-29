import json
import random
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from APP.LOGS.error_handler import error_handler
from APP.BILLING.payment_menu import PaymentManager

console = Console(force_terminal=True, color_system="truecolor")


class BookingManager:

    def __init__(self):
        self.file = "APP/DATABASE/booking.json"

        self.total_tables = 10

        
        self.slots = {
            "1": ("🌅 Morning", "9AM - 12PM", "🍳 Breakfast"),
            "2": ("🌞 Afternoon", "12PM - 3PM", "🍛 Lunch"),
            "3": ("🌆 Evening", "3PM - 6PM", "☕ Snacks"),
            "4": ("🌙 Night", "6PM - 9PM", "🍽️ Dinner")
        }

        self.table_capacity = {
            1: 2,
            2: 4,
            3: 6,
            4: 4,
            5: 2,
            6: 6,
            7: 4,
            8: 2,
            9: 6,
            10: 4
        }

        self.table_type = {
            1: "🟢 Small Table",
            2: "🔵 Family Table",
            3: "🟣 VIP Table",
            4: "🔵 Family Table",
            5: "🟢 Small Table",
            6: "🟣 VIP Table",
            7: "🔵 Family Table",
            8: "🟢 Small Table",
            9: "🟣 VIP Table",
            10: "🔵 Family Table"
        }

       
        self.stalls = [
            {"id": 1, "name": "🍔 Fast Food Corner", "time": "3PM - 10PM", "price": 150},
            {"id": 2, "name": "🍛 Indian Kitchen", "time": "12PM - 11PM", "price": 200},
            {"id": 3, "name": "☕ Cafe & Snacks", "time": "9AM - 9PM", "price": 120},
            {"id": 4, "name": "🍕 Italian Hub", "time": "1PM - 11PM", "price": 250}
        ]

        self.colors = {
            "available": "[bold green]✅ Available[/bold green]",
            "booked": "[bold red]❌ Booked[/bold red]",
            "title": "[bold cyan]",
            "warning": "[bold yellow]",
            "error": "[bold red]"
        }

    # ================= SLOT VALIDATION =================
    def is_valid_slot(self, date_str, slot):
        now = datetime.now()
        try:
            booking_date = datetime.strptime(date_str, "%d-%m-%Y")
        except:
            return False

        if booking_date.date() == now.date():
            hour = now.hour
            if slot == "Morning" and hour >= 12:
                return False
            if slot == "Afternoon" and hour >= 15:
                return False
            if slot == "Evening" and hour >= 18:
                return False
            if slot == "Night" and hour >= 21:
                return False

        return True

    # ================= CLEAN =================
    def clean_expired(self, bookings):
        now = datetime.now()
        valid = []
        for b in bookings:
            try:
                booking_time = datetime.strptime(b.get("date"), "%d-%m-%Y")
                if booking_time >= now:
                    valid.append(b)
            except:
                valid.append(b)
        return valid

    def load(self):
        try:
            with open(self.file, "r") as f:
                return json.load(f)
        except:
            return []

    def save(self, data):
        try:
            with open(self.file, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "save", e)

    # ================= SHOW TABLE STATUS =================

    def show_tables(self, data, selected_date):

        table = Table(
            title=f"📅 TABLE STATUS ({selected_date})",
            box=box.DOUBLE_EDGE,
            show_lines=True
        )

        table.add_column("Table", style="bold yellow", justify="center")

        for s in self.slots.values():
            table.add_column(
                f"[bold cyan]{s[0]}[/bold cyan]\n[green]({s[2]})[/green]",
                justify="center"
            )

        for t in range(1, self.total_tables + 1):
            row = [str(t)]

            for slot_name, _, _ in self.slots.values():
                booked = any(
                    b.get("table") == t and
                    b.get("slot") == slot_name and
                    b.get("date") == selected_date and
                    b.get("status", "Active") == "Active"
                    for b in data
                )

                if booked:
                    row.append("[bold red]❌ Booked[/bold red]")
                else:
                    row.append("[bold green]✅ Available[/bold green]")

            table.add_row(*row)

        console.print(Panel(table, border_style="cyan"))

        # ================= 🪑 SEATING INFO =================
        seat_table = Table(
            title="🪑 TABLE SEATING INFO",
            box=box.DOUBLE_EDGE,
            show_lines=True
        )

        seat_table.add_column("Table", style="bold yellow", justify="center")
        seat_table.add_column("Chairs Available", style="green", justify="center")
        seat_table.add_column("Type", style="magenta", justify="center")

        for t in range(1, self.total_tables + 1):
            chairs = self.table_capacity[t]
            ttype = self.table_type[t]

            seat_table.add_row(
                str(t),
                f"{chairs} Chairs",
                ttype
            )

        console.print(Panel(seat_table, border_style="magenta"))

        # ================= 📌 RULES =================
        console.print(Panel(
            "[bold yellow]📌 BOOKING RULES[/bold yellow]\n\n"
            "[green]🟢 Normal Booking  → Max 4 People Allowed[/green]\n"
            "[magenta]🟣 VIP Booking     → Max 6 People Allowed[/magenta]\n\n"
            "[red]⚠️ Note:[/red]\n"
            "• Table capacity exceed nahi kar sakte\n"
            "• Agar 2-chair table hai → max 2 hi book hoga",
            border_style="yellow"
        ))

        # ================= NOTE =================
        console.print(Panel(
            "[bold cyan]ℹ️ STATUS GUIDE[/bold cyan]\n"
            "• ❌ Booked = Already reserved\n"
            "• ✅ Available = You can book\n"
            "• Multi-day booking supported\n"
            "• If one day booked → same slot blocked for that day",
            border_style="cyan"
        ))

        # ================= USER BOOKINGS =================
        user = input("Enter your name to check your bookings (or press Enter to skip): ").strip().lower()

        if user:
            user_bookings = [
                b for b in data
                if b.get("user") == user and b.get("status") == "Active"
            ]

            if user_bookings:
                user_table = Table(
                    title="📅 YOUR ACTIVE BOOKINGS",
                    box=box.DOUBLE_EDGE,
                    show_lines=True
                )

                user_table.add_column("ID", style="cyan")
                user_table.add_column("Table", style="yellow")
                user_table.add_column("Slot", style="green")
                user_table.add_column("Date", style="magenta")

                for b in user_bookings:
                    user_table.add_row(
                        str(b.get("id")),
                        str(b.get("table")),
                        b.get("slot"),
                        b.get("date")
                    )

                console.print(Panel(user_table, border_style="green"))
            else:
                console.print("[red]❌ No Active Booking Found[/red]")
    # ================= BOOK =================
    
    def book_table(self):
        try:
            data = self.clean_expired(self.load())
            self.save(data)

            console.print(Panel(
                "[bold green]📅 TABLE BOOKING SYSTEM[/bold green]\n\n"
                "[cyan]✔ Max 10 days advance booking[/cyan]\n"
                "[yellow]✔ Slot system available[/yellow]",
                border_style="green"
            ))

            console.print("[bold yellow]👤 Enter Name:[/bold yellow]")
            name = input().strip().lower()

            console.print("[bold green]📱 Enter Mobile Number:[/bold green]")
            mobile = input().strip()

            if not mobile.isdigit() or len(mobile) != 10:
                console.print("[red]❌ Invalid Mobile Number[/red]")
                return

            console.print("[bold cyan]📅 Enter Date (DD-MM-YYYY):[/bold cyan]")
            booking_date = input()

            try:
                selected = datetime.strptime(booking_date, "%d-%m-%Y").date()
            except:
                console.print("[red]Invalid date[/red]")
                return

            today = datetime.now().date()
            if selected < today or selected > today + timedelta(days=10):
                console.print("[red]Date out of range[/red]")
                return

            try:
                days = int(input("How many days to book (max 10): "))
                if days < 1 or days > 10:
                    console.print("[red]❌ Max 10 days allowed[/red]")
                    return
            except:
                console.print("[red]Invalid input[/red]")
                return


            self.show_tables(data, booking_date)

            console.print("[green]✅ Available[/green]  |  [red]❌ Booked[/red]")

           
            console.print(Panel(
                "[bold yellow]📌 BOOKING RULES[/bold yellow]\n\n"
                "[green]🟢 Normal → Max 4 People[/green]\n"
                "[magenta]🟣 VIP → Max 6 People[/magenta]",
                border_style="yellow"
            ))

            console.print("[bold cyan]1. 🟢 Normal (₹100)\n2. 🟣 VIP (₹200)[/bold cyan]")
            t_choice = input("Enter choice: ")

            if t_choice == "1":
                price = 100
                max_people = 4
                type_name = "Normal"
            elif t_choice == "2":
                price = 200
                max_people = 6
                type_name = "VIP"
            else:
                return

            try:
                table_no = int(input("Enter Table No (1-10): "))
            except:
                console.print("[red]Invalid table number[/red]")
                return

            if table_no not in self.table_capacity:
                console.print("[red]Invalid table[/red]")
                return

            try:
                people = int(input("👥 Enter number of persons: "))
            except:
                console.print("[red]Invalid input[/red]")
                return

            if people > self.table_capacity[table_no] or people > max_people:
                console.print("[red]❌ Exceeds table capacity / booking limit[/red]")
                return

            console.print("\n[bold cyan]Select Slot:[/bold cyan]")
            for k, v in self.slots.items():
                console.print(f"[cyan]{k}[/cyan]. {v[0]} ({v[1]})")

            ch = input("Choice: ")

            if ch not in self.slots:
                console.print("[red]Invalid slot[/red]")
                return

            slot = self.slots[ch][0]

            stall_table = Table(title="🍴 AVAILABLE FOOD STALLS", box=box.DOUBLE_EDGE)
            stall_table.add_column("ID", style="cyan")
            stall_table.add_column("Stall Name", style="yellow")
            stall_table.add_column("Timing", style="green")
            stall_table.add_column("Avg Price", style="magenta")

            for s in self.stalls:
                stall_table.add_row(str(s["id"]), s["name"], s["time"], f"₹{s['price']}")

            console.print(Panel(stall_table, border_style="cyan"))

            try:
                stall_choice = int(input("Select Stall (1-4): "))
                stall = self.stalls[stall_choice - 1]
            except:
                console.print("[red]Invalid stall[/red]")
                return

            total_price = 0
            bookings_added = []

            for i in range(days):
                next_date = (datetime.strptime(booking_date, "%d-%m-%Y") + timedelta(days=i)).strftime("%d-%m-%Y")

                if not self.is_valid_slot(next_date, slot):
                    console.print(f"[red]❌ Slot passed for {next_date}[/red]")
                    return

                for b in data:
                    if b.get("table_id") == f"T{table_no}" and b.get("slot") == slot and b.get("date") == next_date:
                        console.print(f"[red]❌ Already booked on {next_date}[/red]")
                        return

                booking = {
                    "booking_id": random.randint(1000, 9999),
                    "name": name,
                    "mobile": mobile,
                    "guests": people,
                    "table_id": f"T{table_no}",
                    "slot": slot,
                    "date": next_date,
                    "datetime": f"{next_date} ({slot})",
                    "price": price,
                    "status": "Confirmed"
                }

                data.append(booking)
                bookings_added.append(booking)
                total_price += price

            self.save(data)

            try:
                pm = PaymentManager()
                bill, bills = pm.get_or_create_bill(name)

                for b in bookings_added:
                    bill.setdefault("table_booking", []).append({
                        "id": b["booking_id"],
                        "table": b["table_id"],
                        "slot": b["slot"],
                        "date": b["date"],
                        "price": b["price"],
                        "status": "Confirmed"
                    })

                bill["subtotal"] = bill.get("subtotal", 0) + total_price
                pm.save(bills)

            except Exception as e:
                console.print(f"[red]⚠️ Billing Error: {e}[/red]")

            console.print(Panel(
                f"[bold green]✅ BOOKING CONFIRMED[/bold green]\n\n"
                f"[cyan]Name      :[/cyan] {name}\n"
                f"[yellow]Table     :[/yellow] T{table_no} ({self.table_capacity[table_no]} Chairs)\n"
                f"[magenta]Type      :[/magenta] {type_name}\n"
                f"[green]Slot      :[/green] {slot}\n"
                f"[blue]Stall     :[/blue] {stall['name']}\n"
                f"[cyan]Days      :[/cyan] {days}\n"
                f"[bold yellow]Total ₹   :[/bold yellow] {total_price}",
                border_style="green"
            ))

        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "book_table", e)
    # ================= VIEW =================
    def view_booking(self):
        data = self.load()

        console.print("[bold yellow]📱 Enter Mobile Number:[/bold yellow]")
        mobile = input().strip()

        user_data = [
            b for b in data
            if b.get("mobile") == mobile
        ]

        if not user_data:
            console.print("[bold red]❌ No Booking Found[/bold red]")
            return

        try:
            user_data = sorted(
                user_data,
                key=lambda x: datetime.strptime(x.get("date"), "%d-%m-%Y")
            )
        except:
            pass

        table = Table(title="📋 YOUR BOOKINGS", box=box.DOUBLE_EDGE, show_lines=True)

        table.add_column("Booking ID", style="cyan", justify="center")
        table.add_column("Name", style="yellow", justify="center")
        table.add_column("Mobile", style="green", justify="center")
        table.add_column("Date", style="magenta", justify="center")
        table.add_column("Slot", style="blue", justify="center")
        table.add_column("Table", style="cyan", justify="center")
        table.add_column("Price", style="green", justify="center")
        table.add_column("Status", style="white", justify="center")
        table.add_column("Payment", style="bold green", justify="center")

        total_amount = 0

        for b in user_data:
            table.add_row(
                str(b.get("booking_id")),
                b.get("name"), 
                b.get("mobile"),
                b.get("date"),
                b.get("slot"),
                b.get("table_id"),      
                f"₹{b.get('price', 0)}",
                b.get("status", "Confirmed"),
                b.get("payment_status", "Pending")
            )

            total_amount += b.get("price", 0)
            pending_count = 0
            paid_count = 0

            for b in user_data:
                if b.get("payment_status") == "Paid":
                    paid_count += 1
                else:
                    pending_count += 1


        console.print(Panel(table, border_style="green"))

        console.print(Panel(
            f"[bold cyan]📊 SUMMARY[/bold cyan]\n\n"
            f"[yellow]Total Bookings:[/yellow] {len(user_data)}\n"
            f"[green]Total Amount:[/green] ₹{total_amount}\n\n"
            f"[red]Pending Payments:[/red] {pending_count}\n"
            f"[green]Paid Payments:[/green] {paid_count}",
            border_style="cyan"
        ))
    # ================= CANCEL =================
    

    def cancel_booking(self):
        try:
            data = self.load()

            console.print("[bold yellow]📱 Enter Mobile Number:[/bold yellow]")
            mobile = input().strip()

            user_bookings = [
                b for b in data
                if b.get("mobile") == mobile and b.get("status") == "Active"
            ]

            if not user_bookings:
                console.print("[red]❌ No Active Booking Found[/red]")
                return

            table = Table(title="📋 YOUR BOOKINGS", box=box.DOUBLE_EDGE, show_lines=True)
            table.add_column("ID", style="cyan", justify="center")
            table.add_column("Table", style="yellow", justify="center")
            table.add_column("Slot", style="green", justify="center")
            table.add_column("Date", style="magenta", justify="center")
            table.add_column("Price", style="green", justify="center")
            table.add_column("Status", style="white", justify="center")

            for b in user_bookings:
                table.add_row(
                    str(b.get("id")),
                    f"T{b.get('table')}",
                    b.get("slot"),
                    b.get("date"),
                    f"₹{b.get('price', 0)}",
                    b.get("status")
                )

            console.print(Panel(table, border_style="cyan"))

            try:
                cancel_id = int(input("\nEnter Booking ID to cancel: "))
            except:
                console.print("[red]❌ Invalid Booking ID[/red]")
                return

            found = False
            refund = 0

            for b in data:
                if b.get("id") == cancel_id and b.get("mobile") == mobile:
                    if b.get("status") != "Active":
                        console.print("[yellow]⚠️ Already Cancelled[/yellow]")
                        return

                    b["status"] = "Cancelled"
                    refund = b.get("price", 0)
                    found = True
                    break

            if not found:
                console.print("[red]❌ Booking not found[/red]")
                return

            self.save(data)


            console.print(Panel(
                f"[bold green]✅ BOOKING CANCELLED[/bold green]\n\n"
                f"[cyan]Booking ID:[/cyan] {cancel_id}\n"
                f"[green]Refund Amount:[/green] ₹{refund}",
                border_style="green"
            ))

        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "cancel_booking", e)
def booking_menu():
    bm = BookingManager()

    while True:
        console.print(Panel(
            "[bold blue]1. 📅 Book Table[/bold blue]\n"
            "[bold cyan]2. 📋 View Booking[/bold cyan]\n"
            "[bold yellow]3. ❌ Cancel Booking[/bold yellow]\n"
            "[bold red]4. 🔙 Back[/bold red]",
            border_style="blue"
        ))

        ch = input("Choice: ")

        if ch == "1":
            bm.book_table()
        elif ch == "2":
            bm.view_booking()
        elif ch == "3":
            bm.cancel_booking()
        elif ch == "4":
            break





