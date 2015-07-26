import re, sys

filename = sys.argv[1]

re_iterator = re.compile('in (([a-zA-Z]+ ?)+)')


with open(filename, "r") as f:
    lines = f.readlines()

    #lines = ['@pv |V||O| = sum(|V||O|[c] if |V||O|[c] <> 0 on c) where V in Q CH G I X DS CI MT MC']

def convert_iterator(mo):
    return 'in {' + ', '.join(mo.group(1).split(' ')) + '}'

def convert(l):
    # Don't touch comments!
    if '#' in l:
        return l
    else:
        # Options
        l = l.replace('@over', '!over').replace('@pv', '!pv')

        # Iterators
        return re.sub(re_iterator, convert_iterator, l)

with open("test.mdl", 'w') as f:
    f.write(''.join(convert(l) for l in lines))
