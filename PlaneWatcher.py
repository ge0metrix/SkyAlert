import time

from AirplanesLive_Client import AirplanesClient
from datetime import datetime
from AircraftResp import AircraftResp
from AircraftTypes import AircraftTypes
from SeenAircraft import SeenAircraft
from typing import Any, List
from AlertList import AlertList

# importing module
import logging

# Creating an object
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.WARN, format="%(asctime)s - %(levelname)s - %(message)s"
)


class PlaneWatcher:
    def __init__(self, lat: float, lon: float, rad: int):
        self.client: AirplanesClient = AirplanesClient()
        self.aircraft: List[AircraftResp] = []
        self.__aircraft_types: AircraftTypes = AircraftTypes()
        self.interestingData:AlertList = AlertList()
        self.__interesting_hexes: List = self.interestingData.interesting_hexes
        
        self.lat: float = lat
        self.lon: float = lon
        self.radius: int = rad
        self.last_refresh: datetime = datetime.now()
        self.seen: dict[str, SeenAircraft] = {}

    def refresh(self):
        self.last_refresh = datetime.now()
        logger.info("Fetching nearby aircraft...")
        data: List[dict] | None = self.client.get_point(
            self.lat, self.lon, self.radius
        )
        if not data:
            self.aircraft = []
            return
        self.aircraft = [AircraftResp.from_dict(x) for x in data]
        self.update_seen()

    def update_seen(self) -> None:
        for ac in self.aircraft:
            dist = ac.distance_to(lat=self.lat, lon=self.lon, unit="nm")

            if not dist:
                dist = float("inf")

            seenac = SeenAircraft(
                hex=ac.hex,
                type=ac.t,
                typeDesc=ac.desc,
                tail=ac.r,
                flight=ac.flight,
                closestApproach=dist,
                firstSeen=self.last_refresh,
                lastSeen=self.last_refresh,
                is_helicopter=self.is_helicopter(ac.t),
                is_interesting=self.is_interesting(ac.hex),
                groundSpeed=ac.gs,
                altitude=ac.alt_geom if ac.alt_geom != "ground" else 0,
                emergency=ac.emergency,
            )
            if ac.hex not in self.seen:
                self.seen[ac.hex] = seenac
                logger.info(f"New aircraft seen: {ac.hex} ({ac.flight})")
            else:
                self.seen[ac.hex].lastSeen = self.last_refresh
                if dist is not None:
                    if (
                        self.seen[ac.hex].closestApproach is None
                        or dist < self.seen[ac.hex].closestApproach
                    ):
                        self.seen[ac.hex].closestTime = self.last_refresh
                        self.seen[ac.hex].closestApproach = dist
                        self.seen[ac.hex].flight = ac.flight
                        self.seen[ac.hex].groundSpeed=ac.gs if ac.gs is not None else float(0)
                        self.seen[ac.hex].altitude=ac.alt_geom if ac.alt_geom != "ground" else float(0)
                        self.seen[ac.hex].emergency=ac.emergency if ac.emergency is not None or ac.emergency != "False" else "False"

    def is_helicopter(self, type_str: str) -> bool:
        for item in self.__aircraft_types.aircraft_types:
            if item["Designator"] == type_str:
                return (
                    item["AircraftDescription"] == "Helicopter"
                    or item["AircraftDescription"] == "Tiltrotor"
                )
        return False

    def print_helicopters(self):
        helicopters = [
            ac
            for ac in self.aircraft
            if self.is_helicopter(ac.t)
        ]
        for heli in helicopters:
            dist = heli.distance_to(lat=self.lat, lon=self.lon, unit="nm")
            dist_str = "unknown" if dist is None else f"{dist:.2f} nm"
            print(
                f"{self.last_refresh}\t{heli.hex}\t{heli.flight}\t{heli.desc}\t{dist_str}"
            )

    def print_aircraft(self):
        for aircraft in self.aircraft:
            dist = aircraft.distance_to(lat=self.lat, lon=self.lon, unit="nm")
            dist_str = "unknown" if dist is None else f"{dist:.2f} nm"
            print(
                f"{self.last_refresh}\t{aircraft.hex}\t{aircraft.flight}\t{aircraft.desc}\t{dist_str}"
            )

    def is_interesting(self, hex:str) -> bool:
        return hex.lower() in self.__interesting_hexes
    
    def get_interesting(self, hex:str) -> dict[str,Any]:
        x =  [x for x in self.interestingData.interesting_aircraft if x['$ICAO'].lower() == hex.lower()]
        if len(x) > 0:
            return x[0]
        return {}


if __name__ == "__main__":
    watcher = PlaneWatcher(42.5197568, -71.417856, 10)
    while True:
        watcher.refresh()
        for k in watcher.seen.keys():
            print(watcher.seen[k], watcher.is_helicopter(watcher.seen[k].type))
        print("----")
        time.sleep(5)
