"""
FIFA World Cup 2026 - Stadium Operations Decision Engine
Routes decisions to Gemini API or runs deterministic offline fallback heuristics.
"""

import json
from typing import Dict, Any, Optional
import google.generativeai as genai
from config import config, LLMTimeoutException
from state_engine import StadiumStateContext
from security_engine import SecuritySanitizer

# Localized offline fallbacks
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
        self._model: Optional[genai.GenerativeModel] = None
        self._configured: bool = False

        # Attempt to configure Gemini once
        if config.is_api_configured():
            try:
                genai.configure(api_key=config.GEMINI_API_KEY)
                self._model = genai.GenerativeModel(config.GEMINI_MODEL)
                self._configured = True
            except Exception:
                self._model = None
                self._configured = False

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

        # Lazy configuration if not configured in init
        if not self._configured or self._model is None:
            try:
                genai.configure(api_key=config.GEMINI_API_KEY)
                self._model = genai.GenerativeModel(config.GEMINI_MODEL)
                self._configured = True
            except Exception as e:
                raise LLMTimeoutException(f"GenAI connection error: {str(e)}")

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
            response = self._model.generate_content(
                contents=[
                    {"role": "user", "parts": [f"{system_prompt}\n\nStaff Query: {sanitized_query}"]}
                ]
            )
            if not response or not response.text:
                raise LLMTimeoutException("Gemini API returned an empty response.")
            return response.text
        except Exception as e:
            if isinstance(e, LLMTimeoutException):
                raise e
            raise LLMTimeoutException(f"GenAI connection error: {str(e)}")
