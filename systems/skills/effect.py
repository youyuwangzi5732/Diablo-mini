"""
效果系统 - 处理技能效果、增益、减益等
"""
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import time


class EffectType(Enum):
    BUFF = "buff"
    DEBUFF = "debuff"
    DOT = "dot"
    HOT = "hot"
    SHIELD = "shield"
    CONTROL = "control"
    AURA = "aura"
    TRIGGER = "trigger"


class ControlType(Enum):
    STUN = "stun"
    FREEZE = "freeze"
    ROOT = "root"
    SLOW = "slow"
    SILENCE = "silence"
    BLIND = "blind"
    CHARM = "charm"
    FEAR = "fear"
    KNOCKBACK = "knockback"
    PULL = "pull"


@dataclass
class Effect:
    id: str
    name: str
    effect_type: EffectType
    duration: float
    
    source_id: str = ""
    target_id: str = ""
    
    effects: Dict[str, float] = field(default_factory=dict)
    
    tick_interval: float = 1.0
    tick_damage: float = 0
    tick_heal: float = 0
    damage_type: str = "physical"
    
    control_type: Optional[ControlType] = None
    
    stackable: bool = False
    max_stacks: int = 1
    current_stacks: int = 1
    
    icon: str = ""
    particle_effect: str = ""
    
    start_time: float = field(default_factory=time.time)
    last_tick_time: float = 0
    
    on_apply: Optional[Callable] = None
    on_remove: Optional[Callable] = None
    on_tick: Optional[Callable] = None
    
    def __post_init__(self):
        self.start_time = time.time()
        self.last_tick_time = self.start_time
    
    def is_expired(self) -> bool:
        if self.duration <= 0:
            return False
        return time.time() - self.start_time >= self.duration
    
    def get_remaining_time(self) -> float:
        if self.duration <= 0:
            return float('inf')
        remaining = self.duration - (time.time() - self.start_time)
        return max(0, remaining)
    
    def get_progress(self) -> float:
        if self.duration <= 0:
            return 0
        return min(1.0, (time.time() - self.start_time) / self.duration)
    
    def should_tick(self) -> bool:
        if self.tick_interval <= 0:
            return False
        return time.time() - self.last_tick_time >= self.tick_interval
    
    def tick(self) -> Dict[str, Any]:
        self.last_tick_time = time.time()
        
        result = {
            "damage": self.tick_damage * self.current_stacks,
            "heal": self.tick_heal * self.current_stacks,
            "damage_type": self.damage_type
        }
        
        if self.on_tick:
            try:
                self.on_tick(self)
            except Exception as e:
                print(f"Effect tick callback error: {e}")
        
        return result
    
    def add_stack(self) -> bool:
        if not self.stackable:
            return False
        
        if self.current_stacks >= self.max_stacks:
            return False
        
        self.current_stacks += 1
        return True
    
    def remove_stack(self) -> bool:
        if self.current_stacks <= 1:
            return False
        
        self.current_stacks -= 1
        return True
    
    def refresh_duration(self, new_duration: float = None):
        self.start_time = time.time()
        if new_duration is not None:
            self.duration = new_duration
    
    def get_total_effects(self) -> Dict[str, float]:
        return {
            attr: value * self.current_stacks
            for attr, value in self.effects.items()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "effect_type": self.effect_type.value,
            "duration": self.duration,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "effects": self.effects,
            "tick_interval": self.tick_interval,
            "tick_damage": self.tick_damage,
            "tick_heal": self.tick_heal,
            "damage_type": self.damage_type,
            "control_type": self.control_type.value if self.control_type else None,
            "stackable": self.stackable,
            "max_stacks": self.max_stacks,
            "current_stacks": self.current_stacks,
            "icon": self.icon,
            "start_time": self.start_time,
            "last_tick_time": self.last_tick_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Effect':
        effect = cls(
            id=data["id"],
            name=data["name"],
            effect_type=EffectType(data["effect_type"]),
            duration=data["duration"],
            source_id=data.get("source_id", ""),
            target_id=data.get("target_id", ""),
            effects=data.get("effects", {}),
            tick_interval=data.get("tick_interval", 1.0),
            tick_damage=data.get("tick_damage", 0),
            tick_heal=data.get("tick_heal", 0),
            damage_type=data.get("damage_type", "physical"),
            control_type=ControlType(data["control_type"]) if data.get("control_type") else None,
            stackable=data.get("stackable", False),
            max_stacks=data.get("max_stacks", 1),
            current_stacks=data.get("current_stacks", 1),
            icon=data.get("icon", "")
        )
        effect.start_time = data.get("start_time", time.time())
        effect.last_tick_time = data.get("last_tick_time", effect.start_time)
        return effect


class EffectManager:
    def __init__(self):
        self._effects: Dict[str, List[Effect]] = {}
        self._global_effects: List[Effect] = []
    
    def add_effect(self, target_id: str, effect: Effect) -> bool:
        if target_id not in self._effects:
            self._effects[target_id] = []
        
        if not effect.stackable:
            for existing in self._effects[target_id]:
                if existing.id == effect.id:
                    existing.refresh_duration(effect.duration)
                    return True
        
        self._effects[target_id].append(effect)
        
        if effect.on_apply:
            try:
                effect.on_apply(effect)
            except Exception as e:
                print(f"Effect apply callback error: {e}")
        
        return True
    
    def remove_effect(self, target_id: str, effect_id: str) -> bool:
        if target_id not in self._effects:
            return False
        
        for i, effect in enumerate(self._effects[target_id]):
            if effect.id == effect_id:
                removed = self._effects[target_id].pop(i)
                
                if removed.on_remove:
                    try:
                        removed.on_remove(removed)
                    except Exception as e:
                        print(f"Effect remove callback error: {e}")
                
                return True
        
        return False
    
    def remove_all_effects(self, target_id: str):
        if target_id in self._effects:
            for effect in self._effects[target_id]:
                if effect.on_remove:
                    try:
                        effect.on_remove(effect)
                    except Exception as e:
                        print(f"Effect remove callback error: {e}")
            
            self._effects[target_id].clear()
    
    def get_effects(self, target_id: str) -> List[Effect]:
        return self._effects.get(target_id, [])
    
    def get_effects_by_type(self, target_id: str, effect_type: EffectType) -> List[Effect]:
        return [
            e for e in self._effects.get(target_id, [])
            if e.effect_type == effect_type
        ]
    
    def has_effect(self, target_id: str, effect_id: str) -> bool:
        for effect in self._effects.get(target_id, []):
            if effect.id == effect_id:
                return True
        return False
    
    def get_total_effects(self, target_id: str) -> Dict[str, float]:
        total: Dict[str, float] = {}
        
        for effect in self._effects.get(target_id, []):
            for attr, value in effect.get_total_effects().items():
                if attr in total:
                    total[attr] += value
                else:
                    total[attr] = value
        
        return total
    
    def is_controlled(self, target_id: str, control_type: ControlType = None) -> bool:
        for effect in self._effects.get(target_id, []):
            if effect.effect_type == EffectType.CONTROL:
                if control_type is None or effect.control_type == control_type:
                    return True
        return False
    
    def update(self, delta_time: float) -> Dict[str, List[Dict[str, Any]]]:
        tick_results: Dict[str, List[Dict[str, Any]]] = {}
        
        for target_id, effects in list(self._effects.items()):
            expired = []
            ticks = []
            
            for effect in effects:
                if effect.should_tick():
                    tick_result = effect.tick()
                    tick_result["effect_id"] = effect.id
                    tick_result["effect_name"] = effect.name
                    ticks.append(tick_result)
                
                if effect.is_expired():
                    expired.append(effect)
            
            if ticks:
                tick_results[target_id] = ticks
            
            for effect in expired:
                self.remove_effect(target_id, effect.id)
        
        return tick_results
    
    def dispel(self, target_id: str, effect_type: EffectType = None, 
               count: int = 1) -> List[str]:
        removed = []
        
        if target_id not in self._effects:
            return removed
        
        to_remove = []
        for effect in self._effects[target_id]:
            if effect_type is None or effect.effect_type == effect_type:
                to_remove.append(effect.id)
                if len(to_remove) >= count:
                    break
        
        for effect_id in to_remove:
            if self.remove_effect(target_id, effect_id):
                removed.append(effect_id)
        
        return removed
    
    def cleanse(self, target_id: str) -> List[str]:
        return self.dispel(target_id, EffectType.DEBUFF, count=999)
    
    def purge(self, target_id: str) -> List[str]:
        return self.dispel(target_id, EffectType.BUFF, count=999)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "effects": {
                target_id: [e.to_dict() for e in effects]
                for target_id, effects in self._effects.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EffectManager':
        manager = cls()
        
        for target_id, effects_data in data.get("effects", {}).items():
            manager._effects[target_id] = [
                Effect.from_dict(e) for e in effects_data
            ]
        
        return manager
