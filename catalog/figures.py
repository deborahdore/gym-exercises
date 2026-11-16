# Draws the exercise illustrations in catalog/images (480 px transparent PNGs).
# Run from the repository root:  python3 catalog/figures.py
# Angles: 0 = down, 90 = the way the figure faces (right), 180 = up, -90 = behind.
#
# Every exercise is drawn twice: once faded, at the other end of the movement, and once solid.
# M(a, b) picks a for the faded pass and b for the solid one; mark() follows a point through
# both passes and an arrow is drawn between its two positions, in the direction of the effort.
# The muscles named in mus= are tinted on the solid figure.
import math
import os
from PIL import Image, ImageDraw

S, N = 8, 240
BODY, BACK = (51, 65, 85, 255), (148, 163, 184, 255)
ACC, FRAME, HALO = (37, 99, 235, 255), (147, 197, 253, 255), (241, 245, 249, 255)
MUS, ARROW, FADED = (249, 115, 22, 255), (5, 150, 105, 255), (100, 116, 139, 255)
FY = 205  # height of the ankle when the foot is on the floor
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
im = d = None
GHOST = False
MARKS, ARROWS, CENTER = ({}, {}), [], (120, 120)


def M(a, b):
    return a if GHOST else b


def v(a, l):
    return (l * math.sin(math.radians(a)), l * math.cos(math.radians(a)))


def add(p, q):
    return (p[0] + q[0], p[1] + q[1])


def sub(p, q):
    return (p[0] - q[0], p[1] - q[1])


def lerp(p, q, t):
    return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)


def ang(p, q):  # angle of the segment p -> q, in the convention above
    return math.degrees(math.atan2(q[0] - p[0], q[1] - p[1]))


def tone(col):  # the faded pass has no outlines and no muscles, and a single body colour
    if not GHOST:
        return col
    if col in (HALO, MUS):
        return None
    return FADED if col in (BODY, BACK) else col


def line(pts, w, col):
    col = tone(col)
    if col is None:
        return
    pts = [(x * S, y * S) for x, y in pts]
    d.line(pts, fill=col, width=int(w * S))
    for x, y in pts:
        r = w * S / 2
        d.ellipse((x - r, y - r, x + r, y + r), fill=col)


def dot(p, r, col):
    col = tone(col)
    if col is not None:
        d.ellipse(((p[0] - r) * S, (p[1] - r) * S, (p[0] + r) * S, (p[1] + r) * S), fill=col)


def poly(pts, col):
    col = tone(col)
    if col is not None:
        d.polygon([(x * S, y * S) for x, y in pts], fill=col)


def cap(p, q, r1, r2, col):  # limb that tapers from radius r1 at p to r2 at q
    l = math.hypot(q[0] - p[0], q[1] - p[1]) or 1
    n = ((p[1] - q[1]) / l, (q[0] - p[0]) / l)
    poly([(p[0] + n[0] * r1, p[1] + n[1] * r1), (q[0] + n[0] * r2, q[1] + n[1] * r2),
          (q[0] - n[0] * r2, q[1] - n[1] * r2), (p[0] - n[0] * r1, p[1] - n[1] * r1)], col)
    dot(p, r1, col)
    dot(q, r2, col)


def patch(p, q, t1, t2, n, w):  # muscle: part of the segment p -> q, shifted sideways by n
    line([add(lerp(p, q, t1), n), add(lerp(p, q, t2), n)], w, MUS)


def floor(x1=18, x2=222, y=211):
    line([(x1, y), (x2, y)], 2.5, FRAME)


def mark(p, off=15, key=0, rev=False):  # rev: the effort goes from the solid pose to the faded one
    MARKS[0 if GHOST else 1][key] = (p, off, rev, CENTER)


def arrow(p, q):
    if not GHOST:
        ARROWS.append((p, q, 0, None))


def draw_arrow(p, q, off, centre):
    l = math.hypot(q[0] - p[0], q[1] - p[1])
    u = ((q[0] - p[0]) / l, (q[1] - p[1]) / l)
    n = (-u[1], u[0])
    if off:  # beside the path, on the side away from the body (a negative off: towards it)
        m = lerp(p, q, 0.5)
        if centre and (m[0] - centre[0]) * n[0] + (m[1] - centre[1]) * n[1] < 0:
            n = (-n[0], -n[1])
        p, q = add(p, (n[0] * off, n[1] * off)), add(q, (n[0] * off, n[1] * off))
    if l < 26:
        g = (26 - l) / 2
        p, q = add(p, (-u[0] * g, -u[1] * g)), add(q, (u[0] * g, u[1] * g))
    for i in (0, 1):  # keep it inside the picture
        s = max(0, 9 - min(p[i], q[i])) - max(0, max(p[i], q[i]) - 231)
        p = (p[0] + s * (i == 0), p[1] + s * (i == 1))
        q = (q[0] + s * (i == 0), q[1] + s * (i == 1))
    b = add(q, (-u[0] * 12, -u[1] * 12))
    for grow, col in ((2.2, HALO), (0, ARROW)):
        line([p, b], 4.5 + 2 * grow, col)
        h = 7.5 + grow
        tip = add(q, (u[0] * grow * 1.6, u[1] * grow * 1.6))
        base = add(b, (-u[0] * grow, -u[1] * grow))
        poly([tip, add(base, (n[0] * h, n[1] * h)), add(base, (-n[0] * h, -n[1] * h))], col)


# ---- equipment
def plate(p, r=17):
    dot(p, r, ACC)
    dot(p, r * 0.3, FRAME)


def db(p, r=9):  # dumbbell seen end-on
    dot(p, r, ACC)
    dot(p, r * 0.35, FRAME)


def dbl(p, a=90, l=11):  # dumbbell seen from the side, a = direction of the handle
    a1, a2 = add(p, v(a, l)), add(p, v(a + 180, l))
    line([a1, a2], 4, ACC)
    for e in (a1, a2):
        n = v(a + 90, 6)
        line([add(e, n), add(e, (-n[0], -n[1]))], 6, ACC)


def pad(p, q, w=8):
    line([p, q], w, FRAME)


def frame(*pts):
    line(list(pts), 5, FRAME)


def cable(p, q):
    line([p, q], 2, ACC)
    dot(q, 5, FRAME)
    dot(q, 2, ACC)


def handle(p, a=0, l=8):
    line([add(p, v(a, l)), add(p, v(a + 180, l))], 5, ACC)


def bench(x1, x2, y):
    pad((x1, y + 4), (x2, y + 4))
    frame((x1 + 12, y + 10), (x1 + 12, 208))
    frame((x2 - 12, y + 10), (x2 - 12, 208))


# ---- joints: a limb is either two angles or a point to reach
def T(p, hint=(0, 1)):       # reach the point p; the elbow (or knee) goes towards hint
    return ("to", p, hint)


def R(p, hint=(0, 1)):       # same, p relative to the shoulder
    return ("rel", p, hint)


def H(p, hint=(0, -1)):      # same, p relative to the head
    return ("head", p, hint)


def X(p, hint=(1, 0.5)):     # front view: p = (distance from the centre line, y), mirrored
    return ("sym", p, hint)


def ik(s, t, l1, l2, hint):
    dx, dy = t[0] - s[0], t[1] - s[1]
    dist = max(abs(l1 - l2) + 1, min(l1 + l2 - 0.5, math.hypot(dx, dy) or 1))
    base = math.atan2(dy, dx)
    a = math.acos((l1 * l1 + dist * dist - l2 * l2) / (2 * l1 * dist))
    joints = [(s[0] + l1 * math.cos(base + k * a), s[1] + l1 * math.sin(base + k * a)) for k in (1, -1)]
    joint = max(joints, key=lambda e: (e[0] - s[0]) * hint[0] + (e[1] - s[1]) * hint[1])
    return joint, (s[0] + dist * math.cos(base), s[1] + dist * math.sin(base))


def chain(s, spec, l1, l2, anchors):
    if isinstance(spec[0], str):
        a, b = ik(s, add(anchors.get(spec[0], (0, 0)), spec[1]), l1, l2, spec[2])
    else:
        a = add(s, v(spec[0], l1))
        b = add(a, v(spec[1], l2))
    return (a, b, ang(s, a), ang(a, b))


# ---- figure seen from the side
def side(hip=None, torso=180, arms=(), legs=(), foot=None, neck=None):
    if hip is None:  # stand the last leg on the point `foot`
        hip = sub(foot, add(v(legs[-1][0], 42), v(legs[-1][1], 42)))
    sh = add(hip, v(torso, 58))
    head = add(sh, v(torso if neck is None else neck, 24))
    anchors = {"rel": sh, "head": head}
    J = {"hip": hip, "sh": sh, "head": head, "torso": torso,
         "arms": [chain(sh, a, 32, 30, anchors) for a in arms],
         "legs": [chain(hip, l, 42, 42, anchors) for l in legs]}
    J["hand"] = J["arms"][-1][1] if J["arms"] else None
    J["foot"] = J["legs"][-1][1] if J["legs"] else None
    return J


def leg(J, i, col, feet, halo=False, mus=()):
    kn, ft, th, s = J["legs"][i]
    if halo:
        cap(J["hip"], kn, 10.7, 8.7, HALO)
        cap(kn, ft, 8.7, 7, HALO)
    cap(J["hip"], kn, 8.5, 6.5, col)
    cap(kn, ft, 6.5, 4.8, col)
    if feet:
        cap(ft, add(ft, v(s + 90, 10)), 4.8, 3.6, col)
    if "quads" in mus:
        patch(J["hip"], kn, 0.2, 0.82, v(th + 90, 2.4), 7)
    if "hams" in mus:
        patch(J["hip"], kn, 0.2, 0.82, v(th - 90, 2.4), 7)
    if "calves" in mus:
        patch(kn, ft, 0.12, 0.62, v(s - 90, 1.4), 6)


def arm(J, i, col, halo=False, mus=()):
    el, hand, ua, fa = J["arms"][i]
    if halo:
        cap(J["sh"], el, 9, 7.4, HALO)
        cap(el, hand, 7.4, 6.6, HALO)
        dot(hand, 7.2, HALO)
    cap(J["sh"], el, 6.8, 5.2, col)
    cap(el, hand, 5.2, 4.2, col)
    dot(hand, 5, col)
    if "biceps" in mus:
        patch(J["sh"], el, 0.28, 0.85, v(ua + 90, 1.4), 6)
    if "triceps" in mus:
        patch(J["sh"], el, 0.28, 0.85, v(ua - 90, 1.4), 6)


def head_on_top(J):
    dot(J["head"], 14, HALO)
    dot(J["head"], 12, BODY)


def body(J, feet=True, far_arm=True, mus=(), far=BACK, ml=-1):
    global CENTER
    hip, sh, t = J["hip"], J["sh"], J["torso"]
    CENTER = lerp(hip, sh, 0.5)
    n = len(J["legs"])
    feet = feet if isinstance(feet, tuple) else (feet,) * n
    ml = ml % n if n else 0
    for i in range(n - 1):
        leg(J, i, far, feet[i], mus=mus if ml == i else ())
    if len(J["arms"]) > 1 and far_arm:
        arm(J, 0, far)
    if n:
        leg(J, n - 1, BODY, feet[-1], halo=n > 1, mus=mus if ml == n - 1 else ())
    cap(hip, sh, 9.5, 11, BODY)
    f = v(t - 90, 1)  # unit vector pointing out of the chest
    if "glutes" in mus:
        dot(add(hip, (-f[0] * 2.5, -f[1] * 2.5)), 7.5, MUS)
    if "abs" in mus:
        patch(hip, sh, 0.14, 0.5, (f[0] * 4, f[1] * 4), 8)
    if "lowback" in mus:
        patch(hip, sh, 0.14, 0.45, (-f[0] * 4.5, -f[1] * 4.5), 7)
    if "chest" in mus:
        patch(hip, sh, 0.58, 0.9, (f[0] * 4.5, f[1] * 4.5), 9)
    if "back" in mus:
        patch(hip, sh, 0.45, 0.9, (-f[0] * 5, -f[1] * 5), 8)
    cap(sh, J["head"], 5, 5, BODY)
    dot(J["head"], 12, BODY)
    if J["arms"]:
        arm(J, -1, BODY, halo=True, mus=mus)
    if "delts" in mus:
        dot(sh, 6.2, MUS)


# ---- figure seen from the front; limbs are given for the right side and mirrored
def front(cx, sy, arms, legs, th=42, sh=42, tl=56):
    J = {"sh": [], "hip": [], "arms": [], "legs": [], "head": (cx, sy - 25), "cx": cx, "sy": sy, "tl": tl}
    for k, sign in enumerate((-1, 1)):
        s0, h0 = (cx + sign * 19, sy), (cx + sign * 10, sy + tl)
        pair = []
        for spec, start, l1, l2 in ((arms[k] if isinstance(arms, list) else arms, s0, 32, 30),
                                    (legs[k] if isinstance(legs, list) else legs, h0, th, sh)):
            if spec[0] == "sym":
                pair.append(ik(start, (cx + sign * spec[1][0], spec[1][1]), l1, l2, (sign * spec[2][0], spec[2][1])))
            else:
                a = add(start, v(sign * spec[0], l1))
                pair.append((a, add(a, v(sign * spec[1], l2))))
        J["sh"].append(s0)
        J["hip"].append(h0)
        J["arms"].append(pair[0])
        J["legs"].append(pair[1])
    return J


def fbody(J, mus=(), feet=True):
    global CENTER
    cx, sy, tl = J["cx"], J["sy"], J["tl"]
    CENTER = (cx, sy + tl / 2)
    for k, sign in enumerate((-1, 1)):
        h, (kn, ft) = J["hip"][k], J["legs"][k]
        cap(h, kn, 8.5, 6.5, BODY)
        cap(kn, ft, 6.5, 5, BODY)
        if feet:
            cap(ft, add(ft, (sign * 5, 2)), 5, 4, BODY)
        for name, shift in (("thigh", 0), ("outer", 2.6), ("inner", -2.6)):
            if name in mus:
                patch(h, kn, 0.22, 0.82, (sign * shift, 0), 7.5 if name == "thigh" else 6)
        if "calves" in mus:
            patch(kn, ft, 0.12, 0.62, (0, 0), 6)
    (lx, _), (rx, _) = J["sh"]
    (hl, hy), (hr, _) = J["hip"]
    poly([(lx - 4, sy - 5), (rx + 4, sy - 5), (cx + 13, sy + tl * 0.6), (hr + 7, hy + 4),
          (hl - 7, hy + 4), (cx - 13, sy + tl * 0.6)], BODY)
    line([(lx, sy), (rx, sy)], 13, BODY)
    line([(hl, hy), (hr, hy)], 14, BODY)
    if "traps" in mus:
        line([(cx - 11, sy - 3), (cx + 11, sy - 3)], 6, MUS)
    if "chest" in mus:
        line([(cx - 9, sy + 11), (cx + 9, sy + 11)], 12, MUS)
    if "abs" in mus:
        line([(cx, sy + tl * 0.42), (cx, sy + tl * 0.8)], 11, MUS)
    if "glutes" in mus:
        line([(hl, hy), (hr, hy)], 9, MUS)
    for sign in (-1, 1):
        if "lats" in mus:
            line([(cx + sign * 14, sy + 10), (cx + sign * 9, sy + tl * 0.55)], 7, MUS)
    line([(cx, sy), J["head"]], 10, BODY)
    dot(J["head"], 12, BODY)
    for k in (0, 1):
        s0, (el, hand) = J["sh"][k], J["arms"][k]
        cap(s0, el, 9, 7.4, HALO)
        cap(el, hand, 7.4, 6.6, HALO)
        cap(s0, el, 6.8, 5.2, BODY)
        cap(el, hand, 5.2, 4.2, BODY)
        dot(hand, 5, BODY)
        if "uarm" in mus:
            patch(s0, el, 0.28, 0.85, (0, 0), 6)
        if "delts" in mus:
            dot(s0, 6.2, MUS)


# ---- poses shared by several exercises
def lying(arms, legs=None):  # on a flat bench, head to the left
    bench(52, 168, 160)
    return side((150, 152), -90, arms, legs or [T((190, FY), (0, -1))])


def incline(arms):  # on an incline bench
    floor()
    pad((150, 176), (97, 113))
    pad((150, 178), (172, 178))
    frame((158, 184), (158, 208))
    frame((112, 140), (112, 208))
    return side((142, 162), -140, arms, [T((186, FY), (0, -1))])


def standing(arms, torso=180, legs=((-4, -3), (4, 3)), fx=118):
    floor()
    return side(None, torso, arms, list(legs), foot=(fx, FY))


def seated(arms, legs=((90, 0),), torso=-176, x=92):  # on a machine seat, back pad behind
    floor()
    pad((x - 16, 176), (x + 26, 176))
    pad((x - 17, 166), (x - 22, 100))
    frame((x + 4, 182), (x + 4, 208))
    return side((x, 162), torso, arms, list(legs))


def column(x=206, top=20):  # cable tower
    floor()
    frame((x, 208), (x, top))
    line([(x - 9, 206), (x + 9, 206)], 6, FRAME)


def pulley(x, y=24, tower=204):  # high pulley on an arm of the tower
    line([(tower, y), (x, y)], 5, FRAME)
    return (x, y + 2)


def squatting(arms, torso, legs, up=178, fx=140):  # bottom of the squat solid, standing faded
    floor()
    return side(None, M(up, torso), arms, [M((3, -1), legs)], foot=(fx, FY))


def prone(up, hand=(166, FY), foot=(34, FY)):  # push-up position: up = (leg angle, torso angle)
    floor()
    return side(None, up[1], [T(hand, (-1, -0.4))], [(up[0], up[0])], foot=foot)


def fseated(arms):  # on a bench, seen from the front
    floor()
    pad((92, 162), (148, 162))
    frame((120, 168), (120, 208))
    return front(120, 100, arms, (40, 0), th=20)


def hanging(grip, sy):  # from a bar, seen from behind
    line([(40, 22), (200, 22)], 6, ACC)
    frame((48, 22), (48, 8))
    frame((192, 22), (192, 8))
    return front(120, sy, X((grip, 22), (1, 0.6)), (6, 3), sh=36)


# ---- chest
def bench_press():
    J = lying([R(M((8, -28), (8, -61)), (1, 0.3))])
    body(J, mus=("chest", "triceps"))
    plate(J["hand"], 18)
    floor()
    mark(J["hand"], 29)


def incline_bench_press():
    J = incline([R(M((16, -24), (6, -61)), (1, 0.6))])
    body(J, mus=("chest", "delts", "triceps"))
    plate(J["hand"], 16)
    mark(J["hand"], 26)


def incline_dumbbell_press():
    J = incline([R(M((16, -24), (6, -61)), (1, 0.6))])
    body(J, mus=("chest", "delts"))
    db(J["hand"], 10)
    mark(J["hand"], 20)


def dumbbell_fly():  # seen from above, lying on the bench
    line([(120, 40), (120, 200)], 34, FRAME)
    J = front(120, 80, (96, 104), (4, 2))
    fbody(J, mus=("chest",))
    for k, sign in enumerate((-1, 1)):
        dbl(J["arms"][k][1], 0)
        arrow((120 + sign * 84, 46), (120 + sign * 40, 36))


def chest_press_machine():
    J = seated([R(M((8, 12), (60, 2)), (-0.4, 1))])
    frame((70, 208), (70, 52), (128, 52))
    frame((128, 52), (J["hand"][0] + 4, J["hand"][1] - 2))
    body(J, mus=("chest", "triceps"))
    handle(J["hand"], 0)
    mark(J["hand"], 27)


def pec_deck():
    floor()
    line([(120, 70), (120, 150)], 40, FRAME)
    J = front(120, 96, (88, 180), (35, 0), th=22)
    for k, sign in enumerate((-1, 1)):
        el, hand = J["arms"][k]
        line([add(el, (sign * 9, 4)), add(hand, (sign * 9, -4))], 7, ACC)
        arrow((120 + sign * 70, 46), (120 + sign * 30, 46))
    pad((92, 158), (148, 158))
    fbody(J, mus=("chest",))


def cable_crossover():
    floor()
    J = front(120, 66, M((96, 72), (50, 25)), (8, 3))
    for k, x in enumerate((22, 218)):
        frame((x, 208), (x, 22))
        cable(J["arms"][k][1], (x, 26))
    fbody(J, mus=("chest",))
    for k in (0, 1):
        handle(J["arms"][k][1], 90, 6)
        mark(J["arms"][k][1], -16, k)


def push_up():
    J = prone(M((-76, 96), (-62, 110)))
    body(J, mus=("chest", "triceps"))
    mark(J["head"], 20)


def dip():
    floor()
    frame((90, 208), (90, 142))
    frame((170, 208), (170, 142))
    line([(82, 139), (178, 139)], 6, ACC)
    J = side((114, M(160, 137)), 172, [T((124, 139), (-1, 0))], [(10, -70)])
    body(J, feet=False, mus=("chest", "triceps"))
    mark(J["head"], 22)


def dumbbell_pullover():
    J = lying([M((-104, -100), (172, 170))])
    body(J, mus=("chest", "back"))
    db(J["hand"], 10)
    floor()
    mark(J["hand"], 18)


# ---- back
def pull_up():
    J = hanging(44, M(82, 56))
    fbody(J, mus=("lats", "uarm"))
    mark((196, J["sy"] + 44), 0)


def chin_up():  # narrow grip, palms towards the face
    J = hanging(21, M(84, 56))
    fbody(J, mus=("lats", "uarm"))
    mark((186, J["sy"] + 44), 0)


def assisted_pull_up():  # kneeling on the pad of the machine
    floor()
    frame((206, 208), (206, 22))
    line([(40, 22), (206, 22)], 6, ACC)
    J = front(120, M(84, 58), X((44, 22), (1, 0.6)), (5, 0), sh=22)
    y = J["legs"][0][0][1] + 12
    frame((120, y + 6), (120, 208))
    fbody(J, mus=("lats", "uarm"), feet=False)
    line([(88, y), (152, y)], 9, ACC)
    mark((184, J["sy"] + 30), 0)


def lat_pulldown():
    floor()
    y = M(44, 92)
    J = front(120, 104, X((46, y), (1, 0.8)), (40, 0), th=20)
    pad((92, 166), (148, 166))
    frame((120, 172), (120, 208))
    cable((120, y), (120, 12))
    fbody(J, mus=("lats", "uarm"))
    line([(46, y), (194, y)], 6, ACC)
    line([(82, 172), (158, 172)], 9, ACC)
    mark((210, y), 0)


def straight_arm_pulldown():
    column(204, 20)
    top = pulley(170)
    J = side(None, 168, [M((122, 126), (24, 30))], [(-3, 2)], foot=(100, FY))
    cable(J["hand"], top)
    body(J, mus=("back",))
    handle(J["hand"], M(30, 100), 7)
    mark(J["hand"], 15)


def seated_cable_row():
    column(212, 110)
    pad((60, 182), (112, 182))
    frame((72, 188), (72, 208))
    frame((104, 188), (104, 208))
    line([(168, 172), (176, 204)], 7, FRAME)
    J = side((84, 168), 178, [R(M((60, 32), (22, 34)), (-1, 0.2))], [(78, 62)])
    cable(J["hand"], (212, 150))
    body(J, mus=("back", "biceps"))
    handle(J["hand"], 0, 7)
    mark(J["hand"], -16)


def machine_row():  # chest against the pad, pulling the lever
    floor()
    pad((70, 178), (112, 178))
    frame((90, 184), (90, 208))
    pad((116, 108), (120, 150), 9)
    frame((118, 150), (130, 208))
    J = side((90, 164), 176, [R(M((60, 26), (24, 32)), (-1, 0.2))], [(84, 4)])
    frame((178, 208), (178, 130), add(J["hand"], (4, 0)))
    body(J, mus=("back", "biceps"))
    handle(J["hand"], 0, 7)
    mark(J["hand"], -16)


def barbell_row():
    J = standing([R(M((0, 61), (-18, 27)), (-1, -1))], torso=112, legs=((22, -8),), fx=126)
    body(J, mus=("back", "biceps"))
    plate(J["hand"], 17)
    mark(J["hand"], 28)


def dumbbell_row():
    floor()
    bench(70, 176, 180)
    J = side((88, 132), 96, [(4, -4), R(M((2, 60), (-10, 26)), (-1, -1))], [(-28, -12), (2, -90)])
    body(J, feet=(True, False), mus=("back", "biceps"))
    db(J["hand"], 10)
    mark(J["hand"], 20)


def inverted_row():  # hanging under a low bar, heels on the floor
    floor()
    frame((84, 208), (84, 120))
    a = M(12, 28)
    J = side(None, -90 - a, [T((84, 120), (-0.3, 1))], [(90 - a, 90 - a)], foot=(196, FY))
    body(J, mus=("back", "biceps"))
    dot((84, 120), 6, ACC)
    mark(J["hip"], 0)


def deadlift():
    floor()
    J = side(None, M(178, 135), [(0, 0)], [M((3, -1), (38, -6))], foot=(128, FY))
    body(J, mus=("glutes", "hams", "lowback"))
    plate(J["hand"], 21)
    mark(J["head"], 20, rev=True)


def sumo_deadlift():  # wide stance, seen from the front
    floor()
    J = front(120, M(66, 98), (3, 0), X((42, FY), (1, 0)))
    y = J["arms"][0][1][1]
    fbody(J, mus=("glutes", "thigh"))
    line([(46, y), (194, y)], 5, ACC)
    for x in (44, 196):
        line([(x, y - 24), (x, y + 24)], 8, ACC)
    mark((216, y), 0, rev=True)


def back_extension():
    floor()
    frame((62, 208), (104, 150))
    frame((150, 208), (104, 150))
    J = side((112, 128), M(70, 128), [R((10, 12), (1, 1))], [(-52, -52)])
    pad((94, 142), (122, 150), 10)
    line([(40, 196), (52, 204)], 8, ACC)
    body(J, feet=False, mus=("lowback", "glutes", "hams"))
    mark(J["head"], 20)


# ---- shoulders
def overhead_press():
    J = standing([R(M((16, -6), (8, -50)), M((0.3, 1), (1, 0)))])
    body(J, mus=("delts", "triceps"))
    plate(J["hand"], 11)
    mark(J["hand"], 22)


def dumbbell_shoulder_press():
    J = fseated(M((112, 180), (166, 186)))
    fbody(J, mus=("delts", "uarm"))
    for k in (0, 1):
        dbl(J["arms"][k][1], 90)
        mark(J["arms"][k][1], 22, k)


def arnold_press():  # starts with the dumbbells in front of the shoulders
    J = fseated(M((14, 178), (166, 186)))
    fbody(J, mus=("delts", "uarm"))
    for k in (0, 1):
        dbl(J["arms"][k][1], M(0, 90))
        mark(J["arms"][k][1], 26, k)


def shoulder_press_machine():
    J = seated([R(M((16, -20), (10, -60)), (1, 0.6))])
    frame((66, 208), (66, 40), (J["hand"][0], J["hand"][1] - 2))
    body(J, mus=("delts", "triceps"))
    handle(J["hand"], 90)
    mark(J["hand"], 18)


def lateral_raise():
    floor()
    J = front(120, 66, M((8, 4), (82, 86)), (6, 3))
    fbody(J, mus=("delts",))
    for k in (0, 1):
        dbl(J["arms"][k][1], 90, 9)
        mark(J["arms"][k][1], 14, k)


def cable_lateral_raise():  # low pulley on the left, working arm on the right
    floor()
    frame((24, 208), (24, 60))
    J = front(128, 66, [(8, 4), M((-8, -14), (82, 86))], (6, 3))
    cable(J["arms"][1][1], (24, 198))
    fbody(J, mus=("delts",))
    handle(J["arms"][1][1], 0, 6)
    mark(J["arms"][1][1], 14)


def front_raise():
    J = standing([(0, 2), M((2, 4), (88, 90))])
    body(J, mus=("delts",))
    db(J["arms"][0][1], 8)
    db(J["hand"], 9)
    mark(J["hand"], 18)


def rear_delt_fly():  # bent over, seen from the front
    floor()
    J = front(120, 92, M((6, 2), (84, 90)), (5, 2), tl=30)
    J["head"] = (120, 80)
    fbody(J, mus=("delts",))
    for k in (0, 1):
        dbl(J["arms"][k][1], 0, 9)
        mark(J["arms"][k][1], 15, k)


def shrug():
    floor()
    J = front(120, 66, (8, 2), (6, 3))
    fbody(J, mus=("traps",))
    for k, sign in enumerate((-1, 1)):
        dbl(J["arms"][k][1], 90, 9)
        arrow((120 + sign * 44, 62), (120 + sign * 44, 34))


def face_pull():
    column(210, 30)
    J = side(None, 184, [R(M((58, -8), (16, -14)), (-0.3, -1))], [(-12, -8), (10, 4)], foot=(98, FY))
    cable(J["hand"], (210, 62))
    body(J, mus=("delts", "back"))
    handle(J["hand"], 0, 6)
    mark(J["hand"], 15)


# ---- arms
def barbell_curl():
    J = standing([M((2, 8), (4, 150))])
    body(J, mus=("biceps",))
    plate(J["hand"], 13)
    mark(J["hand"], 24)


def dumbbell_curl():
    J = standing([(0, 4), M((2, 8), (4, 150))])
    body(J, mus=("biceps",))
    db(J["arms"][0][1], 8)
    db(J["hand"], 9)
    mark(J["hand"], 19)


def hammer_curl():
    J = standing([(0, 4), M((2, 8), (4, 140))])
    body(J, mus=("biceps",))
    dbl(J["arms"][0][1], 90, 8)
    dbl(J["hand"], M(90, 50), 9)
    mark(J["hand"], 20)


def preacher_curl():
    floor()
    pad((70, 180), (112, 180))
    frame((90, 186), (90, 208))
    frame((146, 208), (146, 150))
    J = side((88, 166), 168, [(52, M(64, 152))], [(88, 0)])
    pad((112, 116), (150, 152), 9)
    body(J, mus=("biceps",))
    plate(J["hand"], 12)
    mark(J["hand"], 22)


def concentration_curl():  # seated, elbow against the thigh
    floor()
    bench(56, 118, 172)
    J = side((98, 160), 150, [(20, M(28, 150))], [(90, 0)])
    body(J, mus=("biceps",))
    db(J["hand"], 9)
    mark(J["hand"], 18)


def cable_curl():
    column(204, 60)
    J = standing([M((6, 22), (8, 150))], fx=106)
    cable(J["hand"], (204, 198))
    body(J, mus=("biceps",))
    handle(J["hand"], 90, 7)
    mark(J["hand"], 18)


def triceps_pushdown():
    column(204, 20)
    top = pulley(142)
    J = side(None, 172, [(6, M(122, 14))], [(-6, -3), (5, 3)], foot=(110, FY))
    cable(J["hand"], top)
    body(J, mus=("triceps",))
    handle(J["hand"], 90, 7)
    mark(J["hand"], 16)


def overhead_triceps_extension():
    floor()
    bench(70, 132, 172)
    J = side((104, 160), 180, [(172, M(-72, 176))], [T((146, FY), (1, -1))])
    body(J, mus=("triceps",))
    head_on_top(J)
    db(J["hand"], 10)
    mark(J["hand"], 18)


def skull_crusher():
    J = lying([(176, M(-72, 180))])
    body(J, mus=("triceps",))
    plate(J["hand"], 12)
    floor()
    mark(J["hand"], 22)


def bench_dip():
    floor()
    bench(28, 100, 178)
    J = side((114, M(196, 176)), 180, [T((96, 174), (-1, -0.5))], [T((194, FY), (0, -1))])
    body(J, mus=("triceps",))
    mark(J["head"], 20)


# ---- legs
def squat():
    J = squatting([R((-8, -2), (0, 1))], 152, (76, -20))
    body(J, mus=("quads", "glutes"))
    bar = add(J["sh"], (-10, 0))
    plate(bar, 15)
    mark(bar, 26, rev=True)


def front_squat():
    J = squatting([R((13, -1), (1, 0.5))], 164, (80, -24))
    body(J, mus=("quads", "glutes"))
    bar = add(J["sh"], (11, 1))
    plate(bar, 15)
    mark(bar, 26, rev=True)


def goblet_squat():
    J = squatting([R((14, 14), (0, 1))], 162, (78, -22))
    body(J, mus=("quads", "glutes"))
    db(J["hand"], 11)
    mark(J["head"], 20, rev=True)


def smith_machine_squat():  # the bar runs on the rails of the machine
    J = squatting([R((-8, -2), (0, 1))], 168, (84, -12), up=176)
    x = J["sh"][0] - 10
    frame((x, 208), (x, 26))
    line([(x - 14, 26), (x + 14, 26)], 6, FRAME)
    body(J, mus=("quads", "glutes"))
    plate((x, J["sh"][1]), 15)
    mark((x, J["sh"][1]), 26, rev=True)


def hack_squat():  # leaning on the sled, feet on the plate
    floor()
    frame((40, 60), (150, 208))
    line([(160, 186), (190, 208)], 8, ACC)
    hip = M((100, 140), (118, 164))
    J = side(hip, -143, [R((-6, 4), (1, 1))], [T((172, 196), (0.3, -1))])
    pad(add(hip, (-14, 2)), add(J["sh"], (-12, 2)), 9)
    body(J, mus=("quads", "glutes"))
    mark(J["head"], 22, rev=True)


def leg_press():
    floor()
    frame((40, 208), (200, 208))
    pad((96, 186), (62, 124))
    pad((74, 190), (104, 190))
    J = side((90, 174), -151, [(8, 60)], [M((124, 96), (106, 98))])
    f = J["foot"]
    body(J, feet=False, mus=("quads", "glutes"))
    line([add(f, v(190, 26)), add(f, v(10, 22))], 7, ACC)
    plate(add(f, (26, 6)), 14)
    mark(add(f, (4, -38)), 0)


def leg_extension():
    J = seated([(4, 20)], legs=((90, M(6, 72)),))
    frame((96, 208), (140, 208), (140, 176))
    body(J, feet=False, mus=("quads",))
    dot(add(J["foot"], v(J["legs"][0][3] + 90, 11)), 7, ACC)
    mark(J["foot"], 20)


def leg_curl():  # lying
    floor()
    pad((70, 164), (190, 164))
    frame((88, 170), (88, 208))
    frame((172, 170), (172, 208))
    J = side((122, 152), 91, [(25, 95)], [(-90, M(-94, 160))])
    body(J, feet=False, mus=("hams",))
    dot(add(J["foot"], v(J["legs"][0][3] - 90, 11)), 7, ACC)
    mark(J["foot"], 18)


def lunge():
    floor()
    J = side(M((102, 136), (108, 156)), 180, [(0, 0)], [T((55, FY), (1, 1)), T((150, FY), (1, -0.2))])
    body(J, far_arm=False, mus=("quads", "glutes"))
    db(J["hand"], 9)
    mark(J["head"], 20, rev=True)


def bulgarian_split_squat():
    floor()
    bench(24, 86, 170)
    J = side(M((124, 130), (126, 150)), 172, [(0, 0)], [T((66, 163), (0.3, 1)), T((164, FY), (1, -0.2))])
    body(J, far_arm=False, mus=("quads", "glutes"))
    db(J["hand"], 9)
    mark(J["head"], 20, rev=True)


def step_up():
    floor()
    line([(132, 198), (200, 198)], 22, FRAME)
    hip = M((112, 124), (146, 100))
    J = side(hip, 176, [(-4, 6), (6, 12)], [T(M((96, FY), (134, 176)), (1, 0)), T((150, 181), (1, -0.2))])
    body(J, mus=("quads", "glutes"))
    mark(J["head"], 20)


def wall_sit():
    floor()
    line([(64, 30), (64, 208)], 10, FRAME)
    J = side((82, 163), 180, [(14, 62)], [T((126, FY), (1, -1))])
    body(J, mus=("quads",))


def romanian_deadlift():
    floor()
    J = side(None, M(178, 112), [(0, 0)], [M((2, 0), (10, -4))], foot=(112, FY))
    body(J, mus=("hams", "glutes", "lowback"))
    plate(J["hand"], 17)
    mark(J["head"], 20, rev=True)


def bridge(sh, torso, bar=False):  # shoulders fixed, hips pushed up
    hip = sub(sh, v(torso, 58))
    J = side(hip, torso, [T(add(hip, (0, -13)) if bar else (sh[0] + 58, 203), (0, -1))],
             [T((hip[0] + 44, FY), (0.5, -1))], neck=None if bar else -90)
    body(J, mus=("glutes", "hams"))
    return J


def hip_thrust():
    floor()
    bench(20, 80, 178)
    J = bridge((73, 150), M(-125, -80), bar=True)
    plate(add(J["hip"], (0, -13)), 17)
    mark(add(J["hip"], (0, -13)), 28)


def glute_bridge():
    floor()
    J = bridge((70, 199), M(-88, -62))
    mark(J["hip"], 0)


def hip_abduction_machine():
    floor()
    line([(120, 74), (120, 150)], 40, FRAME)
    J = front(120, 96, (12, -20), M((22, 4), (62, 6)), th=30)
    pad((90, 160), (150, 160))
    fbody(J, mus=("outer",))
    for k, sign in enumerate((-1, 1)):
        kn = J["legs"][k][0]
        line([add(kn, (sign * 11, -12)), add(kn, (sign * 11, 12))], 7, ACC)
        mark(add(kn, (sign * 6, -30)), 0, k)


def hip_adduction_machine():  # same seat as the abductor, pads on the inside of the knees
    floor()
    line([(120, 74), (120, 150)], 40, FRAME)
    J = front(120, 96, (12, -20), M((62, 6), (24, 4)), th=30)
    pad((90, 160), (150, 160))
    fbody(J, mus=("inner",))
    for k, sign in enumerate((-1, 1)):
        kn = J["legs"][k][0]
        line([add(kn, (-sign * 11, -12)), add(kn, (-sign * 11, 12))], 7, ACC)
        mark(add(kn, (sign * 6, -30)), 0, k)


def calf_raise():
    floor()
    line([(96, 203), (150, 203)], 12, FRAME)
    J = side((116, M(108, 100)), 180, [(0, 2)], [(0, 0)])
    body(J, feet=False, mus=("calves",))
    ft = J["foot"]
    cap(ft, (ft[0] + 10, 193), 4.8, 3.6, BODY)
    db(J["hand"], 9)
    arrow((88, 192), (88, 162))


def seated_calf_raise():
    floor()
    J = seated([(20, 70)], legs=((90, 0),), torso=178)
    kn, ft = J["legs"][0][0], J["foot"]
    frame((kn[0] + 4, kn[1] - 14), (176, kn[1] - 14), (176, 208))
    body(J, feet=False, mus=("calves",))
    cap(ft, (ft[0] + 11, ft[1] + 4), 4.8, 3.6, BODY)
    line([(ft[0] + 2, 207), (ft[0] + 22, 207)], 7, FRAME)
    line([(kn[0] - 12, kn[1] - 13), (kn[0] + 12, kn[1] - 13)], 8, ACC)
    arrow((ft[0] - 16, 204), (ft[0] - 16, 178))


def cable_kickback():
    column(204, 60)
    J = side(None, 140, [(78, 84)], [M((-4, -8), (-52, -58)), (4, 0)], foot=(120, FY))
    cable(J["legs"][0][1], (204, 198))
    body(J, mus=("glutes", "hams"), far=BODY, ml=0)
    mark(J["legs"][0][1], 16)


# ---- core
def plank():
    floor()
    J = side(None, 100, [(0, 90)], [(-75, -75)], foot=(28, FY))
    body(J, feet=False, mus=("abs",))


def side_plank():
    floor()
    J = side(None, 103, [(180, 180), (0, 90)], [(-77, -77)], foot=(28, FY))
    body(J, feet=False, mus=("abs",), far=BODY)


def crunch():
    floor()
    J = side((118, 197), M(-92, -118), [H((2, -3))], [T((166, FY), (0, -1))])
    body(J, mus=("abs",))
    mark(J["head"], 20)


def bicycle_crunch():  # one knee in, the other leg out, alternating
    floor()
    J = side((116, 196), -112, [H((3, -3), (1, -1))], [(104, 96), (152, 62)])
    body(J, mus=("abs",))
    kn = J["legs"][1][0]
    arrow(add(kn, (22, -6)), add(kn, (-2, -22)))


def leg_raise():  # lying on the floor
    floor()
    J = side((126, 198), -90, [(90, 90)], [M((90, 90), (166, 170))])
    body(J, feet=False, mus=("abs",))
    mark(J["foot"], 18)


def dead_bug():  # on the back: one arm and the opposite leg reach out
    floor()
    J = side((132, 198), -90, [(-98, -96), (178, 180)], [(96, 94), (168, 78)])
    body(J, feet=False, mus=("abs",))


def hanging_leg_raise():
    frame((52, 208), (52, 22), (128, 22))
    line([(36, 208), (68, 208)], 6, FRAME)
    J = side((122, 142), 180, [(180, 180)], [M((4, 2), (88, 86))])
    body(J, mus=("abs",))
    head_on_top(J)
    dot(J["hand"], 6, ACC)
    mark(J["foot"], 18)


def russian_twist():
    floor()
    J = side((112, 194), -152, [(72, 86)], [(116, 76)])
    body(J, mus=("abs",))
    plate(J["hand"], 11)


def cable_crunch():
    column(204, 20)
    top = pulley(132)
    J = side((96, 162), M(170, 132), [H((7, -2), (1, 1))], [(14, -90)])
    cable(J["hand"], top)
    body(J, feet=False, mus=("abs",))
    mark(J["head"], 22)


def ab_wheel():  # kneeling roll-out
    floor()
    a, torso, x = M((80, 114, 142), (35, 100, 212))
    hip = add((70, 203), v(90 + a, 42))
    J = side(hip, torso, [T((x, 196), (0, -1))], [(ang(hip, (70, 203)), -90)])
    body(J, feet=False, mus=("abs",))
    dot((x, 197), 10, ACC)
    dot((x, 197), 3.5, FRAME)
    mark((x, 226), 0)


def mountain_climber():
    floor()
    J = side((108, 166), 110, [T((166, FY), (-1, -0.4))], [(-62, -62), (62, -42)])
    body(J, mus=("abs",))
    kn = J["legs"][1][0]
    arrow(add(kn, (-30, 14)), add(kn, (-4, 16)))


def superman():  # lying face down, arms and legs lifted
    floor()
    J = side((120, 198), M(91, 101), [M((91, 91), (108, 106))], [M((-91, -91), (-101, -99))], neck=M(95, 112))
    body(J, feet=False, mus=("lowback", "glutes"))


# ---- TRX: straps hanging from an anchor at the top of the picture
def trx(p, top, foot=False):
    line([(top[0] - 13, 16), (top[0] + 13, 16)], 6, FRAME)
    line([top, p], 3, ACC)
    if foot:
        dot(p, 6, ACC)
    else:
        handle(p, ang(top, p) + 90, 6)


def leaning(a, arms, fx=134):  # straight body leaning back, a = angle from the vertical
    floor()
    return side(None, a - 180, arms, [(a, a)], foot=(fx, FY))


def trx_row():
    top = (114, 18)
    J = leaning(M(40, 30), [M(T(top), R((-3, 0), (-1, 0.3)))])
    trx(J["hand"], top)
    body(J, mus=("back", "biceps"))
    mark(J["head"], 20)


def trx_chest_press():
    floor()
    top = (119, 18)
    a = M(-52, -42)
    J = side(None, a + 180, [R(M((16, -5), (61, -6)), (-0.5, 1))], [(a, a)], foot=(60, FY))
    trx(J["hand"], top)
    body(J, mus=("chest", "triceps"))
    mark(J["head"], 20)


def trx_y_raise():
    top = (106, 18)
    J = leaning(M(40, 28), [M(T(top), (155, 155))], fx=126)
    trx(J["hand"], top)
    body(J, mus=("delts", "back"))
    mark(J["head"], 20)


def trx_biceps_curl():
    top = (97, 18)
    J = leaning(M(40, 30), [M(T(top), (112, 205))], fx=130)
    trx(J["hand"], top)
    body(J, mus=("biceps",))
    mark(J["head"], 20)


def trx_triceps_extension():
    floor()
    top = (100, 18)
    a = M(-48, -40)
    J = side(None, a + 180, [(158, M(-128, 150))], [(a, a)], foot=(56, FY))
    trx(J["hand"], top)
    body(J, mus=("triceps",))
    mark(J["head"], 20)


def trx_squat():
    top = (203, 18)
    J = squatting([M(R((44, -4), (0, 1)), (104, 104))], 152, (76, -20), up=176, fx=104)
    trx(J["hand"], top)
    body(J, mus=("quads", "glutes"))
    mark(J["head"], 20, rev=True)


def trx_plank():  # forearm plank, feet in the cradles
    floor()
    J = side((128, 183), 100, [(0, 90)], [(-94, -94)])
    trx(J["foot"], (J["foot"][0], 18), foot=True)
    body(J, feet=False, mus=("abs",))


EXERCISES = [
    bench_press, incline_bench_press, incline_dumbbell_press, dumbbell_fly, chest_press_machine, pec_deck,
    cable_crossover, push_up, dip, dumbbell_pullover,
    pull_up, chin_up, assisted_pull_up, lat_pulldown, straight_arm_pulldown, seated_cable_row, machine_row,
    barbell_row, dumbbell_row, inverted_row, deadlift, sumo_deadlift, back_extension,
    overhead_press, dumbbell_shoulder_press, arnold_press, shoulder_press_machine, lateral_raise,
    cable_lateral_raise, front_raise, rear_delt_fly, shrug, face_pull,
    barbell_curl, dumbbell_curl, hammer_curl, preacher_curl, concentration_curl, cable_curl,
    triceps_pushdown, overhead_triceps_extension, skull_crusher, bench_dip,
    squat, front_squat, goblet_squat, smith_machine_squat, hack_squat, leg_press, leg_extension, leg_curl,
    lunge, bulgarian_split_squat, step_up, wall_sit, romanian_deadlift, hip_thrust, glute_bridge,
    hip_abduction_machine, hip_adduction_machine, calf_raise, seated_calf_raise, cable_kickback,
    plank, side_plank, crunch, bicycle_crunch, leg_raise, dead_bug, hanging_leg_raise, russian_twist,
    cable_crunch, ab_wheel, mountain_climber, superman,
    trx_row, trx_chest_press, trx_y_raise, trx_biceps_curl, trx_triceps_extension, trx_squat, trx_plank,
]


def render(f):
    global im, d, GHOST
    MARKS[0].clear()
    MARKS[1].clear()
    ARROWS.clear()
    layers = []
    for GHOST in (True, False):
        im = Image.new("RGBA", (N * S, N * S), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        f()
        layers.append(im)
    layers[0].putalpha(layers[0].getchannel("A").point(lambda a: int(a * 0.4)))
    im = Image.alpha_composite(layers[0], layers[1])
    d = ImageDraw.Draw(im)
    for key, (q, off, rev, centre) in MARKS[1].items():
        p = MARKS[0].get(key, (q,))[0]
        if math.hypot(q[0] - p[0], q[1] - p[1]) > 10:
            draw_arrow(*((q, p) if rev else (p, q)), off, centre)
    for a in ARROWS:
        draw_arrow(*a)
    return im.resize((480, 480), Image.LANCZOS)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for f in EXERCISES:
        render(f).save(os.path.join(OUT, f.__name__ + ".png"), optimize=True)
    print(len(EXERCISES), "figures written to", OUT)
