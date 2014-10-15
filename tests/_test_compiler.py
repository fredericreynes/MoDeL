from .. import grammar
from .. import traversal
from .. import lineparser
from .. import compiler
import csv
import os

class TestParser(object):

    def _expected(self, res, nodetype, children_count, *children_types):
        assert res.nodetype == nodetype
        assert len(res.children) == children_count
        for i, t in enumerate(children_types):
            if t is None:
                assert res.children[i] is None
            elif t == traversal.ASTNone:
                assert res.children[i] == traversal.ASTNone
            else:
                assert res.children[i].nodetype == t

    def test_parses_integer(self):
        res = grammar.integer.parseString("42")[0]
        assert res.nodetype == "integer"
        assert res.immediate == 42
        res = grammar.integer.parseString("-42")[0]
        assert res.nodetype == "integer"
        assert res.immediate == -42

    def test_parses_real(self):
        res = grammar.real.parseString("3.14159")[0]
        assert res.nodetype == "real"
        assert res.immediate == 3.14159
        res = grammar.real.parseString("-3.14159")[0]
        assert res.nodetype == "real"
        assert res.immediate == -3.14159

    def test_parses_variableName(self):
        res = grammar.variableName.parseString("testVariable")[0]
        assert res.nodetype == "variableName"
        assert res.immediate == "testVariable"
        res = grammar.variableName.parseString("_test9_Variable")[0]
        assert res.nodetype == "variableName"
        assert res.immediate == "_test9_Variable"

    def test_parses_placeholder(self):
        res = grammar.placeholder.parseString("|X|")[0]
        self._expected(res, "placeholder", 1, "variableName")

    def test_parses_identifier(self):
        res = grammar.identifier.parseString("test|X|_energy|O|")[0]
        self._expected(res, "identifier", 4, "variableName", "placeholder", "variableName", "placeholder")
        res = grammar.identifier.parseString("testVar")[0]
        self._expected(res, "identifier", 1, "variableName")

    def test_parses_identifierTime(self):
        res = grammar.identifierTime.parseString("test|X|_energy|O|{-1}")[0]
        self._expected(res, "identifierTime", 2, "identifier", "timeOffset")

    def test_parses_timeOffset(self):
        res = grammar.timeOffset.parseString("{-1}")[0]
        self._expected(res, "timeOffset", 1, "integer")
        res = grammar.timeOffset.parseString("{outOfTimeMan}")[0]
        self._expected(res, "timeOffset", 1, "variableName")

    def test_parses_index(self):
        res = grammar.index.parseString("[com, sec]")[0]
        self._expected(res, "index", 2, "expression", "expression")

    def test_parses_array(self):
        res = grammar.array.parseString("|X|tes|M|_arrayName8[com, 5, sec]")[0]
        self._expected(res, "array", 3, "identifier", "index", traversal.ASTNone)
        res = grammar.array.parseString("timeAry[5]{-1}")[0]
        self._expected(res, "array", 3, "identifier", "index", "timeOffset")

    def test_parses_function(self):
        res = grammar.func.parseString("d(log(test))")[0]
        self._expected(res, "function", 2, "variableName", "formula")
        assert res.children[1].children[1].nodetype == "expression"
        res = grammar.func.parseString("@elem(PK[s], %baseyear)")[0]
        self._expected(res, "function", 3, "variableName", "expression", "expression")
        assert res.children[0].immediate == '@elem'
        res = grammar.func.parseString("multiple(c, s, 42)")[0]
        self._expected(res, "function", 4, "variableName", "expression", "expression", "expression")

    def test_parses_expression(self):
        res = grammar.expression.parseString("D|O|[com, sec] + d(log(Q[com, sec])) - A / B")[0]
        self._expected(res, "expression", 7, "array", "operator", "function", "operator", "identifier", "operator", "identifier")
        res = grammar.expression.parseString("( (CH[c]>0) * CH[c] + (CH[c]<=0) * 1 )")[0]
        self._expected(res, "expression", 3, "literal", "expression", "literal")
        res = grammar.expression.parseString("( (CH[c]>=0) * CH[c] + (CH[c]=>0) * 1 )")[0]
        self._expected(res, "expression", 3, "literal", "expression", "literal")
        res = grammar.expression.parseString("-ES_KLEM($s, 1) * d(log(CK[s]) - log(CL[s]))")[0]
        self._expected(res, "expression", 4, "operator", "function", "operator", "function")
        # res = grammar.expression.parseString("-ES_KLEM{-1}")[0]
        # self._expected(res, "expression", 2, "identifierTime")

    def test_parses_equation(self):
        res = grammar.equation.parseString("energy|O|[com] + _test|X||M|[sec] = log(B[j])")[0]
        self._expected(res, "equation", 2, "expression", "expression")

    def test_parses_condition(self):
        res = grammar.condition.parseString("if energy[com, sec] > 0")[0]
        self._expected(res, "condition", 1, "expression")

    def test_parses_listBase(self):
        res = grammar.lstBase.parseString("01 02 03 04 05 06 07")[0]
        self._expected(res, "listBase", 7, "string", "string", "string", "string", "string", "string", "string")

    def test_parses_list(self):
        res = grammar.lst.parseString("01 02 03 04 05 06 07")[0]
        self._expected(res, "list", 2, "listBase", traversal.ASTNone)
        assert res.children[0].children[3].immediate == "04"
        res = grammar.lst.parseString("Q_Mtep Q_Mtep_ES")[0]
        self._expected(res, "list", 2, "listBase", traversal.ASTNone)
        assert res.children[0].children[1].immediate == "Q_Mtep_ES"
        res = grammar.lst.parseString("01 02 03 04 05 06 07 \ 04 06")[0]
        self._expected(res, "list", 2, "listBase", "listBase")
        assert res.children[0].children[3].immediate == "04"
        assert res.children[1].children[1].immediate == "06"

    def test_parses_iterator(self):
        res = grammar.iter.parseString("com in 01 02 03 04 05 06 07")[0]
        self._expected(res, "iterator", 2, "group", "group")
        res = grammar.iter.parseString("(c, s) in (01 02 03, 04 05 06)")[0]
        self._expected(res, "iterator", 2, "group", "group")

    def test_parses_formula(self):
        res = grammar.formula.parseString("|V|[com] = |V|D[com] + |V|M[com] where V in Q CH G I DS, com in 01 02 03 04 05 06 07 08 09")[0]
        self._expected(res, "formula", 5, "none", "equation", "none", "iterator", "iterator")
        res = grammar.formula.parseString("Q = QD + QM")[0]
        self._expected(res, "formula", 4, "none", "equation", "none", "none")
        res = grammar.formula.parseString("|V|[com] = |V|D[com] + |V|M[com] if |V|[com] > 0 where V in Q CH I, com in 01 02 07 08 09")[0]
        self._expected(res, "formula", 5, "none", "equation", "condition", "iterator", "iterator")
        res = grammar.formula.parseString("Q[s] = sum(Q[c, s] if Q[c, s] <> 0 where c in 01 02 03) where s in 10 11 12")[0]
        self._expected(res, "formula", 4, "none", "equation", "none", "iterator")
        self._expected(res.children[1].children[1], 'expression', 1, "function")

    def test_parses_formula(self):
        res = grammar.seriesFormula.parseString("|V|[com] := |V|D[com] + |V|M[com] where V in Q CH G I DS, com in 01 02 03 04 05 06 07 08 09")[0]
        self._expected(res, "seriesFormula", 5, "none", "equation", "none", "iterator", "iterator")

    def test_parses_assignment(self):
        res = grammar.assignment.parseString("%test := 1 2 3")[0]
        self._expected(res, "assignment", 2, "group", "group")
        res = grammar.assignment.parseString("(%test, %pouet) := (1 2 3, 15 12 3)")[0]
        self._expected(res, "assignment", 2, "group", "group")
        self._expected(res.children[0], "group", 2, "localName", "localName")
        self._expected(res.children[1], "group", 2, "list", "list")

    def test_parses_instruction(self):
        res = grammar.instruction.parseString("Q[s] = sum(Q[c, s] if Q[c, s] <> 0 where c in 01 02 03), s in 10 11 12")[0]
        self._expected(res, "instruction", 1, "formula")
        res = grammar.instruction.parseString("Q[s] := sum(Q[c, s] if Q[c, s] <> 0 where c in 01 02 03), s in 10 11 12")[0]
        self._expected(res, "instruction", 1, "seriesFormula")
        res = grammar.instruction.parseString("%test := 1 2 3")[0]
        self._expected(res, "instruction", 1, "assignment")
        res = grammar.instruction.parseString("s in 1 2 3")[0]
        self._expected(res, "instruction", 1, "iterator")
        res = grammar.instruction.parseString("s in %list_sec")[0]
        self._expected(res, "instruction", 1, "iterator")

class TestCompiler(object):
    def test_compiles_integer(self):
        ast = grammar.integer.parseString("42")[0]
        assert traversal.compile_ast(ast).compiled == 42

    def test_compiles_real(self):
        ast = grammar.real.parseString("3.14159")[0]
        assert traversal.compile_ast(ast).compiled == 3.14159

    def test_compiles_variableName(self):
        ast = grammar.variableName.parseString("_test9_Variable")[0]
        assert traversal.compile_ast(ast).compiled == "_test9_Variable"

    def test_compiles_list(self):
        ast = grammar.lst.parseString("01 02 03 04 05")[0]
        assert traversal.compile_ast(ast).compiled == { 'list': ['01', '02', '03', '04', '05'],
                                                        'loopCounters': [1, 2, 3, 4, 5] }
        ast = grammar.lst.parseString("01 02 03 04 05 06 07 \ 04 06")[0]
        assert traversal.compile_ast(ast).compiled == { 'list' : ['01', '02', '03', '05', '07'],
                                                        'loopCounters': [1, 2, 3, 5, 7] }
        ast = grammar.lst.parseString("%variables")[0]
        assert traversal.compile_ast(ast, heap = {'%variables': {'list': ['Q', 'CH', 'G', 'I', 'DS'],
                                                                 'loopCounters': [1, 2, 3, 4, 5]} }).compiled == {'list': ['Q', 'CH', 'G', 'I', 'DS'],
                                                                                                                  'loopCounters': [1, 2, 3, 4, 5]}


    def test_compiles_placeholder(self):
        ast = grammar.placeholder.parseString("|V|")[0]
        assert traversal.compile_ast(ast, bindings = {'V': 'X'})[0].compiled == 'X'

    def test_compiles_iterator(self):
        ast = grammar.iter.parseString("V in Q CH G I DS")[0]
        assert traversal.compile_ast(ast).compiled == {'names': ['V', '$V'],
                                                       'lists': [('Q', 1), ('CH', 2), ('G', 3), ('I', 4), ('DS', 5)]}
        ast = grammar.iter.parseString("V in Q CH G I DS \ CH I DS")[0]
        assert traversal.compile_ast(ast).compiled == {'names': ['V', '$V'],
                                                       'lists': [('Q', 1), ('G', 3)]}
        ast = grammar.iter.parseString("(c, s) in (01 02 03, 04 05 06)")[0]
        assert traversal.compile_ast(ast).compiled == {'names': ['c', '$c', 's', '$s'],
                                                       'lists': [('01', 1, '04', 1),
                                                                 ('02', 2, '05', 2),
                                                                 ('03', 3, '06', 3)]}
        ast = grammar.iter.parseString("V in %variables")[0]
        assert traversal.compile_ast(ast, heap = {'%variables': {'list': ['Q', 'CH', 'G', 'I', 'DS'],
                                                                 'loopCounters': [1, 2, 3, 4, 5]} }).compiled == {'names': ['V', '$V'],
                                                                                                                  'lists': [('Q', 1), ('CH', 2), ('G', 3), ('I', 4), ('DS', 5)]}
        ast = grammar.iter.parseString("V in %variables \ CH I DS")[0]
        assert traversal.compile_ast(ast, heap = {'%variables': {'list': ['Q', 'CH', 'G', 'I', 'DS'],
                                                                 'loopCounters': [1, 2, 3, 4, 5]} }).compiled == {'names': ['V', '$V'],
                                                                                                                  'lists': [('Q', 1), ('G', 3)]}
        ast = grammar.iter.parseString("V in %variables \ %exclusion")[0]
        assert traversal.compile_ast(ast, heap = {'%variables': {'list': ['Q', 'CH', 'G', 'I', 'DS'],
                                                                 'loopCounters': [1, 2, 3, 4, 5]},
                                                  '%exclusion': {'list': ['CH', 'I', 'DS'],
                                                                 'loopCounters': [2, 4, 5]}}).compiled == {'names': ['V', '$V'],
                                                                                                           'lists': [('Q', 1), ('G', 3)]}



class TestGenerator(object):
    def test_generates_integer(self):
        ast = grammar.integer.parseString("42")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast))
        assert res.generated == "42"

    def test_generates_real(self):
        ast = grammar.real.parseString("3.14159")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast))
        assert res.generated == "3.14159"

    def test_generates_variableName(self):
        ast = grammar.variableName.parseString("_test9_Variable")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast))
        assert res.generated == "_test9_Variable"
        ast = grammar.variableName.parseString("M")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast, as_value = True))
        assert res.generated == 'PM * M'

    def test_generates_identifier(self):
        ast = grammar.identifier.parseString("test|V|_energy|O|")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast, {'V': 'Q', 'O': 'M'}))
        assert res.generated == "testQ_energyM"
        ast = grammar.identifier.parseString("test|V|_energy|O|")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast, {'V': 'Q', 'O': 'M'}, as_value = True))
        assert res.generated == "PtestQ_energyM * testQ_energyM"

    def test_generates_identifierTime(self):
        ast = grammar.identifierTime.parseString("test|V|_energy|O|{-1}")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast, {'V': 'Q', 'O': 'M'}))
        assert res.generated == "testQ_energyM(-1)"

    def test_generates_array(self):
        ast = grammar.array.parseString("arrayName8[com, 5, sec]")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast, {'com': '24', 'sec': '2403'}))
        assert res.generated == "arrayName8_24_5_2403"
        ast = grammar.array.parseString("timeAry[5]{-1}")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast))
        assert res.generated == "timeAry_5(-1)"
        ast = grammar.array.parseString("test[$s]")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast, {'$s': 15}))
        assert res.generated == "test_15"
        ast = grammar.array.parseString("arrayName8[com, 5, sec]")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast, {'com': '24', 'sec': '2403'}, as_value = True))
        assert res.generated == "ParrayName8_24_5_2403 * arrayName8_24_5_2403"

    def test_generates_function(self):
        ast = grammar.func.parseString("d(log(test[j]))")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast, {'j': 24}))
        assert res.generated == "d(log(test_24))"
        ast = grammar.func.parseString("@elem(PK, %baseyear)")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast, heap = {'%baseyear': 2006}))
        assert res.generated == "@elem(PK, 2006)"
        ast = grammar.func.parseString("@elem(PK[s]{-1}, %baseyear)")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast, {'s': 13}, heap = {'%baseyear': 2006}))
        assert res.generated == "@elem(PK_13(-1), 2006)"
        ast = grammar.func.parseString("ES_KLEM($s, 1)")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast, {'$s': 42}))
        assert res.generated == "ES_KLEM(42, 1)"
        ast = grammar.func.parseString("sum(Q[c, s] if Q[c, s] <> 0 where c in 01 02 03)")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast, {'s': '10'}), {'Q_01_10': 15, 'Q_02_10': 0, 'Q_03_10': 20})
        assert res.generated == "0 + Q_01_10 + Q_03_10"
        ast = grammar.func.parseString("sum(Q[c, s] if Q[c, s] <> 0 where c in 02 03)")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast, {'s': '10'}), {'Q_01_10': 15, 'Q_02_10': 0, 'Q_03_10': 0})
        assert res.generated == "0"
        ast = grammar.func.parseString("value(QD[c] + ID[c])")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast, {'c': '42'}))
        print res.generated
        assert res.generated == "PQD_42 * QD_42 + PID_42 * ID_42"
        ast = grammar.func.parseString("sum(c1 - c2 if c1 <> c2 where (c1, c2) in (01 02 03, 01 02 03))")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast, {'s': '10'}), {'Q_01_10': 15, 'Q_02_10': 0, 'Q_03_10': 20})
        assert res.generated == "0"
        ast = grammar.func.parseString("sum(|V|[c] where c in 01 02 03)")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast, {'V': 'Q'}))
        assert res.generated == "0 + Q_01 + Q_02 + Q_03"
        ast = grammar.func.parseString("sum(Q[c] where c in %list_com)")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast, heap = {'%list_com': ['01', '02', '03']}))
        assert res.generated == "0 + Q_01 + Q_02 + Q_03"
        ast = grammar.func.parseString("if(Q[s] <> 0, 42, YQ[s])")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast, {'s': '01'}), {'Q_01': 15, 'YQ_01': 0})
        assert res.generated == "42"


    def test_generates_equation(self):
        ast = grammar.equation.parseString("energy[com] = B[3]")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast, {'com': '24'}))
        assert res.generated == "energy_24 = B_3"
        ast = grammar.equation.parseString("energy[com] = log(B[3])")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast, {'com': '24'}))
        assert res.generated == "energy_24 = log(B_3)"
        ast = grammar.equation.parseString("energy[com] = B[3]")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast, {'com': '24'}, as_value = True))
        assert res.generated == "Penergy_24 * energy_24 = PB_3 * B_3"

    def test_generates_expression(self):
        ast = grammar.expression.parseString("D[com, sec] + d(log(Q)) - A / B")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast, {'com': '24', 'sec': '2403'}))
        assert res.generated == "D_24_2403 + d(log(Q)) - A / B"
        ast = grammar.expression.parseString("D[com, sec] + Q[com, sec] - A")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast, {'com': '24', 'sec': '2403'}, as_value = True))
        assert res.generated == "PD_24_2403 * D_24_2403 + PQ_24_2403 * Q_24_2403 - PA * A"
        ast = grammar.expression.parseString("( (CH[c]>0) * CH[c] + (CH[c]<=0) * 1 )")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast, {'c': '01'}))
        assert res.generated == "( ( CH_01 > 0 ) * CH_01 + ( CH_01 <= 0 ) * 1 )"
        ast = grammar.expression.parseString("EBE[s] - @elem(PK[s]{-1}, %baseyear) * Tdec[s] * K[s]{-1}")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast, {'s': '02'}, heap = {'%baseyear': 2006}))
        assert res.generated == "EBE_02 - @elem(PK_02(-1), 2006) * Tdec_02 * K_02(-1)"
        ast = grammar.expression.parseString("s")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast, {'s': '02'}, use_bindings = True))
        assert res.generated == "02"

    def test_generates_condition(self):
        ast= grammar.condition.parseString("if 2 * Q[com, sec] + 4 * X[com, sec] > 0")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast, {'com': '24', 'sec': '2403'}), {'Q_24_2403': 1, 'X_24_2403': 10})
        assert res.generated == "2 * Q_24_2403 + 4 * X_24_2403 > 0"
        ast = grammar.condition.parseString("if 2 * Q[com, sec] - X[com, sec] ^ 2 < 0")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast, {'com': '24', 'sec': '2403'}), {'Q_24_2403': 1, 'X_24_2403': 10})
        assert res.generated == "2 * Q_24_2403 - X_24_2403 ^ 2 < 0"

    def test_generates_formula(self):
        expected = ("Q_01 = QD_01 + QM_01\n"
                    "Q_02 = QD_02 + QM_02\n"
                    "CH_01 = CHD_01 + CHM_01\n"
                    "CH_02 = CHD_02 + CHM_02")
        ast = grammar.formula.parseString("|V|[com] = |V|D[com] + |V|M[com] where V in Q CH, com in 01 02")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast))
        assert '\n'.join(res.generated) == expected
        expected = ("Q_02 = QD_02 + QM_02\n"
                    "CH_02 = CHD_02 + CHM_02")
        ast = grammar.formula.parseString("|V|[com] = |V|D[com] + |V|M[com] if CHD[com] > 0 where V in Q CH, com in 01 02")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast), {"CHD_01": 0, "CHD_02": 15})
        assert '\n'.join(res.generated) == expected
        expected = ("Q_02 = QD_02 + QM_02\n"
                    "CH_02 = CHD_02 + CHM_02\n"
                    "PQ_02 * Q_02 = PQD_02 * QD_02 + PQM_02 * QM_02\n"
                    "PCH_02 * CH_02 = PCHD_02 * CHD_02 + PCHM_02 * CHM_02")
        ast = grammar.formula.parseString("@pv |V|[com] = |V|D[com] + |V|M[com] if CHD[com] > 0 where V in Q CH, com in 01 02")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast), {"CHD_01": 0, "CHD_02": 15})
        assert '\n'.join(res.generated) == expected
        expected = ("Q_10 = 0 + Q_01_10 + Q_03_10\n"
                    "Q_11 = 0 + Q_01_11 + Q_02_11 + Q_03_11\n"
                    "Q_12 = 0 + Q_01_12 + Q_02_12")
        ast = grammar.formula.parseString("Q[s] = sum(Q[c, s] if Q[c, s] <> 0 where c in 01 02 03) where s in 10 11 12")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast),
                                            {'Q_01_10': 15, 'Q_02_10': 0,  'Q_03_10': 20,
                                             'Q_01_11': 15, 'Q_02_11': 42, 'Q_03_11': 20,
                                             'Q_01_12': 15, 'Q_02_12': 13, 'Q_03_12': 0})
        assert '\n'.join(res.generated) == expected
        expected = ("Q_10 = 0 + Q_01_10 + Q_03_10\n"
                    "Q_11 = 0 + Q_01_11 + Q_02_11 + Q_03_11\n"
                    "PQ_10 * Q_10 = 0 + PQ_01_10 * Q_01_10 + PQ_03_10 * Q_03_10\n"
                    "PQ_11 * Q_11 = 0 + PQ_01_11 * Q_01_11 + PQ_02_11 * Q_02_11 + PQ_03_11 * Q_03_11")
        ast = grammar.formula.parseString("@pv Q[s] = sum(Q[c, s] if Q[c, s] <> 0 where c in 01 02 03) where s in 10 11")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast),
                                    {'Q_01_10': 15, 'Q_02_10': 0,  'Q_03_10': 20,
                                     'Q_01_11': 15, 'Q_02_11': 42, 'Q_03_11': 20})
        assert '\n'.join(res.generated) == expected
        expected = ("Q_04 = Test_1 + 2 * 1\n"
                    "Q_05 = Test_2 + 2 * 2\n"
                    "Q_06 = Test_3 + 2 * 3")
        ast = grammar.formula.parseString("Q[c] = Test[$c] + 2 * $c where c in 04 05 06")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast))
        assert '\n'.join(res.generated) == expected
        expected = ("Q_04 = QD_04 + QM_04")
        ast = grammar.formula.parseString("Q[c] = QD[c] + QM[c] if K_n[c] <> 0 where c in 04 05")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast), {'K_N_04': 15, 'K_N_05': 0})
        assert '\n'.join(res.generated) == expected
        expected = ("PM_01 = PWD_01 * TC")
        ast = grammar.formula.parseString("PM[c] = PWD[c]*TC if M[c] <> 0 where c in 01 02")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast), {'M_01': 15, 'M_02': 0})
        assert '\n'.join(res.generated) == expected
        expected = ("YQ = 0 + YQ_01 + YQ_02 + YQ_03\n"
                    "M = 0 + M_01 + M_02 + M_03")
        ast = grammar.formula.parseString("|V| = sum(|V|[c] where c in 01 02 03) where V in YQ M")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast))
        assert '\n'.join(res.generated) == expected
        expected = "EMS_HH_BUIL_21_H01_CA = 42"
        ast = grammar.formula.parseString("EMS_HH_BUIL[s, h, class] = 42 where s in %list_sector, h in %list_household, class in %list_class")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast, heap = {'%list_sector': '21', '%list_household': 'H01', '%list_class': 'CA' }))
        assert '\n'.join(res.generated) == expected
        expected = "Q = 0 + Q_01 + Q_02 + Q_03"
        ast = grammar.formula.parseString("Q = sum(Q[c] where c in %list_com)")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast, heap = {'%list_com': ['01', '02', '03']}))
        assert '\n'.join(res.generated) == expected
        expected = ("Q = 0 + Q_01 + Q_02 + Q_03\n"
                    "PQ * Q = 0 + PQ_01 * Q_01 + PQ_02 * Q_02 + PQ_03 * Q_03")
        ast = grammar.formula.parseString("@pv Q = sum(Q[c] where c in %list_com)")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast, heap = {'%list_com': {'list': ['01', '02', '03'], 'loopCounters': [1, 2, 3]} }))
        assert '\n'.join(res.generated) == expected
        expected = ("d(log(EMS_01)) = d(log(E_01))\n"
                    "d(log(EMS_02)) = d(log(E_02))\n"
                    "d(log(EMS_03)) = d(log(E_03))")
        ast = grammar.formula.parseString("d(log(EMS[s])) = d(log(E[s]))")[0]
        iter = grammar.compile_ast(grammar.iter.parseString("s in 01 02 03")[0]).compiled
        res, _ = traversal.generate(traversal.compile_ast(ast, heap = {'s': iter }))
        assert '\n'.join(res.generated) == expected
        expected = ("TCO_VAL_sec_21 = 0 + TCO_VAL_21_01 + TCO_VAL_21_02 + TCO_VAL_21_03\n"
                    "TCO_VAL_sec_22 = 0 + TCO_VAL_22_01 + TCO_VAL_22_02 + TCO_VAL_22_03\n"
                    "TCO_VAL_sec_24 = 0 + TCO_VAL_24_01 + TCO_VAL_24_02 + TCO_VAL_24_03")
        ce2_iter = traversal.compile_ast(grammar.iter.parseString("ce2 in 21 22 24")[0]).compiled
        s_iter = traversal.compile_ast(grammar.iter.parseString("s in 01 02 03")[0]).compiled
        ast = grammar.formula.parseString("TCO_VAL_sec[ce2] = sum(TCO_VAL[ce2, s] where s in 01 02 03)")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast, heap = {'s': s_iter, 'ce2': ce2_iter}))
        assert '\n'.join(res.generated) == expected
        ast = grammar.formula.parseString("TCO_VAL_sec[ce2] = sum(TCO_VAL[ce2, s] where s)")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast, heap = {'s': s_iter, 'ce2': ce2_iter}))
        assert '\n'.join(res.generated) == expected

    def test_generates_seriesFormula(self):
        expected = ("if @elem(CHD_01, \"2006\")  > 0 then\n"
                    "  series Q_01 = QD_01 + QM_01\n"
                    "endif\n"
                    "if @elem(CHD_02, \"2006\")  > 0 then\n"
                    "  series Q_02 = QD_02 + QM_02\n"
                    "endif")
        ast = grammar.seriesFormula.parseString("Q[com] := QD[com] + QM[com] if CHD[com] > 0 where com in 01 02")[0]
        res, _ = traversal.generate(traversal.compile_ast(ast), {"%baseyear": 2006, "CHD_01": 0, "CHD_02": 15})
        assert '\n'.join(res.generated) == expected


    def test_generates_assignment(self):
        ast = grammar.assignment.parseString("(%test, %pouet) := (1 2 3, 15 12 3)")[0]
        res, heap = traversal.generate(traversal.compile_ast(ast))
        assert res.generated == ""
        assert heap['%test'] == {'list': ['1', '2', '3'],
                                 'loopCounters': [1, 2, 3]}
        assert heap['%pouet'] == {'list': ['15', '12', '3'],
                                  'loopCounters': [1, 2, 3]}
        ast = grammar.assignment.parseString("%baseyear := 2006")[0]
        res, heap = traversal.generate(traversal.compile_ast(ast))
        assert res.generated == ""
        assert heap['%baseyear'] == '2006'
        ast = grammar.assignment.parseString("%list_household := H01")[0]
        res, heap = traversal.generate(traversal.compile_ast(ast))
        assert res.generated == ""
        assert heap['%list_household'] == 'H01'

    def test_generates_instruction(self):
        ast = grammar.instruction.parseString("s in 1 2 3")[0]
        res, heap = traversal.generate(traversal.compile_ast(ast))
        assert res.generated == ""
        assert heap['s'] == {'names': ['s', '$s'],
                             'lists': [('1', 1), ('2', 2), ('3', 3)]}
        ast = grammar.instruction.parseString("s in %list_sec")[0]
        res, heap = traversal.generate(traversal.compile_ast(ast, heap = {'%list_sec': {'list': ['1', '2', '3'], 'loopCounters': [1, 2, 3]} }))
        assert res.generated == ""
        assert heap['s'] == {'names': ['s', '$s'],
                             'lists': [('1', 1), ('2', 2), ('3', 3)]}


class TestLineParser:
    def test_parses_lines(self):
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

        line 7 doesn't continue _p
        line _8 in_cludes escapes (and also a bug).
        line 9 also has a comment # which gets rid of this backslash _
        and lastly line 10.
        """

        assert len(lineparser.parse_lines(test.split("\n"))) == 10



test_files = {
    'in1.txt': r"""# First test file
    Q[c] = Test[$c] + 2 * $c where c in 04 05 06
    """,

    'in2.txt': r"""# Test comment
    %sectors := 04 05 06
    Q[c] = Test[$c] + 2 * $c where c in %sectors
    """ ,

    'lists.mdl': r"""# Files containing the lists
    %sectors := 04 05 06""",

    'in3.mdl': r"""
    include lists

    Q[c] = Test[$c] + 2 * $c where c in %sectors
    """,

    'in4.txt': r"""
    include in3
    """,

    'in5.txt': r"""
    include lists

    s in %sectors

    Q[s] = Test[$s] + 2 * $s
    """,

    'test_series.mdl': r"""
    include lists

    s in %sectors

    Q[s] := Test[$s] + 2 * $s
    """,

    'in6.txt': r"""
    include test_series
    """,

    'in7.txt': r"""
    include lists

    s in %sectors

    Q[s] = Test[$s] + 2 * $s
    @over Q[s] = Test[$s] + 2 * $s
    """,

    'real.txt': r"""#---CO2 household emissions from housing use---

    include _lists

    %baseyear := 2006

    # equation 6b.1

    d(log(EMS_HH_BUIL[ce2, h, class])) = (@year > %baseyear) * d(log(ENER_BUIL[h, class, ce2])) + (@year =< %baseyear) * (log(1 + STEADYSTATE(2,1))) if EMS_HH_BUIL[ce2, h, class] <> 0 where ce2 in %list_com_E_CO2, h in %list_household, class in %list_ener_class"""}

class TestFileCompiler:
    def setup(self):
        for fname, test in test_files.iteritems():
            with open(fname, 'w') as f:
                f.write(test)

    def teardown(self):
        for fname in test_files:
            try:
                os.remove(fname)
                os.remove("dependency.graphml")
            except Exception as e:
                pass

    def test_compiles_simple_file(self):
        expected = ("Q_06 = Test_3 + 2 * 3\n"
                    "Q_05 = Test_2 + 2 * 2\n"
                    "Q_04 = Test_1 + 2 * 1")
        # The code to be compiled is passed in file in.txt
        model = compiler.MoDeLFile("in1.txt")
        # Compile and generate the output
        output = model.compile_program()
        assert output == expected

    def test_compiles_file_with_assignment(self):
        expected = ("Q_06 = Test_3 + 2 * 3\n"
                    "Q_05 = Test_2 + 2 * 2\n"
                    "Q_04 = Test_1 + 2 * 1")
        # The code to be compiled is passed in file in.txt
        model = compiler.MoDeLFile("in2.txt")
        # Compile and generate the output
        output = model.compile_program()
        assert output == expected

    def test_compiles_file_with_include(self):
        expected = ("Q_06 = Test_3 + 2 * 3\n"
                    "Q_05 = Test_2 + 2 * 2\n"
                    "Q_04 = Test_1 + 2 * 1")
        # The code to be compiled is passed in file in.txt
        model = compiler.MoDeLFile("in3.mdl")
        # Compile and generate the output
        output = model.compile_program()
        assert output == expected

    def test_compiles_file_with_recursive_includes(self):
        expected = ("Q_06 = Test_3 + 2 * 3\n"
                    "Q_05 = Test_2 + 2 * 2\n"
                    "Q_04 = Test_1 + 2 * 1")
        # The code to be compiled is passed in file in.txt
        model = compiler.MoDeLFile("in4.txt")
        # Compile and generate the output
        output = model.compile_program()
        assert output == expected

    def test_compiles_file_with_implicit_iterators(self):
        expected = ("Q_06 = Test_3 + 2 * 3\n"
                    "Q_05 = Test_2 + 2 * 2\n"
                    "Q_04 = Test_1 + 2 * 1")
        # The code to be compiled is passed in file in.txt
        model = compiler.MoDeLFile("in5.txt")
        # Compile and generate the output
        output = model.compile_program()
        assert output == expected

    def test_compiles_series_file(self):
        expected = ("series Q_06 = Test_3 + 2 * 3\n"
                    "series Q_05 = Test_2 + 2 * 2\n"
                    "series Q_04 = Test_1 + 2 * 1")
        # The code to be compiled is passed in file in.txt
        model = compiler.MoDeLFile("in6.txt")
        # Compile and generate the output
        output = model.compile_program()
        assert output == expected

    def test_compiles_override(self):
        expected = ("Q_06 = Test_3 + 2 * 3\n"
                    "Q_05 = Test_2 + 2 * 2\n"
                    "Q_04 = Test_1 + 2 * 1")
        # The code to be compiled is passed in file in.txt
        model = compiler.MoDeLFile("in7.txt")
        # Compile and generate the output
        output = model.compile_program()
        assert output == expected

    # def test_compiles_file_real_case(self):
    #     expected = ("d(log(EMS_HH_BUIL_21_H01_cC)) = ( @year > 2006 ) * d(log(ENER_BUIL_H01_cC_21)) + ( @year =< 2006 ) * ( log(1 + STEADYSTATE(2, 1)) )\n"
    #                 "d(log(EMS_HH_BUIL_21_H01_cD)) = ( @year > 2006 ) * d(log(ENER_BUIL_H01_cD_21)) + ( @year =< 2006 ) * ( log(1 + STEADYSTATE(2, 1)) )\n"
    #                 "d(log(EMS_HH_BUIL_21_H01_cE)) = ( @year > 2006 ) * d(log(ENER_BUIL_H01_cE_21)) + ( @year =< 2006 ) * ( log(1 + STEADYSTATE(2, 1)) )\n"
    #                 "d(log(EMS_HH_BUIL_21_H01_cF)) = ( @year > 2006 ) * d(log(ENER_BUIL_H01_cF_21)) + ( @year =< 2006 ) * ( log(1 + STEADYSTATE(2, 1)) )\n"
    #                 "d(log(EMS_HH_BUIL_21_H01_cG)) = ( @year > 2006 ) * d(log(ENER_BUIL_H01_cG_21)) + ( @year =< 2006 ) * ( log(1 + STEADYSTATE(2, 1)) )\n"
    #                 "d(log(EMS_HH_BUIL_22_H01_cA)) = ( @year > 2006 ) * d(log(ENER_BUIL_H01_cA_22)) + ( @year =< 2006 ) * ( log(1 + STEADYSTATE(2, 1)) )\n"
    #                 "d(log(EMS_HH_BUIL_22_H01_cB)) = ( @year > 2006 ) * d(log(ENER_BUIL_H01_cB_22)) + ( @year =< 2006 ) * ( log(1 + STEADYSTATE(2, 1)) )\n"
    #                 "d(log(EMS_HH_BUIL_22_H01_cC)) = ( @year > 2006 ) * d(log(ENER_BUIL_H01_cC_22)) + ( @year =< 2006 ) * ( log(1 + STEADYSTATE(2, 1)) )\n"
    #                 "d(log(EMS_HH_BUIL_22_H01_cE)) = ( @year > 2006 ) * d(log(ENER_BUIL_H01_cE_22)) + ( @year =< 2006 ) * ( log(1 + STEADYSTATE(2, 1)) )\n"
    #                 "d(log(EMS_HH_BUIL_22_H01_cD)) = ( @year > 2006 ) * d(log(ENER_BUIL_H01_cD_22)) + ( @year =< 2006 ) * ( log(1 + STEADYSTATE(2, 1)) )\n"
    #                 "d(log(EMS_HH_BUIL_22_H01_cG)) = ( @year > 2006 ) * d(log(ENER_BUIL_H01_cG_22)) + ( @year =< 2006 ) * ( log(1 + STEADYSTATE(2, 1)) )\n"
    #                 "d(log(EMS_HH_BUIL_22_H01_cF)) = ( @year > 2006 ) * d(log(ENER_BUIL_H01_cF_22)) + ( @year =< 2006 ) * ( log(1 + STEADYSTATE(2, 1)) )\n"
    #                 "d(log(EMS_HH_BUIL_24_H01_cC)) = ( @year > 2006 ) * d(log(ENER_BUIL_H01_cC_24)) + ( @year =< 2006 ) * ( log(1 + STEADYSTATE(2, 1)) )\n"
    #                 "d(log(EMS_HH_BUIL_24_H01_cB)) = ( @year > 2006 ) * d(log(ENER_BUIL_H01_cB_24)) + ( @year =< 2006 ) * ( log(1 + STEADYSTATE(2, 1)) )\n"
    #                 "d(log(EMS_HH_BUIL_24_H01_cF)) = ( @year > 2006 ) * d(log(ENER_BUIL_H01_cF_24)) + ( @year =< 2006 ) * ( log(1 + STEADYSTATE(2, 1)) )\n"
    #                 "d(log(EMS_HH_BUIL_24_H01_cE)) = ( @year > 2006 ) * d(log(ENER_BUIL_H01_cE_24)) + ( @year =< 2006 ) * ( log(1 + STEADYSTATE(2, 1)) )\n"
    #                 "d(log(EMS_HH_BUIL_24_H01_cD)) = ( @year > 2006 ) * d(log(ENER_BUIL_H01_cD_24)) + ( @year =< 2006 ) * ( log(1 + STEADYSTATE(2, 1)) )\n"
    #                 "d(log(EMS_HH_BUIL_24_H01_cG)) = ( @year > 2006 ) * d(log(ENER_BUIL_H01_cG_24)) + ( @year =< 2006 ) * ( log(1 + STEADYSTATE(2, 1)) )")
    #     # The code to be compiled is passed in file in.txt
    #     model = compiler.MoDeLFile("real.txt")
    #     # Compile and generate the output
    #     output = model.compile_program()
    #     assert output == expected