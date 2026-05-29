"""cad_data 单元测试"""
import sys; sys.path.insert(0, "E:/CAD自动化制图/src")
from cad_data import PowerhouseData, Layer, HatchPattern

def test_powerhouse_data():
    d = PowerhouseData()
    errs = d.validate()
    assert len(errs) == 0, f"验证失败: {errs}"
    assert d.total_length == 94000
    assert d.span == 17000
    print(f"[OK] PowerhouseData 验证通过 ({len(errs)} 错误)")

def test_layer_enum():
    assert len(list(Layer)) >= 15
    assert Layer.CONCRETE.value == "S-CONC-混凝土"
    print(f"[OK] Layer 枚举 ({len(list(Layer))} 个)")

def test_hatch_pattern():
    assert HatchPattern.CONCRETE.value == "ANSI31"
    print(f"[OK] HatchPattern 枚举 ({len(list(HatchPattern))} 个)")

def test_invalid_data():
    d = PowerhouseData(total_length=0)
    errs = d.validate()
    assert len(errs) > 0
    print(f"[OK] 数据校验有效 ({len(errs)} 个错误被检出)")

if __name__ == "__main__":
    test_powerhouse_data()
    test_layer_enum()
    test_hatch_pattern()
    test_invalid_data()
    print("\n所有测试通过！")
