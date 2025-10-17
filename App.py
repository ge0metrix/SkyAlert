from typing import List
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header
from textual.containers import HorizontalGroup, VerticalScroll
from textual.widgets import Button, Digits, Footer, Header, DataTable

from PlaneWatcher import PlaneWatcher
from textual.widget import Widget

from datetime import datetime
import click

from SeenAircraft import SeenAircraft


class SkyAlertApp(App):

    CSS_PATH = "skyalert.tss"
    ENABLE_COMMAND_PALETTE = False

    def __init__(self, lat, lon, range, **kwargs) -> None:
        super().__init__(**kwargs)
        self.watcher = PlaneWatcher(lat, lon, range)
        self.title = f"Plane Watcher ({lat}, {lon}) Range: {range}nm"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        currenttable = DataTable(id="current_table", classes="current_table")
        currenttable.cursor_type = "none"
        currenttable.zebra_stripes = True

        interestingtable = DataTable(
            id="interesting_table", classes="interesting_table"
        )
        interestingtable.cursor_type = "none"
        interestingtable.zebra_stripes = True

        seentable = DataTable(id="seen_table", classes="seen_table")
        seentable.cursor_type = "none"
        seentable.zebra_stripes = True

        yield currenttable
        yield interestingtable
        yield seentable

    def on_mount(self) -> None:
        columns = [
            ("Hex", "Hex"),
            ("Type", "Type"),
            ("Reg", "Reg"),
            ("Flight", "Flight"),
            ("Distance", "Closest"),
            ("First Seen", "First Seen"),
            ("Last Seen", "Last Seen"),
            #("Helicopter", "Helicopter"),
            #("Interesting", "Interesting"),
            ("Speed", "Speed"),
            ("Altitude", "Altitude"),
            ("Highest Altitude", "Highest Altitude"),
            ("Lowest Altitude", "Lowest Altitude"),
            ("Fastest GS", "Fastest GS"),
            ("Slowest GS", "Slowest GS"),
            ("Interesting Desc", "Interesting Desc"),
            #("Emergency", "Emergency")
        ]

        currenttable = self.get_widget_by_id("current_table", expect_type=DataTable)
        for label, key in columns:
            currenttable.add_column(label=label, key=key)

        columns = [
            ("Hex", "Hex"),
            ("Type", "Type"),
            ("Reg", "Reg"),
            ("Flight", "Flight"),
            ("Closest", "Closest"),
            ("First Seen", "First Seen"),
            ("Last Seen", "Last Seen"),
            #("Helicopter", "Helicopter"),
            #("Interesting", "Interesting"),
            ("Speed", "Speed"),
            ("Altitude", "Altitude"),
            ("Highest Altitude", "Highest Altitude"),
            ("Lowest Altitude", "Lowest Altitude"),
            ("Fastest GS", "Fastest GS"),
            ("Slowest GS", "Slowest GS"),
            ("Interesting Desc", "Interesting Desc"),

            #("Emergency", "Emergency")

        ]
        interestingtable = self.get_widget_by_id(
            "interesting_table", expect_type=DataTable
        )
        for label, key in columns:
            interestingtable.add_column(label=label, key=key)

        seentable = self.get_widget_by_id("seen_table", expect_type=DataTable)
        for label, key in columns:
            seentable.add_column(label=label, key=key)

        self.refresh_data()
        self.set_interval(5, self.refresh_data)

    def update_aircraft_table(self, table: DataTable, data: list[SeenAircraft]) -> None:
        self.log.info(f"{table.id}:\t Updating with {len(data)} entries")
        table.clear()
        for ac in data:
            if ac.hex.startswith("~"):
                self.log.debug(f"{table.id}:\t Skipping invalid hex {ac.hex}")
                continue
            closest = (
                f"{ac.closestApproach:.2f}" if ac.closestApproach is not None else "N/A"
            )
            first_seen = ac.firstSeen.strftime("%Y-%m-%d %H:%M:%S")
            last_seen = ac.lastSeen.strftime("%Y-%m-%d %H:%M:%S")
            color: str = "white"
            interestingdesc = self.watcher.get_interesting(ac.hex)
            color = "white"
            if ac.is_interesting and ac.is_helicopter:
                color = "red"
            elif ac.is_interesting:
                color = "yellow"
            elif ac.is_helicopter:
                color = "blue"
            elif ac.emergency and ac.emergency != "none":
                color = "magenta"
            self.log.debug(f"{table.id}:\t Adding row for {ac.hex} to table {table.id}")
            self.log.debug(f"{table.id}:\t {ac.highest_altitude}")
            rk = table.add_row(
                f"[{color}]{ac.hex.upper()}[/{color}]",
                f"[{color}]{ac.type}[/{color}]",
                f"[{color}]{ac.tail}[/{color}]",
                f"[{color}]{ac.flight}[/{color}]",
                f"[{color}]{closest}[/{color}]",
                f"[{color}]{first_seen}[/{color}]",
                f"[{color}]{last_seen}[/{color}]",
                #f"[{color}]{ac.is_helicopter}[/{color}]",
                #f"[{color}]{ac.is_interesting}[/{color}]",
                f"[{color}]{ac.groundSpeed} kt[/{color}]",
                f"[{color}]{ac.altitude} ft[/{color}]",
                f"[{color}]{ac.highest_altitude} ft[/{color}]",
                f"[{color}]{ac.lowest_altitude} ft[/{color}]",
                f"[{color}]{ac.fastestGs} kt[/{color}]",
                f"[{color}]{ac.slowestGs} kt[/{color}]",
                f'[{color}]{interestingdesc.get("$Operator")}[/{color}]',
                
                #f"[{color}]{ac.emergency}[/{color}]",
                
                key=ac.hex,
            )

    def update_seen(self) -> None:
        seentable = self.get_widget_by_id("seen_table", expect_type=DataTable)
        sortedac = sorted(
            self.watcher.seen.values(),
            key=lambda ac: (ac.lastSeen, -ac.closestApproach),
            reverse=True,
        )
        self.log.debug(sortedac)
        self.update_aircraft_table(seentable, sortedac)

    def update_interesting(self) -> None:
        interestingtable = self.get_widget_by_id(
            "interesting_table", expect_type=DataTable
        )
        interestingac = [
            ac
            for ac in self.watcher.seen.values()
            if ac.is_interesting or ac.is_helicopter
        ]
        sortedac = sorted(
            interestingac,
            key=lambda ac: (ac.lastSeen, -ac.closestApproach),
            reverse=True,
        )
        self.update_aircraft_table(interestingtable, sortedac)

    def update_current(self) -> None:
        currenttable = self.get_widget_by_id("current_table", expect_type=DataTable)
        aircraft: List[SeenAircraft] = []
        for ac in self.watcher.aircraft:
            dist = ac.distance_to(lat=self.watcher.lat, lon=self.watcher.lon, unit="nm")
            seenac = SeenAircraft(
                hex=ac.hex,
                type=ac.t,
                typeDesc=ac.desc,
                tail=ac.r,
                flight=ac.flight,
                closestApproach=dist if dist is not None else float("inf"),
                firstSeen=self.watcher.last_refresh,
                lastSeen=self.watcher.last_refresh,
                is_helicopter=self.watcher.is_helicopter(ac.t),
                is_interesting=self.watcher.is_interesting(ac.hex),
                groundSpeed=ac.gs,
                altitude=ac.alt_geom if ac.alt_geom else 0,
                emergency=ac.emergency,
            )
            aircraft.append(seenac)
        sortedac = sorted(
            aircraft, key=lambda ac: (ac.lastSeen, -ac.closestApproach), reverse=True
        )
        self.update_aircraft_table(currenttable, sortedac)

    def refresh_data(self) -> None:
        self.watcher.refresh()
        self.update_seen()
        self.update_current()
        self.update_interesting()


@click.command()
@click.option(
    "--lat", type=float, required=True, help="Latitude of the location to monitor"
)
@click.option(
    "--lon", type=float, required=True, help="Longitude of the location to monitor"
)
@click.option(
    "--range",
    type=int,
    default=5,
    help="Range in nautical miles to monitor (default: 5)",
)
def main(lat: float, lon: float, range: int) -> None:
    app = SkyAlertApp(lat=lat, lon=lon, range=range)
    app.run()


if __name__ == "__main__":
    main()
