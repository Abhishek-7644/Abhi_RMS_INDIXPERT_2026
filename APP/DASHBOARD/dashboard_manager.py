from rich.console import Console
from rich.panel import Panel

from APP.ORDER.order_manager import order_menu, OrderManager
from APP.BOOKING.booking_manager import booking_menu
from APP.BILLING.payment_menu import payment_menu, PaymentManager
from APP.INVENTORY.inventory_manager import inventory_staff_menu
from APP.REPORTS.report_manager import report_menu
from APP.FEEDBACK.feedback_manager import feedback_menu
from APP.RESTAURANT.restaurant_manager import RestaurantManager

console = Console(force_terminal=True, color_system="truecolor")


class DashboardManager:

    # ================= SAFE CALL =================
    def safe_call(self, func):
        try:
            func()
        except Exception as e:
            console.print(f"[bold red]❌ Error: {e}[/bold red]")

    def order(self, method):
        getattr(OrderManager(), method)()

    # ================= REDIRECT =================
    def redirect(self, user):
        role = user.get("role")

        if role == "admin":
            self.admin_dashboard()
        elif role == "user":
            self.user_dashboard()
        elif role == "manager":
            self.manager_dashboard()
        elif role == "chef":
            self.chef_dashboard()
        elif role == "inventory_staff":
            self.inventory_staff_dashboard()
        elif role == "delivery_staff":
            self.delivery_dashboard()
        else:
            self.staff_dashboard()

    # ================= USER =================
    def user_dashboard(self):
        while True:
            console.print(Panel(
                "[bold magenta]🌟 USER DASHBOARD 🌟[/bold magenta]\n\n"
                "[bold green]1. 🍽️ Menu[/bold green]\n"
                "[bold cyan]2. 🛒 Create Order[/bold cyan]\n"
                "[bold yellow]3. 📦 My Orders[/bold yellow]\n"
                "[bold blue]4. 💳 Payment[/bold blue]\n"
                "[bold magenta]5. 🧾 Print Bill[/bold magenta]\n"
                "[bold white]6. 🌐 Online Panel[/bold white]\n"
                "[bold green]7. 📅 Booking[/bold green]\n"
                "[bold cyan]8. 📝 Feedback[/bold cyan]\n"
                "[bold bright_yellow]9. ℹ️ About Restaurant[/bold bright_yellow]\n"
                "[bold red]10. 🚪 Logout[/bold red]",
                border_style="bright_magenta"
            ))

            ch = input("Choice :")

            if ch == "1":
                from APP.MENU.menu_manager import MenuManager
                self.safe_call(lambda: MenuManager().view_menu())
            elif ch in ["2", "3"]:
                self.safe_call(order_menu)
            elif ch == "4":
                self.safe_call(payment_menu)
            elif ch == "5":
                self.safe_call(lambda: PaymentManager().view())
            elif ch == "6":
                self.online_user_panel()
            elif ch == "7":
                self.safe_call(booking_menu)
            elif ch == "8":
                self.safe_call(feedback_menu)
            elif ch == "9":
                self.safe_call(lambda: RestaurantManager().view_restaurant_info())
            elif ch == "10":
                break

    # ================= USER ONLINE =================
    def online_user_panel(self):
        while True:
            console.print(Panel(
                "[bold blue]🌐 ONLINE USER PANEL[/bold blue]\n\n"
                "[bold green]1. 🍽️ View Menu[/bold green]\n"
                "[bold cyan]2. 🛒 Place Order[/bold cyan]\n"
                "[bold yellow]3. 📦 My Orders[/bold yellow]\n"
                "[bold magenta]4. 🔄 Update Order[/bold magenta]\n"
                "[bold blue]5. 🔍 Track Order[/bold blue]\n"
                "[bold red]6. 💳 Pay Bill[/bold red]\n"
                "[bold white]7. 🧾 Print Bill[/bold white]\n"
                "[bold green]8. 📅 Booking[/bold green]\n"
                "[bold cyan]9. 📝 Feedback[/bold cyan]\n"
                "[bold red]10. 🔙 Back[/bold red]",
                border_style="blue"
            ))

            ch = input("Choice :")

            if ch == "1":
                from APP.MENU.menu_manager import MenuManager
                self.safe_call(lambda: MenuManager().view_menu())
            elif ch in ["2", "3", "4", "5"]:
                self.safe_call(order_menu)
            elif ch == "6":
                self.safe_call(payment_menu)
            elif ch == "7":
                self.safe_call(lambda: PaymentManager().view())
            elif ch == "8":
                self.safe_call(booking_menu)
            elif ch == "9":
                self.safe_call(feedback_menu)
            elif ch == "10":
                break

    # ================= ADMIN =================
    def admin_dashboard(self):
        while True:
            console.print(Panel(
                "[bold red]👑 ADMIN DASHBOARD 👑[/bold red]\n\n"
                "[bold green]1. 🍽️ Menu[/bold green]\n"
                "[bold cyan]2. 📦 Orders[/bold cyan]\n"
                "[bold yellow]3. 📊 Reports[/bold yellow]\n"
                "[bold blue]4. 📦 Inventory[/bold blue]\n"
                "[bold magenta]5. 🌐 Online Panel[/bold magenta]\n"
                "[bold white]6. 📝 Feedback[/bold white]\n"
                "[bold bright_yellow]7. ℹ️ About Restaurant[/bold bright_yellow]\n"
                "[bold red]8. 🚪 Logout[/bold red]",
                border_style="bright_red"
            ))

            ch = input("Choice :")

            if ch == "1":
                from APP.MENU.menu_manager import menu_manager_menu
                self.safe_call(menu_manager_menu)
            elif ch == "2":
                self.safe_call(lambda: self.order("view_orders"))
            elif ch == "3":
                self.safe_call(report_menu)
            elif ch == "4":
                self.safe_call(inventory_staff_menu)
            elif ch == "5":
                self.online_admin_panel()
            elif ch == "6":
                self.safe_call(feedback_menu)
            elif ch == "7":
                self.safe_call(lambda: RestaurantManager().view_restaurant_info())
            elif ch == "8":
                break

    def online_admin_panel(self):
        while True:
            console.print(Panel(
                "[bold magenta]🌐 ONLINE ADMIN PANEL[/bold magenta]\n\n"
                "[bold green]1. 📦 Orders[/bold green]\n"
                "[bold cyan]2. 💳 Payments[/bold cyan]\n"
                "[bold yellow]3. 📝 Feedback[/bold yellow]\n"
                "[bold red]4. 🔙 Back[/bold red]",
                border_style="magenta"
            ))

            ch = input("Choice :")

            if ch == "1":
                self.safe_call(lambda: self.order("view_orders"))
            elif ch == "2":
                self.safe_call(lambda: PaymentManager().view())
            elif ch == "3":
                self.safe_call(feedback_menu)
            elif ch == "4":
                break

    # ================= MANAGER =================
    def manager_dashboard(self):
        while True:
            console.print(Panel(
                "[bold magenta]🧑‍💼 MANAGER DASHBOARD[/bold magenta]\n\n"
                "[bold green]1. 📊 Reports[/bold green]\n"
                "[bold cyan]2. 📦 Orders[/bold cyan]\n"
                "[bold yellow]3. 🌐 Online Panel[/bold yellow]\n"
                "[bold bright_yellow]4. ℹ️ About Restaurant[/bold bright_yellow]\n"
                "[bold red]5. 🔙 Back[/bold red]",
                border_style="magenta"
            ))

            ch = input("Choice :")

            if ch == "1":
                self.safe_call(report_menu)
            elif ch == "2":
                self.safe_call(lambda: self.order("view_orders"))
            elif ch == "3":
                self.manager_online_panel()
            elif ch == "4":
                self.safe_call(lambda: RestaurantManager().view_restaurant_info())
            elif ch == "5":
                break

    def manager_online_panel(self):
        while True:
            console.print(Panel(
                "[bold magenta]🌐 MANAGER ONLINE PANEL[/bold magenta]\n\n"
                "[bold green]1. 📦 Orders[/bold green]\n"
                "[bold cyan]2. 📊 Reports[/bold cyan]\n"
                "[bold red]3. 🔙 Back[/bold red]",
                border_style="magenta"
            ))

            ch = input("Choice :")

            if ch == "1":
                self.safe_call(lambda: self.order("view_orders"))
            elif ch == "2":
                self.safe_call(report_menu)
            elif ch == "3":
                break

    # ================= STAFF =================
    def staff_dashboard(self):
        while True:
            console.print(Panel(
                "[bold green]👨‍🍳 STAFF PANEL[/bold green]\n\n"
                "[bold cyan]1. 📦 Orders[/bold cyan]\n"
                "[bold blue]2. ✅ Confirm[/bold blue]\n"
                "[bold yellow]3. Search Order[/bold yellow]\n"
                "[bold magenta]4. 📦 Pack[/bold magenta]\n"
                "[bold red]5. ❌ Cancel[/bold red]\n"
                "[bold bright_yellow]6. ℹ️ About[/bold bright_yellow]\n"
                "[bold white]7. 🔙 Back[/bold white]",
                border_style="green"
            ))

            ch = input("Choice :")

            if ch == "1":
                self.safe_call(lambda: self.order("view_orders"))
            elif ch == "2":
                self.safe_call(lambda: self.order("confirm_order"))
            elif  ch == "3":
                self.safe_call(lambda: self.order("search_order"))
            elif ch == "4":
                self.safe_call(lambda: self.order("pack_order"))
            elif ch == "5":
                self.safe_call(lambda: self.order("cancel_order"))
            elif ch == "6":
                self.safe_call(lambda: RestaurantManager().view_restaurant_info())
            elif ch == "7":
                break

    # ================= CHEF =================
    def chef_dashboard(self):
        while True:
            console.print(Panel(
                "[bold yellow]👨‍🍳 CHEF PANEL[/bold yellow]\n\n"
                "[bold cyan]1. 📦 View Orders[/bold cyan]\n"
                "[bold green]2. 🍳 Start Cooking[/bold green]\n"
                "[bold blue]3. ✅ Mark Ready[/bold blue]\n"
                "[bold red]4. 🔙 Back[/bold red]",
                border_style="yellow"
            ))

            ch = input("Choice :")

            if ch == "1":
                self.safe_call(lambda: self.order("view_orders"))
            elif ch in ["2", "3"]:
                self.safe_call(lambda: self.order("chef_workflow"))
            elif ch == "4":
                break

    # ================= DELIVERY =================
    def delivery_dashboard(self):
        while True:
            console.print(Panel(
                "[bold white]🛵 DELIVERY PANEL[/bold white]\n\n"
                "[bold cyan]1. 📦 Orders[/bold cyan]\n"
                "[bold yellow]2. 🚚 Pick Order[/bold yellow]\n"
                "[bold yellow]3. Assign Order[/bold yellow]\n"
                "[bold green]4. 📍 Mark Delivered[/bold green]\n"
                "[bold red]5. 🔙 Back[/bold red]",
                border_style="white"
            ))

            ch = input("Choice :")

            if ch == "1":
                self.safe_call(lambda: self.order("view_orders"))
            elif ch == "2":
                self.safe_call(lambda: self.order("pick_order"))
            elif ch == "3":
                self.safe_call(lambda: self.order ("assign_delivery"))
            elif ch == "4":
                self.safe_call(lambda: self.order("mark_delivered"))
            elif ch == "5":
                break

    # ================= INVENTORY =================
    def inventory_staff_dashboard(self):
        while True:
            console.print(Panel(
                "[bold blue]📦 INVENTORY PANEL[/bold blue]\n\n"
                "[bold green]1. Open Inventory[/bold green]\n"
                "[bold red]2. Back[/bold red]",
                border_style="blue"
            ))

            ch = input("Choice :")

            if ch == "1":
                self.safe_call(inventory_staff_menu)
            elif ch == "2":
                break