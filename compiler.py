import os, sys, shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

import pyparsing
import grammar
import ntpath
import csv
import os

with open('tmp_all_vars.csv', 'rb') as csvfile:
    rows = list(csv.reader(csvfile))
    heap = dict(zip(rows[0],
                    [float(e) if e != 'NA' else
                     None for e in rows[2]]))

compiler_in = "_compiler_in"
compiler_out = "_compiler_out"

def ensure_directory(_path):
     if not os.path.exists(_path):
        os.makedirs(_path)

ensure_directory(compiler_in)
ensure_directory(compiler_out)

class CompilerHandler(FileSystemEventHandler):
    def on_modified(self, event):
        filename = ntpath.basename(event.src_path)

        if filename == "shutdown.txt":
            print "Shutting down"
            shutil.rmtree(compiler_in)
            shutil.rmtree(compiler_out)
            os._exit(1)

        else:
            print "Compiling " + filename
            try:
                code = open(event.src_path, 'r').readline().strip()
                compiled = grammar.formula.parseString(code)[0].compile(heap)
                print "Compilation successful"
                print compiled
                with open(compiler_out + "\\" + filename, 'w') as f:
                    f.write(compiled)

            except pyparsing.ParseException as e:
                print str(e)
            except:
                print str(sys.exc_info()[0])
            print

observer = Observer()
observer.schedule(CompilerHandler(), path = compiler_in)
observer.start()

print "Ready to compile\n"

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()
