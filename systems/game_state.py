"""
游戏状态机
"""
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import pygame


class GameStateType(Enum):
    INIT = "init"
    LOADING = "loading"
    MAIN_MENU = "main_menu"
    CHARACTER_SELECT = "character_select"
    CHARACTER_CREATE = "character_create"
    PLAYING = "playing"
    PAUSED = "paused"
    INVENTORY = "inventory"
    CHARACTER_PANEL = "character_panel"
    SKILL_TREE = "skill_tree"
    VENDOR = "vendor"
    CRAFTING = "crafting"
    DIALOGUE = "dialogue"
    CUTSCENE = "cutscene"
    GAME_OVER = "game_over"
    SETTINGS = "settings"
    CREDITS = "credits"


@dataclass
class GameState:
    type: GameStateType
    name: str
    
    on_enter: Optional[Callable] = None
    on_exit: Optional[Callable] = None
    on_update: Optional[Callable] = None
    on_render: Optional[Callable] = None
    on_event: Optional[Callable] = None
    
    pauses_game: bool = False
    shows_hud: bool = True
    allows_input: bool = True
    
    data: Dict[str, Any] = field(default_factory=dict)
    
    _active: bool = False
    
    def enter(self, **kwargs):
        self._active = True
        self.data.update(kwargs)
        if self.on_enter:
            self.on_enter(self, **kwargs)
    
    def exit(self):
        self._active = False
        if self.on_exit:
            self.on_exit(self)
        self.data.clear()
    
    def update(self, delta_time: float):
        if self.on_update:
            self.on_update(self, delta_time)
    
    def render(self, surface: pygame.Surface):
        if self.on_render:
            self.on_render(self, surface)
    
    def handle_event(self, event: pygame.event.Event):
        if self.on_event:
            self.on_event(self, event)
    
    def is_active(self) -> bool:
        return self._active


class GameStateMachine:
    def __init__(self, initial_state: GameStateType = GameStateType.INIT):
        self.states: Dict[GameStateType, GameState] = {}
        self.current_state: Optional[GameState] = None
        self.previous_state: Optional[GameState] = None
        self.state_stack: List[GameStateType] = []
        
        self.transition_callbacks: List[Callable] = []
        
        self._create_default_states()
        
        if initial_state:
            self.change_state(initial_state)
    
    def _create_default_states(self):
        self.states[GameStateType.INIT] = GameState(
            type=GameStateType.INIT,
            name="初始化",
            pauses_game=True,
            shows_hud=False
        )
        
        self.states[GameStateType.LOADING] = GameState(
            type=GameStateType.LOADING,
            name="加载中",
            pauses_game=True,
            shows_hud=False
        )
        
        self.states[GameStateType.MAIN_MENU] = GameState(
            type=GameStateType.MAIN_MENU,
            name="主菜单",
            pauses_game=True,
            shows_hud=False
        )
        
        self.states[GameStateType.CHARACTER_SELECT] = GameState(
            type=GameStateType.CHARACTER_SELECT,
            name="选择角色",
            pauses_game=True,
            shows_hud=False
        )
        
        self.states[GameStateType.CHARACTER_CREATE] = GameState(
            type=GameStateType.CHARACTER_CREATE,
            name="创建角色",
            pauses_game=True,
            shows_hud=False
        )
        
        self.states[GameStateType.PLAYING] = GameState(
            type=GameStateType.PLAYING,
            name="游戏中",
            pauses_game=False,
            shows_hud=True
        )
        
        self.states[GameStateType.PAUSED] = GameState(
            type=GameStateType.PAUSED,
            name="暂停",
            pauses_game=True,
            shows_hud=True
        )
        
        self.states[GameStateType.INVENTORY] = GameState(
            type=GameStateType.INVENTORY,
            name="背包",
            pauses_game=False,
            shows_hud=True
        )
        
        self.states[GameStateType.CHARACTER_PANEL] = GameState(
            type=GameStateType.CHARACTER_PANEL,
            name="角色面板",
            pauses_game=False,
            shows_hud=True
        )
        
        self.states[GameStateType.SKILL_TREE] = GameState(
            type=GameStateType.SKILL_TREE,
            name="技能树",
            pauses_game=False,
            shows_hud=True
        )
        
        self.states[GameStateType.VENDOR] = GameState(
            type=GameStateType.VENDOR,
            name="商人",
            pauses_game=True,
            shows_hud=True
        )
        
        self.states[GameStateType.CRAFTING] = GameState(
            type=GameStateType.CRAFTING,
            name="合成",
            pauses_game=True,
            shows_hud=True
        )
        
        self.states[GameStateType.DIALOGUE] = GameState(
            type=GameStateType.DIALOGUE,
            name="对话",
            pauses_game=True,
            shows_hud=True
        )
        
        self.states[GameStateType.CUTSCENE] = GameState(
            type=GameStateType.CUTSCENE,
            name="过场动画",
            pauses_game=True,
            shows_hud=False,
            allows_input=False
        )
        
        self.states[GameStateType.GAME_OVER] = GameState(
            type=GameStateType.GAME_OVER,
            name="游戏结束",
            pauses_game=True,
            shows_hud=False
        )
        
        self.states[GameStateType.SETTINGS] = GameState(
            type=GameStateType.SETTINGS,
            name="设置",
            pauses_game=True,
            shows_hud=False
        )
        
        self.states[GameStateType.CREDITS] = GameState(
            type=GameStateType.CREDITS,
            name="制作名单",
            pauses_game=True,
            shows_hud=False
        )
    
    def register_state(self, state: GameState):
        self.states[state.type] = state
    
    def change_state(self, new_state_type: GameStateType, **kwargs):
        if new_state_type not in self.states:
            print(f"Unknown state: {new_state_type}")
            return
        
        new_state = self.states[new_state_type]
        
        if self.current_state:
            self.current_state.exit()
            self.previous_state = self.current_state
        
        self.current_state = new_state
        new_state.enter(**kwargs)
        
        for callback in self.transition_callbacks:
            try:
                callback(self.previous_state, new_state)
            except Exception as e:
                print(f"State transition callback error: {e}")
    
    def push_state(self, state_type: GameStateType, **kwargs):
        if state_type not in self.states:
            return
        
        if self.current_state:
            self.state_stack.append(self.current_state.type)
        
        self.change_state(state_type, **kwargs)
    
    def pop_state(self):
        if not self.state_stack:
            return
        
        previous_type = self.state_stack.pop()
        self.change_state(previous_type)
    
    def update(self, delta_time: float):
        if self.current_state:
            self.current_state.update(delta_time)
    
    def render(self, surface: pygame.Surface):
        if self.current_state:
            self.current_state.render(surface)
    
    def handle_event(self, event: pygame.event.Event):
        if self.current_state and self.current_state.allows_input:
            self.current_state.handle_event(event)
    
    def get_current_state(self) -> Optional[GameState]:
        return self.current_state
    
    def get_current_state_type(self) -> Optional[GameStateType]:
        return self.current_state.type if self.current_state else None
    
    def is_game_paused(self) -> bool:
        return self.current_state.pauses_game if self.current_state else False
    
    def should_show_hud(self) -> bool:
        return self.current_state.shows_hud if self.current_state else False
    
    def register_transition_callback(self, callback: Callable):
        self.transition_callbacks.append(callback)
    
    def unregister_transition_callback(self, callback: Callable):
        if callback in self.transition_callbacks:
            self.transition_callbacks.remove(callback)
    
    def is_in_state(self, state_type: GameStateType) -> bool:
        return self.current_state and self.current_state.type == state_type
    
    def can_transition_to(self, state_type: GameStateType) -> bool:
        valid_transitions = {
            GameStateType.INIT: [GameStateType.LOADING, GameStateType.MAIN_MENU],
            GameStateType.LOADING: [GameStateType.MAIN_MENU, GameStateType.PLAYING],
            GameStateType.MAIN_MENU: [GameStateType.CHARACTER_SELECT, GameStateType.CHARACTER_CREATE, 
                                       GameStateType.SETTINGS, GameStateType.CREDITS],
            GameStateType.CHARACTER_SELECT: [GameStateType.MAIN_MENU, GameStateType.PLAYING],
            GameStateType.CHARACTER_CREATE: [GameStateType.MAIN_MENU, GameStateType.PLAYING],
            GameStateType.PLAYING: [GameStateType.PAUSED, GameStateType.INVENTORY, 
                                    GameStateType.CHARACTER_PANEL, GameStateType.SKILL_TREE,
                                    GameStateType.VENDOR, GameStateType.CRAFTING,
                                    GameStateType.DIALOGUE, GameStateType.CUTSCENE,
                                    GameStateType.GAME_OVER, GameStateType.MAIN_MENU],
            GameStateType.PAUSED: [GameStateType.PLAYING, GameStateType.SETTINGS, GameStateType.MAIN_MENU],
            GameStateType.INVENTORY: [GameStateType.PLAYING],
            GameStateType.CHARACTER_PANEL: [GameStateType.PLAYING],
            GameStateType.SKILL_TREE: [GameStateType.PLAYING],
            GameStateType.VENDOR: [GameStateType.PLAYING],
            GameStateType.CRAFTING: [GameStateType.PLAYING],
            GameStateType.DIALOGUE: [GameStateType.PLAYING],
            GameStateType.CUTSCENE: [GameStateType.PLAYING],
            GameStateType.GAME_OVER: [GameStateType.MAIN_MENU, GameStateType.PLAYING],
            GameStateType.SETTINGS: [GameStateType.MAIN_MENU, GameStateType.PAUSED],
            GameStateType.CREDITS: [GameStateType.MAIN_MENU],
        }
        
        if not self.current_state:
            return state_type in [GameStateType.INIT, GameStateType.MAIN_MENU]
        
        return state_type in valid_transitions.get(self.current_state.type, [])
