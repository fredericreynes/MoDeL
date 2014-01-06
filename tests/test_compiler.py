from .. import grammar
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
        res = grammar.variableName.parseString("testVariable")[0]
        assert isinstance(res, grammar.VariableName)
        assert res.value == "testVariable"

    def test_parses_VariableName_with_alphanums_and_underscores(self):
        res = grammar.variableName.parseString("_test9_Variable")[0]
        assert isinstance(res, grammar.VariableName)
        assert res.value == "_test9_Variable"

    def test_parses_Placeholder(self):
        res = grammar.placeholder.parseString("{X}")[0]
        assert isinstance(res, grammar.Placeholder)
        assert res.value == grammar.VariableName("X")

    def test_compiles_Placeholder(self):
        res = grammar.placeholder.parseString("{V}")[0]
        assert res.compile({grammar.VariableName('V'): 'X'}, '') == 'X'

    def test_parses_Identifier(self):
        res = grammar.identifier.parseString("test{X}_energy{O}")[0]
        assert isinstance(res, grammar.Identifier)
        assert len(res.value) == 4
        assert isinstance(res.value[0], grammar.VariableName) and isinstance(res.value[2], grammar.VariableName)
        assert isinstance(res.value[1], grammar.Placeholder) and isinstance(res.value[3], grammar.Placeholder)
        assert res.value[0].value == "test" and res.value[2].value == "_energy"
        assert res.value[1].value == grammar.VariableName("X") and res.value[3].value == grammar.VariableName("O")

    def test_compiles_Identifier(self):
        res = grammar.identifier.parseString("test{V}_energy{O}")[0]
        assert res.compile({grammar.VariableName('V'): 'Q', grammar.VariableName('O'): 'M'}, '') == "testQ_energyM"

    def test_parses_simple_variable_name_as_identifier(self):
        res = grammar.identifier.parseString("testVar")[0]
        assert isinstance(res, grammar.Identifier)
        assert len(res.value) == 1 and isinstance(res.value[0], grammar.VariableName)

    def test_parses_Index(self):
        res = grammar.index.parseString("[com, sec]")[0]
        assert isinstance(res, grammar.Index)
        assert len(res.value) == 2
        assert res.value[0] == grammar.VariableName("com") and res.value[1] == grammar.VariableName("sec")

    def test_parses_Integer(self):
        res = grammar.integer.parseString("42")[0]
        assert isinstance(res, grammar.Integer)
        assert res.value == 42
        res = grammar.integer.parseString("-42")[0]
        assert isinstance(res, grammar.Integer)
        assert res.value == -42

    def test_parses_Real(self):
        res = grammar.real.parseString("3.14159")[0]
        assert isinstance(res, grammar.Real)
        assert res.value == 3.14159
        res = grammar.real.parseString("-3.14159")[0]
        assert isinstance(res, grammar.Real)
        assert res.value == -3.14159

    def test_parses_Array(self):
        res = grammar.array.parseString("{X}tes{M}_arrayName8[com, 5, sec]")[0]
        assert isinstance(res, grammar.Array)
        assert isinstance(res.identifier, grammar.Identifier)
        assert isinstance(res.index, grammar.Index)
        assert len(res.identifier.value) == 4
        assert len(res.index.value) == 3
        assert res.index.value[1].value == 5

    def test_compiles_Array(self):
        res = grammar.array.parseString("arrayName8[com, 5, sec]")[0]
        assert res.compile({grammar.VariableName('com'): '24', grammar.VariableName('sec'): '2403'}, '') == "arrayName8_24_5_2403"

    def test_parses_Func(self):
        res = grammar.func.parseString("d(log(test))")[0]
        assert isinstance(res, grammar.Func)
        assert res.name == 'd' and isinstance(res.expression, grammar.Expression)
        assert isinstance(res.expression.value[0], grammar.Func)

    def test_compiles_Func(self):
        res = grammar.func.parseString("d(log(test[j]))")[0]
        assert res.compile({grammar.VariableName('j'): '24'}, '') == "d(log(test_24))"

    def test_parses_Expression(self):
        res = grammar.expression.parseString("D{O}[com, sec] + d(log(Q[com, sec])) - A / B")[0]
        assert isinstance(res, grammar.Expression)
        assert len(res.value) == 7
        assert isinstance(res.value[0], grammar.Array)
        assert isinstance(res.value[1], grammar.Operator)
        assert isinstance(res.value[2], grammar.Func)
        assert isinstance(res.value[3], grammar.Operator)
        assert isinstance(res.value[4], grammar.Identifier)
        assert isinstance(res.value[5], grammar.Operator)
        assert isinstance(res.value[6], grammar.Identifier)

    def test_compiles_Expression(self):
        res = grammar.expression.parseString("D[com, sec] + d(log(Q[com, sec])) - A / B")[0]
        assert res.compile({grammar.VariableName('com'): '24', grammar.VariableName('sec'): '2403'}, '') == "D_24_2403 + d(log(Q_24_2403)) - A / B"

    def test_evaluates_Expression(self):
        res = grammar.expression.parseString("2 * Q[com, sec] + 4 * X[com, sec]")[0]
        assert res.evaluate({grammar.VariableName('com'): '24', grammar.VariableName('sec'): '2403'},
                            {'Q_24_2403': 1, 'X_24_2403': 10}) == 42
        res = grammar.expression.parseString("2 * Q[com, sec] - X[com, sec] ^ 2 < 0")[0]
        assert res.evaluate({grammar.VariableName('com'): '24', grammar.VariableName('sec'): '2403'},
                            {'Q_24_2403': 1, 'X_24_2403': 10}) == True

    def test_parses_Equation(self):
        res = grammar.equation.parseString("energy{O}[com] + _test{X}{M}[sec] = log(B[j])")[0]
        assert isinstance(res, grammar.Equation)
        assert isinstance(res.lhs, grammar.Expression)
        assert isinstance(res.rhs, grammar.Expression)

    def test_compiles_Equation(self):
        res = grammar.equation.parseString("energy[com] = log(B[3])")[0]
        assert res.compile({grammar.VariableName('com'): '24'}, '') == "energy_24 = log(B_3)"

    def test_parses_Condition(self):
        res = grammar.condition.parseString("if energy[com, sec] > 0")[0]
        assert isinstance(res, grammar.Condition)
        assert isinstance(res.expression, grammar.Expression)
        assert len(res.expression.value) == 3

    def test_parses_Lst(self):
        res = grammar.lst.parseString("01 02 03 04 05 06 07")[0]
        assert isinstance(res, grammar.Lst)
        assert len(res.value) == 7
        assert res.value[3] == "04"

    def test_parses_Iter(self):
        res = grammar.iter.parseString("com in 01 02 03 04 05 06 07")[0]
        assert isinstance(res, grammar.Iter)
        assert isinstance(res.variableName, grammar.VariableName)
        assert isinstance(res.lst, grammar.Lst)

    def test_parses_Formula(self):
        res = grammar.formula.parseString("{V}[com] = {V}D[com] + {V}M[com], V in Q CH G I DS, com in 01 02 03 04 05 06 07 08 09")[0]
        assert isinstance(res, grammar.Formula)
        assert isinstance(res.equation, grammar.Equation)
        assert len(res.iterators) == 2
        assert reduce(lambda x, y: x and y, [isinstance(e, grammar.Iter) for e in res.iterators])
        res = grammar.formula.parseString("Q = QD + QM")[0]
        assert isinstance(res, grammar.Formula)
        assert len(res.iterators) == 0
        res = grammar.formula.parseString("{V}[com] = {V}D[com] + {V}M[com] if {V}[com] > 0, V in Q CH I, com in 01 02 07 08 09")[0]
        assert isinstance(res, grammar.Formula)
        assert len(res.conditions) == 1
        assert isinstance(res.conditions[0], grammar.Condition)
        assert len(res.iterators) == 2

    def test_compiles_Formula(self):
        expected = ("Q_01 = QD_01 + QM_01\n"
                    "Q_02 = QD_02 + QM_02\n"
                    "CH_01 = CHD_01 + CHM_01\n"
                    "CH_02 = CHD_02 + CHM_02")
        res = grammar.formula.parseString("{V}[com] = {V}D[com] + {V}M[com], V in Q CH, com in 01 02")[0]
        assert res.compile({}) == expected
        expected = ("Q_02 = QD_02 + QM_02\n"
                    "CH_02 = CHD_02 + CHM_02")
        res = grammar.formula.parseString("{V}[com] = {V}D[com] + {V}M[com] if CHD[com] > 0, V in Q CH, com in 01 02")[0]
        assert res.compile({"CHD_01": 0, "CHD_02": 15}) == expected
