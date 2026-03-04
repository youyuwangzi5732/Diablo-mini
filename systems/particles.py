"""
粒子效果系统
"""
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import random
import math


class ParticleBlendMode(Enum):
    NORMAL = "normal"
    ADDITIVE = "additive"
    MULTIPLY = "multiply"


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    
    color: Tuple[int, int, int, int] = (255, 255, 255, 255)
    size: float = 3.0
    size_decay: float = 0.0
    
    lifetime: float = 1.0
    age: float = 0.0
    
    gravity: float = 0.0
    friction: float = 1.0
    
    rotation: float = 0.0
    rotation_speed: float = 0.0
    
    blend_mode: ParticleBlendMode = ParticleBlendMode.NORMAL
    
    def update(self, delta_time: float) -> bool:
        self.age += delta_time
        
        if self.age >= self.lifetime:
            return False
        
        self.vy += self.gravity * delta_time
        self.vx *= self.friction
        self.vy *= self.friction
        
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time
        
        self.rotation += self.rotation_speed * delta_time
        
        self.size = max(0, self.size - self.size_decay * delta_time)
        
        return True
    
    def get_alpha(self) -> int:
        if self.lifetime <= 0:
            return self.color[3]
        
        life_ratio = 1 - (self.age / self.lifetime)
        return int(self.color[3] * life_ratio)
    
    def is_alive(self) -> bool:
        return self.age < self.lifetime and self.size > 0


@dataclass
class ParticleEmitterConfig:
    emission_rate: float = 10.0
    max_particles: int = 100
    
    position: Tuple[float, float] = (0, 0)
    position_variance: Tuple[float, float] = (0, 0)
    
    velocity: Tuple[float, float] = (0, 0)
    velocity_variance: Tuple[float, float] = (50, 50)
    
    color: Tuple[int, int, int, int] = (255, 255, 255, 255)
    color_variance: Tuple[int, int, int, int] = (0, 0, 0, 0)
    
    size: float = 3.0
    size_variance: float = 1.0
    size_decay: float = 0.0
    
    lifetime: float = 1.0
    lifetime_variance: float = 0.2
    
    gravity: float = 0.0
    friction: float = 1.0
    
    rotation: float = 0.0
    rotation_variance: float = 0.0
    rotation_speed: float = 0.0
    
    blend_mode: ParticleBlendMode = ParticleBlendMode.NORMAL
    
    angle: float = 0.0
    angle_variance: float = 360.0
    speed: float = 50.0
    speed_variance: float = 20.0
    
    radial_acceleration: float = 0.0
    tangential_acceleration: float = 0.0


class ParticleEmitter:
    _surface_cache: Dict[Tuple[int, int, int, int], Any] = {}
    _cache_max_size: int = 100
    
    def __init__(self, config: ParticleEmitterConfig = None):
        self.config = config or ParticleEmitterConfig()
        self.particles: List[Particle] = []
        self.emission_accumulator = 0.0
        self.active = True
        self.position = list(self.config.position)
    
    @classmethod
    def _get_cached_surface(cls, size: int, color: Tuple[int, int, int], alpha: int) -> Any:
        import pygame
        
        key = (size, color[0], color[1], color[2], alpha)
        
        if key not in cls._surface_cache:
            if len(cls._surface_cache) >= cls._cache_max_size:
                cls._surface_cache.popitem()
            
            surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, (*color, alpha), (size, size), size)
            cls._surface_cache[key] = surface
        
        return cls._surface_cache[key]
    
    def set_position(self, x: float, y: float):
        self.position = [x, y]
    
    def emit(self, count: int = 1):
        for _ in range(count):
            if len(self.particles) >= self.config.max_particles:
                break
            
            particle = self._create_particle()
            self.particles.append(particle)
    
    def _create_particle(self) -> Particle:
        config = self.config
        
        x = self.position[0] + random.uniform(-config.position_variance[0], config.position_variance[0])
        y = self.position[1] + random.uniform(-config.position_variance[1], config.position_variance[1])
        
        angle = math.radians(config.angle + random.uniform(-config.angle_variance, config.angle_variance))
        speed = config.speed + random.uniform(-config.speed_variance, config.speed_variance)
        
        vx = math.cos(angle) * speed + config.velocity[0]
        vy = math.sin(angle) * speed + config.velocity[1]
        vx += random.uniform(-config.velocity_variance[0], config.velocity_variance[0])
        vy += random.uniform(-config.velocity_variance[1], config.velocity_variance[1])
        
        color = (
            max(0, min(255, config.color[0] + random.randint(-config.color_variance[0], config.color_variance[0]))),
            max(0, min(255, config.color[1] + random.randint(-config.color_variance[1], config.color_variance[1]))),
            max(0, min(255, config.color[2] + random.randint(-config.color_variance[2], config.color_variance[2]))),
            max(0, min(255, config.color[3] + random.randint(-config.color_variance[3], config.color_variance[3])))
        )
        
        size = config.size + random.uniform(-config.size_variance, config.size_variance)
        lifetime = config.lifetime + random.uniform(-config.lifetime_variance, config.lifetime_variance)
        rotation = config.rotation + random.uniform(-config.rotation_variance, config.rotation_variance)
        
        return Particle(
            x=x, y=y, vx=vx, vy=vy,
            color=color, size=size, size_decay=config.size_decay,
            lifetime=max(0.1, lifetime), gravity=config.gravity,
            friction=config.friction, rotation=rotation,
            rotation_speed=config.rotation_speed, blend_mode=config.blend_mode
        )
    
    def update(self, delta_time: float):
        if self.active:
            self.emission_accumulator += delta_time * self.config.emission_rate
            
            while self.emission_accumulator >= 1.0:
                self.emit(1)
                self.emission_accumulator -= 1.0
        
        self.particles = [p for p in self.particles if p.update(delta_time)]
    
    def render(self, surface: Any, camera_offset: Tuple[float, float] = (0, 0)):
        import pygame
        
        for particle in self.particles:
            if particle.size <= 0:
                continue
            
            x = int(particle.x - camera_offset[0])
            y = int(particle.y - camera_offset[1])
            
            if x < -50 or x > surface.get_width() + 50:
                continue
            if y < -50 or y > surface.get_height() + 50:
                continue
            
            alpha = particle.get_alpha()
            if alpha <= 0:
                continue
            
            color = (particle.color[0], particle.color[1], particle.color[2])
            size = max(1, int(particle.size))
            
            if particle.blend_mode == ParticleBlendMode.ADDITIVE:
                cached = self._get_cached_surface(size, color, alpha)
                surface.blit(cached, (x - size, y - size), special_flags=pygame.BLEND_ADD)
            else:
                pygame.draw.circle(surface, (*color, alpha), (x, y), size)
    
    def stop(self):
        self.active = False
    
    def start(self):
        self.active = True
    
    def clear(self):
        self.particles.clear()
    
    def is_empty(self) -> bool:
        return len(self.particles) == 0


class ParticleSystem:
    def __init__(self):
        self.emitters: Dict[str, ParticleEmitter] = {}
        self._next_id = 0
    
    def create_emitter(self, config: ParticleEmitterConfig = None) -> str:
        emitter_id = f"emitter_{self._next_id}"
        self._next_id += 1
        
        self.emitters[emitter_id] = ParticleEmitter(config)
        return emitter_id
    
    def get_emitter(self, emitter_id: str) -> Optional[ParticleEmitter]:
        return self.emitters.get(emitter_id)
    
    def remove_emitter(self, emitter_id: str):
        if emitter_id in self.emitters:
            del self.emitters[emitter_id]
    
    def update(self, delta_time: float):
        to_remove = []
        
        for emitter_id, emitter in self.emitters.items():
            emitter.update(delta_time)
            
            if not emitter.active and emitter.is_empty():
                to_remove.append(emitter_id)
        
        for emitter_id in to_remove:
            del self.emitters[emitter_id]
    
    def render(self, surface: Any, camera_offset: Tuple[float, float] = (0, 0)):
        for emitter in self.emitters.values():
            emitter.render(surface, camera_offset)
    
    def clear(self):
        self.emitters.clear()
    
    @staticmethod
    def create_fire_effect(x: float, y: float) -> ParticleEmitterConfig:
        return ParticleEmitterConfig(
            emission_rate=30,
            max_particles=50,
            position=(x, y),
            position_variance=(5, 2),
            angle=-90,
            angle_variance=15,
            speed=40,
            speed_variance=20,
            color=(255, 150, 50, 255),
            color_variance=(50, 50, 0, 0),
            size=5,
            size_variance=2,
            size_decay=3,
            lifetime=0.8,
            lifetime_variance=0.2,
            gravity=-20
        )
    
    @staticmethod
    def create_ice_effect(x: float, y: float) -> ParticleEmitterConfig:
        return ParticleEmitterConfig(
            emission_rate=20,
            max_particles=40,
            position=(x, y),
            position_variance=(10, 10),
            angle=0,
            angle_variance=360,
            speed=30,
            speed_variance=15,
            color=(150, 200, 255, 255),
            color_variance=(50, 50, 50, 0),
            size=4,
            size_variance=2,
            size_decay=2,
            lifetime=1.0,
            lifetime_variance=0.3,
            blend_mode=ParticleBlendMode.ADDITIVE
        )
    
    @staticmethod
    def create_lightning_effect(x: float, y: float) -> ParticleEmitterConfig:
        return ParticleEmitterConfig(
            emission_rate=50,
            max_particles=30,
            position=(x, y),
            position_variance=(3, 3),
            angle=0,
            angle_variance=360,
            speed=100,
            speed_variance=50,
            color=(200, 200, 255, 255),
            color_variance=(55, 55, 0, 0),
            size=3,
            size_variance=1,
            size_decay=5,
            lifetime=0.2,
            lifetime_variance=0.1,
            blend_mode=ParticleBlendMode.ADDITIVE
        )
    
    @staticmethod
    def create_blood_effect(x: float, y: float) -> ParticleEmitterConfig:
        return ParticleEmitterConfig(
            emission_rate=40,
            max_particles=60,
            position=(x, y),
            position_variance=(3, 3),
            angle=0,
            angle_variance=180,
            speed=60,
            speed_variance=30,
            color=(200, 50, 50, 255),
            color_variance=(55, 20, 20, 0),
            size=4,
            size_variance=2,
            size_decay=1,
            lifetime=0.6,
            lifetime_variance=0.2,
            gravity=200
        )
    
    @staticmethod
    def create_level_up_effect(x: float, y: float) -> ParticleEmitterConfig:
        return ParticleEmitterConfig(
            emission_rate=100,
            max_particles=100,
            position=(x, y),
            position_variance=(10, 10),
            angle=-90,
            angle_variance=30,
            speed=80,
            speed_variance=40,
            color=(255, 220, 100, 255),
            color_variance=(0, 30, 50, 0),
            size=5,
            size_variance=2,
            size_decay=2,
            lifetime=1.5,
            lifetime_variance=0.5,
            gravity=-30,
            blend_mode=ParticleBlendMode.ADDITIVE
        )
    
    @staticmethod
    def create_explosion_effect(x: float, y: float) -> ParticleEmitterConfig:
        return ParticleEmitterConfig(
            emission_rate=200,
            max_particles=150,
            position=(x, y),
            position_variance=(5, 5),
            angle=0,
            angle_variance=360,
            speed=150,
            speed_variance=50,
            color=(255, 200, 100, 255),
            color_variance=(0, 55, 100, 0),
            size=6,
            size_variance=3,
            size_decay=4,
            lifetime=0.5,
            lifetime_variance=0.2,
            gravity=50,
            blend_mode=ParticleBlendMode.ADDITIVE
        )
    
    @staticmethod
    def create_magic_trail(x: float, y: float, color: Tuple[int, int, int] = (150, 100, 255)) -> ParticleEmitterConfig:
        return ParticleEmitterConfig(
            emission_rate=20,
            max_particles=30,
            position=(x, y),
            position_variance=(2, 2),
            angle=0,
            angle_variance=360,
            speed=10,
            speed_variance=5,
            color=(*color, 200),
            color_variance=(30, 30, 30, 50),
            size=4,
            size_variance=1,
            size_decay=3,
            lifetime=0.5,
            lifetime_variance=0.2,
            blend_mode=ParticleBlendMode.ADDITIVE
        )

