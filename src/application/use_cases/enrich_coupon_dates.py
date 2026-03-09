import time
from datetime import date
from dateutil.relativedelta import relativedelta
import lseg.data as ld
from lseg.data.content import pricing

from src.core.models.bond_definition import BondDefinition


def _ric_from_isin(isin: str) -> str:
    """Derives the LSEG pricing RIC from an ISIN using the standard formula."""
    return f"{isin[0:2]}{isin[5:11]}="


def _coupon_frequency_months(isin: str) -> int:
    """
    Returns the coupon period in months.
    Italian government bonds (BTP) are semi-annual; all others are annual.
    """
    if isin.startswith("IT"):
        return 6
    return 12


def enrich_coupon_dates(bond_definition: BondDefinition, timeout_seconds: int = 15) -> None:
    """
    Fetches COUPN_DATE (next coupon date) from the LSEG streaming feed for every bond
    in bond_definition, then deduces LastCouponDate by subtracting the coupon frequency.
    Updates each Bond in-place and saves the bond definition to disk.
    """
    bonds = bond_definition.get_all_bonds()
    ric_to_isin = {_ric_from_isin(b.ISIN): b.ISIN for b in bonds}
    rics = list(ric_to_isin.keys())

    snapshots: dict[str, dict] = {}

    def on_refresh(fields: dict, instrument: str, stream):
        snapshots[instrument] = dict(fields)

    print(f"Fetching coupon dates for {len(rics)} bonds from LSEG...")
    stream = pricing.Definition(
        universe=rics,
        fields=["COUPN_DATE"],
    ).get_stream()
    stream.on_refresh(on_refresh)
    stream.open(with_updates=False)

    deadline = time.time() + timeout_seconds
    while len(snapshots) < len(rics) and time.time() < deadline:
        time.sleep(0.2)

    stream.close()

    updated = 0
    for ric, isin in ric_to_isin.items():
        bond = bond_definition.get_bond(isin)
        if bond is None:
            continue

        raw = snapshots.get(ric, {})
        next_cpn_raw = raw.get("COUPN_DATE")

        if next_cpn_raw is None or str(next_cpn_raw) in ("nan", "None", ""):
            print(f"  [{isin}] no COUPN_DATE received")
            continue
        
        if isinstance(next_cpn_raw, date):
            next_cpn = next_cpn_raw
        else:
            next_cpn = date.fromisoformat(str(next_cpn_raw)[:10])

        freq_months = _coupon_frequency_months(isin)
        last_cpn = next_cpn - relativedelta(months=freq_months)

        bond.NextCouponDate = next_cpn.isoformat()
        bond.LastCouponDate = last_cpn.isoformat()
        updated += 1
        print(f"  [{isin}] NextCouponDate={bond.NextCouponDate}  LastCouponDate={bond.LastCouponDate}")

    print(f"\nEnriched {updated}/{len(rics)} bonds with coupon dates.")
    bond_definition.save()
