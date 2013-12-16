import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

import ntpath
import parser
import csv

with open('tmp_all_vars.csv', 'rb') as csvfile:
    rows = list(csv.reader(csvfile))
    heap = dict(zip(rows[0],
                    [float(e) if e != 'NA' else
                     None for e in rows[2]]))


class CompilerHandler(FileSystemEventHandler):
    def __init__(self, observer):
        super(CompilerHandler, self).__init__()
        self.observer = observer

    def on_modified(self, event):
        filename = ntpath.basename(event.src_path)

        if filename == "shutdown.txt":
            print "Shutting down"
            self.observer.stop()

        else:
            print filename

observer = Observer()
observer.schedule(CompilerHandler(observer), path = '.')
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()
