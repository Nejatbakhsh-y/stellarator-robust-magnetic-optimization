"""python -m stellarator_robust.cli {run,validate}."""
import argparse
import json
from .experiments import run
from .validation import convergence


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['run', 'validate'])
    parser.add_argument('--config', default='configs/quick.json')
    parser.add_argument('--output', default='results/quick')
    args = parser.parse_args()
    if args.command == 'validate':
        print(json.dumps(convergence(), indent=2))
    else:
        result = run(args.config, args.output)
        print(json.dumps({'summary': result['summary'], 'metadata': result['metadata']}, indent=2))


if __name__ == '__main__':
    main()
