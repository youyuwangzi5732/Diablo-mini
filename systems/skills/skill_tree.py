"""
技能树系统
"""
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json


class NodeType(Enum):
    SKILL = "skill"
    PASSIVE = "passive"
    ATTRIBUTE = "attribute"
    CHOICE = "choice"
    SOCKET = "socket"
    KEYSTONE = "keystone"


@dataclass
class SkillNode:
    id: str
    name: str
    description: str
    node_type: NodeType
    icon: str = ""
    
    position: Tuple[int, int] = (0, 0)
    
    max_points: int = 1
    current_points: int = 0
    
    skill_id: Optional[str] = None
    passive_id: Optional[str] = None
    
    effects: Dict[str, float] = field(default_factory=dict)
    
    prerequisites: List[str] = field(default_factory=list)
    connections: List[str] = field(default_factory=list)
    
    required_level: int = 1
    class_restriction: Optional[str] = None
    
    allocated: bool = False
    
    def can_allocate(self, allocated_nodes: Set[str], character_level: int, 
                     character_class: str = None) -> Tuple[bool, str]:
        if self.allocated and self.current_points >= self.max_points:
            return False, "已达到最大点数"
        
        if character_level < self.required_level:
            return False, f"需要等级 {self.required_level}"
        
        if self.class_restriction and character_class != self.class_restriction:
            return False, "职业限制"
        
        for prereq in self.prerequisites:
            if prereq not in allocated_nodes:
                return False, f"需要前置节点: {prereq}"
        
        connected = False
        for conn in self.connections:
            if conn in allocated_nodes:
                connected = True
                break
        
        if self.connections and not connected:
            return False, "需要连接到已分配节点"
        
        return True, ""
    
    def allocate(self) -> bool:
        if self.current_points < self.max_points:
            self.current_points += 1
            self.allocated = True
            return True
        return False
    
    def deallocate(self) -> bool:
        if self.current_points > 0:
            self.current_points -= 1
            if self.current_points == 0:
                self.allocated = False
            return True
        return False
    
    def get_effects(self) -> Dict[str, float]:
        if self.current_points == 0:
            return {}
        
        multiplier = self.current_points / self.max_points if self.max_points > 0 else 1
        return {k: v * self.current_points for k, v in self.effects.items()}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "node_type": self.node_type.value,
            "icon": self.icon,
            "position": self.position,
            "max_points": self.max_points,
            "current_points": self.current_points,
            "skill_id": self.skill_id,
            "passive_id": self.passive_id,
            "effects": self.effects,
            "prerequisites": self.prerequisites,
            "connections": self.connections,
            "required_level": self.required_level,
            "class_restriction": self.class_restriction,
            "allocated": self.allocated
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SkillNode':
        node = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            node_type=NodeType(data["node_type"]),
            icon=data.get("icon", ""),
            position=tuple(data.get("position", (0, 0))),
            max_points=data.get("max_points", 1),
            current_points=data.get("current_points", 0),
            skill_id=data.get("skill_id"),
            passive_id=data.get("passive_id"),
            effects=data.get("effects", {}),
            prerequisites=data.get("prerequisites", []),
            connections=data.get("connections", []),
            required_level=data.get("required_level", 1),
            class_restriction=data.get("class_restriction"),
            allocated=data.get("allocated", False)
        )
        return node


class SkillTree:
    def __init__(self, class_id: str = None):
        self.class_id = class_id
        self.nodes: Dict[str, SkillNode] = {}
        self.allocated_nodes: Set[str] = set()
        self.total_points = 0
        self.available_points = 0
        
        self._initialize_tree()
    
    def _initialize_tree(self):
        self._create_core_nodes()
        self._create_class_nodes()
        self._create_connections()
    
    def _create_core_nodes(self):
        core_nodes = [
            SkillNode(
                id="core_health_1",
                name="生命强化 I",
                description="增加最大生命值",
                node_type=NodeType.ATTRIBUTE,
                position=(0, 0),
                max_points=10,
                effects={"max_health_percent": 1},
                required_level=1
            ),
            SkillNode(
                id="core_health_2",
                name="生命强化 II",
                description="增加最大生命值",
                node_type=NodeType.ATTRIBUTE,
                position=(0, 2),
                max_points=10,
                effects={"max_health_percent": 1.5},
                prerequisites=["core_health_1"],
                required_level=10
            ),
            SkillNode(
                id="core_mana_1",
                name="法力强化 I",
                description="增加最大法力值",
                node_type=NodeType.ATTRIBUTE,
                position=(2, 0),
                max_points=10,
                effects={"max_mana_percent": 1},
                required_level=1
            ),
            SkillNode(
                id="core_damage_1",
                name="伤害强化 I",
                description="增加伤害",
                node_type=NodeType.ATTRIBUTE,
                position=(-2, 0),
                max_points=10,
                effects={"damage_percent": 1},
                required_level=1
            ),
            SkillNode(
                id="core_armor_1",
                name="护甲强化 I",
                description="增加护甲",
                node_type=NodeType.ATTRIBUTE,
                position=(0, -2),
                max_points=10,
                effects={"armor_percent": 1},
                required_level=1
            ),
        ]
        
        for node in core_nodes:
            self.nodes[node.id] = node
    
    def _create_class_nodes(self):
        class_nodes = {
            "barbarian": [
                SkillNode(
                    id="barbarian_fury_1",
                    name="怒气掌控",
                    description="增加怒气生成速度",
                    node_type=NodeType.PASSIVE,
                    position=(3, 0),
                    max_points=5,
                    effects={"fury_generation": 5},
                    class_restriction="barbarian",
                    required_level=5
                ),
                SkillNode(
                    id="barbarian_might_1",
                    name="蛮力",
                    description="增加力量",
                    node_type=NodeType.ATTRIBUTE,
                    position=(4, 1),
                    max_points=10,
                    effects={"strength": 5},
                    class_restriction="barbarian",
                    required_level=10
                ),
            ],
            "wizard": [
                SkillNode(
                    id="wizard_arcane_1",
                    name="奥术精通",
                    description="增加奥术伤害",
                    node_type=NodeType.PASSIVE,
                    position=(3, 0),
                    max_points=5,
                    effects={"arcane_damage_percent": 3},
                    class_restriction="wizard",
                    required_level=5
                ),
                SkillNode(
                    id="wizard_intellect_1",
                    name="智慧",
                    description="增加智力",
                    node_type=NodeType.ATTRIBUTE,
                    position=(4, 1),
                    max_points=10,
                    effects={"intelligence": 5},
                    class_restriction="wizard",
                    required_level=10
                ),
            ],
            "demon_hunter": [
                SkillNode(
                    id="dh_precision_1",
                    name="精准",
                    description="增加暴击率",
                    node_type=NodeType.PASSIVE,
                    position=(3, 0),
                    max_points=5,
                    effects={"crit_chance": 1},
                    class_restriction="demon_hunter",
                    required_level=5
                ),
            ],
            "monk": [
                SkillNode(
                    id="monk_spirit_1",
                    name="灵气汇聚",
                    description="增加灵气回复",
                    node_type=NodeType.PASSIVE,
                    position=(3, 0),
                    max_points=5,
                    effects={"spirit_regeneration": 5},
                    class_restriction="monk",
                    required_level=5
                ),
            ],
            "necromancer": [
                SkillNode(
                    id="necro_essence_1",
                    name="精华汲取",
                    description="增加精华回复",
                    node_type=NodeType.PASSIVE,
                    position=(3, 0),
                    max_points=5,
                    effects={"essence_regeneration": 5},
                    class_restriction="necromancer",
                    required_level=5
                ),
            ],
            "crusader": [
                SkillNode(
                    id="crusader_wrath_1",
                    name="神圣愤怒",
                    description="增加愤怒生成",
                    node_type=NodeType.PASSIVE,
                    position=(3, 0),
                    max_points=5,
                    effects={"wrath_generation": 5},
                    class_restriction="crusader",
                    required_level=5
                ),
            ],
            "druid": [
                SkillNode(
                    id="druid_nature_1",
                    name="自然之力",
                    description="增加自然伤害",
                    node_type=NodeType.PASSIVE,
                    position=(3, 0),
                    max_points=5,
                    effects={"nature_damage_percent": 3},
                    class_restriction="druid",
                    required_level=5
                ),
            ],
            "assassin": [
                SkillNode(
                    id="assassin_shadow_1",
                    name="暗影精通",
                    description="增加暗影伤害",
                    node_type=NodeType.PASSIVE,
                    position=(3, 0),
                    max_points=5,
                    effects={"shadow_damage_percent": 3},
                    class_restriction="assassin",
                    required_level=5
                ),
            ],
        }
        
        for class_id, nodes in class_nodes.items():
            for node in nodes:
                self.nodes[node.id] = node
    
    def _create_connections(self):
        connections = [
            ("core_health_1", "core_health_2"),
            ("core_health_1", "core_mana_1"),
            ("core_health_1", "core_damage_1"),
            ("core_health_1", "core_armor_1"),
        ]
        
        for node1_id, node2_id in connections:
            if node1_id in self.nodes and node2_id in self.nodes:
                self.nodes[node1_id].connections.append(node2_id)
                self.nodes[node2_id].connections.append(node1_id)
    
    def add_points(self, count: int):
        self.available_points += count
        self.total_points += count
    
    def allocate_node(self, node_id: str, character_level: int, 
                      character_class: str = None) -> Tuple[bool, str]:
        if self.available_points <= 0:
            return False, "没有可用点数"
        
        if node_id not in self.nodes:
            return False, "节点不存在"
        
        node = self.nodes[node_id]
        
        can_alloc, reason = node.can_allocate(
            self.allocated_nodes, character_level, character_class
        )
        
        if not can_alloc:
            return False, reason
        
        if node.allocate():
            self.allocated_nodes.add(node_id)
            self.available_points -= 1
            return True, ""
        
        return False, "分配失败"
    
    def deallocate_node(self, node_id: str) -> Tuple[bool, str]:
        if node_id not in self.nodes:
            return False, "节点不存在"
        
        node = self.nodes[node_id]
        
        for other_id in self.allocated_nodes:
            if other_id == node_id:
                continue
            other_node = self.nodes[other_id]
            if node_id in other_node.prerequisites:
                return False, f"节点 {other_id} 依赖此节点"
        
        if node.deallocate():
            if node.current_points == 0:
                self.allocated_nodes.discard(node_id)
            self.available_points += 1
            return True, ""
        
        return False, "取消分配失败"
    
    def reset_tree(self):
        for node in self.nodes.values():
            node.current_points = 0
            node.allocated = False
        
        self.available_points = self.total_points
        self.allocated_nodes.clear()
    
    def get_all_effects(self) -> Dict[str, float]:
        all_effects: Dict[str, float] = {}
        
        for node_id in self.allocated_nodes:
            node = self.nodes[node_id]
            effects = node.get_effects()
            for attr, value in effects.items():
                if attr in all_effects:
                    all_effects[attr] += value
                else:
                    all_effects[attr] = value
        
        return all_effects
    
    def get_node(self, node_id: str) -> Optional[SkillNode]:
        return self.nodes.get(node_id)
    
    def get_nodes_by_type(self, node_type: NodeType) -> List[SkillNode]:
        return [node for node in self.nodes.values() if node.node_type == node_type]
    
    def get_allocated_count(self) -> int:
        return sum(node.current_points for node in self.nodes.values())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "class_id": self.class_id,
            "nodes": {k: v.to_dict() for k, v in self.nodes.items()},
            "allocated_nodes": list(self.allocated_nodes),
            "total_points": self.total_points,
            "available_points": self.available_points
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SkillTree':
        tree = cls(data.get("class_id"))
        
        tree.nodes = {
            k: SkillNode.from_dict(v) for k, v in data.get("nodes", {}).items()
        }
        tree.allocated_nodes = set(data.get("allocated_nodes", []))
        tree.total_points = data.get("total_points", 0)
        tree.available_points = data.get("available_points", 0)
        
        return tree
