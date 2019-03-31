import threading
	
def synchronized(func):
	
    func.__lock__ = threading.Lock()
		
    def synced_func(*args, **kws):
        with func.__lock__:
            return func(*args, **kws)

    return synced_func

import time
	
total = 0
		
@synchronized
def count():
    global total
    curr = total + 1
    # time.sleep(3)
    total = curr
		
def counter():
    for i in range(0,10): count()
		
thread1 = threading.Thread(target = counter)
thread2 = threading.Thread(target = counter)

thread1.start()
thread2.start()
    
thread1.join()
thread2.join()

print(total)