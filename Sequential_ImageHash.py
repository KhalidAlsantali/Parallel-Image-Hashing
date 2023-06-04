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
        image_hash = imagehash.average_hash(image)
        image_hash = convert_hash(image_hash)

        hash_list = hashes.get(image_hash, [])
        hash_list.append(imagePath)
        hashes[image_hash] = hash_list

    print("process {} serializing".format("seq"))
    f = open("output\\process_seq.json", "w")
    f.write(json.dumps(hashes))
    f.close()


if __name__ == "__main__":
    start_time = time.time()
    print("grabbing image paths")
    allImagePaths = sorted(list(paths.list_images('Input_Images')))
    print("waiting for procs to finish...")
    process_images(allImagePaths)
    print("time taken")
    print(time.time() - start_time)
