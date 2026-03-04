"""
传送点管理器系统
"""
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

import pygame

class WaypointState(Enum):
    LOCKED = "locked"
    ACTIVE = "active"
    DISCOVERED = "discovered"


@dataclass
class Waypoint:
    id: str
    name: str
    area_id: str
    position: Tuple[float, float]
    state: WaypointState = WaypointState.LOCKED
    required_level: int = 1
    required_quest: Optional[str] = None
    description: str = ""
    
    def can_activate(self, player_level: int, completed_quests: Set[str]) -> Tuple[bool, str]:
        if self.state != WaypointState.LOCKED:
            return False, "传送点已激活"
        
        if player_level < self.required_level:
            return False, f"需要等级 {self.required_level}"
        
        if self.required_quest and self.required_quest not in completed_quests:
            return False, "需要完成前置任务"
        
        return True, ""
    
    def activate(self):
        self.state = WaypointState.ACTIVE
    
    def is_active(self) -> bool:
        return self.state == WaypointState.ACTIVE


class WaypointManager:
    def __init__(self):
        self.waypoints: Dict[str, Waypoint] = {}
        self.discovered_waypoints: Set[str] = set()
        
        self._create_default_waypoints()
    
    def _create_default_waypoints(self):
        default_waypoints = [
            Waypoint(
                id="wp_tristram",
                name="新崔斯特姆",
                area_id="tristram",
                position=(25.0, 25.0),
                state=WaypointState.ACTIVE,
                required_level=1,
                description="冒险者的起点"
            ),
            Waypoint(
                id="wp_weald",
                name="腐化林地入口",
                area_id="weald",
                position=(10.0, 100.0),
                required_level=2,
                description="被腐化的森林"
            ),
            Waypoint(
                id="wp_cathedral",
                name="大教堂入口",
                area_id="cathedral",
                position=(10.0, 75.0),
                required_level=5,
                description="古老的教堂"
            ),
            Waypoint(
                id="wp_oasis",
                name="卡尔蒂姆绿洲",
                area_id="oasis",
                position=(90.0, 10.0),
                required_level=12,
                description="沙漠中的绿洲"
            ),
            Waypoint(
                id="wp_desert",
                name="卡尔蒂姆沙漠",
                area_id="desert",
                position=(125.0, 10.0),
                required_level=15,
                description="无尽的沙漠"
            ),
            Waypoint(
                id="wp_caldeum",
                name="卡尔蒂姆城",
                area_id="caldeum_city",
                position=(30.0, 30.0),
                required_level=15,
                description="沙漠中的繁华城市"
            ),
            Waypoint(
                id="wp_highlands",
                name="亚瑞特高地",
                area_id="highlands",
                position=(100.0, 10.0),
                required_level=25,
                description="通往山脉的高地"
            ),
            Waypoint(
                id="wp_snow",
                name="亚瑞特山脉",
                area_id="snow",
                position=(100.0, 10.0),
                required_level=30,
                description="冰雪覆盖的山脉"
            ),
            Waypoint(
                id="wp_ice_caves",
                name="冰霜洞穴",
                area_id="ice_caves",
                position=(10.0, 70.0),
                required_level=32,
                description="永冻的洞穴"
            ),
            Waypoint(
                id="wp_mountain_peak",
                name="亚瑞特山顶",
                area_id="mountain_peak",
                position=(60.0, 100.0),
                required_level=40,
                description="山脉的最高点"
            ),
            Waypoint(
                id="wp_hell_gate",
                name="地狱之门",
                area_id="hell_gate",
                position=(50.0, 90.0),
                required_level=45,
                description="通往地狱的入口"
            ),
            Waypoint(
                id="wp_hell",
                name="地狱入口",
                area_id="hell",
                position=(150.0, 10.0),
                required_level=50,
                description="燃烧的地狱"
            ),
            Waypoint(
                id="wp_hell_depths",
                name="地狱深渊",
                area_id="hell_depths",
                position=(90.0, 10.0),
                required_level=55,
                description="地狱的最深处"
            ),
            Waypoint(
                id="wp_diablo_lair",
                name="恐惧领地",
                area_id="diablo_lair",
                position=(75.0, 10.0),
                required_level=65,
                required_quest="main_quest_4",
                description="迪亚波罗的领地"
            ),
        ]
        
        for wp in default_waypoints:
            self.waypoints[wp.id] = wp
    
    def get_waypoint(self, waypoint_id: str) -> Optional[Waypoint]:
        return self.waypoints.get(waypoint_id)
    
    def get_waypoint_in_area(self, area_id: str) -> Optional[Waypoint]:
        for wp in self.waypoints.values():
            if wp.area_id == area_id:
                return wp
        return None
    
    def get_active_waypoints(self) -> List[Waypoint]:
        return [wp for wp in self.waypoints.values() if wp.is_active()]
    
    def get_available_waypoints(self, player_level: int, completed_quests: Set[str]) -> List[Waypoint]:
        available = []
        for wp in self.waypoints.values():
            if wp.is_active():
                available.append(wp)
            elif wp.can_activate(player_level, completed_quests)[0]:
                available.append(wp)
        return available
    
    def activate_waypoint(self, waypoint_id: str, player_level: int, 
                          completed_quests: Set[str]) -> Tuple[bool, str]:
        wp = self.waypoints.get(waypoint_id)
        if not wp:
            return False, "传送点不存在"
        
        if wp.is_active():
            return True, "传送点已激活"
        
        can_activate, reason = wp.can_activate(player_level, completed_quests)
        if not can_activate:
            return False, reason
        
        wp.activate()
        self.discovered_waypoints.add(waypoint_id)
        return True, f"激活了传送点: {wp.name}"
    
    def discover_waypoint(self, waypoint_id: str) -> bool:
        wp = self.waypoints.get(waypoint_id)
        if not wp:
            return False
        
        if wp.state == WaypointState.LOCKED:
            wp.state = WaypointState.DISCOVERED
            self.discovered_waypoints.add(waypoint_id)
            return True
        return False
    
    def teleport_to(self, waypoint_id: str) -> Tuple[bool, str, Optional[Tuple[str, Tuple[float, float]]]]:
        wp = self.waypoints.get(waypoint_id)
        if not wp:
            return False, "传送点不存在", None
        
        if not wp.is_active():
            return False, "传送点未激活", None
        
        return True, f"传送到 {wp.name}", (wp.area_id, wp.position)
    
    def can_teleport_to(self, waypoint_id: str) -> bool:
        wp = self.waypoints.get(waypoint_id)
        return wp is not None and wp.is_active()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "discovered_waypoints": list(self.discovered_waypoints),
            "waypoint_states": {
                wp_id: wp.state.value for wp_id, wp in self.waypoints.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WaypointManager':
        manager = cls()
        
        manager.discovered_waypoints = set(data.get("discovered_waypoints", []))
        
        waypoint_states = data.get("waypoint_states", {})
        for wp_id, state_value in waypoint_states.items():
            if wp_id in manager.waypoints:
                manager.waypoints[wp_id].state = WaypointState(state_value)
        
        return manager


class WaypointUI:
    def __init__(self, waypoint_manager: WaypointManager):
        self.waypoint_manager = waypoint_manager
        self.visible = False
        self.selected_waypoint_id: Optional[str] = None
        self._last_layout: Dict[str, Any] = {}
    
    def toggle(self):
        self.visible = not self.visible
    
    def show(self):
        self.visible = True
    
    def hide(self):
        self.visible = False
    
    def update(self, player_level: int, completed_quests: Set[str]):
        self._player_level = player_level
        self._completed_quests = completed_quests
    
    def get_available_destinations(self) -> List[Waypoint]:
        return self.waypoint_manager.get_active_waypoints()
    
    def select_waypoint(self, waypoint_id: str):
        if self.waypoint_manager.can_teleport_to(waypoint_id):
            self.selected_waypoint_id = waypoint_id
            return True
        return False
    
    def confirm_teleport(self) -> Tuple[bool, str, Optional[Tuple[str, Tuple[float, float]]]]:
        if not self.selected_waypoint_id:
            return False, "未选择传送点", None
        
        result = self.waypoint_manager.teleport_to(self.selected_waypoint_id)
        self.selected_waypoint_id = None
        self.visible = False
        return result

    def get_layout(self, surface: pygame.Surface) -> Dict[str, Any]:
        panel_width = 420
        panel_height = 420
        panel_x = (surface.get_width() - panel_width) // 2
        panel_y = (surface.get_height() - panel_height) // 2
        entries = []
        waypoints = self.get_available_destinations()
        item_h = 44
        for i, wp in enumerate(waypoints):
            rect = pygame.Rect(panel_x + 24, panel_y + 74 + i * item_h, panel_width - 48, item_h - 6)
            entries.append((wp, rect))
        confirm_rect = pygame.Rect(panel_x + 80, panel_y + panel_height - 58, 110, 36)
        close_rect = pygame.Rect(panel_x + panel_width - 190, panel_y + panel_height - 58, 110, 36)
        layout = {
            "panel": pygame.Rect(panel_x, panel_y, panel_width, panel_height),
            "entries": entries,
            "confirm": confirm_rect,
            "close": close_rect
        }
        self._last_layout = layout
        return layout

    def render(self, surface: pygame.Surface):
        if not self.visible:
            return
        layout = self.get_layout(surface)
        panel = pygame.Surface((layout["panel"].width, layout["panel"].height), pygame.SRCALPHA)
        pygame.draw.rect(panel, (20, 26, 40, 230), (0, 0, layout["panel"].width, layout["panel"].height), border_radius=14)
        pygame.draw.rect(panel, (110, 150, 210), (0, 0, layout["panel"].width, layout["panel"].height), 2, border_radius=14)
        pygame.draw.rect(panel, (36, 58, 92, 240), (0, 0, layout["panel"].width, 48), border_top_left_radius=14, border_top_right_radius=14)

        title_font = pygame.font.SysFont("Microsoft YaHei UI", 24, bold=True)
        body_font = pygame.font.SysFont("Microsoft YaHei UI", 16)
        small_font = pygame.font.SysFont("Microsoft YaHei UI", 14)
        panel.blit(title_font.render("传送地图", True, (230, 236, 252)), (14, 8))

        for wp, rect in layout["entries"]:
            local_rect = rect.move(-layout["panel"].x, -layout["panel"].y)
            selected = self.selected_waypoint_id == wp.id
            row_color = (58, 78, 108) if selected else (36, 44, 62)
            pygame.draw.rect(panel, row_color, local_rect, border_radius=8)
            if selected:
                pygame.draw.rect(panel, (132, 202, 255), local_rect, 2, border_radius=8)
            panel.blit(body_font.render(wp.name, True, (220, 228, 242)), (local_rect.x + 10, local_rect.y + 6))
            panel.blit(small_font.render(f"等级 {wp.required_level}", True, (166, 178, 196)), (local_rect.x + 12, local_rect.y + 24))

        confirm_rect = layout["confirm"].move(-layout["panel"].x, -layout["panel"].y)
        close_rect = layout["close"].move(-layout["panel"].x, -layout["panel"].y)
        pygame.draw.rect(panel, (60, 110, 84), confirm_rect, border_radius=8)
        pygame.draw.rect(panel, (110, 66, 66), close_rect, border_radius=8)
        panel.blit(body_font.render("传送", True, (240, 248, 240)), (confirm_rect.x + 30, confirm_rect.y + 8))
        panel.blit(body_font.render("关闭", True, (248, 236, 236)), (close_rect.x + 30, close_rect.y + 8))
        surface.blit(panel, (layout["panel"].x, layout["panel"].y))
