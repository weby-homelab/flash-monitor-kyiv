import threading
import time
from light_service import monitor_loop, schedule_loop, alerts_loop, load_state

if __name__ == "__main__":
    print("Starting Flash Monitor Background Services...")
    load_state()
    
    # Start Monitor (timeout detection)
    t1 = threading.Thread(target=monitor_loop)
    t1.daemon = True
    t1.start()

    # Start Alerts (air raid)
    t2 = threading.Thread(target=alerts_loop)
    t2.daemon = True
    t2.start()
    
    # Start Scheduler (periodic reports)
    # We don't use daemon here to keep the main process alive
    print("Scheduler loop starting in main thread...")
    schedule_loop()
