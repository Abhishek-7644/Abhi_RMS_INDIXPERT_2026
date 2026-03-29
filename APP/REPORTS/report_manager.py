import json
from collections import Counter
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from APP.LOGS.error_handler import error_handler

console = Console(force_terminal=True, color_system="truecolor")


class ReportManager:
    def __init__(self):
        self.order_file = "APP/DATABASE/orders.json"
        self.bill_file = "APP/DATABASE/bill.json"
        self.booking_file = "APP/DATABASE/booking.json"

    # ================= LOAD =================
    def load(self):
        try:
            with open(self.order_file, "r") as f:
                return json.load(f)
        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "load", e)
            return []

    def load_bills(self):
        try:
            with open(self.bill_file, "r") as f:
                return json.load(f)
        except:
            return []

    def load_bookings(self):
        try:
            with open(self.booking_file, "r") as f:
                return json.load(f)
        except:
            return []

    # ================= SALES REPORT =================
    def sales_report(self):
        try:
            data = self.load()

            if not data:
                console.print("[red]No orders found![/red]")
                return

            total_orders = len(data)

            bills = self.load_bills()
            total_revenue = sum(
                b.get("final_total", b.get("total", 0))
                for b in bills
                if b.get("payment_status") == "Paid"
            )

            item_counter = Counter()
            for order in data:
                for item in order.get("items", []):
                    item_counter[item["name"]] += item["qty"]

            most_sold = "N/A"
            if item_counter:
                most_sold = item_counter.most_common(1)[0][0]

            table = Table(title="📊 SALES SUMMARY", box=box.DOUBLE_EDGE)
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")

            table.add_row("Total Orders", str(total_orders))
            table.add_row("Total Revenue", f"₹{round(total_revenue, 2)}")
            table.add_row("Most Sold Item", most_sold)

            console.print(Panel(table, border_style="green"))

        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "sales_report", e)

    # ================= ORDER REPORT =================
    def order_report(self):
        try:
            data = self.load()

            if not data:
                console.print("[red]No orders found![/red]")
                return

            table = Table(title="📦 ORDER REPORT", box=box.DOUBLE_EDGE)
            table.add_column("Order ID", style="yellow")
            table.add_column("User", style="cyan")
            table.add_column("Total", style="green")
            table.add_column("Status", style="magenta")

            for order in data:
                table.add_row(
                    str(order.get("order_id")),
                    order.get("user"),
                    f"₹{order.get('total', 0)}",
                    order.get("status")
                )

            console.print(Panel(table, border_style="cyan"))

        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "order_report", e)

    # ================= BOOKING REPORT =================
    def table_booking_report(self):
        try:
            bookings = self.load_bookings()

            if not bookings:
                console.print("[red]No bookings found![/red]")
                return

            total_bookings = len(bookings)
            total_revenue = sum(b.get("price", 0) for b in bookings)

            table = Table(title="📅 BOOKING REPORT", box=box.DOUBLE_EDGE)
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")

            table.add_row("Total Bookings", str(total_bookings))
            table.add_row("Total Revenue", f"₹{total_revenue}")

            console.print(Panel(table, border_style="magenta"))

        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "booking_report", e)

    # ================= DAILY REPORT =================
    def daily_report(self):
        try:
            today = datetime.now().strftime("%d-%m-%Y")
            bills = self.load_bills()

            today_sales = [
                b for b in bills
                if b.get("created_at", "").startswith(today)
                and b.get("payment_status") == "Paid"
            ]

            total = sum(b.get("final_total", 0) for b in today_sales)

            console.print(Panel(
                f"[bold green]📅 TODAY'S REPORT ({today})[/bold green]\n\n"
                f"[cyan]Total Orders:[/cyan] {len(today_sales)}\n"
                f"[green]Revenue:[/green] ₹{total}",
                border_style="green"
            ))

        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "daily_report", e)

    # ================= TOP ITEMS =================
    def top_items(self):
        try:
            data = self.load()

            counter = Counter()

            for order in data:
                for item in order.get("items", []):
                    counter[item["name"]] += item["qty"]

            table = Table(title="🏆 TOP 5 ITEMS", box=box.ROUNDED)
            table.add_column("Item", style="cyan")
            table.add_column("Sold Qty", style="green")

            for item, qty in counter.most_common(5):
                table.add_row(item, str(qty))

            console.print(Panel(table, border_style="yellow"))

        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "top_items", e)

    # ================= ORDER STATUS =================
    def status_summary(self):
        try:
            data = self.load()
            counter = Counter(o.get("status") for o in data)

            table = Table(title="📊 ORDER STATUS", box=box.SIMPLE)
            table.add_column("Status", style="magenta")
            table.add_column("Count", style="green")

            for k, v in counter.items():
                table.add_row(k, str(v))

            console.print(Panel(table, border_style="cyan"))

        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "status_summary", e)

    # ================= PAYMENT REPORT =================
    def payment_report(self):
        try:
            bills = self.load_bills()
            counter = Counter(b.get("payment_method") for b in bills)

            table = Table(title="💳 PAYMENT METHODS", box=box.ROUNDED)
            table.add_column("Method", style="cyan")
            table.add_column("Count", style="green")

            for k, v in counter.items():
                table.add_row(str(k), str(v))

            console.print(Panel(table, border_style="magenta"))

        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "payment_report", e)

    # ================= FULL DASHBOARD =================
    def full_dashboard(self):
        console.print(Panel("[bold yellow]🚀 FULL BUSINESS DASHBOARD[/bold yellow]", border_style="yellow"))

        self.sales_report()
        self.daily_report()
        self.top_items()
        self.status_summary()
        self.payment_report()
        self.table_booking_report()


# ================= MENU =================
def report_menu():
    report = ReportManager()

    while True:
        try:
            console.print(Panel(
                "[bold blue]📊 REPORT MENU[/bold blue]\n\n"
                "[bold cyan]1.] Sales Report [bold cyan]\n"
                "[bold green]2. Order Report [bold green]\n"
                "[bold magenta]3. Booking Report [bold magenta]\n"
                "[bold yellow]4. Daily Report [bold yellow]\n"
                "[bold blue]5. Top Items [bold blue]\n"
                "[bold white]6. Order Status [bold white]\n"
                "[bold cyan]7. Payment Report [bold cyan]\n"
                "[bold green]8. Full Dashboard [bold green]\n"
                "[bold red]9. Back [bold red]",
                border_style="blue"
            ))

            console.print("[bold yellow]Enter choice:[/bold yellow]", end=" ")
            choice = input()
            

            if choice == "1":
                report.sales_report()
            elif choice == "2":
                report.order_report()
            elif choice == "3":
                report.table_booking_report()
            elif choice == "4":
                report.daily_report()
            elif choice == "5":
                report.top_items()
            elif choice == "6":
                report.status_summary()
            elif choice == "7":
                report.payment_report()
            elif choice == "8":
                report.full_dashboard()
            elif choice == "9":
                break
            else:
                console.print("[red]Invalid choice![/red]")

        except Exception as e:
            error_handler.log_exception("ReportMenu", "menu_loop", e)
            console.print("[red]Menu Error![/red]")

