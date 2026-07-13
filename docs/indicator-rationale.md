# Indicator rationale

The MVP uses two rules because both can be calculated from signature history, timestamps, transaction status and direct programme invocation. Thresholds are provisional project assumptions tested for sensitivity, not published fraud thresholds.

## Rapid relevant activity

Definition: count directly Kamino-Lending-related transactions in the inclusive rolling interval ending at the current transaction. Default: at least three within 600 seconds. Required fields are timestamp, direct relevance and a shared analysed-wallet history. Missing timestamps or insufficient history return `not_evaluated`.

Temporal features are consistent with security-event correlation and blockchain anomaly literature (Scarfone and Mell, 2007; Hassan, Rehmani and Chen, 2023). Neither source supplies a Kamino threshold. The default was chosen as a testable project assumption: it is small enough for compact fixtures and distinguishes the constructed four-minute sequence from hourly routine records. Sensitivity tests use counts three/four and windows five/ten/fifteen minutes.

Weight/severity: low when triggered alone because fast legitimate automation or position management is plausible. False negatives include incomplete history and activity outside the window.

## Repeated failed relevant transactions

Definition: count failed directly relevant transactions in the same rolling interval. Default: at least two within 600 seconds. Unknown status produces `not_evaluated` rather than being treated as success.

Zheng et al. (2025) support treating failure status, programmes and temporal patterns as analysable Solana features, while also demonstrating varied failure causes. The rule therefore supports review but not accusations. The default is provisional and sensitivity-tested at two/three failures and five/ten/fifteen minutes.

Weight/severity: moderate when triggered alone. Benign causes include slippage, stale blockhashes, balance/resource conditions and user error. Incomplete provider history creates false negatives.

## Priority logic

Neither rule triggered: no elevated indicator observed within scope. Rapid only: low. Failures only: moderate. Both: elevated manual-review priority. This ordinal mapping avoids pretending that equal points measure risk probability. An equal-weight comparator can be discussed, but with two Boolean rules the individual explanations are more informative than the total.

## Deferred indicators

Destination novelty and clustered outflows were removed because programme and token accounts make destination/direction semantics ambiguous. Value deviation was retained only as future work because token comparability and economic direction require more parsing. This scope reduction protects technical correctness.

