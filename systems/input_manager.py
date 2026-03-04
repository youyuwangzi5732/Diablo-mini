"""
玩家输入控制器
"""
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import pygame


class InputAction(Enum):
    MOVE_UP = "move_up"
    MOVE_DOWN = "move_down"
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    
    SKILL_1 = "skill_1"
    SKILL_2 = "skill_2"
    SKILL_3 = "skill_3"
    SKILL_4 = "skill_4"
    SKILL_5 = "skill_5"
    SKILL_6 = "skill_6"
    
    PRIMARY_ATTACK = "primary_attack"
    SECONDARY_ATTACK = "secondary_attack"
    
    INTERACT = "interact"
    
    INVENTORY = "inventory"
    CHARACTER_PANEL = "character_panel"
    SKILL_TREE = "skill_tree"
    MAP = "map"
    
    PAUSE = "pause"
    
    POTION_1 = "potion_1"
    POTION_2 = "potion_2"
    POTION_3 = "potion_3"
    POTION_4 = "potion_4"
    
    TOWN_PORTAL = "town_portal"


@dataclass
class KeyBinding:
    action: InputAction
    primary_key: int
    secondary_key: Optional[int] = None
    modifier_key: Optional[int] = None


class InputManager:
    DEFAULT_BINDINGS = {
        pygame.K_w: InputAction.MOVE_UP,
        pygame.K_s: InputAction.MOVE_DOWN,
        pygame.K_a: InputAction.MOVE_LEFT,
        pygame.K_d: InputAction.MOVE_RIGHT,
        
        pygame.K_1: InputAction.SKILL_1,
        pygame.K_2: InputAction.SKILL_2,
        pygame.K_3: InputAction.SKILL_3,
        pygame.K_4: InputAction.SKILL_4,
        pygame.K_5: InputAction.SKILL_5,
        pygame.K_6: InputAction.SKILL_6,
        
        pygame.K_i: InputAction.INVENTORY,
        pygame.K_c: InputAction.CHARACTER_PANEL,
        pygame.K_k: InputAction.SKILL_TREE,
        pygame.K_m: InputAction.MAP,
        
        pygame.K_ESCAPE: InputAction.PAUSE,
        
        pygame.K_q: InputAction.POTION_1,
        pygame.K_e: InputAction.POTION_2,
        pygame.K_r: InputAction.POTION_3,
        pygame.K_f: InputAction.POTION_4,
        
        pygame.K_t: InputAction.TOWN_PORTAL,
        
        pygame.K_SPACE: InputAction.INTERACT,
    }
    
    def __init__(self):
        self.key_bindings: Dict[int, InputAction] = dict(self.DEFAULT_BINDINGS)
        
        self.pressed_keys: Set[int] = set()
        self.just_pressed: Set[InputAction] = set()
        self.just_released: Set[InputAction] = set()
        
        self.mouse_position: Tuple[int, int] = (0, 0)
        self.mouse_buttons: Set[int] = set()
        self.mouse_just_pressed: Set[int] = set()
        self.mouse_just_released: Set[int] = set()
        
        self.mouse_world_position: Tuple[float, float] = (0.0, 0.0)
        
        self._action_callbacks: Dict[InputAction, List[callable]] = {}
    
    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            self.pressed_keys.add(event.key)
            
            if event.key in self.key_bindings:
                action = self.key_bindings[event.key]
                self.just_pressed.add(action)
                self._trigger_action(action)
        
        elif event.type == pygame.KEYUP:
            self.pressed_keys.discard(event.key)
            
            if event.key in self.key_bindings:
                action = self.key_bindings[event.key]
                self.just_released.add(action)
        
        elif event.type == pygame.MOUSEMOTION:
            self.mouse_position = event.pos
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_buttons.add(event.button)
            self.mouse_just_pressed.add(event.button)
            
            if event.button == 1:
                self.just_pressed.add(InputAction.PRIMARY_ATTACK)
                self._trigger_action(InputAction.PRIMARY_ATTACK)
            elif event.button == 3:
                self.just_pressed.add(InputAction.SECONDARY_ATTACK)
                self._trigger_action(InputAction.SECONDARY_ATTACK)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.mouse_buttons.discard(event.button)
            self.mouse_just_released.add(event.button)
            
            if event.button == 1:
                self.just_released.add(InputAction.PRIMARY_ATTACK)
            elif event.button == 3:
                self.just_released.add(InputAction.SECONDARY_ATTACK)
    
    def update(self, delta_time: float):
        self.just_pressed.clear()
        self.just_released.clear()
        self.mouse_just_pressed.clear()
        self.mouse_just_released.clear()
    
    def is_action_pressed(self, action: InputAction) -> bool:
        for key, bound_action in self.key_bindings.items():
            if bound_action == action and key in self.pressed_keys:
                return True
        return False
    
    def is_action_just_pressed(self, action: InputAction) -> bool:
        return action in self.just_pressed
    
    def is_action_just_released(self, action: InputAction) -> bool:
        return action in self.just_released
    
    def get_movement_vector(self) -> Tuple[float, float]:
        dx = 0.0
        dy = 0.0
        
        if self.is_action_pressed(InputAction.MOVE_UP):
            dy -= 1.0
        if self.is_action_pressed(InputAction.MOVE_DOWN):
            dy += 1.0
        if self.is_action_pressed(InputAction.MOVE_LEFT):
            dx -= 1.0
        if self.is_action_pressed(InputAction.MOVE_RIGHT):
            dx += 1.0
        
        length = (dx * dx + dy * dy) ** 0.5
        if length > 0:
            dx /= length
            dy /= length
        
        return (dx, dy)
    
    def get_mouse_position(self) -> Tuple[int, int]:
        return self.mouse_position
    
    def get_mouse_world_position(self) -> Tuple[float, float]:
        return self.mouse_world_position
    
    def set_mouse_world_position(self, x: float, y: float):
        self.mouse_world_position = (x, y)
    
    def is_mouse_button_pressed(self, button: int) -> bool:
        return button in self.mouse_buttons
    
    def is_mouse_button_just_pressed(self, button: int) -> bool:
        return button in self.mouse_just_pressed
    
    def register_action_callback(self, action: InputAction, callback: callable):
        if action not in self._action_callbacks:
            self._action_callbacks[action] = []
        self._action_callbacks[action].append(callback)
    
    def unregister_action_callback(self, action: InputAction, callback: callable):
        if action in self._action_callbacks:
            try:
                self._action_callbacks[action].remove(callback)
            except ValueError:
                pass
    
    def _trigger_action(self, action: InputAction):
        if action in self._action_callbacks:
            for callback in self._action_callbacks[action]:
                try:
                    callback(action)
                except Exception as e:
                    print(f"Input callback error: {e}")
    
    def rebind_key(self, key: int, action: InputAction):
        for k, a in list(self.key_bindings.items()):
            if a == action:
                del self.key_bindings[k]
        
        self.key_bindings[key] = action
    
    def reset_bindings(self):
        self.key_bindings = dict(self.DEFAULT_BINDINGS)
    
    def get_binding_for_action(self, action: InputAction) -> Optional[int]:
        for key, bound_action in self.key_bindings.items():
            if bound_action == action:
                return key
        return None
    
    def get_action_name(self, action: InputAction) -> str:
        names = {
            InputAction.MOVE_UP: "向上移动",
            InputAction.MOVE_DOWN: "向下移动",
            InputAction.MOVE_LEFT: "向左移动",
            InputAction.MOVE_RIGHT: "向右移动",
            InputAction.SKILL_1: "技能 1",
            InputAction.SKILL_2: "技能 2",
            InputAction.SKILL_3: "技能 3",
            InputAction.SKILL_4: "技能 4",
            InputAction.SKILL_5: "技能 5",
            InputAction.SKILL_6: "技能 6",
            InputAction.PRIMARY_ATTACK: "主要攻击",
            InputAction.SECONDARY_ATTACK: "次要攻击",
            InputAction.INTERACT: "交互",
            InputAction.INVENTORY: "背包",
            InputAction.CHARACTER_PANEL: "角色面板",
            InputAction.SKILL_TREE: "技能树",
            InputAction.MAP: "地图",
            InputAction.PAUSE: "暂停",
            InputAction.POTION_1: "药水 1",
            InputAction.POTION_2: "药水 2",
            InputAction.POTION_3: "药水 3",
            InputAction.POTION_4: "药水 4",
            InputAction.TOWN_PORTAL: "回城传送门",
        }
        return names.get(action, action.value)


class PlayerController:
    def __init__(self, player: Any, input_manager: InputManager):
        self.player = player
        self.input_manager = input_manager
        
        self.move_speed = 5.0
        self.diagonal_speed_mult = 0.707
        
        self._register_callbacks()
    
    def _register_callbacks(self):
        for i in range(1, 7):
            action = getattr(InputAction, f"SKILL_{i}")
            self.input_manager.register_action_callback(action, self._on_skill_use)
        
        self.input_manager.register_action_callback(InputAction.INTERACT, self._on_interact)
    
    def update(self, delta_time: float):
        if not self.player or not getattr(self.player, 'is_alive', True):
            return
        
        dx, dy = self.input_manager.get_movement_vector()
        
        if dx != 0 or dy != 0:
            self._move_player(dx, dy, delta_time)
        
        if self.input_manager.is_mouse_button_pressed(1):
            self._primary_attack()
    
    def _move_player(self, dx: float, dy: float, delta_time: float):
        if hasattr(self.player, 'attributes'):
            from entities.character.attributes import AttributeType
            speed_mult = self.player.attributes.get_total(AttributeType.MOVEMENT_SPEED)
        else:
            speed_mult = 1.0
        
        actual_speed = self.move_speed * speed_mult
        
        new_x = self.player.position[0] + dx * actual_speed * delta_time
        new_y = self.player.position[1] + dy * actual_speed * delta_time
        
        self.player.position = (new_x, new_y)
        
        if dx != 0 or dy != 0:
            self.player.facing_direction = (dx, dy)
    
    def _primary_attack(self):
        if not hasattr(self.player, 'use_skill'):
            return
        
        mouse_world = self.input_manager.get_mouse_world_position()
        
        dx = mouse_world[0] - self.player.position[0]
        dy = mouse_world[1] - self.player.position[1]
        
        self.player.facing_direction = (dx, dy)
        
        self.player.use_skill(0)
    
    def _on_skill_use(self, action: InputAction):
        if not self.player:
            return
        
        skill_index = {
            InputAction.SKILL_1: 0,
            InputAction.SKILL_2: 1,
            InputAction.SKILL_3: 2,
            InputAction.SKILL_4: 3,
            InputAction.SKILL_5: 4,
            InputAction.SKILL_6: 5,
        }.get(action)
        
        if skill_index is not None and hasattr(self.player, 'use_skill'):
            self.player.use_skill(skill_index)
    
    def _on_interact(self, action: InputAction):
        pass
