"""
开场动画系统
"""
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import pygame

from ui.font_manager import get_font
import math


class AnimationType(Enum):
    FADE_IN = "fade_in"
    FADE_OUT = "fade_out"
    SLIDE_IN = "slide_in"
    SLIDE_OUT = "slide_out"
    SCALE = "scale"
    ROTATE = "rotate"
    TYPEWRITER = "typewriter"
    PARTICLE = "particle"


@dataclass
class AnimationKeyframe:
    time: float
    value: Any
    easing: str = "linear"


@dataclass
class Animation:
    target: Any
    property_name: str
    keyframes: List[AnimationKeyframe]
    duration: float
    loop: bool = False
    ping_pong: bool = False
    
    current_time: float = 0.0
    is_playing: bool = False
    is_complete: bool = False
    direction: int = 1
    
    def start(self):
        self.current_time = 0.0
        self.is_playing = True
        self.is_complete = False
    
    def stop(self):
        self.is_playing = False
    
    def update(self, delta_time: float):
        if not self.is_playing:
            return
        
        self.current_time += delta_time * self.direction
        
        if self.current_time >= self.duration:
            if self.loop:
                if self.ping_pong:
                    self.direction *= -1
                    self.current_time = self.duration
                else:
                    self.current_time = 0.0
            else:
                self.current_time = self.duration
                self.is_complete = True
                self.is_playing = False
        
        elif self.current_time < 0:
            if self.ping_pong and self.loop:
                self.direction *= -1
                self.current_time = 0.0
            else:
                self.current_time = 0.0
        
        self._apply_animation()
    
    def _apply_animation(self):
        if len(self.keyframes) < 2:
            return
        
        progress = self.current_time / self.duration
        
        for i in range(len(self.keyframes) - 1):
            k1 = self.keyframes[i]
            k2 = self.keyframes[i + 1]
            
            if k1.time <= progress <= k2.time:
                local_progress = (progress - k1.time) / (k2.time - k1.time)
                local_progress = self._apply_easing(local_progress, k1.easing)
                
                value = self._interpolate(k1.value, k2.value, local_progress)
                self._set_property(value)
                return
    
    def _apply_easing(self, t: float, easing: str) -> float:
        if easing == "linear":
            return t
        elif easing == "ease_in":
            return t * t
        elif easing == "ease_out":
            return t * (2 - t)
        elif easing == "ease_in_out":
            return t * t * (3 - 2 * t)
        elif easing == "bounce":
            if t < 0.5:
                return 4 * t * t * t
            else:
                return 1 - (-2 * t + 2) ** 3 / 2
        return t
    
    def _interpolate(self, v1: Any, v2: Any, t: float) -> Any:
        if isinstance(v1, (int, float)):
            return v1 + (v2 - v1) * t
        elif isinstance(v1, tuple) and len(v1) == 2:
            return (v1[0] + (v2[0] - v1[0]) * t,
                    v1[1] + (v2[1] - v1[1]) * t)
        elif isinstance(v1, tuple) and len(v1) == 4:
            return (int(v1[0] + (v2[0] - v1[0]) * t),
                    int(v1[1] + (v2[1] - v1[1]) * t),
                    int(v1[2] + (v2[2] - v1[2]) * t),
                    int(v1[3] + (v2[3] - v1[3]) * t))
        return v1
    
    def _set_property(self, value: Any):
        if self.target and hasattr(self.target, self.property_name):
            setattr(self.target, self.property_name, value)


@dataclass
class CutsceneFrame:
    background: Optional[str] = None
    text: str = ""
    text_position: Tuple[int, int] = (50, 80)
    speaker: str = ""
    speaker_position: Tuple[int, int] = (50, 70)
    duration: float = 3.0
    
    animations: List[Dict[str, Any]] = field(default_factory=list)
    sound: Optional[str] = None
    music: Optional[str] = None
    
    choices: List[Dict[str, Any]] = field(default_factory=list)


class Cutscene:
    def __init__(self, cutscene_id: str, name: str):
        self.id = cutscene_id
        self.name = name
        
        self.frames: List[CutsceneFrame] = []
        self.current_frame_index = 0
        
        self.is_playing = False
        self.is_complete = False
        
        self.frame_time = 0.0
        self.text_progress = 0.0
        self.text_speed = 50.0
        
        self.animations: List[Animation] = []
        
        self.on_complete: Optional[Callable] = None
    
    def add_frame(self, frame: CutsceneFrame):
        self.frames.append(frame)
    
    def start(self):
        self.current_frame_index = 0
        self.is_playing = True
        self.is_complete = False
        self.frame_time = 0.0
        self.text_progress = 0.0
        
        if self.frames:
            self._setup_frame(self.frames[0])
    
    def stop(self):
        self.is_playing = False
        self.animations.clear()
    
    def skip(self):
        if self.current_frame_index < len(self.frames) - 1:
            self.current_frame_index += 1
            self.frame_time = 0.0
            self.text_progress = 0.0
            
            if self.current_frame_index < len(self.frames):
                self._setup_frame(self.frames[self.current_frame_index])
        else:
            self.complete()
    
    def complete(self):
        self.is_playing = False
        self.is_complete = True
        
        if self.on_complete:
            self.on_complete()
    
    def _setup_frame(self, frame: CutsceneFrame):
        self.animations.clear()
        
        for anim_data in frame.animations:
            pass
    
    def update(self, delta_time: float):
        if not self.is_playing or self.current_frame_index >= len(self.frames):
            return
        
        current_frame = self.frames[self.current_frame_index]
        
        self.frame_time += delta_time
        
        if current_frame.text:
            self.text_progress += self.text_speed * delta_time
        
        for animation in self.animations:
            animation.update(delta_time)
        
        if self.frame_time >= current_frame.duration:
            self.skip()
    
    def render(self, surface: pygame.Surface):
        if not self.is_playing or self.current_frame_index >= len(self.frames):
            return
        
        current_frame = self.frames[self.current_frame_index]
        
        self._render_background(surface, current_frame)
        self._render_text(surface, current_frame)
        self._render_speaker(surface, current_frame)
    
    def _render_background(self, surface: pygame.Surface, frame: CutsceneFrame):
        if frame.background:
            pass
        else:
            surface.fill((0, 0, 0))
    
    def _render_text(self, surface: pygame.Surface, frame: CutsceneFrame):
        if not frame.text:
            return
        
        font = get_font(24)
        
        visible_text = frame.text[:int(self.text_progress)]
        
        lines = self._wrap_text(visible_text, font, surface.get_width() - 100)
        
        y = frame.text_position[1]
        for line in lines:
            text_surface = font.render(line, True, (255, 255, 255))
            surface.blit(text_surface, (frame.text_position[0], y))
            y += font.get_linesize()
    
    def _render_speaker(self, surface: pygame.Surface, frame: CutsceneFrame):
        if not frame.speaker:
            return
        
        font = get_font(20)
        
        speaker_surface = font.render(frame.speaker, True, (255, 200, 100))
        surface.blit(speaker_surface, frame.speaker_position)
    
    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> List[str]:
        if ' ' not in text:
            lines = []
            current_line = ""
            for char in text:
                test_line = current_line + char
                if font.size(test_line)[0] <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = char
            if current_line:
                lines.append(current_line)
            return lines

        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines
    
    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            self.skip()


class IntroCutscene(Cutscene):
    def __init__(self):
        super().__init__("intro", "开场动画")
        
        self._create_intro_frames()
    
    def _create_intro_frames(self):
        self.frames = [
            CutsceneFrame(
                text="在庇护所的世界中，黑暗从未真正消失...",
                speaker="旁白",
                duration=4.0
            ),
            CutsceneFrame(
                text="天堂与地狱的永恒战争，将这片土地撕裂。",
                speaker="旁白",
                duration=4.0
            ),
            CutsceneFrame(
                text="英雄们从世界各地聚集而来，",
                speaker="旁白",
                duration=3.0
            ),
            CutsceneFrame(
                text="为了对抗即将降临的黑暗...",
                speaker="旁白",
                duration=3.0
            ),
            CutsceneFrame(
                text="而你，就是被选中的那一位。",
                speaker="旁白",
                duration=3.0
            ),
            CutsceneFrame(
                text="欢迎来到庇护所，英雄。",
                speaker="神秘声音",
                duration=3.0
            ),
        ]


class StoryCutscene(Cutscene):
    def __init__(self, cutscene_id: str, name: str, script: List[Tuple[str, str, float]]):
        super().__init__(cutscene_id, name)
        self.frames = [
            CutsceneFrame(
                text=text,
                speaker=speaker,
                duration=duration
            )
            for speaker, text, duration in script
        ]


class AnimationManager:
    def __init__(self):
        self.animations: List[Animation] = []
        self.cutscenes: Dict[str, Cutscene] = {}
        self.current_cutscene: Optional[Cutscene] = None
        
        self._create_default_cutscenes()
    
    def _create_default_cutscenes(self):
        self.cutscenes["intro"] = IntroCutscene()
        self.cutscenes["chapter_cathedral"] = StoryCutscene(
            "chapter_cathedral",
            "第一章：大教堂",
            [
                ("镇长", "你做到了。钟声停歇，但黑暗还在地下蠕动。", 3.5),
                ("治疗师", "亡魂从未离开，他们在等待新的主人。", 3.5),
                ("旁白", "石阶向下，潮湿与铁锈气息混在一起。", 3.5),
                ("旁白", "第一章终章开启：王座阴影。", 3.0),
            ],
        )
        self.cutscenes["chapter_desert"] = StoryCutscene(
            "chapter_desert",
            "第二章：沙海",
            [
                ("卡尔蒂姆商人", "风把尸骨埋进沙丘，也把恶魔埋进去。", 3.5),
                ("旁白", "你越过热浪，看见远处营火连成了猩红弧线。", 3.5),
                ("镇长来信", "北方暂稳，南线就交给你了。", 3.2),
                ("旁白", "第二章作战目标：沙暴深处。", 2.8),
            ],
        )
        self.cutscenes["chapter_snow"] = StoryCutscene(
            "chapter_snow",
            "第三章：寒脊",
            [
                ("训练师", "在这里，迟疑比寒风更致命。", 3.2),
                ("旁白", "雪脊下的裂缝喷出黑焰，像一张正在醒来的口。", 3.8),
                ("训练师", "点亮烽火台，别让它们越过山口。", 3.2),
            ],
        )
        self.cutscenes["chapter_hell"] = StoryCutscene(
            "chapter_hell",
            "终章：黎明之誓",
            [
                ("旁白", "地狱之门开启，脚下每一步都踩在旧日战歌上。", 3.8),
                ("神秘声音", "这是最后一夜，也是第一缕晨光之前的试炼。", 3.8),
                ("镇长", "无论结果如何，崔斯特姆会记住你的名字。", 3.5),
            ],
        )
    
    def create_animation(self, target: Any, property_name: str,
                         keyframes: List[AnimationKeyframe],
                         duration: float, loop: bool = False) -> Animation:
        animation = Animation(
            target=target,
            property_name=property_name,
            keyframes=keyframes,
            duration=duration,
            loop=loop
        )
        self.animations.append(animation)
        return animation
    
    def play_cutscene(self, cutscene_id: str, on_complete: Callable = None):
        cutscene = self.cutscenes.get(cutscene_id)
        if cutscene:
            self.current_cutscene = cutscene
            cutscene.on_complete = on_complete
            cutscene.start()
    
    def stop_cutscene(self):
        if self.current_cutscene:
            self.current_cutscene.stop()
            self.current_cutscene = None
    
    def update(self, delta_time: float):
        for animation in self.animations[:]:
            animation.update(delta_time)
            if animation.is_complete and not animation.loop:
                self.animations.remove(animation)
        
        if self.current_cutscene:
            self.current_cutscene.update(delta_time)
            
            if self.current_cutscene.is_complete:
                self.current_cutscene = None
    
    def render(self, surface: pygame.Surface):
        if self.current_cutscene:
            self.current_cutscene.render(surface)
    
    def handle_event(self, event: pygame.event.Event):
        if self.current_cutscene:
            self.current_cutscene.handle_event(event)
    
    def is_cutscene_playing(self) -> bool:
        return self.current_cutscene is not None and self.current_cutscene.is_playing
