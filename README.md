# Kamino-related Solana monitoring prototype

This repository contains academic project evidence and a small Python command-line prototype created during the 13 July 2026 recovery phase. It prioritises directly Kamino Lending-related activity using two explainable, provisional time-window rules.

It does not detect fraud, identify malicious wallets or provide production monitoring. Current evaluation uses clearly labelled synthetic fixtures without ground truth.

See [the technical design](docs/technical-design.md), [reproduction guide](docs/reproduction-guide.md), [dataset record](data/DATASET.md) and [evaluation analysis](docs/evaluation-analysis.md).

Quick verification:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m kamino_monitor analyse-fixture --input data/raw/fixtures/synthetic-triggering.json --output-dir outputs/synthetic-triggering
```

Credentials are optional and used only for unverified live mode. Put real values in an untracked `.env`; never add them to source, documentation or output.
