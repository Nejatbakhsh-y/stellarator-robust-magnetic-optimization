"""Replay the preserved Linux failure data; this is not a new Linux run."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile
from stellarator_robust.ci_evidence import compare_study


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--artifact', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path('results/ci/clearance-repair/replay.json'))
    args = parser.parse_args()
    digest = hashlib.sha256(args.artifact.read_bytes()).hexdigest()
    # Published by GitHub's artifact API for run 40977794679, artifact 12944135712.
    assert digest == 'befcc90ca3bc461e22b08e379bf1660bab93efe568dd18d8d6fae2fe272c6d14'
    reference_bytes = Path('results/phase2/study.json').read_bytes()
    assert hashlib.sha256(reference_bytes).hexdigest() == '395027e9fdda163448789beda6b1c7eb7d1537d6024d0a0ee32790ddf53bb258'
    with zipfile.ZipFile(args.artifact) as archive:
        load = lambda name: json.loads(archive.read(name))
        execution = load('ci/phase2-cloud/full/execution.json')
        failure = load('ci/phase2-cloud/full/checkpoint-comparison.json')
        current_bytes = archive.read('reproduction/cloud-work/results/phase2/study.json')
        assert current_bytes == archive.read('ci/phase2-cloud/full/phase2/study.json')
    reference = json.loads(reference_bytes)
    current = json.loads(current_bytes)
    path = '/scenarios/holdout/1/sampled_clearance_m'
    assert failure['status'] == execution['status'] == 'FAIL'
    assert any(r['path'] == path and r['absolute_error'] == 5.551115123125783e-17
               for r in failure['numeric_differences'])
    assert reference['scenarios']['holdout'][1]['sampled_clearance_m'] == 0.38888759185268096
    assert current['scenarios']['holdout'][1]['sampled_clearance_m'] == 0.3888875918526809
    # These metadata values passed runtime validation in the original Linux
    # comparison before it rejected clearance. Cross-check its execution record;
    # do not substitute this Windows replay process's Git/Python provenance.
    actual = {key: next(r['current'] for r in failure['excluded'] if r['path'] == '/'+key)
              for key in ('source_commit', 'source_dirty', 'python')}
    assert actual['source_commit'] == execution['commit']
    assert actual['python'] == execution['python']
    assert type(actual['source_dirty']) is bool and actual['source_dirty']
    record = dict(kind='offline_replay_of_preserved_linux_artifact', new_linux_run=False,
                  original_run_id=40977794679, artifact_id=12944135712,
                  artifact_sha256=digest,
                  reference_study_sha256=hashlib.sha256(reference_bytes).hexdigest(),
                  linux_study_sha256=hashlib.sha256(current_bytes).hexdigest(),
                  archived_runtime=actual, status='FAIL', comparison={})
    try:
        compare_study(reference, current, actual=actual, report=record['comparison'])
        record['status'] = 'PASS'
    except Exception as exc:
        record['error'] = str(exc)
        raise
    finally:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(record, indent=2)+'\n')
    print('Archived Linux full-study comparison:', record['status'])
    print('Recorded numerical differences:', len(record['comparison']['numeric_differences']))
    print('No new Linux execution is claimed.')


if __name__ == '__main__':
    main()
