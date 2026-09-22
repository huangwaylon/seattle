"""Find vertical seams in a screenshot — a straight dark or bright column is the artifact a blended,
animated layer leaves behind, and the eye catches it long before a still frame does.

    python3 .map/seam.py shot.png [x0 y0 x1 y1]

Reads the PNG with zlib alone (no Pillow here), averages luminance per column inside the box, and
reports any column that sits far off its neighbours. Not shipped.
"""
import struct
import sys
import zlib


def read_png(path):
    d = open(path, 'rb').read()
    assert d[:8] == b'\x89PNG\r\n\x1a\n', 'not a PNG'
    i, idat, w = 8, b'', None
    while i < len(d):
        ln = struct.unpack('>I', d[i:i + 4])[0]
        typ = d[i + 4:i + 8]
        body = d[i + 8:i + 8 + ln]
        if typ == b'IHDR':
            w, h, depth, colour = struct.unpack('>IIBB', body[:10])
            assert depth == 8 and colour in (2, 6), 'want 8-bit RGB/RGBA'
            nch = 3 if colour == 2 else 4
        elif typ == b'IDAT':
            idat += body
        elif typ == b'IEND':
            break
        i += 12 + ln
    raw = zlib.decompress(idat)
    stride = w * nch
    out, prev = [], bytearray(stride)
    p = 0
    for _ in range(h):
        f = raw[p]
        line = bytearray(raw[p + 1:p + 1 + stride])
        p += 1 + stride
        if f == 1:
            for x in range(nch, stride):
                line[x] = (line[x] + line[x - nch]) & 255
        elif f == 2:
            for x in range(stride):
                line[x] = (line[x] + prev[x]) & 255
        elif f == 3:
            for x in range(stride):
                left = line[x - nch] if x >= nch else 0
                line[x] = (line[x] + ((left + prev[x]) >> 1)) & 255
        elif f == 4:
            for x in range(stride):
                a = line[x - nch] if x >= nch else 0
                b = prev[x]
                c = prev[x - nch] if x >= nch else 0
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                pr = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                line[x] = (line[x] + pr) & 255
        out.append(line)
        prev = line
    return w, h, nch, out


def columns(w, h, nch, rows, box):
    x0, y0, x1, y1 = box
    means = []
    for x in range(x0, x1):
        s = 0
        for y in range(y0, y1):
            r, g, b = rows[y][x * nch:x * nch + 3]
            s += 0.2126 * r + 0.7152 * g + 0.0722 * b
        means.append(s / (y1 - y0))
    return means


def seams(means, x0, k=2.6):
    """A seam is a column that differs from the local trend far more than its neighbours do."""
    devs = []
    for i in range(2, len(means) - 2):
        local = (means[i - 2] + means[i - 1] + means[i + 1] + means[i + 2]) / 4
        devs.append((abs(means[i] - local), i, means[i] - local))
    if not devs:
        return []
    typical = sorted(d[0] for d in devs)[len(devs) // 2]
    return [(x0 + i, round(delta, 2)) for d, i, delta in devs if d > max(1.2, typical * k)]


def bands(means, x0, half=22):
    """A soft seam is a run of columns sitting below (or above) a much wider neighbourhood — the
    single-column test misses those, and those are the ones the eye follows."""
    out = []
    for i in range(len(means)):
        lo, hi = max(0, i - half), min(len(means), i + half + 1)
        window = means[lo:i] + means[i + 1:hi]
        if not window:
            continue
        out.append(means[i] - sum(window) / len(window))
    return out


if __name__ == '__main__':
    path = sys.argv[1]
    w, h, nch, rows = read_png(path)
    box = tuple(int(v) for v in sys.argv[2:6]) if len(sys.argv) > 5 else (0, 0, w, h)
    means = columns(w, h, nch, rows, box)
    found = seams(means, box[0])
    print('%s  box=%s' % (path.split('/')[-1], box))
    if found:
        for x, delta in found[:6]:
            print('  hard column %d  %+.2f' % (x, delta))
    b = bands(means, box[0])
    worst = min(range(len(b)), key=lambda i: b[i])
    best = max(range(len(b)), key=lambda i: b[i])
    print('  widest dark band : column %d  %+.2f vs a 45px window' % (box[0] + worst, b[worst]))
    print('  widest light band: column %d  %+.2f vs a 45px window' % (box[0] + best, b[best]))
