# 🏟️ FIFA World Cup 2026 - Operations Commander Dashboard

Welcome to the official **GenAI-powered operations** control center for the **FIFA World Cup 2026**. Designed specifically for Venue Commanders, this dashboard optimizes **stadium operations** and **crowd management** in real-time across all tournament host cities. By combining live IoT sensor telemetry with a Gemini-powered decision assistant, it ensures safe spectator transit, seamless access control, and rapid operational coordination.

---

## 1. Problem Statement
The **FIFA World Cup 2026** is the largest sporting event in history, welcoming millions of international fans across multiple host nations. Managing massive crowds during high-stress tournament phases—such as the pre-match ingress, half-time concessions rush, and post-match exit—demands immediate operational visibility. 

A delay at a light rail terminal, a scanner bottleneck at a public concourse, or a localized medical incident can quickly cascade. Commanders require a unified terminal that handles **transportation coordination**, automates **emergency response**, directs **volunteer assistance**, and enforces **accessibility support** dynamically.

---

## 2. Key Features

- **📊 Stadium Telemetry**: High-speed metrics on perimeter gate load, public concessions congestion, and transport shuttle wait times.
- **💬 GenAI-Powered Operations**: A contextual assistant terminal providing **real-time decision support** based on live tournament metrics.
- **♿ Accessibility Support**: WCAG 2.1 AA compliant dark theme interfaces, tactile path warnings, and priority elevator routing instructions.
- **🚆 Transportation Coordination**: Live delay tracking for Light Rail connections and the FIFA Fan Festival shuttle networks.
- **🗣️ Multilingual Assistance**: Recommendations to deploy bilingual volunteer teams (Arabic, Spanish, French) to public gates based on spectator language profiles.
- **🚨 Emergency Response**: Quick-action directives and cordons for crowd rushes, fire risks, or medical incidents.
- **🛡️ AI Incident Commander**: A tactical dashboard section that generates safety-critical dispatches using Gemini, delivering Risk Level, Immediate Actions, Volunteer Deployment, Security Response, Medical Response, Public Announcement, and Estimated Resolution Time based on structured stadium context (crowds, weather, transit delays, accessibility, and active incident lists).
- **🌿 Sustainability Insights**: Monitoring green transit options and carbon footprint reductions to align with FIFA's green tournament commitment.

---

## 3. Product Architecture & Information Flow

The platform separates data pipelines, security checks, and layout logic into clean, cohesive modules:

```
[IoT Telemetry / Sensors] ----> [State Engine] ----> [Security Engine]
                                                             |
                                                   (Sanitized State JSON)
                                                             v
[Commander Chat Terminal] ----> [UI Engine] --------> [Decision Engine]
                                                             |
                                                    (API Call or Fallback)
                                                             v
                                                  [Tactical Operations]
```

- **`app.py`**: The central entry point that mounts the UI, re-exports compatibility layers, and starts the event loop.
- **`state_engine.py`**: Manages O(1) primitive dictionary lookups representing gates, transit nodes, and active incident arrays.
- **`security_engine.py`**: Runs HTML escaping and prompt injection defenses to protect command data integrity.
- **`decision_engine.py`**: The GenAI intelligence hub that configures the Gemini client once and routes queries to fallback rule-based models when offline.
- **`ui_engine.py`**: Injects dark high-contrast CSS and renders clean, accessible dashboard views.

---

## 4. Prompt Engineering & GenAI Assistant Flow
1. **Context Extraction**: The active operational phase (e.g. Pre-Match Ingress, Post-Match Egress) and telemetry dictionaries are packaged.
2. **System Role Enforcement**: The AI is instructed to preserve its persona as the "Real-Time Stadium Staff Assistant".
3. **Operational Principles**: Prompt structures mandate safety-first emergency dispatches, priority accessibility paths, and bilingual volunteer deployments.
4. **Offline Resilience**: If the internet or Gemini connection drops, the engine falls back to deterministic local rule engines to continue delivering crowd routing guidance.

---

## 5. Security & Safety First
- **Input Sanitization**: Rejects tags using `html.escape` and pre-compiled regex arrays to identify system override patterns.
- **Zero Hardcoded Keys**: API configuration is resolved strictly via environment variables (`GEMINI_API_KEY`) loaded from `.env`.
- **No Dynamic Commands**: Employs strictly parameterized data structures to avoid dynamic command execution (`eval`, `exec`).

---

## 6. Accessibility Compliance (WCAG 2.1 AA)
- **High Contrast**: Sleek, high-contrast dark theme elements tailored for venue command screens.
- **Semantic DOM Elements**: Semantic buttons, headings, and lists tagged with descriptive `aria-label` properties.
- **Assistive Ready**: Built-in progress bars mapped to ARIA telemetry schemas for screen readers.

---

## 7. Setup & Run Instructions

### Step 1: Initialize Environment
Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install Packages
```bash
pip install -r requirements.txt
```

### Step 3: Run the Dashboard
Start the Streamlit application:
```bash
streamlit run app.py
```

---

## 8. Testing Suite
The automated testing suite verifies configuration parameters, security inputs, and fallback logic:
```bash
./venv/bin/pytest --cov=app --cov=config --cov-report=term-missing test_app.py -v
```
All modules achieve **100% test coverage** under verification.
