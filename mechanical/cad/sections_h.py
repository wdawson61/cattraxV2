import math, json, cadquery as cq
import pod_v3 as p, cap_screw as cs, sensor_h as sh
from collar_parts import R0, th, place, box, W, ring_sector, radial_cyl, band_w, band_t, skin
cell = p.cell_solid()
ins = place(p.insert_local(), p.FACE_BX, R0 + skin)
env, xs, ws, hs = p.envelope()
rec = place(p.recess_local(), p.FACE_BX, R0 + skin)
tg = sh.tongue(); st = sh.stiffener(); ic, c0201 = sh.sensor()
sil = env.cut(W(cell)).cut(W(ins)).cut(W(rec)).cut(tg).cut(st).cut(ic).cut(c0201)
# band from the tracker side into the pod, with its flex at 1.6
bandL = W(ring_sector(R0, R0 + band_t, -band_w/2, band_w/2, 40, 66.5)).cut(W(ring_sector(R0+1.6, R0+1.71, -4, 4, 40, 66.5)))
flexL = W(ring_sector(R0+1.6, R0+1.71, -4, 4, 40, 66.5))
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
    tail = tail.cut(W(radial_cyl(hx, R0, 9, 1.8))); flex = flex.cut(W(radial_cyl(hx, R0, 9, 1.8))); stiff = stiff.cut(W(radial_cyl(hx, R0, 9, 1.8)))
parts = {"sil": sil, "cell": W(cell), "ins": W(ins), "shell": shell, "base": base, "mpod": m_pod, "mcap": m_cap,
         "tail": tail, "flex": flex.union(tg).union(flexL), "stiff": stiff.union(st), "screws": hw["screws"], "nuts": hw["nuts"],
         "hall": ic.union(c0201), "band": bandL}
half = box(-200, 200, -200, 200, -50, 0)
for k, v in parts.items():
    s = v.intersect(half)
    if s.vals(): cq.exporters.export(s, f"/tmp/hA_{k}.stl", tolerance=0.01, angularTolerance=0.1)
cutE = W(ring_sector(0.5, 80, -40, 40, sh.XS - 60, sh.XS))
for k in ("sil", "cell", "flex", "hall", "stiff"):
    s = parts[k].intersect(cutE)
    if s.vals(): cq.exporters.export(s, f"/tmp/hE_{k}.stl", tolerance=0.01, angularTolerance=0.1)
cutF = W(ring_sector(0.5, 80, -40, 40, 102.5 - 60, 102.5))     # cell middle: thinnest point over the tongue
for k in ("sil", "cell", "flex"):
    s = parts[k].intersect(cutF)
    if s.vals(): cq.exporters.export(s, f"/tmp/hF_{k}.stl", tolerance=0.01, angularTolerance=0.1)
for k in ("tg", "ic"):
    pass
cq.exporters.export(tg, "v3h_hall_tongue.step"); cq.exporters.export(st, "v3h_hall_stiffener.step")
# plan view of the flex end (from outside, looking at the neck)
for k, v in {"flex": tg, "stiff": st, "hall": ic.union(c0201)}.items():
    cq.exporters.export(v, f"/tmp/hP_{k}.stl", tolerance=0.01, angularTolerance=0.1); cq.exporters.export(ic.union(c0201), "v3h_hall_sensor.step")
cq.exporters.export(sil, "v3h_pod_silicone.step"); cq.exporters.export(sil, "v3h_pod_silicone.stl", tolerance=0.02, angularTolerance=0.1)
json.dump({"face": p.FACE_BX, "sx": sx, "x_end": x_end, "t0": t0, "XS": sh.XS, "hc": p.clasp_h,
           "base": cs.BASE_T, "endh": cs.END_H, "xm": p.FACE_BX + p.cap_gap + p.mag_skin + 1.5}, open("/tmp/hs.json", "w"))
print("ok", sil.val().isValid())
