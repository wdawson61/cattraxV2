import math, json, cadquery as cq
import pod_v3 as p, cap_screw as cs
from collar_parts import R0, th, place, box, W, ring_sector, radial_cyl, band_w, band_t, skin
cell = p.cell_solid()
ins = place(p.insert_local(), p.FACE_BX, R0 + skin)
env, xs, ws, hs = p.envelope()
rec = place(p.recess_local(), p.FACE_BX, R0 + skin)
sil = env.cut(W(cell)).cut(W(ins)).cut(W(rec))
shell, base, hw, info = cs.cap_parts(ws[-1], hs[-1])
zc0 = p.clasp_h - skin
m_pod = cq.Workplane("YZ", origin=(-p.recess_depth - p.mag_skin - p.mag[0], 0, zc0)).rect(p.mag[1], p.mag[2]).extrude(p.mag[0])
m_cap = cq.Workplane("YZ", origin=(p.cap_gap - p.recess_depth + p.mag_skin + 0.03, 0, zc0)).rect(p.mag[1], p.mag[2]).extrude(p.mag[0])
m_pod = W(place(m_pod, p.FACE_BX, R0 + skin)); m_cap = W(place(m_cap, p.FACE_BX, R0 + skin))
x_end = info["x_end"]; sx = info["screws_x"]
t0 = sx[1] - 1.8
r_t = R0 + cs.BASE_T + 0.05
tail = W(ring_sector(r_t, r_t + band_t, -band_w/2, band_w/2, t0, x_end + 28))
flex = W(ring_sector(r_t + 1.6, r_t + 1.72, -4, 4, t0 + 0.5, x_end + 28))
stiff = W(ring_sector(r_t + 1.72, r_t + 1.92, -4, 4, t0 + 0.5, x_end + 28))
holes = [sx[0] + 5*k for k in range(-1, 6)]
for hx in holes:
    for nm in ("tail", "flex", "stiff"):
        globals()[nm] = globals()[nm].cut(W(radial_cyl(hx, R0, 9, 1.8)))
parts = {"sil": sil, "cell": W(cell), "ins": W(ins), "shell": shell, "base": base, "mpod": m_pod, "mcap": m_cap,
         "tail": tail, "flex": flex, "stiff": stiff, "screws": hw["screws"], "nuts": hw["nuts"]}
half = box(-200, 200, -200, 200, -50, 0)
for k, v in parts.items():
    s = v.intersect(half)
    if s.vals(): cq.exporters.export(s, f"/tmp/sA_{k}.stl", tolerance=0.01, angularTolerance=0.1)
cutC = W(ring_sector(0.5, 80, -40, 40, sx[0] - 60, sx[0]))
for k in ("shell", "base", "tail", "flex", "stiff", "screws", "nuts"):
    s = parts[k].intersect(cutC)
    if s.vals(): cq.exporters.export(s, f"/tmp/sC_{k}.stl", tolerance=0.01, angularTolerance=0.1)
xm = p.FACE_BX + p.cap_gap + p.mag_skin + 1.5          # through the cap magnet
cutD = W(ring_sector(0.5, 80, -40, 40, xm - 60, xm))
for k in ("shell", "base", "mcap"):
    s = parts[k].intersect(cutD)
    if s.vals(): cq.exporters.export(s, f"/tmp/sD_{k}.stl", tolerance=0.01, angularTolerance=0.1)
json.dump({"face": p.FACE_BX, "sx": sx, "x_end": x_end, "t0": t0, "xm": xm, "hc": p.clasp_h,
           "base": cs.BASE_T, "endh": cs.END_H}, open("/tmp/ss.json", "w"))
print("ok")
