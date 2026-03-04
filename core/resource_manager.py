"""
资源管理器 - 管理游戏资源的加载、缓存和卸载
"""
import pygame

from ui.font_manager import get_font
import os
import json
from typing import Dict, Any, Optional, Tuple
from PIL import Image
import numpy as np


class ResourceManager:
    _instance: Optional['ResourceManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        self._textures: Dict[str, pygame.Surface] = {}
        self._sprites: Dict[str, Dict[str, pygame.Surface]] = {}
        self._sounds: Dict[str, pygame.mixer.Sound] = {}
        self._music: Dict[str, str] = {}
        self._fonts: Dict[str, pygame.font.Font] = {}
        self._data: Dict[str, Any] = {}
        
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.asset_path = os.path.join(self.base_path, "assets")
        
    @classmethod
    def get_instance(cls) -> 'ResourceManager':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def load_texture(self, path: str, key: str = None, 
                     scale: Tuple[int, int] = None) -> Optional[pygame.Surface]:
        if key and key in self._textures:
            return self._textures[key]
        
        full_path = os.path.join(self.asset_path, path)
        if not os.path.exists(full_path):
            print(f"Texture not found: {full_path}")
            return None
        
        try:
            surface = pygame.image.load(full_path).convert_alpha()
            if scale:
                surface = pygame.transform.scale(surface, scale)
            
            cache_key = key or path
            self._textures[cache_key] = surface
            return surface
        except Exception as e:
            print(f"Error loading texture {path}: {e}")
            return None
    
    def load_sprite_sheet(self, path: str, key: str, 
                          frame_size: Tuple[int, int], 
                          frame_count: int = None) -> Dict[str, pygame.Surface]:
        cache_key = f"sheet_{key}"
        if cache_key in self._sprites:
            return self._sprites[cache_key]
        
        full_path = os.path.join(self.asset_path, path)
        if not os.path.exists(full_path):
            print(f"Sprite sheet not found: {full_path}")
            return {}
        
        try:
            sheet = pygame.image.load(full_path).convert_alpha()
            sheet_width, sheet_height = sheet.get_size()
            frame_width, frame_height = frame_size
            
            frames = {}
            cols = sheet_width // frame_width
            rows = sheet_height // frame_height
            
            total_frames = frame_count or (cols * rows)
            
            for i in range(total_frames):
                row = i // cols
                col = i % cols
                
                x = col * frame_width
                y = row * frame_height
                
                frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame.blit(sheet, (0, 0), (x, y, frame_width, frame_height))
                frames[f"frame_{i}"] = frame
            
            self._sprites[cache_key] = frames
            return frames
        except Exception as e:
            print(f"Error loading sprite sheet {path}: {e}")
            return {}
    
    def load_sound(self, path: str, key: str = None) -> Optional[pygame.mixer.Sound]:
        cache_key = key or path
        if cache_key in self._sounds:
            return self._sounds[cache_key]
        
        full_path = os.path.join(self.asset_path, path)
        if not os.path.exists(full_path):
            print(f"Sound not found: {full_path}")
            return None
        
        try:
            sound = pygame.mixer.Sound(full_path)
            self._sounds[cache_key] = sound
            return sound
        except Exception as e:
            print(f"Error loading sound {path}: {e}")
            return None
    
    def load_music(self, path: str, key: str = None) -> str:
        cache_key = key or path
        full_path = os.path.join(self.asset_path, path)
        
        if os.path.exists(full_path):
            self._music[cache_key] = full_path
            return full_path
        
        print(f"Music not found: {full_path}")
        return ""
    
    def load_font(self, path: str, size: int, key: str = None) -> Optional[pygame.font.Font]:
        cache_key = f"{key or path}_{size}"
        if cache_key in self._fonts:
            return self._fonts[cache_key]
        
        full_path = os.path.join(self.asset_path, path)
        
        try:
            if os.path.exists(full_path):
                font = pygame.font.Font(full_path, size)
            else:
                font = pygame.font.SysFont(path, size)
            
            self._fonts[cache_key] = font
            return font
        except Exception as e:
            print(f"Error loading font {path}: {e}")
            return pygame.font.SysFont("Arial", size)
    
    def load_json(self, path: str, key: str = None) -> Optional[Dict]:
        cache_key = key or path
        if cache_key in self._data:
            return self._data[cache_key]
        
        full_path = os.path.join(self.asset_path, path)
        if not os.path.exists(full_path):
            print(f"JSON not found: {full_path}")
            return None
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self._data[cache_key] = data
            return data
        except Exception as e:
            print(f"Error loading JSON {path}: {e}")
            return None
    
    def get_texture(self, key: str) -> Optional[pygame.Surface]:
        return self._textures.get(key)
    
    def get_sprite(self, sheet_key: str, frame_name: str) -> Optional[pygame.Surface]:
        cache_key = f"sheet_{sheet_key}"
        if cache_key in self._sprites:
            return self._sprites[cache_key].get(frame_name)
        return None
    
    def get_sound(self, key: str) -> Optional[pygame.mixer.Sound]:
        return self._sounds.get(key)
    
    def get_music_path(self, key: str) -> str:
        return self._music.get(key, "")
    
    def get_font(self, key: str, size: int) -> Optional[pygame.font.Font]:
        cache_key = f"{key}_{size}"
        return self._fonts.get(cache_key)
    
    def get_data(self, key: str) -> Optional[Dict]:
        return self._data.get(key)
    
    def unload_texture(self, key: str):
        if key in self._textures:
            del self._textures[key]
    
    def unload_sound(self, key: str):
        if key in self._sounds:
            del self._sounds[key]
    
    def cleanup(self):
        self._textures.clear()
        self._sprites.clear()
        self._sounds.clear()
        self._music.clear()
        self._fonts.clear()
        self._data.clear()
    
    def preload_essential(self):
        self.load_font("fonts/main.ttf", 16, "main_16")
        self.load_font("fonts/main.ttf", 24, "main_24")
        self.load_font("fonts/main.ttf", 32, "main_32")
        self.load_font("fonts/main.ttf", 48, "main_48")
