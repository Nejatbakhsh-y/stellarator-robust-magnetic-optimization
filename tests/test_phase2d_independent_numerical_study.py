"""Contract and arithmetic checks; no production acceptance inferred."""
import sys
from pathlib import Path
from decimal import Decimal

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import phase2d_independent_numerical_study as study
import phase2d_step50_reproduction as archive


def test_origin_writer_contract_differs_from_path_reader():
    raw = b'{"original":true}'
    members = {'windows-reference/inputs.json': raw,
               'input-sha256.json': ('{"windows-reference":"'+archive.digest(raw)+'"}').encode()}
    old = archive.seals(members)[0]['records'][0]
    assert old['status'] == 'MISSING'
    row = study.origin_contract(members, 'input-sha256.json')[0]
    assert row['writer_bytes_match']
    assert not row['interpreted_exists']
    assert row['association_scope'] == 'LOCAL_REPLAY_MEMBER_ONLY'


def test_wrong_origin_bytes_are_not_recovered_by_digest_search():
    members = {'linux-reference/inputs.json': b'good',
               'windows-reference/inputs.json': b'bad',
               'input-sha256.json': ('{"windows-reference":"'+archive.digest(b'good')+'"}').encode()}
    assert not study.origin_contract(members, 'input-sha256.json')[0]['writer_bytes_match']


def test_precision_repeats_complete_forward_calculation():
    # B=1, L=2, P=1.5; R=0.5, unit total weight.
    for digits in (60, 90):
        result = study.precise_metric([[1.0]], [2.0], [1.0], [-1.0], [-0.5], 0, digits)
        assert Decimal(result['ratio']) == Decimal('0.5')
        assert Decimal(result['numerator_T']) == Decimal('0.5')


def test_original_guard_retained():
    with pytest.raises(ValueError, match='denominator guard'):
        study.precise_metric([[1.0]], [2.0], [1.0], [0.0], [0.0], 0, 90)


def test_case_sensitive_json_and_duplicate_rejection():
    assert archive.decode(b'{"D":1,"d":2}') == {'D':1, 'd':2}
    with pytest.raises(ValueError, match='Duplicate'):
        archive.decode(b'{"D":1,"D":2}')
