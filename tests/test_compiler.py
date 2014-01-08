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

    def test_compiles_VariableName_Price_Volume(self):
        res = grammar.variableName.parseString("M")[0]
        assert res.compile({}, {}, '!pv') == 'PM * M'

    def test_parses_Placeholder(self):
        res = grammar.placeholder.parseString("|X|")[0]
        assert isinstance(res, grammar.Placeholder)
        assert res.value == grammar.VariableName("X")

    def test_compiles_Placeholder(self):
        res = grammar.placeholder.parseString("|V|")[0]
        assert res.compile({grammar.VariableName('V'): 'X'}, {}, '') == 'X'

    def test_parses_Identifier(self):
        res = grammar.identifier.parseString("test|X|_energy|O|")[0]
        assert isinstance(res, grammar.Identifier)
        assert len(res.value) == 4
        assert isinstance(res.value[0], grammar.VariableName) and isinstance(res.value[2], grammar.VariableName)
        assert isinstance(res.value[1], grammar.Placeholder) and isinstance(res.value[3], grammar.Placeholder)
        assert res.value[0].value == "test" and res.value[2].value == "_energy"
        assert res.value[1].value == grammar.VariableName("X") and res.value[3].value == grammar.VariableName("O")

    def test_compiles_Identifier(self):
        res = grammar.identifier.parseString("test|V|_energy|O|")[0]
        assert res.compile({grammar.VariableName('V'): 'Q', grammar.VariableName('O'): 'M'}, {}, '') == "testQ_energyM"

    def test_compiles_Identifier_Price_Volume(self):
        res = grammar.identifier.parseString("test|V|_energy|O|")[0]
        assert res.compile({grammar.VariableName('V'): 'Q', grammar.VariableName('O'): 'M'}, {}, '!pv') == "PtestQ_energyM * testQ_energyM"

    def test_parses_Simple_VariableName_as_Identifier(self):
        res = grammar.identifier.parseString("testVar")[0]
        assert isinstance(res, grammar.Identifier)
        assert len(res.value) == 1 and isinstance(res.value[0], grammar.VariableName)

    def test_parses_Index(self):
        res = grammar.index.parseString("[com, sec]")[0]
        assert isinstance(res, grammar.Index)
        assert len(res.value) == 2
        assert isinstance(res.value[0], grammar.Expression)
        assert isinstance(res.value[1], grammar.Expression)

    def test_parses_TimeOffset(self):
        res = grammar.timeOffset.parseString("(-1)")[0]
        assert isinstance(res, grammar.TimeOffset)
        assert res.value.value == -1
        res = grammar.timeOffset.parseString("(outOfTimeMan)")[0]
        assert isinstance(res, grammar.TimeOffset)
        assert isinstance(res.value, grammar.VariableName)
        assert res.value.value == "outOfTimeMan"

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
        res = grammar.array.parseString("|X|tes|M|_arrayName8[com, 5, sec]")[0]
        assert isinstance(res, grammar.Array)
        assert isinstance(res.identifier, grammar.Identifier)
        assert isinstance(res.index, grammar.Index)
        assert len(res.identifier.value) == 4
        assert len(res.index.value) == 3
        assert len(res.timeOffset) == 0
        res = grammar.array.parseString("timeAry[5](-1)")[0]
        assert isinstance(res, grammar.Array)
        assert isinstance(res.identifier, grammar.Identifier)
        assert isinstance(res.index, grammar.Index)
        assert len(res.timeOffset) == 1

    def test_compiles_Array(self):
        res = grammar.array.parseString("arrayName8[com, 5, sec]")[0]
        assert res.compile({grammar.VariableName('com'): '24', grammar.VariableName('sec'): '2403'}, {}, '') == "arrayName8_24_5_2403"
        res = grammar.array.parseString("timeAry[5](-1)")[0]
        assert res.compile({}, {}, '') == "timeAry_5(-1)"
        res = grammar.array.parseString("test[$s]")[0]
        assert res.compile({grammar.VariableName("$s"): 15}, {}, '') == "test_15"

    def test_compiles_Array_Price_Volume(self):
        res = grammar.array.parseString("arrayName8[com, 5, sec]")[0]
        assert res.compile({grammar.VariableName('com'): '24', grammar.VariableName('sec'): '2403'}, {}, '!pv') == "ParrayName8_24_5_2403 * arrayName8_24_5_2403"

    def test_parses_Func(self):
        res = grammar.func.parseString("d(log(test))")[0]
        assert isinstance(res, grammar.Func)
        assert res.variableName == grammar.VariableName('d') and isinstance(res.expressions[0], grammar.Expression)
        assert isinstance(res.expressions[0].value[0], grammar.Func)
        res = grammar.func.parseString("@elem(PK[s], %baseyear)")[0]
        assert isinstance(res, grammar.Func)
        assert res.variableName == grammar.VariableName('@elem')
        assert len(res.expressions) == 2

    def test_compiles_Func(self):
        res = grammar.func.parseString("d(log(test[j]))")[0]
        assert res.compile({grammar.VariableName('j'): '24'}, {}, '') == "d(log(test_24))"
        res = grammar.func.parseString("@elem(PK[s], %baseyear)")[0]
        assert res.compile({grammar.VariableName('s'): '13'}, {}, '') == "@elem(PK_13, %baseyear)"
        res = grammar.func.parseString("@elem(PK[s](-1), %baseyear)")[0]
        assert res.compile({grammar.VariableName('s'): '13'}, {}, '') == "@elem(PK_13(-1), %baseyear)"
        res = grammar.func.parseString("ES_KLEM($s, 1)")[0]
        assert res.compile({grammar.VariableName('$s'): '42'}, {}, '') == "ES_KLEM(42, 1)"

    def test_parses_Expression(self):
        res = grammar.expression.parseString("D|O|[com, sec] + d(log(Q[com, sec])) - A / B")[0]
        assert isinstance(res, grammar.Expression)
        assert len(res.value) == 7
        assert isinstance(res.value[0], grammar.Array)
        assert isinstance(res.value[1], grammar.Operator)
        assert isinstance(res.value[2], grammar.Func)
        assert isinstance(res.value[3], grammar.Operator)
        assert isinstance(res.value[4], grammar.Identifier)
        assert isinstance(res.value[5], grammar.Operator)
        assert isinstance(res.value[6], grammar.Identifier)
        res = grammar.expression.parseString("( (CH[c]>0) * CH[c] + (CH[c]<=0) * 1 )")[0]
        assert isinstance(res, grammar.Expression)
        res = grammar.expression.parseString("-ES_KLEM($s, 1) * d(log(CK[s]) - log(CL[s]))")[0]
        assert isinstance(res, grammar.Expression)
        assert len(res.value) == 4

    def test_compiles_Expression(self):
        res = grammar.expression.parseString("D[com, sec] + d(log(Q[com, sec])) - A / B")[0]
        assert res.compile({grammar.VariableName('com'): '24', grammar.VariableName('sec'): '2403'}, {}, '') == "D_24_2403 + d(log(Q_24_2403)) - A / B"
        res = grammar.expression.parseString("D[com, sec] + Q[com, sec] - A")[0]
        assert res.compile({grammar.VariableName('com'): '24', grammar.VariableName('sec'): '2403'}, {}, '!pv') == "PD_24_2403 * D_24_2403 + PQ_24_2403 * Q_24_2403 - PA * A"
        res = grammar.expression.parseString("( (CH[c]>0) * CH[c] + (CH[c]<=0) * 1 )")[0]
        assert res.compile({grammar.VariableName('c'): '01'}, {}, '') == "( ( CH_01 > 0 ) * CH_01 + ( CH_01 <= 0 ) * 1 )"
        res = grammar.expression.parseString("EBE[s] - @elem(PK[s](-1), %baseyear) * Tdec[s] * K[s](-1)")[0]
        assert res.compile({grammar.VariableName('s'): '02'}, {}, '') == "EBE_02 - @elem(PK_02(-1), %baseyear) * Tdec_02 * K_02(-1)"
        res = grammar.expression.parseString("s")[0]
        assert res.compile({grammar.VariableName('s'): '02'}, {}, '') == "02"

    def test_evaluates_Expression(self):
        res = grammar.expression.parseString("2 * Q[com, sec] + 4 * X[com, sec]")[0]
        assert res.evaluate({grammar.VariableName('com'): '24', grammar.VariableName('sec'): '2403'},
                            {'Q_24_2403': 1, 'X_24_2403': 10}) == 42
        res = grammar.expression.parseString("2 * Q[com, sec] - X[com, sec] ^ 2 < 0")[0]
        assert res.evaluate({grammar.VariableName('com'): '24', grammar.VariableName('sec'): '2403'},
                            {'Q_24_2403': 1, 'X_24_2403': 10}) == True

    def test_parses_Equation(self):
        res = grammar.equation.parseString("energy|O|[com] + _test|X||M|[sec] = log(B[j])")[0]
        assert isinstance(res, grammar.Equation)
        assert isinstance(res.lhs, grammar.Expression)
        assert isinstance(res.rhs, grammar.Expression)

    def test_compiles_Equation(self):
        res = grammar.equation.parseString("energy[com] = log(B[3])")[0]
        assert res.compile({grammar.VariableName('com'): '24'}, {}, '') == "energy_24 = log(B_3)"
        res = grammar.equation.parseString("energy[com] = B[3]")[0]
        assert res.compile({grammar.VariableName('com'): '24'}, {}, '!pv') == "Penergy_24 * energy_24 = PB_3 * B_3\nenergy_24 = B_3"

    def test_parses_Condition(self):
        res = grammar.condition.parseString("if energy[com, sec] > 0")[0]
        assert isinstance(res, grammar.Condition)
        assert isinstance(res.expression, grammar.Expression)
        assert len(res.expression.value) == 3

    def test_parses_Lst(self):
        res = grammar.lst.parseString("01 02 03 04 05 06 07")[0]
        assert isinstance(res, grammar.Lst)
        assert len(res.base) == 7
        assert res.base[3] == "04"
        res = grammar.lst.parseString("01 02 03 04 05 06 07 \ 04 06")[0]
        assert isinstance(res, grammar.Lst)
        assert len(res.base) == 7
        assert len(res.remove) == 2
        assert res.base[3] == "04"
        assert res.remove[1] == "06"

    def test_compiles_Lst(self):
        res = grammar.lst.parseString("01 02 03 04 05 06 07")[0]
        assert res.compile() == ['01', '02', '03', '04', '05', '06', '07']
        res = grammar.lst.parseString("01 02 03 04 05 06 07 \ 04 06")[0]
        assert res.compile() == ['01', '02', '03', '05', '07']

    def test_parses_Iter(self):
        res = grammar.iter.parseString("com in 01 02 03 04 05 06 07")[0]
        assert isinstance(res, grammar.Iter)
        assert isinstance(res.variableName, grammar.VariableName)
        assert isinstance(res.lst, grammar.Lst)

    def test_parses_SumFunc(self):
        res = grammar.sumFunc.parseString("sum(q[c, s] if q[c, s] <> 0, c in 01 02 03)")[0]
        assert isinstance(res, grammar.SumFunc)
        assert isinstance(res.formula, grammar.Formula)

    def test_compiles_SumFunc(self):
        res = grammar.sumFunc.parseString("sum(Q[c, s] if Q[c, s] <> 0, c in 01 02 03)")[0]
        assert res.compile({grammar.VariableName('s'): '10'}, {'Q_01_10': 15, 'Q_02_10': 0, 'Q_03_10': 20}, '') == "0 + Q_01_10 + Q_03_10"

    def test_parses_Formula(self):
        res = grammar.formula.parseString("|V|[com] = |V|D[com] + |V|M[com], V in Q CH G I DS, com in 01 02 03 04 05 06 07 08 09")[0]
        assert isinstance(res, grammar.Formula)
        assert isinstance(res.equation, grammar.Equation)
        assert len(res.iterators) == 2
        assert reduce(lambda x, y: x and y, [isinstance(e, grammar.Iter) for e in res.iterators])
        res = grammar.formula.parseString("Q = QD + QM")[0]
        assert isinstance(res, grammar.Formula)
        assert len(res.iterators) == 0
        res = grammar.formula.parseString("|V|[com] = |V|D[com] + |V|M[com] if |V|[com] > 0, V in Q CH I, com in 01 02 07 08 09")[0]
        assert isinstance(res, grammar.Formula)
        assert len(res.conditions) == 1
        assert isinstance(res.conditions[0], grammar.Condition)
        assert len(res.iterators) == 2
        res = grammar.formula.parseString("Q[s] = sum(Q[c, s] if Q[c, s] <> 0, c in 01 02 03), s in 10 11 12")[0]
        assert isinstance(res, grammar.Formula)
        assert len(res.iterators)

    def test_compiles_Formula(self):
        expected = ("Q_01 = QD_01 + QM_01\n"
                    "Q_02 = QD_02 + QM_02\n"
                    "CH_01 = CHD_01 + CHM_01\n"
                    "CH_02 = CHD_02 + CHM_02")
        res = grammar.formula.parseString("|V|[com] = |V|D[com] + |V|M[com], V in Q CH, com in 01 02")[0]
        assert res.compile({}) == expected
        expected = ("Q_02 = QD_02 + QM_02\n"
                    "CH_02 = CHD_02 + CHM_02")
        res = grammar.formula.parseString("|V|[com] = |V|D[com] + |V|M[com] if CHD[com] > 0, V in Q CH, com in 01 02")[0]
        assert res.compile({"CHD_01": 0, "CHD_02": 15}) == expected
        expected = ("PQ_02 * Q_02 = PQD_02 * QD_02 + PQM_02 * QM_02\n"
                    "Q_02 = QD_02 + QM_02\n"
                    "PCH_02 * CH_02 = PCHD_02 * CHD_02 + PCHM_02 * CHM_02\n"
                    "CH_02 = CHD_02 + CHM_02")
        res = grammar.formula.parseString("!Pv |V|[com] = |V|D[com] + |V|M[com] if CHD[com] > 0, V in Q CH, com in 01 02")[0]
        assert res.compile({"CHD_01": 0, "CHD_02": 15}) == expected
        expected = ("Q_10 = 0 + Q_01_10 + Q_03_10\n"
                    "Q_11 = 0 + Q_01_11 + Q_02_11 + Q_03_11\n"
                    "Q_12 = 0 + Q_01_12 + Q_02_12")
        res = grammar.formula.parseString("Q[s] = sum(Q[c, s] if Q[c, s] <> 0, c in 01 02 03), s in 10 11 12")[0]
        assert res.compile({'Q_01_10': 15, 'Q_02_10': 0,  'Q_03_10': 20,
                            'Q_01_11': 15, 'Q_02_11': 42, 'Q_03_11': 20,
                            'Q_01_12': 15, 'Q_02_12': 13, 'Q_03_12': 0}) == expected
        expected = ("PQ_10 * Q_10 = 0 + PQ_01_10 * Q_01_10 + PQ_03_10 * Q_03_10\n"
                    "Q_10 = 0 + Q_01_10 + Q_03_10\n"
                    "PQ_11 * Q_11 = 0 + PQ_01_11 * Q_01_11 + PQ_02_11 * Q_02_11 + PQ_03_11 * Q_03_11\n"
                    "Q_11 = 0 + Q_01_11 + Q_02_11 + Q_03_11")
        res = grammar.formula.parseString("!pv Q[s] = sum(Q[c, s] if Q[c, s] <> 0, c in 01 02 03), s in 10 11")[0]
        assert res.compile({'Q_01_10': 15, 'Q_02_10': 0,  'Q_03_10': 20,
                            'Q_01_11': 15, 'Q_02_11': 42, 'Q_03_11': 20}) == expected
        expected = ("Q_04 = Test_1 + 2 * 1\n"
                    "Q_05 = Test_2 + 2 * 2\n"
                    "Q_06 = Test_3 + 2 * 3")
        res = grammar.formula.parseString("Q[c] = Test[$c] + 2 * $c, c in 04 05 06")[0]
        assert res.compile({}) == expected
