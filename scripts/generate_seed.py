#!/usr/bin/env python3
"""Generate deterministic, privacy-safe Northstar Commerce demo orders."""

import csv
import random
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "warehouse" / "seeds" / "raw_orders.csv"
SEED = 20260807
ROWS = 1200


def main() -> None:
    random.seed(SEED)
    start = datetime(2026, 5, 1, 8, 0, tzinfo=UTC)
    currencies = ["USD", "GBP", "EUR"]
    regions = ["North America", "United Kingdom", "Europe"]
    statuses = ["completed"] * 8 + ["refunded", "pending"]

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(
            [
                "order_id",
                "ordered_at",
                "customer_key",
                "region",
                "currency",
                "net_amount",
                "tax_amount",
                "gross_amount",
                "order_status",
            ]
        )
        for index in range(1, ROWS + 1):
            currency_index = random.randrange(len(currencies))  # noqa: S311
            net = Decimal(random.randrange(1800, 65000)) / 100  # noqa: S311
            tax_rate = Decimal("0.20") if currency_index else Decimal("0.08")
            tax = (net * tax_rate).quantize(Decimal("0.01"))
            writer.writerow(
                [
                    f"ORD-{index:06d}",
                    (start + timedelta(minutes=index * 73)).isoformat(),
                    f"CUS-{random.randrange(1, 401):05d}",  # noqa: S311
                    regions[currency_index],
                    currencies[currency_index],
                    f"{net:.2f}",
                    f"{tax:.2f}",
                    f"{net + tax:.2f}",
                    random.choice(statuses),  # noqa: S311
                ]
            )
    print(f"generated={ROWS} path={OUTPUT}")


if __name__ == "__main__":
    main()
