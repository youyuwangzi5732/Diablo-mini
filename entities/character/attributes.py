"""
角色属性系统
"""
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import math


class AttributeType(Enum):
    STRENGTH = "strength"
    DEXTERITY = "dexterity"
    INTELLIGENCE = "intelligence"
    VITALITY = "vitality"
    
    MAX_HEALTH = "max_health"
    HEALTH_REGEN = "health_regen"
    MAX_MANA = "max_mana"
    MANA_REGEN = "mana_regen"
    
    ATTACK_POWER = "attack_power"
    SPELL_POWER = "spell_power"
    ARMOR = "armor"
    DODGE_CHANCE = "dodge_chance"
    
    CRIT_CHANCE = "crit_chance"
    CRIT_DAMAGE = "crit_damage"
    ATTACK_SPEED = "attack_speed"
    CAST_SPEED = "cast_speed"
    
    MOVEMENT_SPEED = "movement_speed"
    
    FIRE_RESIST = "fire_resist"
    COLD_RESIST = "cold_resist"
    LIGHTNING_RESIST = "lightning_resist"
    POISON_RESIST = "poison_resist"
    
    LIFE_STEAL = "life_steal"
    MAGIC_FIND = "magic_find"
    GOLD_FIND = "gold_find"
    
    THORNS = "thorns"
    BLOCK_CHANCE = "block_chance"
    BLOCK_AMOUNT = "block_amount"


@dataclass
class AttributeModifier:
    attribute: AttributeType
    value: float
    is_percentage: bool = False
    source: str = ""
    duration: float = -1
    
    def __hash__(self):
        return hash((self.attribute, self.value, self.is_percentage, self.source))


class Attributes:
    BASE_HEALTH_PER_VITALITY = 10
    BASE_MANA_PER_INTELLIGENCE = 5
    BASE_ARMOR_PER_STRENGTH = 1
    
    def __init__(self):
        self._base_attributes: Dict[AttributeType, float] = {}
        self._modifiers: List[AttributeModifier] = []
        self._callbacks: List[Callable[[AttributeType, float], None]] = []
        
        self._initialize_base_attributes()
    
    def _initialize_base_attributes(self):
        for attr in AttributeType:
            self._base_attributes[attr] = 0.0
        
        self._base_attributes[AttributeType.STRENGTH] = 10
        self._base_attributes[AttributeType.DEXTERITY] = 10
        self._base_attributes[AttributeType.INTELLIGENCE] = 10
        self._base_attributes[AttributeType.VITALITY] = 10
        
        self._base_attributes[AttributeType.CRIT_CHANCE] = 5.0
        self._base_attributes[AttributeType.CRIT_DAMAGE] = 150.0
        self._base_attributes[AttributeType.ATTACK_SPEED] = 1.0
        self._base_attributes[AttributeType.CAST_SPEED] = 1.0
        self._base_attributes[AttributeType.MOVEMENT_SPEED] = 1.0
    
    def get_base(self, attr: AttributeType) -> float:
        return self._base_attributes.get(attr, 0.0)
    
    def set_base(self, attr: AttributeType, value: float):
        self._base_attributes[attr] = value
        self._notify_change(attr)
    
    def add_base(self, attr: AttributeType, value: float):
        self._base_attributes[attr] = self._base_attributes.get(attr, 0.0) + value
        self._notify_change(attr)
    
    def add_modifier(self, modifier: AttributeModifier):
        self._modifiers.append(modifier)
        self._notify_change(modifier.attribute)
    
    def remove_modifier(self, modifier: AttributeModifier):
        if modifier in self._modifiers:
            self._modifiers.remove(modifier)
            self._notify_change(modifier.attribute)
    
    def remove_modifiers_from_source(self, source: str):
        to_remove = [m for m in self._modifiers if m.source == source]
        for modifier in to_remove:
            self._modifiers.remove(modifier)
            self._notify_change(modifier.attribute)
    
    def get_total(self, attr: AttributeType) -> float:
        base = self._base_attributes.get(attr, 0.0)
        flat_bonus = 0.0
        percent_bonus = 0.0
        
        for modifier in self._modifiers:
            if modifier.attribute == attr:
                if modifier.is_percentage:
                    percent_bonus += modifier.value
                else:
                    flat_bonus += modifier.value
        
        return (base + flat_bonus) * (1 + percent_bonus / 100)
    
    def get_modifier_value(self, attr: AttributeType, is_percentage: bool = False) -> float:
        total = 0.0
        for modifier in self._modifiers:
            if modifier.attribute == attr and modifier.is_percentage == is_percentage:
                total += modifier.value
        return total
    
    def calculate_derived_attributes(self) -> Dict[AttributeType, float]:
        derived = {}
        
        strength = self.get_total(AttributeType.STRENGTH)
        dexterity = self.get_total(AttributeType.DEXTERITY)
        intelligence = self.get_total(AttributeType.INTELLIGENCE)
        vitality = self.get_total(AttributeType.VITALITY)
        
        derived[AttributeType.MAX_HEALTH] = (
            100 + 
            vitality * self.BASE_HEALTH_PER_VITALITY +
            strength * 2
        )
        
        derived[AttributeType.MAX_MANA] = (
            50 +
            intelligence * self.BASE_MANA_PER_INTELLIGENCE
        )
        
        derived[AttributeType.HEALTH_REGEN] = vitality * 0.5
        derived[AttributeType.MANA_REGEN] = intelligence * 0.3
        
        derived[AttributeType.ATTACK_POWER] = strength * 1.0
        derived[AttributeType.SPELL_POWER] = intelligence * 1.0
        
        derived[AttributeType.ARMOR] = (
            self.get_base(AttributeType.ARMOR) +
            strength * self.BASE_ARMOR_PER_STRENGTH
        )
        
        derived[AttributeType.DODGE_CHANCE] = dexterity * 0.1
        
        return derived
    
    def register_callback(self, callback: Callable[[AttributeType, float], None]):
        self._callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable[[AttributeType, float], None]):
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def _notify_change(self, attr: AttributeType):
        new_value = self.get_total(attr)
        for callback in self._callbacks:
            try:
                callback(attr, new_value)
            except Exception as e:
                print(f"Attribute callback error: {e}")
    
    def update_durations(self, delta_time: float):
        expired = []
        for modifier in self._modifiers:
            if modifier.duration > 0:
                modifier.duration -= delta_time
                if modifier.duration <= 0:
                    expired.append(modifier)
        
        for modifier in expired:
            self.remove_modifier(modifier)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "base_attributes": {attr.value: val for attr, val in self._base_attributes.items()},
            "modifiers": [
                {
                    "attribute": m.attribute.value,
                    "value": m.value,
                    "is_percentage": m.is_percentage,
                    "source": m.source
                }
                for m in self._modifiers
            ]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Attributes':
        attrs = cls()
        
        for attr_name, value in data.get("base_attributes", {}).items():
            try:
                attr = AttributeType(attr_name)
                attrs._base_attributes[attr] = value
            except ValueError:
                pass
        
        for mod_data in data.get("modifiers", []):
            try:
                attr = AttributeType(mod_data["attribute"])
                modifier = AttributeModifier(
                    attribute=attr,
                    value=mod_data["value"],
                    is_percentage=mod_data.get("is_percentage", False),
                    source=mod_data.get("source", "")
                )
                attrs._modifiers.append(modifier)
            except (ValueError, KeyError):
                pass
        
        return attrs
