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

        self._ContractSymbol = ContractSymbol
        self._ExpiryMonth = ExpiryMonth
        self._LastTradingDate = LastTradingDate
        self._DeliveryDate = DeliveryDate
        self._NotionalValue = NotionalValue
        self._TickValue = TickValue
        self._NotionalCoupon = NotionalCoupon
        self._DeliverableBonds = DeliverableBonds if DeliverableBonds is not None else set()
    
    @property
    def contract_symbol(self) -> str:
        return self._ContractSymbol

    def enrich_expiry_dates(self, expiry_month: str, last_trading_date: str, delivery_date: str) -> None:
        self._ExpiryMonth = expiry_month
        self._LastTradingDate = last_trading_date
        self._DeliveryDate = delivery_date

    def add_deliverable_bond(self, isin: str) -> None:
        self._DeliverableBonds.add(isin)

    def replace_deliverable_bonds(self, isins: set) -> None:
        self._DeliverableBonds = set(isins)
    
    def is_deliverable_bond(self, isin: str) -> bool:
        return isin in self._DeliverableBonds
    
    def remove_deliverable_bond(self, isin: str) -> None:
        self._DeliverableBonds.discard(isin)
    
    def get_all_deliverable_bonds(self) -> Set[str]:
        return self._DeliverableBonds.copy()
    
    def to_dict(self) -> dict:
        return {
            "ContractSymbol": self._ContractSymbol,
            "ExpiryMonth": self._ExpiryMonth,
            "LastTradingDate": self._LastTradingDate,
            "DeliveryDate": self._DeliveryDate,
            "NotionalValue": self._NotionalValue,
            "TickValue": self._TickValue,
            "NotionalCoupon": self._NotionalCoupon,
            "DeliverableBonds": list(self._DeliverableBonds)
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
