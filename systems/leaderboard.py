"""
大秘境排行榜系统
支持本地排行榜、赛季排行、历史记录
"""
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json
import os
from collections import defaultdict


class LeaderboardType(Enum):
    GREATER_RIFT = "greater_rift"
    SPEED_RUN = "speed_run"
    COMBINED = "combined"


class LeaderboardPeriod(Enum):
    ALL_TIME = "all_time"
    SEASON = "season"
    WEEKLY = "weekly"
    DAILY = "daily"


@dataclass
class LeaderboardEntry:
    rank: int
    character_id: str
    character_name: str
    character_class: str
    rift_level: int
    clear_time: float
    timestamp: float
    season: int = 0
    deaths: int = 0
    damage_dealt: int = 0
    damage_taken: int = 0
    skills_used: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "rank": self.rank,
            "character_id": self.character_id,
            "character_name": self.character_name,
            "character_class": self.character_class,
            "rift_level": self.rift_level,
            "clear_time": self.clear_time,
            "timestamp": self.timestamp,
            "season": self.season,
            "deaths": self.deaths,
            "damage_dealt": self.damage_dealt,
            "damage_taken": self.damage_taken,
            "skills_used": self.skills_used
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LeaderboardEntry':
        return cls(
            rank=data.get("rank", 0),
            character_id=data.get("character_id", ""),
            character_name=data.get("character_name", ""),
            character_class=data.get("character_class", ""),
            rift_level=data.get("rift_level", 0),
            clear_time=data.get("clear_time", 0.0),
            timestamp=data.get("timestamp", 0.0),
            season=data.get("season", 0),
            deaths=data.get("deaths", 0),
            damage_dealt=data.get("damage_dealt", 0),
            damage_taken=data.get("damage_taken", 0),
            skills_used=data.get("skills_used", {})
        )
    
    def get_score(self) -> float:
        return self.rift_level * 1000 + (600 - min(self.clear_time, 600))


@dataclass
class LeaderboardCategory:
    category_id: str
    name: str
    leaderboard_type: LeaderboardType
    max_entries: int = 1000
    entries: List[LeaderboardEntry] = field(default_factory=list)
    
    def add_entry(self, entry: LeaderboardEntry) -> int:
        self.entries.append(entry)
        self._sort_and_rank()
        self._trim()
        
        for i, e in enumerate(self.entries):
            if e.character_id == entry.character_id and e.rift_level == entry.rift_level:
                return e.rank
        return -1
    
    def _sort_and_rank(self):
        self.entries.sort(key=lambda e: (-e.rift_level, e.clear_time))
        for i, entry in enumerate(self.entries):
            entry.rank = i + 1
    
    def _trim(self):
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[:self.max_entries]
    
    def get_top(self, count: int = 10) -> List[LeaderboardEntry]:
        return self.entries[:count]
    
    def get_rank(self, character_id: str) -> Optional[int]:
        for entry in self.entries:
            if entry.character_id == character_id:
                return entry.rank
        return None
    
    def get_entry_by_rank(self, rank: int) -> Optional[LeaderboardEntry]:
        for entry in self.entries:
            if entry.rank == rank:
                return entry
        return None
    
    def get_entries_around(self, character_id: str, range_size: int = 5) -> List[LeaderboardEntry]:
        target_rank = self.get_rank(character_id)
        if target_rank is None:
            return []
        
        start = max(1, target_rank - range_size)
        end = min(len(self.entries), target_rank + range_size)
        
        return [e for e in self.entries if start <= e.rank <= end]


class LeaderboardManager:
    def __init__(self, data_dir: str = "leaderboard"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self._categories: Dict[str, LeaderboardCategory] = {}
        self._player_best: Dict[str, Dict[str, LeaderboardEntry]] = defaultdict(dict)
        self._current_season: int = 1
        
        self._initialize_categories()
        self._load_data()
    
    def _initialize_categories(self):
        self._categories["greater_rift_all"] = LeaderboardCategory(
            category_id="greater_rift_all",
            name="大秘境总榜",
            leaderboard_type=LeaderboardType.GREATER_RIFT
        )
        
        self._categories["greater_rift_season"] = LeaderboardCategory(
            category_id="greater_rift_season",
            name="大秘境赛季榜",
            leaderboard_type=LeaderboardType.GREATER_RIFT
        )
        
        self._categories["speed_run"] = LeaderboardCategory(
            category_id="speed_run",
            name="速通榜",
            leaderboard_type=LeaderboardType.SPEED_RUN
        )
        
        classes = ["warrior", "mage", "rogue", "necromancer", "paladin", "amazon", "sorceress", "barbarian"]
        for cls in classes:
            self._categories[f"greater_rift_{cls}"] = LeaderboardCategory(
                category_id=f"greater_rift_{cls}",
                name=f"大秘境 - {self._get_class_name(cls)}",
                leaderboard_type=LeaderboardType.GREATER_RIFT
            )
    
    def _get_class_name(self, class_id: str) -> str:
        names = {
            "warrior": "战士",
            "mage": "法师",
            "rogue": "盗贼",
            "necromancer": "死灵法师",
            "paladin": "圣骑士",
            "amazon": "亚马逊",
            "sorceress": "女巫",
            "barbarian": "野蛮人"
        }
        return names.get(class_id, class_id)
    
    def submit_rift_run(self, character_id: str, character_name: str,
                        character_class: str, rift_level: int, clear_time: float,
                        deaths: int = 0, damage_dealt: int = 0, 
                        damage_taken: int = 0, skills_used: Dict[str, int] = None) -> Dict[str, int]:
        if skills_used is None:
            skills_used = {}
        
        entry = LeaderboardEntry(
            rank=0,
            character_id=character_id,
            character_name=character_name,
            character_class=character_class,
            rift_level=rift_level,
            clear_time=clear_time,
            timestamp=datetime.now().timestamp(),
            season=self._current_season,
            deaths=deaths,
            damage_dealt=damage_dealt,
            damage_taken=damage_taken,
            skills_used=skills_used
        )
        
        ranks = {}
        
        if "greater_rift_all" in self._categories:
            ranks["all"] = self._categories["greater_rift_all"].add_entry(entry)
        
        if "greater_rift_season" in self._categories:
            season_entry = LeaderboardEntry(**{**entry.__dict__, "skills_used": dict(entry.skills_used)})
            ranks["season"] = self._categories["greater_rift_season"].add_entry(season_entry)
        
        class_key = f"greater_rift_{character_class}"
        if class_key in self._categories:
            class_entry = LeaderboardEntry(**{**entry.__dict__, "skills_used": dict(entry.skills_used)})
            ranks["class"] = self._categories[class_key].add_entry(class_entry)
        
        if clear_time < 180 and rift_level >= 50:
            if "speed_run" in self._categories:
                speed_entry = LeaderboardEntry(**{**entry.__dict__, "skills_used": dict(entry.skills_used)})
                ranks["speed"] = self._categories["speed_run"].add_entry(speed_entry)
        
        self._update_player_best(character_id, entry)
        self._save_data()
        
        return ranks
    
    def _update_player_best(self, character_id: str, entry: LeaderboardEntry):
        current_best = self._player_best.get(character_id, {}).get("best")
        
        if current_best is None or entry.rift_level > current_best.rift_level:
            self._player_best[character_id]["best"] = entry
        elif entry.rift_level == current_best.rift_level and entry.clear_time < current_best.clear_time:
            self._player_best[character_id]["best"] = entry
    
    def get_leaderboard(self, category_id: str, count: int = 10) -> List[LeaderboardEntry]:
        category = self._categories.get(category_id)
        if not category:
            return []
        return category.get_top(count)
    
    def get_player_rank(self, character_id: str, category_id: str = "greater_rift_all") -> Optional[int]:
        category = self._categories.get(category_id)
        if not category:
            return None
        return category.get_rank(character_id)
    
    def get_player_best(self, character_id: str) -> Optional[LeaderboardEntry]:
        return self._player_best.get(character_id, {}).get("best")
    
    def get_rankings_around_player(self, character_id: str, 
                                    category_id: str = "greater_rift_all",
                                    range_size: int = 5) -> List[LeaderboardEntry]:
        category = self._categories.get(category_id)
        if not category:
            return []
        return category.get_entries_around(character_id, range_size)
    
    def get_class_leaderboard(self, character_class: str, count: int = 10) -> List[LeaderboardEntry]:
        return self.get_leaderboard(f"greater_rift_{character_class}", count)
    
    def get_season_leaderboard(self, count: int = 10) -> List[LeaderboardEntry]:
        return self.get_leaderboard("greater_rift_season", count)
    
    def get_speed_run_leaderboard(self, count: int = 10) -> List[LeaderboardEntry]:
        return self.get_leaderboard("speed_run", count)
    
    def set_season(self, season: int):
        self._current_season = season
        
        if "greater_rift_season" in self._categories:
            self._categories["greater_rift_season"].entries.clear()
        
        self._save_data()
    
    def get_current_season(self) -> int:
        return self._current_season
    
    def get_statistics(self) -> Dict[str, Any]:
        stats = {
            "total_runs": 0,
            "unique_players": set(),
            "highest_level": 0,
            "fastest_clear": float('inf'),
            "class_distribution": defaultdict(int),
            "level_distribution": defaultdict(int),
        }
        
        for category in self._categories.values():
            for entry in category.entries:
                stats["total_runs"] += 1
                stats["unique_players"].add(entry.character_id)
                stats["highest_level"] = max(stats["highest_level"], entry.rift_level)
                stats["fastest_clear"] = min(stats["fastest_clear"], entry.clear_time)
                stats["class_distribution"][entry.character_class] += 1
                stats["level_distribution"][entry.rift_level] += 1
        
        stats["unique_players"] = len(stats["unique_players"])
        stats["fastest_clear"] = stats["fastest_clear"] if stats["fastest_clear"] != float('inf') else 0
        stats["class_distribution"] = dict(stats["class_distribution"])
        stats["level_distribution"] = dict(stats["level_distribution"])
        
        return stats
    
    def _save_data(self):
        data = {
            "current_season": self._current_season,
            "categories": {},
            "player_best": {}
        }
        
        for cat_id, category in self._categories.items():
            data["categories"][cat_id] = {
                "category_id": category.category_id,
                "name": category.name,
                "entries": [e.to_dict() for e in category.entries]
            }
        
        for char_id, best_data in self._player_best.items():
            if "best" in best_data:
                data["player_best"][char_id] = best_data["best"].to_dict()
        
        filepath = os.path.join(self.data_dir, "leaderboard_data.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _load_data(self):
        filepath = os.path.join(self.data_dir, "leaderboard_data.json")
        
        if not os.path.exists(filepath):
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._current_season = data.get("current_season", 1)
            
            for cat_id, cat_data in data.get("categories", {}).items():
                if cat_id in self._categories:
                    entries = [LeaderboardEntry.from_dict(e) for e in cat_data.get("entries", [])]
                    self._categories[cat_id].entries = entries
                    self._categories[cat_id]._sort_and_rank()
            
            for char_id, entry_data in data.get("player_best", {}).items():
                self._player_best[char_id]["best"] = LeaderboardEntry.from_dict(entry_data)
                
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading leaderboard data: {e}")
    
    def generate_leaderboard_display(self, category_id: str = "greater_rift_all", 
                                      count: int = 10) -> List[str]:
        entries = self.get_leaderboard(category_id, count)
        lines = []
        
        category = self._categories.get(category_id)
        if category:
            lines.append(f"=== {category.name} ===")
        else:
            lines.append("=== 排行榜 ===")
        
        lines.append("-" * 50)
        lines.append(f"{'排名':<6}{'角色名':<12}{'职业':<10}{'层数':<8}{'时间':<10}")
        lines.append("-" * 50)
        
        for entry in entries:
            time_str = f"{int(entry.clear_time // 60):02d}:{int(entry.clear_time % 60):02d}"
            lines.append(
                f"{entry.rank:<6}{entry.character_name:<12}"
                f"{self._get_class_name(entry.character_class):<10}"
                f"{entry.rift_level:<8}{time_str:<10}"
            )
        
        return lines


_leaderboard_manager: Optional[LeaderboardManager] = None


def get_leaderboard() -> LeaderboardManager:
    global _leaderboard_manager
    if _leaderboard_manager is None:
        _leaderboard_manager = LeaderboardManager()
    return _leaderboard_manager
