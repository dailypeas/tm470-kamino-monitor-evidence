import unittest

from kamino_monitor.core import (
    InputError,
    KAMINO_LENDING_MAINNET,
    Thresholds,
    analyse,
    load_fixture_document,
    normalise_canonical_transaction,
    normalise_rpc_transaction,
)


def transaction(signature, timestamp, status="success", programs=None):
    return normalise_canonical_transaction(
        {
            "signature": signature,
            "timestamp": timestamp,
            "status": status,
            "invoked_program_ids": [KAMINO_LENDING_MAINNET] if programs is None else programs,
            "token_transfers": [],
        }
    )


class CoreTests(unittest.TestCase):
    def test_both_indicators_trigger_at_inclusive_boundary(self):
        records = [
            transaction("a", 1000, "failed"),
            transaction("b", 1300, "failed"),
            transaction("c", 1600, "success"),
        ]
        result = analyse(records, Thresholds())[-1]
        self.assertTrue(result["indicators"]["rapid_relevant_activity"]["triggered"])
        self.assertTrue(result["indicators"]["repeated_failed_relevant_transactions"]["triggered"])
        self.assertEqual(result["priority"], "elevated")

    def test_record_just_outside_window_is_excluded(self):
        records = [
            transaction("a", 999, "failed"),
            transaction("b", 1300, "failed"),
            transaction("c", 1600, "success"),
        ]
        result = analyse(records, Thresholds())[-1]
        self.assertFalse(result["indicators"]["rapid_relevant_activity"]["triggered"])
        self.assertFalse(result["indicators"]["repeated_failed_relevant_transactions"]["triggered"])

    def test_non_kamino_transaction_is_not_evaluated(self):
        item = transaction("not-kamino", 1000, programs=["11111111111111111111111111111111"])
        result = analyse([item], Thresholds())[0]
        self.assertEqual(result["kamino_relevance"], "not_direct")
        self.assertEqual(result["indicators"]["rapid_relevant_activity"]["status"], "not_evaluated")

    def test_unknown_status_does_not_become_success(self):
        records = [
            transaction("a", 1000, "success"),
            transaction("b", 1100, "unknown"),
            transaction("c", 1200, "success"),
        ]
        result = analyse(records, Thresholds())[-1]
        self.assertEqual(
            result["indicators"]["repeated_failed_relevant_transactions"]["status"],
            "not_evaluated",
        )

    def test_missing_timestamp_is_not_evaluated(self):
        item = transaction("missing-time", None)
        result = analyse([item], Thresholds())[0]
        self.assertEqual(result["indicators"]["rapid_relevant_activity"]["status"], "not_evaluated")

    def test_invalid_fixture_is_rejected(self):
        with self.assertRaises(InputError):
            load_fixture_document({"fixture_version": "0", "case_id": "bad", "transactions": []})

    def test_rpc_program_index_is_resolved(self):
        raw = {
            "blockTime": 1000,
            "transaction": {
                "message": {
                    "accountKeys": [
                        {"pubkey": "payer"},
                        {"pubkey": KAMINO_LENDING_MAINNET},
                    ],
                    "instructions": [{"programIdIndex": 1}],
                }
            },
            "meta": {"err": None, "innerInstructions": []},
        }
        result = normalise_rpc_transaction(raw, "rpc-signature")
        self.assertEqual(result["kamino_relevance"], "direct")

    def test_thresholds_must_be_positive(self):
        with self.assertRaises(InputError):
            Thresholds(rapid_count=0)


if __name__ == "__main__":
    unittest.main()

