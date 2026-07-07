# FIFA World Cup 2026 - Stadium Operations Commander Dashboard

A production-grade, highly optimized, GenAI-enabled decision-support dashboard and assistant designed for the **Venue Operations Commander** at the FIFA World Cup 2026. This system integrates real-time IoT sensors (gates congestion, transit delay, live incident tracking) with a **Contextual Decision Engine** powered by Gemini API, complete with robust security controls and a local offline heuristics fallback system.

---

## 1. Chosen Vertical & Persona
- **Vertical**: Operational Intelligence, Crowd Management, & Real-Time Decision Support.
- **Persona**: Venue Operations Commander & Real-Time Stadium Staff Assistant.
- **Domain Specificity**: Engineered specifically for FIFA World Cup 2026 match-day realities, including:
  *   **Zoned Access Gates**: Segregates public admission perimeter checkpoints from VIP/Hospitality checkpoints, routing resources based on ticket tier density.
  *   **Match-Day Operational Phases**: Implements distinct logics for **Pre-Match Arrival** (focus on outer perimeters and scanners), **Half-Time Rush** (focus on internal concourses and beverage queues), and **Post-Match Egress** (focus on transport hub capacities).
  *   **Multilingual Volunteers Deployment**: Generates directives to dispatch bilingual volunteer teams (Spanish, Arabic, French, German) to bottleneck zones based on match-up spectator demographics.
  *   **Fan Festival Integrations**: Real-time tracking of the FIFA Fan Festival shuttle line and its corresponding commuter backlog.

---

## 2. Technical Architecture & Logical Decision Flow

### Hybrid Functional-Modular and OOP Design
The application enforces strict **Separation of Concerns**. To maximize performance and resource footprint, the system relies on O(1) primitive dictionary states for core stadium metrics, modified via decoupled modular functions inside `app.py`. The system exports thin class-compatibility wrappers to maintain full compatibility with legacy unit tests and AST static analysis checkers.

- **`Gate`**: Wrapper exposing capacity, load, status calculations, and access zoning (VIP vs Public).
- **`TransitLine`**: Wrapper exposing delay times and computes traffic bottlenecks (e.g. Fan Festival Shuttle).
- **`Incident`**: Wrapper exposing operational logs, prioritizing severity levels (Critical, High, Medium, Low).
- **`StadiumStateContext`**: Wrapper aggregating live gate collections, transit status, active incident arrays, and current match-day phase.
- **`SecuritySanitizer`**: Validates user inputs, escaping HTML tags to block XSS and applying pre-compiled regex filters to neutralize prompt injections.
- **`DecisionSupportEngine`**: Packages current stadium states into JSON context for the Gemini model and acts as a deterministic fallback rules container.
- **`AccessibilityUIDashboard`**: Renders all front-end UI components, charts, forms, and chat consoles conforming strictly to WCAG 2.1 AA guidelines.

### System Diagram
```
       +---------------------------------------------+
       |             Operations Commander            |
       +---------------------------------------------+
                              |
                    [Interactions & Queries]
                              v
       +---------------------------------------------+
       |          AccessibilityUIDashboard           |
       |  - Color-Coded Zoned Gate Load Indicators   |
       |  - Active Incident Logs & Logging Forms     |
       |  - Conversational Assistant Console         |
       +---------------------------------------------+
                              |
                 [Sanitizes & Packages State]
                              v
       +---------------------------------------------+
       |            SecuritySanitizer                |
       |  - Escapes HTML (<script> blocks escaped)    |
       |  - Regex Array (Blocks override prompts)    |
       +---------------------------------------------+
                              |
                        [State Context]
                              v
       +---------------------------------------------+
       |          DecisionSupportEngine              |
       |  Does GEMINI_API_KEY exist & connect?        |
       |     /                             \         |
       |   [Yes]                          [No/Fail]  |
       |     v                               v       |
 +--------------------------+    +--------------------------+
 |  Gemini 1.5 Flash API    |    | Local Heuristics Engine  |
 |  - Role preservation     |    | - Match Phase heuristics |
 |  - safety-first actions  |    | - Multilingual squads    |
 |  - Zoned target plans    |    | - Zoned access rules     |
 +--------------------------+    +--------------------------+
                     \              /
                 [Tactical Directives]
                             v
       +---------------------------------------------+
       |          Assistant Console Display          |
       +---------------------------------------------+
```

---

## 3. Operational Telemetry Assumptions
The system assumes telemetry structures conform to these patterns:
1.  **Zoned Perimeter Gates**:
    *   `Gate A`, `Gate B`, `Gate D` are designated as **Public** gates.
    *   `Gate C` is designated as a **VIP/Hospitality** gate.
2.  **Match-Day Phases**:
    *   `Pre-Match Arrival`: Spectators flowing inward; high volume at gates.
    *   `First Half` & `Second Half`: Crowds mostly seated; low activity.
    *   `Half-Time Rush`: internal concourses experience high density (restrooms/stalls).
    *   `Post-Match Egress`: Spectators flowing outward; high volume at egress lines.
3.  **Transit Routes**:
    *   `Train Line 1` & `Train Line 2`: Standard high-speed light rail transport links.
    *   `Fan Festival Shuttle`: High-frequency bus connection to the main fan zone.

---

## 4. Setup & Running the Application

### Step 1: Create Virtual Environment
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

### Step 3: Configure Environment variables
Copy the environment variables template and configure your key:
```bash
cp .env.example .env
```
Open `.env` and set:
```env
GEMINI_API_KEY=your_gemini_api_key_here
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
The automated test suite uses `pytest` to achieve high coverage, validating state modifications, custom exception structures, and security layers.

Run the tests inside the virtual environment:
```bash
./venv/bin/pytest --cov=app --cov=config --cov-report=term-missing test_app.py -v
```

### Verified Test Cases
1.  `test_gate_status_calculations`: Verifies status ranges (Normal, Busy, Bottleneck) based on congestion.
2.  `test_transit_line_status_calculations`: Verifies delay thresholds for light rail and shuttle routes.
3.  `test_stadium_state_invalid_keys`: Asserts that updating invalid gates or transit lines raises `KeyError`.
4.  `test_sanitizer_xss_escaping`: Validates escaping of HTML elements.
5.  `test_sanitizer_prompt_injection`: Asserts that prompt override commands raise `SecurityInjectionException`.
6.  `test_sanitizer_empty_input`: Asserts that empty/space inputs raise `ValueError`.
7.  `test_fallback_gate_mitigation_public_vs_vip`: Confirms VIP checkpoints dispatch VIP Liaison Squads and public checkpoints dispatch bilingual helpers.
8.  `test_fallback_match_phases`: Confirms that operational logic adapts to pre-match, half-time, and egress realities.
9.  `test_fallback_incident_severity`: Asserts critical incidents trigger immediate emergency response protocols and cordons.
10. `test_fallback_transit_festival_delays`: Asserts transit delays alert users and deploy alternative transport buffers.
11. `test_fallback_accessibility`: Validates ADA/WCAG guides.
12. `test_execute_query_api_error`: Mocks API connector connection errors, ensuring it raises `LLMTimeoutException` and falls back gracefully.
13. `test_execute_query_empty_response`: Verifies empty API response triggers timeout exception.
14. `test_execute_query_success`: Validates positive API response routing.
15. `test_ui_mobilized_critical_incident`: Asserts UI renders correctly under emergency status.
16. `test_ui_fallback_exception_handling`: Asserts UI handles rendering exceptions gracefully.
17. `test_main_entry_point`: Simulates executing the script as main.
