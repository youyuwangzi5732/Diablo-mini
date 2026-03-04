"""
词缀系统 - 装备属性生成
"""
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random


class AffixType(Enum):
    PREFIX = "prefix"
    SUFFIX = "suffix"
    IMPLICIT = "implicit"
    LEGENDARY = "legendary"
    SET = "set"
    ENCHANTED = "enchanted"


@dataclass
class AffixRange:
    min_value: float
    max_value: float
    
    def roll(self) -> float:
        return random.uniform(self.min_value, self.max_value)


@dataclass
class Affix:
    id: str
    name: str
    type: AffixType
    attribute: str
    value_range: AffixRange
    is_percentage: bool = False
    required_level: int = 1
    item_level_requirement: int = 1
    weight: int = 100
    groups: List[str] = field(default_factory=list)
    
    def generate_value(self) -> float:
        return self.value_range.roll()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "attribute": self.attribute,
            "value_range": {
                "min": self.value_range.min_value,
                "max": self.value_range.max_value
            },
            "is_percentage": self.is_percentage,
            "required_level": self.required_level
        }


class AffixGenerator:
    _prefixes: Dict[str, Affix] = {}
    _suffixes: Dict[str, Affix] = {}
    _legendary_affixes: Dict[str, Affix] = {}
    _set_affixes: Dict[str, Affix] = {}
    _initialized = False
    
    @classmethod
    def initialize(cls):
        if cls._initialized:
            return
        
        cls._create_default_affixes()
        cls._initialized = True
    
    @classmethod
    def _create_default_affixes(cls):
        prefix_affixes = [
            Affix(
                id="strength_prefix",
                name="强壮的",
                type=AffixType.PREFIX,
                attribute="strength",
                value_range=AffixRange(10, 50),
                required_level=1,
                weight=100
            ),
            Affix(
                id="dexterity_prefix",
                name="敏捷的",
                type=AffixType.PREFIX,
                attribute="dexterity",
                value_range=AffixRange(10, 50),
                required_level=1,
                weight=100
            ),
            Affix(
                id="intelligence_prefix",
                name="智慧的",
                type=AffixType.PREFIX,
                attribute="intelligence",
                value_range=AffixRange(10, 50),
                required_level=1,
                weight=100
            ),
            Affix(
                id="vitality_prefix",
                name="活力的",
                type=AffixType.PREFIX,
                attribute="vitality",
                value_range=AffixRange(10, 50),
                required_level=1,
                weight=100
            ),
            Affix(
                id="attack_power_prefix",
                name="强力的",
                type=AffixType.PREFIX,
                attribute="attack_power",
                value_range=AffixRange(20, 100),
                required_level=10,
                weight=80
            ),
            Affix(
                id="spell_power_prefix",
                name="魔力的",
                type=AffixType.PREFIX,
                attribute="spell_power",
                value_range=AffixRange(20, 100),
                required_level=10,
                weight=80
            ),
            Affix(
                id="armor_prefix",
                name="坚固的",
                type=AffixType.PREFIX,
                attribute="armor",
                value_range=AffixRange(50, 200),
                required_level=5,
                weight=90
            ),
        ]
        
        suffix_affixes = [
            Affix(
                id="crit_chance_suffix",
                name="暴击",
                type=AffixType.SUFFIX,
                attribute="crit_chance",
                value_range=AffixRange(1, 6),
                is_percentage=True,
                required_level=15,
                weight=60
            ),
            Affix(
                id="crit_damage_suffix",
                name="暴击伤害",
                type=AffixType.SUFFIX,
                attribute="crit_damage",
                value_range=AffixRange(10, 50),
                is_percentage=True,
                required_level=20,
                weight=50
            ),
            Affix(
                id="attack_speed_suffix",
                name="攻击速度",
                type=AffixType.SUFFIX,
                attribute="attack_speed",
                value_range=AffixRange(3, 15),
                is_percentage=True,
                required_level=10,
                weight=70
            ),
            Affix(
                id="life_steal_suffix",
                name="生命偷取",
                type=AffixType.SUFFIX,
                attribute="life_steal",
                value_range=AffixRange(1, 5),
                is_percentage=True,
                required_level=25,
                weight=40
            ),
            Affix(
                id="fire_resist_suffix",
                name="火焰抗性",
                type=AffixType.SUFFIX,
                attribute="fire_resist",
                value_range=AffixRange(5, 20),
                is_percentage=True,
                required_level=1,
                weight=100
            ),
            Affix(
                id="cold_resist_suffix",
                name="冰冷抗性",
                type=AffixType.SUFFIX,
                attribute="cold_resist",
                value_range=AffixRange(5, 20),
                is_percentage=True,
                required_level=1,
                weight=100
            ),
            Affix(
                id="lightning_resist_suffix",
                name="闪电抗性",
                type=AffixType.SUFFIX,
                attribute="lightning_resist",
                value_range=AffixRange(5, 20),
                is_percentage=True,
                required_level=1,
                weight=100
            ),
            Affix(
                id="poison_resist_suffix",
                name="毒素抗性",
                type=AffixType.SUFFIX,
                attribute="poison_resist",
                value_range=AffixRange(5, 20),
                is_percentage=True,
                required_level=1,
                weight=100
            ),
            Affix(
                id="health_regen_suffix",
                name="生命回复",
                type=AffixType.SUFFIX,
                attribute="health_regen",
                value_range=AffixRange(100, 500),
                required_level=5,
                weight=80
            ),
            Affix(
                id="magic_find_suffix",
                name="魔法寻找",
                type=AffixType.SUFFIX,
                attribute="magic_find",
                value_range=AffixRange(5, 25),
                is_percentage=True,
                required_level=15,
                weight=50
            ),
            Affix(
                id="gold_find_suffix",
                name="金币获取",
                type=AffixType.SUFFIX,
                attribute="gold_find",
                value_range=AffixRange(10, 50),
                is_percentage=True,
                required_level=1,
                weight=90
            ),
        ]
        
        legendary_affixes = [
            Affix(
                id="legendary_fire_damage",
                name="火焰伤害",
                type=AffixType.LEGENDARY,
                attribute="fire_damage_percent",
                value_range=AffixRange(15, 30),
                is_percentage=True,
                required_level=30,
                weight=20
            ),
            Affix(
                id="legendary_skill_damage",
                name="技能伤害",
                type=AffixType.LEGENDARY,
                attribute="skill_damage_percent",
                value_range=AffixRange(10, 25),
                is_percentage=True,
                required_level=40,
                weight=15
            ),
            Affix(
                id="legendary_cooldown_reduction",
                name="冷却缩减",
                type=AffixType.LEGENDARY,
                attribute="cooldown_reduction",
                value_range=AffixRange(8, 15),
                is_percentage=True,
                required_level=35,
                weight=25
            ),
            Affix(
                id="legendary_resource_cost",
                name="资源消耗降低",
                type=AffixType.LEGENDARY,
                attribute="resource_cost_reduction",
                value_range=AffixRange(5, 12),
                is_percentage=True,
                required_level=30,
                weight=20
            ),
        ]
        
        for affix in prefix_affixes:
            cls._prefixes[affix.id] = affix
        for affix in suffix_affixes:
            cls._suffixes[affix.id] = affix
        for affix in legendary_affixes:
            cls._legendary_affixes[affix.id] = affix
    
    @classmethod
    def get_prefix(cls, affix_id: str) -> Optional[Affix]:
        if not cls._initialized:
            cls.initialize()
        return cls._prefixes.get(affix_id)
    
    @classmethod
    def get_suffix(cls, affix_id: str) -> Optional[Affix]:
        if not cls._initialized:
            cls.initialize()
        return cls._suffixes.get(affix_id)
    
    @classmethod
    def get_legendary_affix(cls, affix_id: str) -> Optional[Affix]:
        if not cls._initialized:
            cls.initialize()
        return cls._legendary_affixes.get(affix_id)
    
    @classmethod
    def roll_affixes(cls, item_level: int, rarity: int, 
                     count: int = None) -> List[Tuple[Affix, float]]:
        if not cls._initialized:
            cls.initialize()
        
        affixes = []
        
        if rarity == 0:
            return affixes
        elif rarity == 1:
            num_affixes = count or random.randint(1, 2)
        elif rarity == 2:
            num_affixes = count or random.randint(3, 4)
        elif rarity == 3:
            num_affixes = count or random.randint(4, 6)
        elif rarity == 4:
            num_affixes = count or random.randint(4, 6)
        else:
            num_affixes = count or 4
        
        available_prefixes = [
            a for a in cls._prefixes.values()
            if a.required_level <= item_level
        ]
        available_suffixes = [
            a for a in cls._suffixes.values()
            if a.required_level <= item_level
        ]
        
        num_prefixes = num_affixes // 2 + random.randint(0, 1)
        num_suffixes = num_affixes - num_prefixes
        
        if available_prefixes and num_prefixes > 0:
            selected = random.choices(
                available_prefixes,
                weights=[a.weight for a in available_prefixes],
                k=min(num_prefixes, len(available_prefixes))
            )
            for affix in selected:
                value = affix.generate_value()
                affixes.append((affix, value))
        
        if available_suffixes and num_suffixes > 0:
            selected = random.choices(
                available_suffixes,
                weights=[a.weight for a in available_suffixes],
                k=min(num_suffixes, len(available_suffixes))
            )
            for affix in selected:
                value = affix.generate_value()
                affixes.append((affix, value))
        
        return affixes
    
    @classmethod
    def roll_legendary_affixes(cls, item_level: int, 
                                count: int = 2) -> List[Tuple[Affix, float]]:
        if not cls._initialized:
            cls.initialize()
        
        available = [
            a for a in cls._legendary_affixes.values()
            if a.required_level <= item_level
        ]
        
        if not available:
            return []
        
        selected = random.choices(
            available,
            weights=[a.weight for a in available],
            k=min(count, len(available))
        )
        
        return [(affix, affix.generate_value()) for affix in selected]
