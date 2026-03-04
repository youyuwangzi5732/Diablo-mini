"""
NPC动画系统 - 商业化级别的NPC渲染和动画
"""
import pygame
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import math
import random


class NPCAnimationState(Enum):
    IDLE = "idle"
    WALKING = "walking"
    TALKING = "talking"
    WORKING = "working"
    INTERACTING = "interacting"


class NPCType(Enum):
    MERCHANT = "merchant"
    BLACKSMITH = "blacksmith"
    JEWELER = "jeweler"
    QUEST_GIVER = "quest_giver"
    HEALER = "healer"
    STASH_KEEPER = "stash"
    TELEPORTER = "teleporter"
    TRAINER = "trainer"
    GUARD = "guard"
    VILLAGER = "villager"


@dataclass
class NPCFrame:
    surface: pygame.Surface
    duration: float = 0.1


@dataclass
class NPCAnimation:
    frames: List[NPCFrame] = field(default_factory=list)
    current_frame: int = 0
    elapsed: float = 0.0
    loop: bool = True
    
    def get_current_surface(self) -> Optional[pygame.Surface]:
        if not self.frames:
            return None
        return self.frames[self.current_frame].surface
    
    def update(self, delta_time: float):
        if not self.frames:
            return
        
        self.elapsed += delta_time
        if self.elapsed >= self.frames[self.current_frame].duration:
            self.elapsed = 0.0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            if self.current_frame == 0 and not self.loop:
                self.current_frame = len(self.frames) - 1


@dataclass
class NPCSprite:
    npc_type: NPCType
    animations: Dict[NPCAnimationState, NPCAnimation] = field(default_factory=dict)
    current_state: NPCAnimationState = NPCAnimationState.IDLE
    
    # NPC外观配置
    body_color: Tuple[int, int, int] = (200, 200, 200)
    clothing_color: Tuple[int, int, int] = (100, 100, 150)
    hair_color: Tuple[int, int, int] = (80, 60, 40)
    skin_color: Tuple[int, int, int] = (220, 180, 150)
    
    # 位置和移动
    position: Tuple[float, float] = (0.0, 0.0)
    target_position: Optional[Tuple[float, float]] = None
    facing_right: bool = True
    
    # 交互状态
    is_hovered: bool = False
    is_selected: bool = False
    interaction_radius: float = 2.0
    
    # 名字和对话
    name: str = ""
    greeting: str = ""


class NPCAnimator:
    """NPC动画管理器"""
    
    NPC_CONFIGS = {
        NPCType.MERCHANT: {
            "body_color": (100, 150, 100),
            "clothing_color": (80, 120, 80),
            "hair_color": (60, 40, 20),
            "skin_color": (220, 180, 150),
            "name": "商人",
            "greeting": "欢迎光临！有什么需要的吗？"
        },
        NPCType.BLACKSMITH: {
            "body_color": (150, 150, 160),
            "clothing_color": (100, 80, 60),
            "hair_color": (40, 30, 20),
            "skin_color": (200, 160, 130),
            "name": "铁匠",
            "greeting": "需要修理装备吗？"
        },
        NPCType.JEWELER: {
            "body_color": (150, 100, 180),
            "clothing_color": (120, 80, 150),
            "hair_color": (80, 60, 100),
            "skin_color": (230, 200, 180),
            "name": "珠宝匠",
            "greeting": "来看看这些宝石吧！"
        },
        NPCType.QUEST_GIVER: {
            "body_color": (200, 180, 100),
            "clothing_color": (180, 160, 80),
            "hair_color": (100, 80, 40),
            "skin_color": (220, 190, 160),
            "name": "任务发布者",
            "greeting": "冒险者，我有任务要交给你。"
        },
        NPCType.HEALER: {
            "body_color": (200, 200, 255),
            "clothing_color": (180, 180, 240),
            "hair_color": (120, 100, 80),
            "skin_color": (230, 210, 200),
            "name": "治疗师",
            "greeting": "需要治疗吗？"
        },
        NPCType.STASH_KEEPER: {
            "body_color": (150, 130, 100),
            "clothing_color": (130, 110, 80),
            "hair_color": (90, 70, 50),
            "skin_color": (210, 180, 150),
            "name": "仓库管理员",
            "greeting": "要存取物品吗？"
        },
        NPCType.TELEPORTER: {
            "body_color": (100, 100, 200),
            "clothing_color": (80, 80, 180),
            "hair_color": (150, 150, 255),
            "skin_color": (220, 200, 230),
            "name": "传送使者",
            "greeting": "想去哪里？"
        },
        NPCType.TRAINER: {
            "body_color": (180, 150, 100),
            "clothing_color": (160, 130, 80),
            "hair_color": (60, 40, 20),
            "skin_color": (200, 160, 130),
            "name": "训练师",
            "greeting": "想要提升技能吗？"
        },
        NPCType.GUARD: {
            "body_color": (100, 100, 120),
            "clothing_color": (80, 80, 100),
            "hair_color": (50, 40, 30),
            "skin_color": (210, 180, 150),
            "name": "守卫",
            "greeting": "保持警惕！"
        },
        NPCType.VILLAGER: {
            "body_color": (150, 130, 110),
            "clothing_color": (130, 110, 90),
            "hair_color": (80, 60, 40),
            "skin_color": (220, 185, 155),
            "name": "村民",
            "greeting": "你好！"
        }
    }
    
    def __init__(self):
        self._sprite_cache: Dict[NPCType, Dict[NPCAnimationState, List[pygame.Surface]]] = {}
        self._animation_time = 0.0
        self._generate_all_sprites()
    
    def _generate_all_sprites(self):
        """生成所有NPC精灵"""
        for npc_type in NPCType:
            self._sprite_cache[npc_type] = {}
            config = self.NPC_CONFIGS.get(npc_type, {})
            
            for state in NPCAnimationState:
                frames = self._generate_animation_frames(npc_type, state, config)
                self._sprite_cache[npc_type][state] = frames
    
    def _generate_animation_frames(self, npc_type: NPCType, state: NPCAnimationState,
                                    config: Dict) -> List[pygame.Surface]:
        """生成动画帧"""
        frames = []
        frame_count = self._get_frame_count(state)
        
        for i in range(frame_count):
            frame = self._draw_npc_frame(npc_type, state, i, frame_count, config)
            frames.append(frame)
        
        return frames
    
    def _get_frame_count(self, state: NPCAnimationState) -> int:
        """获取动画帧数"""
        counts = {
            NPCAnimationState.IDLE: 4,
            NPCAnimationState.WALKING: 8,
            NPCAnimationState.TALKING: 6,
            NPCAnimationState.WORKING: 6,
            NPCAnimationState.INTERACTING: 4
        }
        return counts.get(state, 4)
    
    def _draw_npc_frame(self, npc_type: NPCType, state: NPCAnimationState,
                        frame_index: int, total_frames: int,
                        config: Dict) -> pygame.Surface:
        """绘制NPC单帧"""
        size = (48, 64)
        surface = pygame.Surface(size, pygame.SRCALPHA)
        
        body_color = config.get("body_color", (200, 200, 200))
        clothing_color = config.get("clothing_color", (100, 100, 150))
        skin_color = config.get("skin_color", (220, 180, 150))
        hair_color = config.get("hair_color", (80, 60, 40))
        
        # 计算动画偏移
        anim_offset = self._calculate_animation_offset(state, frame_index, total_frames)
        
        center_x = size[0] // 2
        base_y = size[1] - 10
        
        # 绘制阴影
        shadow_surface = pygame.Surface((30, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, 80), (0, 0, 30, 10))
        surface.blit(shadow_surface, (center_x - 15, base_y + 5))
        
        # 绘制腿
        leg_offset = anim_offset.get("leg", 0)
        pygame.draw.ellipse(surface, clothing_color, 
                           (center_x - 12, base_y - 15 + leg_offset, 8, 18))
        pygame.draw.ellipse(surface, clothing_color, 
                           (center_x + 4, base_y - 15 - leg_offset, 8, 18))
        
        # 绘制身体
        body_y = base_y - 35 + anim_offset.get("body_y", 0)
        pygame.draw.ellipse(surface, clothing_color, 
                           (center_x - 14, body_y, 28, 30))
        
        # 绘制手臂
        arm_offset = anim_offset.get("arm", 0)
        pygame.draw.ellipse(surface, skin_color, 
                           (center_x - 20, body_y + 5 + arm_offset, 8, 20))
        pygame.draw.ellipse(surface, skin_color, 
                           (center_x + 12, body_y + 5 - arm_offset, 8, 20))
        
        # 绘制头部
        head_y = body_y - 18 + anim_offset.get("head_y", 0)
        pygame.draw.circle(surface, skin_color, (center_x, head_y + 10), 12)
        
        # 绘制头发
        hair_style = self._get_hair_style(npc_type)
        self._draw_hair(surface, center_x, head_y + 10, hair_color, hair_style)
        
        # 绘制面部特征
        self._draw_face(surface, center_x, head_y + 10, state, frame_index)
        
        # 绘制NPC类型特定装饰
        self._draw_npc_accessories(surface, npc_type, center_x, body_y, frame_index)
        
        return surface
    
    def _calculate_animation_offset(self, state: NPCAnimationState,
                                     frame_index: int, total_frames: int) -> Dict[str, int]:
        """计算动画偏移"""
        progress = frame_index / total_frames
        
        offsets = {}
        
        if state == NPCAnimationState.IDLE:
            # 呼吸动画
            offsets["body_y"] = int(2 * math.sin(progress * 2 * math.pi))
            offsets["head_y"] = offsets["body_y"]
        
        elif state == NPCAnimationState.WALKING:
            # 行走动画
            offsets["leg"] = int(4 * math.sin(progress * 2 * math.pi))
            offsets["arm"] = int(3 * math.sin(progress * 2 * math.pi))
            offsets["body_y"] = int(1 * abs(math.sin(progress * 2 * math.pi)))
        
        elif state == NPCAnimationState.TALKING:
            # 说话动画
            offsets["head_y"] = int(1 * math.sin(progress * 4 * math.pi))
        
        elif state == NPCAnimationState.WORKING:
            # 工作动画
            offsets["arm"] = int(5 * math.sin(progress * 2 * math.pi))
            offsets["body_y"] = int(2 * abs(math.sin(progress * 2 * math.pi)))
        
        return offsets
    
    def _get_hair_style(self, npc_type: NPCType) -> str:
        """获取发型"""
        styles = {
            NPCType.MERCHANT: "short",
            NPCType.BLACKSMITH: "bald",
            NPCType.JEWELER: "long",
            NPCType.QUEST_GIVER: "medium",
            NPCType.HEALER: "long",
            NPCType.STASH_KEEPER: "short",
            NPCType.TELEPORTER: "mystical",
            NPCType.TRAINER: "short",
            NPCType.GUARD: "short",
            NPCType.VILLAGER: "medium"
        }
        return styles.get(npc_type, "short")
    
    def _draw_hair(self, surface: pygame.Surface, x: int, y: int,
                   color: Tuple[int, int, int], style: str):
        """绘制头发"""
        if style == "bald":
            return
        
        # 基础头发
        pygame.draw.arc(surface, color, (x - 12, y - 14, 24, 16), 0, math.pi, 4)
        
        if style == "long":
            # 长发
            pygame.draw.ellipse(surface, color, (x - 10, y - 5, 6, 15))
            pygame.draw.ellipse(surface, color, (x + 4, y - 5, 6, 15))
        
        elif style == "mystical":
            # 神秘发型（发光效果）
            glow_surface = pygame.Surface((30, 20), pygame.SRCALPHA)
            pygame.draw.ellipse(glow_surface, (*color, 150), (0, 0, 30, 20))
            surface.blit(glow_surface, (x - 15, y - 15))
    
    def _draw_face(self, surface: pygame.Surface, x: int, y: int,
                   state: NPCAnimationState, frame_index: int):
        """绘制面部"""
        # 眼睛
        eye_color = (40, 40, 40)
        eye_y = y - 2
        
        # 眨眼动画
        if state == NPCAnimationState.IDLE and frame_index == 2:
            # 眨眼
            pygame.draw.line(surface, eye_color, (x - 5, eye_y), (x - 3, eye_y), 2)
            pygame.draw.line(surface, eye_color, (x + 3, eye_y), (x + 5, eye_y), 2)
        else:
            pygame.draw.circle(surface, (255, 255, 255), (x - 4, eye_y), 3)
            pygame.draw.circle(surface, eye_color, (x - 4, eye_y), 2)
            pygame.draw.circle(surface, (255, 255, 255), (x + 4, eye_y), 3)
            pygame.draw.circle(surface, eye_color, (x + 4, eye_y), 2)
        
        # 嘴巴
        mouth_y = y + 5
        if state == NPCAnimationState.TALKING:
            # 说话动画
            mouth_open = abs(math.sin(frame_index * math.pi / 3)) * 3
            pygame.draw.ellipse(surface, (150, 100, 100), 
                              (x - 3, mouth_y - mouth_open/2, 6, mouth_open + 2))
        else:
            pygame.draw.arc(surface, (150, 100, 100), 
                          (x - 4, mouth_y - 2, 8, 6), 0.2, math.pi - 0.2, 1)
    
    def _draw_npc_accessories(self, surface: pygame.Surface, npc_type: NPCType,
                               x: int, body_y: int, frame_index: int):
        """绘制NPC配饰"""
        if npc_type == NPCType.MERCHANT:
            # 商人背包
            pygame.draw.rect(surface, (100, 80, 60), (x + 12, body_y + 5, 10, 15))
            pygame.draw.rect(surface, (80, 60, 40), (x + 12, body_y + 5, 10, 15), 1)
        
        elif npc_type == NPCType.BLACKSMITH:
            # 铁匠围裙
            pygame.draw.rect(surface, (80, 60, 40), (x - 10, body_y + 10, 20, 20))
        
        elif npc_type == NPCType.JEWELER:
            # 珠宝匠放大镜
            pygame.draw.circle(surface, (200, 200, 220), (x + 18, body_y + 10), 5)
            pygame.draw.circle(surface, (150, 150, 170), (x + 18, body_y + 10), 5, 1)
        
        elif npc_type == NPCType.HEALER:
            # 治疗师十字架
            pygame.draw.rect(surface, (255, 255, 255), (x - 2, body_y + 5, 4, 12))
            pygame.draw.rect(surface, (255, 255, 255), (x - 5, body_y + 8, 10, 4))
        
        elif npc_type == NPCType.TELEPORTER:
            # 传送使者魔法光环
            glow_alpha = int(100 + 50 * math.sin(frame_index * math.pi / 2))
            glow_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (100, 100, 255, glow_alpha), (20, 20), 15)
            surface.blit(glow_surface, (x - 20, body_y - 10))
        
        elif npc_type == NPCType.GUARD:
            # 守卫头盔
            pygame.draw.arc(surface, (100, 100, 110), (x - 14, body_y - 35, 28, 20), 0, math.pi, 3)
            pygame.draw.rect(surface, (100, 100, 110), (x - 14, body_y - 26, 28, 3))
    
    def create_npc_sprite(self, npc_type: NPCType, position: Tuple[float, float],
                          name: str = None) -> NPCSprite:
        """创建NPC精灵"""
        config = self.NPC_CONFIGS.get(npc_type, {})
        
        sprite = NPCSprite(
            npc_type=npc_type,
            body_color=config.get("body_color", (200, 200, 200)),
            clothing_color=config.get("clothing_color", (100, 100, 150)),
            hair_color=config.get("hair_color", (80, 60, 40)),
            skin_color=config.get("skin_color", (220, 180, 150)),
            position=position,
            name=name or config.get("name", "NPC"),
            greeting=config.get("greeting", "")
        )
        
        # 初始化动画
        for state in NPCAnimationState:
            frames = self._sprite_cache.get(npc_type, {}).get(state, [])
            if frames:
                animation = NPCAnimation(
                    frames=[NPCFrame(surface=f, duration=0.15) for f in frames],
                    loop=True
                )
                sprite.animations[state] = animation
        
        return sprite
    
    def render_npc(self, surface: pygame.Surface, sprite: NPCSprite,
                   camera_offset: Tuple[float, float], tile_size: int = 64):
        """渲染NPC"""
        # 计算屏幕位置
        screen_x = int(sprite.position[0] * tile_size - camera_offset[0] + tile_size // 2 - 24)
        screen_y = int(sprite.position[1] * tile_size - camera_offset[1] + tile_size // 2 - 64)
        
        # 检查是否在屏幕范围内
        if (screen_x + 48 < 0 or screen_x > surface.get_width() or
            screen_y + 64 < 0 or screen_y > surface.get_height()):
            return
        
        # 获取当前动画帧
        animation = sprite.animations.get(sprite.current_state)
        if animation:
            frame_surface = animation.get_current_surface()
            if frame_surface:
                # 翻转处理
                if not sprite.facing_right:
                    frame_surface = pygame.transform.flip(frame_surface, True, False)
                
                surface.blit(frame_surface, (screen_x, screen_y))
        
        # 绘制选中/悬停效果
        if sprite.is_hovered or sprite.is_selected:
            # 高亮边框
            highlight_surface = pygame.Surface((52, 68), pygame.SRCALPHA)
            pygame.draw.rect(highlight_surface, (255, 255, 100, 100), 
                           (0, 0, 52, 68), 2)
            surface.blit(highlight_surface, (screen_x - 2, screen_y - 2))
        
        # 绘制名称
        self._render_npc_name(surface, sprite, screen_x, screen_y)
        
        # 绘制交互提示
        if sprite.is_hovered:
            self._render_interaction_hint(surface, sprite, screen_x, screen_y)
    
    def _render_npc_name(self, surface: pygame.Surface, sprite: NPCSprite,
                          x: int, y: int):
        """渲染NPC名称"""
        from ui.font_manager import get_font
        font = get_font(12)
        
        name_text = font.render(sprite.name, True, (255, 255, 255))
        name_x = x + (48 - name_text.get_width()) // 2
        name_y = y - 18
        
        # 背景
        bg_padding = 3
        bg_rect = (name_x - bg_padding, name_y - bg_padding,
                  name_text.get_width() + bg_padding * 2,
                  name_text.get_height() + bg_padding * 2)
        
        bg_surface = pygame.Surface((bg_rect[2], bg_rect[3]), pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (30, 30, 30, 200), (0, 0, bg_rect[2], bg_rect[3]))
        surface.blit(bg_surface, (bg_rect[0], bg_rect[1]))
        
        surface.blit(name_text, (name_x, name_y))
    
    def _render_interaction_hint(self, surface: pygame.Surface, sprite: NPCSprite,
                                  x: int, y: int):
        """渲染交互提示"""
        from ui.font_manager import get_font
        font = get_font(10)
        
        hint_text = font.render("[右键交互]", True, (255, 220, 100))
        hint_x = x + (48 - hint_text.get_width()) // 2
        hint_y = y + 68
        
        surface.blit(hint_text, (hint_x, hint_y))
    
    def update(self, delta_time: float):
        """更新动画"""
        self._animation_time += delta_time
    
    def update_sprite(self, sprite: NPCSprite, delta_time: float):
        """更新NPC精灵动画"""
        animation = sprite.animations.get(sprite.current_state)
        if animation:
            animation.update(delta_time)


class TownNPCManager:
    """主城NPC管理器"""
    
    DEFAULT_NPC_POSITIONS = {
        "merchant": (16, 16),
        "blacksmith": (36, 19),
        "jeweler": (23, 33),
        "quest_giver": (13, 29),
        "healer": (9, 19),
        "stash": (39, 33),
        "teleporter": (25, 9),
        "trainer": (43, 26),
    }
    
    def __init__(self):
        self.animator = NPCAnimator()
        self.npcs: Dict[str, NPCSprite] = {}
        self._spawn_town_npcs()
    
    def _spawn_town_npcs(self):
        """生成主城NPC"""
        npc_type_map = {
            "merchant": NPCType.MERCHANT,
            "blacksmith": NPCType.BLACKSMITH,
            "jeweler": NPCType.JEWELER,
            "quest_giver": NPCType.QUEST_GIVER,
            "healer": NPCType.HEALER,
            "stash": NPCType.STASH_KEEPER,
            "teleporter": NPCType.TELEPORTER,
            "trainer": NPCType.TRAINER,
        }
        
        for npc_id, (npc_type_str, position) in zip(
            npc_type_map.keys(), 
            self.DEFAULT_NPC_POSITIONS.values()
        ):
            npc_type = npc_type_map[npc_id]
            sprite = self.animator.create_npc_sprite(npc_type, position)
            self.npcs[npc_id] = sprite
    
    def update(self, delta_time: float):
        """更新所有NPC"""
        self.animator.update(delta_time)
        for npc in self.npcs.values():
            self.animator.update_sprite(npc, delta_time)
            
            # 随机改变状态
            if random.random() < 0.001:
                if npc.current_state == NPCAnimationState.IDLE:
                    npc.current_state = NPCAnimationState.WORKING
                else:
                    npc.current_state = NPCAnimationState.IDLE
    
    def render(self, surface: pygame.Surface, camera_offset: Tuple[float, float],
               tile_size: int = 64):
        """渲染所有NPC"""
        for npc in self.npcs.values():
            self.animator.render_npc(surface, npc, camera_offset, tile_size)
    
    def get_npc_at_position(self, world_pos: Tuple[float, float],
                             range_limit: float = 1.5) -> Optional[NPCSprite]:
        """获取指定位置的NPC"""
        for npc in self.npcs.values():
            dx = world_pos[0] - npc.position[0]
            dy = world_pos[1] - npc.position[1]
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance <= range_limit:
                return npc
        
        return None
    
    def set_hovered_npc(self, world_pos: Tuple[float, float]):
        """设置悬停的NPC"""
        for npc in self.npcs.values():
            dx = world_pos[0] - npc.position[0]
            dy = world_pos[1] - npc.position[1]
            distance = math.sqrt(dx * dx + dy * dy)
            
            npc.is_hovered = distance <= 1.0
