from rich.console import Console
from rich.panel import Panel
from APP.AUTH.menu import start_menu

console = Console()


def main():
    console.print(Panel(
        "[bold cyan]🚀 RESTAURANT MANAGEMENT SYSTEM[/bold cyan]\n"
        "[green]All Modules Execution[/green]",
        border_style="magenta"
    ))

    start_menu()


if __name__ == "__main__":
    main()
