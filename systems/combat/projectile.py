"""
投射物系统
"""
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import math


class ProjectileType(Enum):
    ARROW = "arrow"
    BOLT = "bolt"
    MAGIC_MISSILE = "magic_missile"
    FIREBALL = "fireball"
    ICE_BOLT = "ice_bolt"
    LIGHTNING = "lightning"
    BONE_SPEAR = "bone_spear"
    THROWING_KNIFE = "throwing_knife"


@dataclass
class Projectile:
    id: str
    projectile_type: ProjectileType
    
    position: Tuple[float, float]
    velocity: Tuple[float, float]
    
    damage: Tuple[float, float]
    damage_type: str
    
    owner_id: str
    target_id: Optional[str] = None
    
    speed: float = 10.0
    lifetime: float = 5.0
    age: float = 0.0
    
    piercing: int = 0
    pierce_count: int = 0
    
    homing: bool = False
    homing_strength: float = 0.0
    
    area_of_effect: float = 0.0
    aoe_damage_percent: float = 0.5
    
    hit_targets: List[str] = field(default_factory=list)
    
    sprite: str = ""
    scale: float = 1.0
    rotation: float = 0.0
    
    on_hit_callback: Optional[Callable] = None
    on_expire_callback: Optional[Callable] = None
    
    def update(self, delta_time: float, targets: List[Any] = None):
        self.age += delta_time
        
        if self.homing and targets:
            nearest = self._find_nearest_target(targets)
            if nearest:
                self._home_towards(nearest, delta_time)
        
        self.position = (
            self.position[0] + self.velocity[0] * delta_time,
            self.position[1] + self.velocity[1] * delta_time
        )
        
        self.rotation = math.atan2(self.velocity[1], self.velocity[0])
    
    def _find_nearest_target(self, targets: List[Any]) -> Optional[Any]:
        if not targets:
            return None
        
        nearest = None
        min_distance = float('inf')
        
        for target in targets:
            if hasattr(target, 'position') and hasattr(target, 'id'):
                if target.id in self.hit_targets or target.id == self.owner_id:
                    continue
                
                if not getattr(target, 'is_alive', True):
                    continue
                
                dx = target.position[0] - self.position[0]
                dy = target.position[1] - self.position[1]
                distance = math.sqrt(dx * dx + dy * dy)
                
                if distance < min_distance:
                    min_distance = distance
                    nearest = target
        
        return nearest
    
    def _home_towards(self, target: Any, delta_time: float):
        if not hasattr(target, 'position'):
            return
        
        dx = target.position[0] - self.position[0]
        dy = target.position[1] - self.position[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            target_dir = (dx / distance, dy / distance)
            
            current_speed = math.sqrt(
                self.velocity[0] ** 2 + self.velocity[1] ** 2
            )
            
            current_dir = (
                self.velocity[0] / current_speed if current_speed > 0 else 0,
                self.velocity[1] / current_speed if current_speed > 0 else 0
            )
            
            new_dir = (
                current_dir[0] + (target_dir[0] - current_dir[0]) * self.homing_strength * delta_time,
                current_dir[1] + (target_dir[1] - current_dir[1]) * self.homing_strength * delta_time
            )
            
            dir_length = math.sqrt(new_dir[0] ** 2 + new_dir[1] ** 2)
            if dir_length > 0:
                new_dir = (new_dir[0] / dir_length, new_dir[1] / dir_length)
            
            self.velocity = (
                new_dir[0] * current_speed,
                new_dir[1] * current_speed
            )
    
    def is_expired(self) -> bool:
        return self.age >= self.lifetime
    
    def check_collision(self, target: Any, hit_radius: float = 0.5) -> bool:
        if not hasattr(target, 'position'):
            return False
        
        if target.id in self.hit_targets:
            return False
        
        if hasattr(target, 'id') and target.id == self.owner_id:
            return False
        
        if not getattr(target, 'is_alive', True):
            return False
        
        dx = target.position[0] - self.position[0]
        dy = target.position[1] - self.position[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        return distance <= hit_radius
    
    def on_hit(self, target: Any) -> Dict[str, Any]:
        self.hit_targets.append(target.id)
        
        import random
        damage = random.uniform(self.damage[0], self.damage[1])
        
        result = {
            "damage": damage,
            "damage_type": self.damage_type,
            "target_id": target.id,
            "projectile_id": self.id
        }
        
        if self.piercing > 0 and self.pierce_count < self.piercing:
            self.pierce_count += 1
            result["destroy"] = False
        else:
            result["destroy"] = True
        
        if self.on_hit_callback:
            self.on_hit_callback(self, target, result)
        
        return result
    
    def get_aoe_targets(self, all_targets: List[Any], hit_radius: float = 0.5) -> List[Any]:
        if self.area_of_effect <= 0:
            return []
        
        aoe_targets = []
        
        for target in all_targets:
            if not hasattr(target, 'position'):
                continue
            
            if target.id in self.hit_targets:
                continue
            
            if not getattr(target, 'is_alive', True):
                continue
            
            dx = target.position[0] - self.position[0]
            dy = target.position[1] - self.position[1]
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance <= self.area_of_effect:
                aoe_targets.append(target)
        
        return aoe_targets


class ProjectileManager:
    def __init__(self):
        self.projectiles: Dict[str, Projectile] = {}
        self._next_id = 0
    
    def create_projectile(self, projectile_type: ProjectileType,
                          position: Tuple[float, float],
                          direction: Tuple[float, float],
                          speed: float,
                          damage: Tuple[float, float],
                          damage_type: str,
                          owner_id: str,
                          **kwargs) -> Projectile:
        proj_id = f"proj_{self._next_id}"
        self._next_id += 1
        
        velocity = (
            direction[0] * speed,
            direction[1] * speed
        )
        
        projectile = Projectile(
            id=proj_id,
            projectile_type=projectile_type,
            position=position,
            velocity=velocity,
            damage=damage,
            damage_type=damage_type,
            owner_id=owner_id,
            speed=speed,
            **kwargs
        )
        
        self.projectiles[proj_id] = projectile
        return projectile
    
    def remove_projectile(self, projectile_id: str):
        if projectile_id in self.projectiles:
            del self.projectiles[projectile_id]
    
    def update(self, delta_time: float, targets: List[Any] = None):
        to_remove = []
        
        for proj_id, projectile in self.projectiles.items():
            projectile.update(delta_time, targets)
            
            if projectile.is_expired():
                to_remove.append(proj_id)
                if projectile.on_expire_callback:
                    projectile.on_expire_callback(projectile)
        
        for proj_id in to_remove:
            self.remove_projectile(proj_id)
    
    def check_collisions(self, targets: List[Any], hit_radius: float = 0.5) -> List[Dict[str, Any]]:
        results = []
        to_remove = []
        
        for proj_id, projectile in self.projectiles.items():
            for target in targets:
                if projectile.check_collision(target, hit_radius):
                    result = projectile.on_hit(target)
                    results.append(result)
                    
                    if result.get("destroy", True):
                        to_remove.append(proj_id)
                    break
        
        for proj_id in to_remove:
            self.remove_projectile(proj_id)
        
        return results
    
    def get_projectiles(self) -> List[Projectile]:
        return list(self.projectiles.values())
    
    def get_projectiles_by_owner(self, owner_id: str) -> List[Projectile]:
        return [
            p for p in self.projectiles.values()
            if p.owner_id == owner_id
        ]
    
    def clear(self):
        self.projectiles.clear()
