import re, sys

filename = sys.argv[1]

re_iterator = re.compile('in (([a-zA-Z0-9]+ ?)+)')
re_set_definition = re.compile(':= (([a-zA-Z0-9]+ ?)+)')


with open(filename, "r") as f:
    lines = f.readlines()

    #lines = ['@pv |V||O| = sum(|V||O|[c] if |V||O|[c] <> 0 on c) where V in Q CH G I X DS CI MT MC']

def convert_iterator(mo):
    return 'in {' + ', '.join(s for s in mo.group(1).split(' ') if len(s) > 0) + '}'

def convert_set_definition(mo):
    return ':= {' + ', '.join(s for s in mo.group(1).split(' ') if len(s) > 0) + '}'

def convert(l):
    # Don't touch comments!
    if l[0] == '#':
        return l
    else:
        # Options
        l = l.replace('@over', '!over').replace('@pv', '!pv')

        # Iterators
        l = re.sub(re_iterator, convert_iterator, l)

        # Set definitions
        l = re.sub(re_set_definition, convert_set_definition, l)

        return l

with open("test.mdl", 'w') as f:
    f.write(''.join(convert(l) for l in lines))
