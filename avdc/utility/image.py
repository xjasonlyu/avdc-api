import imghdr
from io import BytesIO
from typing import Optional

import numpy as np
from PIL import Image
from face_recognition import face_locations

from avdc.utility.httpclient import get_blob


def getImageByURL(url: str) -> bytes:
    return get_blob(url)


def getImageFormat(data: bytes) -> Optional[str]:
    # try:
    #     im: Image.Image = Image.open(BytesIO(data))
    # except UnidentifiedImageError:
    #     return
    # else:
    #     return im.format
    return imghdr.what(BytesIO(data))


def getImageSize(img: np.ndarray) -> tuple[int, int]:
    s = img.shape
    return s[0], s[1]  # height, width


def bytesToImage(data: bytes, mode: str = 'RGB') -> np.ndarray:
    im: Image.Image = Image.open(BytesIO(data))
    if mode:
        im = im.convert(mode)
    return np.array(im)


def imageToBytes(img: np.ndarray, fmt: str = 'JPEG') -> bytes:
    im = Image.fromarray(img)
    buffer = BytesIO()
    im.save(buffer, format=fmt)
    return buffer.getvalue()


def getFaceCenter(loc: tuple[int, int, int, int]) -> tuple[int, int]:
    return (loc[1] + loc[3]) // 2, (loc[0] + loc[2]) // 2


def findFaces(img: np.ndarray) -> list[tuple[int, int, int, int]]:
    return face_locations(img, number_of_times_to_upsample=1)


def sortFaces(faces: list[tuple[int, int, int, int]], reverse: bool = True):
    faces.sort(key=lambda x: abs(x[0] - x[2]) * abs(x[1] - x[3]),
               reverse=reverse)


def cropImage(img: np.ndarray, x: int = -1, scale: float = 0.67) -> np.ndarray:
    _height, _width = getImageSize(img)
    width = int(_height * scale)

    if width >= _width:  # no need to crop
        return img

    if x < 0 or x > _width // 2:  # default to right side
        return img[:_height, _width - width:_width]

    _x = x - (width // 2)
    left = _x if _x > 0 else 0
    right = min(left + width, _width)
    return img[:_height, left:right]


def autoCropImage(img: np.ndarray, face_detection: bool = True, **kwargs) -> np.ndarray:
    if not face_detection:
        return cropImage(img, **kwargs)

    # find all faces
    faces = findFaces(img)
    sortFaces(faces)  # sort

    if not faces:  # no faces detected
        return cropImage(img, **kwargs)

    x, _ = getFaceCenter(faces[0])
    return cropImage(img, x=x, **kwargs)


if __name__ == '__main__':
    i = getImageByURL('https://image.mgstage.com/images/shirouto/siro/4386/pb_e_siro-4386.jpg')
    # j = autoCropImage(bytesToImage(i))
    # Image.fromarray(j).show()
    print(getImageFormat(i))
