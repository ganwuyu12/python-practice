from client import calc_cost

def test_calc_cost_zero():
    assert calc_cost(0, 0) == 0

def test_calc_cost_positive():
    expected = 5 * 0.02/1e6 + 11 * 4/1e6
    assert calc_cost(5, 11) == expected