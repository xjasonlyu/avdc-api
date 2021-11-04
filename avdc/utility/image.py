import imghdr
from io import BytesIO
from typing import Optional

import numpy as np
from PIL import Image, UnidentifiedImageError
from cachetools import cached, TTLCache

from avdc.utility.face_api import detect_faces
from avdc.utility.httpclient import get_blob, Session, ResponseStream
from avdc.utility.imagesize import getSize


@cached(cache=TTLCache(maxsize=1000, ttl=7200))
def getRemoteImageSizeByURL(url: str) -> tuple[int, int]:
    with Session() as session:
        r = session.get(url, stream=True)
        stream = ResponseStream(r.iter_content(chunk_size=64))
        return getSize(stream)[::-1]  # height, width


def getRawImageByURL(url: str, **kwargs) -> bytes:
    return get_blob(url, raise_for_status=True, **kwargs)


def getRawImageFormat(data: bytes) -> Optional[str]:
    with BytesIO(data) as f:
        fmt = imghdr.what(f)

        if fmt is None:  # fallback
            try:
                im: Image.Image = Image.open(f)
            except UnidentifiedImageError:
                pass
            else:
                fmt = im.format

    return fmt.lower() if isinstance(fmt, str) else None


def getRawImageSize(data: bytes) -> tuple[int, int]:
    return getImageSize(bytesToImage(data))  # height, width


def getImageSize(img: np.ndarray) -> tuple[int, int]:
    s = img.shape
    return s[0], s[1]  # height, width


def bytesToImage(data: bytes, mode: str = 'RGB') -> np.ndarray:
    with BytesIO(data) as f:
        im: Image.Image = Image.open(f)
        if mode:
            im = im.convert(mode)
        return np.array(im)


def imageToBytes(img: np.ndarray, fmt: str = 'JPEG', quality: int = 95, subsampling: int = 0) -> bytes:
    im: Image.Image = Image.fromarray(img)
    with BytesIO() as f:
        im.save(f,
                format=fmt,
                quality=quality,
                subsampling=subsampling)
        return f.getvalue()


def getFaceCenter(loc: tuple[int, int, int, int]) -> tuple[int, int]:
    return (loc[1] + loc[3]) // 2, (loc[0] + loc[2]) // 2


def findFaces(img: np.ndarray) -> list[tuple[int, int, int, int]]:
    return [(*reversed(face[0]), *reversed(face[2]))
            for face in detect_faces(imageToBytes(img))]


def sortFaces(faces: list[tuple[int, int, int, int]], reverse: bool = True):
    faces.sort(key=lambda x: abs(x[0] - x[2]) * abs(x[1] - x[3]),
               reverse=reverse)


def cropImage(img: np.ndarray,
              center: int = -1,
              scale: float = 2 / 3,
              tolerance: float = 0.01,
              default_to_right: bool = True,
              default_to_top: bool = True) -> np.ndarray:
    height, width = getImageSize(img)
    # expected width
    _width = int(height * scale)

    if _width >= width:
        if abs(width / height - scale) <= tolerance:
            # no need to crop
            return img

        _height = int(width / scale)

        if default_to_top:
            return img[:min(height, _height), :]
        else:  # fit to center
            x = abs(height - _height) // 2
            return img[x:height - x, :]

    # default to right side
    if center < 0 or (center > width // 2 and default_to_right):
        left, right = width - _width, width
        return img[:, left:right]

    left = min(max(0, center - (_width // 2)), width - _width)
    right = left + _width
    return img[:, left:right]


def autoCropImage(img: np.ndarray, face_detection: bool = True, pos: float = -1, **options) -> np.ndarray:
    if not face_detection or 0 <= pos <= 1:
        return cropImage(img,
                         center=int(pos * getImageSize(img)[1]),
                         default_to_right=False,
                         **options)

    # find and sort faces
    faces = findFaces(img)
    sortFaces(faces)

    return cropImage(img=img,
                     center=-1 if not faces  # no faces detected
                     else getFaceCenter(faces[0])[0],  # x
                     **options)


if __name__ == '__main__':
    i = getRawImageByURL('https://www.javbus.com/imgs/cover/1hk2_b.jpg')
    j = autoCropImage(bytesToImage(i), face_detection=True, scale=0.66, default_to_top=False, default_to_right=False)
    Image.fromarray(j).show()
    # print(getRawImageFormat(i))
