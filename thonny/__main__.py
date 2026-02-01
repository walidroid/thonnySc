from thonny import report_time
from thonny.main import run

report_time("Before launch")
import threading
import logging
logging.warning("APP STARTED | Main thread = %s", threading.current_thread().name)
run()
