import os, sys, shutil
import atexit
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

import pyparsing
import grammar
import ntpath
import csv
import os

if len(sys.argv) > 1:
    os.chdir(sys.argv[1])

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

def safe_delete(_path):
    if os.path.exists(_path):
        shutil.rmtree(_path)

ensure_directory(compiler_in)
ensure_directory(compiler_out)

def shutdown():
    print ("Shutting down")
    safe_delete(compiler_in)
    safe_delete(compiler_out)

atexit.register(shutdown)

class CompilerHandler(FileSystemEventHandler):
    def on_modified(self, event):
        filename = ntpath.basename(event.src_path)

        if filename == "shutdown.txt":
            shutdown()
            os._exit(0)

        else:
            print ("Compiling " + filename)
            try:
                code = open(event.src_path, 'r').readline().strip()
                if code[0] == '"':
                    code = code[1:-1]
                compiled = grammar.formula.parseString(code)[0].compile(heap)
                print ("Compilation successful")
                print (compiled)
                with open(compiler_out + "\\" + filename, 'w') as f:
                    f.write(compiled)

            except pyparsing.ParseException as e:
                print (str(e))
            except:
                print (str(sys.exc_info()[0]))
                print

observer = Observer()
observer.schedule(CompilerHandler(), path = compiler_in)
observer.start()

print ("Ready to compile\n")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()
