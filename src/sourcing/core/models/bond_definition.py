import json
import logging
from typing import Dict, List

from .bond import Bond

_logger = logging.getLogger(__name__)


class BondPortfolio:    
    def __init__(self, json_file: str = "bond_portfolio.json"):
        self.json_file = json_file
        self.bonds: Dict[str, Bond] = {}
        self.load()
    
    def add_bond(self, bond: Bond) -> None:
        self.bonds[bond.isin] = bond
    
    def get_bond(self, isin: str) -> Bond:
        return self.bonds.get(isin)
    
    def remove_bond(self, isin: str) -> bool:
        if isin in self.bonds:
            del self.bonds[isin]
            return True
        return False
    
    def get_all_bonds(self) -> List[Bond]:
        return list(self.bonds.values())
    
    def save(self) -> None:
        data = {
            isin: bond.to_dict()
            for isin, bond in self.bonds.items()
        }
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        _logger.info("Saved %d bonds to %s", len(self.bonds), self.json_file)
    
    def load(self) -> None:
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.bonds = {}
            for isin, bond_data in data.items():
                self.bonds[isin] = Bond.from_dict(bond_data)
            
            _logger.info("Loaded %d bonds from %s", len(self.bonds), self.json_file)
        except FileNotFoundError:
            _logger.info("%s not found. Starting with empty portfolio.", self.json_file)
            self.bonds = {}
        except json.JSONDecodeError:
            _logger.warning("%s is empty or invalid. Starting with empty portfolio.", self.json_file)
            self.bonds[isin].add_conversion_factor(future, cf)
            return True
        return False