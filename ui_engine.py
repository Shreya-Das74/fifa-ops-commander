"""
FIFA World Cup 2026 - Stadium Operations UI Engine
Injects accessibility-compliant custom styles and renders dashboard layouts.
"""

import streamlit as st
from state_engine import StadiumStateContext
from security_engine import SecuritySanitizer
from decision_engine import DecisionSupportEngine
from config import config, SecurityInjectionException, LLMTimeoutException

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

    def render_incident_commander(self) -> None:
        """Renders the AI Incident Commander section in the UI command terminal."""
        st.markdown("<h2 style='font-size:1.35rem;'>🚨 AI Incident Commander</h2>", unsafe_allow_html=True)
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.9rem; color:#9CA3AF;'>Generate instant tactical dispatches, public announcements, and security controls for active logs.</p>", unsafe_allow_html=True)
        
        incidents = self.state.incidents
        inc_options = [f"{inc.incident_id}: {inc.title} ({inc.location})" for inc in incidents]
        inc_options.append("Custom Situation...")
        
        selected_option = st.selectbox(
            "Select Target Incident / Sector",
            inc_options,
            key="ic_select"
        )
        
        custom_situation = ""
        if selected_option == "Custom Situation...":
            custom_situation = st.text_area(
                "Describe Custom Incident / Situation",
                placeholder="e.g. VIP parking entrance gate jam due to motorcade delay...",
                key="ic_custom"
            )
            
        if st.button("Generate Tactical Directives", use_container_width=True, key="ic_generate"):
            # Prepare incident state payload
            incident_data = {}
            if selected_option == "Custom Situation...":
                if not custom_situation.strip():
                    st.error("Please describe the custom situation.")
                    return
                # Sanitize the input to prevent injection
                try:
                    clean_desc = self.sanitizer.sanitize_input(custom_situation)
                except Exception as e:
                    st.error(str(e))
                    return
                incident_data = {
                    "id": "custom",
                    "title": "Custom Operational Situation",
                    "location": "Venue Area",
                    "priority": "High",
                    "description": clean_desc,
                    "status": "Active"
                }
            else:
                inc_id = selected_option.split(":")[0]
                incident_obj = next((i for i in incidents if i.incident_id == inc_id), None)
                if incident_obj:
                    incident_data = incident_obj.to_dict()
            
            with st.spinner("Formulating incident response..."):
                plan = self.engine.generate_incident_commander_plan(incident_data, self.state)
                st.session_state.ic_plan = plan
                st.rerun()
                
        if "ic_plan" in st.session_state and st.session_state.ic_plan:
            st.markdown("---")
            st.markdown("### 📋 Formulated Tactical Plan")
            st.markdown(st.session_state.ic_plan)
            if st.button("Dismiss Directives", key="ic_dismiss"):
                st.session_state.ic_plan = ""
                st.rerun()
                
        st.markdown("</div>", unsafe_allow_html=True)

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
            self.render_incident_commander()
