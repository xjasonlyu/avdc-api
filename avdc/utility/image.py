import imghdr
from io import BytesIO
from typing import Optional

import numpy as np
from PIL import Image
from face_recognition import face_locations

from avdc.utility.httpclient import get_blob


def getRawImageByURL(url: str) -> bytes:
    return get_blob(url, raise_for_status=True)


def getRawImageFormat(data: bytes) -> Optional[str]:
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


def imageToBytes(img: np.ndarray, fmt: str = 'JPEG', quality: int = 95, subsampling: int = 0) -> bytes:
    im: Image.Image = Image.fromarray(img)
    buffer = BytesIO()
    im.save(buffer,
            format=fmt,
            quality=quality,
            subsampling=subsampling)
    return buffer.getvalue()


def getFaceCenter(loc: tuple[int, int, int, int]) -> tuple[int, int]:
    return (loc[1] + loc[3]) // 2, (loc[0] + loc[2]) // 2


def findFaces(img: np.ndarray) -> list[tuple[int, int, int, int]]:
    return face_locations(img, number_of_times_to_upsample=1)


def sortFaces(faces: list[tuple[int, int, int, int]], reverse: bool = True):
    faces.sort(key=lambda x: abs(x[0] - x[2]) * abs(x[1] - x[3]),
               reverse=reverse)


def cropImage(img: np.ndarray,
              center: int = -1,
              scale: float = 2 / 3,
              tolerance: float = 0.01,
              default_to_right: bool = True) -> np.ndarray:
    height, width = getImageSize(img)
    # expected width
    _width = int(height * scale)

    if _width >= width:
        if abs(width / height - scale) <= tolerance:
            # no need to crop
            return img

        height = int(width / scale)
        # just fit to top
        return img[:min(height, height), :]

    # default to right side
    if center < 0 or (center > width // 2 and default_to_right):
        left, right = width - _width, width
        return img[:, left:right]

    x = center - (_width // 2)
    left = x if x > 0 else 0
    right = min(left + _width, width)
    return img[:, left:right]


def autoCropImage(img: np.ndarray, face_detection: bool = True, **options) -> np.ndarray:
    if not face_detection:
        return cropImage(img, **options)

    # find and sort faces
    faces = findFaces(img)
    sortFaces(faces)

    return cropImage(img=img,
                     center=-1 if not faces  # no faces detected
                     else getFaceCenter(faces[0])[0],  # x
                     **options)


if __name__ == '__main__':
    i = getRawImageByURL('https://imgix.pedestrian.tv/content/uploads/2021/01/14/'
                         'Ted-Mosby.jpg?ar=16%3A9&auto=format&crop=focal&fit=crop&q=65&w=1200')
    j = autoCropImage(bytesToImage(i), default_to_right=False)
    Image.fromarray(j).show()
    # print(getRawImageFormat(i))
