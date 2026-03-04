"""
游戏引擎核心类
"""
import pygame
import sys
from typing import Optional, Dict, Any
from config.game_config import GameConfig


class GameEngine:
    _instance: Optional['GameEngine'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        self.config = GameConfig()
        self.screen = pygame.display.set_mode(
            (self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT),
            pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE
        )
        pygame.display.set_caption("暗黑迷你 - Diablo Mini")
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False
        
        self.current_state = "main_menu"
        self.states: Dict[str, Any] = {}
        
        self.managers = {}
        self.systems = {}
        
        self.delta_time = 0.0
        self.game_time = 0.0
        
    @classmethod
    def get_instance(cls) -> 'GameEngine':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def register_manager(self, name: str, manager: Any):
        self.managers[name] = manager
        
    def get_manager(self, name: str) -> Optional[Any]:
        return self.managers.get(name)
    
    def register_system(self, name: str, system: Any):
        self.systems[name] = system
        
    def get_system(self, name: str) -> Optional[Any]:
        return self.systems.get(name)
    
    def register_state(self, name: str, state: Any):
        self.states[name] = state
        
    def change_state(self, state_name: str, **kwargs):
        if state_name in self.states:
            if hasattr(self.states.get(self.current_state), 'exit'):
                self.states[self.current_state].exit()
            self.current_state = state_name
            if hasattr(self.states[state_name], 'enter'):
                self.states[state_name].enter(**kwargs)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.current_state == "game":
                        self.paused = not self.paused
                    elif self.current_state == "main_menu":
                        self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.config.SCREEN_WIDTH = event.w
                self.config.SCREEN_HEIGHT = event.h
                self.screen = pygame.display.set_mode(
                    (event.w, event.h),
                    pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE
                )
            
            if self.current_state in self.states:
                state = self.states[self.current_state]
                if hasattr(state, 'handle_event'):
                    state.handle_event(event)
    
    def update(self):
        if self.paused and self.current_state == "game":
            return
            
        if self.current_state in self.states:
            state = self.states[self.current_state]
            if hasattr(state, 'update'):
                state.update(self.delta_time)
        
        for system in self.systems.values():
            if hasattr(system, 'update'):
                system.update(self.delta_time)
    
    def render(self):
        self.screen.fill((0, 0, 0))
        
        if self.current_state in self.states:
            state = self.states[self.current_state]
            if hasattr(state, 'render'):
                state.render(self.screen)
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.delta_time = self.clock.tick(self.config.FPS) / 1000.0
            self.game_time += self.delta_time
            
            self.handle_events()
            self.update()
            self.render()
        
        self.quit()
    
    def quit(self):
        for manager in self.managers.values():
            if hasattr(manager, 'cleanup'):
                manager.cleanup()
        
        for system in self.systems.values():
            if hasattr(system, 'cleanup'):
                system.cleanup()
        
        pygame.quit()
        sys.exit()
