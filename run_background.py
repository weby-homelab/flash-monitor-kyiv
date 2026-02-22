import threading
import time
from light_service import monitor_loop, schedule_loop, load_state

if __name__ == "__main__":
    print("Starting Flash Monitor Background Services...")
    load_state()
    
    # Start Monitor (timeout detection)
    t1 = threading.Thread(target=monitor_loop)
    t1.daemon = True
    t1.start()
    
    # Start Scheduler (periodic reports)
    # We don't use daemon here to keep the main process alive
    schedule_loop()
