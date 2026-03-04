"""
数据埋点系统 - 商业化级别的游戏数据分析
支持留存、活跃、经济、战斗效率等指标
"""
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import time
import os
from datetime import datetime
from collections import defaultdict


class EventType(Enum):
    # 会话事件
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    
    # 角色事件
    CHARACTER_CREATE = "character_create"
    CHARACTER_LEVEL_UP = "character_level_up"
    CHARACTER_DEATH = "character_death"
    
    # 经济事件
    GOLD_EARN = "gold_earn"
    GOLD_SPEND = "gold_spend"
    ITEM_LOOT = "item_loot"
    ITEM_SELL = "item_sell"
    ITEM_CRAFT = "item_craft"
    
    # 战斗事件
    COMBAT_START = "combat_start"
    COMBAT_END = "combat_end"
    SKILL_USE = "skill_use"
    DAMAGE_DEAL = "damage_deal"
    DAMAGE_TAKE = "damage_take"
    
    # 探索事件
    AREA_ENTER = "area_enter"
    AREA_EXIT = "area_exit"
    WAYPOINT_UNLOCK = "waypoint_unlock"
    
    # 任务事件
    QUEST_START = "quest_start"
    QUEST_COMPLETE = "quest_complete"
    QUEST_FAIL = "quest_fail"
    
    # 秘境事件
    RIFT_ENTER = "rift_enter"
    RIFT_COMPLETE = "rift_complete"
    RIFT_FAIL = "rift_fail"
    
    # 社交事件
    NPC_INTERACT = "npc_interact"
    TRADE_COMPLETE = "trade_complete"
    
    # UI事件
    UI_OPEN = "ui_open"
    UI_CLOSE = "ui_close"
    TUTORIAL_COMPLETE = "tutorial_complete"


@dataclass
class AnalyticsEvent:
    """分析事件"""
    event_type: EventType
    timestamp: float
    session_id: str
    character_id: str
    character_level: int
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "session_id": self.session_id,
            "character_id": self.character_id,
            "character_level": self.character_level,
            "data": self.data
        }


@dataclass
class SessionStats:
    """会话统计"""
    session_id: str
    start_time: float
    end_time: Optional[float] = None
    duration: float = 0
    
    # 角色信息
    character_id: str = ""
    character_class: str = ""
    character_level_start: int = 1
    character_level_end: int = 1
    
    # 经济统计
    gold_earned: int = 0
    gold_spent: int = 0
    items_looted: int = 0
    items_sold: int = 0
    
    # 战斗统计
    combats: int = 0
    kills: int = 0
    deaths: int = 0
    damage_dealt: int = 0
    damage_taken: int = 0
    skills_used: int = 0
    
    # 探索统计
    areas_visited: int = 0
    waypoints_unlocked: int = 0
    
    # 任务统计
    quests_started: int = 0
    quests_completed: int = 0
    
    # 秘境统计
    rifts_entered: int = 0
    rifts_completed: int = 0
    highest_rift_level: int = 0
    
    @property
    def gold_net(self) -> int:
        return self.gold_earned - self.gold_spent
    
    @property
    def dps(self) -> float:
        if self.duration <= 0:
            return 0
        return self.damage_dealt / self.duration
    
    @property
    def survival_rate(self) -> float:
        if self.combats <= 0:
            return 1.0
        return 1.0 - (self.deaths / self.combats)


class AnalyticsManager:
    """数据分析管理器"""
    
    def __init__(self, data_dir: str = "analytics"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self._events: List[AnalyticsEvent] = []
        self._session: Optional[SessionStats] = None
        self._session_id: str = ""
        
        # 聚合统计
        self._daily_stats: Dict[str, Dict] = defaultdict(lambda: {
            "sessions": 0,
            "new_characters": 0,
            "total_play_time": 0,
            "total_gold_earned": 0,
            "total_gold_spent": 0,
            "total_kills": 0,
            "total_deaths": 0,
        })
        
        # 留存追踪
        self._player_first_seen: Dict[str, str] = {}
        self._player_sessions: Dict[str, List[str]] = defaultdict(list)
        
        # 实时指标
        self._current_character_id: str = ""
        self._current_character_level: int = 1
    
    def start_session(self, character_id: str, character_class: str, level: int):
        """开始会话"""
        self._session_id = self._generate_session_id()
        self._current_character_id = character_id
        self._current_character_level = level
        
        self._session = SessionStats(
            session_id=self._session_id,
            start_time=time.time(),
            character_id=character_id,
            character_class=character_class,
            character_level_start=level,
            character_level_end=level
        )
        
        # 记录会话开始事件
        self.track_event(EventType.SESSION_START, {
            "character_class": character_class,
            "level": level
        })
        
        # 更新留存数据
        today = datetime.now().strftime("%Y-%m-%d")
        if character_id not in self._player_first_seen:
            self._player_first_seen[character_id] = today
            self._daily_stats[today]["new_characters"] += 1
        
        self._player_sessions[character_id].append(today)
    
    def end_session(self):
        """结束会话"""
        if not self._session:
            return
        
        self._session.end_time = time.time()
        self._session.duration = self._session.end_time - self._session.start_time
        
        # 记录会话结束事件
        self.track_event(EventType.SESSION_END, {
            "duration": self._session.duration,
            "gold_net": self._session.gold_net,
            "kills": self._session.kills,
            "quests_completed": self._session.quests_completed
        })
        
        # 更新每日统计
        today = datetime.now().strftime("%Y-%m-%d")
        self._daily_stats[today]["sessions"] += 1
        self._daily_stats[today]["total_play_time"] += self._session.duration
        self._daily_stats[today]["total_gold_earned"] += self._session.gold_earned
        self._daily_stats[today]["total_gold_spent"] += self._session.gold_spent
        self._daily_stats[today]["total_kills"] += self._session.kills
        self._daily_stats[today]["total_deaths"] += self._session.deaths
        
        # 保存会话数据
        self._save_session()
        
        self._session = None
    
    def track_event(self, event_type: EventType, data: Dict[str, Any] = None):
        """追踪事件"""
        if data is None:
            data = {}
        
        event = AnalyticsEvent(
            event_type=event_type,
            timestamp=time.time(),
            session_id=self._session_id,
            character_id=self._current_character_id,
            character_level=self._current_character_level,
            data=data
        )
        
        self._events.append(event)
        self._process_event(event)
        
        # 定期保存
        if len(self._events) >= 100:
            self._save_events()
    
    def _process_event(self, event: AnalyticsEvent):
        """处理事件"""
        if not self._session:
            return
        
        if event.event_type == EventType.GOLD_EARN:
            self._session.gold_earned += event.data.get("amount", 0)
        
        elif event.event_type == EventType.GOLD_SPEND:
            self._session.gold_spent += event.data.get("amount", 0)
        
        elif event.event_type == EventType.ITEM_LOOT:
            self._session.items_looted += 1
        
        elif event.event_type == EventType.ITEM_SELL:
            self._session.items_sold += 1
        
        elif event.event_type == EventType.COMBAT_START:
            self._session.combats += 1
        
        elif event.event_type == EventType.CHARACTER_DEATH:
            self._session.deaths += 1
        
        elif event.event_type == EventType.DAMAGE_DEAL:
            self._session.damage_dealt += event.data.get("amount", 0)
            if event.data.get("killed", False):
                self._session.kills += 1
        
        elif event.event_type == EventType.DAMAGE_TAKE:
            self._session.damage_taken += event.data.get("amount", 0)
        
        elif event.event_type == EventType.SKILL_USE:
            self._session.skills_used += 1
        
        elif event.event_type == EventType.AREA_ENTER:
            self._session.areas_visited += 1
        
        elif event.event_type == EventType.WAYPOINT_UNLOCK:
            self._session.waypoints_unlocked += 1
        
        elif event.event_type == EventType.QUEST_START:
            self._session.quests_started += 1
        
        elif event.event_type == EventType.QUEST_COMPLETE:
            self._session.quests_completed += 1
        
        elif event.event_type == EventType.RIFT_ENTER:
            self._session.rifts_entered += 1
        
        elif event.event_type == EventType.RIFT_COMPLETE:
            self._session.rifts_completed += 1
            level = event.data.get("level", 0)
            if level > self._session.highest_rift_level:
                self._session.highest_rift_level = level
        
        elif event.event_type == EventType.CHARACTER_LEVEL_UP:
            self._session.character_level_end = event.data.get("level", self._session.character_level_end)
            self._current_character_level = self._session.character_level_end
    
    def _generate_session_id(self) -> str:
        """生成会话ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _save_session(self):
        """保存会话数据"""
        if not self._session:
            return
        
        filename = f"session_{self._session.session_id}.json"
        filepath = os.path.join(self.data_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                "session_id": self._session.session_id,
                "start_time": self._session.start_time,
                "end_time": self._session.end_time,
                "duration": self._session.duration,
                "character_id": self._session.character_id,
                "character_class": self._session.character_class,
                "character_level_start": self._session.character_level_start,
                "character_level_end": self._session.character_level_end,
                "gold_earned": self._session.gold_earned,
                "gold_spent": self._session.gold_spent,
                "items_looted": self._session.items_looted,
                "items_sold": self._session.items_sold,
                "combats": self._session.combats,
                "kills": self._session.kills,
                "deaths": self._session.deaths,
                "damage_dealt": self._session.damage_dealt,
                "damage_taken": self._session.damage_taken,
                "skills_used": self._session.skills_used,
                "areas_visited": self._session.areas_visited,
                "waypoints_unlocked": self._session.waypoints_unlocked,
                "quests_started": self._session.quests_started,
                "quests_completed": self._session.quests_completed,
                "rifts_entered": self._session.rifts_entered,
                "rifts_completed": self._session.rifts_completed,
                "highest_rift_level": self._session.highest_rift_level,
            }, f, indent=2, ensure_ascii=False)
    
    def _save_events(self):
        """保存事件数据"""
        if not self._events:
            return
        
        filename = f"events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.data_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump([e.to_dict() for e in self._events], f, indent=2, ensure_ascii=False)
        
        self._events.clear()
    
    def get_retention_report(self, days: int = 7) -> Dict[str, Any]:
        """获取留存报告"""
        report = {
            "period_days": days,
            "daily_active_users": [],
            "new_users": [],
            "retention_rates": {},
        }
        
        # 计算每日活跃用户
        for player_id, sessions in self._player_sessions.items():
            unique_days = list(set(sessions))
            for day in unique_days:
                stats = self._daily_stats.get(day, {})
                stats["active_players"] = stats.get("active_players", set())
                stats["active_players"].add(player_id)
        
        # 生成报告
        sorted_days = sorted(self._daily_stats.keys())[-days:]
        
        for day in sorted_days:
            stats = self._daily_stats[day]
            report["daily_active_users"].append({
                "date": day,
                "sessions": stats["sessions"],
                "new_characters": stats["new_characters"],
                "play_time_avg": stats["total_play_time"] / max(1, stats["sessions"])
            })
        
        return report
    
    def get_economy_report(self) -> Dict[str, Any]:
        """获取经济报告"""
        total_earned = sum(s["total_gold_earned"] for s in self._daily_stats.values())
        total_spent = sum(s["total_gold_spent"] for s in self._daily_stats.values())
        
        return {
            "total_gold_earned": total_earned,
            "total_gold_spent": total_spent,
            "gold_flow": total_earned - total_spent,
            "daily_stats": dict(self._daily_stats)
        }
    
    def get_combat_report(self) -> Dict[str, Any]:
        """获取战斗报告"""
        total_kills = sum(s["total_kills"] for s in self._daily_stats.values())
        total_deaths = sum(s["total_deaths"] for s in self._daily_stats.values())
        
        return {
            "total_kills": total_kills,
            "total_deaths": total_deaths,
            "kd_ratio": total_kills / max(1, total_deaths),
            "daily_stats": {
                day: {
                    "kills": stats["total_kills"],
                    "deaths": stats["total_deaths"]
                }
                for day, stats in self._daily_stats.items()
            }
        }
    
    def get_current_session_stats(self) -> Optional[SessionStats]:
        """获取当前会话统计"""
        return self._session
    
    def generate_summary(self) -> str:
        """生成摘要报告"""
        lines = []
        lines.append("=" * 50)
        lines.append("游戏数据分析报告")
        lines.append("=" * 50)
        
        if self._session:
            lines.append(f"\n当前会话:")
            lines.append(f"  时长: {self._session.duration:.1f}秒")
            lines.append(f"  金币净收入: {self._session.gold_net}")
            lines.append(f"  击杀: {self._session.kills}")
            lines.append(f"  死亡: {self._session.deaths}")
            lines.append(f"  完成任务: {self._session.quests_completed}")
        
        economy = self.get_economy_report()
        lines.append(f"\n经济统计:")
        lines.append(f"  总收入: {economy['total_gold_earned']}")
        lines.append(f"  总支出: {economy['total_gold_spent']}")
        
        combat = self.get_combat_report()
        lines.append(f"\n战斗统计:")
        lines.append(f"  总击杀: {combat['total_kills']}")
        lines.append(f"  总死亡: {combat['total_deaths']}")
        lines.append(f"  K/D比: {combat['kd_ratio']:.2f}")
        
        lines.append("\n" + "=" * 50)
        
        return "\n".join(lines)


# 全局分析管理器
_analytics_manager: Optional[AnalyticsManager] = None


def get_analytics() -> AnalyticsManager:
    """获取分析管理器"""
    global _analytics_manager
    if _analytics_manager is None:
        _analytics_manager = AnalyticsManager()
    return _analytics_manager


def track_event(event_type: EventType, data: Dict[str, Any] = None):
    """便捷追踪事件函数"""
    get_analytics().track_event(event_type, data)
