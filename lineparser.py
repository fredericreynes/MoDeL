from pyparsing import *

# Exclude newlines from default whitespace,
# since we deal with them manually
ParserElement.setDefaultWhitespaceChars(" \t")

comment = Suppress('#' + restOfLine)
EOL = LineEnd().suppress()
SOL = LineStart().leaveWhitespace()
continuation = (Literal('_').leaveWhitespace() + EOL).suppress()
blankline = SOL + LineEnd()

code = OneOrMore(White(" \t") | Word(printables)).setParseAction(lambda toks: ''.join(toks))
physical_line = (code + EOL).setParseAction(lambda toks: toks[0].rstrip())
logical_line = (OneOrMore(code + continuation) + physical_line).setParseAction(lambda toks: ''.join([x.lstrip() for x in toks]))
line = physical_line | logical_line | EOL

program = OneOrMore(line) + StringEnd()

program.ignore(blankline).ignore(comment)

test = r"""# this is a comment
  # comment with leading whitespace
line 1
line 2

line 3 # has a comment
line 4 \# does not have a comment
line 5 _
  continues over three _
  physical lines

line 6 _

  continues over two physical lines, with a blank in between

line 7 doesn't continue __
line _8 in_cludes escapes (and also a bug).
    line 9 also has a comment # which gets rid of this backslash _
and lastly line 10.
"""

test_logical = r"""line 5 _
  continues over three _
  physical lines"""


for l in logical_line.parseString(test_logical):
    print l
