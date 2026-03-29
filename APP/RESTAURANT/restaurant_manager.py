from rich.console import Console
from rich.panel import Panel
import json

console = Console(force_terminal=True, color_system="truecolor")


class RestaurantManager:

    def __init__(self):
        self.file = "APP/DATABASE/restaurant.json"

    # ================= VIEW =================
    def view_restaurant_info(self):
        try:
            with open(self.file, "r") as f:
                data = json.load(f)

            content = f"""
[bold yellow]🏢 {data.get('name')}[/bold yellow]

[cyan]👤 Owner:[/cyan] {data.get('owner')}
[green]📅 Since:[/green] {data.get('since')}
[magenta]📍 Location:[/magenta] {data.get('location')}

[bold blue]🍽️ Speciality:[/bold blue]
{data.get('speciality')}

[bold white]📞 Contact:[/bold white] {data.get('contact')}

[bold cyan]📖 About Us:[/bold cyan]
{data.get('about')}
"""

            console.print(
                Panel(
                    content,
                    border_style="bright_magenta",
                    title="✨ Restaurant Info ✨"
                )
            )

        except Exception as e:
            console.print("[red]❌ Unable to load restaurant info[/red]")