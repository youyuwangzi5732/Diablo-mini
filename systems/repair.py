"""
装备修理系统
"""
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum


@dataclass
class RepairResult:
    success: bool
    item: Any
    message: str
    cost: int = 0
    durability_restored: int = 0


class RepairSystem:
    REPAIR_COST_PER_DURABILITY = 10
    
    def __init__(self):
        self.repair_discount = 0.0
    
    def calculate_repair_cost(self, item: Any) -> int:
        if not hasattr(item, 'current_durability') or not hasattr(item, 'max_durability'):
            return 0
        
        durability_loss = item.max_durability - item.current_durability
        
        if durability_loss <= 0:
            return 0
        
        rarity = getattr(item, 'rarity', None)
        rarity_mult = 1.0
        if rarity:
            rarity_value = rarity.value if hasattr(rarity, 'value') else 0
            rarity_mult = 1.0 + rarity_value * 0.5
        
        item_level = getattr(item, 'level', 1)
        level_mult = 1.0 + item_level * 0.1
        
        base_cost = durability_loss * self.REPAIR_COST_PER_DURABILITY
        final_cost = int(base_cost * rarity_mult * level_mult)
        
        if self.repair_discount > 0:
            final_cost = int(final_cost * (1 - self.repair_discount))
        
        return max(1, final_cost)
    
    def repair_item(self, item: Any, player_gold: int) -> RepairResult:
        if not hasattr(item, 'current_durability') or not hasattr(item, 'max_durability'):
            return RepairResult(False, item, "此物品无法修理")
        
        if item.current_durability >= item.max_durability:
            return RepairResult(False, item, "此物品不需要修理")
        
        cost = self.calculate_repair_cost(item)
        
        if player_gold < cost:
            return RepairResult(False, item, f"金币不足，需要 {cost} 金币")
        
        durability_restored = item.max_durability - item.current_durability
        item.current_durability = item.max_durability
        
        return RepairResult(
            True, item,
            f"修理成功！恢复了 {durability_restored} 点耐久度",
            cost,
            durability_restored
        )
    
    def repair_all(self, items: List[Any], player_gold: int) -> Tuple[List[RepairResult], int, int]:
        results = []
        total_cost = 0
        total_repaired = 0
        remaining_gold = player_gold
        
        for item in items:
            if item is None:
                continue
            
            if not hasattr(item, 'current_durability') or not hasattr(item, 'max_durability'):
                continue
            
            if item.current_durability >= item.max_durability:
                continue
            
            cost = self.calculate_repair_cost(item)
            
            if remaining_gold >= cost:
                result = self.repair_item(item, remaining_gold)
                results.append(result)
                
                if result.success:
                    total_cost += result.cost
                    total_repaired += 1
                    remaining_gold -= result.cost
        
        return results, total_cost, total_repaired
    
    def get_repair_preview(self, item: Any) -> Dict[str, Any]:
        if not hasattr(item, 'current_durability') or not hasattr(item, 'max_durability'):
            return {"can_repair": False}
        
        durability_loss = item.max_durability - item.current_durability
        
        if durability_loss <= 0:
            return {"can_repair": False, "message": "不需要修理"}
        
        return {
            "can_repair": True,
            "current_durability": item.current_durability,
            "max_durability": item.max_durability,
            "durability_loss": durability_loss,
            "cost": self.calculate_repair_cost(item)
        }
    
    def get_all_repair_cost(self, items: List[Any]) -> int:
        total = 0
        for item in items:
            if item is None:
                continue
            total += self.calculate_repair_cost(item)
        return total
    
    def set_discount(self, discount: float):
        self.repair_discount = max(0.0, min(0.5, discount))
