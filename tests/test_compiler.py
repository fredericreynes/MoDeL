from .. import parser
import csv

class TestCompiler(object):
    @classmethod
    def setup_class(cls):
        with open('../tmp_all_vars.csv', 'rb') as csvfile:
            rows = list(csv.reader(csvfile))
            cls.heap = dict(zip(rows[0],
                                [float(e) if e != 'NA' else
                                 None for e in rows[2]]))

    def test_parses_VariableName_with_alphas(self):
        res = parser.variableName.parseString("testVariable")[0]
        assert isinstance(res, parser.VariableName)
        assert res.value == "testVariable"

    def test_parses_VariableName_with_alphanums_and_underscores(self):
        res = parser.variableName.parseString("_test9_Variable")[0]
        assert isinstance(res, parser.VariableName)
        assert res.value == "_test9_Variable"

    def test_parses_Placeholder(self):
        res = parser.placeholder.parseString("{X}")[0]
        assert isinstance(res, parser.Placeholder)
        assert res.value == parser.VariableName("X")

    def test_compiles_Placeholder(self):
        res = parser.placeholder.parseString("{V}")[0]
        assert res.compile({parser.VariableName('V'): 'X'}) == 'X'

    def test_parses_Identifier(self):
        res = parser.identifier.parseString("test{X}_energy{O}")[0]
        assert isinstance(res, parser.Identifier)
        assert len(res.value) == 4
        assert isinstance(res.value[0], parser.VariableName) and isinstance(res.value[2], parser.VariableName)
        assert isinstance(res.value[1], parser.Placeholder) and isinstance(res.value[3], parser.Placeholder)
        assert res.value[0].value == "test" and res.value[2].value == "_energy"
        assert res.value[1].value == parser.VariableName("X") and res.value[3].value == parser.VariableName("O")

    def test_compiles_Identifier(self):
        res = parser.identifier.parseString("test{V}_energy{O}")[0]
        assert res.compile({parser.VariableName('V'): 'Q', parser.VariableName('O'): 'M'}) == "testQ_energyM"

    def test_parses_simple_variable_name_as_identifier(self):
        res = parser.identifier.parseString("testVar")[0]
        assert isinstance(res, parser.Identifier)
        assert len(res.value) == 1 and isinstance(res.value[0], parser.VariableName)

    def test_parses_Index(self):
        res = parser.index.parseString("[com, sec]")[0]
        assert isinstance(res, parser.Index)
        assert len(res.value) == 2
        assert res.value[0] == parser.VariableName("com") and res.value[1] == parser.VariableName("sec")

    def test_parses_Integer(self):
        res = parser.integer.parseString("42")[0]
        assert isinstance(res, parser.Integer)
        assert res.value == 42
        res = parser.integer.parseString("-42")[0]
        assert isinstance(res, parser.Integer)
        assert res.value == -42

    def test_parses_Real(self):
        res = parser.real.parseString("3.14159")[0]
        assert isinstance(res, parser.Real)
        assert res.value == 3.14159
        res = parser.real.parseString("-3.14159")[0]
        assert isinstance(res, parser.Real)
        assert res.value == -3.14159

    def test_parses_Array(self):
        res = parser.array.parseString("{X}tes{M}_arrayName8[com, 5, sec]")[0]
        assert isinstance(res, parser.Array)
        assert isinstance(res.identifier, parser.Identifier)
        assert isinstance(res.index, parser.Index)
        assert len(res.identifier.value) == 4
        assert len(res.index.value) == 3
        assert res.index.value[1].value == 5

    def test_compiles_Array(self):
        res = parser.array.parseString("arrayName8[com, 5, sec]")[0]
        assert res.compile({parser.VariableName('com'): '24', parser.VariableName('sec'): '2403'}) == "arrayName8_24_5_2403"

    def test_parses_Func(self):
        res = parser.func.parseString("d(log(test))")[0]
        assert isinstance(res, parser.Func)
        assert res.name == 'd' and isinstance(res.expression, parser.Expression)
        assert isinstance(res.expression.value[0], parser.Func)

    def test_compiles_Func(self):
        res = parser.func.parseString("d(log(test[j]))")[0]
        assert res.compile({parser.VariableName('j'): '24'}) == "d(log(test_24))"

    def test_parses_Expression(self):
        res = parser.expression.parseString("D{O}[com, sec] + d(log(Q[com, sec])) - A / B")[0]
        assert isinstance(res, parser.Expression)
        assert len(res.value) == 7
        assert isinstance(res.value[0], parser.Array)
        assert isinstance(res.value[1], parser.Operator)
        assert isinstance(res.value[2], parser.Func)
        assert isinstance(res.value[3], parser.Operator)
        assert isinstance(res.value[4], parser.Identifier)
        assert isinstance(res.value[5], parser.Operator)
        assert isinstance(res.value[6], parser.Identifier)

    def test_compiles_Expression(self):
        res = parser.expression.parseString("D[com, sec] + d(log(Q[com, sec])) - A / B")[0]
        assert res.compile({parser.VariableName('com'): '24', parser.VariableName('sec'): '2403'}) == "D_24_2403 + d(log(Q_24_2403)) - A / B"

    def test_evaluates_Expression(self):
        res = parser.expression.parseString("2 * Q[com, sec] + 4 * X[com, sec]")[0]
        assert res.evaluate({parser.VariableName('com'): '24', parser.VariableName('sec'): '2403'},
                            {'Q_24_2403': 1, 'X_24_2403': 10}) == 42
        res = parser.expression.parseString("2 * Q[com, sec] - X[com, sec] ^ 2 < 0")[0]
        assert res.evaluate({parser.VariableName('com'): '24', parser.VariableName('sec'): '2403'},
                            {'Q_24_2403': 1, 'X_24_2403': 10}) == True

    def test_parses_Equation(self):
        res = parser.equation.parseString("energy{O}[com] + _test{X}{M}[sec] = log(B[j])")[0]
        assert isinstance(res, parser.Equation)
        assert isinstance(res.lhs, parser.Expression)
        assert isinstance(res.rhs, parser.Expression)

    def test_compiles_Equation(self):
        res = parser.equation.parseString("energy[com] = log(B[3])")[0]
        assert res.compile({parser.VariableName('com'): '24'}) == "energy_24 = log(B_3)"

    def test_parses_Condition(self):
        res = parser.condition.parseString("if energy[com, sec] > 0")[0]
        assert isinstance(res, parser.Condition)
        assert isinstance(res.expression, parser.Expression)
        assert len(res.expression.value) == 3

    def test_parses_Lst(self):
        res = parser.lst.parseString("01 02 03 04 05 06 07")[0]
        assert isinstance(res, parser.Lst)
        assert len(res.value) == 7
        assert res.value[3] == "04"

    def test_parses_Iter(self):
        res = parser.iter.parseString("com in 01 02 03 04 05 06 07")[0]
        assert isinstance(res, parser.Iter)
        assert isinstance(res.variableName, parser.VariableName)
        assert isinstance(res.lst, parser.Lst)

    def test_parses_Formula(self):
        res = parser.formula.parseString("{V}[com] = {V}D[com] + {V}M[com], V in Q CH G I DS, com in 01 02 03 04 05 06 07 08 09")[0]
        assert isinstance(res, parser.Formula)
        assert isinstance(res.equation, parser.Equation)
        assert len(res.iterators) == 2
        assert reduce(lambda x, y: x and y, [isinstance(e, parser.Iter) for e in res.iterators])
        res = parser.formula.parseString("Q = QD + QM")[0]
        assert isinstance(res, parser.Formula)
        assert len(res.iterators) == 0
        res = parser.formula.parseString("{V}[com] = {V}D[com] + {V}M[com] if {V}[com] > 0, V in Q CH I, com in 01 02 07 08 09")[0]
        assert isinstance(res, parser.Formula)
        assert len(res.conditions) == 1
        assert isinstance(res.conditions[0], parser.Condition)
        assert len(res.iterators) == 2

    def test_compiles_Formula(self):
        expected = ("Q_01 = QD_01 + QM_01\n"
                    "Q_02 = QD_02 + QM_02\n"
                    "CH_01 = CHD_01 + CHM_01\n"
                    "CH_02 = CHD_02 + CHM_02")
        res = parser.formula.parseString("{V}[com] = {V}D[com] + {V}M[com], V in Q CH, com in 01 02")[0]
        assert res.compile({}) == expected
        expected = ("Q_02 = QD_02 + QM_02\n"
                    "CH_02 = CHD_02 + CHM_02")
        res = parser.formula.parseString("{V}[com] = {V}D[com] + {V}M[com] if CHD[com] > 0, V in Q CH, com in 01 02")[0]
        assert res.compile({"CHD_01": 0, "CHD_02": 15}) == expected
