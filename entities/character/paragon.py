"""
巅峰等级系统
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class ParagonCategory(Enum):
    CORE = "core"
    OFFENSE = "offense"
    DEFENSE = "defense"
    UTILITY = "utility"


@dataclass
class ParagonNode:
    id: str
    name: str
    description: str
    category: ParagonCategory
    max_points: int = 50
    effect_per_point: float = 1.0
    effect_type: str = ""
    icon: str = ""
    prerequisites: List[str] = field(default_factory=list)
    position: tuple = (0, 0)


class ParagonSystem:
    POINTS_PER_LEVEL = 4
    
    def __init__(self):
        self.paragon_level = 0
        self.total_points = 0
        self.spent_points: Dict[str, int] = {}
        self.available_points = 0
        
        self._nodes: Dict[str, ParagonNode] = {}
        self._initialize_nodes()
    
    def _initialize_nodes(self):
        core_nodes = [
            ParagonNode(
                id="strength",
                name="力量",
                description="每点增加5点力量",
                category=ParagonCategory.CORE,
                max_points=50,
                effect_per_point=5,
                effect_type="strength"
            ),
            ParagonNode(
                id="dexterity",
                name="敏捷",
                description="每点增加5点敏捷",
                category=ParagonCategory.CORE,
                max_points=50,
                effect_per_point=5,
                effect_type="dexterity"
            ),
            ParagonNode(
                id="intelligence",
                name="智力",
                description="每点增加5点智力",
                category=ParagonCategory.CORE,
                max_points=50,
                effect_per_point=5,
                effect_type="intelligence"
            ),
            ParagonNode(
                id="vitality",
                name="体能",
                description="每点增加5点体能",
                category=ParagonCategory.CORE,
                max_points=50,
                effect_per_point=5,
                effect_type="vitality"
            ),
        ]
        
        offense_nodes = [
            ParagonNode(
                id="attack_speed",
                name="攻击速度",
                description="每点增加0.2%攻击速度",
                category=ParagonCategory.OFFENSE,
                max_points=50,
                effect_per_point=0.2,
                effect_type="attack_speed_percent"
            ),
            ParagonNode(
                id="crit_chance",
                name="暴击率",
                description="每点增加0.1%暴击率",
                category=ParagonCategory.OFFENSE,
                max_points=50,
                effect_per_point=0.1,
                effect_type="crit_chance"
            ),
            ParagonNode(
                id="crit_damage",
                name="暴击伤害",
                description="每点增加1%暴击伤害",
                category=ParagonCategory.OFFENSE,
                max_points=50,
                effect_per_point=1.0,
                effect_type="crit_damage"
            ),
            ParagonNode(
                id="cooldown_reduction",
                name="冷却缩减",
                description="每点增加0.2%冷却缩减",
                category=ParagonCategory.OFFENSE,
                max_points=50,
                effect_per_point=0.2,
                effect_type="cooldown_reduction"
            ),
        ]
        
        defense_nodes = [
            ParagonNode(
                id="max_health",
                name="最大生命",
                description="每点增加0.5%最大生命",
                category=ParagonCategory.DEFENSE,
                max_points=50,
                effect_per_point=0.5,
                effect_type="max_health_percent"
            ),
            ParagonNode(
                id="armor",
                name="护甲",
                description="每点增加0.5%护甲",
                category=ParagonCategory.DEFENSE,
                max_points=50,
                effect_per_point=0.5,
                effect_type="armor_percent"
            ),
            ParagonNode(
                id="all_resist",
                name="全抗性",
                description="每点增加5点全抗性",
                category=ParagonCategory.DEFENSE,
                max_points=50,
                effect_per_point=5,
                effect_type="all_resist"
            ),
            ParagonNode(
                id="health_regen",
                name="生命回复",
                description="每点增加100点每秒生命回复",
                category=ParagonCategory.DEFENSE,
                max_points=50,
                effect_per_point=100,
                effect_type="health_regen"
            ),
        ]
        
        utility_nodes = [
            ParagonNode(
                id="movement_speed",
                name="移动速度",
                description="每点增加0.5%移动速度",
                category=ParagonCategory.UTILITY,
                max_points=50,
                effect_per_point=0.5,
                effect_type="movement_speed_percent"
            ),
            ParagonNode(
                id="gold_find",
                name="金币获取",
                description="每点增加2%金币获取",
                category=ParagonCategory.UTILITY,
                max_points=50,
                effect_per_point=2.0,
                effect_type="gold_find"
            ),
            ParagonNode(
                id="magic_find",
                name="魔法寻找",
                description="每点增加2%魔法寻找",
                category=ParagonCategory.UTILITY,
                max_points=50,
                effect_per_point=2.0,
                effect_type="magic_find"
            ),
            ParagonNode(
                id="resource_cost_reduction",
                name="消耗降低",
                description="每点降低0.2%资源消耗",
                category=ParagonCategory.UTILITY,
                max_points=50,
                effect_per_point=0.2,
                effect_type="resource_cost_reduction"
            ),
        ]
        
        for node in core_nodes + offense_nodes + defense_nodes + utility_nodes:
            self._nodes[node.id] = node
            self.spent_points[node.id] = 0
    
    def add_experience(self, amount: int) -> int:
        levels_gained = 0
        
        return levels_gained
    
    def get_experience_for_level(self, level: int) -> int:
        return int(1000 * (level ** 1.5))
    
    def level_up(self):
        self.paragon_level += 1
        self.total_points += self.POINTS_PER_LEVEL
        self.available_points += self.POINTS_PER_LEVEL
    
    def spend_point(self, node_id: str) -> bool:
        if node_id not in self._nodes:
            return False
        
        if self.available_points <= 0:
            return False
        
        current = self.spent_points.get(node_id, 0)
        max_points = self._nodes[node_id].max_points
        
        if current >= max_points:
            return False
        
        self.spent_points[node_id] = current + 1
        self.available_points -= 1
        return True
    
    def remove_point(self, node_id: str) -> bool:
        if node_id not in self._nodes:
            return False
        
        current = self.spent_points.get(node_id, 0)
        if current <= 0:
            return False
        
        self.spent_points[node_id] = current - 1
        self.available_points += 1
        return True
    
    def reset_points(self):
        for node_id in self.spent_points:
            self.spent_points[node_id] = 0
        self.available_points = self.total_points
    
    def get_node_effect(self, node_id: str) -> float:
        if node_id not in self._nodes:
            return 0.0
        
        points = self.spent_points.get(node_id, 0)
        effect = self._nodes[node_id].effect_per_point
        return points * effect
    
    def get_all_effects(self) -> Dict[str, float]:
        effects = {}
        for node_id in self._nodes:
            effect_type = self._nodes[node_id].effect_type
            if effect_type:
                if effect_type not in effects:
                    effects[effect_type] = 0
                effects[effect_type] += self.get_node_effect(node_id)
        return effects
    
    def get_category_points(self, category: ParagonCategory) -> Dict[str, int]:
        return {
            node_id: points
            for node_id, points in self.spent_points.items()
            if self._nodes[node_id].category == category
        }
    
    def get_nodes_by_category(self, category: ParagonCategory) -> List[ParagonNode]:
        return [node for node in self._nodes.values() if node.category == category]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "paragon_level": self.paragon_level,
            "total_points": self.total_points,
            "spent_points": self.spent_points.copy(),
            "available_points": self.available_points
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ParagonSystem':
        system = cls()
        system.paragon_level = data.get("paragon_level", 0)
        system.total_points = data.get("total_points", 0)
        system.available_points = data.get("available_points", 0)
        
        for node_id, points in data.get("spent_points", {}).items():
            if node_id in system.spent_points:
                system.spent_points[node_id] = points
        
        return system
