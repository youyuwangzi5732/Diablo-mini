"""
物品基础类
"""
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random
import uuid

from .affix import Affix, AffixType, AffixGenerator


class ItemType(Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    ACCESSORY = "accessory"
    CONSUMABLE = "consumable"
    POTION = "potion"
    MATERIAL = "material"
    GEM = "gem"
    RUNE = "rune"


class ItemRarity(Enum):
    COMMON = 0
    MAGIC = 1
    RARE = 2
    LEGENDARY = 3
    SET = 4
    CRAFTED = 5


@dataclass
class ItemAffixInstance:
    affix: Affix
    value: float
    is_ancient: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "affix_id": self.affix.id,
            "value": self.value,
            "is_ancient": self.is_ancient
        }
    
    def get_effective_value(self) -> float:
        if self.is_ancient:
            return self.value * 1.3
        return self.value


@dataclass
class Item:
    id: str
    base_id: str
    name: str
    item_type: ItemType
    rarity: ItemRarity
    
    level: int = 1
    required_level: int = 1
    
    icon: str = ""
    description: str = ""
    
    max_stack: int = 1
    quantity: int = 1
    
    sockets: int = 0
    socketed_items: List[Any] = field(default_factory=list)
    
    affixes: List[ItemAffixInstance] = field(default_factory=list)
    implicit_affixes: List[ItemAffixInstance] = field(default_factory=list)
    
    is_identified: bool = True
    is_ancient: bool = False
    
    set_id: Optional[str] = None
    legendary_power: Optional[str] = None
    
    base_stats: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]
    
    def get_name_with_rarity(self) -> str:
        rarity_colors = {
            ItemRarity.COMMON: "",
            ItemRarity.MAGIC: "魔法 ",
            ItemRarity.RARE: "稀有 ",
            ItemRarity.LEGENDARY: "传奇 ",
            ItemRarity.SET: "套装 ",
            ItemRarity.CRAFTED: "合成 "
        }
        
        prefix = rarity_colors.get(self.rarity, "")
        ancient_prefix = "远古 " if self.is_ancient else ""
        
        return f"{ancient_prefix}{prefix}{self.name}"
    
    def get_total_stats(self) -> Dict[str, float]:
        stats = self.base_stats.copy()
        
        for affix_inst in self.implicit_affixes:
            attr = affix_inst.affix.attribute
            value = affix_inst.get_effective_value()
            if attr in stats:
                stats[attr] += value
            else:
                stats[attr] = value
        
        for affix_inst in self.affixes:
            attr = affix_inst.affix.attribute
            value = affix_inst.get_effective_value()
            if attr in stats:
                stats[attr] += value
            else:
                stats[attr] = value
        
        return stats
    
    def add_affix(self, affix: Affix, value: float, is_implicit: bool = False):
        instance = ItemAffixInstance(
            affix=affix,
            value=value,
            is_ancient=self.is_ancient
        )
        
        if is_implicit:
            self.implicit_affixes.append(instance)
        else:
            self.affixes.append(instance)
    
    def remove_affix(self, index: int) -> Optional[ItemAffixInstance]:
        if 0 <= index < len(self.affixes):
            return self.affixes.pop(index)
        return None
    
    def reroll_affix(self, index: int) -> bool:
        if 0 <= index < len(self.affixes):
            affix_inst = self.affixes[index]
            new_value = affix_inst.affix.generate_value()
            affix_inst.value = new_value
            return True
        return False
    
    def socket_item(self, item) -> bool:
        if len(self.socketed_items) >= self.sockets:
            return False
        
        self.socketed_items.append(item)
        return True
    
    def unsocket_item(self, index: int) -> Optional[Any]:
        if 0 <= index < len(self.socketed_items):
            return self.socketed_items.pop(index)
        return None
    
    def can_stack_with(self, other: 'Item') -> bool:
        if self.base_id != other.base_id:
            return False
        if self.rarity != other.rarity:
            return False
        if self.max_stack <= 1:
            return False
        if len(self.affixes) > 0 or len(other.affixes) > 0:
            return False
        
        return True
    
    def merge_stack(self, other: 'Item') -> bool:
        if not self.can_stack_with(other):
            return False
        
        total = self.quantity + other.quantity
        if total > self.max_stack:
            self.quantity = self.max_stack
            other.quantity = total - self.max_stack
        else:
            self.quantity = total
            other.quantity = 0
        
        return True
    
    def split_stack(self, count: int) -> Optional['Item']:
        if count >= self.quantity:
            return None
        
        new_item = Item(
            id="",
            base_id=self.base_id,
            name=self.name,
            item_type=self.item_type,
            rarity=self.rarity,
            level=self.level,
            required_level=self.required_level,
            icon=self.icon,
            max_stack=self.max_stack,
            quantity=count
        )
        
        self.quantity -= count
        return new_item
    
    def get_sell_value(self) -> int:
        base_value = self.level * 10
        
        rarity_multiplier = {
            ItemRarity.COMMON: 1,
            ItemRarity.MAGIC: 2,
            ItemRarity.RARE: 5,
            ItemRarity.LEGENDARY: 20,
            ItemRarity.SET: 15,
            ItemRarity.CRAFTED: 10
        }
        
        value = base_value * rarity_multiplier.get(self.rarity, 1)
        
        if self.is_ancient:
            value *= 2
        
        for socketed in self.socketed_items:
            if hasattr(socketed, 'get_sell_value'):
                value += socketed.get_sell_value()
        
        return int(value)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "base_id": self.base_id,
            "name": self.name,
            "item_type": self.item_type.value,
            "rarity": self.rarity.value,
            "level": self.level,
            "required_level": self.required_level,
            "icon": self.icon,
            "description": self.description,
            "max_stack": self.max_stack,
            "quantity": self.quantity,
            "sockets": self.sockets,
            "socketed_items": [s.to_dict() if hasattr(s, 'to_dict') else str(s) for s in self.socketed_items],
            "affixes": [a.to_dict() for a in self.affixes],
            "implicit_affixes": [a.to_dict() for a in self.implicit_affixes],
            "is_identified": self.is_identified,
            "is_ancient": self.is_ancient,
            "set_id": self.set_id,
            "legendary_power": self.legendary_power,
            "base_stats": self.base_stats
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Item':
        item = cls(
            id=data["id"],
            base_id=data["base_id"],
            name=data["name"],
            item_type=ItemType(data["item_type"]),
            rarity=ItemRarity(data["rarity"]),
            level=data.get("level", 1),
            required_level=data.get("required_level", 1),
            icon=data.get("icon", ""),
            description=data.get("description", ""),
            max_stack=data.get("max_stack", 1),
            quantity=data.get("quantity", 1),
            sockets=data.get("sockets", 0),
            is_identified=data.get("is_identified", True),
            is_ancient=data.get("is_ancient", False),
            set_id=data.get("set_id"),
            legendary_power=data.get("legendary_power"),
            base_stats=data.get("base_stats", {})
        )
        
        return item


class ItemFactory:
    _base_items: Dict[str, Dict[str, Any]] = {}
    _initialized = False
    
    @classmethod
    def initialize(cls):
        if cls._initialized:
            return
        
        cls._create_base_items()
        cls._initialized = True
    
    @classmethod
    def _create_base_items(cls):
        weapons = {
            "sword_1h": {
                "name": "长剑",
                "item_type": ItemType.WEAPON,
                "weapon_type": "sword",
                "two_handed": False,
                "base_damage": (10, 20),
                "attack_speed": 1.2,
                "sockets_range": (1, 3),
                "required_stats": {"strength": 10}
            },
            "axe_1h": {
                "name": "战斧",
                "item_type": ItemType.WEAPON,
                "weapon_type": "axe",
                "two_handed": False,
                "base_damage": (15, 30),
                "attack_speed": 1.0,
                "sockets_range": (1, 2),
                "required_stats": {"strength": 15}
            },
            "mace_1h": {
                "name": "钉头锤",
                "item_type": ItemType.WEAPON,
                "weapon_type": "mace",
                "two_handed": False,
                "base_damage": (12, 25),
                "attack_speed": 1.1,
                "sockets_range": (1, 2),
                "required_stats": {"strength": 12}
            },
            "dagger": {
                "name": "匕首",
                "item_type": ItemType.WEAPON,
                "weapon_type": "dagger",
                "two_handed": False,
                "base_damage": (5, 15),
                "attack_speed": 1.5,
                "sockets_range": (1, 2),
                "required_stats": {"dexterity": 10}
            },
            "staff": {
                "name": "法杖",
                "item_type": ItemType.WEAPON,
                "weapon_type": "staff",
                "two_handed": True,
                "base_damage": (8, 18),
                "attack_speed": 0.9,
                "sockets_range": (2, 4),
                "required_stats": {"intelligence": 15}
            },
            "wand": {
                "name": "魔杖",
                "item_type": ItemType.WEAPON,
                "weapon_type": "wand",
                "two_handed": False,
                "base_damage": (6, 12),
                "attack_speed": 1.3,
                "sockets_range": (1, 2),
                "required_stats": {"intelligence": 10}
            },
            "bow": {
                "name": "弓",
                "item_type": ItemType.WEAPON,
                "weapon_type": "bow",
                "two_handed": True,
                "base_damage": (10, 22),
                "attack_speed": 1.1,
                "sockets_range": (1, 3),
                "required_stats": {"dexterity": 15}
            },
            "crossbow": {
                "name": "弩",
                "item_type": ItemType.WEAPON,
                "weapon_type": "crossbow",
                "two_handed": True,
                "base_damage": (15, 35),
                "attack_speed": 0.8,
                "sockets_range": (1, 2),
                "required_stats": {"dexterity": 20}
            },
        }
        
        armor = {
            "helmet_heavy": {
                "name": "重型头盔",
                "item_type": ItemType.ARMOR,
                "armor_type": "heavy",
                "slot": "head",
                "base_armor": 50,
                "sockets_range": (1, 2),
                "required_stats": {"strength": 20}
            },
            "helmet_light": {
                "name": "轻型头盔",
                "item_type": ItemType.ARMOR,
                "armor_type": "light",
                "slot": "head",
                "base_armor": 25,
                "sockets_range": (1, 2),
                "required_stats": {"dexterity": 10}
            },
            "chest_heavy": {
                "name": "重型胸甲",
                "item_type": ItemType.ARMOR,
                "armor_type": "heavy",
                "slot": "chest",
                "base_armor": 150,
                "sockets_range": (2, 4),
                "required_stats": {"strength": 30}
            },
            "chest_light": {
                "name": "轻型胸甲",
                "item_type": ItemType.ARMOR,
                "armor_type": "light",
                "slot": "chest",
                "base_armor": 75,
                "sockets_range": (2, 3),
                "required_stats": {"dexterity": 15}
            },
            "gloves_heavy": {
                "name": "重型手套",
                "item_type": ItemType.ARMOR,
                "armor_type": "heavy",
                "slot": "hands",
                "base_armor": 30,
                "sockets_range": (1, 2),
                "required_stats": {"strength": 15}
            },
            "boots_heavy": {
                "name": "重型靴子",
                "item_type": ItemType.ARMOR,
                "armor_type": "heavy",
                "slot": "feet",
                "base_armor": 40,
                "sockets_range": (1, 2),
                "required_stats": {"strength": 15}
            },
            "shoulders_heavy": {
                "name": "重型护肩",
                "item_type": ItemType.ARMOR,
                "armor_type": "heavy",
                "slot": "shoulders",
                "base_armor": 45,
                "sockets_range": (1, 2),
                "required_stats": {"strength": 18}
            },
            "belt_heavy": {
                "name": "重型腰带",
                "item_type": ItemType.ARMOR,
                "armor_type": "heavy",
                "slot": "waist",
                "base_armor": 35,
                "sockets_range": (1, 2),
                "required_stats": {"strength": 15}
            },
            "legs_heavy": {
                "name": "重型护腿",
                "item_type": ItemType.ARMOR,
                "armor_type": "heavy",
                "slot": "legs",
                "base_armor": 80,
                "sockets_range": (2, 3),
                "required_stats": {"strength": 25}
            },
        }
        
        accessories = {
            "ring": {
                "name": "戒指",
                "item_type": ItemType.ACCESSORY,
                "slot": "ring",
                "sockets_range": (0, 1)
            },
            "amulet": {
                "name": "护身符",
                "item_type": ItemType.ACCESSORY,
                "slot": "neck",
                "sockets_range": (0, 1)
            },
        }
        
        cls._base_items.update(weapons)
        cls._base_items.update(armor)
        cls._base_items.update(accessories)
    
    @classmethod
    def create_item(cls, base_id: str, level: int = 1, 
                    rarity: ItemRarity = None) -> Optional[Item]:
        if not cls._initialized:
            cls.initialize()
        
        base_data = cls._base_items.get(base_id)
        if not base_data:
            return None
        
        if rarity is None:
            rarity = cls._roll_rarity()
        
        item = Item(
            id="",
            base_id=base_id,
            name=base_data["name"],
            item_type=ItemType(base_data["item_type"].value) if hasattr(base_data["item_type"], 'value') else ItemType(base_data["item_type"]),
            rarity=rarity,
            level=level,
            required_level=level
        )
        
        if "base_damage" in base_data:
            min_dmg, max_dmg = base_data["base_damage"]
            scaled_min = min_dmg * (1 + level * 0.1)
            scaled_max = max_dmg * (1 + level * 0.1)
            item.base_stats["min_damage"] = scaled_min
            item.base_stats["max_damage"] = scaled_max
        
        if "base_armor" in base_data:
            scaled_armor = base_data["base_armor"] * (1 + level * 0.05)
            item.base_stats["armor"] = scaled_armor
        
        if "attack_speed" in base_data:
            item.base_stats["attack_speed"] = base_data["attack_speed"]
        
        sockets_range = base_data.get("sockets_range", (0, 0))
        item.sockets = random.randint(sockets_range[0], sockets_range[1])
        
        if rarity != ItemRarity.COMMON:
            cls._add_affixes(item, level, rarity)
        
        if rarity in [ItemRarity.LEGENDARY, ItemRarity.SET]:
            if random.random() < 0.1:
                item.is_ancient = True
        
        return item
    
    @classmethod
    def _roll_rarity(cls) -> ItemRarity:
        weights = [70, 20, 7, 2, 1, 0]
        roll = random.random() * 100
        cumulative = 0
        
        for i, weight in enumerate(weights):
            cumulative += weight
            if roll < cumulative:
                return ItemRarity(i)
        
        return ItemRarity.COMMON
    
    @classmethod
    def _add_affixes(cls, item: Item, level: int, rarity: ItemRarity):
        AffixGenerator.initialize()
        
        if rarity == ItemRarity.MAGIC:
            affixes = AffixGenerator.roll_affixes(level, 1)
            for affix, value in affixes:
                item.add_affix(affix, value)
        
        elif rarity == ItemRarity.RARE:
            affixes = AffixGenerator.roll_affixes(level, 2)
            for affix, value in affixes:
                item.add_affix(affix, value)
        
        elif rarity == ItemRarity.LEGENDARY:
            normal_affixes = AffixGenerator.roll_affixes(level, 2, 3)
            for affix, value in normal_affixes:
                item.add_affix(affix, value)
            
            legendary_affixes = AffixGenerator.roll_legendary_affixes(level, 2)
            for affix, value in legendary_affixes:
                item.add_affix(affix, value)
        
        elif rarity == ItemRarity.SET:
            affixes = AffixGenerator.roll_affixes(level, 2, 4)
            for affix, value in affixes:
                item.add_affix(affix, value)
        
        elif rarity == ItemRarity.CRAFTED:
            affixes = AffixGenerator.roll_affixes(level, 2, 4)
            for affix, value in affixes:
                item.add_affix(affix, value)
    
    @classmethod
    def get_base_item_ids(cls) -> List[str]:
        if not cls._initialized:
            cls.initialize()
        return list(cls._base_items.keys())
    
    @classmethod
    def get_base_item_data(cls, base_id: str) -> Optional[Dict[str, Any]]:
        if not cls._initialized:
            cls.initialize()
        return cls._base_items.get(base_id)
