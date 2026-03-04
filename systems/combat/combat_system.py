"""
战斗系统核心
"""
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random
import math


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
class DamageResult:
    damage: float
    damage_type: DamageType
    is_crit: bool = False
    is_dodged: bool = False
    is_blocked: bool = False
    blocked_amount: float = 0
    overkill: float = 0
    source_id: str = ""
    target_id: str = ""


@dataclass
class CombatResult:
    success: bool
    damage_results: List[DamageResult] = field(default_factory=list)
    killed_targets: List[str] = field(default_factory=list)
    applied_effects: List[Dict[str, Any]] = field(default_factory=list)


class CombatSystem:
    def __init__(self):
        self.damage_numbers: List[Dict[str, Any]] = []
        self.combat_log: List[str] = []
    
    def calculate_damage(self, attacker: Any, defender: Any,
                         base_damage: Tuple[float, float],
                         damage_type: DamageType,
                         skill_multiplier: float = 1.0) -> DamageResult:
        min_dmg, max_dmg = base_damage
        
        raw_damage = random.uniform(min_dmg, max_dmg)
        raw_damage *= skill_multiplier
        
        if hasattr(attacker, 'attributes'):
            attrs = attacker.attributes
            primary_attr = self._get_primary_attribute_value(attacker)
            raw_damage += primary_attr * 0.5
        
        is_crit = self._check_crit(attacker)
        if is_crit:
            crit_mult = self._get_crit_damage(attacker)
            raw_damage *= crit_mult
        
        if self._check_dodge(defender):
            return DamageResult(
                damage=0,
                damage_type=damage_type,
                is_dodged=True,
                source_id=getattr(attacker, 'id', ''),
                target_id=getattr(defender, 'id', '')
            )
        
        damage_reduction = self._calculate_damage_reduction(defender, damage_type)
        final_damage = raw_damage * (1 - damage_reduction)
        
        is_blocked = False
        blocked_amount = 0
        if self._check_block(defender):
            is_blocked = True
            blocked_amount = self._get_block_amount(defender)
            final_damage = max(0, final_damage - blocked_amount)
        
        return DamageResult(
            damage=final_damage,
            damage_type=damage_type,
            is_crit=is_crit,
            is_blocked=is_blocked,
            blocked_amount=blocked_amount,
            source_id=getattr(attacker, 'id', ''),
            target_id=getattr(defender, 'id', '')
        )
    
    def apply_damage(self, target: Any, damage_result: DamageResult) -> float:
        if damage_result.is_dodged:
            return 0
        
        if hasattr(target, 'current_health'):
            actual_damage = min(damage_result.damage, target.current_health)
            target.current_health -= actual_damage
            
            if target.current_health <= 0:
                target.is_alive = False
                damage_result.overkill = -target.current_health
            
            self._add_damage_number(target, damage_result)
            
            return actual_damage
        
        return 0
    
    def heal(self, target: Any, amount: float, source: Any = None) -> float:
        if not hasattr(target, 'current_health') or not hasattr(target, 'get_max_health'):
            return 0
        
        max_health = target.get_max_health() if callable(target.get_max_health) else target.get_max_health
        actual_heal = min(amount, max_health - target.current_health)
        target.current_health += actual_heal
        
        self._add_damage_number(target, DamageResult(
            damage=-actual_heal,
            damage_type=DamageType.HOLY,
            source_id=getattr(source, 'id', '') if source else '',
            target_id=getattr(target, 'id', '')
        ))
        
        return actual_heal
    
    def _check_crit(self, attacker: Any) -> bool:
        crit_chance = 5.0
        
        if hasattr(attacker, 'attributes'):
            from entities.character.attributes import AttributeType
            crit_chance = attacker.attributes.get_total(AttributeType.CRIT_CHANCE)
        
        return random.random() * 100 < crit_chance
    
    def _get_crit_damage(self, attacker: Any) -> float:
        crit_damage = 1.5
        
        if hasattr(attacker, 'attributes'):
            from entities.character.attributes import AttributeType
            crit_damage = attacker.attributes.get_total(AttributeType.CRIT_DAMAGE) / 100
        
        return crit_damage
    
    def _check_dodge(self, defender: Any) -> bool:
        dodge_chance = 0
        
        if hasattr(defender, 'attributes'):
            from entities.character.attributes import AttributeType
            dodge_chance = defender.attributes.get_total(AttributeType.DODGE_CHANCE)
        
        return random.random() * 100 < dodge_chance
    
    def _check_block(self, defender: Any) -> bool:
        block_chance = 0
        
        if hasattr(defender, 'equipment'):
            off_hand = defender.equipment.get('off_hand')
            if off_hand and hasattr(off_hand, 'item_type'):
                from entities.items.item import ItemType
                if off_hand.item_type == ItemType.WEAPON:
                    block_chance = 15
        
        return random.random() * 100 < block_chance
    
    def _get_block_amount(self, defender: Any) -> float:
        base_block = 50
        
        if hasattr(defender, 'attributes'):
            from entities.character.attributes import AttributeType
            base_block += defender.attributes.get_total(AttributeType.STRENGTH) * 0.5
        
        return base_block
    
    def _calculate_damage_reduction(self, defender: Any, damage_type: DamageType) -> float:
        armor = 0
        resist = 0
        
        if hasattr(defender, 'attributes'):
            from entities.character.attributes import AttributeType
            armor = defender.attributes.get_total(AttributeType.ARMOR)
            
            resist_map = {
                DamageType.FIRE: AttributeType.FIRE_RESIST,
                DamageType.COLD: AttributeType.COLD_RESIST,
                DamageType.LIGHTNING: AttributeType.LIGHTNING_RESIST,
                DamageType.POISON: AttributeType.POISON_RESIST,
            }
            
            if damage_type in resist_map:
                resist = defender.attributes.get_total(resist_map[damage_type])
        
        armor_reduction = armor / (armor + 100)
        resist_reduction = resist / 100
        
        total_reduction = armor_reduction + resist_reduction * (1 - armor_reduction)
        
        return min(0.9, total_reduction)
    
    def _get_primary_attribute_value(self, character: Any) -> float:
        if not hasattr(character, 'character_class') or not character.character_class:
            return 0
        
        primary_attr = character.character_class.primary_attribute
        
        if hasattr(character, 'attributes'):
            from entities.character.attributes import AttributeType
            attr_type = getattr(AttributeType, primary_attr.upper(), None)
            if attr_type:
                return character.attributes.get_total(attr_type)
        
        return 0
    
    def _add_damage_number(self, target: Any, damage_result: DamageResult):
        if hasattr(target, 'position'):
            self.damage_numbers.append({
                "x": target.position[0],
                "y": target.position[1],
                "damage": damage_result.damage,
                "is_crit": damage_result.is_crit,
                "is_heal": damage_result.damage < 0,
                "color": self._get_damage_color(damage_result),
                "lifetime": 1.5,
                "velocity_y": -50
            })
    
    def _get_damage_color(self, damage_result: DamageResult) -> Tuple[int, int, int]:
        if damage_result.is_dodged:
            return (150, 150, 150)
        
        if damage_result.damage < 0:
            return (100, 255, 100)
        
        if damage_result.is_crit:
            return (255, 255, 0)
        
        color_map = {
            DamageType.PHYSICAL: (255, 255, 255),
            DamageType.FIRE: (255, 100, 50),
            DamageType.COLD: (100, 200, 255),
            DamageType.LIGHTNING: (255, 255, 100),
            DamageType.POISON: (100, 255, 100),
            DamageType.HOLY: (255, 230, 150),
            DamageType.SHADOW: (150, 100, 200),
            DamageType.ARCANE: (200, 100, 255),
        }
        
        return color_map.get(damage_result.damage_type, (255, 255, 255))
    
    def update(self, delta_time: float):
        for dmg_num in self.damage_numbers[:]:
            dmg_num["lifetime"] -= delta_time
            dmg_num["y"] += dmg_num["velocity_y"] * delta_time
            
            if dmg_num["lifetime"] <= 0:
                self.damage_numbers.remove(dmg_num)
    
    def get_damage_numbers(self) -> List[Dict[str, Any]]:
        return self.damage_numbers
    
    def calculate_thorns_damage(self, attacker: Any, defender: Any, 
                                 incoming_damage: float) -> float:
        thorns = 0
        
        if hasattr(defender, 'attributes'):
            from entities.character.attributes import AttributeType
            thorns = defender.attributes.get_total(AttributeType.THORNS)
        
        return incoming_damage * thorns / 100
    
    def calculate_life_steal(self, attacker: Any, damage_dealt: float) -> float:
        life_steal = 0
        
        if hasattr(attacker, 'attributes'):
            from entities.character.attributes import AttributeType
            life_steal = attacker.attributes.get_total(AttributeType.LIFE_STEAL)
        
        return damage_dealt * life_steal / 100
