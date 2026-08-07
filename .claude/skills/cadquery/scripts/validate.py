"""Run a CadQuery script and sanity-check what it exported.

Usage: python validate.py MODEL_SCRIPT.py

Runs the script with this interpreter (which must have cadquery installed),
then re-imports every STEP file the script wrote and reports solid count,
volume and bounding box. Exits non-zero if the script fails, exports nothing,
or a STEP file contains no solid.
"""

import runpy
import sys
import time
from pathlib import Path
from typing import cast


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    script = Path(sys.argv[1]).resolve()

    start = time.time()
    try:
        runpy.run_path(str(script), run_name="__main__")
    except Exception:
        import traceback

        traceback.print_exc()
        print("VALIDATE: FAIL (script raised)")
        return 1

    # files written by the script (in its directory or cwd)
    produced = [
        p
        for d in {script.parent, Path.cwd()}
        for p in d.iterdir()
        if p.suffix.lower() in {".step", ".stp", ".stl", ".dxf", ".svg", ".3mf"}
        and p.stat().st_mtime >= start - 1
    ]
    if not produced:
        print("VALIDATE: FAIL (script ran but exported no CAD files)")
        return 1

    from cadquery import Shape, importers

    ok = True
    for p in sorted(set(produced)):
        if p.suffix.lower() in {".step", ".stp"}:
            shape = importers.importStep(str(p))
            solids = cast("list[Shape]", shape.solids().vals())
            if not solids:
                print(f"{p.name}: NO SOLIDS — broken export")
                ok = False
                continue
            total = sum(s.Volume() for s in solids)
            bb = cast("Shape", shape.val()).BoundingBox()
            print(
                f"{p.name}: {len(solids)} solid(s), volume {total:.3f} mm^3, "
                f"bbox {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f} mm"
            )
        else:
            size = p.stat().st_size
            print(f"{p.name}: {size} bytes")
            if size == 0:
                ok = False
    print("VALIDATE: OK" if ok else "VALIDATE: FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
