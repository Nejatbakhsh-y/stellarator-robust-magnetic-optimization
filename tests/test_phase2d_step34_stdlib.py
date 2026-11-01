"""Portable checks for the independent forensic arithmetic (no scientific stack)."""
import importlib.util
import ast
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('step34', Path(__file__).resolve().parents[1]/'scripts/phase2d_step34_independent.py')
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)


class IndependentArithmetic(unittest.TestCase):
    def test_malformed_payloads_rejected(self):
        for payload in ({'shape': [True], 'binary64_le': '00'*8},
                        {'shape': [-1], 'binary64_le': ''},
                        {'shape': [1], 'binary64_le': '00 '*8},
                        {'shape': [1], 'binary64_le': '00'*4}):
            with self.assertRaises(ValueError):
                s.unpack(payload)

    def test_dot_rejects_truncated_vector(self):
        with self.assertRaises(ValueError):
            s.dot([s.D(1)], [])

    def test_scientific_rows_cannot_be_silently_truncated(self):
        with self.assertRaises(ValueError):
            s.kkt([[1.], [2.]], [0.], [0.])
        with self.assertRaises(ValueError):
            s.ratio(dict(fine_A=[[1.]], fine_b=[3.], fine_weights=[]), [-1.], [0.], 0, 90)

    def test_singular_field_reference_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Singular'):
            s.field([[0., 0., 0.]], [[0., 0., 0.], [1., 0., 0.]], 1.)

    def test_missing_evidence_cannot_create_empty_analysis(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(ValueError, 'Missing historical'):
                s.analyze(root/'missing', root/'output')
            self.assertFalse((root/'output').exists())

    def test_actual_gate_function_rejects_failed_and_incomplete_verdicts(self):
        # Execute the actual dependency-free gate body with controlled validator
        # verdicts; this supplements, not replaces, real producer regressions.
        path = Path(__file__).resolve().parents[1]/'src/stellarator_robust/upstream_attribution.py'
        tree = ast.parse(path.read_text())
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'require_solve')
        namespace = {'numeric': lambda *args: None}
        exec(compile(ast.Module(body=[function], type_ignores=[]), str(path), 'exec'), namespace)
        for gates, incomplete in (({}, False), (dict(dense=False, row3=True, row4=True), False),
                                  (dict(dense=True, row3=True, row4=True), True)):
            namespace['validate_solve'] = lambda *args: (gates, incomplete)
            with self.assertRaises(ValueError):
                namespace['require_solve']({}, {}, {})

    def test_closed_form_singular_values(self):
        values = s.singular_values([[3., 0.], [0., 2.], [0., 0.]])
        self.assertEqual(values, [3., 2.])

    def test_coupled_singular_values(self):
        values = s.singular_values([[2., 1.], [1., 2.]])
        for actual, expected in zip(values, [3., 1.]):
            self.assertAlmostEqual(actual, expected, places=14)

    def test_active_bound_kkt_signs(self):
        self.assertEqual(s.kkt([[1.]], [2.], [1.])['kkt_max'], '0')
        self.assertEqual(s.kkt([[1.]], [0.], [1.])['kkt_max'], '1')

    def test_ratio_exact_and_denominator_guard(self):
        arrays = dict(fine_A=[[1.]], fine_b=[3.], fine_weights=[1.])
        # B=2, L=3, P=2.5, hence R=.5 exactly.
        r = s.ratio(arrays, [-1.], [-.5], 0, 90)
        self.assertEqual(s.D(r['ratio']), s.D('.5'))
        self.assertIsNone(s.ratio(arrays, [0.], [0.], 0, 90)['ratio'])

    def test_polygon_field_orientation_and_scaling(self):
        vertices = [[-1., -1., 0.], [1., -1., 0.], [1., 1., 0.], [-1., 1., 0.]]
        a = s.field([[0., 0., 0.]], vertices, 1.)[0]
        b = s.field([[0., 0., 0.]], vertices[::-1], 2.)[0]
        self.assertEqual(s.D(a[0]), 0)
        self.assertEqual(s.D(a[1]), 0)
        self.assertGreater(s.D(a[2]), 0)
        self.assertAlmostEqual(float(b[2]), -2*float(a[2]), places=20)


if __name__ == '__main__':
    unittest.main()
