# Limited emergency evaluation method

Created: 13 July 2026.

The evaluation addresses technical correctness, repeatability, explanation behaviour, missing/malformed input and threshold sensitivity. It does not measure detection accuracy because the dataset has no defensible malicious/benign ground truth.

Automated tests cover inclusive and exclusive time-window boundaries, both-rule activation, non-Kamino exclusion, unknown status, missing timestamp, malformed fixture version, raw RPC programme-index resolution, invalid thresholds, CLI output and malformed JSON.

Sensitivity evaluation crosses:

- rapid count 3 or 4;
- rapid window 300, 600 or 900 seconds;
- failure count 2 or 3;
- failure window 300, 600 or 900 seconds;
- both synthetic cases.

This produces 72 case/configuration combinations. Outputs are compared by counts in each ordinal priority. Equal-versus-weighted scoring is not claimed as validated: with only two Boolean rules, the current ordinal table is equivalent to provisional weights of one for rapid activity and two for repeated failures. The individual rule results remain the primary explanation.

