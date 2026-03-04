"""
赛季系统
支持赛季轮换、赛季词缀、赛季奖励、赛季旅程
"""
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import os
import random


class SeasonState(Enum):
    PRE_SEASON = "pre_season"
    ACTIVE = "active"
    ENDING = "ending"
    ENDED = "ended"


class SeasonRewardType(Enum):
    PORTRAIT = "portrait"
    FRAME = "frame"
    WINGS = "wings"
    PET = "pet"
    TRANSMOG = "transmog"
    BANNER = "banner"
    CONQUEST_POINTS = "conquest_points"


@dataclass
class SeasonAffix:
    affix_id: str
    name: str
    description: str
    effect_type: str
    effect_value: float
    is_negative: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "affix_id": self.affix_id,
            "name": self.name,
            "description": self.description,
            "effect_type": self.effect_type,
            "effect_value": self.effect_value,
            "is_negative": self.is_negative
        }


@dataclass
class SeasonReward:
    reward_id: str
    reward_type: SeasonRewardType
    name: str
    description: str
    tier: int
    icon: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "reward_id": self.reward_id,
            "reward_type": self.reward_type.value,
            "name": self.name,
            "description": self.description,
            "tier": self.tier,
            "icon": self.icon
        }


@dataclass
class SeasonJourneyChapter:
    chapter_id: int
    name: str
    description: str
    required_points: int
    tasks: List[Dict[str, Any]] = field(default_factory=list)
    rewards: List[SeasonReward] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "chapter_id": self.chapter_id,
            "name": self.name,
            "description": self.description,
            "required_points": self.required_points,
            "tasks": self.tasks,
            "rewards": [r.to_dict() for r in self.rewards]
        }


@dataclass
class SeasonJourneyProgress:
    character_id: str
    season: int
    total_points: int = 0
    completed_tasks: List[str] = field(default_factory=list)
    claimed_chapters: List[int] = field(default_factory=list)
    chapter_points: Dict[int, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "character_id": self.character_id,
            "season": self.season,
            "total_points": self.total_points,
            "completed_tasks": self.completed_tasks,
            "claimed_chapters": self.claimed_chapters,
            "chapter_points": self.chapter_points
        }


@dataclass
class Season:
    season_id: int
    name: str
    theme: str
    start_date: datetime
    end_date: datetime
    state: SeasonState = SeasonState.ACTIVE
    
    affixes: List[SeasonAffix] = field(default_factory=list)
    rewards: List[SeasonReward] = field(default_factory=list)
    journey_chapters: List[SeasonJourneyChapter] = field(default_factory=list)
    
    bonus_exp: float = 1.0
    bonus_gold: float = 1.0
    bonus_drop: float = 1.0
    
    haedrig_gift_class: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "season_id": self.season_id,
            "name": self.name,
            "theme": self.theme,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "state": self.state.value,
            "affixes": [a.to_dict() for a in self.affixes],
            "rewards": [r.to_dict() for r in self.rewards],
            "journey_chapters": [c.to_dict() for c in self.journey_chapters],
            "bonus_exp": self.bonus_exp,
            "bonus_gold": self.bonus_gold,
            "bonus_drop": self.bonus_drop,
            "haedrig_gift_class": self.haedrig_gift_class
        }
    
    @property
    def duration_days(self) -> int:
        return (self.end_date - self.start_date).days
    
    @property
    def days_remaining(self) -> int:
        remaining = (self.end_date - datetime.now()).days
        return max(0, remaining)
    
    @property
    def is_active(self) -> bool:
        return self.state == SeasonState.ACTIVE and datetime.now() < self.end_date


class SeasonManager:
    def __init__(self, data_dir: str = "seasons"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self._current_season: Optional[Season] = None
        self._seasons: Dict[int, Season] = {}
        self._player_progress: Dict[str, SeasonJourneyProgress] = {}
        self._claimed_rewards: Dict[str, List[str]] = {}
        
        self._season_change_callbacks: List[Callable[[Season], None]] = []
        
        self._initialize_seasons()
        self._load_data()
    
    def _initialize_seasons(self):
        predefined_affixes = [
            SeasonAffix("explosive", "爆炸", "怪物死亡时爆炸，造成范围伤害", "on_death_explosion", 50, True),
            SeasonAffix("vampiric", "吸血", "怪物攻击回复生命", "life_steal", 0.1, True),
            SeasonAffix("frenzy", "狂暴", "怪物攻击速度提升", "attack_speed", 0.3, True),
            SeasonAffix("fortified", "强化", "怪物生命值提升", "health", 0.5, True),
            SeasonAffix("elemental", "元素", "怪物攻击附带随机元素伤害", "elemental_damage", 25, True),
            SeasonAffix("shadow", "暗影", "怪物有几率隐身", "stealth_chance", 0.2, True),
            SeasonAffix("regenerating", "再生", "怪物持续回复生命", "health_regen", 5, True),
            SeasonAffix("reflecting", "反射", "怪物反射部分伤害", "damage_reflect", 0.15, True),
        ]
        
        predefined_rewards = [
            SeasonReward("portrait_s1", SeasonRewardType.PORTRAIT, "赛季头像框", "完成赛季旅程获得", 1),
            SeasonReward("frame_s1", SeasonRewardType.FRAME, "赛季边框", "达到70级获得", 1),
            SeasonReward("wings_s1", SeasonRewardType.WINGS, "赛季翅膀", "完成全部旅程章节获得", 3),
            SeasonReward("pet_s1", SeasonRewardType.PET, "赛季宠物", "完成第4章获得", 2),
            SeasonReward("transmog_s1", SeasonRewardType.TRANSMOG, "赛季幻化", "完成第2章获得", 1),
        ]
        
        now = datetime.now()
        
        for i in range(1, 5):
            start = now - timedelta(days=90 * (4 - i))
            end = start + timedelta(days=90)
            
            season = Season(
                season_id=i,
                name=f"第{i}赛季",
                theme=self._get_season_theme(i),
                start_date=start,
                end_date=end,
                state=SeasonState.ACTIVE if i == 4 else SeasonState.ENDED,
                affixes=random.sample(predefined_affixes, min(3, len(predefined_affixes))),
                rewards=predefined_rewards,
                bonus_exp=1.0 + i * 0.1,
                bonus_gold=1.0 + i * 0.05,
                haedrig_gift_class=random.choice(["warrior", "mage", "rogue", "necromancer"])
            )
            
            season.journey_chapters = self._create_journey_chapters(i)
            
            self._seasons[i] = season
            
            if i == 4:
                self._current_season = season
    
    def _get_season_theme(self, season_id: int) -> str:
        themes = {
            1: "暗影崛起",
            2: "元素风暴",
            3: "死亡领主",
            4: "永恒之战",
        }
        return themes.get(season_id, f"第{season_id}赛季")
    
    def _create_journey_chapters(self, season_id: int) -> List[SeasonJourneyChapter]:
        chapters = [
            SeasonJourneyChapter(
                chapter_id=1,
                name="初入赛季",
                description="开始你的赛季旅程",
                required_points=100,
                tasks=[
                    {"task_id": f"s{season_id}_c1_t1", "name": "创建赛季角色", "points": 20, "type": "create_character"},
                    {"task_id": f"s{season_id}_c1_t2", "name": "达到10级", "points": 30, "type": "reach_level"},
                    {"task_id": f"s{season_id}_c1_t3", "name": "完成第一个任务", "points": 20, "type": "complete_quest"},
                    {"task_id": f"s{season_id}_c1_t4", "name": "击杀100只怪物", "points": 30, "type": "kill_monsters"},
                ],
                rewards=[SeasonReward(f"transmog_s{season_id}", SeasonRewardType.TRANSMOG, "赛季幻化", "完成第一章获得", 1)]
            ),
            SeasonJourneyChapter(
                chapter_id=2,
                name="渐入佳境",
                description="继续你的冒险",
                required_points=300,
                tasks=[
                    {"task_id": f"s{season_id}_c2_t1", "name": "达到40级", "points": 50, "type": "reach_level"},
                    {"task_id": f"s{season_id}_c2_t2", "name": "完成5个任务", "points": 50, "type": "complete_quest"},
                    {"task_id": f"s{season_id}_c2_t3", "name": "击杀1000只怪物", "points": 80, "type": "kill_monsters"},
                    {"task_id": f"s{season_id}_c2_t4", "name": "完成一次秘境", "points": 60, "type": "complete_rift"},
                    {"task_id": f"s{season_id}_c2_t5", "name": "获得一件传奇装备", "points": 60, "type": "get_legendary"},
                ],
                rewards=[SeasonReward(f"frame_s{season_id}", SeasonRewardType.FRAME, "赛季边框", "完成第二章获得", 1)]
            ),
            SeasonJourneyChapter(
                chapter_id=3,
                name="勇者之路",
                description="证明你的实力",
                required_points=600,
                tasks=[
                    {"task_id": f"s{season_id}_c3_t1", "name": "达到70级", "points": 100, "type": "reach_level"},
                    {"task_id": f"s{season_id}_c3_t2", "name": "完成10次秘境", "points": 100, "type": "complete_rift"},
                    {"task_id": f"s{season_id}_c3_t3", "name": "击杀5000只怪物", "points": 150, "type": "kill_monsters"},
                    {"task_id": f"s{season_id}_c3_t4", "name": "完成大秘境20层", "points": 150, "type": "complete_greater_rift"},
                    {"task_id": f"s{season_id}_c3_t5", "name": "获得5件传奇装备", "points": 100, "type": "get_legendary"},
                ],
                rewards=[SeasonReward(f"pet_s{season_id}", SeasonRewardType.PET, "赛季宠物", "完成第三章获得", 2)]
            ),
            SeasonJourneyChapter(
                chapter_id=4,
                name="传奇之路",
                description="成为真正的传奇",
                required_points=1000,
                tasks=[
                    {"task_id": f"s{season_id}_c4_t1", "name": "完成大秘境50层", "points": 200, "type": "complete_greater_rift"},
                    {"task_id": f"s{season_id}_c4_t2", "name": "击杀20000只怪物", "points": 200, "type": "kill_monsters"},
                    {"task_id": f"s{season_id}_c4_t3", "name": "获得20件传奇装备", "points": 150, "type": "get_legendary"},
                    {"task_id": f"s{season_id}_c4_t4", "name": "完成所有主线任务", "points": 200, "type": "complete_quest"},
                    {"task_id": f"s{season_id}_c4_t5", "name": "达到巅峰等级100", "points": 250, "type": "reach_paragon"},
                ],
                rewards=[SeasonReward(f"wings_s{season_id}", SeasonRewardType.WINGS, "赛季翅膀", "完成第四章获得", 3)]
            ),
        ]
        return chapters
    
    def get_current_season(self) -> Optional[Season]:
        return self._current_season
    
    def get_season(self, season_id: int) -> Optional[Season]:
        return self._seasons.get(season_id)
    
    def get_all_seasons(self) -> List[Season]:
        return list(self._seasons.values())
    
    def start_new_season(self, name: str, theme: str, duration_days: int = 90) -> Season:
        new_id = max(self._seasons.keys()) + 1 if self._seasons else 1
        
        if self._current_season:
            self._current_season.state = SeasonState.ENDED
        
        now = datetime.now()
        season = Season(
            season_id=new_id,
            name=name,
            theme=theme,
            start_date=now,
            end_date=now + timedelta(days=duration_days),
            state=SeasonState.ACTIVE,
            journey_chapters=self._create_journey_chapters(new_id)
        )
        
        self._seasons[new_id] = season
        self._current_season = season
        
        for callback in self._season_change_callbacks:
            callback(season)
        
        self._save_data()
        
        return season
    
    def end_season(self):
        if not self._current_season:
            return
        
        self._current_season.state = SeasonState.ENDED
        self._save_data()
    
    def get_season_affixes(self) -> List[SeasonAffix]:
        if not self._current_season:
            return []
        return self._current_season.affixes
    
    def get_season_bonuses(self) -> Dict[str, float]:
        if not self._current_season:
            return {"exp": 1.0, "gold": 1.0, "drop": 1.0}
        
        return {
            "exp": self._current_season.bonus_exp,
            "gold": self._current_season.bonus_gold,
            "drop": self._current_season.bonus_drop
        }
    
    def get_journey_progress(self, character_id: str) -> SeasonJourneyProgress:
        if character_id not in self._player_progress:
            self._player_progress[character_id] = SeasonJourneyProgress(
                character_id=character_id,
                season=self._current_season.season_id if self._current_season else 0
            )
        return self._player_progress[character_id]
    
    def complete_task(self, character_id: str, task_id: str) -> bool:
        progress = self.get_journey_progress(character_id)
        
        if task_id in progress.completed_tasks:
            return False
        
        task = self._find_task(task_id)
        if not task:
            return False
        
        progress.completed_tasks.append(task_id)
        progress.total_points += task.get("points", 0)
        
        chapter_id = self._get_task_chapter(task_id)
        if chapter_id:
            progress.chapter_points[chapter_id] = progress.chapter_points.get(chapter_id, 0) + task.get("points", 0)
        
        self._save_data()
        return True
    
    def _find_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        if not self._current_season:
            return None
        
        for chapter in self._current_season.journey_chapters:
            for task in chapter.tasks:
                if task.get("task_id") == task_id:
                    return task
        return None
    
    def _get_task_chapter(self, task_id: str) -> Optional[int]:
        if not self._current_season:
            return None
        
        for chapter in self._current_season.journey_chapters:
            for task in chapter.tasks:
                if task.get("task_id") == task_id:
                    return chapter.chapter_id
        return None
    
    def can_claim_chapter_reward(self, character_id: str, chapter_id: int) -> bool:
        progress = self.get_journey_progress(character_id)
        
        if chapter_id in progress.claimed_chapters:
            return False
        
        if not self._current_season:
            return False
        
        chapter = next((c for c in self._current_season.journey_chapters if c.chapter_id == chapter_id), None)
        if not chapter:
            return False
        
        chapter_points = progress.chapter_points.get(chapter_id, 0)
        return chapter_points >= chapter.required_points
    
    def claim_chapter_reward(self, character_id: str, chapter_id: int) -> List[SeasonReward]:
        if not self.can_claim_chapter_reward(character_id, chapter_id):
            return []
        
        progress = self.get_journey_progress(character_id)
        progress.claimed_chapters.append(chapter_id)
        
        chapter = next((c for c in self._current_season.journey_chapters if c.chapter_id == chapter_id), None)
        if not chapter:
            return []
        
        if character_id not in self._claimed_rewards:
            self._claimed_rewards[character_id] = []
        
        for reward in chapter.rewards:
            self._claimed_rewards[character_id].append(reward.reward_id)
        
        self._save_data()
        
        return chapter.rewards
    
    def get_claimed_rewards(self, character_id: str) -> List[str]:
        return self._claimed_rewards.get(character_id, [])
    
    def get_journey_status(self, character_id: str) -> Dict[str, Any]:
        progress = self.get_journey_progress(character_id)
        
        if not self._current_season:
            return {"error": "No active season"}
        
        chapters_status = []
        for chapter in self._current_season.journey_chapters:
            chapter_points = progress.chapter_points.get(chapter.chapter_id, 0)
            completed_tasks = [t for t in chapter.tasks if t.get("task_id") in progress.completed_tasks]
            
            chapters_status.append({
                "chapter_id": chapter.chapter_id,
                "name": chapter.name,
                "points": chapter_points,
                "required_points": chapter.required_points,
                "completed": chapter_points >= chapter.required_points,
                "claimed": chapter.chapter_id in progress.claimed_chapters,
                "total_tasks": len(chapter.tasks),
                "completed_tasks": len(completed_tasks)
            })
        
        return {
            "season_id": self._current_season.season_id,
            "season_name": self._current_season.name,
            "total_points": progress.total_points,
            "chapters": chapters_status,
            "days_remaining": self._current_season.days_remaining
        }
    
    def register_season_change_callback(self, callback: Callable[[Season], None]):
        self._season_change_callbacks.append(callback)
    
    def _save_data(self):
        data = {
            "current_season_id": self._current_season.season_id if self._current_season else None,
            "player_progress": {
                char_id: progress.to_dict() 
                for char_id, progress in self._player_progress.items()
            },
            "claimed_rewards": self._claimed_rewards
        }
        
        filepath = os.path.join(self.data_dir, "season_data.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    def _load_data(self):
        filepath = os.path.join(self.data_dir, "season_data.json")
        
        if not os.path.exists(filepath):
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            current_id = data.get("current_season_id")
            if current_id and current_id in self._seasons:
                self._current_season = self._seasons[current_id]
            
            for char_id, progress_data in data.get("player_progress", {}).items():
                self._player_progress[char_id] = SeasonJourneyProgress(
                    character_id=progress_data.get("character_id", char_id),
                    season=progress_data.get("season", 0),
                    total_points=progress_data.get("total_points", 0),
                    completed_tasks=progress_data.get("completed_tasks", []),
                    claimed_chapters=progress_data.get("claimed_chapters", []),
                    chapter_points=progress_data.get("chapter_points", {})
                )
            
            self._claimed_rewards = data.get("claimed_rewards", {})
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading season data: {e}")


_season_manager: Optional[SeasonManager] = None


def get_season_manager() -> SeasonManager:
    global _season_manager
    if _season_manager is None:
        _season_manager = SeasonManager()
    return _season_manager
