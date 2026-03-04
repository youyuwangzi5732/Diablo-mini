"""
背包UI - 商业化级别的物品拖拽和提示系统
"""
from typing import Dict, List, Optional, Any, Tuple, Callable
import pygame

from .ui_manager import UIManager
from config.game_config import ColorConfig, EquipmentConfig
from .ui_theme import draw_panel, font as ui_font, ui


class DragState:
    """拖拽状态"""
    NONE = 0
    DRAGGING = 1
    SWAPPING = 2


class ItemTooltip:
    """物品提示框"""
    
    RARITY_COLORS = {
        0: (200, 200, 200),      # 普通 - 白色
        1: (100, 150, 255),      # 魔法 - 蓝色
        2: (255, 200, 50),       # 稀有 - 黄色
        3: (255, 150, 50),       # 传奇 - 橙色
        4: (0, 255, 100),        # 套装 - 绿色
        5: (200, 100, 255),      # 合成 - 紫色
    }
    
    AFFIX_COLORS = {
        "positive": (100, 255, 100),
        "negative": (255, 100, 100),
        "neutral": (200, 200, 200),
        "special": (255, 200, 100),
        "set": (0, 255, 100),
    }
    
    def __init__(self):
        self.visible = False
        self.item = None
        self.position = (0, 0)
        self.width = 280
        self.line_height = 18
        self.padding = 10
    
    def show(self, item: Any, position: Tuple[int, int]):
        self.visible = True
        self.item = item
        self.position = position
    
    def hide(self):
        self.visible = False
        self.item = None
    
    def render(self, surface: pygame.Surface):
        if not self.visible or not self.item:
            return
        
        item = self.item
        
        # 计算提示框高度
        lines = self._build_tooltip_lines(item)
        height = len(lines) * self.line_height + self.padding * 2 + 20
        
        # 调整位置避免超出屏幕
        x, y = self.position
        if x + self.width > surface.get_width():
            x = surface.get_width() - self.width - 10
        if y + height > surface.get_height():
            y = y - height - 10
        
        # 绘制背景
        tooltip_surface = pygame.Surface((self.width, height), pygame.SRCALPHA)
        
        # 边框颜色根据稀有度
        rarity = getattr(item, 'rarity', None)
        rarity_value = rarity.value if hasattr(rarity, 'value') else (rarity or 0)
        border_color = self.RARITY_COLORS.get(rarity_value, (150, 150, 150))
        
        # 背景
        pygame.draw.rect(tooltip_surface, (20, 20, 25, 240), (0, 0, self.width, height))
        pygame.draw.rect(tooltip_surface, border_color, (0, 0, self.width, height), 2)
        
        # 渲染内容
        y_offset = self.padding
        for line_type, line_text, line_color in lines:
            font = ui_font("small")
            text_surface = font.render(line_text, True, line_color)
            tooltip_surface.blit(text_surface, (self.padding, y_offset))
            y_offset += self.line_height
        
        surface.blit(tooltip_surface, (x + 15, y + 15))
    
    def _build_tooltip_lines(self, item: Any) -> List[Tuple[str, str, Tuple[int, int, int]]]:
        """构建提示框内容行"""
        lines = []
        
        # 物品名称
        name = getattr(item, 'name', '未知物品')
        rarity = getattr(item, 'rarity', None)
        rarity_value = rarity.value if hasattr(rarity, 'value') else (rarity or 0)
        name_color = self.RARITY_COLORS.get(rarity_value, (255, 255, 255))
        lines.append(("name", name, name_color))
        
        # 物品类型
        item_type = getattr(item, 'item_type', None)
        if item_type:
            type_name = getattr(item_type, 'name', str(item_type))
            type_names = {
                "WEAPON": "武器",
                "ARMOR": "护甲",
                "ACCESSORY": "饰品",
                "POTION": "药水",
                "GEM": "宝石",
                "RUNE": "符文",
                "MATERIAL": "材料"
            }
            lines.append(("type", type_names.get(type_name, type_name), (150, 150, 150)))
        
        # 基础属性
        if hasattr(item, 'base_armor') and item.base_armor:
            lines.append(("armor", f"护甲: {item.base_armor}", (200, 200, 200)))
        
        if hasattr(item, 'base_damage') and item.base_damage:
            dmg_min = getattr(item, 'damage_min', item.base_damage)
            dmg_max = getattr(item, 'damage_max', item.base_damage)
            lines.append(("damage", f"伤害: {dmg_min}-{dmg_max}", (200, 200, 200)))
        
        # 攻击速度
        if hasattr(item, 'attack_speed') and item.attack_speed:
            lines.append(("speed", f"攻击速度: {item.attack_speed:.2f}", (150, 150, 150)))
        
        # 词缀
        affixes = getattr(item, 'affixes', [])
        if affixes:
            lines.append(("separator", "─" * 20, (80, 80, 80)))
            for affix in affixes[:6]:  # 最多显示6个词缀
                affix_name = getattr(affix, 'name', str(affix))
                affix_value = getattr(affix, 'value', '')
                if affix_value:
                    lines.append(("affix", f"+{affix_value} {affix_name}", (100, 255, 100)))
                else:
                    lines.append(("affix", affix_name, (100, 255, 100)))
        
        # 宝石插槽
        sockets = getattr(item, 'sockets', [])
        if sockets:
            lines.append(("separator", "─" * 20, (80, 80, 80)))
            socket_count = len(sockets)
            filled_count = sum(1 for s in sockets if s is not None)
            lines.append(("sockets", f"插槽: {filled_count}/{socket_count}", (200, 200, 200)))
        
        # 套装信息
        set_name = getattr(item, 'set_name', None)
        if set_name:
            lines.append(("separator", "─" * 20, (80, 80, 80)))
            lines.append(("set", f"套装: {set_name}", (0, 255, 100)))
        
        # 需求等级
        req_level = getattr(item, 'required_level', 1)
        lines.append(("separator", "─" * 20, (80, 80, 80)))
        lines.append(("level", f"需要等级: {req_level}", (180, 180, 180)))
        
        # 物品等级
        item_level = getattr(item, 'item_level', 1)
        lines.append(("ilvl", f"物品等级: {item_level}", (150, 150, 150)))
        
        return lines


class InventoryUI:
    def __init__(self, ui_manager: UIManager):
        self.ui_manager = ui_manager
        self.screen_width = ui_manager.screen_width
        self.screen_height = ui_manager.screen_height
        
        self.visible = False
        
        self.inventory_width = 10
        self.inventory_height = 6
        self.slot_size = 40
        self.slot_spacing = 2
        
        self.base_panel_width = 500
        self.base_panel_height = 400
        self.panel_width = self.base_panel_width
        self.panel_height = self.base_panel_height
        
        self.items: List[Optional[Any]] = [None] * 60
        self.equipment: Dict[str, Any] = {}
        
        self.selected_slot: Optional[int] = None
        self.hovered_slot: Optional[int] = None
        self.hovered_equipment_slot: Optional[str] = None
        
        self.dragging_item: Optional[Any] = None
        self.drag_source: Optional[str] = None
        self.drag_source_index: Optional[int] = None
        self.drag_state = DragState.NONE
        
        self.tooltip = ItemTooltip()
        
        # 拖拽回调
        self.on_item_equipped: Optional[Callable] = None
        self.on_item_unequipped: Optional[Callable] = None
        self.on_item_swapped: Optional[Callable] = None
    
    def toggle(self):
        self.visible = not self.visible
    
    def set_items(self, items: List[Optional[Any]]):
        self.items = items
    
    def set_equipment(self, equipment: Dict[str, Any]):
        self.equipment = equipment
    
    def get_panel_position(self) -> tuple:
        x = (self.screen_width - self.panel_width) // 2
        y = (self.screen_height - self.panel_height) // 2
        return (x, y)

    def _apply_ui_scale(self):
        self.panel_width = ui(self.base_panel_width)
        self.panel_height = ui(self.base_panel_height)
        self.slot_size = ui(40)
        self.slot_spacing = ui(2)
    
    def update(self, delta_time: float):
        pass
    
    def render(self, surface: pygame.Surface):
        if not self.visible:
            return
        self._apply_ui_scale()
        
        panel_x, panel_y = self.get_panel_position()
        
        panel_surface = pygame.Surface(
            (self.panel_width, self.panel_height),
            pygame.SRCALPHA
        )
        body_rect = draw_panel(panel_surface, self.panel_width, self.panel_height, "背包", "圆角一体化界面")
        
        self._render_equipment_slots(panel_surface)
        self._render_inventory_grid(panel_surface)
        self._render_item_details(panel_surface)
        
        surface.blit(panel_surface, (panel_x, panel_y))
        
        # 渲染拖拽中的物品
        if self.dragging_item:
            self._render_dragging_item(surface)
        
        # 渲染物品提示框
        self.tooltip.render(surface)
    
    def _render_equipment_slots(self, surface: pygame.Surface):
        start_x = ui(20)
        start_y = ui(58)
        
        slot_positions = {
            "head": (60, 0),
            "shoulders": (0, 50),
            "chest": (60, 50),
            "hands": (120, 50),
            "waist": (60, 100),
            "legs": (60, 150),
            "feet": (60, 200),
            "main_hand": (0, 125),
            "off_hand": (120, 125),
            "neck": (0, 0),
            "ring_left": (0, 200),
            "ring_right": (120, 200),
        }
        
        slot_labels = {
            "head": "头",
            "shoulders": "肩",
            "chest": "胸",
            "hands": "手",
            "waist": "腰",
            "legs": "腿",
            "feet": "脚",
            "main_hand": "主",
            "off_hand": "副",
            "neck": "颈",
            "ring_left": "戒",
            "ring_right": "戒",
        }
        
        for slot, (dx, dy) in slot_positions.items():
            x = start_x + dx
            y = start_y + dy
            
            item = self.equipment.get(slot)
            
            # 背景色
            color = (40, 40, 45)
            border_color = (70, 70, 75)
            
            # 高亮悬停的装备槽
            if self.hovered_equipment_slot == slot:
                border_color = (150, 150, 200)
            
            # 拖拽目标高亮
            if self.dragging_item and self._can_equip_in_slot(self.dragging_item, slot):
                border_color = (100, 255, 100)
            
            if item:
                rarity = getattr(item, 'rarity', None)
                if rarity:
                    rarity_colors = {
                        0: ColorConfig.RARITY_COMMON,
                        1: ColorConfig.RARITY_MAGIC,
                        2: ColorConfig.RARITY_RARE,
                        3: ColorConfig.RARITY_LEGENDARY,
                        4: ColorConfig.RARITY_SET,
                        5: ColorConfig.RARITY_CRAFTED
                    }
                    border_color = rarity_colors.get(rarity.value if hasattr(rarity, 'value') else rarity, 
                                               ColorConfig.RARITY_COMMON)
            
            pygame.draw.rect(surface, color, (x, y, self.slot_size, self.slot_size))
            pygame.draw.rect(surface, border_color, (x, y, self.slot_size, self.slot_size), 2)
            
            if item:
                self._render_item_icon(surface, item, x, y)
            else:
                # 显示槽位标签
                font = ui_font("small")
                label = slot_labels.get(slot, "")
                text = font.render(label, True, (80, 80, 80))
                text_x = x + (self.slot_size - text.get_width()) // 2
                text_y = y + (self.slot_size - text.get_height()) // 2
                surface.blit(text, (text_x, text_y))
    
    def _render_inventory_grid(self, surface: pygame.Surface):
        start_x = ui(180)
        start_y = ui(58)
        
        for row in range(self.inventory_height):
            for col in range(self.inventory_width):
                slot_index = row * self.inventory_width + col
                x = start_x + col * (self.slot_size + self.slot_spacing)
                y = start_y + row * (self.slot_size + self.slot_spacing)
                
                item = self.items[slot_index] if slot_index < len(self.items) else None
                
                color = (35, 35, 40)
                border_color = (60, 60, 65)
                
                # 高亮悬停槽位
                if self.hovered_slot == slot_index:
                    border_color = (120, 120, 150)
                
                # 拖拽目标高亮
                if self.dragging_item and not item:
                    border_color = (80, 120, 80)
                
                if item:
                    rarity = getattr(item, 'rarity', None)
                    if rarity:
                        rarity_colors = {
                            0: ColorConfig.RARITY_COMMON,
                            1: ColorConfig.RARITY_MAGIC,
                            2: ColorConfig.RARITY_RARE,
                            3: ColorConfig.RARITY_LEGENDARY,
                            4: ColorConfig.RARITY_SET,
                            5: ColorConfig.RARITY_CRAFTED
                        }
                        border_color = rarity_colors.get(
                            rarity.value if hasattr(rarity, 'value') else rarity,
                            ColorConfig.RARITY_COMMON
                        )
                
                pygame.draw.rect(surface, color, (x, y, self.slot_size, self.slot_size))
                pygame.draw.rect(surface, border_color, 
                                 (x, y, self.slot_size, self.slot_size), 2)
                
                if item:
                    self._render_item_icon(surface, item, x, y)
    
    def _render_item_icon(self, surface: pygame.Surface, item: Any, x: int, y: int):
        font = ui_font("small")
        
        name = getattr(item, 'name', '???')
        if name:
            initial = name[0]
            
            # 根据稀有度设置颜色
            rarity = getattr(item, 'rarity', None)
            rarity_value = rarity.value if hasattr(rarity, 'value') else (rarity or 0)
            text_color = ItemTooltip.RARITY_COLORS.get(rarity_value, (255, 255, 255))
            
            text = font.render(initial, True, text_color)
            text_x = x + (self.slot_size - text.get_width()) // 2
            text_y = y + (self.slot_size - text.get_height()) // 2
            surface.blit(text, (text_x, text_y))
            
            # 绘制物品类型图标
            item_type = getattr(item, 'item_type', None)
            if item_type:
                self._draw_item_type_indicator(surface, item_type, x, y)
    
    def _draw_item_type_indicator(self, surface: pygame.Surface, item_type, x: int, y: int):
        """绘制物品类型指示器"""
        type_colors = {
            "WEAPON": (255, 100, 100),
            "ARMOR": (100, 150, 255),
            "ACCESSORY": (200, 150, 255),
            "POTION": (100, 255, 100),
            "GEM": (255, 200, 100),
            "RUNE": (150, 100, 255),
        }
        
        type_name = getattr(item_type, 'name', str(item_type))
        color = type_colors.get(type_name, (150, 150, 150))
        
        # 在角落绘制小圆点
        pygame.draw.circle(surface, color, (x + 6, y + self.slot_size - 6), 3)
    
    def _render_item_details(self, surface: pygame.Surface):
        if self.hovered_slot is None or self.hovered_slot >= len(self.items):
            return
        
        item = self.items[self.hovered_slot]
        if not item:
            return
        
        detail_x = ui(180)
        detail_y = ui(320)
        
        font = ui_font("body")
        
        name = getattr(item, 'name', '???')
        name_text = font.render(name, True, (255, 255, 255))
        surface.blit(name_text, (detail_x, detail_y))
        
        level = getattr(item, 'required_level', 1)
        level_text = font.render(f"需要等级: {level}", True, (180, 180, 180))
        surface.blit(level_text, (detail_x, detail_y + 20))
    
    def _render_dragging_item(self, surface: pygame.Surface):
        if not self.dragging_item:
            return
        
        mouse_pos = pygame.mouse.get_pos()
        
        # 绘制拖拽中的物品
        drag_surface = pygame.Surface((self.slot_size, self.slot_size), pygame.SRCALPHA)
        
        rarity = getattr(self.dragging_item, 'rarity', None)
        rarity_value = rarity.value if hasattr(rarity, 'value') else (rarity or 0)
        border_color = ItemTooltip.RARITY_COLORS.get(rarity_value, (150, 150, 150))
        
        pygame.draw.rect(drag_surface, (50, 50, 55, 200), (0, 0, self.slot_size, self.slot_size))
        pygame.draw.rect(drag_surface, border_color, (0, 0, self.slot_size, self.slot_size), 2)
        
        font = ui_font("small")
        name = getattr(self.dragging_item, 'name', '?')
        text = font.render(name[0] if name else '?', True, (255, 255, 255))
        text_x = (self.slot_size - text.get_width()) // 2
        text_y = (self.slot_size - text.get_height()) // 2
        drag_surface.blit(text, (text_x, text_y))
        
        surface.blit(drag_surface, (mouse_pos[0] - self.slot_size // 2, 
                                     mouse_pos[1] - self.slot_size // 2))
    
    def _can_equip_in_slot(self, item: Any, slot: str) -> bool:
        """检查物品是否可以装备到指定槽位"""
        if not item:
            return False
        
        item_type = getattr(item, 'item_type', None)
        if not item_type:
            return False
        
        type_name = getattr(item_type, 'name', str(item_type))
        
        slot_mapping = {
            "WEAPON": ["main_hand", "off_hand"],
            "ARMOR": ["head", "shoulders", "chest", "hands", "waist", "legs", "feet"],
            "ACCESSORY": ["neck", "ring_left", "ring_right"],
        }
        
        allowed_slots = slot_mapping.get(type_name, [])
        
        # 检查护甲类型与槽位匹配
        armor_type = getattr(item, 'armor_type', None)
        if armor_type:
            armor_type_name = getattr(armor_type, 'name', str(armor_type))
            armor_slot_map = {
                "HELM": ["head"],
                "SHOULDERS": ["shoulders"],
                "CHEST": ["chest"],
                "GLOVES": ["hands"],
                "BELT": ["waist"],
                "LEGS": ["legs"],
                "BOOTS": ["feet"],
            }
            allowed_slots = armor_slot_map.get(armor_type_name, allowed_slots)
        
        # 检查武器类型
        weapon_type = getattr(item, 'weapon_type', None)
        if weapon_type and slot in ["main_hand", "off_hand"]:
            return True
        
        return slot in allowed_slots
    
    def handle_click(self, pos: tuple, button: int) -> bool:
        if not self.visible:
            return False
        
        panel_x, panel_y = self.get_panel_position()
        local_pos = (pos[0] - panel_x, pos[1] - panel_y)
        
        # 检查装备槽点击
        equipment_slot = self._get_equipment_slot_at(local_pos)
        if equipment_slot:
            self._handle_equipment_click(equipment_slot, button)
            return True
        
        # 检查背包槽点击
        start_x = 180
        start_y = 50
        
        for row in range(self.inventory_height):
            for col in range(self.inventory_width):
                slot_index = row * self.inventory_width + col
                x = start_x + col * (self.slot_size + self.slot_spacing)
                y = start_y + row * (self.slot_size + self.slot_spacing)
                
                if x <= local_pos[0] <= x + self.slot_size and \
                   y <= local_pos[1] <= y + self.slot_size:
                    self._handle_slot_click(slot_index, button)
                    return True
        
        # 点击空白区域取消拖拽
        if self.dragging_item:
            self._cancel_drag()
        
        return True
    
    def _get_equipment_slot_at(self, local_pos: tuple) -> Optional[str]:
        """获取指定位置的装备槽"""
        start_x = ui(20)
        start_y = ui(58)
        
        slot_positions = {
            "head": (60, 0),
            "shoulders": (0, 50),
            "chest": (60, 50),
            "hands": (120, 50),
            "waist": (60, 100),
            "legs": (60, 150),
            "feet": (60, 200),
            "main_hand": (0, 125),
            "off_hand": (120, 125),
            "neck": (0, 0),
            "ring_left": (0, 200),
            "ring_right": (120, 200),
        }
        
        for slot, (dx, dy) in slot_positions.items():
            x = start_x + dx
            y = start_y + dy
            
            if x <= local_pos[0] <= x + self.slot_size and \
               y <= local_pos[1] <= y + self.slot_size:
                return slot
        
        return None
    
    def _handle_equipment_click(self, slot: str, button: int):
        """处理装备槽点击"""
        if button == 1:  # 左键
            if self.dragging_item:
                # 尝试装备物品
                if self._can_equip_in_slot(self.dragging_item, slot):
                    current_equipped = self.equipment.get(slot)
                    
                    # 交换装备
                    self.equipment[slot] = self.dragging_item
                    
                    if current_equipped:
                        # 将原装备放回拖拽源
                        if self.drag_source and self.drag_source.startswith("inventory_"):
                            src_idx = int(self.drag_source.split("_")[1])
                            self.items[src_idx] = current_equipped
                        else:
                            self.dragging_item = current_equipped
                            self.drag_source = f"equipment_{slot}"
                            return
                    
                    self.dragging_item = None
                    self.drag_source = None
                    
                    if self.on_item_equipped:
                        self.on_item_equipped(slot, self.equipment[slot])
            else:
                # 开始拖拽已装备的物品
                item = self.equipment.get(slot)
                if item:
                    self.dragging_item = item
                    self.drag_source = f"equipment_{slot}"
                    self.drag_source_index = None
        
        elif button == 3:  # 右键
            item = self.equipment.get(slot)
            if item:
                # 卸下装备到背包
                for i, inv_item in enumerate(self.items):
                    if inv_item is None:
                        self.items[i] = item
                        self.equipment[slot] = None
                        if self.on_item_unequipped:
                            self.on_item_unequipped(slot)
                        break
    
    def _handle_slot_click(self, slot_index: int, button: int):
        if button == 1:
            if self.dragging_item:
                # 放置物品到槽位
                target_item = self.items[slot_index]
                
                if target_item is None:
                    # 空槽位，直接放置
                    self.items[slot_index] = self.dragging_item
                    
                    # 清除源位置
                    self._clear_drag_source()
                    
                    self.dragging_item = None
                    self.drag_source = None
                else:
                    # 交换物品
                    self.items[slot_index] = self.dragging_item
                    self.dragging_item = target_item
                    self.drag_source = f"inventory_{slot_index}"
            else:
                # 开始拖拽
                item = self.items[slot_index]
                if item:
                    self.dragging_item = item
                    self.drag_source = f"inventory_{slot_index}"
                    self.drag_source_index = slot_index
        
        elif button == 3:
            item = self.items[slot_index]
            if item:
                self.ui_manager.trigger_callback("use_item", item, slot_index)
    
    def _clear_drag_source(self):
        """清除拖拽源位置的物品"""
        if not self.drag_source:
            return
        
        if self.drag_source.startswith("inventory_"):
            src_idx = int(self.drag_source.split("_")[1])
            if 0 <= src_idx < len(self.items):
                self.items[src_idx] = None
        elif self.drag_source.startswith("equipment_"):
            slot = self.drag_source.split("_")[1]
            if slot in self.equipment:
                self.equipment[slot] = None
    
    def _cancel_drag(self):
        """取消拖拽"""
        self.dragging_item = None
        self.drag_source = None
        self.drag_source_index = None
    
    def handle_motion(self, pos: tuple):
        if not self.visible:
            return
        
        panel_x, panel_y = self.get_panel_position()
        local_pos = (pos[0] - panel_x, pos[1] - panel_y)
        
        # 检查装备槽悬停
        self.hovered_equipment_slot = self._get_equipment_slot_at(local_pos)
        
        # 检查背包槽悬停
        start_x = 180
        start_y = 50
        
        self.hovered_slot = None
        
        for row in range(self.inventory_height):
            for col in range(self.inventory_width):
                slot_index = row * self.inventory_width + col
                x = start_x + col * (self.slot_size + self.slot_spacing)
                y = start_y + row * (self.slot_size + self.slot_spacing)
                
                if x <= local_pos[0] <= x + self.slot_size and \
                   y <= local_pos[1] <= y + self.slot_size:
                    self.hovered_slot = slot_index
                    break
        
        # 更新提示框
        if self.hovered_slot is not None and self.hovered_slot < len(self.items):
            item = self.items[self.hovered_slot]
            if item:
                self.tooltip.show(item, pos)
            else:
                self.tooltip.hide()
        elif self.hovered_equipment_slot:
            item = self.equipment.get(self.hovered_equipment_slot)
            if item:
                self.tooltip.show(item, pos)
            else:
                self.tooltip.hide()
        else:
            self.tooltip.hide()
    
    def resize(self, width: int, height: int):
        self.screen_width = width
        self.screen_height = height
