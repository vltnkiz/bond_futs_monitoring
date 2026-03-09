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
        self.ISIN = ISIN
        self.CouponRate = CouponRate
        self.MaturityDate = MaturityDate
        self.DayCountConv = DayCountConv
        self.CF = CF if CF is not None else {}
        self.NextCouponDate = NextCouponDate
        self.LastCouponDate = LastCouponDate
    
    def add_conversion_factor(self, future: str, conversion_factor: float) -> None:
        self.CF[future] = conversion_factor
    
    def get_conversion_factor(self, future: str) -> float:
        return self.CF.get(future)
    
    def __repr__(self) -> str:
        return (
            f"Bond(ISIN={self.ISIN}, CouponRate={self.CouponRate}, "
            f"MaturityDate={self.MaturityDate}, DayCountConv={self.DayCountConv}, "
            f"NextCouponDate={self.NextCouponDate}, LastCouponDate={self.LastCouponDate}, "
            f"CF={dict(self.CF)})"
        )
    
    def __str__(self) -> str:
        cf_str = ", ".join([f"{k}: {v:.6f}" for k, v in self.CF.items()])
        return (
            f"Bond {self.ISIN}\n"
            f"  Coupon: {self.CouponRate:.6f}\n"
            f"  Maturity: {self.MaturityDate}\n"
            f"  Day Count: {self.DayCountConv}\n"
            f"  Next Coupon: {self.NextCouponDate}\n"
            f"  Last Coupon: {self.LastCouponDate}\n"
            f"  Conversion Factors: {cf_str}"
        )
    
    def to_dict(self) -> dict:
        d = {
            "ISIN": self.ISIN,
            "CouponRate": self.CouponRate,
            "MaturityDate": self.MaturityDate,
            "DayCountConv": self.DayCountConv,
            "CF": self.CF,
        }
        if self.NextCouponDate is not None:
            d["NextCouponDate"] = self.NextCouponDate
        if self.LastCouponDate is not None:
            d["LastCouponDate"] = self.LastCouponDate
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
