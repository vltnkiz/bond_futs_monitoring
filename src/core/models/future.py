from typing import Set


class Future:
    def __init__(
        self, 
        ContractSymbol: str, 
        ExpiryMonth: str,
        LastTradingDate: str,
        DeliveryDate: str,
        NotionalValue: float,
        TickValue: float,
        NotionalCoupon: float,
        DeliverableBonds: Set[str] = None
    ):

        self.ContractSymbol = ContractSymbol
        self.ExpiryMonth = ExpiryMonth
        self.LastTradingDate = LastTradingDate
        self.DeliveryDate = DeliveryDate
        self.NotionalValue = NotionalValue
        self.TickValue = TickValue
        self.NotionalCoupon = NotionalCoupon
        self.DeliverableBonds = DeliverableBonds if DeliverableBonds is not None else set()
    
    def add_deliverable_bond(self, isin: str) -> None:
        self.DeliverableBonds.add(isin)
    
    def is_deliverable_bond(self, isin: str) -> bool:
        return isin in self.DeliverableBonds
    
    def remove_deliverable_bond(self, isin: str) -> None:
        self.DeliverableBonds.discard(isin)
    
    def get_all_deliverable_bonds(self) -> Set[str]:
        return self.DeliverableBonds.copy()
    
    def __repr__(self) -> str:
        return (
            f"Future(ContractSymbol={self.ContractSymbol}, ExpiryMonth={self.ExpiryMonth}, "
            f"LastTradingDate={self.LastTradingDate}, DeliveryDate={self.DeliveryDate}, "
            f"NotionalValue={self.NotionalValue}, TickValue={self.TickValue}, "
            f"NotionalCoupon={self.NotionalCoupon}, DeliverableBonds={len(self.DeliverableBonds)} bonds)"
        )
    
    def __str__(self) -> str:
        bond_list = "\n    ".join(sorted(self.DeliverableBonds)) if self.DeliverableBonds else "None"
        
        return (
            f"Future {self.ContractSymbol}\n"
            f"  Expiry Month: {self.ExpiryMonth}\n"
            f"  Last Trading Date: {self.LastTradingDate}\n"
            f"  Delivery Date: {self.DeliveryDate}\n"
            f"  Notional Value: {self.NotionalValue:,.2f}\n"
            f"  Tick Value: {self.TickValue}\n"
            f"  Notional Coupon: {self.NotionalCoupon:.6f}\n"
            f"  Deliverable Bonds:\n    {bond_list}"
        )
    
    def to_dict(self) -> dict:
        return {
            "ContractSymbol": self.ContractSymbol,
            "ExpiryMonth": self.ExpiryMonth,
            "LastTradingDate": self.LastTradingDate,
            "DeliveryDate": self.DeliveryDate,
            "NotionalValue": self.NotionalValue,
            "TickValue": self.TickValue,
            "NotionalCoupon": self.NotionalCoupon,
            "DeliverableBonds": list(self.DeliverableBonds)
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Future':
        return cls(
            ContractSymbol=data["ContractSymbol"],
            ExpiryMonth=data["ExpiryMonth"],
            LastTradingDate=data["LastTradingDate"],
            DeliveryDate=data["DeliveryDate"],
            NotionalValue=data["NotionalValue"],
            TickValue=data["TickValue"],
            NotionalCoupon=data["NotionalCoupon"],
            DeliverableBonds=set(data.get("DeliverableBonds", []))
        )
