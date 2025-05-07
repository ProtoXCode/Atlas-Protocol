# Atlas Protocol – Intent Logic Examples

## Purpose
This blueprint provides hands-on examples for how to define parts and systems using Atlas-style intent logic. These are not geometry-first definitions — they are logical declarations of *purpose*, *constraints*, and *function*, which Atlas then compiles into geometry and BOMs.

This is where new users learn how to speak the language of intent.

---

## 🟦 Example 1: Door Panel (Industrial Equipment Access)

### Goal
Create a hinged steel door panel for a control cabinet, mounted to the right side, with cutout for handle and required fastener clearance.

```yaml
intent:
  name: control_cabinet_door
  function: access_panel
  material: steel_sheet_1.5mm
  location:
    mount_to: cabinet_right_face
    offset: (x=10mm, y=0mm)
  dimensions:
    width: 400mm
    height: 600mm
    tolerance: ±0.5mm
  constraints:
    - hinge_side: left
    - open_angle: 120_deg
    - include_cutout:
        type: handle
        position: center_right
    - maintain_clearance:
        around: door_perimeter
        min_gap: 2mm
  fasteners:
    - type: M6_bolt
      count: 4
      spacing: equal_vertical
      access_method: wrench
```

Atlas will:
- Generate a panel geometry with hinge zones
- Apply fastener hole patterns and clearance checks
- Simulate wrench tool access
- Flag opening collision if needed

---

## 🟫 Example 2: Donkey Cart (Legacy Import + Intent Wrap)

### Goal
Define a legacy wooden cart with basic structural logic, and retrofit duckfat-based damping as a temporary innovation.

```yaml
intent:
  name: BZ_donkey_cart_v1
  function: human_transport
  legacy_geometry: ./donkey_cart_legacy.stp
  constraints:
    - payload_capacity: 120kg
    - terrain_profile: gravel
    - wheelbase: approx_950mm
    - materials:
        frame: salvaged_wood
        fasteners: iron_nails
  modifications:
    - suspension_upgrade:
        method: fat_damped_cloth_sling
        medium: duckfat
        coverage_zone: seat_underframe
        note: \"melts above 30°C\"
  test:
    run_street_validation: true
    gait_unit: Donkey_v2
    target_speed: 3.5km/h
```

Atlas will:
- Import legacy mesh and tag primary subassemblies
- Apply modifier logic to flag melted duckfat as thermal failure risk
- Estimate dynamic load response using donkey gait simulator
- Recommend substitution from Caladan if duckfat is unavailable

---

## 🔧 Example 3: Winding Coil (Production Twin Generator)

### Goal
Declare a low-voltage transformer coil with automated turn calculation and layer spacing based on power spec.

```yaml
intent:
  name: LV_coil_3ph
  function: electromagnetic_induction
  coil_specs:
    wire_type: Cu_flat
    current: 120A
    target_voltage: 400V
    max_loss: 2%
  constraints:
    - core_window: (w=100mm, h=160mm)
    - insulation_thickness: 2mm
    - tap_count: 5
    - cooling_margin: 4mm around
  production:
    generate_winding_program: true
    output: .gcode / .json / workcard.pdf
```

Atlas will:
- Calculate turn count, spacing, and max winding height
- Verify window fit and apply insulation logic
- Create machine-ready winding file
- Attach it to production BOM with QA traceability

---

## Final Thought
Intent logic isn’t programming — it’s storytelling with constraints. These examples teach Atlas how to *reason before it renders.*
More examples? Drop them into `samples/intent_library/` and let the twin grow smarter.



# Atlas Protocol – Intent Logic Examples

## Purpose
This blueprint provides hands-on examples for how to define parts and systems using Atlas-style intent logic. These are not geometry-first definitions — they are logical declarations of *purpose*, *constraints*, and *function*, which Atlas then compiles into geometry and BOMs.

This is where new users learn how to speak the language of intent.

---

## 🟦 Example 1: Door Panel (Industrial Equipment Access)

### Goal
Create a hinged steel door panel for a control cabinet, mounted to the right side, with cutout for handle and required fastener clearance.

```yaml
intent:
  name: control_cabinet_door
  function: access_panel
  material: steel_sheet_1.5mm
  location:
    mount_to: cabinet_right_face
    offset: (x=10mm, y=0mm)
  dimensions:
    width: 400mm
    height: 600mm
    tolerance: ±0.5mm
  constraints:
    - hinge_side: left
    - open_angle: 120_deg
    - include_cutout:
        type: handle
        position: center_right
    - maintain_clearance:
        around: door_perimeter
        min_gap: 2mm
  fasteners:
    - type: M6_bolt
      count: 4
      spacing: equal_vertical
      access_method: wrench
```

Atlas will:
- Generate a panel geometry with hinge zones
- Apply fastener hole patterns and clearance checks
- Simulate wrench tool access
- Flag opening collision if needed

---

## 🟫 Example 2: Donkey Cart (Legacy Import + Intent Wrap)

### Goal
Define a legacy wooden cart with basic structural logic, and retrofit duckfat-based damping as a temporary innovation.

```yaml
intent:
  name: BZ_donkey_cart_v1
  function: human_transport
  legacy_geometry: ./donkey_cart_legacy.stp
  constraints:
    - payload_capacity: 120kg
    - terrain_profile: gravel
    - wheelbase: approx_950mm
    - materials:
        frame: salvaged_wood
        fasteners: iron_nails
  modifications:
    - suspension_upgrade:
        method: fat_damped_cloth_sling
        medium: duckfat
        coverage_zone: seat_underframe
        note: "melts above 30°C"
  test:
    run_street_validation: true
    gait_unit: Donkey_v2
    target_speed: 3.5km/h
```

Atlas will:
- Import legacy mesh and tag primary subassemblies
- Apply modifier logic to flag melted duckfat as thermal failure risk
- Estimate dynamic load response using donkey gait simulator
- Recommend substitution from Caladan if duckfat is unavailable

---

## 🔧 Example 3: Winding Coil (Production Twin Generator)

### Goal
Declare a low-voltage transformer coil with automated turn calculation and layer spacing based on power spec.

```yaml
intent:
  name: LV_coil_3ph
  function: electromagnetic_induction
  coil_specs:
    wire_type: Cu_flat
    current: 120A
    target_voltage: 400V
    max_loss: 2%
  constraints:
    - core_window: (w=100mm, h=160mm)
    - insulation_thickness: 2mm
    - tap_count: 5
    - cooling_margin: 4mm around
  production:
    generate_winding_program: true
    output: .gcode / .json / workcard.pdf
```

Atlas will:
- Calculate turn count, spacing, and max winding height
- Verify window fit and apply insulation logic
- Create machine-ready winding file
- Attach it to production BOM with QA traceability

---

## Final Thought
Intent logic isn’t programming — it’s storytelling with constraints. These examples teach Atlas how to *reason before it renders.*