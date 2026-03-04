"""
装备强化系统
"""
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random


class EnhancementType(Enum):
    UPGRADE = "upgrade"
    REFINE = "refine"
    REROLL = "reroll"
    SOCKET = "socket"
    TRANSMUTE = "transmute"
    ENCHANT = "enchant"


@dataclass
class EnhancementResult:
    success: bool
    item: Any
    message: str
    cost: int = 0
    bonus_applied: Dict[str, float] = field(default_factory=dict)


class EnhancementSystem:
    UPGRADE_COSTS = {
        1: 100, 2: 200, 3: 400, 4: 800, 5: 1600,
        6: 3200, 7: 6400, 8: 12800, 9: 25600, 10: 51200,
        11: 100000, 12: 200000, 13: 400000, 14: 800000, 15: 1500000
    }
    
    UPGRADE_SUCCESS_RATES = {
        1: 1.0, 2: 1.0, 3: 0.95, 4: 0.90, 5: 0.85,
        6: 0.75, 7: 0.65, 8: 0.55, 9: 0.45, 10: 0.35,
        11: 0.25, 12: 0.20, 13: 0.15, 14: 0.10, 15: 0.05
    }
    
    UPGRADE_STAT_BONUSES = {
        1: 1.0, 2: 2.0, 3: 3.0, 4: 4.0, 5: 5.0,
        6: 7.0, 7: 9.0, 8: 11.0, 9: 14.0, 10: 17.0,
        11: 21.0, 12: 26.0, 13: 32.0, 14: 39.0, 15: 50.0
    }
    
    def __init__(self):
        self.enchant_materials = {
            "common": "crystal_shard",
            "magic": "magic_dust",
            "rare": "rare_essence",
            "legendary": "legendary_soul",
            "set": "set_essence"
        }
    
    def upgrade_equipment(self, item: Any, player_gold: int,
                          materials: Dict[str, int] = None) -> EnhancementResult:
        if not hasattr(item, 'enchant_level'):
            return EnhancementResult(False, item, "此物品无法强化")
        
        current_level = item.enchant_level
        
        if current_level >= 15:
            return EnhancementResult(False, item, "已达到最高强化等级")
        
        cost = self.UPGRADE_COSTS.get(current_level + 1, 1000000)
        
        if player_gold < cost:
            return EnhancementResult(False, item, f"金币不足，需要 {cost} 金币")
        
        success_rate = self.UPGRADE_SUCCESS_RATES.get(current_level + 1, 0.05)
        
        if materials:
            protection_stone = materials.get("protection_stone", 0)
            if protection_stone > 0:
                success_rate += 0.1 * protection_stone
                success_rate = min(1.0, success_rate)
        
        roll = random.random()
        
        if roll < success_rate:
            item.enchant_level += 1
            bonus_percent = self.UPGRADE_STAT_BONUSES.get(item.enchant_level, 50)
            
            return EnhancementResult(
                True, item,
                f"强化成功！装备等级提升至 +{item.enchant_level}",
                cost,
                {"stat_bonus_percent": bonus_percent}
            )
        else:
            if current_level >= 7:
                if random.random() < 0.5:
                    item.enchant_level = max(0, current_level - 1)
                    return EnhancementResult(
                        False, item,
                        f"强化失败，装备等级降至 +{item.enchant_level}",
                        cost
                    )
            
            return EnhancementResult(False, item, "强化失败", cost)
    
    def reroll_affix(self, item: Any, affix_index: int,
                     player_gold: int, materials: Dict[str, int] = None) -> EnhancementResult:
        if not hasattr(item, 'affixes') or not item.affixes:
            return EnhancementResult(False, item, "此物品没有可重铸的词缀")
        
        if affix_index < 0 or affix_index >= len(item.affixes):
            return EnhancementResult(False, item, "无效的词缀索引")
        
        rarity = getattr(item, 'rarity', None)
        rarity_value = rarity.value if hasattr(rarity, 'value') else 0
        
        cost = 1000 * (rarity_value + 1) * (affix_index + 1)
        
        if player_gold < cost:
            return EnhancementResult(False, item, f"金币不足，需要 {cost} 金币")
        
        from entities.items.affix import AffixGenerator
        AffixGenerator.initialize()
        
        item_level = getattr(item, 'level', 1)
        
        old_affix = item.affixes[affix_index]
        new_affixes = AffixGenerator.roll_affixes(item_level, rarity_value, 1)
        
        if new_affixes:
            new_affix, new_value = new_affixes[0]
            item.affixes[affix_index] = type(old_affix)(
                affix=new_affix,
                value=new_value,
                is_ancient=getattr(old_affix, 'is_ancient', False)
            )
            
            return EnhancementResult(
                True, item,
                f"词缀重铸成功：{new_affix.name} +{new_value:.1f}",
                cost
            )
        
        return EnhancementResult(False, item, "词缀重铸失败")
    
    def add_socket(self, item: Any, player_gold: int,
                   materials: Dict[str, int] = None) -> EnhancementResult:
        if not hasattr(item, 'sockets'):
            return EnhancementResult(False, item, "此物品无法添加镶孔")
        
        max_sockets = self._get_max_sockets(item)
        current_sockets = item.sockets
        socketed_count = len(getattr(item, 'socketed_items', []))
        
        if current_sockets >= max_sockets:
            return EnhancementResult(False, item, "已达到最大镶孔数量")
        
        rarity = getattr(item, 'rarity', None)
        rarity_value = rarity.value if hasattr(rarity, 'value') else 0
        
        cost = 5000 * (current_sockets + 1) * (rarity_value + 1)
        
        if player_gold < cost:
            return EnhancementResult(False, item, f"金币不足，需要 {cost} 金币")
        
        item.sockets += 1
        
        return EnhancementResult(
            True, item,
            f"成功添加镶孔，当前镶孔数：{item.sockets}",
            cost
        )
    
    def _get_max_sockets(self, item: Any) -> int:
        item_type = getattr(item, 'item_type', None)
        item_type_value = item_type.value if hasattr(item_type, 'value') else ""
        
        if item_type_value in ["weapon"]:
            return 3
        elif item_type_value in ["armor"]:
            return 4
        elif item_type_value in ["accessory"]:
            return 1
        
        return 0
    
    def enchant_item(self, item: Any, enchant_type: str,
                     player_gold: int, materials: Dict[str, int] = None) -> EnhancementResult:
        if not hasattr(item, 'rarity'):
            return EnhancementResult(False, item, "此物品无法附魔")
        
        rarity = item.rarity
        rarity_value = rarity.value if hasattr(rarity, 'value') else 0
        
        if rarity_value < 1:
            return EnhancementResult(False, item, "普通物品无法附魔")
        
        cost = 2000 * rarity_value
        
        if player_gold < cost:
            return EnhancementResult(False, item, f"金币不足，需要 {cost} 金币")
        
        enchant_effects = {
            "fire_damage": {"fire_damage_percent": random.uniform(5, 15)},
            "cold_damage": {"cold_damage_percent": random.uniform(5, 15)},
            "lightning_damage": {"lightning_damage_percent": random.uniform(5, 15)},
            "attack_speed": {"attack_speed_percent": random.uniform(3, 8)},
            "crit_chance": {"crit_chance": random.uniform(2, 5)},
            "crit_damage": {"crit_damage_percent": random.uniform(10, 25)},
            "life_steal": {"life_steal_percent": random.uniform(1, 3)},
            "resource_cost": {"resource_cost_reduction": random.uniform(3, 8)},
        }
        
        if enchant_type not in enchant_effects:
            return EnhancementResult(False, item, "无效的附魔类型")
        
        effect = enchant_effects[enchant_type]
        
        if not hasattr(item, 'enchant_effects'):
            item.enchant_effects = {}
        
        item.enchant_effects.update(effect)
        
        return EnhancementResult(
            True, item,
            f"附魔成功：{enchant_type}",
            cost,
            effect
        )
    
    def transmute_item(self, item: Any, transmute_type: str,
                       player_gold: int, materials: Dict[str, int] = None) -> EnhancementResult:
        from entities.items.item import ItemRarity
        
        rarity = getattr(item, 'rarity', ItemRarity.COMMON)
        rarity_value = rarity.value if hasattr(rarity, 'value') else 0
        
        if transmute_type == "upgrade_rarity":
            if rarity_value >= 4:
                return EnhancementResult(False, item, "无法进一步提升品质")
            
            cost = 50000 * (rarity_value + 1)
            
            if player_gold < cost:
                return EnhancementResult(False, item, f"金币不足，需要 {cost} 金币")
            
            if materials and materials.get("legendary_soul", 0) < 1:
                return EnhancementResult(False, item, "需要传奇之魂")
            
            item.rarity = ItemRarity(rarity_value + 1)
            
            return EnhancementResult(
                True, item,
                f"物品品质提升至 {item.rarity.name}",
                cost
            )
        
        elif transmute_type == "make_ancient":
            if getattr(item, 'is_ancient', False):
                return EnhancementResult(False, item, "此物品已是远古物品")
            
            if rarity_value < 3:
                return EnhancementResult(False, item, "只有传奇或套装物品可以转化为远古物品")
            
            cost = 100000
            
            if player_gold < cost:
                return EnhancementResult(False, item, f"金币不足，需要 {cost} 金币")
            
            item.is_ancient = True
            
            for affix_inst in getattr(item, 'affixes', []):
                if hasattr(affix_inst, 'is_ancient'):
                    affix_inst.is_ancient = True
            
            return EnhancementResult(
                True, item,
                "物品已转化为远古物品，所有属性提升30%",
                cost,
                {"ancient_bonus": 0.3}
            )
        
        return EnhancementResult(False, item, "无效的转化类型")
    
    def get_upgrade_preview(self, item: Any) -> Dict[str, Any]:
        current_level = getattr(item, 'enchant_level', 0)
        
        if current_level >= 15:
            return {"max_level": True}
        
        next_level = current_level + 1
        
        return {
            "current_level": current_level,
            "next_level": next_level,
            "cost": self.UPGRADE_COSTS.get(next_level, 1000000),
            "success_rate": self.UPGRADE_SUCCESS_RATES.get(next_level, 0.05),
            "stat_bonus": self.UPGRADE_STAT_BONUSES.get(next_level, 50)
        }
