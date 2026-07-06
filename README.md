# FIFA World Cup 2026 - Stadium Operations Commander & Assistant

A production-grade, highly optimized, GenAI-enabled decision-support dashboard and assistant designed for the **Venue Operations Commander** at the FIFA World Cup 2026. This system integrates real-time IoT sensors (gates congestion, transit delay, live incident tracking) with a **Contextual Decision Engine** powered by Gemini API, complete with robust security controls and a local offline heuristics fallback system.

---

## 1. Chosen Vertical & Persona
- **Vertical**: Operational Intelligence, Crowd Management, & Real-Time Decision Support.
- **Persona**: Venue Operations Commander & Real-Time Stadium Staff Assistant.
- **Role & Logic**: The system acts as the digital co-pilot in the Stadium Command Center. It continuously ingests simulated stream feeds (crowd flow at gates, rail system delays, medical/security logs) and translates them into context-aware, safety-first mitigation actions for stadium staff, specifically focusing on spectator safety and WCAG accessibility standards.

---

## 2. Technical Architecture & Logical Decision Flow

### High-Contrast Web Dashboard & Core Engine
Built using **Python** and **Streamlit** to achieve a lightweight footprint (<1MB repository size) while providing a high-contrast, fully responsive dashboard.

```
       +---------------------------------------------+
       |           Venue Command Staff               |
       +---------------------------------------------+
                              |
                     [Interactions / Query]
                              v
       +---------------------------------------------+
       |            Streamlit Web Interface          |
       |  - High-Contrast CSS Theme (WCAG Compliant) |
       |  - Live Metrics Telemetry Sliders           |
       |  - Incident Entry Form & Logger             |
       +---------------------------------------------+
                              |
                    [Packages State & Query]
                              v
       +---------------------------------------------+
       |        Security & Sanitization Layer        |
       |  - HTML Escaper (XSS Protection)            |
       |  - Regex injection scanner (Neutralizer)   |
       +---------------------------------------------+
                              |
               [Sanitized Context + Prompt]
                              v
       +---------------------------------------------+
       |         Contextual Decision Engine          |
       |  Does GEMINI_API_KEY exist?                 |
       |     /                             \         |
       |   [Yes]                          [No/Fail]  |
       |     v                               v       |
+--------------------------+    +--------------------------+
|  Gemini 1.5 Flash API    |    | Local Heuristics Engine  |
|  - Role preservation     |    | - Deterministic Rules    |
|  - Safety / Accessibility|    | - WCAG/ADA Fallback Plan |
+--------------------------+    +--------------------------+
                     \              /
                  [Command Directives]
                             v
       +---------------------------------------------+
       |             Dashboard Display               |
       +---------------------------------------------+
```

### Security & Sanitization Architecture
- **XSS Mitigation**: The query input sanitization uses `html.escape` to neutralize JavaScript tag injection.
- **Prompt Injection Defense**: Detects phrases like `Ignore previous instructions` or `system override` and dynamically replaces them with `[Instruction Override Blocked by Security Protocol]`.
- **API Guard**: Reads API keys from environment configurations. If keys are missing, the system warns the commander and shifts to local heuristics instead of crashing.

---

## 3. Telemetry Assumptions (Simulated Inputs)
The application operates on the following simulated data structures:
1. **Gates Data**: Capacity, live percentage loads, and status labels (Normal, Busy, Bottleneck).
2. **Transit Data**: Scheduled routes, active delay minutes, and status indicators.
3. **Active Incidents Feed**: Security, logistics, and medical situations logged by roaming stewards, each labeled with a priority (Low, Medium, High, Critical) and location.

---

## 4. Setup & Running the Application

### Prerequisites
- Python 3.9, 3.10, or 3.11 installed.

### Step 1: Clone and Set Up Directory
Create a virtual environment inside the `fifa-ops-commander` directory:
```bash
# Navigate to the workspace directory
cd fifa-ops-commander

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Copy the `.env.example` to `.env` and enter your Gemini API Key:
```bash
cp .env.example .env
```
Open `.env` and set:
```env
GEMINI_API_KEY=your_actual_gemini_api_key
```
*Note: If no API key is specified, the application will run in **Offline Fallback Heuristics Mode**, which contains complete rule-based response logic and remains 100% testable and operational.*

### Step 4: Run the Application
Start the Streamlit application:
```bash
streamlit run app.py
```
This will spin up a local server (typically at `http://localhost:8501`).

---

## 5. Running the Test Suite
The automated test suite validates the security sanitization layer, configuration, and the fallback heuristics decision engine.

Run the tests using `pytest`:
```bash
pytest test_app.py -v
```
All unit tests should pass, ensuring the codebase is robust, secure, and ready for production command centers.
