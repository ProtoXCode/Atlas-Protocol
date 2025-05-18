# KIEL – Kanban Intent Execution Layer

## Meaning  
**KIEL** is the stabilizing force beneath the Atlas Protocol execution stack — like the **keel of a ship**, it ensures forward momentum is balanced, directed, and aligned with material reality.

---

## Objective  
Provide a real-time interface to prioritize and visualize production tasks based on feasibility.  
Focus on what **can be worked on now**, and clearly flag what **can’t** — with reasons.

---

## Core Logic

### 1. Feasible Work Order List  
- Pull all **active, unfinished orders** from ERP  
- For each order:
  - Check material availability
  - Check upstream dependency status
- If all required conditions are met:
  - Include in **Top 5 Feasible Orders**
- Display format:
  - Row-based view (like Excel)
  - Cells represent required parts or substeps
  - Color codes:
    - Green = ready
    - Yellow = partial
    - Red = warning (e.g. newly blocked)

---

### 2. Unfeasible Work Order List  
- Maintain a **secondary list of 5 orders** that are currently blocked  
- For each:
  - Show exact reason it’s blocked:
    - “Missing Winding Foil 27mm”
    - “Cutting Job #214 incomplete”
    - “Machine X in maintenance”
- Purpose: Transparent tracking of what’s *next up*, once blockers are cleared

---

### 3. Station-Specific Task Queues  
- Each process/machine (e.g., winding) gets:
  - A personal list of Top 5 *feasible* tasks  
- Sourced by:
  - Filtering global list by process type
  - Sorting by due date or priority
- Automatically updates as tasks are completed or become unfeasible

---

### 4. Efficiency Tracker  
- For every completed task:
  - Pull **predetermined time** from ERP routing  
  - Compare with **actual clocked time**
  - Log time difference for performance tracking
- Efficiency data visible to:
  - Operators (per task)
  - Managers (aggregated view)

---

## Interface Layout (MVP)

```
+----------------------------+        +----------------------------+
|   Feasible Work Orders     |        |   Unfeasible Work Orders   |
|   (Top 5 only)             |        |   (Next 5 blocked)         |
|   [ Job #302 ] [parts...]  |        |   [ Job #416 ] [reason...] |
|   [ Job #298 ] [parts...]  |        |   [ Job #317 ] [reason...] |
|            ...             |        |            ...             |
+----------------------------+        +----------------------------+

+-------------------------------------+
|   [Station View: Winder A]          |
|   [ Task #302 ] [Start] [Time est]  |
|   [ Task #298 ] [Blocked]           |
|                ...                  |
+-------------------------------------+

+--------------------+  +---------------------+
| Efficiency Tracker |  | Task Performance DB |
| Time target: 00:43 |  | Actual:     00:47   |
| Status: -4 mins    |  | Logged.             |
+--------------------+  +---------------------+
```

---

## Stack Suggestions (MVP)

- **Backend**: FastAPI + ERP Client for pulling work orders and routing data
- **Frontend**: Dash (for quick MVP) or basic React + Tailwind UI
- **Data**: Local in-memory cache or SQLite for short-term state