"""
技能核心类
"""
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import random
import math


class SkillType(Enum):
    ACTIVE = "active"
    PASSIVE = "passive"
    TOGGLE = "toggle"
    CHANNELING = "channeling"


class TargetType(Enum):
    SELF = "self"
    ENEMY = "enemy"
    ALLY = "ally"
    GROUND = "ground"
    AREA = "area"
    PROJECTILE = "projectile"
    NO_TARGET = "no_target"


class DamageType(Enum):
    PHYSICAL = "physical"
    FIRE = "fire"
    COLD = "cold"
    LIGHTNING = "lightning"
    POISON = "poison"
    HOLY = "holy"
    SHADOW = "shadow"
    ARCANE = "arcane"


@dataclass
class SkillBranch:
    id: str
    name: str
    description: str
    level_requirement: int = 1
    effects: Dict[str, float] = field(default_factory=dict)
    modifiers: Dict[str, float] = field(default_factory=dict)


@dataclass
class SkillLevelData:
    level: int
    damage_multiplier: float = 1.0
    resource_cost: float = 0
    cooldown: float = 0
    duration: float = 0
    range: float = 0
    area_of_effect: float = 0
    extra_effects: Dict[str, float] = field(default_factory=dict)


@dataclass
class Skill:
    id: str
    name: str
    description: str
    icon: str
    
    skill_type: SkillType
    target_type: TargetType
    damage_type: DamageType
    
    max_level: int = 5
    required_level: int = 1
    
    base_resource_cost: float = 0
    resource_type: str = "mana"
    
    base_cooldown: float = 0
    base_duration: float = 0
    base_range: float = 5.0
    base_area_of_effect: float = 0
    
    base_damage_min: float = 0
    base_damage_max: float = 0
    damage_multiplier: float = 1.0
    weapon_damage_percent: float = 0
    
    branches: List[SkillBranch] = field(default_factory=list)
    level_data: List[SkillLevelData] = field(default_factory=list)
    
    prerequisites: List[str] = field(default_factory=list)
    allowed_classes: List[str] = field(default_factory=list)
    
    animation: str = ""
    sound: str = ""
    particle_effect: str = ""
    
    def get_level_data(self, level: int) -> SkillLevelData:
        if level <= 0:
            return SkillLevelData(level=1)
        
        if level <= len(self.level_data):
            return self.level_data[level - 1]
        
        base = self.level_data[-1] if self.level_data else SkillLevelData(level=1)
        
        return SkillLevelData(
            level=level,
            damage_multiplier=base.damage_multiplier * (1 + (level - len(self.level_data)) * 0.1),
            resource_cost=base.resource_cost,
            cooldown=base.cooldown,
            duration=base.duration,
            range=base.range,
            area_of_effect=base.area_of_effect
        )
    
    def get_resource_cost(self, level: int, selected_branch: str = None) -> float:
        level_data = self.get_level_data(level)
        cost = level_data.resource_cost if level_data.resource_cost > 0 else self.base_resource_cost
        
        if selected_branch:
            for branch in self.branches:
                if branch.id == selected_branch:
                    cost *= branch.modifiers.get("resource_cost_multiplier", 1.0)
                    break
        
        return cost
    
    def get_cooldown(self, level: int, selected_branch: str = None) -> float:
        level_data = self.get_level_data(level)
        cooldown = level_data.cooldown if level_data.cooldown > 0 else self.base_cooldown
        
        if selected_branch:
            for branch in self.branches:
                if branch.id == selected_branch:
                    cooldown *= branch.modifiers.get("cooldown_multiplier", 1.0)
                    break
        
        return cooldown
    
    def get_damage(self, level: int, attack_power: float, weapon_damage: float = 0,
                   selected_branch: str = None) -> tuple:
        level_data = self.get_level_data(level)
        
        base_damage = random.uniform(self.base_damage_min, self.base_damage_max)
        weapon_contribution = weapon_damage * (self.weapon_damage_percent / 100)
        
        total_damage = (base_damage + weapon_contribution) * level_data.damage_multiplier
        
        total_damage += attack_power * self.damage_multiplier
        
        if selected_branch:
            for branch in self.branches:
                if branch.id == selected_branch:
                    total_damage *= branch.modifiers.get("damage_multiplier", 1.0)
                    break
        
        min_damage = total_damage * 0.8
        max_damage = total_damage * 1.2
        
        return (min_damage, max_damage)
    
    def get_range(self, level: int) -> float:
        level_data = self.get_level_data(level)
        return level_data.range if level_data.range > 0 else self.base_range
    
    def get_area_of_effect(self, level: int) -> float:
        level_data = self.get_level_data(level)
        return level_data.area_of_effect if level_data.area_of_effect > 0 else self.base_area_of_effect
    
    def can_use(self, caster, level: int, selected_branch: str = None) -> bool:
        if level <= 0 or level > self.max_level:
            return False
        
        resource_cost = self.get_resource_cost(level, selected_branch)
        if hasattr(caster, 'current_resource'):
            if caster.current_resource < resource_cost:
                return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "skill_type": self.skill_type.value,
            "target_type": self.target_type.value,
            "damage_type": self.damage_type.value,
            "max_level": self.max_level,
            "required_level": self.required_level,
            "base_resource_cost": self.base_resource_cost,
            "resource_type": self.resource_type,
            "base_cooldown": self.base_cooldown,
            "base_duration": self.base_duration,
            "base_range": self.base_range,
            "base_area_of_effect": self.base_area_of_effect,
            "base_damage_min": self.base_damage_min,
            "base_damage_max": self.base_damage_max,
            "damage_multiplier": self.damage_multiplier,
            "weapon_damage_percent": self.weapon_damage_percent,
            "branches": [{"id": b.id, "name": b.name, "description": b.description} for b in self.branches],
            "prerequisites": self.prerequisites,
            "allowed_classes": self.allowed_classes
        }


class SkillFactory:
    _skills: Dict[str, Skill] = {}
    _initialized = False
    
    @classmethod
    def initialize(cls):
        if cls._initialized:
            return
        
        cls._create_default_skills()
        cls._initialized = True
    
    @classmethod
    def _create_default_skills(cls):
        barbarian_skills = [
            Skill(
                id="bash",
                name="猛击",
                description="对敌人造成强力打击，生成怒气",
                icon="skill_bash",
                skill_type=SkillType.ACTIVE,
                target_type=TargetType.ENEMY,
                damage_type=DamageType.PHYSICAL,
                max_level=5,
                required_level=1,
                base_resource_cost=-6,
                resource_type="fury",
                base_damage_min=10,
                base_damage_max=20,
                weapon_damage_percent=150,
                branches=[
                    SkillBranch(
                        id="fury_bash",
                        name="狂暴猛击",
                        description="增加伤害和怒气生成",
                        level_requirement=1,
                        modifiers={"damage_multiplier": 1.3, "resource_cost_multiplier": 1.5}
                    ),
                    SkillBranch(
                        id="stun_bash",
                        name="眩晕猛击",
                        description="有几率眩晕敌人",
                        level_requirement=1,
                        effects={"stun_chance": 30, "stun_duration": 2}
                    ),
                    SkillBranch(
                        id="cleave",
                        name="横扫",
                        description="攻击前方多个敌人",
                        level_requirement=1,
                        modifiers={"area_of_effect": 3}
                    )
                ],
                allowed_classes=["barbarian"]
            ),
            Skill(
                id="whirlwind",
                name="旋风斩",
                description="旋转攻击周围所有敌人",
                icon="skill_whirlwind",
                skill_type=SkillType.CHANNELING,
                target_type=TargetType.AREA,
                damage_type=DamageType.PHYSICAL,
                max_level=5,
                required_level=12,
                base_resource_cost=10,
                resource_type="fury",
                base_damage_min=5,
                base_damage_max=10,
                weapon_damage_percent=50,
                base_area_of_effect=6,
                allowed_classes=["barbarian"]
            ),
            Skill(
                id="leap",
                name="跳跃攻击",
                description="跳向目标位置并造成范围伤害",
                icon="skill_leap",
                skill_type=SkillType.ACTIVE,
                target_type=TargetType.GROUND,
                damage_type=DamageType.PHYSICAL,
                max_level=5,
                required_level=8,
                base_resource_cost=15,
                resource_type="fury",
                base_cooldown=10,
                base_damage_min=50,
                base_damage_max=100,
                weapon_damage_percent=100,
                base_range=15,
                base_area_of_effect=4,
                allowed_classes=["barbarian"]
            ),
            Skill(
                id="ground_stomp",
                name="大地践踏",
                description="践踏地面，眩晕周围敌人",
                icon="skill_ground_stomp",
                skill_type=SkillType.ACTIVE,
                target_type=TargetType.AREA,
                damage_type=DamageType.PHYSICAL,
                max_level=5,
                required_level=15,
                base_resource_cost=20,
                resource_type="fury",
                base_cooldown=12,
                base_damage_min=30,
                base_damage_max=60,
                base_area_of_effect=8,
                allowed_classes=["barbarian"]
            ),
        ]
        
        wizard_skills = [
            Skill(
                id="magic_missile",
                name="魔法飞弹",
                description="发射追踪敌人的魔法飞弹",
                icon="skill_magic_missile",
                skill_type=SkillType.ACTIVE,
                target_type=TargetType.PROJECTILE,
                damage_type=DamageType.ARCANE,
                max_level=5,
                required_level=1,
                base_resource_cost=10,
                resource_type="mana",
                base_damage_min=15,
                base_damage_max=25,
                base_range=20,
                branches=[
                    SkillBranch(
                        id="multi_missile",
                        name="多重飞弹",
                        description="发射多枚飞弹",
                        level_requirement=1,
                        modifiers={"projectile_count": 3}
                    ),
                    SkillBranch(
                        id="seeking_missile",
                        name="追踪飞弹",
                        description="飞弹自动追踪敌人",
                        level_requirement=1,
                        effects={"homing": 100}
                    ),
                ],
                allowed_classes=["wizard"]
            ),
            Skill(
                id="meteor",
                name="陨石术",
                description="召唤陨石从天而降",
                icon="skill_meteor",
                skill_type=SkillType.ACTIVE,
                target_type=TargetType.GROUND,
                damage_type=DamageType.FIRE,
                max_level=5,
                required_level=19,
                base_resource_cost=50,
                resource_type="mana",
                base_cooldown=12,
                base_damage_min=200,
                base_damage_max=400,
                weapon_damage_percent=200,
                base_range=20,
                base_area_of_effect=6,
                allowed_classes=["wizard"]
            ),
            Skill(
                id="frost_nova",
                name="冰霜新星",
                description="释放冰霜能量，冻结周围敌人",
                icon="skill_frost_nova",
                skill_type=SkillType.ACTIVE,
                target_type=TargetType.AREA,
                damage_type=DamageType.COLD,
                max_level=5,
                required_level=8,
                base_resource_cost=25,
                resource_type="mana",
                base_cooldown=8,
                base_damage_min=30,
                base_damage_max=60,
                base_area_of_effect=8,
                allowed_classes=["wizard"]
            ),
            Skill(
                id="teleport",
                name="传送",
                description="瞬间移动到目标位置",
                icon="skill_teleport",
                skill_type=SkillType.ACTIVE,
                target_type=TargetType.GROUND,
                damage_type=DamageType.ARCANE,
                max_level=5,
                required_level=12,
                base_resource_cost=20,
                resource_type="mana",
                base_cooldown=10,
                base_range=25,
                allowed_classes=["wizard"]
            ),
        ]
        
        demon_hunter_skills = [
            Skill(
                id="hungering_arrow",
                name="饥饿箭",
                description="发射追踪敌人的箭矢",
                icon="skill_hungering_arrow",
                skill_type=SkillType.ACTIVE,
                target_type=TargetType.PROJECTILE,
                damage_type=DamageType.PHYSICAL,
                max_level=5,
                required_level=1,
                base_resource_cost=3,
                resource_type="hatred",
                base_damage_min=10,
                base_damage_max=20,
                weapon_damage_percent=100,
                base_range=25,
                allowed_classes=["demon_hunter"]
            ),
            Skill(
                id="multishot",
                name="多重射击",
                description="向多个方向发射箭矢",
                icon="skill_multishot",
                skill_type=SkillType.ACTIVE,
                target_type=TargetType.AREA,
                damage_type=DamageType.PHYSICAL,
                max_level=5,
                required_level=12,
                base_resource_cost=25,
                resource_type="hatred",
                base_damage_min=15,
                base_damage_max=30,
                weapon_damage_percent=80,
                base_area_of_effect=10,
                allowed_classes=["demon_hunter"]
            ),
            Skill(
                id="vault",
                name="翻滚",
                description="快速翻滚到目标位置",
                icon="skill_vault",
                skill_type=SkillType.ACTIVE,
                target_type=TargetType.GROUND,
                damage_type=DamageType.PHYSICAL,
                max_level=5,
                required_level=8,
                base_resource_cost=8,
                resource_type="discipline",
                base_cooldown=2,
                base_range=15,
                allowed_classes=["demon_hunter"]
            ),
        ]
        
        monk_skills = [
            Skill(
                id="fists_of_thunder",
                name="雷光拳",
                description="快速连击，第三击释放闪电",
                icon="skill_fists_thunder",
                skill_type=SkillType.ACTIVE,
                target_type=TargetType.ENEMY,
                damage_type=DamageType.LIGHTNING,
                max_level=5,
                required_level=1,
                base_resource_cost=0,
                resource_type="spirit",
                base_damage_min=8,
                base_damage_max=16,
                weapon_damage_percent=120,
                allowed_classes=["monk"]
            ),
            Skill(
                id="dashing_strike",
                name="疾风击",
                description="瞬间移动到敌人身边进行攻击",
                icon="skill_dashing_strike",
                skill_type=SkillType.ACTIVE,
                target_type=TargetType.ENEMY,
                damage_type=DamageType.PHYSICAL,
                max_level=5,
                required_level=8,
                base_resource_cost=25,
                resource_type="spirit",
                base_cooldown=6,
                base_damage_min=20,
                base_damage_max=40,
                weapon_damage_percent=100,
                base_range=20,
                allowed_classes=["monk"]
            ),
        ]
        
        necromancer_skills = [
            Skill(
                id="raise_skeleton",
                name="召唤骷髅",
                description="召唤骷髅战士为你战斗",
                icon="skill_raise_skeleton",
                skill_type=SkillType.ACTIVE,
                target_type=TargetType.NO_TARGET,
                damage_type=DamageType.PHYSICAL,
                max_level=5,
                required_level=1,
                base_resource_cost=30,
                resource_type="essence",
                base_cooldown=2,
                base_duration=60,
                allowed_classes=["necromancer"]
            ),
            Skill(
                id="bone_spear",
                name="骨矛",
                description="发射穿透敌人的骨矛",
                icon="skill_bone_spear",
                skill_type=SkillType.ACTIVE,
                target_type=TargetType.PROJECTILE,
                damage_type=DamageType.PHYSICAL,
                max_level=5,
                required_level=8,
                base_resource_cost=20,
                resource_type="essence",
                base_damage_min=50,
                base_damage_max=100,
                weapon_damage_percent=150,
                base_range=20,
                allowed_classes=["necromancer"]
            ),
        ]
        
        crusader_skills = [
            Skill(
                id="punish",
                name="惩罚",
                description="打击敌人并获得格挡加成",
                icon="skill_punish",
                skill_type=SkillType.ACTIVE,
                target_type=TargetType.ENEMY,
                damage_type=DamageType.HOLY,
                max_level=5,
                required_level=1,
                base_resource_cost=5,
                resource_type="wrath",
                base_damage_min=10,
                base_damage_max=20,
                weapon_damage_percent=130,
                allowed_classes=["crusader"]
            ),
            Skill(
                id="akarat_champion",
                name="阿卡拉特勇士",
                description="变身为神圣战士，提升所有属性",
                icon="skill_akarat",
                skill_type=SkillType.ACTIVE,
                target_type=TargetType.SELF,
                damage_type=DamageType.HOLY,
                max_level=5,
                required_level=20,
                base_resource_cost=50,
                resource_type="wrath",
                base_cooldown=90,
                base_duration=20,
                allowed_classes=["crusader"]
            ),
        ]
        
        druid_skills = [
            Skill(
                id="werewolf",
                name="狼人变身",
                description="变身为狼人形态，提升攻击速度",
                icon="skill_werewolf",
                skill_type=SkillType.TOGGLE,
                target_type=TargetType.SELF,
                damage_type=DamageType.PHYSICAL,
                max_level=5,
                required_level=1,
                base_resource_cost=50,
                resource_type="mana",
                allowed_classes=["druid"]
            ),
            Skill(
                id="tornado",
                name="龙卷风",
                description="召唤龙卷风攻击敌人",
                icon="skill_tornado",
                skill_type=SkillType.ACTIVE,
                target_type=TargetType.GROUND,
                damage_type=DamageType.COLD,
                max_level=5,
                required_level=12,
                base_resource_cost=30,
                resource_type="mana",
                base_damage_min=30,
                base_damage_max=60,
                base_duration=5,
                base_range=15,
                allowed_classes=["druid"]
            ),
        ]
        
        assassin_skills = [
            Skill(
                id="tiger_strike",
                name="虎击",
                description="蓄力攻击，释放时造成巨额伤害",
                icon="skill_tiger_strike",
                skill_type=SkillType.ACTIVE,
                target_type=TargetType.ENEMY,
                damage_type=DamageType.PHYSICAL,
                max_level=5,
                required_level=1,
                base_resource_cost=5,
                resource_type="mana",
                base_damage_min=5,
                base_damage_max=10,
                weapon_damage_percent=50,
                allowed_classes=["assassin"]
            ),
            Skill(
                id="shadow_master",
                name="影子大师",
                description="召唤一个影子分身协助战斗",
                icon="skill_shadow_master",
                skill_type=SkillType.ACTIVE,
                target_type=TargetType.NO_TARGET,
                damage_type=DamageType.SHADOW,
                max_level=5,
                required_level=30,
                base_resource_cost=40,
                resource_type="mana",
                base_cooldown=30,
                base_duration=60,
                allowed_classes=["assassin"]
            ),
        ]
        
        for skill in (barbarian_skills + wizard_skills + demon_hunter_skills + 
                      monk_skills + necromancer_skills + crusader_skills + 
                      druid_skills + assassin_skills):
            cls._skills[skill.id] = skill
    
    @classmethod
    def get_skill(cls, skill_id: str) -> Optional[Skill]:
        if not cls._initialized:
            cls.initialize()
        return cls._skills.get(skill_id)
    
    @classmethod
    def get_skills_for_class(cls, class_id: str) -> List[Skill]:
        if not cls._initialized:
            cls.initialize()
        
        return [
            skill for skill in cls._skills.values()
            if not skill.allowed_classes or class_id in skill.allowed_classes
        ]
    
    @classmethod
    def get_all_skills(cls) -> Dict[str, Skill]:
        if not cls._initialized:
            cls.initialize()
        return cls._skills.copy()
