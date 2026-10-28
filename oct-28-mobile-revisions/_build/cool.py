"""Cool down warm/yellow photos: neutralise the yellow cast, keep reds (sauce, brand) intact."""
import sys
import numpy as np
from PIL import Image

def cool(img, strength=1.0):
    mode = img.mode
    alpha = img.getchannel('A') if 'A' in mode else None
    rgb = np.asarray(img.convert('RGB')).astype(np.float32) / 255.0
    # 1) white-balance shift toward blue (mild), weighted so shadows/highlights move less
    lum = rgb @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    w = (np.clip(lum * (1 - lum) * 4, 0, 1) * 0.6 + 0.4)[..., None] * strength
    gains = np.array([-0.035, -0.008, 0.05], np.float32)
    rgb = rgb + w * gains * (0.35 + rgb)
    # 2) pull saturation out of yellow/amber hues only (≈35°–65°)
    mx = rgb.max(-1); mn = rgb.min(-1); d = mx - mn + 1e-6
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    yellow = np.clip(1 - np.abs(h - 48) / 22, 0, 1) * strength
    grey = lum[..., None]
    rgb = rgb - (rgb - grey) * (0.18 * yellow)[..., None]
    out = Image.fromarray((np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8), 'RGB')
    if alpha is not None:
        out.putalpha(alpha)
    return out

if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    im = Image.open(src)
    o = cool(im)
    if dst.lower().endswith(('.jpg', '.jpeg')):
        o.convert('RGB').save(dst, quality=86, optimize=True, progressive=True)
    else:
        o.save(dst, optimize=True)
