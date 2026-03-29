import json
import getpass
import re
import random
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from APP.LOGS.error_handler import error_handler

console: Console = Console(force_terminal=True, color_system="truecolor")


class PaymentManager:

    def __init__(self):
        self.file = "APP/DATABASE/bill.json"

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

    # ================= GENERATE BILL ID =================
    def generate_bill_id(self, data):
        existing = [b.get("bill_id") for b in data if b.get("bill_id")]
        while True:
            bid = random.randint(1000, 9999)
            if bid not in existing:
                return bid

    # ================= GET / CREATE BILL =================
    def get_or_create_bill(self, username):
        data = self.load()
        username = username.strip().lower()

        for b in data:
            if b.get("user") == username and b.get("payment_status") == "Pending":
                return b, data

        new_bill = {
            "bill_id": self.generate_bill_id(data),
            "user": username,
            "mobile": "",
            "gst_number": "22AAAAA0000A1Z5",
            "created_at": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
            "subtotal": 0,
            "payment_status": "Pending",
            "items": [],
            "table_booking": []
        }

        data.append(new_bill)
        self.save(data)
        return new_bill, data

    # ================= CALCULATION =================
    def calculate(self, bill):
        subtotal = bill.get("subtotal", 0)

        discount = 0
        if subtotal > 500:
            discount = int(subtotal * 0.10)
            subtotal -= discount

        gst = round(subtotal * 0.18, 2)

        extra = 0
        if bill.get("fast_delivery"):
            extra += int(subtotal * 0.05)
        if bill.get("night"):
            extra += int(subtotal * 0.05)

        final_total = subtotal + gst + extra

        return subtotal, discount, gst, extra, final_total

    # ================= VIEW =================
    def view(self):
        try:
            data = self.load()

            if not data:
                console.print("[bold red]❌ No Bills Found[/bold red]")
                return

            username = input("Enter your name: ").strip().lower()
            found = False

            for bill in data:
                if bill.get("user","").strip().lower() != username:
                    continue

                found = True

                if not bill.get("mobile"):
                    while True:
                        mobile = input("Enter Mobile Number (+91XXXXXXXXXX): ").strip()
                        if mobile.startswith("+91") and mobile[3:].isdigit() and len(mobile) == 13:
                            bill["mobile"] = mobile
                            break
                        else:
                            console.print("[red]❌ Invalid Mobile[/red]")

                subtotal, discount, gst, extra, final_total = self.calculate(bill)

                content = f"""
[bold cyan]🧾 BILL RECEIPT[/bold cyan]

[green]🆔 Bill ID     :[/green] {bill.get('bill_id')}
[green]👤 Customer    :[/green] {bill.get('user')}
[green]📱 Mobile      :[/green] {bill.get('mobile')}
[green]🆔 GST No      :[/green] {bill.get('gst_number')}
[green]🕒 Date & Time :[/green] {bill.get('created_at')}
"""

               # ================= ORDERS SHOW =================
                if bill.get("items"):
                    content += "\n[bold yellow]🍽️ Orders:[/bold yellow]\n\n"

                    for item in bill["items"]:
                        content += (
                            f"• Order ID: {item.get('order_id')} | "
                            f"{item['name']} x{item['qty']} = ₹{item['price']*item['qty']}\n"
                        )
                else:
                    content += "\n[red]No Order Items[/red]\n"

                # ================= DELIVERY INFO =================
                if bill.get("order_type") == "ONLINE":
                    content += "\n[bold cyan]🚚 Delivery Details:[/bold cyan]\n"
                    content += f"• Type: {bill.get('delivery_type')}\n"
                    content += f"• City: {bill.get('city')}\n"

                if bill.get("table_booking"):
                    content += "\n[bold cyan]📅 Table Booking:[/bold cyan]\n"

                    grouped = {}

                    for tb in bill["table_booking"]:
                        if tb.get("status", "").lower() == "cancelled":
                            continue

                        bid = tb.get("id")

                        if bid not in grouped:
                            grouped[bid] = {
                                "table": tb.get("table"),
                                "slot": tb.get("slot"),
                                "dates": [],
                                "price": 0
                            }

                        grouped[bid]["dates"].append(tb.get("date"))
                        grouped[bid]["price"] += tb.get("price", 0)

                    for bid, g in grouped.items():
                        dates = ", ".join(g["dates"])

                        content += (
                            f"• ID: {bid} | "
                            f"Table {g['table']} | "
                            f"{g['slot']} | "
                            f"Dates: {dates} "
                            f"(₹{g['price']})\n"
                        )

                    if bill.get("refund_details"):
                        content += "\n[bold red]💸 Refund Details:[/bold red]\n"

                        for r in bill["refund_details"]:
                            if r.get("type") == "order":

                                    content += (
                                        f"• Order ID: {r.get('order_id')} "
                                        f"( -₹{r.get('amount')} )\n"
                                    )
                            else:
                                    content += (
                                        f"• Table {r.get('table')} | "
                                        f"{r.get('slot')} | "
                                        f"{r.get('date')} "
                                        f"( -₹{r.get('amount')} )\n"
                                    )


                        # ================= 🧮 CALCULATION BREAKDOWN =================

                original_total = bill.get("subtotal", 0)

                content += "\n[bold cyan]🧮 Calculation:[/bold cyan]\n"

                
                content += f"• Total Items Price: ₹{original_total}\n"

                if discount:
                    after_discount = original_total - discount
                    content += f"• Discount Applied: -₹{discount}\n"
                    content += f"• After Discount: ₹{after_discount}\n"
                else:
                    after_discount = original_total

                content += f"• GST (18%): ₹{gst}\n"

                if extra:
                    content += f"• Extra Charges: ₹{extra}\n"

                content += f"\n[bold green]💰 Final Payable:[/bold green] ₹{final_total}\n"
                content += f"[white]Status:[/white] {bill.get('payment_status')}"

                console.print(Panel(content, border_style="cyan"))

            if not found:
                console.print("[red]❌ No Bills Found[/red]")

            self.save(data)

        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "view", e)

    # ================= PAY =================
    def pay(self):
        try:
            data = self.load()
            bill_id = int(input("Enter Bill ID: "))

            for bill in data:
                if bill.get("bill_id") == bill_id:

                    if bill.get("payment_status") == "Paid":
                        console.print("[yellow]⚠️ Already Paid[/yellow]")
                        return

                    console.print(Panel(
                        "[bold green]💳 Payment Options[/bold green]\n\n"
                        "1. UPI\n2. CASH\n3. CARD",
                        border_style="green"
                    ))

                    method = input("Choose: ")

                    # ================= UPI =================
                    if method == "1":
                        console.print("1. QR\n2. UPI ID\n3. Mobile Number")
                        m = input("Choose: ")

                        if m == "1":
                            pin = getpass.getpass("Enter 4 digit PIN: ")
                            if not pin.isdigit() or len(pin) != 4:
                                console.print("[red]Invalid PIN[/red]")
                                return
                            bill["payment_method"] = "QR"

                        elif m == "2":
                            upi = input("Enter UPI: ")
                            if not re.fullmatch(r"[a-zA-Z0-9.\-_]+@[a-zA-Z]+", upi):
                                console.print("[red]Invalid UPI[/red]")
                                return
                            bill["payment_method"] = "UPI"
                            bill["upi_id"] = upi

                        # 🔥 NEW MOBILE OPTION (10 DIGIT)
                        elif m == "3":
                                mobile = input("Enter UPI Mobile Number (10 digit): ").strip()

                                if mobile.isdigit() and len(mobile) == 10:

                                    # 🔥 PIN ADD
                                    pin = getpass.getpass("Enter 4 digit PIN: ")
                                    if not pin.isdigit() or len(pin) != 4:
                                        console.print("[red]❌ Invalid PIN[/red]")
                                        return

                                    bill["payment_method"] = "UPI-Mobile"
                                    bill["upi_mobile"] = mobile

    

                                else:
                                    console.print("[red]❌ Invalid Mobile (Enter 10 digit)[/red]")
                                    return

                    # ================= CASH =================
                    elif method == "2":
                        bill["payment_method"] = "CASH"

                    # ================= CARD =================
                    elif method == "3":
                        card = getpass.getpass("Enter 14 digit card: ")
                        if not (card.isdigit() and len(card) == 14):
                            console.print("[red]Invalid Card[/red]")
                            return

                        cvv = getpass.getpass("Enter CVV (3 digit): ")
                        if not (cvv.isdigit() and len(cvv) == 3):
                            console.print("[red]Invalid CVV[/red]")
                            return

                        bill["payment_method"] = "CARD"
                        bill["card_last4"] = card[-4:] 

                    else:
                        return

                    # ================= FINAL CALCULATION =================
                    subtotal, discount, gst, extra, final_total = self.calculate(bill)

                    bill["payment_status"] = "Paid"
                    bill["final_total"] = final_total
                    bill["paid_at"] = datetime.now().strftime("%d-%m-%Y %I:%M %p")

                    self.save(data)

                    console.print(Panel(
                        f"[bold green]✅ PAYMENT SUCCESSFUL[/bold green]\n\n💰 ₹{final_total}",
                        border_style="green"
                    ))
                    return

            console.print("[red]Bill not found[/red]")

        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "pay", e)
    # ================= HISTORY =================
    def payment_history(self):
        try:
            data = self.load()
            username = input("Enter your name: ").strip().lower()

            bills = [b for b in data if b.get("user") == username and b.get("payment_status") == "Paid"]

            if not bills:
                console.print("[red]❌ No History[/red]")
                return

            for b in bills:
                console.print(Panel(
                    f"[cyan]Bill ID:[/cyan] {b['bill_id']}\n"
                    f"[green]Amount:[/green] ₹{b.get('final_total')}\n"
                    f"[yellow]Method:[/yellow] {b.get('payment_method')}\n"
                    f"[magenta]Paid At:[/magenta] {b.get('paid_at')}",
                    border_style="cyan"
                ))

        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "payment_history", e)

    # ================= DELETE =================
    def delete(self):
        try:
            data = self.load()
            bill_id = int(input("Enter Bill ID: "))

            for b in data:
                if b.get("bill_id") == bill_id:

                    if b.get("payment_status") == "Paid":
                        console.print("[yellow]⚠️ Cannot delete Paid Bill[/yellow]")
                        return

                    data.remove(b)
                    self.save(data)
                    console.print("[green]✅ Deleted[/green]")
                    return

            console.print("[red]Bill not found[/red]")

        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "delete", e)


# ================= MENU =================
def payment_menu():
    pm = PaymentManager()

    while True:
        console.print(Panel(
            "[bold magenta]💳 PAYMENT MENU[/bold magenta]\n\n"
            "1. View Bills\n2. Pay Bill\n3. History\n4. Delete\n5. Back",
            border_style="magenta"
        ))

        ch = input("Choice: ")

        if ch == "1":
            pm.view()
        elif ch == "2":
            pm.pay()
        elif ch == "3":
            pm.payment_history()
        elif ch == "4":
            pm.delete()
        elif ch == "5":
            break