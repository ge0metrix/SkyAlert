from textual.app import App, ComposeResult
from textual.widgets import Footer, Header
from textual.containers import HorizontalGroup, VerticalScroll
from textual.widgets import Button, Digits, Footer, Header, DataTable
from PlaneWatcher import PlaneWatcher

from datetime import datetime

class PlaneWatcherApp(App):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        seentable = DataTable(id='seen_table')
        seentable.cursor_type = "none"
        seentable.zebra_stripes = True
        seentable.loading = True
        yield VerticalScroll(seentable)


    def on_mount(self) -> None:
        seentable = self.get_widget_by_id('seen_table', expect_type=DataTable)
        columns = ["Hex", "Type", "Reg", "Flight", "Closest (nm)", "First Seen", "Last Seen", "Helicopter?", "Interesting?", "Interesting Desc"]
        seentable.add_columns(*columns)
        self.watcher = PlaneWatcher(42.5197568, -71.417856, 10)
        self.refresh_data()
        self.set_interval(10, self.refresh_data)


    def refresh_data(self) -> None:
        self.watcher.refresh()
        seentable = self.get_widget_by_id('seen_table', expect_type=DataTable)
        seentable.clear()
        seentable.loading = True
        sortedac = sorted(self.watcher.seen.values(), key=lambda ac: (ac.lastSeen, -ac.closestApproach), reverse=True)
        for ac in sortedac:
            closest = f"{ac.closestApproach:.2f}" if ac.closestApproach is not None else "N/A"
            first_seen = ac.firstSeen.strftime("%Y-%m-%d %H:%M:%S")
            last_seen = ac.lastSeen.strftime("%Y-%m-%d %H:%M:%S")
            if ac.is_interesting and ac.is_helicopter:
                interestingdesc = self.watcher.get_interesting(ac.hex)
                seentable.add_row(f'[red on yellow]{ac.hex}[/red on yellow]', f'[red on yellow]{ac.type}[/red on yellow]', f'[red on yellow]{ac.tail}[/red on yellow]', f'[red on yellow]{ac.flight}[/red on yellow]', f'[red on yellow]{closest}[/red on yellow]', f'[red on yellow]{first_seen}[/red on yellow]', f'[red on yellow]{last_seen}[/red on yellow]', f'[red on yellow]{ac.is_helicopter}[/red on yellow]', f'[red on yellow]{ac.is_interesting}[/red on yellow]',f'[red on yellow]{interestingdesc}[/red on yellow]' , '', key=ac.hex)
            elif ac.is_interesting:
                interestingdesc = self.watcher.get_interesting(ac.hex)
                seentable.add_row(f'[red]{ac.hex}[/red]', f'[red]{ac.type}[/red]', f'[red]{ac.tail}[/red]', f'[red]{ac.flight}[/red]', f'[red]{closest}[/red]', f'[red]{first_seen}[/red]', f'[red]{last_seen}[/red]', f'[red]{ac.is_helicopter}[/red]', f'[red]{ac.is_interesting}[/red]', f'[red]{interestingdesc}[/red]', key=ac.hex)
            elif ac.is_helicopter:
                seentable.add_row(f'[yellow]{ac.hex}[/yellow]', f'[yellow]{ac.type}[/yellow]', f'[yellow]{ac.tail}[/yellow]', f'[yellow]{ac.flight}[/yellow]', f'[yellow]{closest}[/yellow]', f'[yellow]{first_seen}[/yellow]', f'[yellow]{last_seen}[/yellow]', f'[yellow]{ac.is_helicopter}[/yellow]', f'[yellow]{ac.is_interesting}[/yellow]','', key=ac.hex)
            else:
                seentable.add_row(ac.hex, ac.type, ac.tail, ac.flight, closest, first_seen, last_seen, ac.is_helicopter, ac.is_interesting, key=ac.hex)
        seentable.loading = False


if __name__ == "__main__":
    app = PlaneWatcherApp()
    app.run()