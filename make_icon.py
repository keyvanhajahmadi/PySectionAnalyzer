"""Generate KP logo multi-size .ico using Pillow + manual ICO writer."""
from PIL import Image, ImageDraw, ImageFont
import os, struct

SIZES = [16, 32, 48, 64, 128]
gold = (244, 201, 74)
gold_dark = (200, 137, 10)
blue = (74, 159, 225)
blue_dark = (26, 95, 154)
bg = (14, 30, 53)

def make_frame(SIZE):
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx = cy = SIZE // 2
    r = SIZE // 2 - 2
    scale = (r - 2) / 190
    def sx(x): return cx + (x - 200) * scale
    def sy(y): return cy + (y - 200) * scale

    lw = max(1, SIZE // 32)
    dw = max(1, SIZE // 48)

    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=bg, outline=gold, width=lw)
    if SIZE >= 32:
        draw.ellipse([cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4], outline=(30, 58, 96), width=1)

    btm = [70, 110, 155, 200, 245, 290, 330]
    top = [110, 155, 200, 245, 290]
    yb, yt = 270, 175
    b = [sx(x) for x in btm]
    t = [sx(x) for x in top]
    yb_s, yt_s = sy(yb), sy(yt)

    draw.line([b[0], yb_s, b[-1], yb_s], fill=blue, width=dw)
    draw.line([t[0], yt_s, t[-1], yt_s], fill=blue, width=dw)

    for i in range(1, len(btm) - 1):
        draw.line([b[i], yb_s, t[i-1], yt_s], fill=blue_dark, width=dw)
    for i in range(len(top)):
        if i + 1 < len(btm):
            draw.line([b[i+1], yb_s, t[i], yt_s], fill=blue_dark, width=dw)
            draw.line([b[i], yb_s, t[i], yt_s], fill=blue_dark, width=dw)

    draw.line([b[0], yb_s, t[0], yt_s], fill=blue, width=dw)
    draw.line([b[-1], yb_s, t[-1], yt_s], fill=blue, width=dw)

    if SIZE >= 32:
        pairs = [(top[0], btm[2]), (btm[3], top[2]), (top[3], btm[4]), (btm[5], top[4])]
        for x1, x2 in pairs:
            draw.line([sx(x1), sy(yt), sx(x2), sy(yb)], fill=gold_dark, width=max(1, dw-1))

    nr = max(1, SIZE // 16)
    for px in b:
        draw.ellipse([px - nr, yb_s - nr, px + nr, yb_s + nr], fill=gold)
    for px in t:
        draw.ellipse([px - nr, yt_s - nr, px + nr, yt_s + nr], fill=gold)
    draw.ellipse([t[2] - nr - 1, yt_s - nr - 1, t[2] + nr + 1, yt_s + nr + 1], fill=gold)

    if SIZE >= 32:
        n1, n2 = max(1, SIZE // 16), max(2, SIZE // 10)
        draw.polygon([b[0], yb_s + n1, b[0] - n1, yb_s + n2, b[0] + n1, yb_s + n2], fill=gold)
        draw.polygon([b[-1], yb_s + n1, b[-1] - n1, yb_s + n2, b[-1] + n1, yb_s + n2], fill=gold)

    fx, fy = t[2], yt_s - cx // 4
    draw.line([fx, fy - cx // 6, fx, fy + 2], fill=gold, width=dw)
    draw.polygon([fx, fy + 4, fx - 2, fy - 1, fx + 2, fy - 1], fill=gold)

    if SIZE >= 32:
        fsize = max(5, SIZE // 7)
        try:
            font = ImageFont.truetype("segoeui.ttf", fsize)
        except:
            font = ImageFont.load_default()
        kp_y = sy(340)
        draw.text((cx, kp_y), "KP", fill=gold, font=font, anchor="mm")
        # PySectionAnalyzer subtext
        try:
            font2 = ImageFont.truetype("segoeui.ttf", max(4, SIZE // 12))
        except:
            font2 = ImageFont.load_default()
        draw.text((cx, sy(352)), "PyStructAnalyzer", fill=blue, font=font2, anchor="mm")

    return img


def write_ico(images, path):
    """Write multi-size ICO file manually."""
    count = len(images)
    header_size = 6 + count * 16
    data_offset = header_size
    entries = []
    all_data = b""

    for img in images:
        w, h = img.size
        # Convert RGBA to BGRA for BMP
        pixels = bytearray()
        and_mask = bytearray()
        row_size = ((w * 32 + 31) // 32) * 4  # 32bpp row stride
        and_row_size = ((w + 31) // 32) * 4   # 1bpp row stride

        # BMP stores bottom-up
        for y in range(h - 1, -1, -1):
            for x in range(w):
                r, g, b, a = img.getpixel((x, y))
                pixels.extend([b, g, r, a])
            # Pad row
            pixels.extend([0] * (row_size - w * 4))
            # AND mask row (1 = transparent, 0 = opaque)
            and_bytes = bytearray()
            for x in range(0, w, 8):
                byte = 0
                for bit in range(8):
                    if x + bit < w:
                        _, _, _, a = img.getpixel((x + bit, y))
                        if a < 128:
                            byte |= (1 << (7 - bit))
                and_bytes.append(byte)
            # Pad AND row
            and_bytes.extend([0] * (and_row_size - len(and_bytes)))
            and_mask.extend(and_bytes)

        # BITMAPINFOHEADER (40 bytes)
        bih = struct.pack("<IiiHHIIiiII",
            40,             # size
            w,              # width
            h * 2,          # height (doubled for ICO)
            1,              # planes
            32,             # bpp
            0,              # compression (BI_RGB)
            row_size * h + len(and_mask),  # image size
            0, 0, 0, 0      # colors, important colors
        )

        frame_data = bih + bytes(pixels) + bytes(and_mask)
        entries.append({
            "w": w if w < 256 else 0,
            "h": h if h < 256 else 0,
            "size": len(frame_data),
            "offset": data_offset,
        })
        all_data += frame_data
        data_offset += len(frame_data)

    with open(path, "wb") as f:
        # Header
        f.write(struct.pack("<HHH", 0, 1, count))
        # Directory entries
        for e in entries:
            f.write(struct.pack("<BBBBHHII",
                e["w"], e["h"], 0, 0, 1, 32, e["size"], e["offset"]))
        # Frame data
        f.write(all_data)

    print(f"ICO saved: {path} ({os.path.getsize(path)} bytes, {count} sizes)")


frames = [make_frame(s) for s in SIZES]
path = os.path.join(os.path.dirname(__file__), "kp_logo.ico")
write_ico(frames, path)
