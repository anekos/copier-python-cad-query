---
name: cadquery
description: Use when writing, debugging, or reviewing CadQuery code — Python parametric 3D CAD scripts using Workplane/Sketch/Assembly, exporting STEP/STL/DXF/AMF, or when errors mention cadquery, cq, OCP, or OCCT.
---

# CadQuery

Python parametric CAD library on the OCCT kernel. Generated against **cadquery 2.8.0**. All lengths are **mm**, angles are **degrees**.

## Projects

CadQuery projects live under `~/forge/cad/CadQuery/{name}/` as uv-managed src-layout
packages with a click CLI (`uv run {name} build` exports to `dist/`). When creating or
working in a project, follow `references/project-template.md` exactly: model code is a
pydantic `Param` + pure `build(param) -> Workplane` in `main.py`; CLI wiring via
`click_cadquery.define_options` in `__init__.py`.

For throwaway experiments outside a project:

```bash
uv venv --python 3.13 .venv && uv pip install --python .venv/bin/python cadquery
```

(Known-good: Python 3.12/3.13. Newest CPython may lack OCP wheels.)

## Mental model (read before writing code)

- `Workplane` is a **fluent chain over a stack** of objects (points, wires, solids) plus a *context solid*. 2D ops (`rect`, `circle`, `moveTo`…) draw pending wires **at each point on the stack**; 3D ops (`extrude`, `cutBlind`…) consume pending wires and combine into the context solid (`combine=True` is the default; pass `combine=False` to get a separate solid).
- Sketch on a face: `.faces(">Z").workplane()`. The new plane's origin is the **projection of the previous origin** onto that face (`centerOption="ProjectedOrigin"` default) — NOT the face center. Use `centerOption="CenterOfMass"` or `"CenterOfBoundBox"` when you want the face center; a vertex selected right after the face becomes the origin with `CenterOfMass`.
- Pattern of features: draw construction geometry, select its vertices, then apply a hole/circle at every point: `.rect(w, h, forConstruction=True).vertices().cboreHole(...)`. Also `pushPoints([...])`, `rarray(xs, ys, nx, ny)`, `polarArray(radius, startAngle, angle, count)`.
- Reuse earlier state with tags: `.tag("base")` … `.workplaneFromTagged("base")`, or `.faces(">X", tag="base")`.

## String selectors

Used by `faces() / edges() / vertices() / solids()`:

| Selector | Meaning |
|---|---|
| `>Z` / `<Z` | furthest / nearest in Z (`>Z[n]`: nth from far end, `>Z[-2]`: second furthest) |
| `+Z`, `-Z` | facing that direction |
| `\|Z` / `#Z` | parallel / perpendicular to Z |
| `%Plane`, `%Cylinder`, `%CIRCLE`, `%LINE` | by geometry type |
| `and`, `or`, `not`, `exc`, `(...)` | combinators, e.g. `">>X[2] and (not \|Z)"` |

## Pitfalls (verified on 2.8.0)

- `shell(-t)` hollows **inward**; pre-selected faces are removed (`.faces(">Z").shell(-2)` → open top). Positive `t` grows outward.
- `hole(d)` drills **through everything** by default; give `depth=` for blind holes. Depth is measured from the workplane.
- Multiple fillets: order matters. Fillet vertical edges (`edges("|Z")`) before top/bottom perimeters (`edges("#Z")`) or OCCT may fail/produce junk.
- `box(..., centered=...)` accepts a bool or a per-axis 3-tuple, e.g. `centered=(True, True, False)` to sit on Z=0.
- `Sketch` ops take `mode=`: `"a"` add, `"s"` subtract, `"i"` intersect, `"c"` construction (+`tag=`). Selections persist — call `.reset()` before selecting a different feature set. `Sketch.parray(r, a1, da, n)` = radius, start angle, sweep, count; `da=360` with `n=6` does not duplicate 0°/360°.
- `Sketch.slot(w, h)`: `w` is the straight-segment length, `h` the width — **overall length is `w + h`** (verified: `slot(5.8, 4.2)` → bbox 10.0 × 4.2). For a 10 mm overall slot of width 4.2, use `slot(5.8, 4.2)`.
- `fillet()`/`chamfer()` apply to the currently selected edges (e.g. after `.faces(">Z").edges()`); with no edge selection they apply to all edges of the selected faces.
- `Assembly.save()` is **deprecated** (FutureWarning) — use `assy.export("out.step")`. Count solids via `assy.toCompound().Solids()`.
- `Assembly.add(obj, loc=cq.Location((x, y, z)), name=..., color=cq.Color("red"))`; `Location` also takes `(pnt, axis, angle)`.
- Interrogate results: `w.val()` → underlying Shape; `shape.Volume()`, `shape.BoundingBox()` → `.xlen/.ylen/.zlen`; `w.solids().vals()` lists solids.
- `show_object()` only exists inside CQ-editor. In plain scripts, export instead.
- Export: `w.export("part.step")` or `cq.exporters.export(w, "part.stl")` — format inferred from extension (STEP/STL/DXF/SVG/AMF/3MF/…). DXF export of a section: `cq.exporters.export(w.section(), "s.dxf")`.
- `extrude()`/`cutBlind()` accept `"next"`/`"last"` or a `Face` as the until-argument, and `both=True`, `taper=`.

## Validation loop (do this every time)

1. Write the model as a plain script; end with `export` plus printed evidence:
   ```python
   solid = result.val()
   print(f"volume={solid.Volume():.1f} bbox={solid.BoundingBox().xlen:.1f}x"
         f"{solid.BoundingBox().ylen:.1f}x{solid.BoundingBox().zlen:.1f}")
   result.export("part.step")
   ```
2. Run it. An exception from OCP/OCCT usually means invalid geometry for that op (e.g. fillet radius too large, self-intersecting shell) — adjust parameters, don't retry blindly.
3. Check printed volume/bbox against a rough hand estimate before declaring success.
4. Or run `scripts/validate.py model.py` (same interpreter) — it re-imports exported STEP files and fails on empty/broken output.

## References (load on demand)

- `references/project-template.md` — REQUIRED when creating a new project or editing an existing one: directory layout, pyproject/Makefile/CLI templates, setup commands.
- `references/api-workplane.md` — every `Workplane` method signature + one-line doc; selector classes; exporters/importers.
- `references/api-sketch-assembly.md` — `Sketch`, `Assembly`, `Location`/`Vector`/`Plane`, free-function API (`cadquery.func`).
- `references/examples.md` — ~45 official examples (Workplane, Sketch, Assembly constraints, free functions). Check here first; most tasks are a variation of one of these.

References are auto-generated: after a cadquery upgrade, rerun
`python scripts/gen_api_reference.py references/` with the project interpreter.
