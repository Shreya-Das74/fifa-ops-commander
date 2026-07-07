"""
FIFA World Cup 2026 - Stadium Operations Command Assistant
An enterprise-grade, functional-modular, real-time command dashboard and GenAI assistant.
Enforces strict typing, detailed Google docstrings, custom exceptions, and WCAG accessibility.
"""

from typing import Dict, List, Any
import streamlit as st
import google.generativeai as genai

# Import modular blocks
from config import config, FIFAOpsException, ConfigurationException, SecurityInjectionException, LLMTimeoutException
from state_engine import Gate, TransitLine, Incident, StadiumStateContext, init_stadium_state
from security_engine import SecuritySanitizer, sanitize_input
from decision_engine import DecisionSupportEngine, get_fallback_response
from ui_engine import AccessibilityUIDashboard

# Legacy compatibility exports for test compatibility
StadiumState = StadiumStateContext
DecisionEngine = DecisionSupportEngine


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
