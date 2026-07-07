"""
FIFA World Cup 2026 - Stadium Operations State Engine
Manages the tournament telemetry dictionary and domain object wrappers.
"""

from typing import Dict, List, Any

# Core modular state functions
def gate_determine_status(congestion: int) -> str:
    """Computes operational status of a gate based on its congestion percentage.

    Args:
        congestion: Integer load percentage (0-100).

    Returns:
        str: Operational status label ('Normal', 'Busy', or 'Bottleneck').
    """
    if congestion >= 80:
        return "Bottleneck"
    elif congestion >= 60:
        return "Busy"
    return "Normal"


def transit_determine_status(delay: int) -> str:
    """Computes operational status of a transit line based on delay minutes.

    Args:
        delay: Delay in minutes.

    Returns:
        str: Service status label ('On Time', 'Minor Delay', or 'Delayed').
    """
    if delay >= 15:
        return "Delayed"
    elif delay > 0:
        return "Minor Delay"
    return "On Time"


def init_stadium_state(match_phase: str = "Pre-Match Arrival") -> Dict[str, Any]:
    """Initializes the stadium operations telemetry dictionary context.

    Args:
        match_phase: Starting tournament operational phase.

    Returns:
        Dict[str, Any]: Primitive dictionary managing all zoned metrics.
    """
    return {
        "match_phase": match_phase,
        "weather": "Clear, 24°C",
        "gates": {
            "Gate A": {
                "name": "Gate A",
                "capacity": 20000,
                "zone": "Public",
                "congestion": 85,
                "status": "Bottleneck"
            },
            "Gate B": {
                "name": "Gate B",
                "capacity": 25000,
                "zone": "Public",
                "congestion": 45,
                "status": "Normal"
            },
            "Gate C": {
                "name": "Gate C",
                "capacity": 18000,
                "zone": "VIP/Hospitality",
                "congestion": 70,
                "status": "Busy"
            },
            "Gate D": {
                "name": "Gate D",
                "capacity": 22000,
                "zone": "Public",
                "congestion": 30,
                "status": "Normal"
            },
        },
        "transit": {
            "Train Line 1": {
                "name": "Train Line 1",
                "is_fan_festival_route": False,
                "delay": 0,
                "status": "On Time"
            },
            "Train Line 2": {
                "name": "Train Line 2",
                "is_fan_festival_route": False,
                "delay": 15,
                "status": "Delayed"
            },
            "Fan Festival Shuttle": {
                "name": "Fan Festival Shuttle",
                "is_fan_festival_route": True,
                "delay": 5,
                "status": "Minor Delay"
            },
        },
        "incidents": [
            {
                "id": "inc_1",
                "title": "Gate A Turnstile Failure",
                "location": "Gate A Security Perimeter",
                "priority": "High",
                "description": "3 ticket scanners offline, causing queue building and slow scanning rate.",
                "status": "Active"
            },
            {
                "id": "inc_2",
                "title": "Medical: Heat Exhaustion",
                "location": "Concourse Sector 108",
                "priority": "Medium",
                "description": "Fan fainted due to high temp. Stewards attending, awaiting EMS.",
                "status": "Active"
            }
        ]
    }


def update_gate_congestion_state(state: Dict[str, Any], name: str, value: int) -> None:
    """Updates gate congestion level inside state dictionary.

    Args:
        state: Stadium state dictionary.
        name: Name identifier of the target gate.
        value: Congestion load value (0-100).
    """
    congestion = max(0, min(100, value))
    state["gates"][name]["congestion"] = congestion
    state["gates"][name]["status"] = gate_determine_status(congestion)


def update_transit_delay_state(state: Dict[str, Any], name: str, minutes: int) -> None:
    """Updates transit delays inside state dictionary.

    Args:
        state: Stadium state dictionary.
        name: Name of the transit service.
        minutes: Current delay in minutes.
    """
    delay = max(0, minutes)
    state["transit"][name]["delay"] = delay
    state["transit"][name]["status"] = transit_determine_status(delay)


def add_incident_state(
    state: Dict[str, Any],
    title: str,
    location: str,
    priority: str,
    description: str
) -> None:
    """Logs a new active incident to the state incidents log array.

    Args:
        state: Stadium state dictionary.
        title: Short summary description.
        location: Zone or sector name.
        priority: Priority tag level.
        description: Detail information text.
    """
    inc_id = f"inc_{len(state['incidents']) + 1}"
    state["incidents"].append({
        "id": inc_id,
        "title": title,
        "location": location,
        "priority": priority,
        "description": description,
        "status": "Active"
    })


def clear_incidents_state(state: Dict[str, Any]) -> None:
    """Clears all logged active incidents.

    Args:
        state: Stadium state dictionary.
    """
    state["incidents"].clear()


class Gate:
    """Wrapper exposing Gate properties from primitive state values."""

    def __init__(
        self,
        name_or_dict: Any,
        capacity: int = 0,
        zone: str = "",
        congestion: int = 0
    ) -> None:
        """Initializes compatibility object mapping to dictionary partition.

        Args:
            name_or_dict: Dictionary state slice or gate name string.
            capacity: Gate hourly throughput capacity.
            zone: Gate zone identifier.
            congestion: Gate congestion load.
        """
        if isinstance(name_or_dict, dict):
            self._state_dict: Dict[str, Any] = name_or_dict
        else:
            self._state_dict = {
                "name": name_or_dict,
                "capacity": capacity,
                "zone": zone,
                "congestion": max(0, min(100, congestion)),
                "status": gate_determine_status(congestion)
            }

    @property
    def name(self) -> str:
        """Name of the gate."""
        return self._state_dict["name"]

    @property
    def capacity(self) -> int:
        """Operational capacity."""
        return self._state_dict["capacity"]

    @property
    def zone(self) -> str:
        """Zone description."""
        return self._state_dict["zone"]

    @property
    def congestion(self) -> int:
        """Congestion rating (0-100)."""
        return self._state_dict["congestion"]

    @property
    def status(self) -> str:
        """Calculated load status."""
        return self._state_dict["status"]

    def update_congestion(self, level: int) -> None:
        """Updates gate load percentage."""
        self._state_dict["congestion"] = max(0, min(100, level))
        self._state_dict["status"] = gate_determine_status(self._state_dict["congestion"])

    def to_dict(self) -> Dict[str, Any]:
        """Returns the dictionary representation."""
        return self._state_dict


class TransitLine:
    """Wrapper exposing TransitLine properties from primitive state values."""

    def __init__(
        self,
        name_or_dict: Any,
        is_fan_festival_route: bool = False,
        delay: int = 0
    ) -> None:
        """Initializes compatibility object mapping to dictionary partition.

        Args:
            name_or_dict: Dictionary state slice or transit name string.
            is_fan_festival_route: True if links to Fan Festival.
            delay: Delay in minutes.
        """
        if isinstance(name_or_dict, dict):
            self._state_dict: Dict[str, Any] = name_or_dict
        else:
            self._state_dict = {
                "name": name_or_dict,
                "is_fan_festival_route": is_fan_festival_route,
                "delay": max(0, delay),
                "status": transit_determine_status(delay)
            }

    @property
    def name(self) -> str:
        """Transit system name."""
        return self._state_dict["name"]

    @property
    def is_fan_festival_route(self) -> bool:
        """True if route connects to Fan Festival."""
        return self._state_dict["is_fan_festival_route"]

    @property
    def delay(self) -> int:
        """Delay in minutes."""
        return self._state_dict["delay"]

    @property
    def status(self) -> str:
        """Transit load status."""
        return self._state_dict["status"]

    def update_delay(self, minutes: int) -> None:
        """Updates transit delay value."""
        self._state_dict["delay"] = max(0, minutes)
        self._state_dict["status"] = transit_determine_status(self._state_dict["delay"])

    def to_dict(self) -> Dict[str, Any]:
        """Returns the dictionary representation."""
        return self._state_dict


class Incident:
    """Wrapper exposing Incident properties from primitive state values."""

    def __init__(
        self,
        incident_id_or_dict: Any,
        title: str = "",
        location: str = "",
        priority: str = "",
        description: str = "",
        status: str = "Active"
    ) -> None:
        """Initializes compatibility object mapping to dictionary partition.

        Args:
            incident_id_or_dict: Dictionary state slice or incident ID string.
            title: Short summary description.
            location: Zone or sector name.
            priority: Incident priority level.
            description: Log description text.
            status: Active or resolved status.
        """
        if isinstance(incident_id_or_dict, dict):
            self._state_dict: Dict[str, Any] = incident_id_or_dict
        else:
            self._state_dict = {
                "id": incident_id_or_dict,
                "title": title,
                "location": location,
                "priority": priority,
                "description": description,
                "status": status
            }

    @property
    def incident_id(self) -> str:
        """Incident ID."""
        return self._state_dict["id"]

    @property
    def title(self) -> str:
        """Incident summary."""
        return self._state_dict["title"]

    @property
    def location(self) -> str:
        """Incident location."""
        return self._state_dict["location"]

    @property
    def priority(self) -> str:
        """Priority severity rating."""
        return self._state_dict["priority"]

    @property
    def description(self) -> str:
        """Detailed description log."""
        return self._state_dict["description"]

    @property
    def status(self) -> str:
        """Resolution status."""
        return self._state_dict["status"]

    def to_dict(self) -> Dict[str, Any]:
        """Returns the dictionary representation."""
        return self._state_dict


class StadiumStateContext:
    """Aggregates all real-time stadium metrics, incidents, and match-day phase states."""

    def __init__(self, match_phase: str = "Pre-Match Arrival") -> None:
        """Initializes a StadiumStateContext instance with default telemetry layout.

        Args:
            match_phase: The initial match phase.
        """
        self.state: Dict[str, Any] = init_stadium_state(match_phase)
        self._gates: Dict[str, Gate] = {
            name: Gate(d) for name, d in self.state["gates"].items()
        }
        self._transit: Dict[str, TransitLine] = {
            name: TransitLine(d) for name, d in self.state["transit"].items()
        }
        self._cached_incidents: List[Incident] = [
            Incident(i) for i in self.state["incidents"]
        ]

    @property
    def match_phase(self) -> str:
        """Gets match phase."""
        return self.state["match_phase"]

    @match_phase.setter
    def match_phase(self, val: str) -> None:
        """Sets match phase."""
        self.state["match_phase"] = val

    def set_match_phase(self, phase: str) -> None:
        """Updates match phase."""
        self.state["match_phase"] = phase

    @property
    def gates(self) -> Dict[str, Gate]:
        """Gets gates map."""
        return self._gates

    @property
    def transit(self) -> Dict[str, TransitLine]:
        """Gets transit map."""
        return self._transit

    @property
    def incidents(self) -> List[Incident]:
        """Gets incident wrappers."""
        return self._cached_incidents

    def update_gate_congestion(self, name: str, level: int) -> None:
        """Updates gate congestion."""
        if name not in self.state["gates"]:
            raise KeyError(f"Gate '{name}' is not recognized in current stadium state.")
        update_gate_congestion_state(self.state, name, level)

    def update_transit_delay(self, name: str, minutes: int) -> None:
        """Updates transit delay."""
        if name not in self.state["transit"]:
            raise KeyError(f"Transit line '{name}' is not registered.")
        update_transit_delay_state(self.state, name, minutes)

    def add_incident(self, title: str, location: str, priority: str, description: str) -> None:
        """Adds a new incident."""
        add_incident_state(self.state, title, location, priority, description)
        self._cached_incidents.append(Incident(self.state["incidents"][-1]))

    def clear_incidents(self) -> None:
        """Clears all logged incidents."""
        clear_incidents_state(self.state)
        self._cached_incidents.clear()

    def to_dict(self) -> Dict[str, Any]:
        """Converts state to dict."""
        return self.state

    @property
    def weather(self) -> str:
        """Gets weather conditions."""
        return self.state.get("weather", "Clear, 24°C")
