"""
存档系统 - 处理游戏存档的保存和加载
"""
import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib
import shutil
from config.game_config import GameConfig


class SaveSystem:
    _instance: Optional['SaveSystem'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.save_path = os.path.join(self.base_path, "saves")
        
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        
        self.current_save: Optional[str] = None
        self.auto_save_interval = 300
        self.save_schema_version = 2
        self.signature_secret = "diablo-mini-local-signature"
        
    @classmethod
    def get_instance(cls) -> 'SaveSystem':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def create_save_slot(self, slot_name: str) -> Dict[str, Any]:
        slot_path = os.path.join(self.save_path, slot_name)
        if not os.path.exists(slot_path):
            os.makedirs(slot_path)
        
        save_data = {
            "meta": {
                "slot_name": slot_name,
                "created": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat(),
                "play_time": 0,
                "version": f"{self.save_schema_version}.0"
            },
            "characters": [],
            "settings": {},
            "achievements": [],
            "lore_discovered": []
        }
        
        meta_path = os.path.join(slot_path, "meta.json")
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(save_data["meta"], f, ensure_ascii=False, indent=2)
        
        return save_data
    
    def get_save_slots(self) -> List[Dict[str, Any]]:
        slots = []
        
        if not os.path.exists(self.save_path):
            return slots
        
        for slot_name in os.listdir(self.save_path):
            slot_path = os.path.join(self.save_path, slot_name)
            if os.path.isdir(slot_path):
                meta_path = os.path.join(slot_path, "meta.json")
                if os.path.exists(meta_path):
                    try:
                        with open(meta_path, 'r', encoding='utf-8') as f:
                            meta = json.load(f)
                        slots.append(meta)
                    except Exception as e:
                        print(f"Error reading save slot {slot_name}: {e}")
        
        return sorted(slots, key=lambda x: x.get("last_modified", ""), reverse=True)
    
    def save_character(self, slot_name: str, character_data: Dict[str, Any]) -> bool:
        slot_path = os.path.join(self.save_path, slot_name)
        if not os.path.exists(slot_path):
            self.create_save_slot(slot_name)
        
        char_id = character_data.get("id", "default")
        char_path = os.path.join(slot_path, f"char_{char_id}.json")
        
        try:
            character_data["saved_at"] = datetime.now().isoformat()
            
            with open(char_path, 'w', encoding='utf-8') as f:
                json.dump(character_data, f, ensure_ascii=False, indent=2)
            
            meta_path = os.path.join(slot_path, "meta.json")
            if os.path.exists(meta_path):
                with open(meta_path, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                meta["last_modified"] = datetime.now().isoformat()
                with open(meta_path, 'w', encoding='utf-8') as f:
                    json.dump(meta, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving character: {e}")
            return False
    
    def load_character(self, slot_name: str, char_id: str) -> Optional[Dict[str, Any]]:
        slot_path = os.path.join(self.save_path, slot_name)
        char_path = os.path.join(slot_path, f"char_{char_id}.json")
        
        if not os.path.exists(char_path):
            return None
        
        try:
            with open(char_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if "schema_version" not in data:
                data["schema_version"] = 1
            data.setdefault("last_seen_at", "")
            return data
        except Exception as e:
            print(f"Error loading character: {e}")
            return None
    
    def get_characters_in_slot(self, slot_name: str) -> List[Dict[str, Any]]:
        slot_path = os.path.join(self.save_path, slot_name)
        characters = []
        
        if not os.path.exists(slot_path):
            return characters
        
        for filename in os.listdir(slot_path):
            if filename.startswith("char_") and filename.endswith(".json"):
                try:
                    char_path = os.path.join(slot_path, filename)
                    with open(char_path, 'r', encoding='utf-8') as f:
                        char_data = json.load(f)
                    characters.append(char_data)
                except Exception as e:
                    print(f"Error reading character {filename}: {e}")
        
        return sorted(characters, key=lambda x: x.get("saved_at", ""), reverse=True)
    
    def delete_character(self, slot_name: str, char_id: str) -> bool:
        slot_path = os.path.join(self.save_path, slot_name)
        char_path = os.path.join(slot_path, f"char_{char_id}.json")
        
        if os.path.exists(char_path):
            try:
                os.remove(char_path)
                return True
            except Exception as e:
                print(f"Error deleting character: {e}")
                return False
        return False
    
    def delete_save_slot(self, slot_name: str) -> bool:
        slot_path = os.path.join(self.save_path, slot_name)
        
        if os.path.exists(slot_path):
            try:
                import shutil
                shutil.rmtree(slot_path)
                return True
            except Exception as e:
                print(f"Error deleting save slot: {e}")
                return False
        return False
    
    def save_game(self, slot_name: str, game_data: Dict[str, Any]) -> bool:
        slot_path = os.path.join(self.save_path, slot_name)
        if not os.path.exists(slot_path):
            self.create_save_slot(slot_name)
        
        save_path = os.path.join(slot_path, "game_save.json")
        
        try:
            now = datetime.now().isoformat()
            payload = dict(game_data)
            payload["saved_at"] = now
            payload["schema_version"] = self.save_schema_version
            payload["last_seen_at"] = now
            self._backup_current_save(slot_path, save_path)
            wrapper = {
                "meta": {
                    "schema_version": self.save_schema_version,
                    "saved_at": now,
                    "signature": self._sign_payload(payload)
                },
                "payload": payload
            }

            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(wrapper, f, ensure_ascii=False, indent=2)
            
            if "character" in payload:
                char_data = dict(payload["character"])
                char_data["last_seen_at"] = payload.get("last_seen_at", now)
                char_data["schema_version"] = self.save_schema_version
                char_id = char_data.get("id", "default")
                char_path = os.path.join(slot_path, f"char_{char_id}.json")
                with open(char_path, 'w', encoding='utf-8') as f:
                    json.dump(char_data, f, ensure_ascii=False, indent=2)
            
            meta_path = os.path.join(slot_path, "meta.json")
            if os.path.exists(meta_path):
                with open(meta_path, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                meta["last_modified"] = datetime.now().isoformat()
                meta["play_time"] = payload.get("play_time", 0)
                meta["version"] = f"{self.save_schema_version}.0"
                with open(meta_path, 'w', encoding='utf-8') as f:
                    json.dump(meta, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
    
    def load_game(self, slot_name: str) -> Optional[Dict[str, Any]]:
        slot_path = os.path.join(self.save_path, slot_name)
        save_path = os.path.join(slot_path, "game_save.json")
        
        if not os.path.exists(save_path):
            characters = self.get_characters_in_slot(slot_name)
            if characters:
                return {"character": characters[0]}
            return None
        
        try:
            raw_data = self._safe_read_json(save_path)
            if raw_data is None:
                return None

            if "payload" in raw_data and "meta" in raw_data:
                payload = raw_data.get("payload", {})
                meta = raw_data.get("meta", {})
                signature = meta.get("signature", "")
                if not self._verify_payload(payload, signature):
                    backup_payload = self._load_latest_backup(slot_path)
                    if backup_payload:
                        return self._migrate_save_payload(backup_payload)
                    return None
                return self._migrate_save_payload(payload)

            return self._migrate_save_payload(raw_data)
        except Exception as e:
            print(f"Error loading game: {e}")
            return None

    def load_game_for_character(self, slot_name: str, char_id: str) -> Optional[Dict[str, Any]]:
        game_data = self.load_game(slot_name)
        if game_data and game_data.get("character", {}).get("id") == char_id:
            return game_data
        char_data = self.load_character(slot_name, char_id)
        if not char_data:
            return None
        return {"character": char_data}
    
    def save_settings(self, settings: Dict[str, Any]) -> bool:
        settings_path = os.path.join(self.base_path, "config", "user_settings.json")
        
        try:
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def load_settings(self) -> Dict[str, Any]:
        settings_path = os.path.join(self.base_path, "config", "user_settings.json")
        
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r', encoding='utf-8') as f:
                    return self._normalize_settings(json.load(f))
            except Exception as e:
                print(f"Error loading settings: {e}")
        
        return GameConfig.DEFAULT_SETTINGS.copy()
    
    def export_character(self, slot_name: str, char_id: str, export_path: str) -> bool:
        char_data = self.load_character(slot_name, char_id)
        if char_data:
            try:
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(char_data, f, ensure_ascii=False, indent=2)
                return True
            except Exception as e:
                print(f"Error exporting character: {e}")
        return False
    
    def import_character(self, slot_name: str, import_path: str) -> bool:
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                char_data = json.load(f)
            
            char_data["id"] = self._generate_char_id()
            return self.save_character(slot_name, char_data)
        except Exception as e:
            print(f"Error importing character: {e}")
            return False
    
    def _generate_char_id(self) -> str:
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:8]

    def _safe_read_json(self, path: str) -> Optional[Dict[str, Any]]:
        if not os.path.exists(path):
            return None
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _backup_current_save(self, slot_path: str, save_path: str):
        if not os.path.exists(save_path):
            return
        backup_dir = os.path.join(slot_path, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"game_save_{stamp}.json")
        shutil.copy2(save_path, backup_path)
        backups = sorted(
            [os.path.join(backup_dir, p) for p in os.listdir(backup_dir) if p.endswith(".json")],
            key=lambda p: os.path.getmtime(p),
            reverse=True
        )
        for old in backups[8:]:
            try:
                os.remove(old)
            except Exception:
                pass

    def _load_latest_backup(self, slot_path: str) -> Optional[Dict[str, Any]]:
        backup_dir = os.path.join(slot_path, "backups")
        if not os.path.exists(backup_dir):
            return None
        backups = sorted(
            [os.path.join(backup_dir, p) for p in os.listdir(backup_dir) if p.endswith(".json")],
            key=lambda p: os.path.getmtime(p),
            reverse=True
        )
        for backup in backups:
            try:
                data = self._safe_read_json(backup)
                if not data:
                    continue
                if "payload" in data and "meta" in data:
                    payload = data.get("payload", {})
                    signature = data.get("meta", {}).get("signature", "")
                    if self._verify_payload(payload, signature):
                        return payload
                else:
                    return data
            except Exception:
                continue
        return None

    def _sign_payload(self, payload: Dict[str, Any]) -> str:
        text = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(f"{self.signature_secret}:{text}".encode("utf-8")).hexdigest()

    def _verify_payload(self, payload: Dict[str, Any], signature: str) -> bool:
        if not signature:
            return False
        return self._sign_payload(payload) == str(signature)

    def _migrate_save_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        schema_version = int(payload.get("schema_version", 1))
        if schema_version < 2:
            payload.setdefault("telemetry", {})
            payload.setdefault("live_ops", {})
            payload.setdefault("risk_alerts", [])
            payload["schema_version"] = 2
        payload.setdefault("story_flags", {})
        payload.setdefault("chapter_history", [])
        payload.setdefault("ending_history", [])
        payload.setdefault("achievements", {})
        payload.setdefault("achievement_progress", {})
        payload.setdefault("settings", {})
        return payload

    def _normalize_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        normalized = GameConfig.DEFAULT_SETTINGS.copy()

        if "audio" in settings or "video" in settings or "gameplay" in settings:
            audio = settings.get("audio", {})
            video = settings.get("video", {})
            gameplay = settings.get("gameplay", {})

            normalized.update({
                "master_volume": int(audio.get("master_volume", normalized["master_volume"]) * 100) if audio.get("master_volume", 0) <= 1 else int(audio.get("master_volume", normalized["master_volume"])),
                "music_volume": int(audio.get("music_volume", normalized["music_volume"]) * 100) if audio.get("music_volume", 0) <= 1 else int(audio.get("music_volume", normalized["music_volume"])),
                "sfx_volume": int(audio.get("sfx_volume", normalized["sfx_volume"]) * 100) if audio.get("sfx_volume", 0) <= 1 else int(audio.get("sfx_volume", normalized["sfx_volume"])),
                "fullscreen": bool(video.get("fullscreen", normalized["fullscreen"])),
                "vsync": bool(video.get("vsync", normalized["vsync"])),
                "show_damage_numbers": bool(gameplay.get("show_damage_numbers", normalized["show_damage_numbers"])),
                "show_health_bars": bool(gameplay.get("show_health_bars", normalized["show_health_bars"])),
            })
            return normalized

        normalized.update({
            "master_volume": int(settings.get("master_volume", normalized["master_volume"])),
            "music_volume": int(settings.get("music_volume", normalized["music_volume"])),
            "sfx_volume": int(settings.get("sfx_volume", normalized["sfx_volume"])),
            "fullscreen": bool(settings.get("fullscreen", normalized["fullscreen"])),
            "vsync": bool(settings.get("vsync", normalized["vsync"])),
            "show_damage_numbers": bool(settings.get("show_damage_numbers", normalized["show_damage_numbers"])),
            "show_health_bars": bool(settings.get("show_health_bars", normalized["show_health_bars"])),
        })
        return normalized
