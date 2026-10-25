"""Environment selection for optional local historical data access."""
from __future__ import annotations

import os
from collections.abc import Mapping

from .providers import HistoricalCandleProvider
from .upstox import UpstoxHistoricalCandleProvider, UpstoxSetupError


def configured_historical_provider(*, environ: Mapping[str, str] | None = None
                                   ) -> HistoricalCandleProvider | None:
    """Return Upstox only when opted in; ``None`` leaves synthetic snapshot mode active."""
    env = os.environ if environ is None else environ
    mode = env.get("DATA_PROVIDER", "synthetic").strip().lower()
    if mode == "synthetic":
        return None
    if mode != "upstox":
        raise ValueError("DATA_PROVIDER must be 'synthetic' or 'upstox'")
    token = env.get("UPSTOX_ACCESS_TOKEN")
    if not token or not token.strip():
        raise UpstoxSetupError(
            "DATA_PROVIDER=upstox requires UPSTOX_ACCESS_TOKEN in the environment")
    return UpstoxHistoricalCandleProvider(access_token=token)
