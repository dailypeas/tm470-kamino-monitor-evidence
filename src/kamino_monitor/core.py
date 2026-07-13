"""Normalisation and transparent indicator evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable

KAMINO_LENDING_MAINNET = "KLend2g3cP87fffoy8q1mQqGKjrxjC8boSyAYavgmjD"


class InputError(ValueError):
    """Raised when an input cannot be analysed safely."""


@dataclass(frozen=True)
class Thresholds:
    rapid_count: int = 3
    rapid_window_seconds: int = 600
    failure_count: int = 2
    failure_window_seconds: int = 600

    def __post_init__(self) -> None:
        for name, value in self.__dict__.items():
            if not isinstance(value, int) or value <= 0:
                raise InputError(f"{name} must be a positive integer")


def _normalise_account_keys(message: dict[str, Any], meta: dict[str, Any]) -> list[str]:
    keys: list[str] = []
    for item in message.get("accountKeys", []):
        value = item.get("pubkey") if isinstance(item, dict) else item
        if isinstance(value, str):
            keys.append(value)
    loaded = meta.get("loadedAddresses") or {}
    for group in ("writable", "readonly"):
        keys.extend(value for value in loaded.get(group, []) if isinstance(value, str))
    return keys


def _instruction_program_ids(
    instructions: Iterable[dict[str, Any]], account_keys: list[str]
) -> list[str]:
    program_ids: list[str] = []
    for instruction in instructions:
        direct = instruction.get("programId")
        if isinstance(direct, str):
            program_ids.append(direct)
            continue
        index = instruction.get("programIdIndex")
        if isinstance(index, int) and 0 <= index < len(account_keys):
            program_ids.append(account_keys[index])
    return program_ids


def normalise_rpc_transaction(result: dict[str, Any], signature: str) -> dict[str, Any]:
    """Convert a Solana getTransaction result to the canonical record."""
    if not isinstance(result, dict):
        raise InputError("RPC transaction result must be an object")
    transaction = result.get("transaction") or {}
    message = transaction.get("message") or {}
    meta = result.get("meta") or {}
    account_keys = _normalise_account_keys(message, meta)
    instructions = list(message.get("instructions") or [])
    for inner_group in meta.get("innerInstructions") or []:
        instructions.extend(inner_group.get("instructions") or [])
    program_ids = _instruction_program_ids(instructions, account_keys)
    error = meta.get("err")
    timestamp = result.get("blockTime")
    return normalise_canonical_transaction(
        {
            "signature": signature,
            "timestamp": timestamp,
            "status": "failed" if error is not None else "success",
            "error": error,
            "fee_payer": account_keys[0] if account_keys else None,
            "account_keys": account_keys,
            "invoked_program_ids": program_ids,
            "token_transfers": [],
            "source_type": "solana_rpc",
            "source_case_id": None,
        }
    )


def normalise_canonical_transaction(raw: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise InputError("each transaction must be an object")
    signature = raw.get("signature")
    if not isinstance(signature, str) or not signature.strip():
        raise InputError("transaction signature must be a non-empty string")
    timestamp = raw.get("timestamp")
    if timestamp is not None and (not isinstance(timestamp, int) or isinstance(timestamp, bool)):
        raise InputError(f"{signature}: timestamp must be an integer or null")
    status = raw.get("status", "unknown")
    if status not in {"success", "failed", "unknown"}:
        raise InputError(f"{signature}: invalid status {status!r}")
    programs = raw.get("invoked_program_ids")
    if programs is None:
        programs = []
        relevance = "unknown"
    elif not isinstance(programs, list) or not all(isinstance(value, str) for value in programs):
        raise InputError(f"{signature}: invoked_program_ids must be a string list")
    else:
        relevance = "direct" if KAMINO_LENDING_MAINNET in programs else "not_direct"
    transfers = raw.get("token_transfers") or []
    if not isinstance(transfers, list):
        raise InputError(f"{signature}: token_transfers must be a list")
    for transfer in transfers:
        if not isinstance(transfer, dict):
            raise InputError(f"{signature}: each token transfer must be an object")
        amount = transfer.get("amount")
        if amount is not None:
            try:
                Decimal(str(amount))
            except InvalidOperation as exc:
                raise InputError(f"{signature}: invalid transfer amount") from exc
    return {
        "signature": signature,
        "timestamp": timestamp,
        "status": status,
        "error": raw.get("error"),
        "fee_payer": raw.get("fee_payer"),
        "account_keys": list(raw.get("account_keys") or []),
        "invoked_program_ids": programs,
        "kamino_relevance": relevance,
        "token_transfers": transfers,
        "source_type": raw.get("source_type", "fixture"),
        "source_case_id": raw.get("source_case_id"),
    }


def load_fixture_document(document: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    if not isinstance(document, dict):
        raise InputError("fixture top level must be an object")
    if document.get("fixture_version") != "1.0":
        raise InputError("fixture_version must be '1.0'")
    case_id = document.get("case_id")
    if not isinstance(case_id, str) or not case_id:
        raise InputError("fixture case_id must be a non-empty string")
    transactions = document.get("transactions")
    if not isinstance(transactions, list):
        raise InputError("fixture transactions must be a list")
    return case_id, [normalise_canonical_transaction(item) for item in transactions]


def _indicator(status: str, triggered: bool | None, **details: Any) -> dict[str, Any]:
    return {"status": status, "triggered": triggered, **details}


def analyse(transactions: list[dict[str, Any]], thresholds: Thresholds) -> list[dict[str, Any]]:
    relevant = [item for item in transactions if item["kamino_relevance"] == "direct"]
    assessed: list[dict[str, Any]] = []
    for current in transactions:
        timestamp = current["timestamp"]
        if current["kamino_relevance"] != "direct":
            reason = "Transaction is not a verified direct invocation of the configured Kamino Lending programme."
            rapid = _indicator("not_evaluated", None, reason=reason)
            failures = _indicator("not_evaluated", None, reason=reason)
        elif timestamp is None:
            reason = "Timestamp is missing; rolling-window indicators cannot be evaluated."
            rapid = _indicator("not_evaluated", None, reason=reason)
            failures = _indicator("not_evaluated", None, reason=reason)
        else:
            rapid_start = timestamp - thresholds.rapid_window_seconds
            rapid_history = [
                item for item in relevant
                if item["timestamp"] is not None and rapid_start <= item["timestamp"] <= timestamp
            ]
            if len([item for item in relevant if item["timestamp"] is not None]) < thresholds.rapid_count:
                rapid = _indicator(
                    "not_evaluated", None,
                    observed_count=len(rapid_history),
                    threshold_count=thresholds.rapid_count,
                    window_seconds=thresholds.rapid_window_seconds,
                    reason="Insufficient timestamped directly relevant history for the configured count threshold.",
                )
            else:
                triggered = len(rapid_history) >= thresholds.rapid_count
                rapid = _indicator(
                    "evaluated", triggered,
                    observed_count=len(rapid_history),
                    threshold_count=thresholds.rapid_count,
                    window_seconds=thresholds.rapid_window_seconds,
                    reason=(
                        f"{len(rapid_history)} directly Kamino-related transactions were observed "
                        f"in the preceding {thresholds.rapid_window_seconds // 60} minutes "
                        f"(provisional threshold: {thresholds.rapid_count})."
                    ),
                )
            failure_start = timestamp - thresholds.failure_window_seconds
            failure_window = [
                item for item in relevant
                if item["timestamp"] is not None and failure_start <= item["timestamp"] <= timestamp
            ]
            if current["status"] == "unknown" or any(item["status"] == "unknown" for item in failure_window):
                failures = _indicator(
                    "not_evaluated", None,
                    reason="At least one directly relevant record in the failure window has unknown status.",
                )
            else:
                failed_count = sum(item["status"] == "failed" for item in failure_window)
                triggered = failed_count >= thresholds.failure_count
                failures = _indicator(
                    "evaluated", triggered,
                    observed_count=failed_count,
                    threshold_count=thresholds.failure_count,
                    window_seconds=thresholds.failure_window_seconds,
                    reason=(
                        f"{failed_count} failed directly Kamino-related transactions were observed "
                        f"in the preceding {thresholds.failure_window_seconds // 60} minutes "
                        f"(provisional threshold: {thresholds.failure_count})."
                    ),
                )
        rapid_true = rapid["triggered"] is True
        failure_true = failures["triggered"] is True
        if rapid_true and failure_true:
            priority = "elevated"
        elif failure_true:
            priority = "moderate"
        elif rapid_true:
            priority = "low"
        else:
            priority = "no_elevated_indicator_observed"
        assessed.append(
            {
                **current,
                "indicators": {
                    "rapid_relevant_activity": rapid,
                    "repeated_failed_relevant_transactions": failures,
                },
                "priority": priority,
                "output_caveat": "Priority supports manual technical review; it is not a probability or finding of maliciousness.",
            }
        )
    return assessed


def make_run_result(
    case_id: str, transactions: list[dict[str, Any]], thresholds: Thresholds
) -> dict[str, Any]:
    assessed = analyse(transactions, thresholds)
    return {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "case_id": case_id,
        "thresholds": thresholds.__dict__,
        "records": assessed,
        "summary": {
            "transaction_count": len(assessed),
            "direct_kamino_count": sum(item["kamino_relevance"] == "direct" for item in assessed),
            "priority_counts": {
                value: sum(item["priority"] == value for item in assessed)
                for value in ("elevated", "moderate", "low", "no_elevated_indicator_observed")
            },
        },
        "limitations": [
            "Direct invocation of one configured Kamino Lending mainnet programme is the only relevance test.",
            "Thresholds are provisional project assumptions and are not validated fraud thresholds.",
            "No ground-truth maliciousness labels are inferred.",
        ],
    }

