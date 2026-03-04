"""
装备系统
"""
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

from .item import Item, ItemFactory, ItemType, ItemRarity
from .affix import Affix, AffixType


class EquipmentSlot(Enum):
    HEAD = "head"
    SHOULDERS = "shoulders"
    CHEST = "chest"
    HANDS = "hands"
    WAIST = "waist"
    LEGS = "legs"
    FEET = "feet"
    MAIN_HAND = "main_hand"
    OFF_HAND = "off_hand"
    NECK = "neck"
    RING_LEFT = "ring_left"
    RING_RIGHT = "ring_right"


@dataclass
class SetBonus:
    required_pieces: int
    name: str
    description: str
    effects: Dict[str, float]


@dataclass
class EquipmentSet:
    id: str
    name: str
    items: List[str]
    bonuses: List[SetBonus]


@dataclass
class Equipment(Item):
    slot: EquipmentSlot = field(default=EquipmentSlot.CHEST)
    durability: int = field(default=100)
    max_durability: int = field(default=100)
    enchant_level: int = field(default=0)
    reforge_count: int = field(default=0)
    current_durability: int = field(default=100)
    
    def __post_init__(self):
        super().__post_init__()
        self.current_durability = self.durability
    
    def get_total_armor(self) -> float:
        if self.item_type != ItemType.ARMOR:
            return 0
        
        base_armor = self.base_stats.get("armor", 0)
        
        for affix_inst in self.affixes:
            if affix_inst.affix.attribute == "armor":
                base_armor += affix_inst.get_effective_value()
        
        return base_armor
    
    def get_total_damage(self) -> Tuple[float, float]:
        if self.item_type != ItemType.WEAPON:
            return (0, 0)
        
        min_dmg = self.base_stats.get("min_damage", 0)
        max_dmg = self.base_stats.get("max_damage", 0)
        
        for affix_inst in self.affixes:
            attr = affix_inst.affix.attribute
            if attr == "min_damage":
                min_dmg += affix_inst.get_effective_value()
            elif attr == "max_damage":
                max_dmg += affix_inst.get_effective_value()
            elif attr == "damage_percent":
                percent = affix_inst.get_effective_value() / 100
                min_dmg *= (1 + percent)
                max_dmg *= (1 + percent)
        
        return (min_dmg, max_dmg)
    
    def get_dps(self) -> float:
        if self.item_type != ItemType.WEAPON:
            return 0
        
        min_dmg, max_dmg = self.get_total_damage()
        avg_damage = (min_dmg + max_dmg) / 2
        attack_speed = self.base_stats.get("attack_speed", 1.0)
        
        speed_bonus = 0
        for affix_inst in self.affixes:
            if affix_inst.affix.attribute == "attack_speed":
                speed_bonus += affix_inst.get_effective_value()
        
        effective_speed = attack_speed * (1 + speed_bonus / 100)
        
        return avg_damage * effective_speed
    
    def repair(self, amount: int = None):
        if amount is None:
            self.durability = self.max_durability
        else:
            self.durability = min(self.max_durability, self.durability + amount)
    
    def take_damage(self, amount: int = 1):
        self.durability = max(0, self.durability - amount)
    
    def is_broken(self) -> bool:
        return self.durability <= 0
    
    def enchant(self) -> bool:
        if self.enchant_level >= 15:
            return False
        
        success_chance = max(0.1, 1 - self.enchant_level * 0.1)
        
        import random
        if random.random() < success_chance:
            self.enchant_level += 1
            return True
        return False
    
    def reforge(self) -> bool:
        if self.reforge_count >= 5:
            return False
        
        self.reforge_count += 1
        
        self.affixes.clear()
        
        ItemFactory._add_affixes(self, self.level, self.rarity)
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "slot": self.slot.value,
            "durability": self.durability,
            "max_durability": self.max_durability,
            "enchant_level": self.enchant_level,
            "reforge_count": self.reforge_count
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Equipment':
        item = super().from_dict(data)
        
        equipment = cls(
            id=item.id,
            base_id=item.base_id,
            name=item.name,
            item_type=item.item_type,
            rarity=item.rarity,
            slot=EquipmentSlot(data.get("slot", "chest"))
        )
        
        equipment.level = item.level
        equipment.required_level = item.required_level
        equipment.icon = item.icon
        equipment.description = item.description
        equipment.sockets = item.sockets
        equipment.socketed_items = item.socketed_items
        equipment.affixes = item.affixes
        equipment.implicit_affixes = item.implicit_affixes
        equipment.is_identified = item.is_identified
        equipment.is_ancient = item.is_ancient
        equipment.set_id = item.set_id
        equipment.legendary_power = item.legendary_power
        equipment.base_stats = item.base_stats
        
        equipment.durability = data.get("durability", 100)
        equipment.max_durability = data.get("max_durability", 100)
        equipment.enchant_level = data.get("enchant_level", 0)
        equipment.reforge_count = data.get("reforge_count", 0)
        
        return equipment


class EquipmentManager:
    def __init__(self):
        self.equipped: Dict[EquipmentSlot, Optional[Equipment]] = {
            slot: None for slot in EquipmentSlot
        }
        self._set_bonuses: Dict[str, int] = {}
    
    def equip(self, item: Equipment, slot: EquipmentSlot = None) -> Optional[Equipment]:
        if slot is None:
            slot = item.slot
        
        if slot not in EquipmentSlot:
            return None
        
        old_item = self.equipped[slot]
        self.equipped[slot] = item
        
        if old_item:
            self._update_set_bonus(old_item.set_id, -1)
        
        if item.set_id:
            self._update_set_bonus(item.set_id, 1)
        
        return old_item
    
    def unequip(self, slot: EquipmentSlot) -> Optional[Equipment]:
        if slot not in self.equipped:
            return None
        
        item = self.equipped[slot]
        if item:
            if item.set_id:
                self._update_set_bonus(item.set_id, -1)
            self.equipped[slot] = None
        
        return item
    
    def get_equipped(self, slot: EquipmentSlot) -> Optional[Equipment]:
        return self.equipped.get(slot)
    
    def get_all_equipped(self) -> Dict[EquipmentSlot, Equipment]:
        return {slot: item for slot, item in self.equipped.items() if item is not None}
    
    def get_total_stats(self) -> Dict[str, float]:
        total_stats: Dict[str, float] = {}
        
        for item in self.equipped.values():
            if item:
                for stat, value in item.get_total_stats().items():
                    if stat in total_stats:
                        total_stats[stat] += value
                    else:
                        total_stats[stat] = value
        
        set_bonuses = self.get_active_set_bonuses()
        for bonus in set_bonuses:
            for stat, value in bonus.effects.items():
                if stat in total_stats:
                    total_stats[stat] += value
                else:
                    total_stats[stat] = value
        
        return total_stats
    
    def _update_set_bonus(self, set_id: str, change: int):
        if set_id:
            current = self._set_bonuses.get(set_id, 0)
            self._set_bonuses[set_id] = max(0, current + change)
    
    def get_set_piece_count(self, set_id: str) -> int:
        return self._set_bonuses.get(set_id, 0)
    
    def get_active_set_bonuses(self) -> List[SetBonus]:
        active_bonuses = []
        
        for set_id, count in self._set_bonuses.items():
            set_data = self._get_set_data(set_id)
            if set_data:
                for bonus in set_data.bonuses:
                    if count >= bonus.required_pieces:
                        active_bonuses.append(bonus)
        
        return active_bonuses
    
    def _get_set_data(self, set_id: str) -> Optional[EquipmentSet]:
        set_data = {
            "immortal_king": EquipmentSet(
                id="immortal_king",
                name="不朽之王的呼唤",
                items=["immortal_king_helm", "immortal_king_chest", "immortal_king_gloves", 
                       "immortal_king_belt", "immortal_king_boots", "immortal_king_weapon"],
                bonuses=[
                    SetBonus(2, "不朽之力", "力量+100", {"strength": 100}),
                    SetBonus(3, "狂暴之心", "暴击伤害+30%", {"crit_damage": 30}),
                    SetBonus(4, "不朽意志", "所有抗性+50", {"all_resist": 50}),
                    SetBonus(5, "王者降临", "伤害+20%", {"damage_percent": 20}),
                    SetBonus(6, "不朽之王", "获得野蛮人所有技能+1等级", {"skill_level_barbarian": 1}),
                ]
            ),
            "tal_rasha": EquipmentSet(
                id="tal_rasha",
                name="塔拉夏的战衣",
                items=["tal_rasha_helm", "tal_rasha_chest", "tal_rasha_amulet", 
                       "tal_rasha_belt", "tal_rasha_orb"],
                bonuses=[
                    SetBonus(2, "元素协调", "所有元素伤害+15%", {"elemental_damage": 15}),
                    SetBonus(3, "奥术能量", "法术强度+50", {"spell_power": 50}),
                    SetBonus(4, "元素精通", "冰冷、火焰、闪电抗性+60", {"all_resist": 60}),
                    SetBonus(5, "大法师", "获得魔法师所有技能+1等级", {"skill_level_wizard": 1}),
                ]
            ),
            "natalya": EquipmentSet(
                id="natalya",
                name="娜塔亚的复仇",
                items=["natalya_helm", "natalya_chest", "natalya_gloves", 
                       "natalya_boots", "natalya_weapon"],
                bonuses=[
                    SetBonus(2, "暗影步", "移动速度+15%", {"movement_speed": 15}),
                    SetBonus(3, "致命精准", "暴击率+10%", {"crit_chance": 10}),
                    SetBonus(4, "暗影之力", "攻击力+25%", {"attack_power": 25}),
                    SetBonus(5, "猎魔大师", "获得猎魔人所有技能+1等级", {"skill_level_demon_hunter": 1}),
                ]
            ),
            "inarius": EquipmentSet(
                id="inarius",
                name="伊纳瑞斯的恩典",
                items=["inarius_helm", "inarius_chest", "inarius_gloves", 
                       "inarius_pants", "inarius_boots", "inarius_weapon"],
                bonuses=[
                    SetBonus(2, "骨甲", "护甲+150", {"armor": 150}),
                    SetBonus(3, "死亡之力", "死灵法术伤害+20%", {"necro_damage": 20}),
                    SetBonus(4, "灵魂收割", "生命偷取+5%", {"life_steal": 5}),
                    SetBonus(5, "白骨领主", "所有抗性+40", {"all_resist": 40}),
                    SetBonus(6, "伊纳瑞斯的祝福", "获得死灵法师所有技能+1等级", {"skill_level_necromancer": 1}),
                ]
            ),
            "sunwuko": EquipmentSet(
                id="sunwuko",
                name="孙吾空的战甲",
                items=["sunwuko_helm", "sunwuko_chest", "sunwuko_amulet", 
                       "sunwuko_gloves", "sunwuko_pants", "sunwuko_weapon"],
                bonuses=[
                    SetBonus(2, "灵光护体", "闪避+15%", {"dodge_chance": 15}),
                    SetBonus(3, "真言之力", "精神恢复+20%", {"spirit_regen": 20}),
                    SetBonus(4, "圣僧之道", "所有伤害+15%", {"damage_percent": 15}),
                    SetBonus(5, "武僧大师", "获得武僧所有技能+1等级", {"skill_level_monk": 1}),
                    SetBonus(6, "齐天大圣", "暴击伤害+50%", {"crit_damage": 50}),
                ]
            ),
            "akkhan": EquipmentSet(
                id="akkhan",
                name="阿克汉的战铠",
                items=["akkhan_helm", "akkhan_chest", "akkhan_gloves", 
                       "akkhan_pants", "akkhan_boots", "akkhan_weapon"],
                bonuses=[
                    SetBonus(2, "圣光护盾", "格挡+15%", {"block_chance": 15}),
                    SetBonus(3, "神圣之力", "神圣伤害+20%", {"holy_damage": 20}),
                    SetBonus(4, "圣教军之魂", "愤怒恢复+15%", {"wrath_regen": 15}),
                    SetBonus(5, "十字军", "所有抗性+50", {"all_resist": 50}),
                    SetBonus(6, "阿克汉的祝福", "获得圣教军所有技能+1等级", {"skill_level_crusader": 1}),
                ]
            ),
            "zunimassa": EquipmentSet(
                id="zunimassa",
                name="祖尼玛萨的萦绕",
                items=["zunimassa_helm", "zunimassa_chest", "zunimassa_amulet", 
                       "zunimassa_boots", "zunimassa_offhand"],
                bonuses=[
                    SetBonus(2, "自然之力", "宠物伤害+50%", {"pet_damage": 50}),
                    SetBonus(3, "灵魂链接", "生命+20%", {"max_health_percent": 20}),
                    SetBonus(4, "萨满之道", "法术强度+40", {"spell_power": 40}),
                    SetBonus(5, "德鲁伊大师", "获得德鲁伊所有技能+1等级", {"skill_level_druid": 1}),
                ]
            ),
            "shadow": EquipmentSet(
                id="shadow",
                name="暗影之装",
                items=["shadow_helm", "shadow_chest", "shadow_gloves", 
                       "shadow_pants", "shadow_boots", "shadow_weapon"],
                bonuses=[
                    SetBonus(2, "暗影步", "移动速度+20%", {"movement_speed": 20}),
                    SetBonus(3, "致命一击", "暴击率+12%", {"crit_chance": 12}),
                    SetBonus(4, "暗影之力", "暴击伤害+40%", {"crit_damage": 40}),
                    SetBonus(5, "刺客大师", "攻击速度+15%", {"attack_speed": 15}),
                    SetBonus(6, "暗影之王", "获得刺客所有技能+1等级", {"skill_level_assassin": 1}),
                ]
            ),
        }
        
        return set_data.get(set_id)
    
    def repair_all(self):
        for item in self.equipped.values():
            if item and hasattr(item, 'repair'):
                item.repair()
    
    def get_total_durability(self) -> Tuple[int, int]:
        total_current = 0
        total_max = 0
        
        for item in self.equipped.values():
            if item:
                total_current += item.durability
                total_max += item.max_durability
        
        return (total_current, total_max)
