"""Run mypy programmatically on selected files and print results.

This helper avoids shell quoting/PowerShell differences and duplicate-module
errors by passing explicit file paths to the mypy API.
"""
from mypy import api
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

files = [
    ROOT / 'main.py',
    ROOT / 'services' / 'data_fetcher.py',
    ROOT / 'services' / 'image_fetcher.py',
    ROOT / 'services' / 'map_renderer.py',
    ROOT / 'ui' / 'main_window.py',
    ROOT / 'utils' / 'geo_utils.py',
]

exit_code = 0
for p in files:
    print(f"Running mypy on {p}")
    args = ['--ignore-missing-imports', '--check-untyped-defs', str(p)]
    result = api.run(args)
    stdout, stderr, code = result
    if stdout:
        print('STDOUT:\n', stdout)
    if stderr:
        print('STDERR:\n', stderr)
    if code != 0:
        exit_code = code

print('\nOverall exit code:', exit_code)
if exit_code != 0:
    raise SystemExit(exit_code)
