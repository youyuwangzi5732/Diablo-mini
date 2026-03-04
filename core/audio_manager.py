"""
音频管理器 - 管理游戏音效和音乐
"""
import pygame
from typing import Dict, Optional, List
from enum import Enum
import random


class MusicState(Enum):
    NONE = 0
    MAIN_MENU = 1
    TOWN = 2
    EXPLORATION = 3
    COMBAT = 4
    BOSS = 5
    CREDITS = 6


class AudioManager:
    _instance: Optional['AudioManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        self._master_volume = 1.0
        self._music_volume = 0.8
        self._sfx_volume = 1.0
        self._voice_volume = 1.0
        
        self._current_music_state = MusicState.NONE
        self._current_track: Optional[str] = None
        self._music_playlist: Dict[MusicState, List[str]] = {
            MusicState.MAIN_MENU: [],
            MusicState.TOWN: [],
            MusicState.EXPLORATION: [],
            MusicState.COMBAT: [],
            MusicState.BOSS: [],
            MusicState.CREDITS: []
        }
        
        self._sound_channels: Dict[str, int] = {}
        self._ambient_sounds: Dict[str, pygame.mixer.Sound] = {}
        self._ambient_channels: Dict[str, int] = {}
        
    @classmethod
    def get_instance(cls) -> 'AudioManager':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def set_master_volume(self, volume: float):
        self._master_volume = max(0.0, min(1.0, volume))
        self._update_music_volume()
    
    def set_music_volume(self, volume: float):
        self._music_volume = max(0.0, min(1.0, volume))
        self._update_music_volume()
    
    def set_sfx_volume(self, volume: float):
        self._sfx_volume = max(0.0, min(1.0, volume))
    
    def set_voice_volume(self, volume: float):
        self._voice_volume = max(0.0, min(1.0, volume))
    
    def _update_music_volume(self):
        effective_volume = self._master_volume * self._music_volume
        pygame.mixer.music.set_volume(effective_volume)
    
    def play_music(self, track_path: str, loop: bool = True, fade_ms: int = 1000):
        try:
            if self._current_track:
                pygame.mixer.music.fadeout(fade_ms)
            
            pygame.mixer.music.load(track_path)
            self._update_music_volume()
            pygame.mixer.music.play(-1 if loop else 0, fade_ms=fade_ms)
            self._current_track = track_path
        except Exception as e:
            print(f"Error playing music {track_path}: {e}")
    
    def stop_music(self, fade_ms: int = 1000):
        if self._current_track:
            pygame.mixer.music.fadeout(fade_ms)
            self._current_track = None
    
    def pause_music(self):
        pygame.mixer.music.pause()
    
    def resume_music(self):
        pygame.mixer.music.unpause()
    
    def set_music_state(self, state: MusicState):
        if state == self._current_music_state:
            return
        
        self._current_music_state = state
        playlist = self._music_playlist.get(state, [])
        
        if playlist:
            track = random.choice(playlist)
            self.play_music(track)
    
    def add_to_playlist(self, state: MusicState, track_path: str):
        if state not in self._music_playlist:
            self._music_playlist[state] = []
        self._music_playlist[state].append(track_path)
    
    def play_sound(self, sound: pygame.mixer.Sound, category: str = "sfx", 
                   volume: float = 1.0, loop: bool = False) -> Optional[int]:
        if not sound:
            return None
        
        if category == "sfx":
            effective_volume = self._master_volume * self._sfx_volume * volume
        elif category == "voice":
            effective_volume = self._master_volume * self._voice_volume * volume
        else:
            effective_volume = self._master_volume * volume
        
        sound.set_volume(effective_volume)
        
        channel = pygame.mixer.find_channel()
        if channel:
            channel.play(sound, loops=-1 if loop else 0)
            return channel.get_iden()
        
        return None
    
    def stop_sound(self, channel_id: int):
        for i in range(pygame.mixer.get_num_channels()):
            channel = pygame.mixer.Channel(i)
            if channel.get_iden() == channel_id:
                channel.stop()
                break
    
    def play_ambient(self, name: str, sound: pygame.mixer.Sound, volume: float = 0.5):
        if name in self._ambient_channels:
            return
        
        effective_volume = self._master_volume * self._sfx_volume * volume
        sound.set_volume(effective_volume)
        
        channel = pygame.mixer.find_channel()
        if channel:
            channel.play(sound, loops=-1)
            self._ambient_sounds[name] = sound
            self._ambient_channels[name] = channel.get_iden()
    
    def stop_ambient(self, name: str, fade_ms: int = 500):
        if name in self._ambient_channels:
            for i in range(pygame.mixer.get_num_channels()):
                channel = pygame.mixer.Channel(i)
                if channel.get_iden() == self._ambient_channels[name]:
                    channel.fadeout(fade_ms)
                    break
            
            del self._ambient_sounds[name]
            del self._ambient_channels[name]
    
    def stop_all_ambient(self):
        for name in list(self._ambient_channels.keys()):
            self.stop_ambient(name, 0)
    
    def stop_all_sounds(self):
        pygame.mixer.stop()
    
    def cleanup(self):
        self.stop_music(0)
        self.stop_all_sounds()
        self._ambient_sounds.clear()
        self._ambient_channels.clear()
    
    def get_master_volume(self) -> float:
        return self._master_volume
    
    def get_music_volume(self) -> float:
        return self._music_volume
    
    def get_sfx_volume(self) -> float:
        return self._sfx_volume
    
    def get_voice_volume(self) -> float:
        return self._voice_volume
