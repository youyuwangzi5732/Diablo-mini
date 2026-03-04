# Diablo Mini - 资源替换指南

本文档详细说明如何替换游戏中的各类资源，包括人物建模、动作模组、建筑/植物/地形资源、音乐资源等。

---

## 目录

1. [项目结构概览](#1-项目结构概览)
2. [资源系统架构](#2-资源系统架构)
3. [人物建模替换](#3-人物建模替换)
4. [动作模组替换](#4-动作模组替换)
5. [建筑/植物/地形资源](#5-建筑植物地形资源)
6. [音乐音效资源](#6-音乐音效资源)
7. [UI资源替换](#7-ui资源替换)
8. [资源格式规范](#8-资源格式规范)
9. [资源加载流程](#9-资源加载流程)
10. [最佳实践](#10-最佳实践)

---

## 1. 项目结构概览

```
Diablo-mini/
├── main.py                 # 主入口
├── config/                 # 配置模块
│   └── game_config.py      # 游戏配置（颜色、尺寸等）
├── core/                   # 核心系统
│   ├── resource_manager.py # 资源管理器
│   ├── audio_manager.py    # 音频管理器
│   └── save_system.py      # 存档系统
├── entities/               # 实体类
│   ├── character/          # 角色系统
│   │   ├── character.py    # 角色主类
│   │   ├── character_class.py  # 职业定义
│   │   ├── attributes.py   # 属性系统
│   │   └── paragon.py      # 巅峰系统
│   └── items/              # 物品系统
│       ├── item.py         # 物品基类
│       ├── equipment.py    # 装备类
│       ├── gem.py          # 宝石系统
│       └── rune.py         # 符文系统
├── systems/                # 游戏系统
│   ├── animation.py        # 动画系统
│   ├── particles.py        # 粒子系统
│   ├── sound_manager.py    # 音效管理
│   └── combat/             # 战斗系统
│       └── monster.py      # 怪物定义
├── ui/                     # UI模块
│   ├── hud.py              # 游戏HUD
│   ├── inventory_ui.py     # 背包界面
│   └── ...
└── assets/                 # 资源目录（需创建）
    ├── sprites/            # 精灵图片
    ├── animations/         # 动画文件
    ├── audio/              # 音频文件
    ├── fonts/              # 字体文件
    └── tiles/              # 地形瓦片
```

---

## 2. 资源系统架构

### 2.1 当前资源管理器

位置: `core/resource_manager.py`

```python
class ResourceManager:
    """
    资源管理器 - 负责加载和缓存所有游戏资源
    
    使用方式:
        manager = ResourceManager()
        manager.load_image("player", "assets/sprites/player.png")
        player_sprite = manager.get_image("player")
    """
    
    def __init__(self):
        self._images: Dict[str, pygame.Surface] = {}
        self._sounds: Dict[str, pygame.mixer.Sound] = {}
        self._fonts: Dict[str, pygame.font.Font] = {}
        self._animations: Dict[str, Dict] = {}
```

### 2.2 创建资源目录

首先创建资源目录结构：

```python
# 在项目根目录创建 assets 文件夹
import os

def create_asset_directories():
    directories = [
        "assets/sprites/characters",
        "assets/sprites/monsters",
        "assets/sprites/items",
        "assets/sprites/tiles",
        "assets/sprites/ui",
        "assets/animations/characters",
        "assets/animations/effects",
        "assets/audio/music",
        "assets/audio/sfx",
        "assets/fonts",
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
```

---

## 3. 人物建模替换

### 3.1 角色精灵系统

**当前实现**: 角色使用简单的圆形渲染

**文件位置**: `main.py` 第 1057-1072 行

```python
# 当前渲染方式
def _render_player(self, surface: pygame.Surface):
    pygame.draw.circle(surface, (100, 150, 255), (x, y), 20)
```

### 3.2 替换为精灵图片

**步骤 1**: 创建角色精灵类

```python
# entities/character/sprite.py

import pygame
from typing import Dict, List, Tuple
from enum import Enum

class Direction(Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"

class CharacterSprite:
    """
    角色精灵类 - 支持多方向动画
    
    资源格式要求:
        - 每个方向一帧或多帧动画
        - 推荐尺寸: 64x64 或 128x128 像素
        - 格式: PNG (带透明通道)
    
    文件命名规范:
        assets/sprites/characters/{class_id}/
            ├── idle_down_0.png
            ├── idle_down_1.png
            ├── walk_down_0.png
            ├── walk_down_1.png
            ├── attack_down_0.png
            └── ...
    """
    
    def __init__(self, class_id: str, resource_manager):
        self.class_id = class_id
        self.resource_manager = resource_manager
        
        self.sprites: Dict[str, List[pygame.Surface]] = {}
        self.current_animation = "idle"
        self.current_direction = Direction.DOWN
        self.current_frame = 0
        self.animation_speed = 0.1
        self.animation_timer = 0.0
        
        self._load_sprites()
    
    def _load_sprites(self):
        """加载角色精灵"""
        base_path = f"assets/sprites/characters/{self.class_id}"
        
        animations = ["idle", "walk", "attack", "cast", "death"]
        directions = ["up", "down", "left", "right"]
        
        for anim in animations:
            for direction in directions:
                frames = []
                frame_index = 0
                
                while True:
                    path = f"{base_path}/{anim}_{direction}_{frame_index}.png"
                    try:
                        surface = pygame.image.load(path).convert_alpha()
                        frames.append(surface)
                        frame_index += 1
                    except FileNotFoundError:
                        break
                
                if frames:
                    key = f"{anim}_{direction}"
                    self.sprites[key] = frames
    
    def set_animation(self, animation: str, direction: Direction = None):
        """设置当前动画"""
        if direction:
            self.current_direction = direction
        
        key = f"{animation}_{self.current_direction.value}"
        if key in self.sprites and self.current_animation != animation:
            self.current_animation = animation
            self.current_frame = 0
            self.animation_timer = 0.0
    
    def update(self, delta_time: float):
        """更新动画帧"""
        key = f"{self.current_animation}_{self.current_direction.value}"
        
        if key in self.sprites:
            frames = self.sprites[key]
            self.animation_timer += delta_time
            
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0.0
                self.current_frame = (self.current_frame + 1) % len(frames)
    
    def render(self, surface: pygame.Surface, position: Tuple[int, int]):
        """渲染当前帧"""
        key = f"{self.current_animation}_{self.current_direction.value}"
        
        if key in self.sprites:
            frame = self.sprites[key][self.current_frame]
            rect = frame.get_rect(center=position)
            surface.blit(frame, rect)
```

**步骤 2**: 修改角色类以使用精灵

```python
# entities/character/character.py

class Character:
    def __init__(self, class_id: str, name: str):
        # ... 现有初始化代码 ...
        
        # 添加精灵
        from .sprite import CharacterSprite
        self.sprite = CharacterSprite(class_id, resource_manager)
    
    def update(self, delta_time: float):
        # ... 现有更新代码 ...
        
        # 更新动画
        self.sprite.update(delta_time)
        
        # 根据移动方向设置动画
        if self.is_moving:
            self.sprite.set_animation("walk", self.facing_direction)
        else:
            self.sprite.set_animation("idle")
```

**步骤 3**: 修改渲染代码

```python
# main.py

def _render_player(self, surface: pygame.Surface):
    if not self.data.player:
        return
    
    cam_x, cam_y = self.data.camera_offset
    x, y = self.data.player.position
    screen_x = int(x * 64 - cam_x) + 32
    screen_y = int(y * 64 - cam_y) + 32
    
    # 使用精灵渲染
    self.data.player.sprite.render(surface, (screen_x, screen_y))
```

### 3.3 角色精灵资源规范

| 属性 | 推荐值 | 说明 |
|------|--------|------|
| 帧尺寸 | 64x64 或 128x128 | 像素 |
| 帧率 | 10-15 FPS | 动画速度 |
| 方向数 | 4 或 8 | 四方向或八方向 |
| 动画类型 | idle, walk, attack, cast, death, hurt | 基础动画 |
| 文件格式 | PNG | 带透明通道 |
| 色彩深度 | 32-bit RGBA | 支持透明度 |

---

## 4. 动作模组替换

### 4.1 动画系统架构

**文件位置**: `systems/animation.py`

```python
@dataclass
class AnimationFrame:
    sprite: pygame.Surface
    duration: float
    offset: Tuple[int, int] = (0, 0)
    hitbox: Optional[pygame.Rect] = None
    effects: List[Dict] = field(default_factory=list)

@dataclass
class Animation:
    id: str
    name: str
    frames: List[AnimationFrame]
    loop: bool = True
    interruptible: bool = True
    
    def get_current_frame(self, time: float) -> AnimationFrame:
        total_duration = sum(f.duration for f in self.frames)
        current_time = time % total_duration
        
        for frame in self.frames:
            if current_time < frame.duration:
                return frame
            current_time -= frame.duration
        
        return self.frames[-1]
```

### 4.2 创建动画数据文件

**JSON格式动画定义**:

```json
// assets/animations/characters/barbarian_attack.json
{
    "id": "barbarian_attack",
    "name": "野蛮人攻击",
    "loop": false,
    "interruptible": false,
    "total_duration": 0.6,
    "frames": [
        {
            "sprite": "barbarian_attack_0.png",
            "duration": 0.1,
            "offset": [0, 0],
            "hitbox": null,
            "effects": []
        },
        {
            "sprite": "barbarian_attack_1.png",
            "duration": 0.1,
            "offset": [5, 0],
            "hitbox": {"x": 30, "y": 0, "width": 40, "height": 60},
            "effects": [
                {"type": "swing", "frame": 1}
            ]
        },
        {
            "sprite": "barbarian_attack_2.png",
            "duration": 0.15,
            "offset": [10, 0],
            "hitbox": {"x": 40, "y": -10, "width": 50, "height": 80},
            "effects": [
                {"type": "hit", "damage_multiplier": 1.0}
            ]
        },
        {
            "sprite": "barbarian_attack_3.png",
            "duration": 0.15,
            "offset": [5, 0],
            "hitbox": null,
            "effects": []
        },
        {
            "sprite": "barbarian_attack_4.png",
            "duration": 0.1,
            "offset": [0, 0],
            "hitbox": null,
            "effects": []
        }
    ]
}
```

### 4.3 动画加载器

```python
# systems/animation_loader.py

import json
import pygame
from typing import Dict, List
from .animation import Animation, AnimationFrame

class AnimationLoader:
    """
    动画加载器 - 从JSON文件加载动画数据
    """
    
    def __init__(self, resource_manager):
        self.resource_manager = resource_manager
    
    def load_animation(self, json_path: str) -> Animation:
        """从JSON文件加载动画"""
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        frames = []
        for frame_data in data['frames']:
            sprite = self._load_sprite(frame_data['sprite'])
            
            hitbox = None
            if 'hitbox' in frame_data:
                hb = frame_data['hitbox']
                hitbox = pygame.Rect(hb['x'], hb['y'], hb['width'], hb['height'])
            
            frame = AnimationFrame(
                sprite=sprite,
                duration=frame_data['duration'],
                offset=tuple(frame_data.get('offset', [0, 0])),
                hitbox=hitbox,
                effects=frame_data.get('effects', [])
            )
            frames.append(frame)
        
        return Animation(
            id=data['id'],
            name=data['name'],
            frames=frames,
            loop=data.get('loop', True),
            interruptible=data.get('interruptible', True)
        )
    
    def _load_sprite(self, sprite_name: str) -> pygame.Surface:
        """加载精灵图片"""
        path = f"assets/sprites/{sprite_name}"
        return pygame.image.load(path).convert_alpha()
```

### 4.4 动作模组资源规范

| 动作类型 | 帧数 | 持续时间 | 说明 |
|----------|------|----------|------|
| idle | 4-8 | 0.8-1.5s | 待机动画 |
| walk | 6-8 | 0.5-0.8s | 行走循环 |
| run | 6-8 | 0.3-0.5s | 奔跑循环 |
| attack | 4-6 | 0.4-0.8s | 普通攻击 |
| skill | 6-10 | 0.6-1.2s | 技能释放 |
| cast | 6-10 | 0.8-1.5s | 施法动画 |
| hurt | 2-3 | 0.2-0.3s | 受击动画 |
| death | 6-10 | 1.0-2.0s | 死亡动画 |

---

## 5. 建筑/植物/地形资源

### 5.1 地形瓦片系统

**创建瓦片管理器**:

```python
# systems/tile_manager.py

import pygame
from typing import Dict, Tuple
from enum import Enum

class TileType(Enum):
    GRASS = "grass"
    DIRT = "dirt"
    STONE = "stone"
    WATER = "water"
    SAND = "sand"
    SNOW = "snow"
    LAVA = "lava"

class TileManager:
    """
    地形瓦片管理器
    
    资源格式要求:
        - 瓦片尺寸: 64x64 像素
        - 格式: PNG
        - 支持自动边缘过渡
    
    文件结构:
        assets/sprites/tiles/
            ├── grass.png
            ├── grass_edge_top.png
            ├── grass_edge_bottom.png
            ├── dirt.png
            ├── stone.png
            └── ...
    """
    
    TILE_SIZE = 64
    
    def __init__(self):
        self.tiles: Dict[str, pygame.Surface] = {}
        self.tile_variants: Dict[str, List[pygame.Surface]] = {}
        self._load_tiles()
    
    def _load_tiles(self):
        """加载所有瓦片"""
        tile_types = [
            "grass", "dirt", "stone", "water", 
            "sand", "snow", "lava", "void"
        ]
        
        for tile_type in tile_types:
            # 加载基础瓦片
            base_path = f"assets/sprites/tiles/{tile_type}.png"
            try:
                self.tiles[tile_type] = pygame.image.load(base_path).convert_alpha()
            except FileNotFoundError:
                self.tiles[tile_type] = self._create_fallback_tile(tile_type)
            
            # 加载变体
            self.tile_variants[tile_type] = []
            for i in range(4):  # 4种变体
                variant_path = f"assets/sprites/tiles/{tile_type}_{i}.png"
                try:
                    variant = pygame.image.load(variant_path).convert_alpha()
                    self.tile_variants[tile_type].append(variant)
                except FileNotFoundError:
                    pass
    
    def _create_fallback_tile(self, tile_type: str) -> pygame.Surface:
        """创建备用瓦片（纯色）"""
        colors = {
            "grass": (50, 120, 50),
            "dirt": (139, 90, 43),
            "stone": (128, 128, 128),
            "water": (50, 100, 200),
            "sand": (194, 178, 128),
            "snow": (240, 240, 255),
            "lava": (255, 100, 0),
            "void": (20, 20, 20),
        }
        
        surface = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE))
        surface.fill(colors.get(tile_type, (100, 100, 100)))
        return surface
    
    def get_tile(self, tile_type: str, variant: int = -1) -> pygame.Surface:
        """获取瓦片"""
        if variant >= 0 and tile_type in self.tile_variants:
            variants = self.tile_variants[tile_type]
            if variants and variant < len(variants):
                return variants[variant]
        
        return self.tiles.get(tile_type, self.tiles["void"])
```

### 5.2 建筑和环境物体

```python
# systems/environment_objects.py

from dataclasses import dataclass
from typing import Tuple, Optional
import pygame

@dataclass
class EnvironmentObject:
    """
    环境物体定义
    
    资源格式:
        assets/sprites/environment/
            ├── tree_0.png
            ├── tree_1.png
            ├── rock_0.png
            ├── chest_0.png
            ├── barrel_0.png
            └── ...
    """
    id: str
    name: str
    sprite: pygame.Surface
    position: Tuple[float, float]
    size: Tuple[int, int]
    blocking: bool = False
    destructible: bool = False
    interactable: bool = False
    shadow: Optional[pygame.Surface] = None

class EnvironmentObjectFactory:
    OBJECTS = {
        "tree": {
            "sprites": ["tree_0.png", "tree_1.png", "tree_2.png"],
            "size": (64, 96),
            "blocking": True,
            "shadow": True
        },
        "rock": {
            "sprites": ["rock_0.png", "rock_1.png"],
            "size": (48, 48),
            "blocking": True,
            "shadow": False
        },
        "chest": {
            "sprites": ["chest_closed.png", "chest_open.png"],
            "size": (48, 32),
            "blocking": True,
            "interactable": True
        },
        "barrel": {
            "sprites": ["barrel_0.png"],
            "size": (32, 48),
            "blocking": True,
            "destructible": True
        },
    }
    
    @classmethod
    def create(cls, object_type: str, position: Tuple[float, float]) -> EnvironmentObject:
        """创建环境物体"""
        config = cls.OBJECTS.get(object_type)
        if not config:
            raise ValueError(f"Unknown object type: {object_type}")
        
        sprite_path = f"assets/sprites/environment/{config['sprites'][0]}"
        sprite = pygame.image.load(sprite_path).convert_alpha()
        
        shadow = None
        if config.get("shadow"):
            shadow = cls._create_shadow(config["size"])
        
        return EnvironmentObject(
            id=f"{object_type}_{id(position)}",
            name=object_type,
            sprite=sprite,
            position=position,
            size=config["size"],
            blocking=config.get("blocking", False),
            destructible=config.get("destructible", False),
            interactable=config.get("interactable", False),
            shadow=shadow
        )
    
    @classmethod
    def _create_shadow(cls, size: Tuple[int, int]) -> pygame.Surface:
        """创建阴影"""
        shadow = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 80), 
                           (0, size[1]//2, size[0], size[1]//3))
        return shadow
```

### 5.3 地形资源规范

| 资源类型 | 尺寸 | 格式 | 说明 |
|----------|------|------|------|
| 地形瓦片 | 64x64 | PNG | 无透明通道 |
| 树木 | 64x96 | PNG | 带透明通道 |
| 岩石 | 48x48 | PNG | 带透明通道 |
| 建筑 | 128x128+ | PNG | 可多瓦片组合 |
| 装饰物 | 32x32 | PNG | 带透明通道 |

---

## 6. 音乐音效资源

### 6.1 音频管理器扩展

**文件位置**: `core/audio_manager.py`

```python
# 扩展音频管理器以支持外部音频文件

class AudioManager:
    """
    音频管理器 - 支持加载外部音频文件
    
    资源格式要求:
        音乐: OGG 或 MP3 (推荐OGG)
        音效: WAV 或 OGG
    
    文件结构:
        assets/audio/
            ├── music/
            │   ├── main_menu.ogg
            │   ├── town.ogg
            │   ├── combat.ogg
            │   └── boss.ogg
            └── sfx/
                ├── attack_0.wav
                ├── hit_0.wav
                ├── pickup.wav
                └── ...
    """
    
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        self.music_volume = 0.8
        self.sfx_volume = 1.0
        
        self.current_music: Optional[str] = None
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        
        self._load_audio()
    
    def _load_audio(self):
        """加载所有音频"""
        # 加载音效
        sfx_dir = "assets/audio/sfx"
        if os.path.exists(sfx_dir):
            for filename in os.listdir(sfx_dir):
                if filename.endswith(('.wav', '.ogg')):
                    name = os.path.splitext(filename)[0]
                    path = os.path.join(sfx_dir, filename)
                    self.sounds[name] = pygame.mixer.Sound(path)
                    self.sounds[name].set_volume(self.sfx_volume)
    
    def play_music(self, music_id: str, loop: bool = True, fade_ms: int = 1000):
        """播放音乐"""
        path = f"assets/audio/music/{music_id}.ogg"
        
        if not os.path.exists(path):
            path = f"assets/audio/music/{music_id}.mp3"
        
        if os.path.exists(path):
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1 if loop else 0, fade_ms=fade_ms)
            self.current_music = music_id
    
    def play_sfx(self, sfx_id: str, volume: float = 1.0):
        """播放音效"""
        if sfx_id in self.sounds:
            sound = self.sounds[sfx_id]
            sound.set_volume(volume * self.sfx_volume)
            sound.play()
    
    def stop_music(self, fade_ms: int = 1000):
        """停止音乐"""
        pygame.mixer.music.fadeout(fade_ms)
        self.current_music = None
```

### 6.2 音效触发点

在游戏代码中添加音效触发：

```python
# 战斗音效
def _attack_monster(self, monster):
    # ... 攻击逻辑 ...
    
    # 播放攻击音效
    self.audio_manager.play_sfx("sword_swing")
    
    # 命中时
    if damage_result["final_damage"] > 0:
        self.audio_manager.play_sfx("hit_flesh")

# 物品音效
def _collect_loot(self, dropped):
    # ... 拾取逻辑 ...
    
    if dropped.is_gold:
        self.audio_manager.play_sfx("gold_pickup")
    else:
        self.audio_manager.play_sfx("item_pickup")

# UI音效
def _on_button_click(self):
    self.audio_manager.play_sfx("ui_click")
```

### 6.3 音频资源规范

| 类型 | 格式 | 采样率 | 比特率 | 说明 |
|------|------|--------|--------|------|
| 背景音乐 | OGG | 44100 Hz | 128-256 kbps | 循环播放 |
| 环境音效 | OGG | 44100 Hz | 128 kbps | 循环播放 |
| 技能音效 | WAV/OGG | 44100 Hz | - | 短促清晰 |
| UI音效 | WAV | 22050 Hz | - | 简短 |
| 语音 | OGG | 44100 Hz | 128 kbps | 压缩格式 |

---

## 7. UI资源替换

### 7.1 UI图片资源

```python
# ui/ui_assets.py

class UIAssets:
    """
    UI资源管理
    
    文件结构:
        assets/sprites/ui/
            ├── buttons/
            │   ├── button_normal.png
            │   ├── button_hover.png
            │   └── button_pressed.png
            ├── panels/
            │   ├── inventory_bg.png
            │   ├── character_panel.png
            │   └── skill_tree_bg.png
            ├── icons/
            │   ├── skills/
            │   ├── items/
            │   └── buffs/
            └── frames/
                ├── item_frame.png
                └── skill_slot.png
    """
    
    def __init__(self):
        self.buttons: Dict[str, pygame.Surface] = {}
        self.panels: Dict[str, pygame.Surface] = {}
        self.icons: Dict[str, pygame.Surface] = {}
        self.frames: Dict[str, pygame.Surface] = {}
        
        self._load_assets()
    
    def _load_assets(self):
        """加载UI资源"""
        # 加载按钮
        for state in ["normal", "hover", "pressed", "disabled"]:
            path = f"assets/sprites/ui/buttons/button_{state}.png"
            try:
                self.buttons[state] = pygame.image.load(path).convert_alpha()
            except FileNotFoundError:
                self.buttons[state] = self._create_fallback_button(state)
        
        # 加载面板
        for panel in ["inventory", "character", "skills", "quest"]:
            path = f"assets/sprites/ui/panels/{panel}_bg.png"
            try:
                self.panels[panel] = pygame.image.load(path).convert_alpha()
            except FileNotFoundError:
                pass
    
    def _create_fallback_button(self, state: str) -> pygame.Surface:
        """创建备用按钮"""
        colors = {
            "normal": (60, 60, 80),
            "hover": (80, 80, 100),
            "pressed": (40, 40, 60),
            "disabled": (50, 50, 50),
        }
        
        surface = pygame.Surface((120, 40), pygame.SRCALPHA)
        pygame.draw.rect(surface, colors[state], (0, 0, 120, 40), border_radius=5)
        pygame.draw.rect(surface, (100, 100, 120), (0, 0, 120, 40), 2, border_radius=5)
        return surface
```

### 7.2 技能图标系统

```python
# ui/skill_icons.py

class SkillIconManager:
    """
    技能图标管理
    
    文件结构:
        assets/sprites/ui/icons/skills/
            ├── barbarian/
            │   ├── bash.png
            │   ├── cleave.png
            │   └── whirlwind.png
            ├── wizard/
            │   ├── magic_missile.png
            │   └── meteor.png
            └── ...
    """
    
    def __init__(self):
        self.icons: Dict[str, pygame.Surface] = {}
        self._load_icons()
    
    def _load_icons(self):
        """加载所有技能图标"""
        base_path = "assets/sprites/ui/icons/skills"
        
        if not os.path.exists(base_path):
            return
        
        for class_dir in os.listdir(base_path):
            class_path = os.path.join(base_path, class_dir)
            if os.path.isdir(class_path):
                for icon_file in os.listdir(class_path):
                    if icon_file.endswith('.png'):
                        skill_id = os.path.splitext(icon_file)[0]
                        icon_path = os.path.join(class_path, icon_file)
                        self.icons[skill_id] = pygame.image.load(icon_path).convert_alpha()
    
    def get_icon(self, skill_id: str, size: Tuple[int, int] = (48, 48)) -> pygame.Surface:
        """获取技能图标"""
        if skill_id in self.icons:
            icon = self.icons[skill_id]
            if icon.get_size() != size:
                icon = pygame.transform.scale(icon, size)
            return icon
        
        # 返回默认图标
        return self._create_default_icon(size)
    
    def _create_default_icon(self, size: Tuple[int, int]) -> pygame.Surface:
        """创建默认图标"""
        surface = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(surface, (40, 40, 60), (0, 0, *size), border_radius=4)
        pygame.draw.rect(surface, (80, 80, 100), (0, 0, *size), 2, border_radius=4)
        
        font = pygame.font.SysFont("Arial", 12)
        text = font.render("?", True, (150, 150, 150))
        text_rect = text.get_rect(center=(size[0]//2, size[1]//2))
        surface.blit(text, text_rect)
        
        return surface
```

---

## 8. 资源格式规范

### 8.1 图片资源

| 类型 | 格式 | 色彩深度 | 透明通道 | 推荐工具 |
|------|------|----------|----------|----------|
| 精灵 | PNG | 32-bit RGBA | 是 | Aseprite, Photoshop |
| UI | PNG | 32-bit RGBA | 是 | Figma, Photoshop |
| 瓦片 | PNG | 24-bit RGB | 否 | Tiled, Aseprite |
| 图标 | PNG | 32-bit RGBA | 是 | Aseprite |

### 8.2 音频资源

| 类型 | 格式 | 采样率 | 声道 | 推荐工具 |
|------|------|--------|------|----------|
| 音乐 | OGG Vorbis | 44100 Hz | 立体声 | Audacity, FL Studio |
| 音效 | WAV/OGG | 44100 Hz | 单声道/立体声 | Audacity |
| 语音 | OGG Vorbis | 44100 Hz | 单声道 | Audacity |

### 8.3 动画资源

| 类型 | 格式 | 说明 |
|------|------|------|
| 帧动画 | PNG序列 | 每帧一个文件 |
| 动画数据 | JSON | 帧时长、偏移、碰撞框 |
| 骨骼动画 | Spine/DragonBones | 可选，需额外支持 |

---

## 9. 资源加载流程

### 9.1 初始化加载

```python
# main.py

def _initialize_resources(self):
    """初始化所有资源"""
    print("正在加载资源...")
    
    # 1. 加载UI资源
    self.ui_assets = UIAssets()
    print("  UI资源加载完成")
    
    # 2. 加载瓦片
    self.tile_manager = TileManager()
    print("  地形瓦片加载完成")
    
    # 3. 加载音频
    self.audio_manager = AudioManager()
    print("  音频资源加载完成")
    
    # 4. 加载技能图标
    self.skill_icons = SkillIconManager()
    print("  技能图标加载完成")
    
    # 5. 预加载角色精灵
    self.character_sprites = {}
    for class_id in ["barbarian", "wizard", "demon_hunter", "monk", 
                     "necromancer", "crusader", "druid", "assassin"]:
        self.character_sprites[class_id] = CharacterSprite(class_id, self.resource_manager)
    print("  角色精灵加载完成")
    
    print("资源加载完成！")
```

### 9.2 按需加载

```python
# 按区域加载资源
def _on_area_change(self, new_area_id: str):
    """区域切换时的资源加载"""
    area = self.world.get_area(new_area_id)
    
    # 加载该区域的怪物精灵
    for spawn in area.monster_spawns:
        monster_id = spawn["monster_id"]
        if monster_id not in self.monster_sprites:
            self._load_monster_sprite(monster_id)
    
    # 加载该区域的音乐
    area_music = {
        "tristram": "town",
        "weald": "forest",
        "cathedral": "dungeon",
        "desert": "desert",
        "snow": "snow",
        "hell": "hell",
    }
    music_id = area_music.get(new_area_id, "exploration")
    self.audio_manager.play_music(music_id)
```

---

## 10. 最佳实践

### 10.1 资源命名规范

```
# 角色精灵
{class_id}_{animation}_{direction}_{frame}.png
例如: barbarian_attack_down_0.png

# 怪物精灵
monster_{monster_id}_{animation}_{frame}.png
例如: monster_zombie_walk_0.png

# 技能图标
skill_{skill_id}.png
例如: skill_bash.png

# 物品图标
item_{item_type}_{variant}.png
例如: item_sword_0.png

# UI元素
ui_{element}_{state}.png
例如: ui_button_hover.png
```

### 10.2 性能优化建议

1. **纹理图集**: 将多个小图片合并到一个大图
2. **延迟加载**: 按需加载资源，避免一次性加载所有
3. **资源缓存**: 已加载的资源保持缓存
4. **压缩音频**: 使用OGG格式压缩音乐文件
5. **预渲染**: 预先渲染复杂效果

### 10.3 资源替换检查清单

- [ ] 确认资源尺寸符合规范
- [ ] 确认文件格式正确
- [ ] 确认文件命名符合规范
- [ ] 确认透明通道正确设置
- [ ] 测试动画帧率是否流畅
- [ ] 测试音频音量是否平衡
- [ ] 检查内存占用是否合理

---

## 附录: 推荐资源网站

### 免费资源
- [OpenGameArt.org](https://opengameart.org/) - 开源游戏素材
- [Kenney.nl](https://kenney.nl/) - 免费游戏资源
- [itch.io](https://itch.io/game-assets) - 独立游戏资源

### 付费资源
- [Unity Asset Store](https://assetstore.unity.com/) - Unity资源商店
- [Unreal Marketplace](https://www.unrealengine.com/marketplace) - UE资源市场
- [Humble Bundle](https://www.humblebundle.com/) - 游戏资源包

### 制作工具
- [Aseprite](https://www.aseprite.org/) - 像素画编辑器
- [Tiled](https://www.mapeditor.org/) - 地图编辑器
- [Audacity](https://www.audacityteam.org/) - 音频编辑器
- [Spine](http://esotericsoftware.com/) - 骨骼动画

---

**文档版本**: 1.0  
**最后更新**: 2024年  
**作者**: Diablo Mini 开发团队
