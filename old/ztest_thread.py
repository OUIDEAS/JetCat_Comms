import multiprocessing
import threading
import random
import time
from functools import reduce


def func(number):
    random_list = random.sample(range(1000000), number)
    time.sleep(2)
    return reduce(lambda x, y: x*y, random_list)

    
number = 50000

multiprocessing_start_timer = time.time()
process1 = multiprocessing.Process(target=func, args=(number,))
process2 = multiprocessing.Process(target=func, args=(number,))
process3 = multiprocessing.Process(target=func, args=(number,))
process1.start()
process2.start()
process3.start()
process1.join()
process2.join()
process3.join()

print("Time1: ", time.time()-multiprocessing_start_timer)


threading_start_time = time.time()
thread1 = threading.Thread(target=func, args=(number,))
thread2 = threading.Thread(target=func, args=(number,))
thread1.start()
thread2.start()
thread1.join()
thread2.join()

print("Time2: ", time.time()-threading_start_time)


start_time = time.time()
f1 = func(number)
f2 = func(number)
f3 = func(number)

print("Time3:", time.time()-start_time)