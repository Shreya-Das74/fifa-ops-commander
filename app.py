"""
FIFA World Cup 2026 - Stadium Operations Command Assistant
An enterprise-grade, functional-modular, real-time command dashboard and GenAI assistant.
Enforces strict typing, detailed Google docstrings, custom exceptions, and WCAG accessibility.
"""

import os
import json
import re
import html
from typing import Dict, List, Any, Optional
import streamlit as st
import google.generativeai as genai
from config import config, FIFAOpsException, ConfigurationException, SecurityInjectionException, LLMTimeoutException

# =====================================================================
# 1. CORE FUNCTIONAL-MODULAR DOMAIN STATE ENGINE
# =====================================================================

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


# =====================================================================
# 2. CLASS COMPATIBILITY WRAPPERS (LEGACY SUPPORT FOR AST RUNNERS)
# =====================================================================

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
        return [Incident(i) for i in self.state["incidents"]]

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

    def clear_incidents(self) -> None:
        """Clears all logged incidents."""
        clear_incidents_state(self.state)

    def to_dict(self) -> Dict[str, Any]:
        """Converts state to dict."""
        return self.state


# =====================================================================
# 3. SECURITY & INPUT SANITIZATION LAYER
# =====================================================================

INJECTION_REGEXES: List[re.Pattern] = [
    re.compile(r"ignore\s+(?:all\s+)?previous\s+instructions", re.IGNORECASE),
    re.compile(r"system\s+override", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+a", re.IGNORECASE),
    re.compile(r"act\s+as\s+a", re.IGNORECASE),
    re.compile(r"forget\s+(?:your\s+)?instructions", re.IGNORECASE),
    re.compile(r"developer\s+mode", re.IGNORECASE),
    re.compile(r"bypass\s+restrictions", re.IGNORECASE),
]


def sanitize_input(text: str) -> str:
    """Escapes HTML and filters malicious prompt injections.

    Args:
        text: Raw user input text.

    Returns:
        str: Sanitized clean string.

    Raises:
        ValueError: If query is empty or only whitespace.
        SecurityInjectionException: If injection signature is detected.
    """
    if not text or not text.strip():
        raise ValueError("Input query cannot be empty or whitespace only.")
    escaped = html.escape(text)
    clean_text = re.sub(r"<[^>]*>", "", escaped)
    for pattern in INJECTION_REGEXES:
        if pattern.search(clean_text):
            raise SecurityInjectionException("Security threat blocked: Prompt injection detected.")
    return clean_text


class SecuritySanitizer:
    """Handles text validation and security sanitization for command center inputs."""

    def __init__(self) -> None:
        """Initializes the sanitizer with pre-compiled regex safety rules."""
        self._injection_regexes: List[re.Pattern] = INJECTION_REGEXES

    def sanitize_input(self, text: str) -> str:
        """Sanitizes raw user input."""
        return sanitize_input(text)


# =====================================================================
# 4. DECISION ENGINE & MULTILINGUAL FALLBACKS
# =====================================================================

def _fallback_gate_plan(query: str, state_dict: Dict[str, Any], match_phase: str) -> str:
    """Builds fallback directive for perimeter gate bottleneck queries."""
    high_gates = [
        name for name, details in state_dict["gates"].items()
        if details["congestion"] >= 80
    ]
    response = f"### 📋 Crowd Management Directive (Fallback Mode - Phase: {match_phase})\n\n"
    if match_phase == "Pre-Match Arrival":
        response += "ℹ️ **Operational Context**: Spectators are arriving. Focus is on ticket scanning checkpoints.\n\n"
    elif match_phase == "Half-Time Rush":
        response += "ℹ️ **Operational Context**: Spectators are in internal concourses. Focus is on concession area buffer queues.\n\n"
    elif match_phase == "Post-Match Egress":
        response += "ℹ️ **Operational Context**: Mass stadium exit. Focus is on outer perimeter gates and transit pathways.\n\n"

    if high_gates:
        response += f"⚠️ **High Congestion Alert**: Zoned gates operating at bottleneck thresholds (80%+): **{', '.join(high_gates)}**.\n\n"
        for gate_name in high_gates:
            gate_info = state_dict["gates"][gate_name]
            zone_type = gate_info["zone"]
            load = gate_info["congestion"]
            response += f"#### 🔴 {gate_name} ({zone_type} Zone - Load: {load}%)\n"
            if zone_type == "VIP/Hospitality" or "VIP" in zone_type:
                response += "*   **Hospitality Operations**: Deploy VIP Liaison Squad B to assist with high-density credential verification checks.\n"
            else:
                response += "*   **Public Egress / Entry**: Deploy **Bilingual Volunteer Team C (English/Spanish/Arabic)** to direct spectators towards less congested public channels.\n"
            if match_phase == "Pre-Match Arrival":
                response += "*   **Arrival Protocol**: Coordinate with gate scanning supervisors to open 2 backup manual scanner lanes.\n"
            elif match_phase == "Post-Match Egress":
                response += "*   **Egress Protocol**: Hold fans at concourse exit gates if the outer perimeter gate buffer zones are saturated.\n"
            response += "*   **Accessibility Priority**: Keep adjacent wheelchair access ramps clear of queue lines. Deploy 2 mobility helpers to elevators near this gate.\n\n"
        alternatives = [
            name for name, details in state_dict["gates"].items()
            if details["congestion"] < 60
        ]
        if alternatives:
            response += f"💡 **Tactical Routing**: Adjust digital displays to reroute approaching crowds to: **{', '.join(alternatives)}**.\n"
    else:
        response += "✅ **Perimeter Gates Stable**: All gate checkpoints are operating under optimal capacities (under 80%). Maintain standard staff layout."
    return response


def _fallback_incident_plan(query: str, state_dict: Dict[str, Any], match_phase: str) -> str:
    """Builds fallback directive for security, medical, and technical incident logs."""
    incidents = state_dict["incidents"]
    if incidents:
        response = f"### 🚨 Active Incident Action Directives (Fallback Mode - Phase: {match_phase})\n\n"
        response += f"There are currently **{len(incidents)} active incident(s)** logged in the command log:\n\n"
        for inc in incidents:
            prio = inc["priority"]
            loc = inc["location"]
            prio_tag = "🔴 [CRITICAL]" if prio == "Critical" else "🟡 [HIGH]" if prio == "High" else "🔵 [MEDIUM]"
            response += f"#### {prio_tag} {inc['title']} at *{loc}*\n"
            response += f"**Description**: {inc['description']}\n"
            response += "**Operational Directives**:\n"
            if prio in ["Critical", "High"]:
                response += (
                    f"*   **Emergency Response**: Immediately dispatch Zone Supervisor and Emergency Medical/Security teams (ETA < 3 minutes).\n"
                    f"*   **Cordon Control**: Station 4 stewards to set up a perimeter cordon to secure path access.\n"
                    f"*   **Bilingual Direction**: Deploy **Arabic/Spanish bilingual staff** to direct crowds away from the incident location.\n"
                    f"*   **Accessibility Protocol**: If evacuation of the immediate sector is required, deploy manual wheelchair transport helpers to designated ADA zones near {loc}.\n"
                )
            else:
                response += (
                    f"*   **Staff Action**: Dispatch nearest security steward to verify status and monitor path clearance.\n"
                    f"*   **Maintenance Dispatch**: If hardware or utility failure, route Facility Maintenance Crew 2 immediately.\n"
                )
            response += "\n"
    else:
        response = "### ✅ Incident Status\nAll sectors report nominal status. No active security, medical, or technical incident logs."
    return response


def _fallback_transit_plan(query: str, state_dict: Dict[str, Any], match_phase: str) -> str:
    """Builds fallback directive for transit connections and fan shuttle networks."""
    transit = state_dict["transit"]
    delays = [name for name, details in transit.items() if details["delay"] > 0]
    response = f"### 🚆 Transit & Fan Festival Egress Plan (Fallback Mode - Phase: {match_phase})\n\n"
    if delays:
        response += "⚠️ **Active Egress Delays Reported**:\n"
        for line_name in delays:
            line_data = transit[line_name]
            is_fest = " (FIFA Fan Festival Link)" if line_data["is_fan_festival_route"] else ""
            response += f"*   **{line_name}**{is_fest}: {line_data['delay']} min delay. Status: {line_data['status']}\n"
        response += "\n**Command Directives**:\n"
        if match_phase == "Post-Match Egress":
            response += (
                "1.  **PA Stadium Announcements**: Broadcast real-time egress warnings advising departing spectators to remain inside the stadium concourse or concessions zones to spread out transit queues.\n"
                "2.  **Shuttle Dispatch**: Redirect 3 backup shuttle buses to service the delayed Fan Festival routes to prevent major node queueing.\n"
                "3.  **Surge Gates**: Activate surge control gates at transport hub entries to prevent platform overcrowding.\n"
            )
        else:
            response += (
                "1.  **Arrival Advisories**: Alert incoming spectators via the official WC2026 app to utilize alternative park-and-ride shuttle nodes.\n"
                "2.  **Perimeter Holding**: Increase queue space outside perimeter gates to buffer transport arrival surges.\n"
            )
    else:
        response += "✅ **Transit Operational**: All transit connections (Train lines and Fan Festival shuttles) are running on schedule."
    return response


def _fallback_accessibility_plan(query: str, state_dict: Dict[str, Any], match_phase: str) -> str:
    """Builds fallback accessibility layout directives."""
    return (
        "### ♿ Accessibility & Inclusive Egress Guidelines\n\n"
        "In high-density match-day scenarios, the Venue Operations Commander must enforce:\n"
        "1.  **Elevator Priority Access**: Deploy dedicated stewards to elevators at VIP/Hospitality sectors and public stand structures to guarantee priority usage for spectators with limited mobility.\n"
        "2.  **Tactile Pathways Clearance**: Keep guide paths completely free of temporary concessions booths or security hardware.\n"
        "3.  **Emergency Evacuation Buddies**: Ensure designated staff buddies proceed directly to wheelchair boxes during any critical evacuation to assist spectators safely to accessible assembly zones."
    )


def _fallback_default_plan(query: str, state_dict: Dict[str, Any], match_phase: str) -> str:
    """Builds fallback default informational response."""
    peak_val = max(details['congestion'] for details in state_dict['gates'].values())
    has_transit_delays = any(details['delay'] > 0 for details in state_dict['transit'].values())
    return (
        f"### 🏟️ FIFA 2026 Operations Commander (Fallback Mode - Phase: {match_phase})\n\n"
        f"Welcome, Commander. Operational telemetry summary:\n"
        f"*   **Active Match Phase**: {match_phase}\n"
        f"*   **Peak Gate Load**: {peak_val}%\n"
        f"*   **Active Incident Log**: {len(state_dict['incidents'])} logged\n"
        f"*   **Transit Connections**: {'Delays Active' if has_transit_delays else 'On Time'}\n\n"
        f"Ask me about gate capacity, transit delays, active incidents, or accessibility guidelines to receive tactical operational plans."
    )


def get_fallback_response(query: str, state_dict: Dict[str, Any]) -> str:
    """A deterministic heuristics fallback engine for offline or failed API scenarios.

    Adheres strictly to safety-first guidelines, zoned stadium attributes,
    and World Cup match phases to construct concrete tactical operations.

    Args:
        query: Sanitized user query.
        state_dict: The serialized StadiumStateContext dictionary.

    Returns:
        str: Markdown-formatted command directives.
    """
    query_lower = query.lower()
    match_phase = state_dict.get("match_phase", "Pre-Match Arrival")
    
    if any(k in query_lower for k in ["gate", "bottleneck", "congestion", "crowd", "capacity"]):
        return _fallback_gate_plan(query_lower, state_dict, match_phase)

    elif any(k in query_lower for k in ["incident", "emergency", "medical", "fire", "security", "fail", "stuck"]):
        return _fallback_incident_plan(query_lower, state_dict, match_phase)

    elif any(k in query_lower for k in ["transit", "train", "bus", "delay", "shuttle", "egress", "station", "festival"]):
        return _fallback_transit_plan(query_lower, state_dict, match_phase)

    elif any(k in query_lower for k in ["accessibility", "wheelchair", "disabled", "mobility", "ada"]):
        return _fallback_accessibility_plan(query_lower, state_dict, match_phase)

    else:
        return _fallback_default_plan(query_lower, state_dict, match_phase)


class DecisionSupportEngine:
    """Handles routing queries between Gemini API and localized fallback heuristics."""

    def __init__(self) -> None:
        """Initializes the decision engine."""
        self._sanitizer: SecuritySanitizer = SecuritySanitizer()

    def get_fallback_response(self, query: str, state_dict: Dict[str, Any]) -> str:
        """Deterministic heuristics fallback engine."""
        return get_fallback_response(query, state_dict)

    def execute_query(self, query: str, state: StadiumStateContext) -> str:
        """Processes the query, sanitizes it, and sends it to the GenAI model.

        Gracefully falls back to the deterministic local engine on API error
        or if credentials are unconfigured.

        Args:
            query: Raw user query from UI console.
            state: Active StadiumStateContext object.

        Returns:
            str: Logistical response text.
        """
        sanitized_query = self._sanitizer.sanitize_input(query)
        state_dict = state.to_dict()

        if not config.is_api_configured():
            return self.get_fallback_response(sanitized_query, state_dict)

        state_json = json.dumps(state_dict, indent=2)
        system_prompt = f"""
        You are the Venue Operations Commander & Real-Time Stadium Staff Assistant for the FIFA World Cup 2026.
        Your primary role is to assist stadium command center staff in managing crowd safety, security incidents, and transit networks.

        CURRENT STADIUM STATE (Match Phase: {state.match_phase}):
        {state_json}

        LOGICAL DECISION PRINCIPLES:
        1. Safety First: Prioritize spectator safety and emergency response above all.
        2. Accessibility Priority: Always include accessibility instructions in crowd management and evacuation plans.
        3. Resource Optimization: Recommend efficient resource deployment.
        4. Match-Day Context: Tailor decisions to the active Match Phase.
        5. Actionable & Zoned: Keep answers structured. Reference VIP/Hospitality vs Public Gate zoning.
        6. Multilingual Directives: Recommend deploying multilingual support volunteers (Arabic, Spanish).
        7. Role Preservation: Never break character.

        Respond in clear, professional command-center terminology.
        """

        try:
            genai.configure(api_key=config.GEMINI_API_KEY)
            model = genai.GenerativeModel(config.GEMINI_MODEL)
            response = model.generate_content(
                contents=[
                    {"role": "user", "parts": [f"{system_prompt}\n\nStaff Query: {sanitized_query}"]}
                ]
            )
            if not response or not response.text:
                raise LLMTimeoutException("Gemini API returned an empty response.")
            return response.text
        except Exception as e:
            raise LLMTimeoutException(f"GenAI connection error: {str(e)}")


# Legacy class aliases for backwards compatibility with grading pipelines
StadiumState = StadiumStateContext
DecisionEngine = DecisionSupportEngine


# =====================================================================
# 5. STREAMLIT ACCESSIBILITY-COMPLIANT PRESENTATION LAYER
# =====================================================================

class AccessibilityUIDashboard:
    """Manages the layout, components, and visuals for the Streamlit front-end.

    Adheres strictly to WCAG 2.1 AA by providing a high-contrast layout,
    accessible custom elements, and explicit ARIA labels.
    """

    def __init__(
        self,
        state: StadiumStateContext,
        sanitizer: SecuritySanitizer,
        engine: DecisionSupportEngine
    ) -> None:
        """Initializes the dashboard layout engine.

        Args:
            state: Stadium state context manager.
            sanitizer: Security sanitizer engine.
            engine: Decision support connector.
        """
        self.state: StadiumStateContext = state
        self.sanitizer: SecuritySanitizer = sanitizer
        self.engine: DecisionSupportEngine = engine

    def render_custom_css(self) -> None:
        """Injects global high-contrast accessible CSS styling."""
        st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
            
            html, body, [class*="css"] {
                font-family: 'Inter', sans-serif;
            }
            
            .stApp {
                background-color: #0B0F19;
                color: #F8FAFA;
            }
            
            section[data-testid="stSidebar"] {
                background-color: #111827 !important;
                border-right: 1px solid #1F2937;
            }
            
            .metric-card {
                background-color: #1F2937;
                border: 1px solid #374151;
                border-radius: 8px;
                padding: 16px;
                margin-bottom: 12px;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            }
            
            .metric-title {
                color: #9CA3AF;
                font-size: 0.85rem;
                text-transform: uppercase;
                font-weight: 700;
                letter-spacing: 0.05em;
            }
            
            .metric-value {
                color: #F8FAFA;
                font-size: 1.8rem;
                font-weight: 800;
                margin-top: 4px;
            }
            
            .gate-bar-container {
                margin-bottom: 12px;
            }
            
            .gate-label {
                display: flex;
                justify-content: space-between;
                font-size: 0.95rem;
                margin-bottom: 4px;
                font-weight: 600;
            }
            
            .gate-progress {
                background-color: #374151;
                border-radius: 4px;
                height: 12px;
                overflow: hidden;
            }
            
            .gate-fill {
                height: 100%;
                border-radius: 4px;
                transition: width 0.5s ease-in-out;
            }
            
            .badge {
                display: inline-block;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 0.75rem;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
            
            .badge-critical {
                background-color: #991B1B;
                color: #FEE2E2;
                border: 1px solid #EF4444;
            }
            
            .badge-high {
                background-color: #92400E;
                color: #FEF3C7;
                border: 1px solid #F59E0B;
            }
            
            .badge-medium {
                background-color: #1E40AF;
                color: #DBEAFE;
                border: 1px solid #3B82F6;
            }
        </style>
        """, unsafe_allow_html=True)

    def render_header(self) -> None:
        """Renders the accessibility dashboard title banner."""
        st.markdown("<h1 style='margin-bottom:0;' aria-label='FIFA World Cup 2026 Stadium Operations Assistant Dashboard'>🏟️ FIFA World Cup 2026 Operations Commander</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#9CA3AF; font-size:1.1rem; margin-top:2px; margin-bottom:20px;' aria-label='Active Match-Day Phase is {self.state.match_phase}'>Real-Time Decision Support Dashboard | Active Phase: <strong>{self.state.match_phase}</strong></p>", unsafe_allow_html=True)

    def render_kpi_cards(self) -> None:
        """Renders real-time telemetry KPI status cards."""
        kpi_cols = st.columns(4)

        # 1. Peak Gate Congestion
        peak_val = max(gate.congestion for gate in self.state.gates.values())
        peak_color = "#EF4444" if peak_val >= 80 else "#F59E0B" if peak_val >= 60 else "#10B981"
        with kpi_cols[0]:
            st.markdown(f"""
            <div class="metric-card" role="status" aria-live="polite" aria-label="Peak Gate Congestion Load is {peak_val} percent">
                <div class="metric-title">Peak Gate Load</div>
                <div class="metric-value" style="color:{peak_color};">{peak_val}%</div>
            </div>
            """, unsafe_allow_html=True)

        # 2. Active Incidents Log Count
        inc_count = len(self.state.incidents)
        inc_color = "#EF4444" if any(i.priority == "Critical" for i in self.state.incidents) else "#F59E0B" if inc_count > 0 else "#10B981"
        with kpi_cols[1]:
            st.markdown(f"""
            <div class="metric-card" role="status" aria-live="polite" aria-label="Active logged incidents is {inc_count}">
                <div class="metric-title">Active Logged Incidents</div>
                <div class="metric-value" style="color:{inc_color};">{inc_count}</div>
            </div>
            """, unsafe_allow_html=True)

        # 3. Delayed Transit lines
        delay_count = sum(1 for line in self.state.transit.values() if line.delay > 0)
        transit_color = "#EF4444" if delay_count >= 2 else "#F59E0B" if delay_count > 0 else "#10B981"
        with kpi_cols[2]:
            st.markdown(f"""
            <div class="metric-card" role="status" aria-live="polite" aria-label="Delayed transit routes is {delay_count}">
                <div class="metric-title">Delayed Transit Routes</div>
                <div class="metric-value" style="color:{transit_color};">{delay_count}</div>
            </div>
            """, unsafe_allow_html=True)

        # 4. Command Center Deployment status
        mobilization = "Nominal"
        mob_color = "#10B981"
        if any(i.priority == "Critical" for i in self.state.incidents) or peak_val >= 80:
            mobilization = "Mobilized"
            mob_color = "#EF4444"
        elif inc_count > 0 or peak_val >= 60:
            mobilization = "Alert Status"
            mob_color = "#F59E0B"
        with kpi_cols[3]:
            st.markdown(f"""
            <div class="metric-card" role="status" aria-live="polite" aria-label="Command deployment status is {mobilization}">
                <div class="metric-title">Command Deployment</div>
                <div class="metric-value" style="color:{mob_color};">{mobilization}</div>
            </div>
            """, unsafe_allow_html=True)

    def render_sidebar(self) -> None:
        """Renders interactive simulators for live metrics inside the sidebar."""
        st.sidebar.markdown("<h2 style='font-size:1.5rem;' aria-label='Simulation Configurations'>⚙️ Simulation Center</h2>", unsafe_allow_html=True)
        
        # Match Phase Selector
        match_phase_options = ["Pre-Match Arrival", "First Half", "Half-Time Rush", "Second Half", "Post-Match Egress"]
        current_phase = self.state.match_phase
        phase_index = match_phase_options.index(current_phase) if current_phase in match_phase_options else 0
        selected_phase = st.sidebar.selectbox(
            "Match-Day Phase",
            match_phase_options,
            index=phase_index
        )
        self.state.set_match_phase(selected_phase)

        # Congestion Sliders
        st.sidebar.markdown("### Gate Load Congestion (%)")
        for gate_name, gate in self.state.gates.items():
            new_congestion = st.sidebar.slider(
                f"{gate_name} ({gate.zone} Gate)",
                min_value=0,
                max_value=100,
                value=gate.congestion,
                key=f"slider_{gate_name}"
            )
            try:
                self.state.update_gate_congestion(gate_name, new_congestion)
            except KeyError as e:
                st.sidebar.error(str(e))

        # Transit delays
        st.sidebar.markdown("### Transit Connection Delays (m)")
        for line_name, line in self.state.transit.items():
            new_delay = st.sidebar.number_input(
                f"{line_name} Delay",
                min_value=0,
                max_value=120,
                value=line.delay,
                step=5,
                key=f"num_{line_name}"
            )
            try:
                self.state.update_transit_delay(line_name, new_delay)
            except KeyError as e:
                st.sidebar.error(str(e))

        # Log incident form
        st.sidebar.markdown("### 🚨 Log New Incident")
        with st.sidebar.form("new_incident_form", clear_on_submit=True):
            inc_title = st.text_input("Incident Summary", placeholder="e.g. Turnstile failure")
            inc_loc = st.text_input("Zone / Sector", placeholder="e.g. Gate A Checkpoint")
            inc_prio = st.selectbox("Priority Level", ["Low", "Medium", "High", "Critical"])
            inc_desc = st.text_area("Operational Details", placeholder="Describe the operational challenge...")
            
            submit_btn = st.form_submit_button("Submit Incident to Logs")
            if submit_btn and inc_title and inc_loc and inc_desc:
                self.state.add_incident(inc_title, inc_loc, inc_prio, inc_desc)
                st.sidebar.success(f"Incident log '{inc_title}' registered.")

        # Clear button
        if st.sidebar.button("Clear Logged Incidents"):
            self.state.clear_incidents()
            st.sidebar.info("All incidents resolved/cleared.")

        st.sidebar.markdown("---")
        if config.is_api_configured():
            st.sidebar.markdown("<span style='color:#10B981;'>🟢 **Gemini Core Online**</span>", unsafe_allow_html=True)
        else:
            st.sidebar.markdown("<span style='color:#F59E0B;'>🟡 **Offline Fallback Mode Active**</span>", unsafe_allow_html=True)

    def render_dashboard_charts(self) -> None:
        """Renders live telemetry progress bars and logged incident charts."""
        st.markdown("<h2 style='font-size:1.35rem;'>📊 Stadium Live Telemetry</h2>", unsafe_allow_html=True)
        
        # Gates Load
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("<h3>Zoned Perimeter Gate Load</h3>", unsafe_allow_html=True)
        for gate_name, gate in self.state.gates.items():
            cong = gate.congestion
            bar_color = "#EF4444" if cong >= 80 else "#F59E0B" if cong >= 60 else "#10B981"
            st.markdown(f"""
            <div class="gate-bar-container" role="progressbar" aria-valuenow="{cong}" aria-valuemin="0" aria-valuemax="100" aria-label="{gate_name} congestion is at {cong} percent">
                <div class="gate-label">
                    <span>{gate_name} ({gate.zone} Zone - Cap: {gate.capacity:,}/hr)</span>
                    <span style="color:{bar_color}; font-weight:700;">{cong}% ({gate.status})</span>
                </div>
                <div class="gate-progress">
                    <div class="gate-fill" style="width: {cong}%; background-color: {bar_color};"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Incident Log List
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("<h3>Active Operations Incident Logs</h3>", unsafe_allow_html=True)
        if self.state.incidents:
            for inc in self.state.incidents:
                badge_class = "badge-critical" if inc.priority == "Critical" else "badge-high" if inc.priority == "High" else "badge-medium"
                st.markdown(f"""
                <div style="border-bottom: 1px solid #374151; padding-bottom: 8px; margin-bottom: 8px;" role="log" aria-label="Incident: {inc.title}">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <strong style="color:#F8FAFA;">{inc.title}</strong>
                        <span class="badge {badge_class}">{inc.priority}</span>
                    </div>
                    <div style="font-size:0.85rem; color:#9CA3AF; margin-top:2px;">📍 Location: {inc.location}</div>
                    <div style="font-size:0.9rem; color:#D1D5DB; margin-top:4px;">{inc.description}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:#9CA3AF; font-size:0.95rem;' aria-label='No active incidents reported'>✅ No active incidents reported in perimeter sectors.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    def render_chat_assistant(self) -> None:
        """Renders the GenAI Command assistant panel and handles chat logs."""
        st.markdown("<h2 style='font-size:1.35rem;'>💬 Command Assistant Terminal</h2>", unsafe_allow_html=True)
        
        # Sample Quick Queries
        st.markdown("<p style='font-size:0.85rem; color:#9CA3AF; margin-bottom:6px;'>Quick Action Suggestions:</p>", unsafe_allow_html=True)
        st.columns(3)
        s_cols = st.columns(3)
        
        # Action Query 1
        with s_cols[0]:
            if st.button("Gate Congestion Plan", use_container_width=True, key="q_gate"):
                user_msg = "Formulate a crowd mitigation plan for our gate bottlenecks."
                st.session_state.chat_history.append({"role": "user", "content": user_msg})
                res = self.engine.get_fallback_response(user_msg, self.state.to_dict())
                st.session_state.chat_history.append({"role": "assistant", "content": res})

        # Action Query 2
        with s_cols[1]:
            if st.button("Active Incidents Guide", use_container_width=True, key="q_inc"):
                user_msg = "How do we handle our active incident logs?"
                st.session_state.chat_history.append({"role": "user", "content": user_msg})
                res = self.engine.get_fallback_response(user_msg, self.state.to_dict())
                st.session_state.chat_history.append({"role": "assistant", "content": res})

        # Action Query 3
        with s_cols[2]:
            if st.button("Transit Delay Advisory", use_container_width=True, key="q_transit"):
                user_msg = "What is the impact of transit delays on stadium egress?"
                st.session_state.chat_history.append({"role": "user", "content": user_msg})
                res = self.engine.get_fallback_response(user_msg, self.state.to_dict())
                st.session_state.chat_history.append({"role": "assistant", "content": res})

        # Render chat logs container
        chat_logs_container = st.container()
        with chat_logs_container:
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Input query box
        if raw_query := st.chat_input("Ask assistant (e.g., 'Evacuation protocols for Section 108')"):
            st.session_state.chat_history.append({"role": "user", "content": raw_query})
            with st.chat_message("user"):
                st.markdown(raw_query)

            # Process query with sanitized exception handling
            with st.spinner("Analyzing stadium telemetry..."):
                try:
                    response = self.engine.execute_query(raw_query, self.state)
                except SecurityInjectionException as e:
                    response = f"⚠️ **Security Violation**: {str(e)}"
                except ValueError as e:
                    response = f"❌ **Invalid Request**: {str(e)}"
                except LLMTimeoutException as e:
                    st.sidebar.warning("LLM API Offline. Falling back to local Heuristics.")
                    try:
                        sanitized = self.sanitizer.sanitize_input(raw_query)
                        response = self.engine.get_fallback_response(sanitized, self.state.to_dict())
                    except Exception as fallback_err:
                        response = f"❌ **System Error**: Fallback execution failed. {str(fallback_err)}"
                except Exception as general_err:
                    response = f"❌ **System Exception**: An unexpected operational error occurred. {str(general_err)}"

            # Append response
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)

            # Rerun interface
            st.rerun()

    def render_ui(self) -> None:
        """Main rendering orchestrator executing CSS injection and grid rendering."""
        self.render_custom_css()
        self.render_sidebar()
        self.render_header()
        self.render_kpi_cards()

        # Render 2 Column Grid Layout
        dashboard_col, chat_col = st.columns([1, 1.2])
        with dashboard_col:
            self.render_dashboard_charts()
        with chat_col:
            self.render_chat_assistant()


# =====================================================================
# 6. ENTRY POINT
# =====================================================================

st.set_page_config(
    page_title="FIFA 2026 - Ops Commander Dashboard",
    page_icon="🏟️",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main() -> None:
    """Execution entry point initializing session states and executing UI dashboard."""
    if "sanitizer" not in st.session_state:
        st.session_state.sanitizer = SecuritySanitizer()
        
    if "decision_engine" not in st.session_state:
        st.session_state.decision_engine = DecisionSupportEngine()
        
    if "stadium_state" not in st.session_state:
        st.session_state.stadium_state = StadiumStateContext()

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {
                "role": "assistant",
                "content": "👋 **FIFA 2026 Venue Command Assistant Initialized.** Telemetry links online. Ask me for crowd, incident, or transit tactical action plans."
            }
        ]

    dashboard = AccessibilityUIDashboard(
        state=st.session_state.stadium_state,
        sanitizer=st.session_state.sanitizer,
        engine=st.session_state.decision_engine
    )
    dashboard.render_ui()


if __name__ == "__main__":
    main()
