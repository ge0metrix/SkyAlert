from dataclasses import dataclass
import json
from typing import List

class AircraftTypes:
    def __get_aircraft_types(self) -> List[dict]:
        with open("AircraftTypes.json", "r") as f:
            data = json.load(f)
        return data
    
    def __init__(self):
        self.aircraft_types:List[dict] = self.__get_aircraft_types()




"""    {
        "ModelFullName": "2",
        "Description": "L4E",
        "WTC": "L",
        "WTG": "G",
        "Designator": "SOL2",
        "ManufacturerCode": "SOLAR IMPULSE",
        "ShowInPart3Only": false,
        "AircraftDescription": "LandPlane",
        "EngineCount": "4",
        "EngineType": "Electric"
    },"""

@dataclass
class AircraftType:
    ModelFullName: str
    Description: str
    WTC: str
    WTG: str
    Designator: str
    ManufacturerCode: str
    ShowInPart3Only: bool
    AircraftDescription: str
    EngineCount: str
    EngineType: str 