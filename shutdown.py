import os

if os.path.exists('_compiler_in'):
    with open('_compiler_in\shutdown.txt', 'w') as f:
        f.write('shutdown')
