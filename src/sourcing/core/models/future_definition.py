import json
import logging
from typing import Dict, List

from .future import Future

_logger = logging.getLogger(__name__)


class FuturePortfolio:
    def __init__(self, json_file: str = "futures_portfolio.json"):
        self.json_file = json_file
        self.futures: Dict[str, Future] = {}
        self.load()
    
    def add_future(self, future: Future) -> None:
        self.futures[future.contract_symbol] = future
    
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
        _logger.info("Saved %d futures to %s", len(self.futures), self.json_file)
    
    def load(self) -> None:
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.futures = {}
            for symbol, future_data in data.items():
                self.futures[symbol] = Future.from_dict(future_data)
            
            _logger.info("Loaded %d futures from %s", len(self.futures), self.json_file)
        except FileNotFoundError:
            _logger.info("%s not found. Starting with empty portfolio.", self.json_file)
            self.futures = {}
        except json.JSONDecodeError:
            _logger.warning("%s is empty or invalid. Starting with empty portfolio.", self.json_file)
            self.futures = {}
        return False
    
    def remove_deliverable_bond(self, contract_symbol: str, isin: str) -> bool:
        if contract_symbol in self.futures:
            self.futures[contract_symbol].remove_deliverable_bond(isin)
            return True
        return False
