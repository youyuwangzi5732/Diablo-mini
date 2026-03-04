"""
词缀池系统 - 商业化级别的装备属性生成
支持分层配置、赛季切换、权重调整
"""
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import random
import json


class AffixType(Enum):
    PREFIX = "prefix"
    SUFFIX = "suffix"
    IMPLICIT = "implicit"
    LEGENDARY = "legendary"
    SET = "set"
    ENCHANTED = "enchanted"
    ANCIENT = "ancient"
    PRIMAL = "primal"


class AffixTier(Enum):
    TIER_1 = 1   # 最差
    TIER_2 = 2
    TIER_3 = 3
    TIER_4 = 4
    TIER_5 = 5   # 最好


class AffixCategory(Enum):
    OFFENSE = "offense"
    DEFENSE = "defense"
    UTILITY = "utility"
    RESOURCE = "resource"
    SPECIAL = "special"


@dataclass
class AffixRange:
    min_value: float
    max_value: float
    tier_multiplier: float = 1.0
    
    def roll(self, tier: AffixTier = AffixTier.TIER_3) -> float:
        base = random.uniform(self.min_value, self.max_value)
        tier_mult = {
            AffixTier.TIER_1: 0.6,
            AffixTier.TIER_2: 0.8,
            AffixTier.TIER_3: 1.0,
            AffixTier.TIER_4: 1.2,
            AffixTier.TIER_5: 1.5,
        }
        return base * tier_mult.get(tier, 1.0) * self.tier_multiplier


@dataclass
class AffixDefinition:
    id: str
    name: str
    type: AffixType
    category: AffixCategory
    attribute: str
    value_range: AffixRange
    is_percentage: bool = False
    required_level: int = 1
    item_level_requirement: int = 1
    weight: int = 100
    groups: List[str] = field(default_factory=list)
    allowed_item_types: List[str] = field(default_factory=list)
    excluded_item_types: List[str] = field(default_factory=list)
    season_id: str = ""
    max_stack: int = 1
    description_template: str = ""
    
    def generate_value(self, tier: AffixTier = AffixTier.TIER_3) -> float:
        return self.value_range.roll(tier)
    
    def format_description(self, value: float) -> str:
        if self.description_template:
            if self.is_percentage:
                return self.description_template.format(value=f"{value:.1f}%")
            return self.description_template.format(value=f"{int(value)}")
        
        if self.is_percentage:
            return f"+{value:.1f}% {self.name}"
        return f"+{int(value)} {self.name}"
    
    def can_apply_to(self, item_type: str) -> bool:
        if self.allowed_item_types and item_type not in self.allowed_item_types:
            return False
        if item_type in self.excluded_item_types:
            return False
        return True


@dataclass
class AffixPool:
    """词缀池 - 管理一组相关词缀"""
    id: str
    name: str
    affix_ids: List[str]
    total_weight: int = 0
    season_id: str = ""
    
    def calculate_weight(self, affixes: Dict[str, AffixDefinition]):
        self.total_weight = sum(
            affixes.get(aid, AffixDefinition(id="", name="", type=AffixType.PREFIX, 
                                             category=AffixCategory.OFFENSE, attribute="", 
                                             value_range=AffixRange(0, 1))).weight
            for aid in self.affix_ids
        )


class AffixPoolManager:
    """词缀池管理器"""
    
    # 词缀定义数据库
    AFFIX_DEFINITIONS: Dict[str, AffixDefinition] = {}
    
    # 词缀池配置
    AFFIX_POOLS: Dict[str, AffixPool] = {}
    
    # 物品类型词缀池映射
    ITEM_AFFIX_POOLS: Dict[str, List[str]] = {}
    
    # 稀有度词缀数量配置
    RARITY_AFFIX_COUNT = {
        "common": {"prefix": 0, "suffix": 0},
        "magic": {"prefix": (1, 2), "suffix": (1, 2)},
        "rare": {"prefix": (2, 3), "suffix": (2, 3)},
        "legendary": {"prefix": (1, 2), "suffix": (1, 2), "legendary": 1},
        "set": {"prefix": (1, 2), "suffix": (1, 2), "set": 1},
        "crafted": {"prefix": (2, 4), "suffix": (2, 4)},
    }
    
    _initialized = False
    _current_season = "default"
    
    @classmethod
    def initialize(cls):
        if cls._initialized:
            return
        
        cls._create_affix_definitions()
        cls._create_affix_pools()
        cls._create_item_mappings()
        cls._initialized = True
    
    @classmethod
    def _create_affix_definitions(cls):
        """创建词缀定义"""
        # ========== 前缀词缀 ==========
        prefix_affixes = [
            # 主属性类
            AffixDefinition(
                id="prefix_strength",
                name="力量",
                type=AffixType.PREFIX,
                category=AffixCategory.OFFENSE,
                attribute="strength",
                value_range=AffixRange(10, 100),
                required_level=1,
                weight=100,
                groups=["primary_stat"],
                description_template="+{value} 力量"
            ),
            AffixDefinition(
                id="prefix_dexterity",
                name="敏捷",
                type=AffixType.PREFIX,
                category=AffixCategory.OFFENSE,
                attribute="dexterity",
                value_range=AffixRange(10, 100),
                required_level=1,
                weight=100,
                groups=["primary_stat"],
                description_template="+{value} 敏捷"
            ),
            AffixDefinition(
                id="prefix_intelligence",
                name="智力",
                type=AffixType.PREFIX,
                category=AffixCategory.OFFENSE,
                attribute="intelligence",
                value_range=AffixRange(10, 100),
                required_level=1,
                weight=100,
                groups=["primary_stat"],
                description_template="+{value} 智力"
            ),
            AffixDefinition(
                id="prefix_vitality",
                name="体质",
                type=AffixType.PREFIX,
                category=AffixCategory.DEFENSE,
                attribute="vitality",
                value_range=AffixRange(10, 100),
                required_level=1,
                weight=100,
                groups=["primary_stat"],
                description_template="+{value} 体质"
            ),
            AffixDefinition(
                id="prefix_all_stats",
                name="全属性",
                type=AffixType.PREFIX,
                category=AffixCategory.OFFENSE,
                attribute="all_stats",
                value_range=AffixRange(5, 50),
                required_level=30,
                weight=30,
                groups=["primary_stat"],
                description_template="+{value} 全属性"
            ),
            
            # 伤害类
            AffixDefinition(
                id="prefix_damage",
                name="伤害",
                type=AffixType.PREFIX,
                category=AffixCategory.OFFENSE,
                attribute="damage",
                value_range=AffixRange(5, 50),
                required_level=1,
                weight=80,
                groups=["damage"],
                allowed_item_types=["weapon"],
                description_template="+{value} 伤害"
            ),
            AffixDefinition(
                id="prefix_damage_percent",
                name="伤害百分比",
                type=AffixType.PREFIX,
                category=AffixCategory.OFFENSE,
                attribute="damage_percent",
                value_range=AffixRange(5, 30),
                is_percentage=True,
                required_level=20,
                weight=50,
                groups=["damage"],
                allowed_item_types=["weapon"],
                description_template="+{value} 伤害"
            ),
            AffixDefinition(
                id="prefix_critical_chance",
                name="暴击率",
                type=AffixType.PREFIX,
                category=AffixCategory.OFFENSE,
                attribute="critical_chance",
                value_range=AffixRange(1, 10),
                is_percentage=True,
                required_level=10,
                weight=60,
                groups=["critical"],
                description_template="+{value} 暴击率"
            ),
            AffixDefinition(
                id="prefix_critical_damage",
                name="暴击伤害",
                type=AffixType.PREFIX,
                category=AffixCategory.OFFENSE,
                attribute="critical_damage",
                value_range=AffixRange(10, 100),
                is_percentage=True,
                required_level=15,
                weight=50,
                groups=["critical"],
                description_template="+{value} 暴击伤害"
            ),
            AffixDefinition(
                id="prefix_attack_speed",
                name="攻击速度",
                type=AffixType.PREFIX,
                category=AffixCategory.OFFENSE,
                attribute="attack_speed",
                value_range=AffixRange(3, 20),
                is_percentage=True,
                required_level=10,
                weight=40,
                groups=["speed"],
                allowed_item_types=["weapon", "gloves"],
                description_template="+{value} 攻击速度"
            ),
            
            # 元素伤害类
            AffixDefinition(
                id="prefix_fire_damage",
                name="火焰伤害",
                type=AffixType.PREFIX,
                category=AffixCategory.OFFENSE,
                attribute="fire_damage",
                value_range=AffixRange(10, 100),
                required_level=1,
                weight=70,
                groups=["elemental_damage", "fire"],
                description_template="+{value} 火焰伤害"
            ),
            AffixDefinition(
                id="prefix_cold_damage",
                name="冰霜伤害",
                type=AffixType.PREFIX,
                category=AffixCategory.OFFENSE,
                attribute="cold_damage",
                value_range=AffixRange(10, 100),
                required_level=1,
                weight=70,
                groups=["elemental_damage", "cold"],
                description_template="+{value} 冰霜伤害"
            ),
            AffixDefinition(
                id="prefix_lightning_damage",
                name="闪电伤害",
                type=AffixType.PREFIX,
                category=AffixCategory.OFFENSE,
                attribute="lightning_damage",
                value_range=AffixRange(10, 100),
                required_level=1,
                weight=70,
                groups=["elemental_damage", "lightning"],
                description_template="+{value} 闪电伤害"
            ),
            AffixDefinition(
                id="prefix_poison_damage",
                name="毒素伤害",
                type=AffixType.PREFIX,
                category=AffixCategory.OFFENSE,
                attribute="poison_damage",
                value_range=AffixRange(10, 100),
                required_level=1,
                weight=70,
                groups=["elemental_damage", "poison"],
                description_template="+{value} 毒素伤害"
            ),
            
            # 防御类
            AffixDefinition(
                id="prefix_armor",
                name="护甲",
                type=AffixType.PREFIX,
                category=AffixCategory.DEFENSE,
                attribute="armor",
                value_range=AffixRange(20, 200),
                required_level=1,
                weight=90,
                groups=["defense"],
                excluded_item_types=["weapon"],
                description_template="+{value} 护甲"
            ),
            AffixDefinition(
                id="prefix_armor_percent",
                name="护甲百分比",
                type=AffixType.PREFIX,
                category=AffixCategory.DEFENSE,
                attribute="armor_percent",
                value_range=AffixRange(3, 20),
                is_percentage=True,
                required_level=20,
                weight=40,
                groups=["defense"],
                excluded_item_types=["weapon"],
                description_template="+{value} 护甲"
            ),
            AffixDefinition(
                id="prefix_block_chance",
                name="格挡率",
                type=AffixType.PREFIX,
                category=AffixCategory.DEFENSE,
                attribute="block_chance",
                value_range=AffixRange(1, 10),
                is_percentage=True,
                required_level=10,
                weight=30,
                groups=["defense", "block"],
                allowed_item_types=["shield", "off_hand"],
                description_template="+{value} 格挡率"
            ),
            AffixDefinition(
                id="prefix_dodge_chance",
                name="闪避率",
                type=AffixType.PREFIX,
                category=AffixCategory.DEFENSE,
                attribute="dodge_chance",
                value_range=AffixRange(1, 8),
                is_percentage=True,
                required_level=15,
                weight=25,
                groups=["defense", "dodge"],
                description_template="+{value} 闪避率"
            ),
        ]
        
        # ========== 后缀词缀 ==========
        suffix_affixes = [
            # 生命和资源
            AffixDefinition(
                id="suffix_health",
                name="生命值",
                type=AffixType.SUFFIX,
                category=AffixCategory.DEFENSE,
                attribute="max_health",
                value_range=AffixRange(20, 200),
                required_level=1,
                weight=100,
                groups=["health"],
                description_template="+{value} 生命值"
            ),
            AffixDefinition(
                id="suffix_health_percent",
                name="生命值百分比",
                type=AffixType.SUFFIX,
                category=AffixCategory.DEFENSE,
                attribute="max_health_percent",
                value_range=AffixRange(3, 15),
                is_percentage=True,
                required_level=25,
                weight=40,
                groups=["health"],
                description_template="+{value} 生命值"
            ),
            AffixDefinition(
                id="suffix_mana",
                name="法力值",
                type=AffixType.SUFFIX,
                category=AffixCategory.RESOURCE,
                attribute="max_resource",
                value_range=AffixRange(10, 100),
                required_level=1,
                weight=80,
                groups=["resource"],
                description_template="+{value} 法力值"
            ),
            AffixDefinition(
                id="suffix_mana_regen",
                name="法力回复",
                type=AffixType.SUFFIX,
                category=AffixCategory.RESOURCE,
                attribute="resource_regen",
                value_range=AffixRange(1, 10),
                required_level=10,
                weight=60,
                groups=["resource"],
                description_template="+{value} 法力回复/秒"
            ),
            AffixDefinition(
                id="suffix_health_regen",
                name="生命回复",
                type=AffixType.SUFFIX,
                category=AffixCategory.DEFENSE,
                attribute="health_regen",
                value_range=AffixRange(5, 50),
                required_level=10,
                weight=70,
                groups=["health"],
                description_template="+{value} 生命回复/秒"
            ),
            
            # 抗性类
            AffixDefinition(
                id="suffix_fire_resist",
                name="火焰抗性",
                type=AffixType.SUFFIX,
                category=AffixCategory.DEFENSE,
                attribute="fire_resistance",
                value_range=AffixRange(5, 40),
                is_percentage=True,
                required_level=1,
                weight=80,
                groups=["resistance", "fire"],
                description_template="+{value} 火焰抗性"
            ),
            AffixDefinition(
                id="suffix_cold_resist",
                name="冰霜抗性",
                type=AffixType.SUFFIX,
                category=AffixCategory.DEFENSE,
                attribute="cold_resistance",
                value_range=AffixRange(5, 40),
                is_percentage=True,
                required_level=1,
                weight=80,
                groups=["resistance", "cold"],
                description_template="+{value} 冰霜抗性"
            ),
            AffixDefinition(
                id="suffix_lightning_resist",
                name="闪电抗性",
                type=AffixType.SUFFIX,
                category=AffixCategory.DEFENSE,
                attribute="lightning_resistance",
                value_range=AffixRange(5, 40),
                is_percentage=True,
                required_level=1,
                weight=80,
                groups=["resistance", "lightning"],
                description_template="+{value} 闪电抗性"
            ),
            AffixDefinition(
                id="suffix_poison_resist",
                name="毒素抗性",
                type=AffixType.SUFFIX,
                category=AffixCategory.DEFENSE,
                attribute="poison_resistance",
                value_range=AffixRange(5, 40),
                is_percentage=True,
                required_level=1,
                weight=80,
                groups=["resistance", "poison"],
                description_template="+{value} 毒素抗性"
            ),
            AffixDefinition(
                id="suffix_all_resist",
                name="全抗性",
                type=AffixType.SUFFIX,
                category=AffixCategory.DEFENSE,
                attribute="all_resistance",
                value_range=AffixRange(3, 20),
                is_percentage=True,
                required_level=30,
                weight=30,
                groups=["resistance"],
                description_template="+{value} 全抗性"
            ),
            
            # 实用类
            AffixDefinition(
                id="suffix_gold_find",
                name="金币获取",
                type=AffixType.SUFFIX,
                category=AffixCategory.UTILITY,
                attribute="gold_find",
                value_range=AffixRange(5, 50),
                is_percentage=True,
                required_level=1,
                weight=70,
                groups=["utility", "gold"],
                description_template="+{value} 金币获取"
            ),
            AffixDefinition(
                id="suffix_magic_find",
                name="魔法获取",
                type=AffixType.SUFFIX,
                category=AffixCategory.UTILITY,
                attribute="magic_find",
                value_range=AffixRange(3, 30),
                is_percentage=True,
                required_level=10,
                weight=50,
                groups=["utility", "mf"],
                description_template="+{value} 魔法获取"
            ),
            AffixDefinition(
                id="suffix_experience",
                name="经验获取",
                type=AffixType.SUFFIX,
                category=AffixCategory.UTILITY,
                attribute="experience_bonus",
                value_range=AffixRange(2, 15),
                is_percentage=True,
                required_level=15,
                weight=40,
                groups=["utility", "exp"],
                description_template="+{value} 经验获取"
            ),
            AffixDefinition(
                id="suffix_movement_speed",
                name="移动速度",
                type=AffixType.SUFFIX,
                category=AffixCategory.UTILITY,
                attribute="movement_speed",
                value_range=AffixRange(3, 15),
                is_percentage=True,
                required_level=10,
                weight=30,
                groups=["utility", "speed"],
                allowed_item_types=["boots"],
                description_template="+{value} 移动速度"
            ),
            AffixDefinition(
                id="suffix_thorns",
                name="反伤",
                type=AffixType.SUFFIX,
                category=AffixCategory.DEFENSE,
                attribute="thorns",
                value_range=AffixRange(10, 100),
                required_level=10,
                weight=50,
                groups=["defense", "thorns"],
                description_template="+{value} 反伤"
            ),
        ]
        
        # ========== 传奇词缀 ==========
        legendary_affixes = [
            AffixDefinition(
                id="legendary_damage_reduction",
                name="伤害减免",
                type=AffixType.LEGENDARY,
                category=AffixCategory.DEFENSE,
                attribute="damage_reduction",
                value_range=AffixRange(5, 20),
                is_percentage=True,
                required_level=50,
                weight=20,
                groups=["legendary", "defense"],
                description_template="受到的伤害减少 {value}"
            ),
            AffixDefinition(
                id="legendary_skill_damage",
                name="技能伤害加成",
                type=AffixType.LEGENDARY,
                category=AffixCategory.OFFENSE,
                attribute="skill_damage_bonus",
                value_range=AffixRange(10, 50),
                is_percentage=True,
                required_level=50,
                weight=20,
                groups=["legendary", "skill"],
                description_template="技能伤害提高 {value}"
            ),
            AffixDefinition(
                id="legendary_resource_cost",
                name="资源消耗降低",
                type=AffixType.LEGENDARY,
                category=AffixCategory.RESOURCE,
                attribute="resource_cost_reduction",
                value_range=AffixRange(10, 30),
                is_percentage=True,
                required_level=50,
                weight=15,
                groups=["legendary", "resource"],
                description_template="技能资源消耗降低 {value}"
            ),
            AffixDefinition(
                id="legendary_cooldown",
                name="冷却缩减",
                type=AffixType.LEGENDARY,
                category=AffixCategory.OFFENSE,
                attribute="cooldown_reduction",
                value_range=AffixRange(5, 20),
                is_percentage=True,
                required_level=50,
                weight=15,
                groups=["legendary", "cooldown"],
                description_template="技能冷却时间减少 {value}"
            ),
            AffixDefinition(
                id="legendary_life_per_hit",
                name="击中回复",
                type=AffixType.LEGENDARY,
                category=AffixCategory.DEFENSE,
                attribute="life_per_hit",
                value_range=AffixRange(100, 500),
                required_level=50,
                weight=20,
                groups=["legendary", "life"],
                description_template="每次击中回复 {value} 点生命"
            ),
            AffixDefinition(
                id="legendary_critical_damage",
                name="暴击伤害加成",
                type=AffixType.LEGENDARY,
                category=AffixCategory.OFFENSE,
                attribute="critical_damage_bonus",
                value_range=AffixRange(50, 150),
                is_percentage=True,
                required_level=50,
                weight=15,
                groups=["legendary", "critical"],
                description_template="暴击伤害提高 {value}"
            ),
        ]
        
        # 注册所有词缀
        for affix in prefix_affixes + suffix_affixes + legendary_affixes:
            cls.AFFIX_DEFINITIONS[affix.id] = affix
    
    @classmethod
    def _create_affix_pools(cls):
        """创建词缀池"""
        pools = [
            # 通用前缀池
            AffixPool(
                id="pool_prefix_primary",
                name="主属性前缀池",
                affix_ids=["prefix_strength", "prefix_dexterity", "prefix_intelligence", "prefix_vitality", "prefix_all_stats"]
            ),
            AffixPool(
                id="pool_prefix_offense",
                name="进攻前缀池",
                affix_ids=["prefix_damage", "prefix_damage_percent", "prefix_critical_chance", "prefix_critical_damage", "prefix_attack_speed"]
            ),
            AffixPool(
                id="pool_prefix_elemental",
                name="元素伤害前缀池",
                affix_ids=["prefix_fire_damage", "prefix_cold_damage", "prefix_lightning_damage", "prefix_poison_damage"]
            ),
            AffixPool(
                id="pool_prefix_defense",
                name="防御前缀池",
                affix_ids=["prefix_armor", "prefix_armor_percent", "prefix_block_chance", "prefix_dodge_chance"]
            ),
            
            # 通用后缀池
            AffixPool(
                id="pool_suffix_health",
                name="生命后缀池",
                affix_ids=["suffix_health", "suffix_health_percent", "suffix_health_regen"]
            ),
            AffixPool(
                id="pool_suffix_resource",
                name="资源后缀池",
                affix_ids=["suffix_mana", "suffix_mana_regen"]
            ),
            AffixPool(
                id="pool_suffix_resistance",
                name="抗性后缀池",
                affix_ids=["suffix_fire_resist", "suffix_cold_resist", "suffix_lightning_resist", "suffix_poison_resist", "suffix_all_resist"]
            ),
            AffixPool(
                id="pool_suffix_utility",
                name="实用后缀池",
                affix_ids=["suffix_gold_find", "suffix_magic_find", "suffix_experience", "suffix_movement_speed", "suffix_thorns"]
            ),
            
            # 传奇词缀池
            AffixPool(
                id="pool_legendary_offense",
                name="传奇进攻池",
                affix_ids=["legendary_skill_damage", "legendary_cooldown", "legendary_critical_damage"]
            ),
            AffixPool(
                id="pool_legendary_defense",
                name="传奇防御池",
                affix_ids=["legendary_damage_reduction", "legendary_life_per_hit"]
            ),
            AffixPool(
                id="pool_legendary_resource",
                name="传奇资源池",
                affix_ids=["legendary_resource_cost"]
            ),
            
            # 武器专用池
            AffixPool(
                id="pool_weapon_prefix",
                name="武器前缀池",
                affix_ids=["prefix_damage", "prefix_damage_percent", "prefix_critical_chance", "prefix_critical_damage", "prefix_attack_speed"]
            ),
            
            # 护甲专用池
            AffixPool(
                id="pool_armor_prefix",
                name="护甲前缀池",
                affix_ids=["prefix_armor", "prefix_armor_percent", "prefix_dodge_chance"]
            ),
        ]
        
        for pool in pools:
            pool.calculate_weight(cls.AFFIX_DEFINITIONS)
            cls.AFFIX_POOLS[pool.id] = pool
    
    @classmethod
    def _create_item_mappings(cls):
        """创建物品类型到词缀池的映射"""
        cls.ITEM_AFFIX_POOLS = {
            "weapon": ["pool_prefix_primary", "pool_prefix_offense", "pool_prefix_elemental",
                      "pool_suffix_health", "pool_suffix_resource", "pool_suffix_utility"],
            "armor": ["pool_prefix_primary", "pool_prefix_defense",
                     "pool_suffix_health", "pool_suffix_resistance", "pool_suffix_utility"],
            "helmet": ["pool_prefix_primary", "pool_prefix_defense",
                      "pool_suffix_health", "pool_suffix_resistance"],
            "chest": ["pool_prefix_primary", "pool_prefix_defense",
                     "pool_suffix_health", "pool_suffix_resistance"],
            "gloves": ["pool_prefix_primary", "pool_prefix_offense", "pool_prefix_defense",
                      "pool_suffix_health", "pool_suffix_utility"],
            "boots": ["pool_prefix_primary", "pool_prefix_defense",
                     "pool_suffix_health", "pool_suffix_utility"],
            "belt": ["pool_prefix_primary", "pool_prefix_defense",
                    "pool_suffix_health", "pool_suffix_utility"],
            "shield": ["pool_prefix_primary", "pool_prefix_defense",
                      "pool_suffix_health", "pool_suffix_resistance"],
            "accessory": ["pool_prefix_primary", "pool_prefix_offense",
                         "pool_suffix_health", "pool_suffix_resistance", "pool_suffix_utility"],
        }
    
    @classmethod
    def generate_affixes_for_item(cls, item_type: str, rarity: str, item_level: int,
                                   character_level: int, count_override: Dict = None) -> List[Tuple[AffixDefinition, float]]:
        """为物品生成词缀"""
        cls.initialize()
        
        result = []
        
        # 获取词缀数量配置
        affix_config = count_override or cls.RARITY_AFFIX_COUNT.get(rarity, {"prefix": 0, "suffix": 0})
        
        # 获取可用的词缀池
        available_pools = cls.ITEM_AFFIX_POOLS.get(item_type, [])
        
        # 生成前缀
        prefix_count = cls._get_affix_count(affix_config.get("prefix", 0))
        prefixes = cls._select_affixes_from_pools(
            available_pools, AffixType.PREFIX, prefix_count, 
            item_type, item_level, character_level
        )
        result.extend(prefixes)
        
        # 生成后缀
        suffix_count = cls._get_affix_count(affix_config.get("suffix", 0))
        suffixes = cls._select_affixes_from_pools(
            available_pools, AffixType.SUFFIX, suffix_count,
            item_type, item_level, character_level
        )
        result.extend(suffixes)
        
        # 传奇词缀
        if "legendary" in affix_config:
            legendary = cls._select_affixes_from_pools(
                ["pool_legendary_offense", "pool_legendary_defense", "pool_legendary_resource"],
                AffixType.LEGENDARY, 1, item_type, item_level, character_level
            )
            result.extend(legendary)
        
        return result
    
    @classmethod
    def _get_affix_count(cls, config) -> int:
        """获取词缀数量"""
        if isinstance(config, int):
            return config
        if isinstance(config, tuple):
            return random.randint(config[0], config[1])
        return 0
    
    @classmethod
    def _select_affixes_from_pools(cls, pool_ids: List[str], affix_type: AffixType,
                                    count: int, item_type: str, item_level: int,
                                    character_level: int) -> List[Tuple[AffixDefinition, float]]:
        """从词缀池中选择词缀"""
        if count <= 0:
            return []
        
        # 收集所有符合条件的词缀
        candidates = []
        for pool_id in pool_ids:
            pool = cls.AFFIX_POOLS.get(pool_id)
            if not pool:
                continue
            
            for affix_id in pool.affix_ids:
                affix = cls.AFFIX_DEFINITIONS.get(affix_id)
                if not affix:
                    continue
                
                # 检查类型匹配
                if affix.type != affix_type:
                    continue
                
                # 检查物品类型
                if not affix.can_apply_to(item_type):
                    continue
                
                # 检查等级要求
                if affix.required_level > character_level:
                    continue
                
                if affix.item_level_requirement > item_level:
                    continue
                
                candidates.append(affix)
        
        if not candidates:
            return []
        
        # 按权重随机选择
        selected = []
        used_groups: Set[str] = set()
        
        for _ in range(count):
            if not candidates:
                break
            
            # 过滤已使用的组
            available = [a for a in candidates 
                        if not any(g in used_groups for g in a.groups)]
            
            if not available:
                available = candidates
            
            # 加权随机选择
            total_weight = sum(a.weight for a in available)
            if total_weight <= 0:
                break
            
            roll = random.randint(1, total_weight)
            cumulative = 0
            selected_affix = None
            
            for affix in available:
                cumulative += affix.weight
                if roll <= cumulative:
                    selected_affix = affix
                    break
            
            if selected_affix:
                # 确定词缀等级
                tier = cls._determine_affix_tier(item_level)
                
                # 生成数值
                value = selected_affix.generate_value(tier)
                selected.append((selected_affix, value))
                
                # 标记已使用的组
                used_groups.update(selected_affix.groups)
                
                # 从候选中移除
                candidates.remove(selected_affix)
        
        return selected
    
    @classmethod
    def _determine_affix_tier(cls, item_level: int) -> AffixTier:
        """根据物品等级确定词缀等级"""
        if item_level >= 70:
            return AffixTier.TIER_5
        elif item_level >= 50:
            return AffixTier.TIER_4
        elif item_level >= 30:
            return AffixTier.TIER_3
        elif item_level >= 15:
            return AffixTier.TIER_2
        else:
            return AffixTier.TIER_1
    
    @classmethod
    def get_affix_by_id(cls, affix_id: str) -> Optional[AffixDefinition]:
        """通过ID获取词缀定义"""
        cls.initialize()
        return cls.AFFIX_DEFINITIONS.get(affix_id)
    
    @classmethod
    def set_season(cls, season_id: str):
        """设置当前赛季"""
        cls._current_season = season_id
    
    @classmethod
    def get_all_affixes_for_display(cls) -> Dict[str, List[Dict]]:
        """获取所有词缀用于显示"""
        cls.initialize()
        
        result = {
            "prefixes": [],
            "suffixes": [],
            "legendary": []
        }
        
        for affix in cls.AFFIX_DEFINITIONS.values():
            affix_data = {
                "id": affix.id,
                "name": affix.name,
                "type": affix.type.value,
                "category": affix.category.value,
                "attribute": affix.attribute,
                "value_range": f"{affix.value_range.min_value}-{affix.value_range.max_value}",
                "is_percentage": affix.is_percentage,
                "required_level": affix.required_level,
            }
            
            if affix.type == AffixType.PREFIX:
                result["prefixes"].append(affix_data)
            elif affix.type == AffixType.SUFFIX:
                result["suffixes"].append(affix_data)
            elif affix.type == AffixType.LEGENDARY:
                result["legendary"].append(affix_data)
        
        return result
