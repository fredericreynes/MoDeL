from .. import compiler
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
        res = compiler.variableName.parseString("testVariable")[0]
        assert isinstance(res, compiler.VariableName)
        assert res.value == "testVariable"

    def test_parses_VariableName_with_alphanums_and_underscores(self):
        res = compiler.variableName.parseString("_test9_Variable")[0]
        assert isinstance(res, compiler.VariableName)
        assert res.value == "_test9_Variable"

    def test_parses_Placeholder(self):
        res = compiler.placeholder.parseString("{X}")[0]
        assert isinstance(res, compiler.Placeholder)
        assert res.value == compiler.VariableName("X")

    def test_compiles_Placeholder(self):
        res = compiler.placeholder.parseString("{V}")[0]
        assert res.compile({compiler.VariableName('V'): 'X'}) == 'X'

    def test_parses_Identifier(self):
        res = compiler.identifier.parseString("test{X}_energy{O}")[0]
        assert isinstance(res, compiler.Identifier)
        assert len(res.value) == 4
        assert isinstance(res.value[0], compiler.VariableName) and isinstance(res.value[2], compiler.VariableName)
        assert isinstance(res.value[1], compiler.Placeholder) and isinstance(res.value[3], compiler.Placeholder)
        assert res.value[0].value == "test" and res.value[2].value == "_energy"
        assert res.value[1].value == compiler.VariableName("X") and res.value[3].value == compiler.VariableName("O")

    def test_compiles_Identifier(self):
        res = compiler.identifier.parseString("test{V}_energy{O}")[0]
        assert res.compile({compiler.VariableName('V'): 'Q', compiler.VariableName('O'): 'M'}) == "testQ_energyM"

    def test_parses_simple_variable_name_as_identifier(self):
        res = compiler.identifier.parseString("testVar")[0]
        assert isinstance(res, compiler.Identifier)
        assert len(res.value) == 1 and isinstance(res.value[0], compiler.VariableName)

    def test_parses_Index(self):
        res = compiler.index.parseString("[com, sec]")[0]
        assert isinstance(res, compiler.Index)
        assert len(res.value) == 2
        assert res.value[0] == compiler.VariableName("com") and res.value[1] == compiler.VariableName("sec")

    def test_parses_Integer(self):
        res = compiler.integer.parseString("42")[0]
        assert isinstance(res, compiler.Integer)
        assert res.value == 42
        res = compiler.integer.parseString("-42")[0]
        assert isinstance(res, compiler.Integer)
        assert res.value == -42

    def test_parses_Real(self):
        res = compiler.real.parseString("3.14159")[0]
        assert isinstance(res, compiler.Real)
        assert res.value == 3.14159
        res = compiler.real.parseString("-3.14159")[0]
        assert isinstance(res, compiler.Real)
        assert res.value == -3.14159

    def test_parses_Array(self):
        res = compiler.array.parseString("{X}tes{M}_arrayName8[com, 5, sec]")[0]
        assert isinstance(res, compiler.Array)
        assert isinstance(res.identifier, compiler.Identifier)
        assert isinstance(res.index, compiler.Index)
        assert len(res.identifier.value) == 4
        assert len(res.index.value) == 3
        assert res.index.value[1].value == 5

    def test_compiles_Array(self):
        res = compiler.array.parseString("arrayName8[com, 5, sec]")[0]
        assert res.compile({compiler.VariableName('com'): '24', compiler.VariableName('sec'): '2403'}) == "arrayName8_24_5_2403"

    def test_parses_Func(self):
        res = compiler.func.parseString("d(log(test))")[0]
        assert isinstance(res, compiler.Func)
        assert res.name == 'd' and isinstance(res.expression, compiler.Expression)
        assert isinstance(res.expression.value[0], compiler.Func)

    def test_compiles_Func(self):
        res = compiler.func.parseString("d(log(test[j]))")[0]
        assert res.compile({compiler.VariableName('j'): '24'}) == "d(log(test_24))"

    def test_parses_Expression(self):
        res = compiler.expression.parseString("D{O}[com, sec] + d(log(Q[com, sec])) - A / B")[0]
        assert isinstance(res, compiler.Expression)
        assert len(res.value) == 7
        assert isinstance(res.value[0], compiler.Array)
        assert isinstance(res.value[1], compiler.Operator)
        assert isinstance(res.value[2], compiler.Func)
        assert isinstance(res.value[3], compiler.Operator)
        assert isinstance(res.value[4], compiler.Identifier)
        assert isinstance(res.value[5], compiler.Operator)
        assert isinstance(res.value[6], compiler.Identifier)

    def test_compiles_Expression(self):
        res = compiler.expression.parseString("D[com, sec] + d(log(Q[com, sec])) - A / B")[0]
        assert res.compile({compiler.VariableName('com'): '24', compiler.VariableName('sec'): '2403'}) == "D_24_2403 + d(log(Q_24_2403)) - A / B"

    def test_evaluates_Expression(self):
        res = compiler.expression.parseString("2 * Q[com, sec] + 4 * X[com, sec]")[0]
        assert res.evaluate({compiler.VariableName('com'): '24', compiler.VariableName('sec'): '2403'},
                            {'Q_24_2403': 1, 'X_24_2403': 10}) == 42
        res = compiler.expression.parseString("2 * Q[com, sec] - X[com, sec] ^ 2 < 0")[0]
        assert res.evaluate({compiler.VariableName('com'): '24', compiler.VariableName('sec'): '2403'},
                            {'Q_24_2403': 1, 'X_24_2403': 10}) == True

    def test_parses_Equation(self):
        res = compiler.equation.parseString("energy{O}[com] + _test{X}{M}[sec] = log(B[j])")[0]
        assert isinstance(res, compiler.Equation)
        assert isinstance(res.lhs, compiler.Expression)
        assert isinstance(res.rhs, compiler.Expression)

    def test_compiles_Equation(self):
        res = compiler.equation.parseString("energy[com] = log(B[3])")[0]
        assert res.compile({compiler.VariableName('com'): '24'}) == "energy_24 = log(B_3)"

    def test_parses_Condition(self):
        res = compiler.condition.parseString("if energy[com, sec] > 0")[0]
        assert isinstance(res, compiler.Condition)
        assert isinstance(res.expression, compiler.Expression)
        assert len(res.expression.value) == 3

    def test_parses_Lst(self):
        res = compiler.lst.parseString("01 02 03 04 05 06 07")[0]
        assert isinstance(res, compiler.Lst)
        assert len(res.value) == 7
        assert res.value[3] == "04"

    def test_parses_Iter(self):
        res = compiler.iter.parseString("com in 01 02 03 04 05 06 07")[0]
        assert isinstance(res, compiler.Iter)
        assert isinstance(res.variableName, compiler.VariableName)
        assert isinstance(res.lst, compiler.Lst)

    def test_parses_Formula(self):
        res = compiler.formula.parseString("{V}[com] = {V}D[com] + {V}M[com], V in Q CH G I DS, com in 01 02 03 04 05 06 07 08 09")[0]
        assert isinstance(res, compiler.Formula)
        assert isinstance(res.equation, compiler.Equation)
        assert len(res.iterators) == 2
        assert reduce(lambda x, y: x and y, [isinstance(e, compiler.Iter) for e in res.iterators])
        res = compiler.formula.parseString("{V}[com] = {V}D[com] + {V}M[com]")[0]
        assert isinstance(res, compiler.Formula)
        assert len(res.iterators) == 0

    def test_compiles_Formula(self):
        expected = ("Q_01 = QD_01 + QM_01\n"
                    "Q_02 = QD_02 + QM_02\n"
                    "CH_01 = CHD_01 + CHM_01\n"
                    "CH_02 = CHD_02 + CHM_02")
        res = compiler.formula.parseString("{V}[com] = {V}D[com] + {V}M[com], V in Q CH, com in 01 02")[0]
        assert res.compile() == expected
