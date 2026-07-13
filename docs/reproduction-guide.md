# Reproduction guide

## Environment

- Python 3.10 or later
- no third-party runtime dependencies
- network access and Helius credentials are not required for fixture tests

## Safe configuration

Copy `.env.example` to `.env` manually only for live retrieval. Never commit `.env`. `HELIUS_RPC_URL` is required in live mode; the URL may contain a `{HELIUS_API_KEY}` placeholder which is replaced from the environment. Fixture mode ignores both values.

## Commands

From the repository root:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m kamino_monitor analyse-fixture --input data/raw/fixtures/synthetic-routine.json --output-dir outputs/synthetic-routine
PYTHONPATH=src python3 -m kamino_monitor analyse-fixture --input data/raw/fixtures/synthetic-triggering.json --output-dir outputs/synthetic-triggering
python3 scripts/run_sensitivity.py
```

Expected test result: 10 tests pass. Fixture commands create `analysis.json` and `analysis.csv`. The sensitivity command writes 72 data rows to `outputs/evaluation-results.csv`.

Optional live commands are:

```bash
PYTHONPATH=src python3 -m kamino_monitor analyse-transaction --signature SIGNATURE --output-dir outputs/live-transaction
PYTHONPATH=src python3 -m kamino_monitor analyse-wallet --wallet ADDRESS --output-dir outputs/live-wallet
```

Live retrieval has not yet been verified in the current evidence set. It must not be described as tested until a genuine run is recorded. Provider errors return a controlled non-zero exit.

## Known limitations

Only direct invocation of one Kamino Lending programme is recognised. Defaults are provisional assumptions. Synthetic fixtures demonstrate correctness against designed cases, not usefulness on real activity or fraud-detection accuracy.

