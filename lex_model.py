import lexer
import time

def lex_file(filename):
    #print filename
    lex = lexer.Lexer(open(filename, 'rU'))
    tok = lex.read()
    while tok[0] <> None:
        tok = lex.read()


files = ["model\lists.mdl", "model\GHG.mdl", "model\Consumer.mdl", "model\Input_Output.mdl", "model\Producer.mdl", "model\Government.mdl", "model\Price.mdl", "model\Demography.mdl", "model\Adjustments.mdl", "model\Exceptions.mdl", "model\carbon_tax.mdl"]

start = time.time()

for f in files:
    lex_file(f)

print time.time() - start, "seconds"
