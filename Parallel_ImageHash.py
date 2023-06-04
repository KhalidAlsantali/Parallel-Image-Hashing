import json
import time
from PIL import Image
import imagehash
from multiprocessing import Pool
from multiprocessing import cpu_count
from imutils import paths
import numpy as np
import os, shutil
import threading


def chunk(l, n):
    for i in range(0, len(l), n):
        yield l[i: i + n]


def convert_hash(h):
    return str(np.array(h))


def process_images_threads(payload):
    print("starting thread {}".format(payload["id"]))

    # CHANGE NUMBER OF THREADS PER PROCESS HERE
    num_threads_per_proc = 4

    num_images = len(payload["input_paths"]) / num_threads_per_proc
    num_images = int(np.ceil(num_images))
    chunked_paths = list(chunk(payload["input_paths"], num_images))

    thread_payloads = []

    for (i, image_paths) in enumerate(chunked_paths):
        output_path = os.path.sep.join(["output", "proc_{}_thread_{}.json".format(i, threading.current_thread().ident)])
        data_t = {
            "id": i,
            "input_paths": image_paths,
            "output_path": output_path
        }
        thread_payloads.append(data_t)

    threads = []
    for payload in thread_payloads:
        thread = threading.Thread(target=process_images_2, args=(payload,))
        threads.append(thread)

    print(threads)
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


def process_images_2(payload):
    print("starting process {}".format(payload["id"]))
    hashes = {}

    payload["output_path"] = os.path.sep.join(["output", "proc_{}_thread_{}.json".format(payload["id"], threading.current_thread().ident)])

    for imagePath in payload["input_paths"]:
        image = Image.open(imagePath)
        h = imagehash.average_hash(image)
        h = convert_hash(h)

        l = hashes.get(h, [])
        l.append(imagePath)
        hashes[h] = l

    print("Process {} Serializing".format(payload["id"]))
    f = open(payload["output_path"], "w")
    f.write(json.dumps(hashes))
    f.close()


def process_images(payload):
    print("Starting Process {}".format(payload["id"]))
    hashes = {}

    for imagePath in payload["input_paths"]:
        image = Image.open(imagePath)
        h = imagehash.average_hash(image)
        h = convert_hash(h)

        l = hashes.get(h, [])
        l.append(imagePath)
        hashes[h] = l

    print("Process {} Serializing".format(payload["id"]))
    f = open(payload["output_path"], "w")
    f.write(json.dumps(hashes))
    f.close()


def technique2(payloads):
    # ================================================
    # MULTIPROCESSING USING DIFFERENT PROCESSES
    print("Launching Pool using {} Processors".format(procs))
    pool = Pool(processes=procs)
    pool.map(process_images, payloads)
    print("Waiting for processes to finish...")
    pool.close()
    pool.join()


def technique3(payloads):
    # ================================================
    # THREADING TECHNIQUE USING THREADS
    print("Launching {} Threads".format(procs))
    threads = []

    for payload in payloads:
        thread = threading.Thread(target=process_images, args=(payload,))
        threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        print("Starting Thread {}".format(thread.getName()))
        thread.join()


def technique4(payloads):
    # ================================================
    # BOTH THREADING AND MULTIPROCESSING
    print("Launching Pool using {} Processors".format(procs))
    pool = Pool(processes=procs)
    pool.map(process_images_threads, payloads)
    print("Waiting for processes to finish...")
    pool.close()
    pool.join()


def deletefiles():
    for file in os.listdir("output"):
        file_path = os.path.join("output", file)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


if __name__ == "__main__":

    deletefiles()

    # CHANGE NUMBER OF CPUS/THREADS FOR TECHNIQUE 2 and 3 HERE
    procs = cpu_count()

    print("Collecting Image Paths...")
    allImagePaths = sorted(list(paths.list_images('101_ObjectCategories')))
    numImagesPerProc = len(allImagePaths) / float(procs)
    numImagesPerProc = int(np.ceil(numImagesPerProc))

    chunkedPaths = list(chunk(allImagePaths, numImagesPerProc))

    payloads = []

    for (i, imagepPaths) in enumerate(chunkedPaths):
        outputPath = os.path.sep.join(["output", "proc_{}.json".format(i)])
        data = {
            "id": i,
            "input_paths": imagepPaths,
            "output_path": outputPath
        }
        payloads.append(data)

    start_time = time.time()

    # COMMENT OUT THE UNUSED TECHNIQUES

    # technique2(payloads)

    technique3(payloads)

    # technique4(payloads)

    print("Multiprocessing Complete")
    print("Time Taken:")
    print(time.time() - start_time)

