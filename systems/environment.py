"""
环境互动元素系统
"""
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import random


class InteractiveType(Enum):
    CHEST = "chest"
    BREAKABLE = "breakable"
    DOOR = "door"
    LEVER = "lever"
    SHRINE = "shrine"
    PORTAL = "portal"
    WAYPOINT = "waypoint"
    HIDDEN_AREA = "hidden_area"
    TRAP = "trap"
    LORE_BOOK = "lore_book"


class InteractiveState(Enum):
    INACTIVE = "inactive"
    ACTIVE = "active"
    USED = "used"
    DESTROYED = "destroyed"
    LOCKED = "locked"


@dataclass
class InteractiveObject:
    id: str
    name: str
    object_type: InteractiveType
    
    position: Tuple[float, float]
    size: Tuple[float, float] = (1.0, 1.0)
    
    state: InteractiveState = InteractiveState.ACTIVE
    
    interaction_range: float = 1.5
    
    required_level: int = 1
    required_key: Optional[str] = None
    required_quest: Optional[str] = None
    
    on_interact: Optional[Callable] = None
    
    loot_table_id: Optional[str] = None
    guaranteed_loot: List[str] = field(default_factory=list)
    
    health: int = 100
    max_health: int = 100
    
    respawn_time: float = 300.0
    time_since_used: float = 0.0
    
    is_hidden: bool = False
    reveal_range: float = 2.0
    
    triggers: List[str] = field(default_factory=list)
    
    def can_interact(self, player: Any) -> Tuple[bool, str]:
        if self.state == InteractiveState.DESTROYED:
            return False, "已损坏"
        
        if self.state == InteractiveState.USED:
            return False, "已使用"
        
        if self.state == InteractiveState.LOCKED:
            if self.required_key:
                if not hasattr(player, 'has_item') or not player.has_item(self.required_key):
                    return False, f"需要钥匙"
            return False, "已锁定"
        
        if self.required_level > 0:
            player_level = getattr(player, 'level', 1)
            if player_level < self.required_level:
                return False, f"需要等级 {self.required_level}"
        
        if self.required_quest:
            if hasattr(player, 'completed_quests'):
                if self.required_quest not in player.completed_quests:
                    return False, "需要完成任务"
        
        return True, ""
    
    def interact(self, player: Any) -> Dict[str, Any]:
        can_interact, message = self.can_interact(player)
        
        if not can_interact:
            return {"success": False, "message": message}
        
        result = {
            "success": True,
            "message": "",
            "loot": [],
            "triggers": self.triggers.copy()
        }
        
        if self.object_type == InteractiveType.CHEST:
            result.update(self._open_chest(player))
        
        elif self.object_type == InteractiveType.BREAKABLE:
            result.update(self._break_object(player))
        
        elif self.object_type == InteractiveType.DOOR:
            result.update(self._open_door(player))
        
        elif self.object_type == InteractiveType.LEVER:
            result.update(self._activate_lever(player))
        
        elif self.object_type == InteractiveType.SHRINE:
            result.update(self._activate_shrine(player))
        
        elif self.object_type == InteractiveType.PORTAL:
            result.update(self._use_portal(player))
        
        elif self.object_type == InteractiveType.WAYPOINT:
            result.update(self._activate_waypoint(player))
        
        elif self.object_type == InteractiveType.LORE_BOOK:
            result.update(self._read_lore_book(player))
        
        if self.on_interact:
            try:
                self.on_interact(self, player, result)
            except Exception as e:
                print(f"Interactive callback error: {e}")
        
        return result
    
    def _open_chest(self, player: Any) -> Dict[str, Any]:
        self.state = InteractiveState.USED
        
        loot = []
        
        for item_id in self.guaranteed_loot:
            loot.append({"type": "item", "id": item_id})
        
        if self.loot_table_id:
            pass
        
        return {
            "message": "打开了宝箱",
            "loot": loot
        }
    
    def _break_object(self, player: Any) -> Dict[str, Any]:
        self.state = InteractiveState.DESTROYED
        
        loot = []
        
        if random.random() < 0.3:
            gold = random.randint(1, 10)
            loot.append({"type": "gold", "amount": gold})
        
        if random.random() < 0.1:
            loot.append({"type": "item", "id": "health_potion_small"})
        
        return {
            "message": "破坏了物体",
            "loot": loot
        }
    
    def _open_door(self, player: Any) -> Dict[str, Any]:
        if self.state == InteractiveState.ACTIVE:
            self.state = InteractiveState.INACTIVE
            return {"message": "门已打开"}
        else:
            self.state = InteractiveState.ACTIVE
            return {"message": "门已关闭"}
    
    def _activate_lever(self, player: Any) -> Dict[str, Any]:
        if self.state == InteractiveState.ACTIVE:
            self.state = InteractiveState.INACTIVE
        else:
            self.state = InteractiveState.ACTIVE
        
        return {"message": "拉动了开关"}
    
    def _activate_shrine(self, player: Any) -> Dict[str, Any]:
        self.state = InteractiveState.USED
        
        effects = []
        
        shrine_types = ["fortune", "combat", "protection", "experience"]
        shrine_type = random.choice(shrine_types)
        
        if shrine_type == "fortune":
            effects.append({"type": "magic_find", "value": 25, "duration": 120})
            return {"message": "幸运神殿：魔法寻找+25%，持续2分钟", "effects": effects}
        
        elif shrine_type == "combat":
            effects.append({"type": "damage", "value": 10, "duration": 120})
            return {"message": "战斗神殿：伤害+10%，持续2分钟", "effects": effects}
        
        elif shrine_type == "protection":
            effects.append({"type": "armor", "value": 25, "duration": 120})
            return {"message": "守护神殿：护甲+25%，持续2分钟", "effects": effects}
        
        else:
            effects.append({"type": "experience", "value": 25, "duration": 120})
            return {"message": "经验神殿：经验获取+25%，持续2分钟", "effects": effects}
    
    def _use_portal(self, player: Any) -> Dict[str, Any]:
        return {
            "message": "使用了传送门",
            "teleport": True,
            "destination": "tristram"
        }
    
    def _activate_waypoint(self, player: Any) -> Dict[str, Any]:
        return {
            "message": "激活了传送点",
            "waypoint_activated": True
        }
    
    def _read_lore_book(self, player: Any) -> Dict[str, Any]:
        self.state = InteractiveState.USED
        
        return {
            "message": "阅读了古籍",
            "lore_discovered": True
        }
    
    def take_damage(self, amount: int) -> bool:
        if self.object_type != InteractiveType.BREAKABLE:
            return False
        
        self.health -= amount
        
        if self.health <= 0:
            self.state = InteractiveState.DESTROYED
            return True
        
        return False
    
    def update(self, delta_time: float):
        if self.state == InteractiveState.USED or self.state == InteractiveState.DESTROYED:
            self.time_since_used += delta_time
            
            if self.time_since_used >= self.respawn_time:
                self.state = InteractiveState.ACTIVE
                self.health = self.max_health
                self.time_since_used = 0.0
    
    def is_in_range(self, position: Tuple[float, float]) -> bool:
        dx = position[0] - self.position[0]
        dy = position[1] - self.position[1]
        distance = (dx * dx + dy * dy) ** 0.5
        return distance <= self.interaction_range
    
    def reveal_if_hidden(self, position: Tuple[float, float]) -> bool:
        if not self.is_hidden:
            return False
        
        dx = position[0] - self.position[0]
        dy = position[1] - self.position[1]
        distance = (dx * dx + dy * dy) ** 0.5
        
        if distance <= self.reveal_range:
            self.is_hidden = False
            return True
        
        return False


class EnvironmentManager:
    def __init__(self):
        self.objects: Dict[str, InteractiveObject] = {}
        self._next_id = 0
    
    def create_object(self, object_type: InteractiveType, position: Tuple[float, float],
                      name: str = "", **kwargs) -> InteractiveObject:
        obj_id = f"obj_{self._next_id}"
        self._next_id += 1
        
        obj = InteractiveObject(
            id=obj_id,
            name=name or object_type.value,
            object_type=object_type,
            position=position,
            **kwargs
        )
        
        self.objects[obj_id] = obj
        return obj
    
    def get_object(self, obj_id: str) -> Optional[InteractiveObject]:
        return self.objects.get(obj_id)
    
    def get_objects_in_range(self, position: Tuple[float, float],
                              range_limit: float) -> List[InteractiveObject]:
        nearby = []
        
        for obj in self.objects.values():
            if obj.is_hidden:
                continue
            
            dx = position[0] - obj.position[0]
            dy = position[1] - obj.position[1]
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance <= range_limit:
                nearby.append(obj)
        
        return nearby
    
    def get_nearest_interactive(self, position: Tuple[float, float]) -> Optional[InteractiveObject]:
        nearest = None
        min_distance = float('inf')
        
        for obj in self.objects.values():
            if obj.is_hidden or obj.state in [InteractiveState.USED, InteractiveState.DESTROYED]:
                continue
            
            dx = position[0] - obj.position[0]
            dy = position[1] - obj.position[1]
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance <= obj.interaction_range and distance < min_distance:
                min_distance = distance
                nearest = obj
        
        return nearest
    
    def update(self, delta_time: float, player_position: Tuple[float, float] = None):
        for obj in self.objects.values():
            obj.update(delta_time)
            
            if player_position and obj.is_hidden:
                obj.reveal_if_hidden(player_position)
    
    def remove_object(self, obj_id: str):
        if obj_id in self.objects:
            del self.objects[obj_id]
    
    def clear(self):
        self.objects.clear()
    
    def spawn_chest(self, position: Tuple[float, float], 
                    loot_table_id: str = None,
                    guaranteed_loot: List[str] = None,
                    locked: bool = False) -> InteractiveObject:
        return self.create_object(
            InteractiveType.CHEST,
            position,
            name="宝箱",
            loot_table_id=loot_table_id,
            guaranteed_loot=guaranteed_loot or [],
            state=InteractiveState.LOCKED if locked else InteractiveState.ACTIVE
        )
    
    def spawn_breakable(self, position: Tuple[float, float],
                        health: int = 50) -> InteractiveObject:
        return self.create_object(
            InteractiveType.BREAKABLE,
            position,
            name="可破坏物体",
            health=health,
            max_health=health
        )
    
    def spawn_waypoint(self, position: Tuple[float, float],
                       name: str = "传送点") -> InteractiveObject:
        return self.create_object(
            InteractiveType.WAYPOINT,
            position,
            name=name
        )
    
    def spawn_shrine(self, position: Tuple[float, float]) -> InteractiveObject:
        return self.create_object(
            InteractiveType.SHRINE,
            position,
            name="神殿"
        )
