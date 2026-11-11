"""Minimal Mapbox Vector Tile decoder, enough to read GBIF binned density tiles.

Returns, per feature, its properties and the bounding box of its geometry in tile units.
"""


def _varint(b, i):
    r = s = 0
    while True:
        c = b[i]; i += 1
        r |= (c & 0x7F) << s
        if c < 0x80:
            return r, i
        s += 7


def _fields(b):
    i, n = 0, len(b)
    while i < n:
        key, i = _varint(b, i)
        f, t = key >> 3, key & 7
        if t == 0:
            v, i = _varint(b, i)
        elif t == 1:
            v = b[i:i + 8]; i += 8
        elif t == 2:
            ln, i = _varint(b, i); v = b[i:i + ln]; i += ln
        elif t == 5:
            v = b[i:i + 4]; i += 4
        else:
            raise ValueError("wire type %d" % t)
        yield f, t, v


def _packed(b):
    out, i = [], 0
    while i < len(b):
        v, i = _varint(b, i); out.append(v)
    return out


def _value(b):
    import struct
    for f, t, v in _fields(b):
        if f == 1: return v.decode()
        if f == 2: return struct.unpack("<f", v)[0]
        if f == 3: return struct.unpack("<d", v)[0]
        if f in (4, 5): return v
        if f == 6: return (v >> 1) ^ -(v & 1)
        if f == 7: return bool(v)


def _bbox(cmds):
    x = y = 0
    xs, ys = [], []
    i = 0
    while i < len(cmds):
        c = cmds[i]; i += 1
        op, cnt = c & 7, c >> 3
        if op in (1, 2):
            for _ in range(cnt):
                dx, dy = cmds[i], cmds[i + 1]; i += 2
                x += (dx >> 1) ^ -(dx & 1); y += (dy >> 1) ^ -(dy & 1)
                xs.append(x); ys.append(y)
    return min(xs), min(ys), max(xs), max(ys)


def decode(data):
    layers = []
    for f, t, v in _fields(data):
        if f != 3: continue
        name, keys, vals, feats, extent = None, [], [], [], 4096
        for lf, lt, lv in _fields(v):
            if lf == 1: name = lv.decode()
            elif lf == 2: feats.append(lv)
            elif lf == 3: keys.append(lv.decode())
            elif lf == 4: vals.append(_value(lv))
            elif lf == 5: extent = lv
        out = []
        for fb in feats:
            tags, geom = [], []
            for ff, ft, fv in _fields(fb):
                if ff == 2: tags = _packed(fv)
                elif ff == 4: geom = _packed(fv)
            props = {keys[tags[k]]: vals[tags[k + 1]] for k in range(0, len(tags), 2)}
            out.append((props, _bbox(geom) if geom else None))
        layers.append({"name": name, "extent": extent, "features": out})
    return layers
