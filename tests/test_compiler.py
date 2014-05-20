from .. import parser
from StringIO import StringIO

class TestCompiler:

    def _compile(self, str, heap = None, iterators = None):
        return parser.Compiler(StringIO(str), heap = heap, iterators = iterators)

    def test_compiles_assignments(self):
        res = self._compile("%test := 01 02 03 04")
        assert res.heap == {'%test': (['01', '02', '03', '04'], [1, 2, 3, 4])}
        res = self._compile("%test := 01 02 03 04 \ 01 02")
        assert res.heap == {'%test': (['03', '04'], [3, 4])}
        res = self._compile("%test := %oth_lst", {'%oth_lst': (['01', '02', '03', '04'], [1, 2, 3, 4])})
        assert res.heap['%test'] == (['01', '02', '03', '04'], [1, 2, 3, 4])
        res = self._compile("%test := %oth_lst \ %excl",
                            {'%oth_lst': (['01', '02', '03', '04'], [1, 2, 3, 4]),
                             '%excl': (['01', '02'], [1, 2])})
        assert res.heap['%test'] == (['03', '04'], [3, 4])

    def test_compiles_placeholder(self):
        res = self._compile("test = a + b - c", iterators = {'V': ['X', 'CH', 'I']})
        assert res.equations == ['test = a + b - c']
        res = self._compile("test|V| = |V|", iterators = {'V': ['X', 'CH', 'I']})
        assert set(res.equations) == set(['testX = X', 'testCH = CH', 'testI = I'])
        res = self._compile("test|V||O| = |V||O|", iterators = {'V': ['X', 'CH', 'I'],
                                                                'O': ['D', 'M']})
        assert set(res.equations) == set(['testXD = XD', 'testCHD = CHD', 'testID = ID',
                                 'testXM = XM', 'testCHM = CHM', 'testIM = IM'])

    def test_compiles_expression(self):
        res = self._compile("test = a + b - c")
        assert res.equations == ['test = a + b - c']
        res = self._compile("test[c] = %a + b[c]", {'%a': '2006'},
                            {'c': ['01', '02', '03']})
        assert set(res.equations) == set(['test_01 = 2006 + b_01',
                                          'test_02 = 2006 + b_02',
                                          'test_03 = 2006 + b_03'])
        res = self._compile("test[c, g, j] = %a + b[c, g, j]", {'%a': '2006'},
                            {'c': ['01', '02'], 'g': ['03', '04'],
                             'j': ['05', '06']})
        assert set(res.equations) == set(['test_01_03_05 = 2006 + b_01_03_05',
                                          'test_02_03_05 = 2006 + b_02_03_05',
                                          'test_01_04_05 = 2006 + b_01_04_05',
                                          'test_02_04_05 = 2006 + b_02_04_05',
                                          'test_01_03_06 = 2006 + b_01_03_06',
                                          'test_02_03_06 = 2006 + b_02_03_06',
                                          'test_01_04_06 = 2006 + b_01_04_06',
                                          'test_02_04_06 = 2006 + b_02_04_06'])

    def test_compiles_function(self):
        res = self._compile("test = testfunc(args)")
        assert res.equations == ['test = testfunc(args)']
