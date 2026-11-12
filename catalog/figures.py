# Draws the exercise illustrations in catalog/images (480 px transparent PNGs).
# Run from the repository root:  python3 catalog/figures.py
# Angles: 0 = down, 90 = the way the figure faces (right), 180 = up, -90 = behind.
import math
import os
from PIL import Image, ImageDraw

S, N = 8, 240
BODY, BACK = (51, 65, 85, 255), (148, 163, 184, 255)
ACC, FRAME, HALO = (37, 99, 235, 255), (147, 197, 253, 255), (241, 245, 249, 255)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
im = d = None


def v(a, l):
    return (l * math.sin(math.radians(a)), l * math.cos(math.radians(a)))


def add(p, q):
    return (p[0] + q[0], p[1] + q[1])


def line(pts, w, col):
    pts = [(x * S, y * S) for x, y in pts]
    d.line(pts, fill=col, width=int(w * S))
    for x, y in pts:
        r = w * S / 2
        d.ellipse((x - r, y - r, x + r, y + r), fill=col)


def dot(p, r, col):
    d.ellipse(((p[0] - r) * S, (p[1] - r) * S, (p[0] + r) * S, (p[1] + r) * S), fill=col)


def floor(x1=18, x2=222, y=211):
    line([(x1, y), (x2, y)], 2.5, FRAME)


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


# ---- figure seen from the side
def side(hip, torso, arms, legs, ground=None):
    sh = add(hip, v(torso, 58))
    J = {"hip": hip, "sh": sh, "head": add(sh, v(torso, 22)), "arms": [], "legs": []}
    for ua, fa in arms:
        el = add(sh, v(ua, 32))
        J["arms"].append((el, add(el, v(fa, 30))))
    for th, s in legs:
        kn = add(hip, v(th, 42))
        J["legs"].append((kn, add(kn, v(s, 42)), s))
    if ground:  # drop the figure so its lowest joint rests on the floor
        low = max([p[1] for a in J["arms"] for p in a] + [p[1] for l in J["legs"] for p in l[:2]])
        dy = ground - 6 - low
        m = lambda p: (p[0], p[1] + dy)
        J = {"hip": m(J["hip"]), "sh": m(J["sh"]), "head": m(J["head"]),
             "arms": [(m(a), m(b)) for a, b in J["arms"]],
             "legs": [(m(a), m(b), s) for a, b, s in J["legs"]]}
    J["hand"] = J["arms"][-1][1] if J["arms"] else None
    J["foot"] = J["legs"][-1][1]
    return J


def limb(a, b, c, col, w=12, halo=False):
    if halo:
        line([a, b, c], w + 4, HALO)
    line([a, b, c], w, col)


def leg(J, i, col, feet, halo=False):
    kn, ft, s = J["legs"][i]
    pts = [J["hip"], kn, ft]
    if halo:
        line(pts, 17, HALO)
    line(pts, 13, col)
    if feet:
        line([ft, add(ft, v(s + 90, 9))], 9, col)


def body(J, feet=True, back_arm=True):
    if len(J["legs"]) > 1:
        leg(J, 0, BACK, feet)
    if len(J["arms"]) > 1 and back_arm:
        limb(J["sh"], *J["arms"][0], BACK)
    leg(J, -1, BODY, feet, halo=len(J["legs"]) > 1)
    line([J["hip"], J["sh"]], 18, BODY)
    dot(J["head"], 12.5, BODY)
    if J["arms"]:
        limb(J["sh"], *J["arms"][-1], BODY, halo=True)


# ---- figure seen from the front; limbs are given for the right side and mirrored
def front(cx, sy, arms, legs, th=42, sh=42, top=False):
    J = {"sh": [], "hip": [], "arms": [], "legs": [], "head": (cx, sy - 24)}
    for k, sign in enumerate((-1, 1)):
        ua, fa = arms[k] if isinstance(arms, list) else arms
        t, s = legs[k] if isinstance(legs, list) else legs
        s0, h0 = (cx + sign * 19, sy), (cx + sign * 10, sy + 56)
        el = add(s0, v(sign * ua, 32))
        kn = add(h0, v(sign * t, th))
        J["sh"].append(s0)
        J["hip"].append(h0)
        J["arms"].append((el, add(el, v(sign * fa, 30))))
        J["legs"].append((kn, add(kn, v(sign * s, sh))))
    return J


def fbody(J):
    for k in (0, 1):
        line([J["hip"][k], *J["legs"][k]], 13, BODY)
    (lx, sy), (rx, _) = J["sh"]
    (hl, hy), (hr, _) = J["hip"]
    d.polygon([(p[0] * S, p[1] * S) for p in [(lx - 3, sy - 4), (rx + 3, sy - 4), (hr + 6, hy + 4), (hl - 6, hy + 4)]], fill=BODY)
    line([(lx, sy), (rx, sy)], 13, BODY)
    line([(hl, hy), (hr, hy)], 13, BODY)
    dot(J["head"], 12.5, BODY)
    for k in (0, 1):
        limb(J["sh"][k], *J["arms"][k], BODY, halo=True)


# ---- poses shared by several exercises
def lying(arms):  # on a flat bench, head to the left
    bench(52, 168, 160)
    return side((150, 152), -90, arms, [(68, 0)])


def standing(arms, torso=180, legs=((-4, -3), (4, 3))):
    floor()
    return side((112, 0), torso, arms, list(legs), ground=211)


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


def head_on_top(J):
    dot(J["head"], 14.5, HALO)
    dot(J["head"], 12.5, BODY)


def plank_legs():
    return [(-66, -66)]


# ---- the exercises
def bench_press():
    J = lying([(165, 180)])
    body(J)
    plate(J["hand"], 18)
    floor()


def incline_dumbbell_press():
    floor()
    pad((150, 176), (97, 113))
    pad((150, 178), (172, 178))
    frame((158, 184), (158, 208))
    frame((112, 140), (112, 208))
    J = side((142, 162), -140, [(172, 180)], [(72, 0)])
    body(J)
    db(J["hand"], 10)


def dumbbell_fly():  # seen from above, lying on the bench
    line([(120, 40), (120, 200)], 34, FRAME)
    J = front(120, 78, (100, 125), (4, 2))
    fbody(J)
    for k in (0, 1):
        dbl(J["arms"][k][1], 0)


def chest_press_machine():
    J = seated([(100, 88)])
    frame((70, 208), (70, 52), (128, 52))
    frame((128, 52), (J["hand"][0] + 4, J["hand"][1] - 2))
    body(J)
    handle(J["hand"], 0)


def pec_deck():
    floor()
    line([(120, 70), (120, 150)], 40, FRAME)
    J = front(120, 96, (88, 180), (35, 0), th=22)
    for k, sign in enumerate((-1, 1)):
        el, hand = J["arms"][k]
        line([add(el, (sign * 9, 4)), add(hand, (sign * 9, -4))], 7, ACC)
    pad((92, 158), (148, 158))
    fbody(J)


def cable_crossover():
    floor()
    J = front(120, 72, (50, 25), (8, 3))
    for k, x in enumerate((22, 218)):
        frame((x, 208), (x, 22))
        cable(J["arms"][k][1], (x, 26))
    fbody(J)
    for k in (0, 1):
        handle(J["arms"][k][1], 90, 6)


def push_up():
    floor()
    J = side((0, 0), 104, [(0, 0)], plank_legs(), ground=211)
    J = side((J["hip"][0] + 100, J["hip"][1]), 104, [(0, 0)], plank_legs())
    body(J, feet=False)


def dip():
    floor()
    frame((90, 208), (90, 142))
    frame((170, 208), (170, 142))
    line([(82, 139), (178, 139)], 6, ACC)
    J = side((122, 138), 172, [(-25, 8)], [(10, -70)])
    body(J, feet=False)


def pull_up():
    line([(40, 22), (200, 22)], 6, ACC)
    frame((48, 22), (48, 8))
    frame((192, 22), (192, 8))
    J = front(120, 72, (125, 172), (6, 3), sh=36)
    fbody(J)


def lat_pulldown():
    floor()
    J = front(120, 104, (125, 170), (40, 0), th=20)
    pad((92, 166), (148, 166))
    frame((120, 172), (120, 208))
    cable((120, 56), (120, 12))
    fbody(J)
    line([(46, 58), (194, 58)], 6, ACC)
    line([(82, 172), (158, 172)], 9, ACC)


def seated_cable_row():
    column(212, 110)
    pad((60, 182), (112, 182))
    frame((72, 188), (72, 208))
    frame((104, 188), (104, 208))
    line([(168, 172), (176, 204)], 7, FRAME)
    J = side((84, 168), 178, [(-25, 82)], [(78, 62)])
    cable(J["hand"], (212, 150))
    body(J)
    handle(J["hand"], 0, 7)


def barbell_row():
    J = standing([(-12, 25)], torso=112, legs=((22, -8),))
    body(J)
    plate(J["hand"], 17)


def dumbbell_row():
    floor()
    bench(70, 176, 180)
    J = side((88, 132), 96, [(4, -4), (-55, 5)], [(-28, -12), (2, -90)])
    leg(J, 0, BACK, True)
    limb(J["sh"], *J["arms"][0], BACK)
    leg(J, 1, BODY, False, halo=True)
    line([J["hip"], J["sh"]], 18, BODY)
    dot(J["head"], 12.5, BODY)
    limb(J["sh"], *J["arms"][1], BODY, halo=True)
    db(J["hand"], 10)


def deadlift():
    J = standing([(0, 0)], torso=135, legs=((38, -6),))
    body(J)
    plate(J["hand"], 21)


def back_extension():
    floor()
    frame((62, 208), (104, 150))
    frame((150, 208), (104, 150))
    J = side((112, 128), 128, [(35, 175)], [(-52, -52)])
    pad((94, 142), (122, 150), 10)
    line([(40, 196), (52, 204)], 8, ACC)
    body(J, feet=False)


def overhead_press():
    J = standing([(125, 180)])
    body(J)
    plate(J["hand"], 15)


def dumbbell_shoulder_press():
    floor()
    J = front(120, 84, (118, 180), (6, 3))
    fbody(J)
    for k in (0, 1):
        dbl(J["arms"][k][1], 90)


def shoulder_press_machine():
    J = seated([(128, 180)])
    frame((66, 208), (66, 60), (J["hand"][0], J["hand"][1] - 2))
    body(J)
    handle(J["hand"], 90)


def lateral_raise():
    floor()
    J = front(120, 84, (82, 86), (6, 3))
    fbody(J)
    for k in (0, 1):
        dbl(J["arms"][k][1], 90, 9)


def front_raise():
    J = standing([(0, 2), (88, 90)])
    body(J)
    db(J["arms"][0][1], 8)
    db(J["hand"], 9)


def face_pull():
    column(210, 30)
    J = side((84, 0), 184, [(96, 150)], [(-12, -8), (10, 4)], ground=211)
    cable(J["hand"], (210, 62))
    body(J)
    handle(J["hand"], 0, 6)


def barbell_curl():
    J = standing([(2, 118)])
    body(J)
    plate(J["hand"], 13)


def dumbbell_curl():
    J = standing([(0, 4), (2, 125)])
    body(J)
    db(J["arms"][0][1], 8)
    db(J["hand"], 9)


def hammer_curl():
    J = standing([(0, 4), (2, 92)])
    body(J)
    dbl(J["arms"][0][1], 90, 8)
    dbl(J["hand"], 0, 9)


def preacher_curl():
    floor()
    pad((70, 180), (112, 180))
    frame((90, 186), (90, 208))
    frame((146, 208), (146, 150))
    J = side((88, 166), 168, [(52, 150)], [(88, 0)])
    pad((112, 116), (150, 152), 9)
    body(J)
    plate(J["hand"], 12)


def triceps_pushdown():
    column(204, 20)
    J = side((104, 0), 172, [(6, 62)], [(-6, -3), (5, 3)], ground=211)
    line([(204, 24), (J["hand"][0], 24)], 5, FRAME)
    cable(J["hand"], (J["hand"][0], 26))
    body(J)
    handle(J["hand"], 90, 7)


def overhead_triceps_extension():
    J = standing([(172, -80)])
    body(J)
    head_on_top(J)
    db(J["hand"], 10)


def skull_crusher():
    J = lying([(180, -80)])
    body(J)
    plate(J["hand"], 12)
    floor()


def bench_dip():
    floor()
    bench(28, 100, 178)
    J = side((112, 180), 180, [(-42, 2)], [(80, 58)])
    body(J)


def squat():
    J = standing([(22, 202)], torso=152, legs=((76, -20),))
    body(J)
    plate(add(J["sh"], (-11, 1)), 15)


def leg_press():
    floor()
    frame((40, 208), (200, 208))
    pad((96, 186), (62, 124))
    pad((74, 190), (104, 190))
    J = side((90, 174), -151, [(8, 60)], [(118, 100)])
    f = J["foot"]
    frame((f[0] + 12, f[1] + 8), (150, 206))
    body(J, feet=False)
    line([add(f, v(190, 26)), add(f, v(10, 22))], 7, ACC)
    plate(add(f, (26, 6)), 14)


def leg_extension():
    J = seated([(4, 20)], legs=((90, 72),))
    frame((96, 208), (140, 208), (140, 176))
    body(J, feet=False)
    dot(add(J["foot"], (-6, -11)), 7, ACC)


def leg_curl():  # lying
    floor()
    pad((70, 164), (190, 164))
    frame((88, 170), (88, 208))
    frame((172, 170), (172, 208))
    J = side((122, 152), 91, [(25, 95)], [(-90, 162)])
    body(J, feet=False)
    dot(add(J["foot"], (-12, 4)), 7, ACC)


def lunge():
    floor()
    J = side((108, 0), 180, [(0, 0)], [(-16, -78), (80, 0)], ground=211)
    body(J, back_arm=False)
    db(J["hand"], 9)


def bulgarian_split_squat():
    floor()
    bench(24, 86, 170)
    J = side((126, 132), 172, [(0, 0)], [(-28, -112), (68, 2)])
    body(J, back_arm=False)
    db(J["hand"], 9)


def romanian_deadlift():
    J = standing([(0, 0)], torso=112, legs=((10, -4),))
    body(J)
    plate(J["hand"], 17)


def hip_thrust():
    floor()
    bench(20, 80, 178)
    J = side((130, 160), -80, [(96, 118)], [(75, 0)])
    body(J)
    plate((130, 147), 17)


def hip_abduction_machine():
    floor()
    line([(120, 74), (120, 150)], 40, FRAME)
    J = front(120, 96, (12, -20), (62, 6), th=30)
    pad((90, 160), (150, 160))
    fbody(J)
    for k, sign in enumerate((-1, 1)):
        kn = J["legs"][k][0]
        line([add(kn, (sign * 11, -12)), add(kn, (sign * 11, 12))], 7, ACC)


def calf_raise():
    floor()
    line([(96, 201), (150, 201)], 14, FRAME)
    J = side((116, 105), 180, [(0, 2)], [(0, 0)])
    body(J, feet=False)
    ft = J["foot"]
    line([ft, add(ft, (9, 6))], 9, BODY)
    db(J["hand"], 9)


def goblet_squat():
    J = standing([(25, 165)], torso=160, legs=((76, -20),))
    body(J)
    db(J["hand"], 11)


def cable_kickback():
    column(204, 60)
    J = side((112, 0), 140, [(78, 84)], [(-52, -58), (4, 0)], ground=211)
    kn, ft, _ = J["legs"][0]
    cable(ft, (204, 198))
    leg(J, 0, BACK, True)
    leg(J, 1, BODY, True, halo=True)
    line([J["hip"], J["sh"]], 18, BODY)
    dot(J["head"], 12.5, BODY)
    limb(J["sh"], *J["arms"][0], BODY, halo=True)


def plank():
    floor()
    J = side((0, 0), 100, [(0, 90)], [(-75, -75)], ground=211)
    J = side((J["hip"][0] + 104, J["hip"][1]), 100, [(0, 90)], [(-75, -75)])
    body(J, feet=False)


def side_plank():
    floor()
    J = side((0, 0), 103, [(180, 180), (0, 90)], [(-77, -77)], ground=211)
    J = side((J["hip"][0] + 104, J["hip"][1]), 103, [(180, 180), (0, 90)], [(-77, -77)])
    leg(J, 0, BODY, False)
    limb(J["sh"], *J["arms"][0], BODY)
    line([J["hip"], J["sh"]], 18, BODY)
    dot(J["head"], 12.5, BODY)
    limb(J["sh"], *J["arms"][1], BODY, halo=True)


def crunch():
    floor()
    J = side((118, 196), -116, [(100, 104)], [(126, 18)])
    body(J)


def hanging_leg_raise():
    frame((52, 208), (52, 22), (128, 22))
    line([(36, 208), (68, 208)], 6, FRAME)
    J = side((122, 142), 180, [(180, 180)], [(88, 86)])
    body(J)
    head_on_top(J)
    dot(J["hand"], 6, ACC)


def russian_twist():
    floor()
    J = side((112, 194), -152, [(72, 86)], [(116, 76)])
    body(J)
    plate(J["hand"], 11)


def cable_crunch():
    column(204, 20)
    J = side((96, 0), 132, [(105, 195)], [(14, -90)], ground=211)
    line([(204, 24), (J["hand"][0], 24)], 5, FRAME)
    cable(J["hand"], (J["hand"][0], 26))
    body(J, feet=False)


def mountain_climber():
    floor()
    legs = [(-66, -66), (38, -55)]
    J = side((0, 0), 104, [(0, 0)], [legs[0]], ground=211)
    J = side((J["hip"][0] + 100, J["hip"][1]), 104, [(0, 0)], legs)
    body(J, feet=False)


EXERCISES = [
    bench_press, incline_dumbbell_press, dumbbell_fly, chest_press_machine, pec_deck, cable_crossover, push_up, dip,
    pull_up, lat_pulldown, seated_cable_row, barbell_row, dumbbell_row, deadlift, back_extension,
    overhead_press, dumbbell_shoulder_press, shoulder_press_machine, lateral_raise, front_raise, face_pull,
    barbell_curl, dumbbell_curl, hammer_curl, preacher_curl, triceps_pushdown, overhead_triceps_extension, skull_crusher, bench_dip,
    squat, leg_press, leg_extension, leg_curl, lunge, bulgarian_split_squat, romanian_deadlift, hip_thrust,
    hip_abduction_machine, calf_raise, goblet_squat, cable_kickback,
    plank, side_plank, crunch, hanging_leg_raise, russian_twist, cable_crunch, mountain_climber,
]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for f in EXERCISES:
        im = Image.new("RGBA", (N * S, N * S), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        f()
        im.resize((480, 480), Image.LANCZOS).save(os.path.join(OUT, f.__name__ + ".png"), optimize=True)
    print(len(EXERCISES), "figures written to", OUT)
