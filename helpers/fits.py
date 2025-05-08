from astropy.io import fits
from astropy.io.fits.convenience import writeto
import numpy as np
import sys
import os
import time

def stitched_path(src_path):
    stitched_path = src_path.replace("/raw/", "/stitched/")
    if "mir3" in src_path:
        if not os.path.exists(os.path.dirname(stitched_path)):
            os.mkdir(os.path.dirname(stitched_path))
        if not os.path.exists(stitched_path) or os.path.getctime(src_path) > os.path.getctime(stitched_path):
            stitch_file(src_path, stitched_path)
        return stitched_path
    else:
        return src_path

def stitch_file(src_path, dest_path):
    hdus = fits.open(src_path)
    chips = []
    for hdu in hdus[1:]:
        chips.append(hdu.data)
    full = np.hstack(chips[::-1])
    header = hdus[0].header
    header['EXTEND'] = False
    out_hdus = fits.HDUList([fits.PrimaryHDU(header=header, data=full)])
    out_hdus.writeto(dest_path, overwrite=True)
    return True
