import json
from typing import Dict, List

from .bond import Bond


class BondDefinition:    
    def __init__(self, json_file: str = "bond_definition.json"):
        self.json_file = json_file
        self.bonds: Dict[str, Bond] = {}
        self.load()
    
    def add_bond(self, bond: Bond) -> None:
        self.bonds[bond.ISIN] = bond
    
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
        print(f"✓ Saved {len(self.bonds)} bonds to {self.json_file}")
    
    def load(self) -> None:
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.bonds = {}
            for isin, bond_data in data.items():
                self.bonds[isin] = Bond.from_dict(bond_data)
            
            print(f"✓ Loaded {len(self.bonds)} bonds from {self.json_file}")
        except FileNotFoundError:
            print(f"Note: {self.json_file} not found. Starting with empty portfolio.")
            self.bonds = {}
        except json.JSONDecodeError:
            print(f"Note: {self.json_file} is empty. Starting with empty portfolio.")
            self.bonds = {}
    
    def update_conversion_factor(self, isin: str, future: str, cf: float) -> bool:
        if isin in self.bonds:
            self.bonds[isin].add_conversion_factor(future, cf)
            return True
        return False
    
    def __repr__(self) -> str:
        return f"BondDefinition({len(self.bonds)} bonds)"
    
    def __len__(self) -> int:
        return len(self.bonds)