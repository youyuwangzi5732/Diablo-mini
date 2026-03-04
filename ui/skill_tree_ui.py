"""
技能树UI - 商业化级别的可视化界面
"""
from typing import Dict, List, Optional, Any, Tuple
import pygame
import math

from .font_manager import get_font

from .ui_element import UIElement, UIButton, UILabel, UIPanel
from .ui_manager import UIManager
from .ui_theme import draw_panel, font as ui_font, line_height, ui


class SkillNodeRenderer:
    """技能节点渲染器"""
    
    NODE_COLORS = {
        'skill': {'bg': (40, 60, 100), 'border': (80, 120, 200), 'active': (100, 150, 255)},
        'passive': {'bg': (60, 40, 80), 'border': (120, 80, 180), 'active': (150, 100, 220)},
        'attribute': {'bg': (40, 70, 50), 'border': (80, 140, 100), 'active': (100, 200, 130)},
        'keystone': {'bg': (80, 60, 30), 'border': (200, 150, 50), 'active': (255, 200, 80)},
    }
    
    def __init__(self, x: int, y: int, size: int = 40):
        self.x = x
        self.y = y
        self.size = size
        self.is_hovered = False
        self.animation_time = 0.0
        self.pulse_phase = 0.0
    
    def update(self, delta_time: float):
        self.animation_time += delta_time
        self.pulse_phase = math.sin(self.animation_time * 3) * 0.5 + 0.5
    
    def render(self, surface: pygame.Surface, node: Any, is_allocated: bool):
        """渲染技能节点"""
        node_type = getattr(node, 'node_type', None)
        type_name = node_type.value if hasattr(node_type, 'value') else str(node_type) if node_type else 'skill'
        
        colors = self.NODE_COLORS.get(type_name, self.NODE_COLORS['skill'])
        
        # 计算节点大小（悬停时放大）
        render_size = self.size
        if self.is_hovered:
            render_size = int(self.size * 1.15)
        
        # 绘制外发光效果（激活状态）
        if is_allocated:
            glow_radius = int(render_size * 0.8)
            glow_alpha = int(100 + 50 * self.pulse_phase)
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            glow_color = (*colors['active'], glow_alpha)
            pygame.draw.circle(glow_surface, glow_color, (glow_radius, glow_radius), glow_radius)
            surface.blit(glow_surface, (self.x - glow_radius, self.y - glow_radius), special_flags=pygame.BLEND_RGBA_ADD)
        
        # 绘制节点背景
        bg_color = colors['active'] if is_allocated else colors['bg']
        pygame.draw.circle(surface, bg_color, (self.x, self.y), render_size // 2)
        
        # 绘制节点边框
        border_color = colors['border']
        if self.is_hovered:
            border_color = (255, 255, 255)
        pygame.draw.circle(surface, border_color, (self.x, self.y), render_size // 2, 3)
        
        # 绘制节点图标/名称
        self._render_node_content(surface, node, render_size)
        
        # 绘制等级指示器
        current_pts = getattr(node, 'current_points', 0)
        max_pts = getattr(node, 'max_points', 1)
        if max_pts > 1:
            self._render_points_indicator(surface, current_pts, max_pts, render_size)
    
    def _render_node_content(self, surface: pygame.Surface, node: Any, size: int):
        """渲染节点内容"""
        name = getattr(node, 'name', '?')
        icon = getattr(node, 'icon', None)
        
        if icon:
            # 如果有图标，渲染图标
            pass
        else:
            # 渲染名称首字
            font = get_font(14)
            display_name = name[:2] if len(name) > 2 else name
            text = font.render(display_name, True, (255, 255, 255))
            text_x = self.x - text.get_width() // 2
            text_y = self.y - text.get_height() // 2
            surface.blit(text, (text_x, text_y))
    
    def _render_points_indicator(self, surface: pygame.Surface, current: int, maximum: int, size: int):
        """渲染点数指示器"""
        font = get_font(10)
        text = font.render(f"{current}/{maximum}", True, (200, 200, 200))
        text_x = self.x - text.get_width() // 2
        text_y = self.y + size // 2 + 2
        surface.blit(text, (text_x, text_y))
    
    def contains_point(self, pos: Tuple[int, int]) -> bool:
        """检查点是否在节点内"""
        dx = pos[0] - self.x
        dy = pos[1] - self.y
        return (dx * dx + dy * dy) <= (self.size // 2) ** 2


class SkillTreeUI:
    def __init__(self, ui_manager: UIManager):
        self.ui_manager = ui_manager
        self.screen_width = ui_manager.screen_width
        self.screen_height = ui_manager.screen_height
        
        self.visible = False
        
        self.base_panel_width = 900
        self.base_panel_height = 650
        self.panel_width = self.base_panel_width
        self.panel_height = self.base_panel_height
        
        self.skill_tree: Optional[Any] = None
        self.character: Optional[Any] = None
        
        self.scroll_offset = (0, 0)
        self.node_size = 44
        self.hovered_node: Optional[str] = None
        self.selected_node: Optional[str] = None
        
        # 节点渲染器缓存
        self._node_renderers: Dict[str, SkillNodeRenderer] = {}
        
        # 动画
        self._animation_time = 0.0
        
        # 当前选中的分支标签
        self._selected_branch: Optional[str] = None
    
    def toggle(self):
        self.visible = not self.visible
    
    def set_skill_tree(self, skill_tree: Any, character: Any):
        self.skill_tree = skill_tree
        self.character = character
        self._update_node_renderers()
    
    def _update_node_renderers(self):
        """更新节点渲染器"""
        if not self.skill_tree:
            return
        
        nodes = getattr(self.skill_tree, 'nodes', {})
        self._node_renderers.clear()
        
        for node_id, node in nodes.items():
            pos = getattr(node, 'position', (0, 0))
            x = ui(450) + pos[0] * ui(70)
            y = ui(80) + pos[1] * ui(70)
            
            renderer = SkillNodeRenderer(x, y, self.node_size)
            self._node_renderers[node_id] = renderer
    
    def get_panel_position(self) -> tuple:
        x = (self.screen_width - self.panel_width) // 2
        y = (self.screen_height - self.panel_height) // 2
        return (x, y)

    def _apply_ui_scale(self):
        self.panel_width = ui(self.base_panel_width)
        self.panel_height = ui(self.base_panel_height)
        self.node_size = ui(44)
    
    def update(self, delta_time: float):
        self._animation_time += delta_time
        
        for renderer in self._node_renderers.values():
            renderer.update(delta_time)
    
    def render(self, surface: pygame.Surface):
        if not self.visible:
            return
        self._apply_ui_scale()
        self._update_node_renderers()
        
        panel_x, panel_y = self.get_panel_position()
        
        panel_surface = pygame.Surface(
            (self.panel_width, self.panel_height),
            pygame.SRCALPHA
        )
        draw_panel(panel_surface, self.panel_width, self.panel_height, "技能树", "圆角一体化视图")
        
        self._render_header(panel_surface)
        self._render_branch_tabs(panel_surface)
        self._render_tree(panel_surface)
        self._render_node_details(panel_surface)
        self._render_legend(panel_surface)
        
        surface.blit(panel_surface, (panel_x, panel_y))
    
    def _render_header(self, surface: pygame.Surface):
        font = ui_font("section", bold=True)
        
        # 标题
        title = font.render("技能树", True, (255, 220, 100))
        surface.blit(title, (ui(20), ui(14)))
        
        # 可用点数
        if self.skill_tree:
            points = getattr(self.skill_tree, 'available_points', 0)
            points_color = (100, 255, 100) if points > 0 else (150, 150, 150)
            points_text = font.render(f"可用点数: {points}", True, points_color)
            surface.blit(points_text, (self.panel_width - ui(200), ui(14)))
            
            # 已分配点数
            allocated = getattr(self.skill_tree, 'allocated_points', 0)
            small_font = ui_font("small")
            alloc_text = small_font.render(f"已分配: {allocated}", True, (180, 180, 180))
            surface.blit(alloc_text, (self.panel_width - ui(200), ui(38)))
    
    def _render_branch_tabs(self, surface: pygame.Surface):
        """渲染分支标签"""
        if not self.skill_tree:
            return
        
        branches = getattr(self.skill_tree, 'branches', {})
        if not branches:
            return
        
        tab_width = ui(100)
        tab_height = ui(30)
        start_x = ui(20)
        y = ui(50)
        
        font = ui_font("small")
        
        for i, (branch_id, branch) in enumerate(branches.items()):
            x = start_x + i * (tab_width + ui(5))
            
            # 标签背景
            is_selected = self._selected_branch == branch_id
            bg_color = (60, 60, 80) if is_selected else (40, 40, 50)
            border_color = (150, 150, 200) if is_selected else (80, 80, 100)
            
            pygame.draw.rect(surface, bg_color, (x, y, tab_width, tab_height), border_radius=5)
            pygame.draw.rect(surface, border_color, (x, y, tab_width, tab_height), 2, border_radius=5)
            
            # 标签文字
            branch_name = getattr(branch, 'name', branch_id)
            text = font.render(branch_name[:6], True, (200, 200, 200))
            text_x = x + (tab_width - text.get_width()) // 2
            text_y = y + (tab_height - text.get_height()) // 2
            surface.blit(text, (text_x, text_y))
    
    def _render_tree(self, surface: pygame.Surface):
        if not self.skill_tree:
            return
        
        # 创建树视图表面
        tree_rect = pygame.Rect(ui(20), ui(90), self.panel_width - ui(40), self.panel_height - ui(230))
        tree_surface = pygame.Surface((tree_rect.width, tree_rect.height), pygame.SRCALPHA)
        tree_surface.fill((20, 20, 25, 200))
        
        nodes = getattr(self.skill_tree, 'nodes', {})
        
        # 先绘制连接线
        for node_id, node in nodes.items():
            connections = getattr(node, 'connections', [])
            for conn_id in connections:
                if conn_id in nodes:
                    self._render_connection(tree_surface, node, nodes[conn_id])
        
        # 再绘制节点
        for node_id, node in nodes.items():
            renderer = self._node_renderers.get(node_id)
            if renderer:
                # 调整坐标到树视图本地坐标
                local_renderer = SkillNodeRenderer(
                    renderer.x - tree_rect.x,
                    renderer.y - tree_rect.y,
                    renderer.size
                )
                local_renderer.is_hovered = renderer.is_hovered
                local_renderer.animation_time = renderer.animation_time
                local_renderer.pulse_phase = renderer.pulse_phase
                
                is_allocated = getattr(node, 'allocated', False)
                local_renderer.render(tree_surface, node, is_allocated)
        
        surface.blit(tree_surface, (tree_rect.x, tree_rect.y))
        
        # 绘制边框
        pygame.draw.rect(surface, (80, 80, 100), tree_rect, 2, border_radius=5)
    
    def _render_connection(self, surface: pygame.Surface, node1: Any, node2: Any):
        """渲染节点连接线"""
        pos1 = getattr(node1, 'position', (0, 0))
        pos2 = getattr(node2, 'position', (0, 0))
        
        # 计算屏幕坐标
        tree_rect = pygame.Rect(ui(20), ui(90), self.panel_width - ui(40), self.panel_height - ui(230))
        
        x1 = ui(450) - tree_rect.x + pos1[0] * ui(70)
        y1 = ui(80) - tree_rect.y + pos1[1] * ui(70)
        x2 = ui(450) - tree_rect.x + pos2[0] * ui(70)
        y2 = ui(80) - tree_rect.y + pos2[1] * ui(70)
        
        allocated1 = getattr(node1, 'allocated', False)
        allocated2 = getattr(node2, 'allocated', False)
        
        # 连接线颜色
        if allocated1 and allocated2:
            color = (100, 150, 255)
            # 添加发光效果
            glow_surface = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
            pygame.draw.line(glow_surface, (*color, 100), (x1, y1), (x2, y2), 6)
            surface.blit(glow_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        else:
            color = (50, 50, 60)
        
        # 绘制连接线
        pygame.draw.line(surface, color, (x1, y1), (x2, y2), 3)
    
    def _render_node_details(self, surface: pygame.Surface):
        if not self.hovered_node or not self.skill_tree:
            return
        
        node = getattr(self.skill_tree, 'nodes', {}).get(self.hovered_node)
        if not node:
            return
        
        detail_y = self.panel_height - ui(130)
        
        # 背景框
        detail_rect = pygame.Rect(ui(20), detail_y - ui(10), self.panel_width - ui(40), ui(120))
        pygame.draw.rect(surface, (30, 30, 40, 200), detail_rect, border_radius=5)
        pygame.draw.rect(surface, (80, 80, 100), detail_rect, 1, border_radius=5)
        
        font = ui_font("body", bold=True)
        font_small = ui_font("small")
        
        # 节点名称
        name = getattr(node, 'name', '未知')
        node_type = getattr(node, 'node_type', None)
        type_name = node_type.value if hasattr(node_type, 'value') else str(node_type) if node_type else ''
        
        name_text = font.render(f"[{type_name}] {name}", True, (255, 220, 100))
        surface.blit(name_text, (ui(30), detail_y))
        
        # 描述
        description = getattr(node, 'description', '')
        if description:
            desc_text = font_small.render(description, True, (180, 180, 180))
            surface.blit(desc_text, (ui(30), detail_y + line_height("small")))
        
        # 点数
        current = getattr(node, 'current_points', 0)
        max_pts = getattr(node, 'max_points', 1)
        points_text = font_small.render(f"点数: {current}/{max_pts}", True, (200, 200, 200))
        surface.blit(points_text, (ui(30), detail_y + line_height("small") * 2))
        
        # 效果
        effects = getattr(node, 'effects', {})
        if effects:
            y_offset = detail_y + line_height("small") * 3
            for attr, value in effects.items():
                effect_text = font_small.render(f"+{value} {attr}", True, (100, 255, 100))
                surface.blit(effect_text, (ui(40), y_offset))
                y_offset += line_height("small")
        
        # 需求
        requirements = getattr(node, 'requirements', {})
        if requirements:
            req_x = self.panel_width - ui(200)
            req_y = detail_y
            
            req_title = font_small.render("需求:", True, (200, 150, 100))
            surface.blit(req_title, (req_x, req_y))
            
            for req_name, req_value in requirements.items():
                req_y += line_height("small")
                req_text = font_small.render(f"{req_name}: {req_value}", True, (150, 150, 150))
                surface.blit(req_text, (req_x + ui(10), req_y))
    
    def _render_legend(self, surface: pygame.Surface):
        """渲染图例"""
        legend_x = self.panel_width - ui(180)
        legend_y = ui(50)
        
        font = ui_font("small")
        
        legend_items = [
            ("技能", (100, 150, 255)),
            ("被动", (150, 100, 220)),
            ("属性", (100, 200, 130)),
            ("核心", (255, 200, 80)),
        ]
        
        for i, (name, color) in enumerate(legend_items):
            y = legend_y + i * ui(18)
            
            # 绘制小圆点
            pygame.draw.circle(surface, color, (legend_x, y + ui(6)), ui(5))
            
            # 绘制名称
            text = font.render(name, True, (180, 180, 180))
            surface.blit(text, (legend_x + ui(12), y))
    
    def handle_click(self, pos: tuple) -> bool:
        if not self.visible:
            return False
        
        panel_x, panel_y = self.get_panel_position()
        local_pos = (pos[0] - panel_x, pos[1] - panel_y)
        
        # 检查分支标签点击
        if self._handle_branch_tab_click(local_pos):
            return True
        
        if self._handle_node_click(local_pos):
            return True
        
        return True
    
    def _handle_branch_tab_click(self, local_pos: tuple) -> bool:
        """处理分支标签点击"""
        if not self.skill_tree:
            return False
        
        branches = getattr(self.skill_tree, 'branches', {})
        if not branches:
            return False
        
        tab_width = ui(100)
        tab_height = ui(30)
        start_x = ui(20)
        y = ui(50)
        
        for i, branch_id in enumerate(branches.keys()):
            x = start_x + i * (tab_width + ui(5))
            
            if x <= local_pos[0] <= x + tab_width and y <= local_pos[1] <= y + tab_height:
                self._selected_branch = branch_id
                return True
        
        return False
    
    def _handle_node_click(self, local_pos: tuple) -> bool:
        if not self.skill_tree:
            return False
        
        nodes = getattr(self.skill_tree, 'nodes', {})
        
        for node_id, node in nodes.items():
            renderer = self._node_renderers.get(node_id)
            if renderer and renderer.contains_point(local_pos):
                if self.character and self.skill_tree:
                    character_level = getattr(self.character, 'level', 1)
                    character_class = getattr(self.character, 'class_id', None)
                    
                    success, message = self.skill_tree.allocate_node(
                        node_id, character_level, character_class
                    )
                    
                    if not success and message:
                        self.ui_manager.add_notification(message, (255, 100, 100))
                    elif success:
                        self.ui_manager.add_notification("技能点已分配", (100, 255, 100))
                
                return True
        
        return False
    
    def handle_motion(self, pos: tuple):
        if not self.visible or not self.skill_tree:
            return
        
        panel_x, panel_y = self.get_panel_position()
        local_pos = (pos[0] - panel_x, pos[1] - panel_y)
        
        nodes = getattr(self.skill_tree, 'nodes', {})
        self.hovered_node = None
        
        for node_id, renderer in self._node_renderers.items():
            is_hovered = renderer.contains_point(local_pos)
            renderer.is_hovered = is_hovered
            
            if is_hovered:
                self.hovered_node = node_id
    
    def resize(self, width: int, height: int):
        self.screen_width = width
        self.screen_height = height
        self._node_renderers.clear()
