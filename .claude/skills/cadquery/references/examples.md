# CadQuery examples

Curated from the official docs (doc/examples.rst, sketch.rst, assy.rst, free-func.rst).
All lengths are in mm. `result` / `show_object()` conventions come from CQ-editor;
in plain scripts, export instead (see SKILL.md).

## Workplane (fluent API)

### Plate with Hole

```python
# The dimensions of the box. These can be modified rather than changing the
# object's code directly.
length = 80.0
height = 60.0
thickness = 10.0
center_hole_dia = 22.0

# Create a box based on the dimensions above and add a 22mm center hole
result = (
    cq.Workplane("XY")
    .box(length, height, thickness)
    .faces(">Z")
    .workplane()
    .hole(center_hole_dia)
)
```

### An extruded prismatic solid

```python
result = cq.Workplane("front").circle(2.0).rect(0.5, 0.75).extrude(0.5)
```

### Building Profiles using lines and arcs

```python
result = (
    cq.Workplane("front")
    .lineTo(2.0, 0)
    .lineTo(2.0, 1.0)
    .threePointArc((1.0, 1.5), (0.0, 1.0))
    .close()
    .extrude(0.25)
)
```

### Moving The Current working point

```python
result = cq.Workplane("front").circle(
    3.0
)  # current point is the center of the circle, at (0, 0)
result = result.center(1.5, 0.0).rect(0.5, 0.5)  # new work center is (1.5, 0.0)

result = result.center(-1.5, 1.5).circle(0.25)  # new work center is (0.0, 1.5).
# The new center is specified relative to the previous center, not global coordinates!

result = result.extrude(0.25)
```

### Polygons

```python
result = (
    cq.Workplane("front")
    .box(3.0, 4.0, 0.25)
    .pushPoints([(0, 0.75), (0, -0.75)])
    .polygon(6, 1.0)
    .cutThruAll()
)
```

### Polylines

```python
(L, H, W, t) = (100.0, 20.0, 20.0, 1.0)
pts = [
    (0, H / 2.0),
    (W / 2.0, H / 2.0),
    (W / 2.0, (H / 2.0 - t)),
    (t / 2.0, (H / 2.0 - t)),
    (t / 2.0, (t - H / 2.0)),
    (W / 2.0, (t - H / 2.0)),
    (W / 2.0, H / -2.0),
    (0, H / -2.0),
]
result = cq.Workplane("front").polyline(pts).mirrorY().extrude(L)
```

### Defining an Edge with a Spline

```python
s = cq.Workplane("XY")
sPnts = [
    (2.75, 1.5),
    (2.5, 1.75),
    (2.0, 1.5),
    (1.5, 1.0),
    (1.0, 1.25),
    (0.5, 1.0),
    (0, 1.0),
]
r = s.lineTo(3.0, 0).lineTo(3.0, 1.0).spline(sPnts, includeCurrent=True).close()
result = r.extrude(0.5)
```

### Mirroring From Faces

```python
result = cq.Workplane("XY").line(0, 1).line(1, 0).line(0, -0.5).close().extrude(1)

result = result.mirror(result.faces(">X"), union=True)
```

### Creating Workplanes on Faces

```python
result = cq.Workplane("front").box(2, 3, 0.5)  # make a basic prism
result = (
    result.faces(">Z").workplane().hole(0.5)
)  # find the top-most face and make a hole
```

### Locating a Workplane on a vertex

```python
result = cq.Workplane("front").box(3, 2, 0.5)  # make a basic prism
result = (
    result.faces(">Z").vertices("<XY").workplane(centerOption="CenterOfMass")
)  # select the lower left vertex and make a workplane
result = result.circle(1.0).cutThruAll()  # cut the corner out
```

### Offset Workplanes

```python
result = cq.Workplane("front").box(3, 2, 0.5)  # make a basic prism
result = result.faces("<X").workplane(
    offset=0.75
)  # workplane is offset from the object surface
result = result.circle(1.0).extrude(0.5)  # disc
```

### Copying Workplanes

```python
result = (
    cq.Workplane("front")
    .circle(1)
    .extrude(10)  # make a cylinder
    # We want to make a second cylinder perpendicular to the first,
    # but we have no face to base the workplane off
    .copyWorkplane(
        # create a temporary object with the required workplane
        cq.Workplane("right", origin=(-5, 0, 0))
    )
    .circle(1)
    .extrude(10)
)
```

### Rotated Workplanes

```python
result = (
    cq.Workplane("front")
    .box(4.0, 4.0, 0.25)
    .faces(">Z")
    .workplane()
    .transformed(offset=cq.Vector(0, -1.5, 1.0), rotate=cq.Vector(60, 0, 0))
    .rect(1.5, 1.5, forConstruction=True)
    .vertices()
    .hole(0.25)
)
```

### Using construction Geometry

```python
result = (
    cq.Workplane("front")
    .box(2, 2, 0.5)
    .faces(">Z")
    .workplane()
    .rect(1.5, 1.5, forConstruction=True)
    .vertices()
    .hole(0.125)
)
```

### Shelling To Create Thin features

```python
result = cq.Workplane("front").box(2, 2, 2).shell(-0.1)
```

### Shelling To Create Thin features

```python
result = cq.Workplane("front").box(2, 2, 2).faces("+Z").shell(0.1)
```

### Making Lofts

```python
result = (
    cq.Workplane("front")
    .box(4.0, 4.0, 0.25)
    .faces(">Z")
    .circle(1.5)
    .workplane(offset=3.0)
    .rect(0.75, 0.5)
    .loft(combine=True)
)
```

### Extruding until a given face

```python
result = (
    cq.Workplane(origin=(20, 0, 0))
    .circle(2)
    .revolve(180, (-20, 0, 0), (-20, -1, 0))
    .center(-20, 0)
    .workplane()
    .rect(20, 4)
    .extrude("next")
)
```

### Making Counter-bored and Counter-sunk Holes

```python
result = (
    cq.Workplane(cq.Plane.XY())
    .box(4, 2, 0.5)
    .faces(">Z")
    .workplane()
    .rect(3.5, 1.5, forConstruction=True)
    .vertices()
    .cboreHole(0.125, 0.25, 0.125, depth=None)
)
```

### Offsetting wires in 2D

```python
result = (
    cq.Workplane()
    .box(4, 2, 0.5)
    .faces(">Z")
    .edges()
    .toPending()
    .offset2D(-0.25, forConstruction=True)
    .vertices()
    .cboreHole(0.125, 0.25, 0.125, depth=None)
)
```

### Rounding Corners with Fillet

```python
result = cq.Workplane("XY").box(3, 3, 0.5).edges("|Z").fillet(0.125)
```

### Tagging objects

```python
result = (
    cq.Workplane("XY")
    # create and tag the base workplane
    .box(10, 10, 10)
    .faces(">Z")
    .workplane()
    .tag("baseplane")
    # extrude a cylinder
    .center(-3, 0)
    .circle(1)
    .extrude(3)
    # to reselect the base workplane, simply
    .workplaneFromTagged("baseplane")
    # extrude a second cylinder
    .center(3, 0)
    .circle(1)
    .extrude(2)
)
```

### Tagging objects

```python
result = (
    cq.Workplane("XY")
    # create a triangular prism and tag it
    .polygon(3, 5)
    .extrude(4)
    .tag("prism")
    # create a sphere that obscures the prism
    .sphere(10)
    # create features based on the prism's faces
    .faces("<X", tag="prism")
    .workplane()
    .circle(1)
    .cutThruAll()
    .faces(">X", tag="prism")
    .faces(">Y")
    .workplane()
    .circle(1)
    .cutThruAll()
)
```

### A Parametric Bearing Pillow Block

```python
(length, height, bearing_diam, thickness, padding) = (30.0, 40.0, 22.0, 10.0, 8.0)

result = (
    cq.Workplane("XY")
    .box(length, height, thickness)
    .faces(">Z")
    .workplane()
    .hole(bearing_diam)
    .faces(">Z")
    .workplane()
    .rect(length - padding, height - padding, forConstruction=True)
    .vertices()
    .cboreHole(2.4, 4.4, 2.1)
)
```

### Splitting an Object

```python
c = cq.Workplane("XY").box(1, 1, 1).faces(">Z").workplane().circle(0.25).cutThruAll()

# now cut it in half sideways
result = c.faces(">Y").workplane(-0.5).split(keepTop=True)
```

### The Classic OCC Bottle

```python
(L, w, t) = (20.0, 6.0, 3.0)
s = cq.Workplane("XY")

# Draw half the profile of the bottle and extrude it
p = (
    s.center(-L / 2.0, 0)
    .vLine(w / 2.0)
    .threePointArc((L / 2.0, w / 2.0 + t), (L, w / 2.0))
    .vLine(-w / 2.0)
    .mirrorX()
    .extrude(30.0, True)
)

# Make the neck
p = p.faces(">Z").workplane(centerOption="CenterOfMass").circle(3.0).extrude(2.0, True)

# Make a shell
result = p.faces(">Z").shell(0.3)
```

### A Parametric Enclosure

```python
# parameter definitions
p_outerWidth = 100.0  # Outer width of box enclosure
p_outerLength = 150.0  # Outer length of box enclosure
p_outerHeight = 50.0  # Outer height of box enclosure

p_thickness = 3.0  # Thickness of the box walls
p_sideRadius = 10.0  # Radius for the curves around the sides of the box
p_topAndBottomRadius = (
    2.0  # Radius for the curves on the top and bottom edges of the box
)

p_screwpostInset = 12.0  # How far in from the edges the screw posts should be place.
p_screwpostID = 4.0  # Inner Diameter of the screw post holes, should be roughly screw diameter not including threads
p_screwpostOD = 10.0  # Outer Diameter of the screw posts.\nDetermines overall thickness of the posts

p_boreDiameter = 8.0  # Diameter of the counterbore hole, if any
p_boreDepth = 1.0  # Depth of the counterbore hole, if
p_countersinkDiameter = 0.0  # Outer diameter of countersink. Should roughly match the outer diameter of the screw head
p_countersinkAngle = 90.0  # Countersink angle (complete angle between opposite sides, not from center to one side)
p_flipLid = True  # Whether to place the lid with the top facing down or not.
p_lipHeight = 1.0  # Height of lip on the underside of the lid.\nSits inside the box body for a snug fit.

# outer shell
oshell = (
    cq.Workplane("XY")
    .rect(p_outerWidth, p_outerLength)
    .extrude(p_outerHeight + p_lipHeight)
)

# weird geometry happens if we make the fillets in the wrong order
if p_sideRadius > p_topAndBottomRadius:
    oshell = oshell.edges("|Z").fillet(p_sideRadius)
    oshell = oshell.edges("#Z").fillet(p_topAndBottomRadius)
else:
    oshell = oshell.edges("#Z").fillet(p_topAndBottomRadius)
    oshell = oshell.edges("|Z").fillet(p_sideRadius)

# inner shell
ishell = (
    oshell.faces("<Z")
    .workplane(p_thickness, True)
    .rect((p_outerWidth - 2.0 * p_thickness), (p_outerLength - 2.0 * p_thickness))
    .extrude(
        (p_outerHeight - 2.0 * p_thickness), False
    )  # set combine false to produce just the new boss
)
ishell = ishell.edges("|Z").fillet(p_sideRadius - p_thickness)

# make the box outer box
box = oshell.cut(ishell)

# make the screw posts
POSTWIDTH = p_outerWidth - 2.0 * p_screwpostInset
POSTLENGTH = p_outerLength - 2.0 * p_screwpostInset

box = (
    box.faces(">Z")
    .workplane(-p_thickness)
    .rect(POSTWIDTH, POSTLENGTH, forConstruction=True)
    .vertices()
    .circle(p_screwpostOD / 2.0)
    .circle(p_screwpostID / 2.0)
    .extrude(-1.0 * (p_outerHeight + p_lipHeight - p_thickness), True)
)

# split lid into top and bottom parts
(lid, bottom) = (
    box.faces(">Z")
    .workplane(-p_thickness - p_lipHeight)
    .split(keepTop=True, keepBottom=True)
    .all()
)  # splits into two solids

# translate the lid, and subtract the bottom from it to produce the lid inset
lowerLid = lid.translate((0, 0, -p_lipHeight))
cutlip = lowerLid.cut(bottom).translate(
    (p_outerWidth + p_thickness, 0, p_thickness - p_outerHeight + p_lipHeight)
)

# compute centers for screw holes
topOfLidCenters = (
    cutlip.faces(">Z")
    .workplane(centerOption="CenterOfMass")
    .rect(POSTWIDTH, POSTLENGTH, forConstruction=True)
    .vertices()
)

# add holes of the desired type
if p_boreDiameter > 0 and p_boreDepth > 0:
    topOfLid = topOfLidCenters.cboreHole(
        p_screwpostID, p_boreDiameter, p_boreDepth, 2.0 * p_thickness
    )
elif p_countersinkDiameter > 0 and p_countersinkAngle > 0:
    topOfLid = topOfLidCenters.cskHole(
        p_screwpostID, p_countersinkDiameter, p_countersinkAngle, 2.0 * p_thickness
    )
else:
    topOfLid = topOfLidCenters.hole(p_screwpostID, 2.0 * p_thickness)

# flip lid upside down if desired
if p_flipLid:
    topOfLid = topOfLid.rotateAboutCenter((1, 0, 0), 180)

# return the combined result
result = topOfLid.union(bottom)
```

### Lego Brick

```python
#####
# Inputs
######
lbumps = 6  # number of bumps long
wbumps = 2  # number of bumps wide
thin = True  # True for thin, False for thick

#
# Lego Brick Constants-- these make a Lego brick a Lego :)
#
pitch = 8.0
clearance = 0.1
bumpDiam = 4.8
bumpHeight = 1.8
if thin:
    height = 3.2
else:
    height = 9.6

t = (pitch - (2 * clearance) - bumpDiam) / 2.0
postDiam = pitch - t  # works out to 6.5
total_length = lbumps * pitch - 2.0 * clearance
total_width = wbumps * pitch - 2.0 * clearance

# make the base
s = cq.Workplane("XY").box(total_length, total_width, height)

# shell inwards not outwards
s = s.faces("<Z").shell(-1.0 * t)

# make the bumps on the top
s = (
    s.faces(">Z")
    .workplane()
    .rarray(pitch, pitch, lbumps, wbumps, True)
    .circle(bumpDiam / 2.0)
    .extrude(bumpHeight)
)

# add posts on the bottom. posts are different diameter depending on geometry
# solid studs for 1 bump, tubes for multiple, none for 1x1
tmp = s.faces("<Z").workplane(invert=True)

if lbumps > 1 and wbumps > 1:
    tmp = (
        tmp.rarray(pitch, pitch, lbumps - 1, wbumps - 1, center=True)
        .circle(postDiam / 2.0)
        .circle(bumpDiam / 2.0)
        .extrude(height - t)
    )
elif lbumps > 1:
    tmp = (
        tmp.rarray(pitch, pitch, lbumps - 1, 1, center=True)
        .circle(t)
        .extrude(height - t)
    )
elif wbumps > 1:
    tmp = (
        tmp.rarray(pitch, pitch, 1, wbumps - 1, center=True)
        .circle(t)
        .extrude(height - t)
    )
else:
    tmp = s
```

### Cycloidal gear

```python
import cadquery as cq
from math import sin, cos, pi, floor


# define the generating function
def hypocycloid(t, r1, r2):
    return (
        (r1 - r2) * cos(t) + r2 * cos(r1 / r2 * t - t),
        (r1 - r2) * sin(t) + r2 * sin(-(r1 / r2 * t - t)),
    )


def epicycloid(t, r1, r2):
    return (
        (r1 + r2) * cos(t) - r2 * cos(r1 / r2 * t + t),
        (r1 + r2) * sin(t) - r2 * sin(r1 / r2 * t + t),
    )


def gear(t, r1=4, r2=1):
    if (-1) ** (1 + floor(t / 2 / pi * (r1 / r2))) < 0:
        return epicycloid(t, r1, r2)
    else:
        return hypocycloid(t, r1, r2)


# create the gear profile and extrude it
result = (
    cq.Workplane("XY")
    .parametricCurve(lambda t: gear(t * 2 * pi, 6, 1))
    .twistExtrude(15, 90)
    .faces(">Z")
    .workplane()
    .circle(2)
    .cutThruAll()
)
```

## Sketch API

### Face-based API

```python
import cadquery as cq

result = (
    cq.Sketch()
    .trapezoid(4, 3, 90)
    .vertices()
    .circle(0.5, mode="s")
    .reset()
    .vertices()
    .fillet(0.25)
    .reset()
    .rarray(0.6, 1, 5, 1)
    .slot(1.5, 0.4, mode="s", angle=90)
)
```

### Modes

```python
result = (
    cq.Sketch()
    .rect(1, 2, mode="c", tag="base")
    .vertices(tag="base")
    .circle(0.7)
    .reset()
    .edges("|Y", tag="base")
    .ellipse(1.2, 1, mode="i")
    .reset()
    .rect(2, 2, mode="i")
    .clean()
)
```

### Edge-based API

```python
import cadquery as cq

result = (
    cq.Sketch()
    .segment((0.0, 0), (0.0, 2.0))
    .segment((2.0, 0))
    .close()
    .arc((0.6, 0.6), 0.4, 0.0, 360.0)
    .assemble(tag="face")
    .edges("%LINE", tag="face")
    .vertices()
    .chamfer(0.2)
)
```

### Convex hull

```python
result = (
    cq.Sketch()
    .arc((0, 0), 1.0, 0.0, 360.0)
    .arc((1, 1.5), 0.5, 0.0, 360.0)
    .segment((0.0, 2), (-1, 3.0))
    .hull()
)
```

### Constraint-based sketches

```python
import cadquery as cq

result = (
    cq.Sketch()
    .segment((0, 0), (0, 3.0), "s1")
    .arc((0.0, 3.0), (1.5, 1.5), (0.0, 0.0), "a1")
    .constrain("s1", "Fixed", None)
    .constrain("s1", "a1", "Coincident", None)
    .constrain("a1", "s1", "Coincident", None)
    .constrain("s1", "a1", "Angle", 45)
    .solve()
    .assemble()
)
```

### Sketches in-place

```python
import cadquery as cq

result = (
    cq.Workplane()
    .box(5, 5, 1)
    .faces(">Z")
    .sketch()
    .regularPolygon(2, 3, tag="outer")
    .regularPolygon(1.5, 3, mode="s")
    .vertices(tag="outer")
    .fillet(0.2)
    .finalize()
    .extrude(0.5)
)
```

### Placing an existing sketch on a workplane

```python
import cadquery as cq

s = cq.Sketch().trapezoid(3, 1, 110).vertices().fillet(0.2)

result = (
    cq.Workplane()
    .box(5, 5, 5)
    .faces(">X")
    .workplane()
    .transformed((0, 0, -90))
    .placeSketch(s)
    .cutThruAll()
)
```

### Sketches spanning multiple elements

```python
import cadquery as cq

result = (
    cq.Workplane()
    .box(5, 5, 1)
    .faces(">Z")
    .workplane()
    .rarray(2, 2, 2, 2)
    .rect(1.5, 1.5)
    .extrude(0.5)
    .faces(">Z")
    .sketch()
    .circle(0.4)
    .wires()
    .distribute(6)
    .circle(0.1, mode="a")
    .clean()
    .finalize()
    .cutBlind(-0.5, taper=10)
)
```

### Lofting between two sketches

```python
from cadquery import Workplane, Sketch, Vector, Location

s1 = Sketch().trapezoid(3, 1, 110).vertices().fillet(0.2)

s2 = Sketch().rect(2, 1).vertices().fillet(0.2)

result = Workplane().placeSketch(s1, s2.moved(z=3)).loft()
```

### Combining sketches

```python
import cadquery as cq

s1 = cq.Sketch().rect(2, 2)
s2 = cq.Sketch().circle(0.5)

result = s1.face(s2, mode='s')
```

### Combining sketches

```python
import cadquery as cq

s1 = cq.Sketch().rect(2, 2).vertices().fillet(0.25).reset()
s2 = cq.Sketch().rect(1, 1, angle=45).vertices().chamfer(0.1).reset()

result = s1 - s2
```

### Offsets made easy

```python
import cadquery as cq

sketch  = (cq.Sketch()
.rect(1.0, 4.0)
.circle(1.0)
.clean()
)

sketch_offset = sketch.copy().wires().offset(0.25)

result = cq.Workplane("front").placeSketch(sketch_offset).extrude(1.0)
result = result.faces(">Z").workplane().placeSketch(sketch).cutBlind(-0.50)
```

### Offsets made easy

```python
import cadquery as cq

sketch  = (cq.Sketch()
.rect(1.0, 4.0)
.circle(1.0)
.clean()
)

sketch_offset = sketch.copy().wires().offset(-0.25, mode='r')

result = cq.Workplane("front").placeSketch(sketch).extrude(1.0)
result = result.faces(">Z").workplane().placeSketch(sketch_offset).cutBlind(-0.50)
```

## Assembly API

### Object locations

```python
import cadquery as cq

cone = cq.Solid.makeCone(1, 0, 2)

assy = cq.Assembly()
assy.add(
    cone,
    loc=cq.Location((0, 0, 0), (1, 0, 0), 180),
    name="cone0",
    color=cq.Color("green"),
)
assy.add(cone, name="cone1", color=cq.Color("blue"))

show_object(assy)
```

### Axis

```python
import cadquery as cq

plate = cq.Workplane().box(10, 10, 1).faces(">Z").workplane().hole(2)
cone = cq.Solid.makeCone(0.8, 0, 4)

assy = cq.Assembly()
assy.add(plate, name="plate", color=cq.Color("green"))
assy.add(cone, name="cone", color=cq.Color("blue"))
# place the center of the flat face of the cone in the center of the upper face of the plate
assy.constrain("plate@faces@>Z", "cone@faces@<Z", "Point")

# set both the flat face of the cone and the upper face of the plate to point in the same direction
assy.constrain("plate@faces@>Z", "cone@faces@<Z", "Axis", param=0)

assy.solve()
show_object(assy)
```

### PointInPlane

```python
import cadquery as cq

# Create an L-shaped object:
bracket = (
    cq.Workplane("YZ")
    .hLine(1)
    .vLine(0.1)
    .hLineTo(0.2)
    .vLineTo(1)
    .hLineTo(0)
    .close()
    .extrude(1)
    # tag some faces for easy reference:
    .faces(">Y[1]")
    .tag("inner_vert")
    .end()
    .faces(">Z[1]")
    .tag("inner_horiz")
    .end()
)

box = cq.Workplane().box(0.5, 0.5, 0.5)

assy = cq.Assembly()
assy.add(bracket, name="bracket", color=cq.Color("gray"))
assy.add(box, name="box", color=cq.Color("green"))

# lock bracket orientation:
assy.constrain("bracket@faces@>Z", "box@faces@>Z", "Axis", param=0)
assy.constrain("bracket@faces@>X", "box@faces@>X", "Axis", param=0)

# constrain the bottom of the box to be on the plane defined by inner_horiz:
assy.constrain("box@faces@<Z", "bracket?inner_horiz", "PointInPlane")
# constrain the side of the box to be 0.2 units from the plane defined by inner_vert
assy.constrain("box@faces@<Y", "bracket?inner_vert", "PointInPlane", param=0.2)
# constrain the end of the box to be 0.1 units inside the end of the bracket
assy.constrain("box@faces@>X", "bracket@faces@>X", "PointInPlane", param=-0.1)

assy.solve()
show_object(assy)
```

### PointOnLine

```python
import cadquery as cq

b1 = cq.Workplane().box(1, 1, 1)
b2 = cq.Workplane().sphere(0.15)

assy = (
    cq.Assembly()
    .add(b1, name="b1")
    .add(b2, loc=cq.Location((0, 0, 4)), name="b2", color=cq.Color("red"))
)

# fix the position of b1
assy.constrain("b1", "Fixed")
# b2 on one of the edges of b1
assy.constrain("b2", "b1@edges@>>Z and >>Y", "PointOnLine")
# b2 on another of the edges of b1
assy.constrain("b2", "b1@edges@>>Z and >>X", "PointOnLine")
# effectively b2 will be constrained to be on the intersection of the two edges

assy.solve()
show_object(assy)
```

### FixedPoint

```python
import cadquery as cq

b1 = cq.Workplane().box(1, 1, 1)
b2 = cq.Workplane().sphere(0.15)

assy = (
    cq.Assembly()
    .add(b1, name="b1")
    .add(b2, loc=cq.Location((0, 0, 4)), name="b2", color=cq.Color("red"))
    .add(b1, loc=cq.Location((-2, 0, 0)), name="b3", color=cq.Color("red"))
)

pnt = (0.5, 0.5, 0.5)

# fix the position of b1
assy.constrain("b1", "Fixed")
# fix b2 center at point
assy.constrain("b2", "FixedPoint", pnt)
# fix b3 vertex position at point
assy.constrain("b3@vertices@<X and <Y and <Z", "FixedPoint", pnt)

assy.solve()
show_object(assy)
```

### Data export

```python
door.export("door.step")
door.export("door.xml")
```

## Free function API (cadquery.func)

### Tutorial

```python
from cadquery.func import *

dh = 2
r = 1

# construct edges
edge1 = circle(r)
edge2 = circle(1.5*r).moved(z=dh)
edge3 = circle(r).moved(z=1.5*dh)

# loft the side face
side = loft(edge1, edge2, edge3)

# bottom face
bottom = fill(side.edges('<Z'))

# top face with continuous curvature
top = cap(side.edges('>Z'), side, [(0,0,1.6*dh)])

# assemble into a solid
s = solid(side, bottom, top)

# construct the final result
result = s.moved((-3*r, 0, 0), (3*r, 0, 0))
```

### Primitives

```python
from cadquery.func import *

e = segment((0,0), (0,1))

c = circle(1)

f = plane(1, 1.5)

b = box(1, 1, 1)

result = compound(e, c.move(2), f.move(4), b.move(6))
```

### Boolean operations

```python
from cadquery.func import *

c1 = cylinder(1, 2)
c2 = cylinder(0.5, 3)

f1 = plane(2, 2).move(z=1)
f2 = plane(1, 1).move(z=1)

e1 = segment((0,-2.5, 1), (0,2.5,1))

# union
r1 = c2 + c1
r2 = fuse(f1, f2)

# difference
r3 = c1 - c2
r4 = cut(f1, f2)

# intersection
r5 = c1*c2
r6 = intersect(f1, f2)

# splitting
r7 = (c1 / f1).solids('<Z')
r8 = split(f2, e1).faces('<X')

results = (r1, r2, r3, r4, r5, r6, r7, r8)
result = compound([el.moved(2*i) for i,el in enumerate(results)])
```
