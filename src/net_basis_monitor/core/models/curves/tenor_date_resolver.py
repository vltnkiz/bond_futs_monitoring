from datetime import date, timedelta

from dateutil.relativedelta import relativedelta


def _add_business_days(d: date, n: int) -> date:
    while n > 0:
        d += timedelta(days=1)
        if d.weekday() <= 4:
            n -= 1
    return d


def _modified_following(d: date) -> date:
    """Modified Following: if d falls on a weekend, move to next Monday unless that
    crosses into a new month, in which case move back to the previous Friday."""
    if d.weekday() <= 4:
        return d
    # Saturday (5) → Monday (+2), Sunday (6) → Monday (+1)
    candidate = d + timedelta(days=7 - d.weekday())
    if candidate.month == d.month:
        return candidate
    # Crosses month end — go to previous Friday instead
    return d - timedelta(days=d.weekday() - 4)


class TenorDateResolver:
    """Resolve money-market tenor labels to maturity dates.

    Uses standard EUR spot (T+2 business days) conventions.
    Weekend adjustments applied via Modified Following.
    Note: public holiday calendars are not applied.

    Supported labels
    ----------------
    ON          Overnight      — T+1 business day
    TN          Tom-Next       — T+2 business days (spot)
    SN          Spot-Next      — T+3 business days
    nW          n weeks        — spot + n*7 days, modified following
    nM          n months       — spot + n months,  modified following
    nY          n years        — spot + n years,   modified following
    """

    def resolve(self, tenor: str, today: date) -> date:
        tenor = tenor.upper().strip()
        spot = _add_business_days(today, 2)

        if tenor == "ON":
            return _add_business_days(today, 1)
        if tenor == "TN":
            return spot
        if tenor == "SN":
            return _add_business_days(today, 3)

        if len(tenor) >= 2:
            unit = tenor[-1]
            try:
                n = int(tenor[:-1])
            except ValueError:
                raise ValueError(f"Unrecognised tenor format: '{tenor}'")

            if unit == "W":
                return _modified_following(spot + timedelta(weeks=n))
            if unit == "M":
                return _modified_following(spot + relativedelta(months=n))
            if unit == "Y":
                return _modified_following(spot + relativedelta(years=n))

        raise ValueError(f"Unrecognised tenor format: '{tenor}'")
