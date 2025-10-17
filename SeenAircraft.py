from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime


@dataclass
class SeenAircraft:
    hex: str
    type: str = ""
    typeDesc: Optional[str] = None
    tail: Optional[str] = None
    flight: Optional[str] = None
    closestApproach: float = float('inf')
    closestTime: datetime = datetime.now()
    firstSeen: datetime = datetime.now()
    lastSeen: datetime = datetime.now()
    is_helicopter: bool = False
    is_interesting: bool = False
    groundSpeed: float = 0
    altitude: float = 0
    emergency: Optional[str] = "False"
    highest_altitude: float = altitude
    lowest_altitude: float = altitude
    fastestGs: float = groundSpeed
    slowestGs: float = groundSpeed