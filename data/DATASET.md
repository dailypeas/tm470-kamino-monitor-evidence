# Dataset record

Created: 13 July 2026 during the recovery phase.

The current dataset contains two explicitly synthetic JSON fixtures. Neither represents an observed wallet, genuine transaction, known incident or malicious ground truth.

| Case | File | Label | Purpose |
|---|---|---|---|
| SYN-ROUTINE-001 | `raw/fixtures/synthetic-routine.json` | Synthetic test case | Three successful direct-Kamino records spaced one hour apart; intended to exercise non-triggering behaviour |
| SYN-TRIGGER-001 | `raw/fixtures/synthetic-triggering.json` | Synthetic test case | Three direct-Kamino records four minutes apart, including two failures, plus one unrelated record; intended to exercise both rules and exclusion |

The timestamps, signatures, wallet strings, errors and transaction combinations are constructed test data. The only real technical identifier embedded in the cases is the public Kamino Lending mainnet programme ID, taken from the official Kamino Finance `klend` repository.

The fixtures test program logic, not operational accuracy. They cannot support precision, recall, accuracy, false-positive-rate or false-negative-rate claims. Public observed fixtures may be added later only with retrieval date, provenance, unknown-ground-truth labelling and cautious interpretation.

