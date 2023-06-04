# Parallel-Image-Hashing

Small project about different methods to use parallel processing to hash images.

[Parallel Image Hash](Parallel_ImageHash.py) uses three different techniques to achieve a speedup on image hashing. 

# Technique 1: Processes
Every processor on the CPU (or any number below that, as can be changed in code) takes an equal number of images and hashes them. The second fastest technique.

# Technique 2: Threads
One processor uses multiple threads as set in code and each thread hashes an equal number of images. This is a concurrency technique and the speedup is achieved by essentially removing CPU downtime. The slowest technique.

# Technique 3: Both threads and processes
This technique combines both techniques such that each processor has a minimum downtime and can work 100% of the runtime of the program. Slightly faster than technique 1.

# Sequential technique
[Sequential Image Hash](Sequential_ImageHash.py) is just as it sounds. One processor using one threads sequentially moving through each image and hashing it.
