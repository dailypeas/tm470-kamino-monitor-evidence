# Limited evaluation analysis

Evaluation date: 13 July 2026.

Ten automated tests passed. The saved routine fixture produced three `no_elevated_indicator_observed` records under the default configuration. The triggering fixture produced one elevated record, one moderate record and two records with no elevated indicator; one of the latter is deliberately non-Kamino and is not evaluated by the rules.

Across all 36 configurations for the routine case, no indicator priority was produced. Across the 36 triggering-case configurations:

- 4 configurations produced at least one elevated record;
- 18 produced at least one moderate record;
- 8 produced at least one low record;
- 12 produced no triggered priority.

The elevated result occurred only when rapid count was 3, failure count was 2, the rapid window was at least 600 seconds and the failure window was at least 600 seconds. This is expected from the constructed four-minute spacing, but it demonstrates that the headline priority changes materially with provisional thresholds.

The results support a limited claim of technical correctness against designed fixtures: the programme excludes a non-Kamino record, respects inclusive boundaries, does not convert missing status into success, produces reasons and writes repeatable structured output. They do not show that the rules identify harmful activity, are useful on routine public Kamino data or have acceptable operational false-positive/negative rates.

Likely false positives include legitimate automated position management and repeated failures caused by slippage, stale blockhashes, balances or network conditions. Likely false negatives include incomplete histories, indirect Kamino calls, activity outside a selected window and use of other Kamino programmes. Manual review remains required.

