from google.cloud import vision


class FaceAPIError(Exception):
    pass


def detect_faces(content: bytes):
    """Detects faces in an image."""
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=content)

    response = client.face_detection(image=image)
    if response.error.message:
        raise FaceAPIError(response.error.message)

    return [tuple((vertex.x, vertex.y)
                  for vertex in face.bounding_poly.vertices)
            for face in response.face_annotations]


if __name__ == '__main__':
    from avdc.utility.image import getRawImageByURL

    print(detect_faces(getRawImageByURL('https://www.javbus.com/imgs/cover/1hk2_b.jpg')))
