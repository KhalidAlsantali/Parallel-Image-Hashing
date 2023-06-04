import json
from PIL import Image
import imagehash
import time
from imutils import paths
import numpy as np


def convert_hash(h):
    return str(np.array(h))


def process_images(payload):
    print("starting process")
    hashes = {}

    for imagePath in payload:
        image = Image.open(imagePath)
        h = imagehash.average_hash(image)
        h = convert_hash(h)

        l = hashes.get(h, [])
        l.append(imagePath)
        hashes[h] = l

    print("process {} serializing".format("seq"))
    f = open("output\\process_seq.json", "w")
    f.write(json.dumps(hashes))
    f.close()


if __name__ == "__main__":
    start_time = time.time()
    print("grabbing image paths")
    allImagePaths = sorted(list(paths.list_images('101_ObjectCategories')))
    print("waiting for procs to finish...")
    process_images(allImagePaths)
    print("time taken")
    print(time.time() - start_time)