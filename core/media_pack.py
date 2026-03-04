import json
import math
import os
import random
import wave
import struct
from typing import Dict, Tuple, List

import pygame


MEDIA_PACK_VERSION = "media_pack_v2026_03_04"


def ensure_media_pack(base_path: str) -> Dict[str, str]:
    assets_root = os.path.join(base_path, "assets")
    manifest_path = os.path.join(assets_root, "manifest.json")
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            if manifest.get("version") == MEDIA_PACK_VERSION:
                return manifest
        except Exception:
            pass
    _generate_media_pack(assets_root)
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _generate_media_pack(assets_root: str):
    if not pygame.get_init():
        pygame.init()
    visual_root = os.path.join(assets_root, "textures")
    audio_root = os.path.join(assets_root, "sounds")
    for path in [
        visual_root,
        os.path.join(visual_root, "tiles"),
        os.path.join(visual_root, "entities"),
        os.path.join(visual_root, "objects"),
        os.path.join(visual_root, "loot"),
        os.path.join(visual_root, "icons"),
        audio_root,
        os.path.join(audio_root, "player"),
        os.path.join(audio_root, "monster"),
        os.path.join(audio_root, "skills"),
        os.path.join(audio_root, "ui"),
        os.path.join(audio_root, "music"),
    ]:
        os.makedirs(path, exist_ok=True)

    _generate_tile_textures(os.path.join(visual_root, "tiles"))
    _generate_entity_textures(os.path.join(visual_root, "entities"))
    _generate_object_textures(os.path.join(visual_root, "objects"))
    _generate_loot_textures(os.path.join(visual_root, "loot"))
    _generate_icon_textures(os.path.join(visual_root, "icons"))

    _generate_sfx(os.path.join(audio_root, "player"), "player")
    _generate_sfx(os.path.join(audio_root, "monster"), "monster")
    _generate_sfx(os.path.join(audio_root, "skills"), "skills")
    _generate_sfx(os.path.join(audio_root, "ui"), "ui")
    _generate_music(os.path.join(audio_root, "music"))

    manifest = {
        "version": MEDIA_PACK_VERSION,
        "visual_root": "assets/textures",
        "audio_root": "assets/sounds",
        "texture_naming": "domain/type_name_size.ext",
        "audio_naming": "category/event_name.ext",
        "packs": ["tiles", "entities", "objects", "loot", "icons", "player", "monster", "skills", "ui", "music"],
    }
    with open(os.path.join(assets_root, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


def _new_surface(size: int = 64) -> pygame.Surface:
    return pygame.Surface((size, size), pygame.SRCALPHA)


def _noise_points(rng: random.Random, count: int, size: int) -> List[Tuple[int, int, int]]:
    pts = []
    for _ in range(count):
        x = rng.randint(0, size - 1)
        y = rng.randint(0, size - 1)
        a = rng.randint(12, 46)
        pts.append((x, y, a))
    return pts


def _generate_tile_textures(path: str):
    palette = {
        "town_64": ((84, 78, 72), (64, 58, 54)),
        "forest_64": ((50, 86, 56), (36, 66, 42)),
        "dungeon_64": ((52, 54, 66), (40, 42, 54)),
        "desert_64": ((148, 126, 88), (126, 106, 74)),
        "snow_64": ((172, 182, 198), (140, 152, 170)),
        "hell_64": ((118, 64, 58), (96, 48, 44)),
    }
    for name, (c1, c2) in palette.items():
        surface = _new_surface(64)
        for y in range(64):
            t = y / 63.0
            row = (
                int(c1[0] * (1 - t) + c2[0] * t),
                int(c1[1] * (1 - t) + c2[1] * t),
                int(c1[2] * (1 - t) + c2[2] * t),
                255,
            )
            pygame.draw.line(surface, row, (0, y), (63, y))
        rng = random.Random(name)
        for x, y, a in _noise_points(rng, 200, 64):
            surface.set_at((x, y), (255, 255, 255, a))
        for i in range(0, 64, 16):
            pygame.draw.line(surface, (255, 255, 255, 18), (i, 0), (i, 63), 1)
            pygame.draw.line(surface, (0, 0, 0, 22), (0, i), (63, i), 1)
        pygame.image.save(surface, os.path.join(path, f"{name}.png"))


def _generate_entity_textures(path: str):
    entries = [
        ("player_default_64", (120, 170, 220), (80, 130, 180)),
        ("monster_normal_64", (190, 72, 72), (140, 44, 44)),
        ("monster_champion_64", (220, 170, 70), (164, 118, 36)),
        ("monster_rare_64", (192, 102, 202), (132, 64, 142)),
        ("monster_unique_64", (166, 108, 224), (112, 74, 164)),
        ("monster_boss_64", (244, 96, 54), (168, 46, 28)),
    ]
    for name, c1, c2 in entries:
        s = _new_surface(64)
        pygame.draw.circle(s, c2, (32, 37), 21)
        pygame.draw.circle(s, c1, (32, 32), 21)
        pygame.draw.circle(s, (255, 255, 255, 66), (24, 24), 8)
        pygame.draw.circle(s, (255, 240, 220, 240), (24, 30), 3)
        pygame.draw.circle(s, (255, 240, 220, 240), (40, 30), 3)
        pygame.image.save(s, os.path.join(path, f"{name}.png"))


def _generate_object_textures(path: str):
    entries = {
        "obj_chest_64": ((139, 90, 43), (92, 64, 34)),
        "obj_breakable_64": ((110, 90, 76), (84, 64, 56)),
        "obj_door_64": ((113, 76, 48), (70, 46, 30)),
        "obj_shrine_64": ((196, 176, 126), (128, 120, 88)),
        "obj_waypoint_64": ((110, 170, 252), (72, 126, 202)),
        "obj_portal_64": ((168, 120, 255), (118, 84, 212)),
    }
    for name, (c1, c2) in entries.items():
        s = _new_surface(64)
        pygame.draw.rect(s, c2, (12, 12, 40, 40), border_radius=8)
        pygame.draw.rect(s, c1, (10, 10, 40, 40), border_radius=8)
        pygame.draw.rect(s, (255, 255, 255, 50), (16, 16, 14, 8), border_radius=4)
        pygame.image.save(s, os.path.join(path, f"{name}.png"))


def _generate_loot_textures(path: str):
    entries = {
        "loot_gold_32": (255, 215, 70),
        "loot_common_32": (200, 200, 200),
        "loot_magic_32": (110, 160, 255),
        "loot_rare_32": (255, 210, 80),
        "loot_legendary_32": (255, 150, 70),
        "loot_set_32": (70, 255, 120),
    }
    for name, color in entries.items():
        s = _new_surface(32)
        pygame.draw.circle(s, (0, 0, 0, 70), (16, 20), 10)
        pygame.draw.circle(s, color, (16, 14), 10)
        pygame.draw.circle(s, (255, 255, 255, 70), (12, 10), 4)
        pygame.image.save(s, os.path.join(path, f"{name}.png"))


def _generate_icon_textures(path: str):
    entries = {
        "icon_swing_48": (200, 200, 200),
        "icon_fireball_48": (250, 128, 76),
        "icon_lightning_48": (252, 244, 130),
        "icon_ice_48": (152, 220, 255),
        "icon_heal_48": (132, 244, 164),
        "icon_teleport_48": (204, 132, 255),
    }
    for name, color in entries.items():
        s = _new_surface(48)
        pygame.draw.rect(s, (36, 42, 58), (2, 2, 44, 44), border_radius=10)
        pygame.draw.rect(s, (92, 116, 156), (2, 2, 44, 44), width=2, border_radius=10)
        pygame.draw.circle(s, color, (24, 24), 12)
        pygame.draw.circle(s, (255, 255, 255, 80), (20, 20), 5)
        pygame.image.save(s, os.path.join(path, f"{name}.png"))


def _write_wav(path: str, samples: List[float], sample_rate: int = 44100):
    with wave.open(path, "w") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        frames = bytearray()
        for s in samples:
            v = max(-1.0, min(1.0, s))
            iv = int(v * 32767)
            frames.extend(struct.pack("<hh", iv, iv))
        wf.writeframes(bytes(frames))


def _synth_tone(freq: float, duration: float, volume: float, waveform: str = "sine", sample_rate: int = 44100) -> List[float]:
    total = int(duration * sample_rate)
    out: List[float] = []
    for i in range(total):
        t = i / sample_rate
        if waveform == "square":
            w = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        elif waveform == "triangle":
            w = 2 * abs(2 * ((freq * t) % 1.0) - 1) - 1
        elif waveform == "saw":
            w = 2 * ((freq * t) % 1.0) - 1
        else:
            w = math.sin(2 * math.pi * freq * t)
        env = min(1.0, i / max(1, int(0.02 * sample_rate)))
        tail = min(1.0, (total - i) / max(1, int(0.08 * sample_rate)))
        out.append(w * env * tail * volume)
    return out


def _mix(*tracks: List[float]) -> List[float]:
    length = max(len(t) for t in tracks) if tracks else 0
    result = [0.0] * length
    for tr in tracks:
        for i, v in enumerate(tr):
            result[i] += v
    return [max(-1.0, min(1.0, v)) for v in result]


def _generate_sfx(path: str, category: str):
    defs = {
        "player": [
            ("hit.wav", [(170, 0.10, 0.38, "triangle"), (96, 0.14, 0.30, "saw")]),
            ("death.wav", [(140, 0.40, 0.34, "saw"), (74, 0.46, 0.26, "triangle")]),
            ("levelup.wav", [(392, 0.18, 0.3, "sine"), (523, 0.18, 0.27, "sine"), (659, 0.2, 0.24, "sine")]),
            ("footstep.wav", [(80, 0.06, 0.35, "square")]),
            ("pickup.wav", [(660, 0.08, 0.28, "sine"), (920, 0.06, 0.2, "sine")]),
            ("gold.wav", [(880, 0.07, 0.26, "sine"), (1320, 0.07, 0.2, "sine")]),
        ],
        "monster": [
            ("hit.wav", [(132, 0.13, 0.33, "saw")]),
            ("death.wav", [(96, 0.32, 0.35, "triangle")]),
            ("aggro.wav", [(188, 0.20, 0.3, "saw"), (156, 0.22, 0.2, "square")]),
        ],
        "skills": [
            ("swing.wav", [(210, 0.09, 0.25, "triangle")]),
            ("fireball.wav", [(440, 0.18, 0.28, "saw"), (220, 0.22, 0.15, "triangle")]),
            ("lightning.wav", [(1200, 0.12, 0.18, "square"), (600, 0.12, 0.12, "square")]),
            ("ice.wav", [(780, 0.14, 0.2, "triangle"), (1040, 0.12, 0.12, "sine")]),
            ("heal.wav", [(660, 0.16, 0.22, "sine"), (880, 0.16, 0.18, "sine")]),
            ("teleport.wav", [(300, 0.20, 0.2, "sine"), (1200, 0.12, 0.12, "triangle")]),
        ],
        "ui": [
            ("click.wav", [(520, 0.05, 0.2, "triangle")]),
            ("hover.wav", [(720, 0.04, 0.14, "sine")]),
            ("open.wav", [(420, 0.08, 0.16, "sine"), (630, 0.08, 0.14, "sine")]),
            ("close.wav", [(630, 0.06, 0.15, "sine"), (360, 0.09, 0.14, "triangle")]),
            ("error.wav", [(240, 0.16, 0.24, "square")]),
            ("success.wav", [(520, 0.08, 0.18, "sine"), (780, 0.08, 0.14, "sine")]),
            ("equip.wav", [(480, 0.06, 0.16, "triangle"), (720, 0.06, 0.12, "triangle")]),
            ("unequip.wav", [(720, 0.06, 0.16, "triangle"), (460, 0.07, 0.12, "triangle")]),
        ],
    }
    for filename, tones in defs.get(category, []):
        tracks = [_synth_tone(f, d, v, w) for f, d, v, w in tones]
        _write_wav(os.path.join(path, filename), _mix(*tracks))


def _sequence(notes: List[Tuple[float, float]], volume: float = 0.18) -> List[float]:
    sample_rate = 44100
    out: List[float] = []
    for freq, dur in notes:
        if freq <= 0:
            out.extend([0.0] * int(dur * sample_rate))
        else:
            out.extend(_synth_tone(freq, dur, volume, "sine", sample_rate))
    return out


def _generate_music(path: str):
    tracks = {
        "main_menu.wav": [(220, 0.4), (330, 0.4), (392, 0.4), (0, 0.2)] * 8,
        "town.wav": [(196, 0.35), (247, 0.35), (294, 0.35), (247, 0.35)] * 8,
        "exploration.wav": [(220, 0.24), (247, 0.24), (294, 0.24), (330, 0.24)] * 12,
        "combat.wav": [(220, 0.14), (220, 0.14), (196, 0.14), (247, 0.14), (294, 0.14)] * 16,
        "boss.wav": [(147, 0.18), (165, 0.18), (196, 0.18), (147, 0.18)] * 16,
        "credits.wav": [(262, 0.36), (330, 0.36), (392, 0.36), (523, 0.36)] * 8,
    }
    for filename, notes in tracks.items():
        melody = _sequence(notes, 0.16)
        pad = _sequence([(n[0] / 2 if n[0] > 0 else 0, n[1]) for n in notes], 0.08)
        _write_wav(os.path.join(path, filename), _mix(melody, pad))
