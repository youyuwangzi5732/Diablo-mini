"""
核心模块初始化
"""
from .game_engine import GameEngine
from .event_system import EventSystem, Event, EventType
from .resource_manager import ResourceManager
from .save_system import SaveSystem
from .audio_manager import AudioManager

__all__ = [
    'GameEngine',
    'EventSystem', 
    'Event',
    'EventType',
    'ResourceManager',
    'SaveSystem',
    'AudioManager'
]
