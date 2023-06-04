import json
import os
import shutil
import threading
import time
from multiprocessing import Pool
from multiprocessing import cpu_count
import imagehash
import numpy as np
from PIL import Image
from imutils import paths


#   This function takes a list of yields subsets of that chunks according to input length.
def chunk(input_list, length_of_chunk):
    for iterator in range(0, len(input_list), length_of_chunk):
        yield input_list[iterator: iterator + length_of_chunk]


#   Return hash as string
def convert_hash(h):
    return str(np.array(h))


#   This function is called once per process/thread in techniques 1 and 2 and hashes the images its given and returns a list of the hashes.
def process_images(payload):
    print("Starting Process {}".format(payload["id"]))
    hashes = {}

    for imagePath in payload["input_paths"]:
        image = Image.open(imagePath)
        image_hash = imagehash.average_hash(image)
        image_hash = convert_hash(image_hash)

        hash_list = hashes.get(image_hash, [])
        hash_list.append(imagePath)
        hashes[image_hash] = hash_list

    print("Process {} Serializing".format(payload["id"]))
    f = open(payload["output_path"], "w")
    f.write(json.dumps(hashes))
    f.close()


#   This function is used for technique 3 using both threads and processes.
#   Each process calls the process_images_per_thread with the number of threads per process which in turn splits and hashes the images accordingly.
def process_images_processes_threads(payload):
    print("starting thread {}".format(payload["id"]))

    # CHANGE NUMBER OF THREADS PER PROCESS HERE
    num_threads_per_proc = 4

    num_images = len(payload["input_paths"]) / num_threads_per_proc
    num_images = int(np.ceil(num_images))
    chunked_paths = list(chunk(payload["input_paths"], num_images))

    thread_payloads = []

    for (iterator, image_paths) in enumerate(chunked_paths):
        output_path = os.path.sep.join(["output", "proc_{}_thread_{}.json".format(iterator, threading.current_thread().ident)])
        data_t = {
            "id": iterator,
            "input_paths": image_paths,
            "output_path": output_path
        }
        thread_payloads.append(data_t)

    threads = []
    for payload in thread_payloads:
        thread = threading.Thread(target=process_images_per_thread, args=(payload,))
        threads.append(thread)

    print(threads)
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


#   This function process images and is called once for every thread in every process for technique 3.
def process_images_per_thread(payload):
    print("starting process {}".format(payload["id"]))
    hashes = {}

    payload["output_path"] = os.path.sep.join(["output", "proc_{}_thread_{}.json".format(payload["id"], threading.current_thread().ident)])

    for imagePath in payload["input_paths"]:
        image = Image.open(imagePath)
        image_hash = imagehash.average_hash(image)
        image_hash = convert_hash(image_hash)

        hash_list = hashes.get(image_hash, [])
        hash_list.append(imagePath)
        hashes[image_hash] = hash_list

    print("Process {} Serializing".format(payload["id"]))
    f = open(payload["output_path"], "w")
    f.write(json.dumps(hashes))
    f.close()


def processes_technique(images):
    # ================================================
    # MULTIPROCESSING USING DIFFERENT PROCESSES
    print("Launching Pool using {} Processors".format(procs))
    pool = Pool(processes=procs)
    pool.map(process_images, images)
    print("Waiting for processes to finish...")
    pool.close()
    pool.join()


def threads_technique(images):
    # ================================================
    # THREADING TECHNIQUE USING THREADS
    print("Launching {} Threads".format(procs))
    threads = []

    for payload in images:
        thread = threading.Thread(target=process_images, args=(payload,))
        threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        print("Starting Thread {}".format(thread.getName()))
        thread.join()


def threads_and_processes_technique(images):
    # ================================================
    # BOTH THREADING AND MULTIPROCESSING
    print("Launching Pool using {} Processors".format(procs))
    pool = Pool(processes=procs)
    pool.map(process_images_processes_threads, images)
    print("Waiting for processes to finish...")
    pool.close()
    pool.join()


#   Resests output folder to avoid mixing inputs between techniques.
def deletefiles():
    for file in os.listdir("output"):
        file_path = os.path.join("output", file)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as error:
            print('Failed to delete %s. Reason: %s' % (file_path, error))


if __name__ == "__main__":

    deletefiles()

    # CHANGE NUMBER OF CPUS/THREADS FOR TECHNIQUES 1 and 2 HERE
    procs = cpu_count()

    print("Collecting Image Paths...")
    allImagePaths = sorted(list(paths.list_images('Input_Images')))
    numImagesPerProc = len(allImagePaths) / float(procs)
    numImagesPerProc = int(np.ceil(numImagesPerProc))

    chunkedPaths = list(chunk(allImagePaths, numImagesPerProc))

    payloads = []

    #   Build payloads by having a list of objects which each contain an id, an output path, and a list of input paths for the images.
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

    processes_technique(payloads)

    # threads_technique(payloads)

    # threads_and_processes_technique(payloads)

    print("Multiprocessing Complete")
    print("Time Taken:")
    print(time.time() - start_time)
