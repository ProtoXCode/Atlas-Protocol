# HEXCOM – Tactical API Layer for Legacy ERP Systems

## Codename Meaning
**HEXCOM** reflects the reality of interfacing with outdated, closed, or undocumented ERP systems via change detection, observation, and state-mapping logic. It pays subtle homage to old-school memory-based debugging tools like Cheat-O-Matic, used to explore and manipulate game states by watching how values change.

This is not an official API.
This is a **reflected interface**, built by watching, probing, and listening.

---

## Objective
To provide a non-invasive method for extracting structured ERP behavior and data by reverse-mapping how values change in the database or UI.

Rather than requesting official access, **HEXCOM observes the system under live use** to infer:
- Field relationships
- Table structure
- ID logic
- Event dependencies

The result is a **shadow API** that mirrors system state in real time.

---

## Use Cases
- Build unofficial read-only APIs for spaghetti ERPs
- Reverse-engineer BOM, routing, stock, or cost data
- Pipe data into modern interfaces (e.g., dashboards, Atlas)
- Validate data drift between systems
- Bypass stale exports and CSV madness

---

## Core Method

### 1. State Monitoring
- Observe system behavior during live usage
- Track known values (e.g., part name, PO number)
- Record before/after deltas on DB, network, or file system

### 2. Field Mapping
- Correlate known inputs with data changes
- Assign readable labels to otherwise unknown fields
- Build a registry of useful hooks (e.g., item_cost, bom_id)

### 3. API Shadow Layer
- Construct logic in your own middleware (e.g., Python + FastAPI)
- Use direct DB reads or replicated data sources
- Provide REST endpoints that reflect ERP behavior:
  ```
  GET /bom/8472
  GET /part/WINDER-3/stock
  GET /orders?due_before=2024-06-01
  ```

---

## Sandbox Mode Strategy
Many ERP systems (e.g., Monitor ERP) support regular sandbox copies of the live database. HEXCOM is most effective when used on these sandbox snapshots:

- Run safe read and write experiments without affecting production
- Simulate value changes and map resulting field updates
- Train your mapping layer over time
- Use daily diffs to detect systemic changes or logic drift

This method provides maximum freedom with zero operational risk.

---

## Ethical Use
HEXCOM is designed to enable modernization when official access is not granted, not to bypass legitimate security or ownership rights. It is recommended to:
- Maintain read-only access
- Avoid writing directly into ERP unless sanctioned
- Log source origins clearly to differentiate mirrored vs. native data

---

## Potential Stack
- **Backend:** FastAPI or Flask for REST layer
- **DB Layer:** psycopg2, pyodbc, or SQLAlchemy direct binds
- **Discovery Tools:** DB trigger logs, UI sniffing, file watchers
- **Optional Frontend:** Dash/Streamlit to verify mappings live

---

## Risks and Considerations
- ERP schema may change silently
- Mapping accuracy depends on user discipline
- High write frequency may slow monitoring tools
- Security policies must be respected

---

## Final Note
HEXCOM is not a product. It's a philosophy: **"If they won't open the door, we'll listen through the wall."**

With HEXCOM, even the most closed ERP becomes a usable data source. Not with access. With observation.