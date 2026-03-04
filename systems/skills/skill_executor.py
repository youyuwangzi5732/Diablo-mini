"""
技能效果执行系统
"""
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import random
import math

from systems.skills.skill import Skill, SkillType, TargetType, DamageType, SkillFactory
from systems.combat.combat_system import CombatSystem, DamageResult
from systems.particles import ParticleSystem


class SkillEffectType(Enum):
    DAMAGE = "damage"
    HEAL = "heal"
    BUFF = "buff"
    DEBUFF = "debuff"
    SUMMON = "summon"
    TELEPORT = "teleport"
    PROJECTILE = "projectile"
    AREA_EFFECT = "area_effect"
    KNOCKBACK = "knockback"
    STUN = "stun"


@dataclass
class SkillExecutionContext:
    caster: Any
    skill: Skill
    level: int
    selected_branch: Optional[str] = None
    target_position: Optional[Tuple[float, float]] = None
    target_entity: Optional[Any] = None
    targets: List[Any] = field(default_factory=list)


@dataclass
class SkillExecutionResult:
    success: bool
    damage_results: List[DamageResult] = field(default_factory=list)
    healed_amount: float = 0
    targets_hit: List[str] = field(default_factory=list)
    effects_applied: List[str] = field(default_factory=list)
    message: str = ""


class SkillExecutor:
    def __init__(self, combat_system: CombatSystem, particle_system: ParticleSystem):
        self.combat_system = combat_system
        self.particle_system = particle_system
        
        self.projectiles: List[Dict[str, Any]] = []
        self.area_effects: List[Dict[str, Any]] = []
        self.active_buffs: List[Dict[str, Any]] = []
        
        self._effect_handlers: Dict[str, Callable] = {
            SkillEffectType.DAMAGE.value: self._apply_damage,
            SkillEffectType.HEAL.value: self._apply_heal,
            SkillEffectType.BUFF.value: self._apply_buff,
            SkillEffectType.DEBUFF.value: self._apply_debuff,
            SkillEffectType.STUN.value: self._apply_stun,
            SkillEffectType.KNOCKBACK.value: self._apply_knockback,
            SkillEffectType.TELEPORT.value: self._apply_teleport,
        }
    
    def execute_skill(self, context: SkillExecutionContext, 
                      monsters: List[Any] = None) -> SkillExecutionResult:
        result = SkillExecutionResult(success=False)
        
        skill = context.skill
        caster = context.caster
        
        if not skill or not caster:
            result.message = "无效的技能或施法者"
            return result
        
        if not skill.can_use(caster, context.level, context.selected_branch):
            result.message = "无法使用技能"
            return result
        
        resource_cost = skill.get_resource_cost(context.level, context.selected_branch)
        if hasattr(caster, 'current_resource'):
            if caster.current_resource < resource_cost:
                result.message = "资源不足"
                return result
            caster.current_resource -= resource_cost
        
        result.success = True
        
        target_type = skill.target_type
        
        if target_type == TargetType.SELF:
            self._execute_self_target(context, result)
        elif target_type == TargetType.ENEMY:
            self._execute_enemy_target(context, result, monsters)
        elif target_type == TargetType.GROUND:
            self._execute_ground_target(context, result, monsters)
        elif target_type == TargetType.AREA:
            self._execute_area_target(context, result, monsters)
        elif target_type == TargetType.PROJECTILE:
            self._execute_projectile(context, result, monsters)
        elif target_type == TargetType.NO_TARGET:
            self._execute_no_target(context, result)
        
        self._spawn_skill_particles(context)
        
        return result
    
    def _execute_self_target(self, context: SkillExecutionContext, 
                             result: SkillExecutionResult):
        skill = context.skill
        caster = context.caster
        
        if skill.damage_type == DamageType.HOLY or skill.base_damage_min < 0:
            heal_amount = self._calculate_heal(context)
            self.combat_system.heal(caster, heal_amount, caster)
            result.healed_amount = heal_amount
        else:
            if skill.skill_type == SkillType.TOGGLE:
                self._toggle_buff(context, result)
            else:
                self._apply_self_buff(context, result)
    
    def _execute_enemy_target(self, context: SkillExecutionContext,
                              result: SkillExecutionResult, monsters: List[Any]):
        skill = context.skill
        caster = context.caster
        
        target = context.target_entity
        if not target and monsters:
            target = self._find_nearest_enemy(caster, monsters, skill.get_range(context.level))
        
        if not target:
            result.message = "没有目标"
            return
        
        damage = self._calculate_damage(context)
        damage_type = self._get_damage_type(skill.damage_type)
        
        damage_result = self.combat_system.calculate_damage(
            caster, target, damage, damage_type
        )
        
        actual_damage = self.combat_system.apply_damage(target, damage_result)
        result.damage_results.append(damage_result)
        result.targets_hit.append(getattr(target, 'id', 'unknown'))
        
        self._apply_branch_effects(context, target, result)
    
    def _execute_ground_target(self, context: SkillExecutionContext,
                               result: SkillExecutionResult, monsters: List[Any]):
        skill = context.skill
        caster = context.caster
        
        target_pos = context.target_position
        if not target_pos:
            if hasattr(caster, 'position'):
                facing = getattr(caster, 'facing_direction', (1, 0))
                range_val = skill.get_range(context.level)
                target_pos = (
                    caster.position[0] + facing[0] * range_val,
                    caster.position[1] + facing[1] * range_val
                )
        
        if not target_pos:
            return
        
        if skill.id == "teleport" or skill.id == "vault" or skill.id == "leap":
            if hasattr(caster, 'position'):
                caster.position = target_pos
            result.effects_applied.append("teleport")
            return
        
        aoe = skill.get_area_of_effect(context.level)
        if aoe > 0 and monsters:
            targets_in_range = self._find_targets_in_area(target_pos, aoe, monsters)
            
            for target in targets_in_range:
                damage = self._calculate_damage(context)
                damage_type = self._get_damage_type(skill.damage_type)
                
                damage_result = self.combat_system.calculate_damage(
                    caster, target, damage, damage_type
                )
                
                self.combat_system.apply_damage(target, damage_result)
                result.damage_results.append(damage_result)
                result.targets_hit.append(getattr(target, 'id', 'unknown'))
        
        self._create_area_effect(context, target_pos)
    
    def _execute_area_target(self, context: SkillExecutionContext,
                             result: SkillExecutionResult, monsters: List[Any]):
        skill = context.skill
        caster = context.caster
        
        center = getattr(caster, 'position', (0, 0))
        aoe = skill.get_area_of_effect(context.level)
        
        if monsters:
            targets_in_range = self._find_targets_in_area(center, aoe, monsters)
            
            for target in targets_in_range:
                damage = self._calculate_damage(context)
                damage_type = self._get_damage_type(skill.damage_type)
                
                damage_result = self.combat_system.calculate_damage(
                    caster, target, damage, damage_type
                )
                
                self.combat_system.apply_damage(target, damage_result)
                result.damage_results.append(damage_result)
                result.targets_hit.append(getattr(target, 'id', 'unknown'))
    
    def _execute_projectile(self, context: SkillExecutionContext,
                            result: SkillExecutionResult, monsters: List[Any]):
        skill = context.skill
        caster = context.caster
        
        caster_pos = getattr(caster, 'position', (0, 0))
        target_pos = context.target_position
        
        if not target_pos and monsters:
            nearest = self._find_nearest_enemy(caster, monsters, skill.get_range(context.level))
            if nearest:
                target_pos = getattr(nearest, 'position', caster_pos)
        
        if not target_pos:
            dx = getattr(caster, 'facing_direction', (1, 0))[0]
            dy = getattr(caster, 'facing_direction', (1, 0))[1]
            range_val = skill.get_range(context.level)
            target_pos = (caster_pos[0] + dx * range_val, caster_pos[1] + dy * range_val)
        
        projectile_count = 1
        if context.selected_branch:
            for branch in skill.branches:
                if branch.id == context.selected_branch:
                    projectile_count = int(branch.modifiers.get("projectile_count", 1))
                    break
        
        for i in range(projectile_count):
            spread = (i - projectile_count // 2) * 0.2 if projectile_count > 1 else 0
            
            self.projectiles.append({
                "id": f"proj_{random.randint(1000, 9999)}",
                "skill_id": skill.id,
                "position": list(caster_pos),
                "target": target_pos,
                "speed": 15.0,
                "damage": self._calculate_damage(context),
                "damage_type": skill.damage_type,
                "caster": caster,
                "level": context.level,
                "branch": context.selected_branch,
                "homing": False,
                "piercing": False,
                "lifetime": 3.0,
                "spread": spread
            })
        
        result.effects_applied.append("projectile_fired")
    
    def _execute_no_target(self, context: SkillExecutionContext,
                           result: SkillExecutionResult):
        skill = context.skill
        caster = context.caster
        
        if skill.id == "raise_skeleton":
            result.effects_applied.append("summon_skeleton")
        elif skill.id == "shadow_master":
            result.effects_applied.append("summon_shadow")
        else:
            self._apply_self_buff(context, result)
    
    def _calculate_damage(self, context: SkillExecutionContext) -> Tuple[float, float]:
        skill = context.skill
        caster = context.caster
        
        attack_power = 0
        weapon_damage = 0
        
        if hasattr(caster, 'get_primary_attribute_value'):
            attack_power = caster.get_primary_attribute_value()
        
        return skill.get_damage(
            context.level, 
            attack_power, 
            weapon_damage,
            context.selected_branch
        )
    
    def _calculate_heal(self, context: SkillExecutionContext) -> float:
        skill = context.skill
        base_heal = abs(skill.base_damage_min) + abs(skill.base_damage_max)
        return base_heal * context.level * 0.5
    
    def _get_damage_type(self, damage_type: DamageType):
        from systems.combat.combat_system import DamageType as CombatDamageType
        
        type_map = {
            DamageType.PHYSICAL: CombatDamageType.PHYSICAL,
            DamageType.FIRE: CombatDamageType.FIRE,
            DamageType.COLD: CombatDamageType.COLD,
            DamageType.LIGHTNING: CombatDamageType.LIGHTNING,
            DamageType.POISON: CombatDamageType.POISON,
            DamageType.HOLY: CombatDamageType.HOLY,
            DamageType.SHADOW: CombatDamageType.ARCANE,
            DamageType.ARCANE: CombatDamageType.ARCANE,
        }
        
        return type_map.get(damage_type, CombatDamageType.PHYSICAL)
    
    def _find_nearest_enemy(self, caster: Any, enemies: List[Any], 
                            max_range: float) -> Optional[Any]:
        if not enemies or not hasattr(caster, 'position'):
            return None
        
        caster_pos = caster.position
        nearest = None
        nearest_dist = float('inf')
        
        for enemy in enemies:
            if not getattr(enemy, 'is_alive', True):
                continue
            
            enemy_pos = getattr(enemy, 'position', None)
            if not enemy_pos:
                continue
            
            dist = math.sqrt(
                (enemy_pos[0] - caster_pos[0]) ** 2 +
                (enemy_pos[1] - caster_pos[1]) ** 2
            )
            
            if dist < nearest_dist and dist <= max_range:
                nearest = enemy
                nearest_dist = dist
        
        return nearest
    
    def _find_targets_in_area(self, center: Tuple[float, float], radius: float,
                              enemies: List[Any]) -> List[Any]:
        targets = []
        
        for enemy in enemies:
            if not getattr(enemy, 'is_alive', True):
                continue
            
            enemy_pos = getattr(enemy, 'position', None)
            if not enemy_pos:
                continue
            
            dist = math.sqrt(
                (enemy_pos[0] - center[0]) ** 2 +
                (enemy_pos[1] - center[1]) ** 2
            )
            
            if dist <= radius:
                targets.append(enemy)
        
        return targets
    
    def _apply_branch_effects(self, context: SkillExecutionContext, target: Any,
                              result: SkillExecutionResult):
        if not context.selected_branch:
            return
        
        skill = context.skill
        for branch in skill.branches:
            if branch.id == context.selected_branch:
                for effect_name, value in branch.effects.items():
                    if effect_name == "stun_chance":
                        if random.random() * 100 < value:
                            self._apply_stun(target, branch.effects.get("stun_duration", 2))
                            result.effects_applied.append("stun")
                    elif effect_name == "freeze_chance":
                        if random.random() * 100 < value:
                            self._apply_debuff(target, "frozen", 3, {"movement_speed": -100})
                            result.effects_applied.append("freeze")
                break
    
    def _apply_damage(self, target: Any, amount: float, damage_type: str):
        if hasattr(target, 'take_damage'):
            target.take_damage(amount)
    
    def _apply_heal(self, target: Any, amount: float):
        if hasattr(target, 'heal'):
            target.heal(amount)
    
    def _apply_buff(self, target: Any, buff_id: str, duration: float, effects: Dict[str, float]):
        if hasattr(target, 'add_buff'):
            target.add_buff(buff_id, duration, effects)
    
    def _apply_debuff(self, target: Any, debuff_id: str, duration: float, effects: Dict[str, float]):
        if hasattr(target, 'add_buff'):
            target.add_buff(debuff_id, duration, effects)
    
    def _apply_stun(self, target: Any, duration: float):
        if hasattr(target, 'add_buff'):
            target.add_buff("stunned", duration, {"can_act": 0, "can_move": 0})
    
    def _apply_knockback(self, target: Any, distance: float, direction: Tuple[float, float]):
        if hasattr(target, 'position'):
            target.position = (
                target.position[0] + direction[0] * distance,
                target.position[1] + direction[1] * distance
            )
    
    def _apply_teleport(self, target: Any, position: Tuple[float, float]):
        if hasattr(target, 'position'):
            target.position = position
    
    def _apply_self_buff(self, context: SkillExecutionContext, result: SkillExecutionResult):
        caster = context.caster
        skill = context.skill
        
        duration = skill.get_level_data(context.level).duration
        if duration <= 0:
            duration = skill.base_duration
        
        if duration > 0 and hasattr(caster, 'add_buff'):
            effects = {}
            
            if skill.id == "akarat_champion":
                effects = {
                    "damage_percent": 50,
                    "armor_percent": 50,
                    "movement_speed": 30
                }
            elif skill.id == "werewolf":
                effects = {
                    "attack_speed": 50,
                    "movement_speed": 30
                }
            
            if effects:
                caster.add_buff(skill.id, duration, effects)
                result.effects_applied.append(f"buff_{skill.id}")
    
    def _toggle_buff(self, context: SkillExecutionContext, result: SkillExecutionResult):
        caster = context.caster
        skill = context.skill
        
        buff_id = f"toggle_{skill.id}"
        
        existing = None
        if hasattr(caster, 'buffs'):
            existing = next((b for b in caster.buffs if b["id"] == buff_id), None)
        
        if existing:
            if hasattr(caster, 'remove_buff'):
                caster.remove_buff(buff_id)
            result.effects_applied.append(f"deactivate_{skill.id}")
        else:
            effects = {}
            if skill.id == "werewolf":
                effects = {
                    "attack_speed": 50,
                    "movement_speed": 30
                }
            
            if effects and hasattr(caster, 'add_buff'):
                caster.add_buff(buff_id, -1, effects)
                result.effects_applied.append(f"activate_{skill.id}")
    
    def _create_area_effect(self, context: SkillExecutionContext, position: Tuple[float, float]):
        skill = context.skill
        
        self.area_effects.append({
            "id": f"aoe_{random.randint(1000, 9999)}",
            "skill_id": skill.id,
            "position": position,
            "radius": skill.get_area_of_effect(context.level),
            "damage": self._calculate_damage(context),
            "damage_type": skill.damage_type,
            "caster": context.caster,
            "level": context.level,
            "duration": skill.get_level_data(context.level).duration,
            "tick_interval": 0.5,
            "tick_timer": 0,
            "branch": context.selected_branch
        })
    
    def _spawn_skill_particles(self, context: SkillExecutionContext):
        skill = context.skill
        caster = context.caster
        
        if not hasattr(caster, 'position'):
            return
        
        pos = caster.position
        
        particle_type = "fire"
        if skill.damage_type == DamageType.FIRE:
            particle_type = "fire"
        elif skill.damage_type == DamageType.COLD:
            particle_type = "ice"
        elif skill.damage_type == DamageType.LIGHTNING:
            particle_type = "lightning"
        elif skill.damage_type == DamageType.POISON:
            particle_type = "poison"
        elif skill.damage_type == DamageType.ARCANE:
            particle_type = "arcane"
        elif skill.damage_type == DamageType.HOLY:
            particle_type = "holy"
        
        if skill.target_type == TargetType.AREA:
            config = self.particle_system.create_explosion_effect(
                pos[0] * 64, pos[1] * 64, particle_type
            )
            self.particle_system.create_emitter(config)
        elif skill.target_type == TargetType.PROJECTILE:
            config = self.particle_system.create_projectile_trail(
                pos[0] * 64, pos[1] * 64, particle_type
            )
            self.particle_system.create_emitter(config)
    
    def update(self, delta_time: float, monsters: List[Any] = None):
        self._update_projectiles(delta_time, monsters)
        self._update_area_effects(delta_time, monsters)
    
    def _update_projectiles(self, delta_time: float, monsters: List[Any]):
        for proj in self.projectiles[:]:
            proj["lifetime"] -= delta_time
            
            if proj["lifetime"] <= 0:
                self.projectiles.remove(proj)
                continue
            
            target = proj["target"]
            if proj["homing"] and monsters:
                caster = proj["caster"]
                nearest = self._find_nearest_enemy(caster, monsters, 50)
                if nearest:
                    target = getattr(nearest, 'position', target)
            
            dx = target[0] - proj["position"][0]
            dy = target[1] - proj["position"][1]
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist < 0.5:
                self._on_projectile_hit(proj, monsters)
                if not proj["piercing"]:
                    self.projectiles.remove(proj)
                continue
            
            dx /= dist
            dy /= dist
            
            if proj["spread"] != 0:
                angle = math.atan2(dy, dx) + proj["spread"]
                dx = math.cos(angle)
                dy = math.sin(angle)
            
            speed = proj["speed"] * delta_time
            proj["position"][0] += dx * speed
            proj["position"][1] += dy * speed
    
    def _on_projectile_hit(self, proj: Dict[str, Any], monsters: List[Any]):
        hit_pos = tuple(proj["position"])
        damage = proj["damage"]
        damage_type = self._get_damage_type(proj["damage_type"])
        caster = proj["caster"]
        
        hit_radius = 1.0
        targets = self._find_targets_in_area(hit_pos, hit_radius, monsters or [])
        
        for target in targets:
            damage_result = self.combat_system.calculate_damage(
                caster, target, damage, damage_type
            )
            self.combat_system.apply_damage(target, damage_result)
    
    def _update_area_effects(self, delta_time: float, monsters: List[Any]):
        for aoe in self.area_effects[:]:
            aoe["duration"] -= delta_time
            aoe["tick_timer"] += delta_time
            
            if aoe["duration"] <= 0:
                self.area_effects.remove(aoe)
                continue
            
            if aoe["tick_timer"] >= aoe["tick_interval"] and monsters:
                aoe["tick_timer"] = 0
                
                targets = self._find_targets_in_area(aoe["position"], aoe["radius"], monsters)
                
                for target in targets:
                    damage = aoe["damage"]
                    damage_type = self._get_damage_type(aoe["damage_type"])
                    
                    damage_result = self.combat_system.calculate_damage(
                        aoe["caster"], target, damage, damage_type
                    )
                    self.combat_system.apply_damage(target, damage_result)
    
    def get_projectiles(self) -> List[Dict[str, Any]]:
        return self.projectiles
    
    def get_area_effects(self) -> List[Dict[str, Any]]:
        return self.area_effects
