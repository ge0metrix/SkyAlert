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

    def __str__(self) -> str:
        return f"{self.lastSeen} \t {self.hex} \t {self.type} \t {self.flight} \t {self.tail} \t {self.closestApproach:.2f}"

class CurrentAircraft:
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

    def __str__(self) -> str:
        return f"{self.lastSeen} \t {self.hex} \t {self.type} \t {self.flight} \t {self.tail} \t {self.closestApproach:.2f}"
