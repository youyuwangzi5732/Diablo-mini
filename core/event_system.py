"""
事件系统 - 处理游戏内各种事件
"""
from enum import Enum, auto
from typing import Callable, Dict, List, Any, Optional
from dataclasses import dataclass, field
import time


class EventType(Enum):
    GAME_START = auto()
    GAME_PAUSE = auto()
    GAME_RESUME = auto()
    GAME_SAVE = auto()
    GAME_LOAD = auto()
    
    PLAYER_LEVEL_UP = auto()
    PLAYER_DEATH = auto()
    PLAYER_RESPAWN = auto()
    PLAYER_SKILL_UNLOCK = auto()
    PLAYER_ATTRIBUTE_CHANGE = auto()
    
    ITEM_PICKUP = auto()
    ITEM_DROP = auto()
    ITEM_EQUIP = auto()
    ITEM_UNEQUIP = auto()
    ITEM_SELL = auto()
    ITEM_BUY = auto()
    ITEM_CRAFT = auto()
    ITEM_SOCKET = auto()
    
    COMBAT_DAMAGE = auto()
    COMBAT_HEAL = auto()
    COMBAT_KILL = auto()
    COMBAT_MISS = auto()
    COMBAT_DODGE = auto()
    COMBAT_CRIT = auto()
    
    SKILL_USE = auto()
    SKILL_COOLDOWN_START = auto()
    SKILL_COOLDOWN_END = auto()
    
    QUEST_START = auto()
    QUEST_COMPLETE = auto()
    QUEST_FAIL = auto()
    QUEST_UPDATE = auto()
    
    NPC_INTERACT = auto()
    NPC_DIALOGUE = auto()
    NPC_TRADE = auto()
    
    AREA_ENTER = auto()
    AREA_EXIT = auto()
    DUNGEON_COMPLETE = auto()
    BOSS_SPAWN = auto()
    BOSS_KILL = auto()
    
    ACHIEVEMENT_UNLOCK = auto()
    LORE_DISCOVER = auto()
    
    UI_OPEN = auto()
    UI_CLOSE = auto()
    UI_CLICK = auto()
    
    AUDIO_PLAY = auto()
    AUDIO_STOP = auto()
    MUSIC_CHANGE = auto()


@dataclass
class Event:
    event_type: EventType
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    source: Optional[str] = None
    target: Optional[str] = None
    propagation: bool = True
    
    def stop_propagation(self):
        self.propagation = False


class EventSystem:
    _instance: Optional['EventSystem'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        self._listeners: Dict[EventType, List[Callable]] = {}
        self._event_queue: List[Event] = []
        self._max_queue_size = 1000
        
    @classmethod
    def get_instance(cls) -> 'EventSystem':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def subscribe(self, event_type: EventType, callback: Callable[[Event], None]) -> int:
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)
        return len(self._listeners[event_type]) - 1
    
    def unsubscribe(self, event_type: EventType, callback: Callable[[Event], None]):
        if event_type in self._listeners:
            try:
                self._listeners[event_type].remove(callback)
            except ValueError:
                pass
    
    def unsubscribe_by_id(self, event_type: EventType, callback_id: int):
        if event_type in self._listeners and callback_id < len(self._listeners[event_type]):
            self._listeners[event_type][callback_id] = None
    
    def emit(self, event_type: EventType, data: Dict[str, Any] = None, 
             source: str = None, target: str = None) -> Event:
        event = Event(
            event_type=event_type,
            data=data or {},
            source=source,
            target=target
        )
        
        if len(self._event_queue) < self._max_queue_size:
            self._event_queue.append(event)
        
        return event
    
    def emit_immediate(self, event_type: EventType, data: Dict[str, Any] = None,
                       source: str = None, target: str = None):
        event = Event(
            event_type=event_type,
            data=data or {},
            source=source,
            target=target
        )
        self._process_event(event)
    
    def process_events(self):
        while self._event_queue:
            event = self._event_queue.pop(0)
            self._process_event(event)
    
    def _process_event(self, event: Event):
        if event.event_type in self._listeners:
            for callback in self._listeners[event.event_type]:
                if callback is not None and event.propagation:
                    try:
                        callback(event)
                    except Exception as e:
                        print(f"Event callback error: {e}")
    
    def clear_queue(self):
        self._event_queue.clear()
    
    def get_queue_size(self) -> int:
        return len(self._event_queue)
