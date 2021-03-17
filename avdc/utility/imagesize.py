# Copyright © 2016 Yoshiki Shibukawa
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the “Software”),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import re
import struct
from xml.etree import ElementTree

_UNIT_KM = -3
_UNIT_100M = -2
_UNIT_10M = -1
_UNIT_1M = 0
_UNIT_10CM = 1
_UNIT_CM = 2
_UNIT_MM = 3
_UNIT_0_1MM = 4
_UNIT_0_01MM = 5
_UNIT_UM = 6
_UNIT_INCH = 6

_TIFF_TYPE_SIZES = {
    1: 1,
    2: 1,
    3: 2,
    4: 4,
    5: 8,
    6: 1,
    7: 1,
    8: 2,
    9: 4,
    10: 8,
    11: 4,
    12: 8,
}


def _convertToDPI(density, unit):
    if unit == _UNIT_KM:
        return int(density * 0.0000254 + 0.5)
    elif unit == _UNIT_100M:
        return int(density * 0.000254 + 0.5)
    elif unit == _UNIT_10M:
        return int(density * 0.00254 + 0.5)
    elif unit == _UNIT_1M:
        return int(density * 0.0254 + 0.5)
    elif unit == _UNIT_10CM:
        return int(density * 0.254 + 0.5)
    elif unit == _UNIT_CM:
        return int(density * 2.54 + 0.5)
    elif unit == _UNIT_MM:
        return int(density * 25.4 + 0.5)
    elif unit == _UNIT_0_1MM:
        return density * 254
    elif unit == _UNIT_0_01MM:
        return density * 2540
    elif unit == _UNIT_UM:
        return density * 25400
    return density


def _convertToPx(value):
    matched = re.match(r"(\d+)(?:\.\d)?([a-z]*)$", value)
    if not matched:
        raise ValueError("unknown length value: %s" % value)
    else:
        length, unit = matched.groups()
        if unit == "":
            return int(length)
        elif unit == "cm":
            return int(length) * 96 / 2.54
        elif unit == "mm":
            return int(length) * 96 / 2.54 / 10
        elif unit == "in":
            return int(length) * 96
        elif unit == "pc":
            return int(length) * 96 / 6
        elif unit == "pt":
            return int(length) * 96 / 6
        elif unit == "px":
            return int(length)
        else:
            raise ValueError("unknown unit type: %s" % unit)


def getSize(fileobj) -> tuple[int, int]:
    height = -1
    width = -1

    try:
        head = fileobj.read(24)
        size = len(head)
        # handle GIFs
        if size >= 10 and head[:6] in (b'GIF87a', b'GIF89a'):
            # Check to see if content_type is correct
            try:
                width, height = struct.unpack("<hh", head[6:10])
            except struct.error:
                raise ValueError("Invalid GIF file")
        # see png edition spec bytes are below chunk length then and finally the
        elif size >= 24 and head.startswith(b'\211PNG\r\n\032\n') and head[12:16] == b'IHDR':
            try:
                width, height = struct.unpack(">LL", head[16:24])
            except struct.error:
                raise ValueError("Invalid PNG file")
        # Maybe this is for an older PNG version.
        elif size >= 16 and head.startswith(b'\211PNG\r\n\032\n'):
            # Check to see if we have the right content type
            try:
                width, height = struct.unpack(">LL", head[8:16])
            except struct.error:
                raise ValueError("Invalid PNG file")
        # handle JPEGs
        elif size >= 2 and head.startswith(b'\377\330'):
            try:
                fileobj.seek(0)  # Read 0xff next
                size = 2
                ftype = 0
                while not 0xc0 <= ftype <= 0xcf or ftype in [0xc4, 0xc8, 0xcc]:
                    fileobj.seek(size, 1)
                    byte = fileobj.read(1)
                    while ord(byte) == 0xff:
                        byte = fileobj.read(1)
                    ftype = ord(byte)
                    size = struct.unpack('>H', fileobj.read(2))[0] - 2
                # We are at a SOFn block
                fileobj.seek(1, 1)  # Skip `precision' byte.
                height, width = struct.unpack('>HH', fileobj.read(4))
            except struct.error:
                raise ValueError("Invalid JPEG file")
        # handle JPEG2000s
        elif size >= 12 and head.startswith(b'\x00\x00\x00\x0cjP  \r\n\x87\n'):
            fileobj.seek(48)
            try:
                height, width = struct.unpack('>LL', fileobj.read(8))
            except struct.error:
                raise ValueError("Invalid JPEG2000 file")
        # handle big endian TIFF
        elif size >= 8 and head.startswith(b"\x4d\x4d\x00\x2a"):
            offset = struct.unpack('>L', head[4:8])[0]
            fileobj.seek(offset)
            ifdsize = struct.unpack(">H", fileobj.read(2))[0]
            for i in range(ifdsize):
                tag, datatype, count, data = struct.unpack(">HHLL", fileobj.read(12))
                if tag == 256:
                    if datatype == 3:
                        width = int(data / 65536)
                    elif datatype == 4:
                        width = data
                    else:
                        raise ValueError("Invalid TIFF file: width column data type should be SHORT/LONG.")
                elif tag == 257:
                    if datatype == 3:
                        height = int(data / 65536)
                    elif datatype == 4:
                        height = data
                    else:
                        raise ValueError("Invalid TIFF file: height column data type should be SHORT/LONG.")
                if width != -1 and height != -1:
                    break
            if width == -1 or height == -1:
                raise ValueError("Invalid TIFF file: width and/or height IDS entries are missing.")
        elif size >= 8 and head.startswith(b"\x49\x49\x2a\x00"):
            offset = struct.unpack('<L', head[4:8])[0]
            fileobj.seek(offset)
            ifdsize = struct.unpack("<H", fileobj.read(2))[0]
            for i in range(ifdsize):
                tag, datatype, count, data = struct.unpack("<HHLL", fileobj.read(12))
                if tag == 256:
                    width = data
                elif tag == 257:
                    height = data
                if width != -1 and height != -1:
                    break
            if width == -1 or height == -1:
                raise ValueError("Invalid TIFF file: width and/or height IDS entries are missing.")
        # handle SVGs
        elif size >= 5 and head.startswith(b'<?xml'):
            try:
                fileobj.seek(0)
                root = ElementTree.parse(fileobj).getroot()
                width = _convertToPx(root.attrib["width"])
                height = _convertToPx(root.attrib["height"])
            except Exception:
                raise ValueError("Invalid SVG file")
    finally:
        pass

    return width, height


def getDPI(fileobj):
    x_dpi = -1
    y_dpi = -1

    try:
        head = fileobj.read(24)
        size = len(head)
        # handle GIFs
        # GIFs doesn't have density
        if size >= 10 and head[:6] in (b'GIF87a', b'GIF89a'):
            pass
        # see png edition spec bytes are below chunk length then and finally the
        elif size >= 24 and head.startswith(b'\211PNG\r\n\032\n'):
            chunk_offset = 8
            chunk = head[8:]
            while True:
                chunk_type = chunk[4:8]
                if chunk_type == b'pHYs':
                    try:
                        x_density, y_density, unit = struct.unpack(">LLB", chunk[8:])
                    except struct.error:
                        raise ValueError("Invalid PNG file")
                    if unit:
                        x_dpi = _convertToDPI(x_density, _UNIT_1M)
                        y_dpi = _convertToDPI(y_density, _UNIT_1M)
                    else:  # no unit
                        x_dpi = x_density
                        y_dpi = y_density
                    break
                elif chunk_type == b'IDAT':
                    break
                else:
                    try:
                        data_size, = struct.unpack(">L", chunk[0:4])
                    except struct.error:
                        raise ValueError("Invalid PNG file")
                    chunk_offset += data_size + 12
                    fileobj.seek(chunk_offset)
                    chunk = fileobj.read(17)
        # handle JPEGs
        elif size >= 2 and head.startswith(b'\377\330'):
            try:
                fileobj.seek(0)  # Read 0xff next
                size = 2
                ftype = 0
                while not 0xc0 <= ftype <= 0xcf:
                    if ftype == 0xe0:  # APP0 marker
                        fileobj.seek(7, 1)
                        unit, x_density, y_density = struct.unpack(">BHH", fileobj.read(5))
                        if unit == 1 or unit == 0:
                            x_dpi = x_density
                            y_dpi = y_density
                        elif unit == 2:
                            x_dpi = _convertToDPI(x_density, _UNIT_CM)
                            y_dpi = _convertToDPI(y_density, _UNIT_CM)
                        break
                    fileobj.seek(size, 1)
                    byte = fileobj.read(1)
                    while ord(byte) == 0xff:
                        byte = fileobj.read(1)
                    ftype = ord(byte)
                    size = struct.unpack('>H', fileobj.read(2))[0] - 2
            except struct.error:
                raise ValueError("Invalid JPEG file")
        # handle JPEG2000s
        elif size >= 12 and head.startswith(b'\x00\x00\x00\x0cjP  \r\n\x87\n'):
            fileobj.seek(32)
            # skip JP2 image header box
            header_size = struct.unpack('>L', fileobj.read(4))[0] - 8
            fileobj.seek(4, 1)
            found_res_box = False
            try:
                while header_size > 0:
                    print("headerSize", header_size)
                    box_header = fileobj.read(8)
                    box_type = box_header[4:]
                    print(box_type)
                    if box_type == 'res ':  # find resolution super box
                        found_res_box = True
                        header_size -= 8
                        print("found res super box")
                        break
                    print("@1", box_header)
                    box_size, = struct.unpack('>L', box_header[:4])
                    print("boxSize", box_size)
                    fileobj.seek(box_size - 8, 1)
                    header_size -= box_size
                if found_res_box:
                    while header_size > 0:
                        box_header = fileobj.read(8)
                        box_type = box_header[4:]
                        print(box_type)
                        if box_type == 'resd':  # Display resolution box
                            print("@2")
                            y_density, x_density, y_unit, x_unit = struct.unpack(">HHBB", fileobj.read(10))
                            x_dpi = _convertToDPI(x_density, x_unit)
                            y_dpi = _convertToDPI(y_density, y_unit)
                            break
                        box_size, = struct.unpack('>L', box_header[:4])
                        print("boxSize", box_size)
                        fileobj.seek(box_size - 8, 1)
                        header_size -= box_size
            except struct.error as e:
                print(e)
                raise ValueError("Invalid JPEG2000 file")
    finally:
        pass

    return x_dpi, y_dpi
