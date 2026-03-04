"""
区域切换系统
"""
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import random

from systems.world.world import World, Area, AreaConnection
from systems.combat.monster import Monster, MonsterFactory


class TransitionType(Enum):
    WALK = "walk"
    PORTAL = "portal"
    WAYPOINT = "waypoint"
    DEATH = "death"
    TELEPORT = "teleport"


@dataclass
class AreaTransition:
    from_area_id: str
    to_area_id: str
    transition_type: TransitionType
    spawn_position: Tuple[float, float]
    required_level: int = 1
    required_quest: Optional[str] = None


@dataclass
class TransitionResult:
    success: bool
    message: str
    new_area_id: Optional[str] = None
    spawn_position: Optional[Tuple[float, float]] = None
    monsters_to_spawn: List[Dict] = field(default_factory=list)


class AreaTransitionManager:
    def __init__(self, world: World):
        self.world = world
        self.transition_callbacks: List[Callable] = []
        
        self.pending_transition: Optional[AreaTransition] = None
        self.transition_cooldown: float = 0.0
        self.cooldown_duration: float = 1.0
    
    def check_for_transition(self, player_pos: Tuple[float, float], 
                             player_level: int,
                             completed_quests: set) -> Optional[AreaTransition]:
        if self.transition_cooldown > 0:
            return None
        
        current_area = self.world.get_current_area()
        if not current_area:
            return None
        
        for conn in current_area.connections:
            conn_pos = conn.position
            
            distance = (
                (player_pos[0] - conn_pos[0]) ** 2 +
                (player_pos[1] - conn_pos[1]) ** 2
            ) ** 0.5
            
            if distance < 2.0:
                can_transition, reason = self._can_transition(
                    conn, player_level, completed_quests
                )
                
                if can_transition:
                    return AreaTransition(
                        from_area_id=current_area.id,
                        to_area_id=conn.target_area_id,
                        transition_type=TransitionType.WALK,
                        spawn_position=self._get_spawn_position(conn.target_area_id, current_area.id),
                        required_level=conn.required_level,
                        required_quest=conn.required_quest
                    )
        
        return None
    
    def _can_transition(self, connection: AreaConnection, 
                        player_level: int,
                        completed_quests: set) -> Tuple[bool, str]:
        if player_level < connection.required_level:
            return False, f"需要等级 {connection.required_level}"
        
        if connection.required_quest and connection.required_quest not in completed_quests:
            return False, "需要完成前置任务"
        
        target_area = self.world.get_area(connection.target_area_id)
        if not target_area:
            return False, "目标区域不存在"
        
        return True, ""
    
    def _get_spawn_position(self, target_area_id: str, 
                            from_area_id: str) -> Tuple[float, float]:
        target_area = self.world.get_area(target_area_id)
        if not target_area:
            return (0.0, 0.0)
        
        for conn in target_area.connections:
            if conn.target_area_id == from_area_id:
                return conn.position
        
        if target_area.is_safe_zone:
            return (target_area.width // 2, target_area.height // 2)
        
        return (target_area.width // 2, target_area.height // 2)
    
    def execute_transition(self, transition: AreaTransition) -> TransitionResult:
        target_area = self.world.get_area(transition.to_area_id)
        if not target_area:
            return TransitionResult(False, "目标区域不存在")
        
        self.world.change_area(transition.to_area_id)
        
        monsters_to_spawn = self._generate_monsters_for_area(target_area)
        
        self.transition_cooldown = self.cooldown_duration
        
        for callback in self.transition_callbacks:
            callback(transition)
        
        return TransitionResult(
            success=True,
            message=f"进入了 {target_area.name}",
            new_area_id=transition.to_area_id,
            spawn_position=transition.spawn_position,
            monsters_to_spawn=monsters_to_spawn
        )
    
    def _generate_monsters_for_area(self, area: Area) -> List[Dict]:
        monsters = []
        
        for spawn_data in area.monster_spawns:
            monster_id = spawn_data.get("monster_id")
            count = spawn_data.get("count", 1)
            level = spawn_data.get("level", 1)
            is_elite = spawn_data.get("elite", False)
            is_boss = spawn_data.get("boss", False)
            
            for _ in range(count):
                spawn_x = random.uniform(5, area.width - 5)
                spawn_y = random.uniform(5, area.height - 5)
                
                monsters.append({
                    "monster_id": monster_id,
                    "level": level,
                    "position": (spawn_x, spawn_y),
                    "is_elite": is_elite,
                    "is_boss": is_boss
                })
        
        return monsters
    
    def teleport_to_area(self, area_id: str, 
                         spawn_position: Tuple[float, float],
                         player_level: int) -> TransitionResult:
        target_area = self.world.get_area(area_id)
        if not target_area:
            return TransitionResult(False, "目标区域不存在")
        
        if player_level < target_area.level_range[0]:
            return TransitionResult(False, f"需要等级 {target_area.level_range[0]}")
        
        transition = AreaTransition(
            from_area_id=self.world.current_area_id,
            to_area_id=area_id,
            transition_type=TransitionType.WAYPOINT,
            spawn_position=spawn_position
        )
        
        return self.execute_transition(transition)
    
    def portal_to_area(self, area_id: str,
                       player_level: int,
                       completed_quests: set) -> TransitionResult:
        target_area = self.world.get_area(area_id)
        if not target_area:
            return TransitionResult(False, "目标区域不存在")
        
        spawn_pos = (target_area.width // 2, target_area.height // 2)
        
        transition = AreaTransition(
            from_area_id=self.world.current_area_id,
            to_area_id=area_id,
            transition_type=TransitionType.PORTAL,
            spawn_position=spawn_pos
        )
        
        return self.execute_transition(transition)
    
    def respawn_in_town(self) -> TransitionResult:
        town_id = "tristram"
        town = self.world.get_area(town_id)
        
        if not town:
            return TransitionResult(False, "无法找到城镇")
        
        spawn_pos = (town.width // 2, town.height // 2)
        
        transition = AreaTransition(
            from_area_id=self.world.current_area_id,
            to_area_id=town_id,
            transition_type=TransitionType.DEATH,
            spawn_position=spawn_pos
        )
        
        return self.execute_transition(transition)
    
    def add_transition_callback(self, callback: Callable):
        self.transition_callbacks.append(callback)
    
    def update(self, delta_time: float):
        if self.transition_cooldown > 0:
            self.transition_cooldown -= delta_time
    
    def get_nearby_transitions(self, player_pos: Tuple[float, float],
                               player_level: int,
                               completed_quests: set) -> List[Dict]:
        transitions = []
        current_area = self.world.get_current_area()
        
        if not current_area:
            return transitions
        
        for conn in current_area.connections:
            conn_pos = conn.position
            distance = (
                (player_pos[0] - conn_pos[0]) ** 2 +
                (player_pos[1] - conn_pos[1]) ** 2
            ) ** 0.5
            
            target_area = self.world.get_area(conn.target_area_id)
            if target_area:
                can_transition, reason = self._can_transition(
                    conn, player_level, completed_quests
                )
                
                transitions.append({
                    "target_area_id": conn.target_area_id,
                    "target_area_name": target_area.name,
                    "position": conn_pos,
                    "distance": distance,
                    "can_transition": can_transition,
                    "reason": reason,
                    "required_level": conn.required_level
                })
        
        return transitions
    
    def is_in_transition_range(self, player_pos: Tuple[float, float]) -> bool:
        current_area = self.world.get_current_area()
        if not current_area:
            return False
        
        for conn in current_area.connections:
            conn_pos = conn.position
            distance = (
                (player_pos[0] - conn_pos[0]) ** 2 +
                (player_pos[1] - conn_pos[1]) ** 2
            ) ** 0.5
            
            if distance < 2.0:
                return True
        
        return False
