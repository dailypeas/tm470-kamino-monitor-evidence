# Emergency minimum viable technical design

Design date: 13 July 2026  
Status: current recovery work; not historical TMA02 work  
Project: *Design and Evaluation of a Risk-Based Blockchain Transaction Monitoring Approach for Kamino-Related Activity on Solana*

## 1. Decision summary

The minimum viable product (MVP) is a Python command-line prototype that loads reproducible JSON fixtures and, optionally, retrieves public Solana data through a Helius RPC URL. It normalises a small transaction history, identifies direct invocation of the Kamino Lending mainnet programme, evaluates two mandatory indicators, and emits explainable JSON and CSV results.

The design deliberately excludes a graphical interface, live streaming, machine learning, wallet attribution, graph clustering, production alerting and exhaustive Kamino product coverage. A third value-deviation indicator is permitted only if the two-indicator pipeline, tests and evaluation are already complete.

## 2. Problem being solved

Solana transactions can contain multiple instructions and accounts. Public availability therefore does not by itself provide a prioritised or explainable view of activity requiring manual review. The prototype tests a narrower question: can a small, transparent ruleset use reproducible Solana transaction fields to prioritise direct Kamino Lending activity for manual technical review?

It does not detect fraud, prove malicious intent, identify people or intervene in transactions. Its output is a project-specific review priority with reasons and limitations.

## 3. Authoritative technical basis

The Kamino Finance `klend` repository describes Kamino Lending as a Solana programme and records the mainnet programme ID as `KLend2g3cP87fffoy8q1mQqGKjrxjC8boSyAYavgmjD` ([Kamino Finance, 2026](https://github.com/Kamino-Finance/klend), accessed 13 July 2026). The MVP uses only this identifier initially. Other Kamino programmes must not be silently treated as covered.

Solana's official RPC documentation distinguishes raw and `jsonParsed` transaction structures. It explains that compiled instructions identify a programme by an index into the transaction account keys, while parsed instructions can expose programme identifiers directly; versioned transactions may also use loaded addresses ([Solana, 2026](https://solana.com/docs/rpc/json-structures), accessed 13 July 2026). The normaliser must therefore handle explicit programme IDs and indexed programme IDs only where the corresponding complete account-key list is available.

Helius currently exposes standard Solana RPC methods and a paginated `getTransactionsForAddress` method ([Helius, 2026a](https://www.helius.dev/docs/agents/typescript-sdk/api-reference), accessed 13 July 2026). Helius also states that its older Enhanced Transactions API continues to operate but is deprecated for new integrations, recommending `getTransactionsForAddress` for history and `getTransaction` for a single transaction ([Helius, 2026b](https://www.helius.dev/docs/enhanced-transactions/overview), accessed 13 July 2026). Accordingly, fixture-based analysis is mandatory and live retrieval is an adapter rather than the core algorithm. The design does not depend on the older `/v0` response descriptions shown in TMA02.

## 4. Lifecycle decision

The recovered TMA01 selected an iterative lifecycle with early throwaway prototypes. That remains appropriate because input formats, direct Kamino identification and indicator usefulness are uncertain. Strict waterfall would freeze assumptions before the data path is tested, while a research-only approach would not satisfy the practical LO11 requirement.

The emergency cycle is:

1. freeze the canonical transaction contract and two indicators;
2. make fixture loading and normalisation pass tests;
3. add direct Kamino programme matching;
4. generate explainable outputs;
5. test boundary, missing and malformed cases;
6. compare provisional thresholds and priority schemes;
7. stop rather than add breadth.

## 5. System boundary

### 5.1 In scope

- one wallet-history analysis or one transaction-signature analysis per command;
- JSON fixture input as the reproducible default;
- optional Helius-backed retrieval when environment variables are present;
- direct Kamino Lending programme invocation only;
- timestamp, success/failure, signature, programme IDs and wallet context;
- two time-window indicators;
- structured output and human-readable explanations;
- explicit `unknown`/`not_evaluated` states where data is inadequate.

### 5.2 Out of scope

- inferred indirect Kamino relationships where the programme is not invoked;
- decoding all Kamino instructions or reconstructing obligations/reserves;
- calculating profit, loss, deposits, withdrawals or economic intent;
- destination novelty, clustered outflows and graph analysis;
- accusations, automated enforcement or claims of detection accuracy;
- continuous monitoring, webhooks, streaming or a user interface.

## 6. Inputs

The CLI should support these mutually exclusive modes:

```text
kamino-monitor analyse-fixture --input <json> --output-dir <dir>
kamino-monitor analyse-wallet --wallet <base58-address> --output-dir <dir>
kamino-monitor analyse-transaction --signature <base58-signature> --output-dir <dir>
```

Fixture mode must work without network access or credentials. Live modes read `HELIUS_RPC_URL` and, if the configured URL construction requires it, `HELIUS_API_KEY`. Missing live credentials produce a clear non-zero error without printing secrets.

Input validation checks that:

- the JSON top level has a recognised fixture version and a transaction list;
- signatures and addresses are non-empty strings with conservative Base58-shaped validation;
- timestamps are integer Unix seconds;
- success/error state is present or explicitly unknown;
- programme IDs are a list of strings after normalisation;
- no indicator treats a missing field as a negative observation.

## 7. Canonical transaction structure

Provider-specific input is converted to a small internal record:

```json
{
  "signature": "string",
  "timestamp": 0,
  "status": "success | failed | unknown",
  "error": "object-or-string-or-null",
  "fee_payer": "string-or-null",
  "account_keys": ["string"],
  "invoked_program_ids": ["string"],
  "token_transfers": [
    {
      "mint": "string-or-null",
      "from": "string-or-null",
      "to": "string-or-null",
      "amount": "decimal-string-or-null"
    }
  ],
  "source_type": "fixture | solana_rpc | helius",
  "source_case_id": "string-or-null"
}
```

Decimal strings are retained at the boundary to avoid binary floating-point alteration. Token transfers are optional because the two mandatory indicators do not depend on their interpretation.

## 8. Kamino relevance

The initial allowlist contains only:

```text
KLend2g3cP87fffoy8q1mQqGKjrxjC8boSyAYavgmjD  # Kamino Lending mainnet
```

Classification is:

- `direct`: at least one invoked programme ID exactly matches the allowlist;
- `not_direct`: invoked programme IDs were extracted successfully and none match;
- `unknown`: programme IDs could not be extracted reliably.

Only `direct` records enter indicator counts. Merely appearing as an unrelated account key is insufficient unless an instruction actually identifies that key as its programme. This reduces false Kamino classifications but creates false negatives for indirect/cross-program behaviour; that limitation is explicit.

## 9. Mandatory indicators

The defaults below are provisional project assumptions for feasibility testing, not academically validated fraud thresholds.

### 9.1 I1: rapid relevant activity

Definition: for each direct Kamino transaction, count direct Kamino transactions for the analysed wallet whose timestamps fall in the inclusive interval `[current_timestamp - window_seconds, current_timestamp]`.

Provisional default: trigger when the count is at least 3 within 600 seconds.

Required fields: timestamp, direct Kamino relevance and shared analysed-wallet context.

Missing-data behaviour: `not_evaluated` if the current timestamp is missing or fewer than three timestamped relevant records are available in the supplied analysis history.

Explanation example: `3 directly Kamino-related transactions were observed in the preceding 10 minutes (provisional threshold: 3).`

Likely false positives include active position management, automation and congestion recovery. Likely false negatives include activity spread just outside the window or incomplete history.

### 9.2 I2: repeated failed relevant transactions

Definition: for each direct Kamino transaction, count failed direct Kamino transactions in the same inclusive rolling interval.

Provisional default: trigger when at least 2 failed relevant transactions occur within 600 seconds.

Required fields: timestamp, direct Kamino relevance and reliable failed/success state.

Missing-data behaviour: `not_evaluated` if status or timestamp is unknown. Unknown status is never converted to success.

Explanation example: `2 failed directly Kamino-related transactions were observed in the preceding 10 minutes (provisional threshold: 2).`

Likely false positives include slippage, stale blockhashes, insufficient balance, user mistakes or transient network conditions. Likely false negatives include failures outside the selected window or provider history omissions.

## 10. Priority output

The initial output preserves each indicator independently. A provisional priority mapping avoids the rejected one-point-per-rule assumption:

| I1 rapid | I2 repeated failures | Priority | Reasoning |
|---|---|---|---|
| false | false | no elevated indicator observed | Neither selected rule triggered within available data |
| true | false | low | Timing alone is contextual and commonly benign |
| false | true | moderate | Repeated observed failures warrant review but have many benign causes |
| true | true | elevated | Two different observable conditions coincide; manual technical review is prioritised |

This is an ordinal triage rule, not a probability or finding of maliciousness. Evaluation must also calculate an equal-weight comparator solely to show whether categorisation changes; it must not report accuracy without ground truth.

## 11. Outputs

Each run creates:

- `analysis.json`: run metadata, configuration, normalised records, per-indicator status, reasons, priority and warnings;
- `analysis.csv`: one row per assessed transaction with flattened indicator and priority fields;
- a concise terminal summary containing no credentials.

Run metadata includes actual UTC execution time, fixture/source identifier, application version or Git commit where available, threshold configuration and warnings. Generated output must never be represented as historical evidence predating the run.

## 12. Failure handling

| Failure | Behaviour |
|---|---|
| Missing/malformed fixture | Reject with file and validation reason; write no misleading partial result |
| Missing live credentials | Clear error naming the missing variable, never its value |
| HTTP timeout/rate limit/server error | Bounded timeout, no infinite retry, non-zero exit and reproducible fixture fallback guidance |
| Unknown provider shape | Reject or preserve as an explicit normalisation error |
| Missing programme IDs | Kamino relevance `unknown`; exclude from indicator counts |
| Missing timestamp/status | Affected indicator `not_evaluated`; include warning |
| Empty history | Valid output with no assessed transactions and an insufficiency warning |

## 13. Test and evaluation design

Minimum cases are:

1. routine direct Kamino history triggering neither rule;
2. rapid successful direct activity triggering I1 only;
3. repeated failed direct activity triggering I2 and possibly I1;
4. non-Kamino activity proving it is excluded;
5. missing timestamp/status producing `not_evaluated`;
6. malformed JSON producing a controlled error;
7. boundary timestamps exactly on and just outside the window.

Synthetic cases must be labelled `synthetic test case`; public fixtures, if added, must include signature, retrieval date and unknown-ground-truth status. Evaluation compares at least:

- rapid counts of 3 and 4 with windows of 5, 10 and 15 minutes;
- failure counts of 2 and 3 with windows of 5, 10 and 15 minutes;
- ordinal mapping versus an equal-weight comparator;
- repeatability of fixture results;
- explanation completeness and missing-data behaviour.

Without defensible labels, precision, recall, accuracy, false-positive rate and false-negative rate must not be calculated. Instead, the evaluation analyses plausible false-positive/negative mechanisms case by case.

## 14. Explainability and ethical safeguards

Every triggered and non-evaluated rule records the observed values, configured threshold, time window and plain-language reason. Outputs use `directly Kamino-related`, `indicator triggered`, `review priority` and `requires manual technical review`. They do not use `malicious`, `criminal`, `attacker` or `fraudulent` unless an external authoritative incident source independently supports a separate contextual statement.

Wallets and signatures are pseudonymous public data. Fixtures should be minimised, the repository kept private during assessment, and no attempt made to link addresses to people. Synthetic examples must be visibly synthetic. The system never makes decisions about individuals and never submits a transaction.

## 15. Decision gates

- **Gate A:** If direct programme IDs cannot be extracted reliably, stop live integration and complete fixture-only evaluation with the limitation documented.
- **Gate B:** If two indicators are not fully tested, do not implement the optional value indicator.
- **Gate C:** If time threatens report assembly, stop development and preserve commands, outputs and limitations.
- **Gate D:** No threshold is described as validated unless later evidence genuinely supports that statement.

## 16. Optional third indicator

Only after Gates A–C are satisfied, a same-mint token-transfer value deviation may compare the current amount with a recent median. It requires a documented direction, consistent mint/decimals and a minimum comparable history. If any condition fails, it returns `not_evaluated`. Destination novelty and clustered outflows remain out of scope.
