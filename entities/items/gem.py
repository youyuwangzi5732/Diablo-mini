"""
宝石系统
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import random

from .item import Item, ItemType, ItemRarity


class GemType(Enum):
    RUBY = "ruby"
    SAPPHIRE = "sapphire"
    EMERALD = "emerald"
    TOPAZ = "topaz"
    AMETHYST = "amethyst"
    DIAMOND = "diamond"


class GemQuality(Enum):
    CHIPPED = 1
    FLAWED = 2
    STANDARD = 3
    FLAWLESS = 4
    PERFECT = 5
    ROYAL = 6
    IMPERIAL = 7


@dataclass
class GemStats:
    weapon: Dict[str, float]
    armor: Dict[str, float]
    jewelry: Dict[str, float]


GEM_STATS = {
    GemType.RUBY: {
        GemQuality.CHIPPED: GemStats(
            weapon={"min_damage": 4, "max_damage": 8},
            armor={"strength": 3},
            jewelry={"strength": 3}
        ),
        GemQuality.FLAWED: GemStats(
            weapon={"min_damage": 6, "max_damage": 12},
            armor={"strength": 5},
            jewelry={"strength": 5}
        ),
        GemQuality.STANDARD: GemStats(
            weapon={"min_damage": 10, "max_damage": 20},
            armor={"strength": 8},
            jewelry={"strength": 8}
        ),
        GemQuality.FLAWLESS: GemStats(
            weapon={"min_damage": 15, "max_damage": 30},
            armor={"strength": 12},
            jewelry={"strength": 12}
        ),
        GemQuality.PERFECT: GemStats(
            weapon={"min_damage": 20, "max_damage": 40},
            armor={"strength": 16},
            jewelry={"strength": 16}
        ),
        GemQuality.ROYAL: GemStats(
            weapon={"min_damage": 28, "max_damage": 56},
            armor={"strength": 22},
            jewelry={"strength": 22}
        ),
        GemQuality.IMPERIAL: GemStats(
            weapon={"min_damage": 40, "max_damage": 80},
            armor={"strength": 30},
            jewelry={"strength": 30}
        ),
    },
    GemType.SAPPHIRE: {
        GemQuality.CHIPPED: GemStats(
            weapon={"cold_damage": 5},
            armor={"cold_resist": 3},
            jewelry={"intelligence": 3}
        ),
        GemQuality.FLAWED: GemStats(
            weapon={"cold_damage": 8},
            armor={"cold_resist": 5},
            jewelry={"intelligence": 5}
        ),
        GemQuality.STANDARD: GemStats(
            weapon={"cold_damage": 12},
            armor={"cold_resist": 8},
            jewelry={"intelligence": 8}
        ),
        GemQuality.FLAWLESS: GemStats(
            weapon={"cold_damage": 18},
            armor={"cold_resist": 12},
            jewelry={"intelligence": 12}
        ),
        GemQuality.PERFECT: GemStats(
            weapon={"cold_damage": 25},
            armor={"cold_resist": 16},
            jewelry={"intelligence": 16}
        ),
        GemQuality.ROYAL: GemStats(
            weapon={"cold_damage": 35},
            armor={"cold_resist": 22},
            jewelry={"intelligence": 22}
        ),
        GemQuality.IMPERIAL: GemStats(
            weapon={"cold_damage": 50},
            armor={"cold_resist": 30},
            jewelry={"intelligence": 30}
        ),
    },
    GemType.EMERALD: {
        GemQuality.CHIPPED: GemStats(
            weapon={"crit_damage": 10},
            armor={"dexterity": 3},
            jewelry={"dexterity": 3}
        ),
        GemQuality.FLAWED: GemStats(
            weapon={"crit_damage": 15},
            armor={"dexterity": 5},
            jewelry={"dexterity": 5}
        ),
        GemQuality.STANDARD: GemStats(
            weapon={"crit_damage": 20},
            armor={"dexterity": 8},
            jewelry={"dexterity": 8}
        ),
        GemQuality.FLAWLESS: GemStats(
            weapon={"crit_damage": 28},
            armor={"dexterity": 12},
            jewelry={"dexterity": 12}
        ),
        GemQuality.PERFECT: GemStats(
            weapon={"crit_damage": 36},
            armor={"dexterity": 16},
            jewelry={"dexterity": 16}
        ),
        GemQuality.ROYAL: GemStats(
            weapon={"crit_damage": 46},
            armor={"dexterity": 22},
            jewelry={"dexterity": 22}
        ),
        GemQuality.IMPERIAL: GemStats(
            weapon={"crit_damage": 60},
            armor={"dexterity": 30},
            jewelry={"dexterity": 30}
        ),
    },
    GemType.TOPAZ: {
        GemQuality.CHIPPED: GemStats(
            weapon={"lightning_damage": 5},
            armor={"lightning_resist": 3},
            jewelry={"magic_find": 5}
        ),
        GemQuality.FLAWED: GemStats(
            weapon={"lightning_damage": 8},
            armor={"lightning_resist": 5},
            jewelry={"magic_find": 8}
        ),
        GemQuality.STANDARD: GemStats(
            weapon={"lightning_damage": 12},
            armor={"lightning_resist": 8},
            jewelry={"magic_find": 12}
        ),
        GemQuality.FLAWLESS: GemStats(
            weapon={"lightning_damage": 18},
            armor={"lightning_resist": 12},
            jewelry={"magic_find": 18}
        ),
        GemQuality.PERFECT: GemStats(
            weapon={"lightning_damage": 25},
            armor={"lightning_resist": 16},
            jewelry={"magic_find": 25}
        ),
        GemQuality.ROYAL: GemStats(
            weapon={"lightning_damage": 35},
            armor={"lightning_resist": 22},
            jewelry={"magic_find": 35}
        ),
        GemQuality.IMPERIAL: GemStats(
            weapon={"lightning_damage": 50},
            armor={"lightning_resist": 30},
            jewelry={"magic_find": 50}
        ),
    },
    GemType.AMETHYST: {
        GemQuality.CHIPPED: GemStats(
            weapon={"life_steal": 1},
            armor={"vitality": 3},
            jewelry={"vitality": 3}
        ),
        GemQuality.FLAWED: GemStats(
            weapon={"life_steal": 2},
            armor={"vitality": 5},
            jewelry={"vitality": 5}
        ),
        GemQuality.STANDARD: GemStats(
            weapon={"life_steal": 3},
            armor={"vitality": 8},
            jewelry={"vitality": 8}
        ),
        GemQuality.FLAWLESS: GemStats(
            weapon={"life_steal": 4},
            armor={"vitality": 12},
            jewelry={"vitality": 12}
        ),
        GemQuality.PERFECT: GemStats(
            weapon={"life_steal": 5},
            armor={"vitality": 16},
            jewelry={"vitality": 16}
        ),
        GemQuality.ROYAL: GemStats(
            weapon={"life_steal": 6},
            armor={"vitality": 22},
            jewelry={"vitality": 22}
        ),
        GemQuality.IMPERIAL: GemStats(
            weapon={"life_steal": 8},
            armor={"vitality": 30},
            jewelry={"vitality": 30}
        ),
    },
    GemType.DIAMOND: {
        GemQuality.CHIPPED: GemStats(
            weapon={"damage_to_elites": 5},
            armor={"all_resist": 2},
            jewelry={"all_resist": 2}
        ),
        GemQuality.FLAWED: GemStats(
            weapon={"damage_to_elites": 8},
            armor={"all_resist": 4},
            jewelry={"all_resist": 4}
        ),
        GemQuality.STANDARD: GemStats(
            weapon={"damage_to_elites": 12},
            armor={"all_resist": 6},
            jewelry={"all_resist": 6}
        ),
        GemQuality.FLAWLESS: GemStats(
            weapon={"damage_to_elites": 18},
            armor={"all_resist": 9},
            jewelry={"all_resist": 9}
        ),
        GemQuality.PERFECT: GemStats(
            weapon={"damage_to_elites": 25},
            armor={"all_resist": 12},
            jewelry={"all_resist": 12}
        ),
        GemQuality.ROYAL: GemStats(
            weapon={"damage_to_elites": 35},
            armor={"all_resist": 16},
            jewelry={"all_resist": 16}
        ),
        GemQuality.IMPERIAL: GemStats(
            weapon={"damage_to_elites": 50},
            armor={"all_resist": 20},
            jewelry={"all_resist": 20}
        ),
    },
}


class Gem(Item):
    def __init__(self, gem_type: GemType, quality: GemQuality):
        self.gem_type = gem_type
        self.quality = quality
        
        quality_names = {
            GemQuality.CHIPPED: "碎裂的",
            GemQuality.FLAWED: "裂开的",
            GemQuality.STANDARD: "",
            GemQuality.FLAWLESS: "无瑕的",
            GemQuality.PERFECT: "完美的",
            GemQuality.ROYAL: "皇家的",
            GemQuality.IMPERIAL: "帝国的"
        }
        
        type_names = {
            GemType.RUBY: "红宝石",
            GemType.SAPPHIRE: "蓝宝石",
            GemType.EMERALD: "祖母绿",
            GemType.TOPAZ: "黄宝石",
            GemType.AMETHYST: "紫宝石",
            GemType.DIAMOND: "钻石"
        }
        
        name = f"{quality_names[quality]}{type_names[gem_type]}".strip()
        
        super().__init__(
            id="",
            base_id=f"gem_{gem_type.value}_{quality.value}",
            name=name,
            item_type=ItemType.GEM,
            rarity=ItemRarity.COMMON,
            max_stack=10
        )
    
    def get_stats_for_slot(self, slot_type: str) -> Dict[str, float]:
        gem_stats = GEM_STATS.get(self.gem_type, {}).get(self.quality)
        if not gem_stats:
            return {}
        
        if slot_type in ["main_hand", "off_hand"]:
            return gem_stats.weapon
        elif slot_type in ["head", "shoulders", "chest", "hands", "waist", "legs", "feet"]:
            return gem_stats.armor
        elif slot_type in ["neck", "ring_left", "ring_right"]:
            return gem_stats.jewelry
        
        return {}
    
    def can_upgrade(self) -> bool:
        return self.quality.value < GemQuality.IMPERIAL.value
    
    def upgrade(self) -> bool:
        if not self.can_upgrade():
            return False
        
        self.quality = GemQuality(self.quality.value + 1)
        
        quality_names = {
            GemQuality.CHIPPED: "碎裂的",
            GemQuality.FLAWED: "裂开的",
            GemQuality.STANDARD: "",
            GemQuality.FLAWLESS: "无瑕的",
            GemQuality.PERFECT: "完美的",
            GemQuality.ROYAL: "皇家的",
            GemQuality.IMPERIAL: "帝国的"
        }
        
        type_names = {
            GemType.RUBY: "红宝石",
            GemType.SAPPHIRE: "蓝宝石",
            GemType.EMERALD: "祖母绿",
            GemType.TOPAZ: "黄宝石",
            GemType.AMETHYST: "紫宝石",
            GemType.DIAMOND: "钻石"
        }
        
        self.name = f"{quality_names[self.quality]}{type_names[self.gem_type]}".strip()
        self.base_id = f"gem_{self.gem_type.value}_{self.quality.value}"
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "gem_type": self.gem_type.value,
            "quality": self.quality.value
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Gem':
        gem = cls(
            gem_type=GemType(data["gem_type"]),
            quality=GemQuality(data["quality"])
        )
        gem.id = data["id"]
        gem.quantity = data.get("quantity", 1)
        return gem


@dataclass
class LegendaryGem:
    id: str
    name: str
    description: str
    icon: str
    max_level: int = 100
    current_level: int = 0
    
    base_effect: str = ""
    upgrade_effect: str = ""
    
    base_value: float = 0
    upgrade_value: float = 0
    
    rank_requirement: int = 0
    
    def get_effect_value(self) -> float:
        return self.base_value + (self.upgrade_value * self.current_level)
    
    def can_upgrade(self, greater_rift_level: int) -> bool:
        if self.current_level >= self.max_level:
            return False
        return greater_rift_level >= self.current_level + 5
    
    def attempt_upgrade(self, greater_rift_level: int) -> bool:
        if not self.can_upgrade(greater_rift_level):
            return False
        
        success_chance = min(1.0, (greater_rift_level - self.current_level) * 0.1)
        
        if random.random() < success_chance:
            self.current_level += 1
            return True
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "max_level": self.max_level,
            "current_level": self.current_level,
            "base_effect": self.base_effect,
            "upgrade_effect": self.upgrade_effect,
            "base_value": self.base_value,
            "upgrade_value": self.upgrade_value,
            "rank_requirement": self.rank_requirement
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LegendaryGem':
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            icon=data.get("icon", ""),
            max_level=data.get("max_level", 100),
            current_level=data.get("current_level", 0),
            base_effect=data.get("base_effect", ""),
            upgrade_effect=data.get("upgrade_effect", ""),
            base_value=data.get("base_value", 0),
            upgrade_value=data.get("upgrade_value", 0),
            rank_requirement=data.get("rank_requirement", 0)
        )


LEGENDARY_GEMS = [
    LegendaryGem(
        id="bane_of_the_powerful",
        name="强者之灾",
        description="击杀精英怪后增加伤害",
        icon="gem_powerful.png",
        base_effect="击杀精英后伤害提高20%，持续20秒",
        upgrade_effect="每级增加1秒持续时间",
        base_value=20,
        upgrade_value=1
    ),
    LegendaryGem(
        id="bane_of_the_trapped",
        name="困者之灾",
        description="对受控场效果影响的敌人造成额外伤害",
        icon="gem_trapped.png",
        base_effect="对受控场敌人伤害提高15%",
        upgrade_effect="每级增加0.5%伤害",
        base_value=15,
        upgrade_value=0.5
    ),
    LegendaryGem(
        id="mirinae_teardrop",
        name="米尔维娜的泪滴",
        description="攻击时有几率释放神圣之矛",
        icon="gem_mirinae.png",
        base_effect="15%几率释放神圣之矛，造成2000%武器伤害",
        upgrade_effect="每级增加50%武器伤害",
        base_value=2000,
        upgrade_value=50
    ),
    LegendaryGem(
        id="wreath_of_lightning",
        name="闪电华冠",
        description="攻击时有几率获得闪电华冠",
        icon="gem_lightning.png",
        base_effect="20%几率获得闪电华冠，对附近敌人造成500%武器伤害",
        upgrade_effect="每级增加25%武器伤害",
        base_value=500,
        upgrade_value=25
    ),
    LegendaryGem(
        id="gogok_of_swiftness",
        name="迅捷勾玉",
        description="攻击时获得攻击速度加成",
        icon="gem_swiftness.png",
        base_effect="每次攻击获得1%攻速，最高15%，持续4秒",
        upgrade_effect="每级增加0.5秒持续时间",
        base_value=4,
        upgrade_value=0.5
    ),
    LegendaryGem(
        id="esoteric_alteration",
        name="秘术异变",
        description="提升非物理抗性并在低血量时获得减伤",
        icon="gem_esoteric.png",
        base_effect="非物理抗性提高10%",
        upgrade_effect="每级提高0.5%非物理抗性",
        base_value=10,
        upgrade_value=0.5
    ),
    LegendaryGem(
        id="molten_wildebeest",
        name="熔火野兽之心",
        description="持续提供生命恢复并获得护盾",
        icon="gem_wildebeest.png",
        base_effect="每秒回复2%最大生命值",
        upgrade_effect="每级提高0.08%生命回复",
        base_value=2,
        upgrade_value=0.08
    ),
    LegendaryGem(
        id="zei_stone",
        name="泽伊复仇之石",
        description="与目标距离越远造成伤害越高",
        icon="gem_zei.png",
        base_effect="每10码提高4%伤害，最多40%",
        upgrade_effect="每级提高0.2%最大伤害",
        base_value=40,
        upgrade_value=0.2
    ),
    LegendaryGem(
        id="pain_enhancer",
        name="受罚者之祸",
        description="暴击使敌人流血并提升攻速",
        icon="gem_pain.png",
        base_effect="暴击造成流血，每秒1200%武器伤害",
        upgrade_effect="每级提高40%流血伤害",
        base_value=1200,
        upgrade_value=40
    ),
    LegendaryGem(
        id="boyarsky_chip",
        name="伯亚斯基之芯",
        description="提高荆棘伤害并减免近战伤害",
        icon="gem_chip.png",
        base_effect="荆棘伤害提高8000",
        upgrade_effect="每级提高1600荆棘伤害",
        base_value=8000,
        upgrade_value=1600
    ),
]
