"""Independent diagnostic guards, including active constrained optima."""
from pathlib import Path
import sys
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import phase2d_step33 as d


def test_decimal_kkt_constrained_signs_and_feasibility():
    M = np.eye(2); y = np.array([2., -2.])
    assert d.decimal_kkt(M, y, np.array([1., -1.]))['status'] == 'PASS'
    assert d.decimal_kkt(M, y, np.array([.9, -.9]))['status'] == 'FAIL'
    assert d.decimal_kkt(M, y, np.array([2., -2.]))['status'] == 'FAIL'


def test_decimal_kkt_coupled_interior():
    M = np.array([[1., 2.], [3., -1.], [0., 1.]])
    x = np.array([.25, -.5]); y = M@x
    assert d.Decimal(d.decimal_kkt(M, y, x)['kkt_max']) == 0
    assert d.decimal_kkt(M, y, x+1e-4)['status'] == 'FAIL'


def test_relabelled_windows_cannot_supply_linux_cell():
    env = dict(platform='Windows-10', python='3.11.9', numpy='2.4.6', scipy='1.17.1')
    d.cohort_environment('windows-reference', env)
    with pytest.raises(ValueError): d.cohort_environment('linux-reference', env)
    env['platform'] = 'Linux-6'
    d.cohort_environment('linux-reference', env)
    with pytest.raises(ValueError): d.cohort_environment('linux-numpy-sensitivity', env)


def test_nonfinite_kkt_rejected():
    with pytest.raises(ValueError): d.decimal_kkt(np.eye(1), np.array([np.nan]), np.zeros(1))
