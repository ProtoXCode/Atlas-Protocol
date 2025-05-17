# 🧭 ATLAS PROTOCOL – BUILD LOGBOOK

This is the living logbook for the construction of the Atlas Protocol.
It documents the ideas, breakthroughs, and phases of development from inception.

---

### 📅 2024-04-30 – The Atlas Idea is Born
- Started working with the idea to automate parts using Python.
- Since all data is known of entire item, why not automate all of it?
- Initial concept: What if we started from **design intent**, not geometry?

---

### 📅 2024-05-01 – Core System Mapped
- Sketched the modular architecture of Atlas:
  - Titan – Master logic resolver
  - Keystone – Constraint manager
  - Relay – Comms and transport
- Recognized that design intent is **compressible**.
- Identified need for custom logic encoder.

---

### 📅 2024-05-02 – Caladan Named and Framed
- Caladan defined as the planetary-scale runtime state engine.
- Introduced ripple-based constraint propagation as a living environment concept.
- Logic-first twins enter scope: machines, assemblies, data flows.

---

### 📅 2024-05-04 – Mini AI path
- AI logic, purpose built AI's with logic layer. AI → Logic/Intent → AI.

---

### 📅 2024-05-03–04 – Keystone ideas
- Defined how constraints flow between subsystems.
- The idea of **co-design across teams and geos** becomes native.
- Potential massive resource reduction in Atlas, potato compatible?

---

### 📅 2024-05-05 – Project planning
- Concepted viewer GUI, must choose demo item:
  - Transformer (Time consuming, but very straight forward)
  - Door (Simple and easy, boring though)
  - Donkey Cart?

---

### 📅 2024-05-06 – Too many new ideas / BHC side project
- Oppurtunity to look at a possibility to compress STEP files.
  - Created full folder structure for BHC repo.
  - Built `compress_to_atlas()` and wired it into CLI and API.
    - Must finish compressor. Let's hope it works, it's *unusual*.
  - Implemented Transfer Portal: Upload STEP → Get .atlas
  - STL Resurrection concept locked in.
  - Built `.atlas` file structure + hash verification spec.
  - Viewer concept scoped: show logic is real, not black box magic.
  - Might look at other file types for same compression if successful.
- STL to STEP conversion possibility. Will look into later.
- Realized that there could be missing data on some of the blueprints, need to check and update.
- Estimated dev time from a 4-5 dev team 9-12 months down to 6-8 weeks solo for core MVP due to keystone blueprints, impressive.

---

### 📅 2024-05-07 – That's a lot of text | Too many ideas
- **Spatial logic breakthrough:***
  - Anchor-based placement replace CAD constraints.
  - Thread-safe, loopable part generation - order no longer matters.
  - Simplified geometry, placement and part constructions.
- Archive recovery operation:
  - Recovered and cleaned **36 new blueprint fragments***.
  - Merged and categorized for future drops.
- Blueprint upgrades:
  - Gauntlet → v2.0.
    - v1.0 archived.
  - Caladan → v1.1 *(clarity pass, same logic)*.
     - v1.0 archived
  - New: **examples_intent_logic**
- Mapped out the logic layer and experience core for an editor.

---

### 📅 2024-05-11 – Project concept almost complete
- **Project progress: (Concept is 90%-ish done)**
  - GUI layout and function flow.
  - Viewer interaction model.
  - Part module logic.
  - Export pipelines.
- Updated docs:
  - LICENSE: Updated to v1.1. Refined commercial use part.
  - README: Fixed link to license.
- First *code*:
  - main.py with layout.
  - Added requirements.txt.

---

### 📅 2024-05-12 – GUI work
- Added another row, dropdown selector for models.
- Long days at work this week at the factory due to Lean/5S corse. 12h days.

---

### 📅 2024-05-17 – Folder restructure
- Moved blueprints into docs folder.
  - Legacy_blueprints into blueprints.
- New folder: idea_oasis - Where misc ideas is added:
  - Added idea for memory management by reversing the file.

---

This log will be continuously updated as Atlas expands.
