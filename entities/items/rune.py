"""
符文系统
"""
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re

from .item import Item, ItemType, ItemRarity


class RuneType(Enum):
    EL = 1
    ELD = 2
    TIR = 3
    NEF = 4
    ETH = 5
    ITH = 6
    TAL = 7
    RAL = 8
    ORT = 9
    THUL = 10
    AMN = 11
    SOL = 12
    SHAEL = 13
    DOL = 14
    HEL = 15
    IO = 16
    LUM = 17
    KO = 18
    FAL = 19
    LEM = 20
    PUL = 21
    UM = 22
    MAL = 23
    IST = 24
    GUL = 25
    VEX = 26
    OHM = 27
    LO = 28
    SUR = 29
    BER = 30
    JAH = 31
    CHAM = 32
    ZOD = 33


@dataclass
class RuneStats:
    weapon: Dict[str, float]
    armor: Dict[str, float]
    shield: Dict[str, float]


RUNE_STATS = {
    RuneType.EL: RuneStats(
        weapon={"attack_rating": 50, "light_radius": 1},
        armor={"armor": 15, "light_radius": 1},
        shield={"armor": 15, "light_radius": 1}
    ),
    RuneType.ELD: RuneStats(
        weapon={"damage_to_undead": 75, "attack_speed_vs_undead": 50},
        armor={"mana": 15},
        shield={"mana": 15}
    ),
    RuneType.TIR: RuneStats(
        weapon={"mana_per_kill": 2},
        armor={"mana": 10},
        shield={"mana": 10}
    ),
    RuneType.NEF: RuneStats(
        weapon={"damage_to_missile": 30},
        armor={"damage_to_melee": 3},
        shield={"damage_to_melee": 3}
    ),
    RuneType.ETH: RuneStats(
        weapon={"target_defense": -25},
        armor={"mana_regen": 15},
        shield={"mana_regen": 15}
    ),
    RuneType.ITH: RuneStats(
        weapon={"max_damage": 9},
        armor={"damage_to_mana": 15},
        shield={"damage_to_mana": 15}
    ),
    RuneType.TAL: RuneStats(
        weapon={"poison_damage": 75},
        armor={"poison_resist": 30},
        shield={"poison_resist": 35}
    ),
    RuneType.RAL: RuneStats(
        weapon={"fire_damage": 30},
        armor={"fire_resist": 30},
        shield={"fire_resist": 35}
    ),
    RuneType.ORT: RuneStats(
        weapon={"lightning_damage": 21},
        armor={"lightning_resist": 30},
        shield={"lightning_resist": 35}
    ),
    RuneType.THUL: RuneStats(
        weapon={"cold_damage": 37},
        armor={"cold_resist": 30},
        shield={"cold_resist": 35}
    ),
    RuneType.AMN: RuneStats(
        weapon={"life_steal": 7},
        armor={"damage_to_attacker": 14},
        shield={"damage_to_attacker": 14}
    ),
    RuneType.SOL: RuneStats(
        weapon={"min_damage": 9},
        armor={"damage_reduction": 7},
        shield={"damage_reduction": 7}
    ),
    RuneType.SHAEL: RuneStats(
        weapon={"attack_speed": 20},
        armor={"faster_hit_recovery": 20},
        shield={"faster_block_rate": 20}
    ),
    RuneType.DOL: RuneStats(
        weapon={"hit_causes_monster_flee": 25},
        armor={"health_regen": 7},
        shield={"health_regen": 7}
    ),
    RuneType.HEL: RuneStats(
        weapon={"requirements": -20},
        armor={"requirements": -15},
        shield={"requirements": -15}
    ),
    RuneType.IO: RuneStats(
        weapon={"vitality": 10},
        armor={"vitality": 10},
        shield={"vitality": 10}
    ),
    RuneType.LUM: RuneStats(
        weapon={"energy": 10},
        armor={"energy": 10},
        shield={"energy": 10}
    ),
    RuneType.KO: RuneStats(
        weapon={"dexterity": 10},
        armor={"dexterity": 10},
        shield={"dexterity": 10}
    ),
    RuneType.FAL: RuneStats(
        weapon={"strength": 10},
        armor={"strength": 10},
        shield={"strength": 10}
    ),
    RuneType.LEM: RuneStats(
        weapon={"gold_find": 75},
        armor={"gold_find": 50},
        shield={"gold_find": 50}
    ),
    RuneType.PUL: RuneStats(
        weapon={"damage_to_demons": 175},
        armor={"defense_vs_demons": 100},
        shield={"defense_vs_demons": 100}
    ),
    RuneType.UM: RuneStats(
        weapon={"chance_open_wounds": 25},
        armor={"all_resist": 15},
        shield={"all_resist": 22}
    ),
    RuneType.MAL: RuneStats(
        weapon={"prevent_monster_heal": 100},
        armor={"magic_damage_reduction": 7},
        shield={"magic_damage_reduction": 7}
    ),
    RuneType.IST: RuneStats(
        weapon={"magic_find": 30},
        armor={"magic_find": 25},
        shield={"magic_find": 25}
    ),
    RuneType.GUL: RuneStats(
        weapon={"attack_rating": 20, "max_damage": 5},
        armor={"max_health": 5},
        shield={"max_health": 5}
    ),
    RuneType.VEX: RuneStats(
        weapon={"mana_steal": 7, "fire_resist": 5},
        armor={"max_mana": 5},
        shield={"max_mana": 5}
    ),
    RuneType.OHM: RuneStats(
        weapon={"damage_percent": 50},
        armor={"damage_reduction": 5},
        shield={"damage_reduction": 5}
    ),
    RuneType.LO: RuneStats(
        weapon={"deadly_strike": 20},
        armor={"lightning_resist": 5},
        shield={"lightning_resist": 5}
    ),
    RuneType.SUR: RuneStats(
        weapon={"hit_blinds_target": 35},
        armor={"mana": 5},
        shield={"mana": 5}
    ),
    RuneType.BER: RuneStats(
        weapon={"chance_crushing_blow": 20},
        armor={"damage_reduction": 8},
        shield={"damage_reduction": 8}
    ),
    RuneType.JAH: RuneStats(
        weapon={"ignore_target_defense": 100},
        armor={"max_health": 5},
        shield={"max_health": 5}
    ),
    RuneType.CHAM: RuneStats(
        weapon={"freeze_target": 3},
        armor={"cannot_be_frozen": 100},
        shield={"cannot_be_frozen": 100}
    ),
    RuneType.ZOD: RuneStats(
        weapon={"indestructible": 100},
        armor={"indestructible": 100},
        shield={"indestructible": 100}
    ),
}


@dataclass
class RuneWord:
    id: str
    name: str
    runes: List[RuneType]
    item_types: List[str]
    required_level: int
    effects: Dict[str, float]
    description: str = ""
    
    def matches(self, socketed_runes: List['Rune']) -> bool:
        if len(socketed_runes) != len(self.runes):
            return False
        
        for i, rune_type in enumerate(self.runes):
            if socketed_runes[i].rune_type != rune_type:
                return False
        
        return True


RUNE_WORDS = [
    RuneWord(
        id="stealth",
        name="隐密",
        runes=[RuneType.TAL, RuneType.ETH],
        item_types=["armor", "chest"],
        required_level=17,
        effects={
            "magic_damage_reduction": 6,
            "dexterity": 6,
            "mana_regen": 15,
            "faster_cast_rate": 25,
            "faster_hit_recovery": 25,
            "faster_run_walk": 25
        },
        description="施法速度+25%，打击恢复+25%，移动速度+25%"
    ),
    RuneWord(
        id="leaf",
        name="叶子",
        runes=[RuneType.TIR, RuneType.RAL],
        item_types=["staff"],
        required_level=19,
        effects={
            "fire_damage": 53,
            "cold_damage": 19,
            "fire_skills": 3,
            "fire_resist": 33,
            "mana_per_kill": 5
        },
        description="火焰技能+3，火焰伤害+53"
    ),
    RuneWord(
        id="ancients_pledge",
        name="古代人的誓约",
        runes=[RuneType.RAL, RuneType.ORT, RuneType.TAL],
        item_types=["shield"],
        required_level=21,
        effects={
            "all_resist": 43,
            "damage_to_attacker": 10,
            "cold_damage": 37
        },
        description="全抗+43%，攻击者受到伤害10"
    ),
    RuneWord(
        id="spirit",
        name="精神",
        runes=[RuneType.TAL, RuneType.THUL, RuneType.ORT, RuneType.AMN],
        item_types=["sword", "shield"],
        required_level=25,
        effects={
            "all_skills": 2,
            "faster_cast_rate": 35,
            "mana": 112,
            "vitality": 22,
            "magic_absorb": 8
        },
        description="所有技能+2，施法速度+35%"
    ),
    RuneWord(
        id="insight",
        name="眼光",
        runes=[RuneType.RAL, RuneType.TIR, RuneType.TAL, RuneType.SOL],
        item_types=["polearm", "staff"],
        required_level=27,
        effects={
            "meditation_aura": 12,
            "all_skills": 5,
            "critical_strike": 35,
            "attack_speed": 20,
            "mana_regen": 20
        },
        description="冥想光环12级，法力回复+20%"
    ),
    RuneWord(
        id="enigma",
        name="谜团",
        runes=[RuneType.JAH, RuneType.IST, RuneType.BER],
        item_types=["armor", "chest"],
        required_level=65,
        effects={
            "teleport": 1,
            "all_skills": 2,
            "strength": 75,
            "magic_find": 50,
            "damage_reduction": 8,
            "health_per_level": 0.75
        },
        description="传送技能+1，所有技能+2，力量+75"
    ),
    RuneWord(
        id="grief",
        name="悔恨",
        runes=[RuneType.ETH, RuneType.TIR, RuneType.LO, RuneType.MAL, RuneType.RAL],
        item_types=["sword", "axe"],
        required_level=59,
        effects={
            "damage": 340,
            "attack_speed": 30,
            "chance_open_wounds": 35,
            "deadly_strike": 15,
            "mana_per_kill": 10
        },
        description="伤害+340，攻击速度+30%"
    ),
    RuneWord(
        id="infinity",
        name="无限",
        runes=[RuneType.BER, RuneType.MAL, RuneType.BER, RuneType.IST],
        item_types=["polearm"],
        required_level=63,
        effects={
            "conviction_aura": 12,
            "all_skills": 5,
            "critical_strike": 40,
            "magic_find": 30,
            "lightning_resist": 85
        },
        description="信念光环12级，暴击率+40%"
    ),
    RuneWord(
        id="fortitude",
        name="刚毅",
        runes=[RuneType.EL, RuneType.SOL, RuneType.DOL, RuneType.LO],
        item_types=["armor", "chest"],
        required_level=59,
        effects={
            "damage_percent": 300,
            "armor": 220,
            "all_resist": 30,
            "health_regen": 7
        },
        description="增强伤害与护甲，兼顾全抗"
    ),
    RuneWord(
        id="harmony",
        name="和谐",
        runes=[RuneType.TIR, RuneType.ITH, RuneType.SOL, RuneType.KO],
        item_types=["bow", "crossbow"],
        required_level=39,
        effects={
            "attack_speed": 20,
            "damage_percent": 180,
            "vitality": 10,
            "dexterity": 20
        },
        description="远程攻速与敏捷强化"
    ),
    RuneWord(
        id="sanctuary",
        name="圣护",
        runes=[RuneType.KO, RuneType.KO, RuneType.MAL],
        item_types=["shield", "off_hand"],
        required_level=49,
        effects={
            "block_chance": 20,
            "all_resist": 50,
            "dexterity": 20,
            "magic_damage_reduction": 7
        },
        description="格挡与抗性并重的防御符文之语"
    ),
    RuneWord(
        id="obsession",
        name="执念",
        runes=[RuneType.ZOD, RuneType.IST, RuneType.LEM, RuneType.LUM, RuneType.IO, RuneType.NEF],
        item_types=["staff", "wand", "orb"],
        required_level=69,
        effects={
            "all_skills": 3,
            "faster_cast_rate": 65,
            "intelligence": 35,
            "mana_regen": 30
        },
        description="高施法速度与高法术增益"
    ),
    RuneWord(
        id="blood_oath",
        name="血誓",
        runes=[RuneType.AMN, RuneType.UM, RuneType.FAL],
        item_types=["sword", "axe", "mace", "fist_weapon"],
        required_level=47,
        effects={
            "life_steal": 10,
            "attack_power": 140,
            "crit_chance": 8,
            "health_regen": 20
        },
        description="近战吸血与暴击强化"
    ),
    RuneWord(
        id="tempest",
        name="风暴",
        runes=[RuneType.ORT, RuneType.THUL, RuneType.SHAEL],
        item_types=["spear", "polearm"],
        required_level=37,
        effects={
            "attack_speed": 30,
            "lightning_damage": 120,
            "cold_damage": 80,
            "movement_speed": 12
        },
        description="高速与元素伤害并行"
    ),
]


class Rune(Item):
    def __init__(self, rune_type: RuneType):
        self.rune_type = rune_type
        
        rune_names = {
            RuneType.EL: "艾尔", RuneType.ELD: "艾德", RuneType.TIR: "特尔",
            RuneType.NEF: "那夫", RuneType.ETH: "艾斯", RuneType.ITH: "伊司",
            RuneType.TAL: "塔尔", RuneType.RAL: "拉尔", RuneType.ORT: "欧特",
            RuneType.THUL: "书尔", RuneType.AMN: "安姆", RuneType.SOL: "索尔",
            RuneType.SHAEL: "夏", RuneType.DOL: "多尔", RuneType.HEL: "海尔",
            RuneType.IO: "艾欧", RuneType.LUM: "卢姆", RuneType.KO: "科",
            RuneType.FAL: "法尔", RuneType.LEM: "蓝姆", RuneType.PUL: "普尔",
            RuneType.UM: "乌姆", RuneType.MAL: "马尔", RuneType.IST: "伊司特",
            RuneType.GUL: "古尔", RuneType.VEX: "伐克斯", RuneType.OHM: "欧姆",
            RuneType.LO: "罗", RuneType.SUR: "瑟", RuneType.BER: "贝",
            RuneType.JAH: "乔", RuneType.CHAM: "查姆", RuneType.ZOD: "萨德"
        }
        
        name = f"{rune_names[rune_type]} #{rune_type.value}"
        
        super().__init__(
            id="",
            base_id=f"rune_{rune_type.value}",
            name=name,
            item_type=ItemType.RUNE,
            rarity=ItemRarity.COMMON,
            max_stack=10
        )
    
    def get_stats_for_slot(self, slot_type: str) -> Dict[str, float]:
        rune_stats = RUNE_STATS.get(self.rune_type)
        if not rune_stats:
            return {}
        
        if slot_type in ["main_hand"]:
            return rune_stats.weapon
        elif slot_type in ["off_hand"]:
            if slot_type == "shield":
                return rune_stats.shield
            return rune_stats.weapon
        elif slot_type in ["head", "shoulders", "chest", "hands", "waist", "legs", "feet"]:
            return rune_stats.armor
        
        return {}
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["rune_type"] = self.rune_type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Rune':
        rune = cls(rune_type=RuneType(data["rune_type"]))
        rune.id = data["id"]
        rune.quantity = data.get("quantity", 1)
        return rune


class RuneWordChecker:
    @staticmethod
    def check(socketed_runes: List[Rune], item_type: str) -> Optional[RuneWord]:
        if not socketed_runes:
            return None
        
        for rune_word in RUNE_WORDS:
            if item_type not in rune_word.item_types:
                continue
            
            if rune_word.matches(socketed_runes):
                return rune_word
        
        return None
    
    @staticmethod
    def get_possible_rune_words(item_type: str, socket_count: int) -> List[RuneWord]:
        return [
            rw for rw in RUNE_WORDS
            if item_type in rw.item_types and len(rw.runes) == socket_count
        ]
