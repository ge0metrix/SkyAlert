from textual.app import App, ComposeResult
from textual.widgets import Footer, Header
from textual.containers import HorizontalGroup, VerticalScroll
from textual.widgets import Button, Digits, Footer, Header, DataTable
from PlaneWatcher import PlaneWatcher

from datetime import datetime
import click
class PlaneWatcherApp(App):
    CSS_PATH = "skyalert.tss"
    def __init__(self, lat, lon, range, **kwargs) -> None:
        super().__init__(**kwargs)
        self.watcher = PlaneWatcher(lat, lon, range)
        self.title = f"Plane Watcher ({lat}, {lon}) Range: {range}nm"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        currenttable = DataTable(id='current_table', classes="current_table")
        currenttable.cursor_type = "none"
        currenttable.zebra_stripes = True

        seentable = DataTable(id='seen_table', classes="seen_table")
        seentable.cursor_type = "none"
        seentable.zebra_stripes = True
        seentable.loading = True
        
        yield currenttable
        yield seentable


    def on_mount(self) -> None:
        
        seentable = self.get_widget_by_id('seen_table', expect_type=DataTable)
        columns = ["Hex", "Type", "Reg", "Flight", "Closest (nm)", "First Seen", "Last Seen", "Helicopter?", "Interesting?", "Interesting Desc"]
        seentable.add_columns(*columns)

        currenttable = self.get_widget_by_id('current_table', expect_type=DataTable)
        columns = ["Hex", "Type", "Reg", "Flight", "Closest (nm)", "First Seen", "Last Seen", "Helicopter?", "Interesting?", "Interesting Desc"]
        currenttable.add_columns(*columns)
        
        self.refresh_data()
        self.set_interval(5, self.refresh_data)


    def update_seen(self) -> None:
        seentable = self.get_widget_by_id('seen_table', expect_type=DataTable)
        seentable.clear()
        seentable.loading = True
        sortedac = sorted(self.watcher.seen.values(), key=lambda ac: (ac.lastSeen, -ac.closestApproach), reverse=True)
        for ac in sortedac:
            closest = f"{ac.closestApproach:.2f}" if ac.closestApproach is not None else "N/A"
            first_seen = ac.firstSeen.strftime("%Y-%m-%d %H:%M:%S")
            last_seen = ac.lastSeen.strftime("%Y-%m-%d %H:%M:%S")
            color: str = "white"
            interestingdesc = self.watcher.get_interesting(ac.hex)
            if ac.is_interesting and ac.is_helicopter:
                color = "red"
            elif ac.is_interesting:\
                color = "yellow"
            elif ac.is_helicopter:
                color = "blue"

            seentable.add_row(f'[{color}]{ac.hex}[/{color}]', f'[{color}]{ac.type}[/{color}]', f'[{color}]{ac.tail}[/{color}]', f'[{color}]{ac.flight}[/{color}]', f'[{color}]{closest}[/{color}]', f'[{color}]{first_seen}[/{color}]', f'[{color}]{last_seen}[/{color}]', f'[{color}]{ac.is_helicopter}[/{color}]', f'[{color}]{ac.is_interesting}[/{color}]', f'[{color}]{interestingdesc.get("$Operator")}[/{color}]', key=ac.hex)

        seentable.loading = False

    def update_current(self) -> None:
        currenttable = self.get_widget_by_id('current_table', expect_type=DataTable)
        currenttable.clear()
        currenttable.loading = True
        for ac in self.watcher.aircraft:
            closest = f""
            first_seen = ""
            last_seen = ""
            color: str = "white"
            interestingdesc = self.watcher.get_interesting(ac.hex)
            dist = ac.distance_to(lat=self.watcher.lat, lon=self.watcher.lon, unit="nm")
            currenttable.add_row(f'[{color}]{ac.hex}[/{color}]', f'[{color}]{ac.t}[/{color}]', f'[{color}]{ac.r}[/{color}]', f'[{color}]{ac.flight}[/{color}]', f'[{color}]{dist}[/{color}]', f'[{color}]{first_seen}[/{color}]', f'[{color}]{last_seen}[/{color}]', f'[{color}]{None}[/{color}]', f'[{color}]{None}[/{color}]', f'[{color}]{interestingdesc.get("$Operator")}[/{color}]', key=ac.hex)

        currenttable.loading = False

    def refresh_data(self) -> None:
        self.watcher.refresh()
        self.update_seen()
        self.update_current()



@click.command()
@click.option('--lat', type=float, required=True, help='Latitude of the location to monitor')
@click.option('--lon', type=float, required=True, help='Longitude of the location to monitor')
@click.option('--range', type=int, default=5, help='Range in nautical miles to monitor (default: 5)')
def main(lat: float, lon: float, range: int) -> None:
    app = PlaneWatcherApp(lat=lat, lon=lon, range=range)
    app.run()


if __name__ == "__main__":
    main()