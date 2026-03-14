from typing import Dict, Optional


class Bond:    
    def __init__(
        self,
        ISIN: str, 
        CouponRate: float, 
        MaturityDate: str,
        DayCountConv: str,
        CF: Dict[str, float] = None,
        NextCouponDate: Optional[str] = None,
        LastCouponDate: Optional[str] = None,
    ):
        self._ISIN = ISIN
        self._CouponRate = CouponRate
        self._MaturityDate = MaturityDate
        self._DayCountConv = DayCountConv
        self._CF = CF if CF is not None else {}
        self._NextCouponDate = NextCouponDate
        self._LastCouponDate = LastCouponDate
    
    @property
    def isin(self) -> str:
        return self._ISIN

    def enrich_coupon_dates(self, next_coupon_date: str, last_coupon_date: str) -> None:
        self._NextCouponDate = next_coupon_date
        self._LastCouponDate = last_coupon_date

    def add_conversion_factor(self, future: str, conversion_factor: float) -> None:
        self._CF[future] = conversion_factor

    def replace_conversion_factors(self, conversion_factors: dict) -> None:
        self._CF.clear()
        self._CF.update(conversion_factors)
    
    def get_conversion_factor(self, future: str) -> float:
        return self._CF.get(future)

    def get_all_conversion_factors(self) -> dict:
        return dict(self._CF)
    
    def to_dict(self) -> dict:
        d = {
            "ISIN": self._ISIN,
            "CouponRate": self._CouponRate,
            "MaturityDate": self._MaturityDate,
            "DayCountConv": self._DayCountConv,
            "CF": self._CF,
        }
        if self._NextCouponDate is not None:
            d["NextCouponDate"] = self._NextCouponDate
        if self._LastCouponDate is not None:
            d["LastCouponDate"] = self._LastCouponDate
        return d
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Bond':
        return cls(
            ISIN=data["ISIN"],
            CouponRate=data["CouponRate"],
            MaturityDate=data["MaturityDate"],
            DayCountConv=data["DayCountConv"],
            CF=data.get("CF", {}),
            NextCouponDate=data.get("NextCouponDate"),
            LastCouponDate=data.get("LastCouponDate"),
        )
