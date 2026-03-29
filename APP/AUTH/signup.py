import re
import random
from getpass import getpass
from rich.console import Console
from rich.panel import Panel
from rich import box
from APP.DATABASE.db import Database
from APP.LOGS.error_handler import error_handler

console = Console()


class Signup:
    def __init__(self):
        self.db = Database()

    def generate_user_id(self):
        try:
            return str(random.randint(100000, 999999))
        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "generate_user_id", e)
            return "000000"

    def validate_phone(self, phone):
        try:
            return re.fullmatch(r"\+91\d{10}", phone)
        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "validate_phone", e)
            return False

    def validate_email(self, email):
        try:
            return re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email)
        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "validate_email", e)
            return False

    def validate_aadhar(self, aadhar):
        return re.fullmatch(r"\d{12}", aadhar)

    def validate_pan(self, pan):
        return re.fullmatch(r"[A-Z]{5}\d{4}[A-Z]", pan)

    def is_unique_username(self, username, users):
        try:
            return all(user["username"] != username for user in users)
        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "is_unique_username", e)
            return False

    def is_unique_email(self, email, users):
        try:
            return all(user.get("email") != email for user in users)
        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "is_unique_email", e)
            return False

    def is_unique_phone(self, phone, users):
        try:
            return all(user.get("phone") != phone for user in users)
        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "is_unique_phone", e)
            return False

    def validate_name(self, name):
        return re.fullmatch(r"[A-Za-z ]+", name)

    def generate_otp(self):
        return str(random.randint(100000, 999999))

    def run(self):
        try:
            console.print(Panel(
                "📝 USER SIGNUP",
                border_style="bright_cyan",
                box=box.DOUBLE
            ))

            users = self.db.load_users()

            # ================= NAME =================
            while True:
                console.print("Enter Full Name:", style="cyan", end=" ")
                name = input()
                if self.validate_name(name):
                    break
                console.print("❌ Name should not contain digits!", style="red")

            # ================= USERNAME =================
            while True:
                console.print("Enter Username:", style="cyan", end=" ")
                username = input()
                if self.is_unique_username(username, users):
                    break
                console.print("❌ Username already exists!", style="red")

            # ================= PASSWORD =================
            while True:
                console.print("Enter Password:", style="cyan", end=" ")
                password = getpass("")
                console.print("Confirm Password:", style="cyan", end=" ")
                confirm = getpass("")

                if password == confirm and len(password) >= 4:
                    break
                console.print("❌ Password mismatch or too short!", style="red")

            # ================= ADDRESS =================
            console.print("Enter Country:", style="cyan", end=" ")
            country = input()

            console.print("Enter State:", style="cyan", end=" ")
            state = input()

            console.print("Enter Address:", style="cyan", end=" ")
            address = input()

            # ================= AADHAAR =================
            while True:
                console.print("Enter Aadhaar (12 digit):", style="cyan", end=" ")
                aadhar = input()
                if self.validate_aadhar(aadhar):
                    break
                console.print("❌ Invalid Aadhaar!", style="red")

            # ================= PAN =================
            while True:
                console.print("Enter PAN (ABCDE1234F):", style="cyan", end=" ")
                pan = input().upper()
                if self.validate_pan(pan):
                    break
                console.print("❌ Invalid PAN format!", style="red")

            # ================= PHONE =================
            while True:
                console.print("Enter Phone (+91XXXXXXXXXX):", style="cyan", end=" ")
                phone = input()

                if not self.validate_phone(phone):
                    console.print("❌ Invalid phone format!", style="red")
                elif not self.is_unique_phone(phone, users):
                    console.print("❌ Phone already exists!", style="red")
                else:
                    break

            phone_otp = self.generate_otp()
            console.print("📲 Sending OTP...", style="yellow")
            console.print(f"Your OTP is: {phone_otp}", style="bold cyan")

            while True:
                console.print("Enter OTP:", style="cyan", end=" ")
                user_otp = input()
                if user_otp == phone_otp:
                    console.print("✅ Phone Verified!", style="green")
                    break
                else:
                    console.print("❌ Wrong OTP!", style="red")

            # ================= EMAIL =================
            while True:
                console.print("Enter Email:", style="cyan", end=" ")
                email = input()

                if not self.validate_email(email):
                    console.print("❌ Invalid email!", style="red")
                elif not self.is_unique_email(email, users):
                    console.print("❌ Email already exists!", style="red")
                else:
                    break

            email_otp = self.generate_otp()
            console.print("📧 Sending Email OTP...", style="yellow")
            console.print(f"Your OTP is: {email_otp}", style="bold cyan")

            while True:
                console.print("Enter OTP:", style="cyan", end=" ")
                user_otp = input()
                if user_otp == email_otp:
                    console.print("✅ Email Verified!", style="green")
                    break
                else:
                    console.print("❌ Wrong OTP!", style="red")

            # ================= EXPERIENCE =================
            console.print("Have you worked before? (y/n):", style="cyan", end=" ")

            while True:
                worked = input().lower().strip()
                if worked in ["y", "n"]:
                    break
                else:
                    console.print("❌ Please enter only y or n", style="red")

            if worked == "y":

                while True:
                    console.print("Enter Experience (years):", style="cyan", end=" ")
                    experience = input().strip()

                    if experience.isdigit():
                        experience = int(experience)
                        break
                    else:
                        console.print("❌ Enter valid number (only digits)", style="red")

                while True:
                    console.print("Where did you work:", style="cyan", end=" ")
                    company = input().strip()

                    if company:
                        break
                    else:
                        console.print("❌ Company name cannot be empty", style="red")

            else:
                experience = None
                company = None

            # ================= QUALIFICATION =================
            console.print(
                "[bold cyan]Enter Qualification:[/bold cyan]\n"
                "[yellow]👉 Minimum qualification: 10th pass[/yellow]",
                end=" "
            )

            qualification = input().lower().strip()

            valid_keywords = ["10th", "12th", "graduate", "diploma"]

            if not any(q in qualification for q in valid_keywords):
                console.print("[bold red]❌ Not eligible (minimum 10th required)[/bold red]")
                return

            # ================= LANGUAGES =================
            console.print("Languages known (comma separated):", style="cyan", end=" ")
            languages = input().split(",")
            languages = [l.strip() for l in languages]

            # ================= COMPUTER =================
            console.print("Computer knowledge? (y/n):", style="cyan", end=" ")
            comp = input().lower()

            if comp == "y":
                console.print("What do you know:", style="cyan", end=" ")
                computer_skills = input()
            else:
                computer_skills = None

            # ================= BIKE =================
            console.print("Do you know bike riding? (y/n):", style="cyan", end=" ")
            bike = input().lower()

            if bike == "y":
                console.print("Do you have license? (y/n):", style="cyan", end=" ")
                license = input().lower()
            else:
                license = "n"

            delivery = bike == "y" and license == "y"

            if delivery:
                console.print("✅ Home Delivery Enabled", style="green")
            else:
                console.print("❌ Home Delivery not available", style="red")

            # ================= SAVE =================
            user = {
                "id": self.generate_user_id(),
                "name": name,
                "username": username,
                "password": password,
                "phone": phone,
                "email": email,
                "aadhar": aadhar,
                "pan": pan,
                "country": country,
                "state": state,
                "address": address,
                "experience": experience,
                "company": company,
                "qualification": qualification,
                "languages": languages,
                "computer_skills": computer_skills,
                "bike": bike,
                "license": license,
                "delivery": delivery,
                "role": "staff"
            }

            users.append(user)
            self.db.save_users(users)

            console.print("🎉 Signup Successful! Welcome aboard!", style="bold green")

        except Exception as e:
            error_handler.log_exception(self.__class__.__name__, "run", e)
            console.print("❌ Something went wrong during signup!", style="bold red")