"""
音效资源管理器
"""
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import pygame
import os
import random


class SoundCategory(Enum):
    PLAYER = "player"
    MONSTER = "monster"
    SKILL = "skill"
    UI = "ui"
    ENVIRONMENT = "environment"
    MUSIC = "music"
    AMBIENT = "ambient"


@dataclass
class SoundConfig:
    sound_id: str
    file_path: str
    category: SoundCategory
    volume: float = 1.0
    max_concurrent: int = 3
    random_pitch: bool = False
    pitch_range: Tuple[float, float] = (0.9, 1.1)
    loop: bool = False


class SoundManager:
    def __init__(self):
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.sound_configs: Dict[str, SoundConfig] = {}
        self.music_tracks: Dict[str, str] = {}
        
        self._active_channels: Dict[str, List[int]] = {}
        
        self._master_volume = 1.0
        self._sfx_volume = 1.0
        self._music_volume = 0.8
        self._ambient_volume = 0.6
        
        self._current_music: Optional[str] = None
        self._current_ambient: List[str] = []
        
        self._create_default_sound_configs()
    
    def _create_default_sound_configs(self):
        player_sounds = [
            ("player_hit", "player/hit.wav", 0.8),
            ("player_death", "player/death.wav", 1.0),
            ("player_levelup", "player/levelup.wav", 1.0),
            ("player_footstep", "player/footstep.wav", 0.3),
            ("player_pickup", "player/pickup.wav", 0.7),
            ("player_gold", "player/gold.wav", 0.6),
        ]
        
        for sound_id, path, volume in player_sounds:
            self.sound_configs[sound_id] = SoundConfig(
                sound_id=sound_id,
                file_path=path,
                category=SoundCategory.PLAYER,
                volume=volume
            )
        
        skill_sounds = [
            ("skill_swing", "skills/swing.wav", 0.7),
            ("skill_fireball", "skills/fireball.wav", 0.9),
            ("skill_lightning", "skills/lightning.wav", 0.9),
            ("skill_ice", "skills/ice.wav", 0.8),
            ("skill_heal", "skills/heal.wav", 0.7),
            ("skill_teleport", "skills/teleport.wav", 0.8),
        ]
        
        for sound_id, path, volume in skill_sounds:
            self.sound_configs[sound_id] = SoundConfig(
                sound_id=sound_id,
                file_path=path,
                category=SoundCategory.SKILL,
                volume=volume
            )
        
        monster_sounds = [
            ("monster_hit", "monster/hit.wav", 0.6),
            ("monster_death", "monster/death.wav", 0.8),
            ("monster_aggro", "monster/aggro.wav", 0.7),
        ]
        
        for sound_id, path, volume in monster_sounds:
            self.sound_configs[sound_id] = SoundConfig(
                sound_id=sound_id,
                file_path=path,
                category=SoundCategory.MONSTER,
                volume=volume
            )
        
        ui_sounds = [
            ("ui_click", "ui/click.wav", 0.5),
            ("ui_hover", "ui/hover.wav", 0.3),
            ("ui_open", "ui/open.wav", 0.6),
            ("ui_close", "ui/close.wav", 0.5),
            ("ui_error", "ui/error.wav", 0.7),
            ("ui_success", "ui/success.wav", 0.7),
            ("item_equip", "ui/equip.wav", 0.6),
            ("item_unequip", "ui/unequip.wav", 0.5),
        ]
        
        for sound_id, path, volume in ui_sounds:
            self.sound_configs[sound_id] = SoundConfig(
                sound_id=sound_id,
                file_path=path,
                category=SoundCategory.UI,
                volume=volume
            )
        
        music_tracks = [
            ("main_menu", "music/main_menu.ogg"),
            ("town", "music/town.ogg"),
            ("exploration", "music/exploration.ogg"),
            ("combat", "music/combat.ogg"),
            ("boss", "music/boss.ogg"),
            ("credits", "music/credits.ogg"),
        ]
        
        for track_id, path in music_tracks:
            self.music_tracks[track_id] = path
    
    def load_sound(self, sound_id: str, base_path: str = "") -> bool:
        if sound_id not in self.sound_configs:
            return False
        
        config = self.sound_configs[sound_id]
        full_path = os.path.join(base_path, "assets", "sounds", config.file_path)
        
        if not os.path.exists(full_path):
            return False
        
        try:
            sound = pygame.mixer.Sound(full_path)
            self.sounds[sound_id] = sound
            return True
        except Exception as e:
            print(f"Error loading sound {sound_id}: {e}")
            return False
    
    def play_sound(self, sound_id: str, volume_mult: float = 1.0) -> bool:
        if sound_id not in self.sounds:
            return False
        
        config = self.sound_configs.get(sound_id)
        if not config:
            return False
        
        sound = self.sounds[sound_id]
        
        effective_volume = self._master_volume * self._sfx_volume * config.volume * volume_mult
        sound.set_volume(effective_volume)
        
        if config.random_pitch:
            pitch = random.uniform(config.pitch_range[0], config.pitch_range[1])
        
        channel = pygame.mixer.find_channel()
        if channel:
            channel.play(sound)
            return True
        
        return False
    
    def play_music(self, track_id: str, fade_ms: int = 1000) -> bool:
        if track_id not in self.music_tracks:
            return False
        
        if self._current_music:
            pygame.mixer.music.fadeout(fade_ms)
        
        track_path = self.music_tracks[track_id]
        
        if not os.path.exists(track_path):
            return False
        
        try:
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.set_volume(self._master_volume * self._music_volume)
            pygame.mixer.music.play(-1, fade_ms=fade_ms)
            self._current_music = track_id
            return True
        except Exception as e:
            print(f"Error playing music {track_id}: {e}")
            return False
    
    def stop_music(self, fade_ms: int = 1000):
        pygame.mixer.music.fadeout(fade_ms)
        self._current_music = None
    
    def pause_music(self):
        pygame.mixer.music.pause()
    
    def resume_music(self):
        pygame.mixer.music.unpause()
    
    def set_master_volume(self, volume: float):
        self._master_volume = max(0.0, min(1.0, volume))
        self._update_all_volumes()
    
    def set_sfx_volume(self, volume: float):
        self._sfx_volume = max(0.0, min(1.0, volume))
    
    def set_music_volume(self, volume: float):
        self._music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self._master_volume * self._music_volume)
    
    def set_ambient_volume(self, volume: float):
        self._ambient_volume = max(0.0, min(1.0, volume))
    
    def _update_all_volumes(self):
        pygame.mixer.music.set_volume(self._master_volume * self._music_volume)
    
    def get_master_volume(self) -> float:
        return self._master_volume
    
    def get_sfx_volume(self) -> float:
        return self._sfx_volume
    
    def get_music_volume(self) -> float:
        return self._music_volume
    
    def play_skill_sound(self, skill_id: str, skill_type: str = ""):
        sound_map = {
            "fire": "skill_fireball",
            "cold": "skill_ice",
            "lightning": "skill_lightning",
            "arcane": "skill_swing",
            "physical": "skill_swing",
            "holy": "skill_heal",
        }
        
        sound_id = sound_map.get(skill_type, "skill_swing")
        self.play_sound(sound_id)
    
    def play_ui_sound(self, ui_action: str):
        sound_map = {
            "click": "ui_click",
            "hover": "ui_hover",
            "open": "ui_open",
            "close": "ui_close",
            "error": "ui_error",
            "success": "ui_success",
        }
        
        sound_id = sound_map.get(ui_action)
        if sound_id:
            self.play_sound(sound_id)
    
    def cleanup(self):
        self.sounds.clear()
        self.stop_music()
