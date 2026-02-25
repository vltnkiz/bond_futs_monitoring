from static_data_loader.core.models.Future import Future
from typing import Dict, List
import json


class FutureDefinition:
    def __init__(self, json_file: str = "futures_definition.json"):
        self.json_file = json_file
        self.futures: Dict[str, Future] = {}
        self.load()
    
    def add_future(self, future: Future) -> None:
        self.futures[future.ContractSymbol] = future
    
    def get_future(self, contract_symbol: str) -> Future:
        return self.futures.get(contract_symbol)
    
    def remove_future(self, contract_symbol: str) -> bool:
        if contract_symbol in self.futures:
            del self.futures[contract_symbol]
            return True
        return False
    
    def get_all_futures(self) -> List[Future]:
        return list(self.futures.values())
    
    def save(self) -> None:
        data = {
            symbol: future.to_dict()
            for symbol, future in self.futures.items()
        }
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved {len(self.futures)} futures to {self.json_file}")
    
    def load(self) -> None:
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.futures = {}
            for symbol, future_data in data.items():
                self.futures[symbol] = Future.from_dict(future_data)
            
            print(f"✓ Loaded {len(self.futures)} futures from {self.json_file}")
        except FileNotFoundError:
            print(f"Note: {self.json_file} not found. Starting with empty portfolio.")
            self.futures = {}
        except json.JSONDecodeError:
            print(f"Note: {self.json_file} is empty. Starting with empty portfolio.")
            self.futures = {}
    
    def add_deliverable_bond(self, contract_symbol: str, isin: str) -> bool:
        if contract_symbol in self.futures:
            self.futures[contract_symbol].add_deliverable_bond(isin)
            return True
        return False
    
    def remove_deliverable_bond(self, contract_symbol: str, isin: str) -> bool:
        if contract_symbol in self.futures:
            self.futures[contract_symbol].remove_deliverable_bond(isin)
            return True
        return False
    
    def __repr__(self) -> str:
        return f"FutureDefinition({len(self.futures)} futures)"
    
    def __len__(self) -> int:
        return len(self.futures)
