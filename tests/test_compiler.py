from .. import compiler

class TestCompiler(object):
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

    def test_parses_Identifier(self):
        res = compiler.identifier.parseString("test{X}_energy{O}")[0]
        assert isinstance(res, compiler.Identifier)
        assert len(res.value) == 4
        assert isinstance(res.value[0], compiler.VariableName) and isinstance(res.value[2], compiler.VariableName)
        assert isinstance(res.value[1], compiler.Placeholder) and isinstance(res.value[3], compiler.Placeholder)
        assert res.value[0].value == "test" and res.value[2].value == "_energy"
        assert res.value[1].value == compiler.VariableName("X") and res.value[3].value == compiler.VariableName("O")

    def test_parses_simple_variable_name_as_identifier(self):
        res = compiler.identifier.parseString("testVar")[0]
        assert isinstance(res, compiler.Identifier)
        assert len(res.value) == 1 and isinstance(res.value[0], compiler.VariableName)

    def test_parses_Index(self):
        res = compiler.index.parseString("[com, sec]")[0]
        assert isinstance(res, compiler.Index)
        assert len(res.value) == 2
        assert res.value[0] == compiler.VariableName("com") and res.value[1] == compiler.VariableName("sec")
