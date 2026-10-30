# usage: gif.py <frames_dir> <out.gif>   (frames rendered at 15fps; output 10fps, identical frames merged into one longer frame)
import sys, os, glob, subprocess
from PIL import Image, ImageChops
fr = sorted(glob.glob(os.path.join(os.path.abspath(sys.argv[1]), '*.png')))
pick = [fr[round(i * 1.5)] for i in range(int(len(fr) / 1.5))]
seq = []  # [path, duration]
prev = None
for p in pick:
    im = Image.open(p).convert('RGB')
    if prev is not None and ImageChops.difference(im, prev).getbbox() is None:
        seq[-1][1] += 0.1
    else:
        seq.append([p, 0.1]); prev = im
lst = sys.argv[2] + '.txt'
with open(lst, 'w') as f:
    for p, d in seq: f.write("file '%s'\nduration %.2f\n" % (p, d))
    f.write("file '%s'\n" % seq[-1][0])
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-vf',
                'split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle',
                '-fps_mode', 'vfr', '-loop', '0', sys.argv[2]], check=True)
os.remove(lst)
