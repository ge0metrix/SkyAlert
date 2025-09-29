from typing import List, Any
import csv

class AlertList:
    def load(self):
        with open("alertlist.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.interesting_aircraft.append(row)
            

    def __init__(self):
        self.interesting_aircraft: List[dict[str,Any]] = [{}]
        self.load()
        self.interesting_hexes: List[str] = [item['$ICAO'].lower() for item in self.interesting_aircraft]


if __name__ == "__main__":
    al = AlertList()
    print(al.interesting_aircraft)