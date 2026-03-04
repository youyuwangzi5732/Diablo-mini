"""
职业类定义
"""
from typing import Dict, List, Optional, Any, Type
from dataclasses import dataclass, field
from enum import Enum
import json
import os


class DamageType(Enum):
    PHYSICAL = "physical"
    FIRE = "fire"
    COLD = "cold"
    LIGHTNING = "lightning"
    POISON = "poison"
    HOLY = "holy"
    SHADOW = "shadow"
    ARCANE = "arcane"


class Resource_type(Enum):
    MANA = "mana"
    FURY = "fury"
    SPIRIT = "spirit"
    HATRED = "hatred"
    DISCIPLINE = "discipline"
    ESSENCE = "essence"
    WRATH = "wrath"


@dataclass
class SkillDefinition:
    id: str
    name: str
    description: str
    icon: str
    max_level: int = 5
    required_level: int = 1
    resource_cost: float = 0
    cooldown: float = 0
    damage_type: DamageType = DamageType.PHYSICAL
    branches: List[Dict[str, Any]] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)


@dataclass
class PassiveDefinition:
    id: str
    name: str
    description: str
    icon: str
    max_level: int = 5
    required_level: int = 1
    effects: List[Dict[str, Any]] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)


@dataclass
class CharacterClass:
    id: str
    name: str
    description: str
    icon: str
    
    primary_attribute: str
    resource_type: Resource_type
    max_resource: float = 100
    
    base_health: int = 100
    base_mana: int = 50
    
    allowed_weapon_types: List[str] = field(default_factory=list)
    allowed_armor_types: List[str] = field(default_factory=list)
    
    skills: List[SkillDefinition] = field(default_factory=list)
    passives: List[PassiveDefinition] = field(default_factory=list)
    
    skill_tree: Dict[str, Any] = field(default_factory=dict)
    
    starting_attributes: Dict[str, int] = field(default_factory=dict)
    attribute_per_level: Dict[str, int] = field(default_factory=dict)
    
    lore: str = ""


class ClassFactory:
    _classes: Dict[str, CharacterClass] = {}
    _initialized = False
    
    @classmethod
    def initialize(cls, data_path: str = None):
        if cls._initialized:
            return
        
        cls._create_default_classes()
        cls._initialized = True
    
    @classmethod
    def _create_default_classes(cls):
        cls._classes["barbarian"] = CharacterClass(
            id="barbarian",
            name="野蛮人",
            description="来自北方山脉的勇猛战士，以强大的力量和近战技巧著称。",
            icon="barbarian_icon",
            primary_attribute="strength",
            resource_type=Resource_type.FURY,
            max_resource=100,
            base_health=150,
            base_mana=0,
            allowed_weapon_types=["sword", "axe", "mace", "dagger", "fist_weapon", "shield"],
            allowed_armor_types=["heavy", "medium"],
            starting_attributes={
                "strength": 15,
                "dexterity": 8,
                "intelligence": 5,
                "vitality": 12
            },
            attribute_per_level={
                "strength": 3,
                "dexterity": 1,
                "intelligence": 1,
                "vitality": 2
            },
            skills=[
                SkillDefinition(
                    id="bash",
                    name="猛击",
                    description="对敌人造成强力打击",
                    icon="skill_bash",
                    max_level=5,
                    required_level=1,
                    resource_cost=10,
                    damage_type=DamageType.PHYSICAL,
                    branches=[
                        {"id": "fury_bash", "name": "狂暴猛击", "description": "增加伤害和怒气生成"},
                        {"id": "stun_bash", "name": "眩晕猛击", "description": "有几率眩晕敌人"},
                        {"id": "cleave", "name": "横扫", "description": "攻击前方多个敌人"}
                    ]
                ),
                SkillDefinition(
                    id="whirlwind",
                    name="旋风斩",
                    description="旋转攻击周围所有敌人",
                    icon="skill_whirlwind",
                    max_level=5,
                    required_level=12,
                    resource_cost=20,
                    damage_type=DamageType.PHYSICAL
                ),
                SkillDefinition(
                    id="leap",
                    name="跳跃攻击",
                    description="跳向目标位置并造成范围伤害",
                    icon="skill_leap",
                    max_level=5,
                    required_level=8,
                    resource_cost=15,
                    cooldown=10,
                    damage_type=DamageType.PHYSICAL
                )
            ],
            passives=[
                PassiveDefinition(
                    id="toughness",
                    name="坚韧",
                    description="增加生命值和护甲",
                    icon="passive_toughness",
                    max_level=5,
                    required_level=10,
                    effects=[{"type": "health_percent", "value": 5}, {"type": "armor_percent", "value": 5}]
                )
            ],
            lore="野蛮人是来自亚瑞特山脉的勇猛战士。他们的家园被毁灭后，流浪于世，以强大的力量和无畏的战斗精神闻名。"
        )
        
        cls._classes["monk"] = CharacterClass(
            id="monk",
            name="武僧",
            description="修炼神圣武学的战士，以敏捷的身手和连击技巧著称。",
            icon="monk_icon",
            primary_attribute="dexterity",
            resource_type=Resource_type.SPIRIT,
            max_resource=100,
            base_health=120,
            base_mana=0,
            allowed_weapon_types=["fist_weapon", "dagger", "staff", "sword"],
            allowed_armor_types=["light", "medium"],
            starting_attributes={
                "strength": 8,
                "dexterity": 15,
                "intelligence": 8,
                "vitality": 9
            },
            attribute_per_level={
                "strength": 1,
                "dexterity": 3,
                "intelligence": 1,
                "vitality": 2
            },
            skills=[
                SkillDefinition(
                    id="fists_of_thunder",
                    name="雷光拳",
                    description="快速连击，第三击释放闪电",
                    icon="skill_fists_thunder",
                    max_level=5,
                    required_level=1,
                    resource_cost=0,
                    damage_type=DamageType.LIGHTNING
                ),
                SkillDefinition(
                    id="dashing_strike",
                    name="疾风击",
                    description="瞬间移动到敌人身边进行攻击",
                    icon="skill_dashing_strike",
                    max_level=5,
                    required_level=8,
                    resource_cost=25,
                    cooldown=6,
                    damage_type=DamageType.PHYSICAL
                )
            ],
            lore="武僧是伊夫葛洛修道院的战士僧侣，通过严格的训练获得了超凡的武技和精神力量。"
        )
        
        cls._classes["wizard"] = CharacterClass(
            id="wizard",
            name="魔法师",
            description="操控奥术能量的施法者，能够释放毁灭性的元素魔法。",
            icon="wizard_icon",
            primary_attribute="intelligence",
            resource_type=Resource_type.MANA,
            max_resource=200,
            base_health=80,
            base_mana=150,
            allowed_weapon_types=["wand", "staff", "orb", "dagger"],
            allowed_armor_types=["cloth", "light"],
            starting_attributes={
                "strength": 5,
                "dexterity": 8,
                "intelligence": 15,
                "vitality": 7
            },
            attribute_per_level={
                "strength": 1,
                "dexterity": 1,
                "intelligence": 3,
                "vitality": 1
            },
            skills=[
                SkillDefinition(
                    id="magic_missile",
                    name="魔法飞弹",
                    description="发射追踪敌人的魔法飞弹",
                    icon="skill_magic_missile",
                    max_level=5,
                    required_level=1,
                    resource_cost=10,
                    damage_type=DamageType.ARCANE
                ),
                SkillDefinition(
                    id="meteor",
                    name="陨石术",
                    description="召唤陨石从天而降",
                    icon="skill_meteor",
                    max_level=5,
                    required_level=19,
                    resource_cost=50,
                    cooldown=12,
                    damage_type=DamageType.FIRE
                )
            ],
            lore="魔法师是来自仙塞学院的奥术大师，他们打破了传统魔法的束缚，自由操控各种元素力量。"
        )
        
        cls._classes["demon_hunter"] = CharacterClass(
            id="demon_hunter",
            name="猎魔人",
            description="以复仇为动力的远程战士，精通弓弩和暗影技巧。",
            icon="demon_hunter_icon",
            primary_attribute="dexterity",
            resource_type=Resource_type.HATRED,
            max_resource=100,
            base_health=100,
            base_mana=0,
            allowed_weapon_types=["bow", "crossbow", "dagger", "sword"],
            allowed_armor_types=["light", "medium"],
            starting_attributes={
                "strength": 6,
                "dexterity": 15,
                "intelligence": 7,
                "vitality": 8
            },
            attribute_per_level={
                "strength": 1,
                "dexterity": 3,
                "intelligence": 1,
                "vitality": 2
            },
            skills=[
                SkillDefinition(
                    id="hungering_arrow",
                    name="饥饿箭",
                    description="发射追踪敌人的箭矢",
                    icon="skill_hungering_arrow",
                    max_level=5,
                    required_level=1,
                    resource_cost=3,
                    damage_type=DamageType.PHYSICAL
                ),
                SkillDefinition(
                    id="multishot",
                    name="多重射击",
                    description="向多个方向发射箭矢",
                    icon="skill_multishot",
                    max_level=5,
                    required_level=12,
                    resource_cost=25,
                    damage_type=DamageType.PHYSICAL
                )
            ],
            lore="猎魔人是经历过恶魔袭击的幸存者，他们以复仇为动力，使用黑暗力量对抗地狱的入侵。"
        )
        
        cls._classes["necromancer"] = CharacterClass(
            id="necromancer",
            name="死灵法师",
            description="操控生死的法师，召唤亡灵大军并施展诅咒。",
            icon="necromancer_icon",
            primary_attribute="intelligence",
            resource_type=Resource_type.ESSENCE,
            max_resource=150,
            base_health=90,
            base_mana=100,
            allowed_weapon_types=["wand", "dagger", "staff", "orb"],
            allowed_armor_types=["cloth", "light"],
            starting_attributes={
                "strength": 6,
                "dexterity": 7,
                "intelligence": 15,
                "vitality": 8
            },
            attribute_per_level={
                "strength": 1,
                "dexterity": 1,
                "intelligence": 3,
                "vitality": 2
            },
            skills=[
                SkillDefinition(
                    id="raise_skeleton",
                    name="召唤骷髅",
                    description="召唤骷髅战士为你战斗",
                    icon="skill_raise_skeleton",
                    max_level=5,
                    required_level=1,
                    resource_cost=30,
                    damage_type=DamageType.PHYSICAL
                ),
                SkillDefinition(
                    id="bone_spear",
                    name="骨矛",
                    description="发射穿透敌人的骨矛",
                    icon="skill_bone_spear",
                    max_level=5,
                    required_level=8,
                    resource_cost=20,
                    damage_type=DamageType.PHYSICAL
                )
            ],
            lore="死灵法师是拉斯玛祭司团的成员，他们操控生死的平衡，使用白骨和鲜血的力量对抗邪恶。"
        )
        
        cls._classes["druid"] = CharacterClass(
            id="druid",
            name="德鲁伊",
            description="自然的守护者，能够变身为野兽并操控元素之力。",
            icon="druid_icon",
            primary_attribute="intelligence",
            resource_type=Resource_type.MANA,
            max_resource=120,
            base_health=110,
            base_mana=100,
            allowed_weapon_types=["staff", "dagger", "mace", "fist_weapon"],
            allowed_armor_types=["light", "medium"],
            starting_attributes={
                "strength": 8,
                "dexterity": 8,
                "intelligence": 12,
                "vitality": 10
            },
            attribute_per_level={
                "strength": 2,
                "dexterity": 1,
                "intelligence": 2,
                "vitality": 2
            },
            skills=[
                SkillDefinition(
                    id="werewolf",
                    name="狼人变身",
                    description="变身为狼人形态，提升攻击速度",
                    icon="skill_werewolf",
                    max_level=5,
                    required_level=1,
                    resource_cost=50,
                    damage_type=DamageType.PHYSICAL
                ),
                SkillDefinition(
                    id="tornado",
                    name="龙卷风",
                    description="召唤龙卷风攻击敌人",
                    icon="skill_tornado",
                    max_level=5,
                    required_level=12,
                    resource_cost=30,
                    damage_type=DamageType.COLD
                )
            ],
            lore="德鲁伊是凯吉斯坦森林的守护者，他们与自然融为一体，能够变身为野兽并召唤自然之力。"
        )
        
        cls._classes["assassin"] = CharacterClass(
            id="assassin",
            name="刺客",
            description="暗影中的杀手，精通陷阱和武术技巧。",
            icon="assassin_icon",
            primary_attribute="dexterity",
            resource_type=Resource_type.MANA,
            max_resource=100,
            base_health=95,
            base_mana=80,
            allowed_weapon_types=["dagger", "fist_weapon", "sword", "bow"],
            allowed_armor_types=["light", "medium"],
            starting_attributes={
                "strength": 7,
                "dexterity": 15,
                "intelligence": 10,
                "vitality": 8
            },
            attribute_per_level={
                "strength": 1,
                "dexterity": 3,
                "intelligence": 2,
                "vitality": 1
            },
            skills=[
                SkillDefinition(
                    id="tiger_strike",
                    name="虎击",
                    description="蓄力攻击，释放时造成巨额伤害",
                    icon="skill_tiger_strike",
                    max_level=5,
                    required_level=1,
                    resource_cost=5,
                    damage_type=DamageType.PHYSICAL
                ),
                SkillDefinition(
                    id="shadow_master",
                    name="影子大师",
                    description="召唤一个影子分身协助战斗",
                    icon="skill_shadow_master",
                    max_level=5,
                    required_level=30,
                    resource_cost=40,
                    cooldown=30,
                    damage_type=DamageType.SHADOW
                )
            ],
            lore="刺客是维兹杰雷法师杀手教团的成员，专门猎杀堕落的法师，以精湛的武术和陷阱技巧闻名。"
        )
        
        cls._classes["crusader"] = CharacterClass(
            id="crusader",
            name="圣教军",
            description="神圣的骑士，以坚定的信仰和强大的防御著称。",
            icon="crusader_icon",
            primary_attribute="strength",
            resource_type=Resource_type.WRATH,
            max_resource=100,
            base_health=140,
            base_mana=0,
            allowed_weapon_types=["sword", "mace", "shield", "flail"],
            allowed_armor_types=["heavy", "medium"],
            starting_attributes={
                "strength": 14,
                "dexterity": 7,
                "intelligence": 8,
                "vitality": 11
            },
            attribute_per_level={
                "strength": 3,
                "dexterity": 1,
                "intelligence": 1,
                "vitality": 2
            },
            skills=[
                SkillDefinition(
                    id="punish",
                    name="惩罚",
                    description="打击敌人并获得格挡加成",
                    icon="skill_punish",
                    max_level=5,
                    required_level=1,
                    resource_cost=5,
                    damage_type=DamageType.HOLY
                ),
                SkillDefinition(
                    id="akarat_champion",
                    name="阿卡拉特勇士",
                    description="变身为神圣战士，提升所有属性",
                    icon="skill_akarat",
                    max_level=5,
                    required_level=20,
                    resource_cost=50,
                    cooldown=90,
                    damage_type=DamageType.HOLY
                )
            ],
            lore="圣教军是圣教骑士团的精英战士，他们以坚定的信仰守护正义，对抗邪恶的入侵。"
        )
    
    @classmethod
    def get_class(cls, class_id: str) -> Optional[CharacterClass]:
        if not cls._initialized:
            cls.initialize()
        return cls._classes.get(class_id)
    
    @classmethod
    def get_all_classes(cls) -> Dict[str, CharacterClass]:
        if not cls._initialized:
            cls.initialize()
        return cls._classes.copy()
    
    @classmethod
    def get_class_ids(cls) -> List[str]:
        if not cls._initialized:
            cls.initialize()
        return list(cls._classes.keys())
    
    @classmethod
    def register_class(cls, character_class: CharacterClass):
        cls._classes[character_class.id] = character_class
