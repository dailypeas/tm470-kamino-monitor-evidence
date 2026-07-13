"""Small standard-library Solana JSON-RPC client."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

from .core import InputError, normalise_rpc_transaction


def _rpc_url() -> str:
    value = os.environ.get("HELIUS_RPC_URL", "").strip()
    if not value:
        raise InputError("live mode requires the HELIUS_RPC_URL environment variable")
    api_key = os.environ.get("HELIUS_API_KEY", "").strip()
    return value.replace("{HELIUS_API_KEY}", api_key)


def rpc_call(method: str, params: list[Any]) -> Any:
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    request = urllib.request.Request(
        _rpc_url(), data=payload, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            document = json.load(response)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise InputError(f"RPC request failed: {type(exc).__name__}") from exc
    if document.get("error"):
        raise InputError(f"RPC returned an error: {document['error']}")
    return document.get("result")


def retrieve_transaction(signature: str) -> list[dict[str, Any]]:
    result = rpc_call(
        "getTransaction",
        [signature, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}],
    )
    if result is None:
        raise InputError("transaction was not found")
    return [normalise_rpc_transaction(result, signature)]


def retrieve_wallet(address: str, limit: int = 50) -> list[dict[str, Any]]:
    signatures = rpc_call("getSignaturesForAddress", [address, {"limit": limit}]) or []
    records: list[dict[str, Any]] = []
    for item in signatures:
        signature = item.get("signature")
        if not isinstance(signature, str):
            continue
        result = rpc_call(
            "getTransaction",
            [signature, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}],
        )
        if result is not None:
            records.append(normalise_rpc_transaction(result, signature))
    return records

