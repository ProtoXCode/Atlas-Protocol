# Atlas Protocol – Geometry Constraint Primitives

## Purpose
This document outlines the base-level geometric logic that governs part placement, alignment, and assembly relationships in Atlas. These primitives form the spatial grammar of the system — enabling high-level design intent to be compiled into deterministic physical arrangements.

While intuitive to experienced designers and engineers, these constraints represent a shift from static modeling to programmable relationships.

---

## Constraint Types

### 1. Anchor
> *Place this part relative to another fixed reference.*
```yaml
constraint:
  anchor_to: base_plate
  at_face: bottom
  offset: (x=20mm, y=0mm, z=5mm)
```

### 2. Align
> *Line up features across parts or geometry.*
```yaml
constraint:
  align: 
    this: hole[1].center
    with: plate[0].hole[0].center
    axis: x
```

### 3. Mate / Stack
> *Establish surface-to-surface contact, flush or opposed.*
```yaml
constraint:
  mate_faces:
    this: back_face
    with: housing.front_face
    type: flush
```

### 4. Hole-to-Hole Lock
> *Define a bolt or pin relationship between parts.*
```yaml
constraint:
  bolt_path:
    origin: partA.hole[2]
    target: partB.hole[2]
    diameter: 8mm
    tolerance: ±0.1mm
```

### 5. Clearance
> *Prevent collision with defined spatial gaps.*
```yaml
constraint:
  keep_clearance:
    from: fan_blade
    to: housing_inner_wall
    min_gap: 3mm
```

### 6. Symmetry
> *Mirror geometry relative to an axis or center part.*
```yaml
constraint:
  symmetric_about: axis_y
  with: left_bracket
```

### 7. Fit / Insert / Interference
> *Define insertion logic with tolerance control.*
```yaml
constraint:
  insert:
    part: dowel_pin
    into: shaft
    fit: press_fit
    tolerance: H7/g6
```

### 8. Follow Path
> *Route geometry along a defined path or curve.*
```yaml
constraint:
  follow_path:
    geometry: wire_bundle
    path: routing_curve
    max_bend_radius: 15mm
```

---

## How These Are Used in Atlas
- Interpreted by the **Generator** to build geometry
- Evaluated by **BOMBE** for ripple compliance
- Integrated by **Enigma** into the versioned constraint tree
- Validated against physical simulation (e.g., stress, tool access)

---

## Example: Bolt-Constrained Flange
```yaml
part: Flange_A
constraint:
  align_with: Flange_B
  at: bolt_hole[0]
  match_pattern: bolt_circle
  enforce_torque_access: true
```
This logic:
- Aligns bolt circles
- Mates faces
- Injects fastener envelope
- Flags torque spec and access requirements

---

## Final Note
These primitives are the alphabet of Atlas assembly logic. When encoded properly, they allow for full assemblies to be generated, simulated, and resolved without ever needing traditional CAD intervention. This is how Atlas moves geometry into the realm of logic.
