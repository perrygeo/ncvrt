#!/usr/bin/env python
from __future__ import print_function
import subprocess
import click
from xml.etree.ElementTree import parse, tostring
from copy import deepcopy
from tempfile import NamedTemporaryFile


@click.command()
@click.argument('filename')
@click.option('--wrap', is_flag=True, default=False, help='Wrap longitude from 0-360 to -180,180')
@click.option('--flip', is_flag=True, default=False, help='Flip yaxis orientation using geotransforms')
def ncvrt(filename, wrap, flip):
    with NamedTemporaryFile(delete=False) as fh:
        tmpvrt = fh.name
    subprocess.check_output(["gdal_translate", "-of", "VRT", filename, tmpvrt])

    root = parse(tmpvrt).getroot()
    gt = root.find("GeoTransform")
    c, a, b, f, d, e = [float(x.strip()) for x in gt.text.split(',')]

    # xsize = dict(root.items())['rasterXSize']
    ysize = float(dict(root.items())['rasterYSize'])

    if flip:
        f = f + (ysize * e)
        e *= -1

    if wrap:
        # TODO confirm that it is centered on prime meridian with even pixels
        c = -180.0

        bands = root.findall("VRTRasterBand")
        for band in bands:
            ssource = band.find("SimpleSource")
            srcrect = ssource.find("SrcRect")
            dstrect = ssource.find("DstRect")
            rect = dict([(x[0], int(x[1])) for x in srcrect.items()])
            halfx = str(int(rect['xSize'] / 2.0))  # TODO confirm even

            east = deepcopy(ssource)
            srcrect = east.find("SrcRect")
            dstrect = east.find("DstRect")
            srcrect.set('xSize', halfx)
            dstrect.set('xSize', halfx)
            srcrect.set('xOff', halfx)

            west = deepcopy(ssource)
            srcrect = west.find("SrcRect")
            dstrect = west.find("DstRect")
            srcrect.set('xSize', halfx)
            dstrect.set('xSize', halfx)
            dstrect.set('xOff', halfx)

            band.remove(ssource)
            band.insert(-1, east)
            band.insert(-1, west)

    gts = ", ".join(str(x) for x in [c, a, b, f, d, e])
    gt.text = gts

    print(tostring(root, encoding='unicode'))

if __name__ == "__main__":
    ncvrt()
