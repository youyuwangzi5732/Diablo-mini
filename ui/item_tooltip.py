"""
物品详情提示框系统
"""
from typing import Dict, List, Optional, Any, Tuple
import pygame

from config.game_config import ColorConfig


class ItemTooltip:
    def __init__(self):
        self.visible = False
        self.item: Optional[Any] = None
        self.position: Tuple[int, int] = (0, 0)
        
        self.padding = 10
        self.line_height = 18
        self.title_height = 24
        self.width = 300
        
        self.font_name = get_font(16, bold=True)
        self.font_normal = get_font(14)
        self.font_small = get_font(12)
        self.font_flavor = get_font(12, italic=True)
    
    def show(self, item: Any, position: Tuple[int, int]):
        self.item = item
        self.position = position
        self.visible = True
    
    def hide(self):
        self.visible = False
        self.item = None
    
    def update_position(self, position: Tuple[int, int]):
        self.position = position
    
    def render(self, surface: pygame.Surface):
        if not self.visible or not self.item:
            return
        
        lines = self._build_tooltip_lines()
        
        total_height = self._calculate_height(lines)
        
        x, y = self._adjust_position(surface, total_height)
        
        tooltip_surface = pygame.Surface(
            (self.width, total_height),
            pygame.SRCALPHA
        )
        
        tooltip_surface.fill((20, 20, 20, 240))
        pygame.draw.rect(tooltip_surface, (100, 100, 100), 
                         (0, 0, self.width, total_height), 2)
        
        current_y = self.padding
        
        for line in lines:
            if line["type"] == "title":
                text = self.font_name.render(line["text"], True, line["color"])
                tooltip_surface.blit(text, (self.padding, current_y))
                current_y += self.title_height
            elif line["type"] == "separator":
                pygame.draw.line(tooltip_surface, (80, 80, 80),
                                 (self.padding, current_y + 5),
                                 (self.width - self.padding, current_y + 5), 1)
                current_y += 15
            elif line["type"] == "stat":
                text = self.font_normal.render(line["text"], True, line["color"])
                tooltip_surface.blit(text, (self.padding, current_y))
                current_y += self.line_height
            elif line["type"] == "flavor":
                text = self.font_flavor.render(line["text"], True, (150, 150, 150))
                tooltip_surface.blit(text, (self.padding, current_y))
                current_y += self.line_height
            elif line["type"] == "socket":
                self._render_socket(tooltip_surface, line, current_y)
                current_y += self.line_height
            elif line["type"] == "set":
                text = self.font_small.render(line["text"], True, line["color"])
                tooltip_surface.blit(text, (self.padding, current_y))
                current_y += self.line_height
            else:
                text = self.font_normal.render(line["text"], True, line.get("color", (200, 200, 200)))
                tooltip_surface.blit(text, (self.padding, current_y))
                current_y += self.line_height
        
        surface.blit(tooltip_surface, (x, y))
    
    def _build_tooltip_lines(self) -> List[Dict[str, Any]]:
        lines = []
        item = self.item
        
        rarity = getattr(item, 'rarity', None)
        rarity_value = rarity.value if hasattr(rarity, 'value') else 0
        
        rarity_colors = {
            0: ColorConfig.RARITY_COMMON,
            1: ColorConfig.RARITY_MAGIC,
            2: ColorConfig.RARITY_RARE,
            3: ColorConfig.RARITY_LEGENDARY,
            4: ColorConfig.RARITY_SET,
            5: ColorConfig.RARITY_CRAFTED
        }
        rarity_color = rarity_colors.get(rarity_value, (200, 200, 200))
        
        item_name = getattr(item, 'name', '未知物品')
        lines.append({
            "type": "title",
            "text": item_name,
            "color": rarity_color
        })
        
        item_type = getattr(item, 'item_type', None)
        if item_type:
            type_name = self._get_item_type_name(item_type)
            lines.append({
                "type": "stat",
                "text": type_name,
                "color": (150, 150, 150)
            })
        
        required_level = getattr(item, 'required_level', 1)
        lines.append({
            "type": "stat",
            "text": f"需要等级: {required_level}",
            "color": (200, 200, 200)
        })
        
        lines.append({"type": "separator"})
        
        if hasattr(item, 'base_damage_min') and hasattr(item, 'base_damage_max'):
            dmg_min = item.base_damage_min
            dmg_max = item.base_damage_max
            lines.append({
                "type": "stat",
                "text": f"伤害: {dmg_min} - {dmg_max}",
                "color": (255, 255, 255)
            })
        
        if hasattr(item, 'armor') and item.armor > 0:
            lines.append({
                "type": "stat",
                "text": f"护甲: {item.armor}",
                "color": (255, 255, 255)
            })
        
        if hasattr(item, 'affixes') and item.affixes:
            for affix_inst in item.affixes:
                affix = affix_inst.affix
                value = affix_inst.get_effective_value()
                
                affix_color = (100, 200, 255) if affix.is_prefix else (255, 200, 100)
                
                text = self._format_affix(affix, value)
                lines.append({
                    "type": "stat",
                    "text": f"+{text}" if not text.startswith('+') else text,
                    "color": affix_color
                })
        
        if hasattr(item, 'socketed_items') and item.socketed_items:
            lines.append({"type": "separator"})
            
            for i, socketed in enumerate(item.socketed_items):
                if socketed:
                    gem_name = getattr(socketed, 'name', '宝石')
                    gem_color = self._get_gem_color(socketed)
                    lines.append({
                        "type": "socket",
                        "text": f"插槽 {i+1}: {gem_name}",
                        "color": gem_color,
                        "gem": socketed
                    })
                else:
                    lines.append({
                        "type": "socket",
                        "text": f"插槽 {i+1}: [空]",
                        "color": (100, 100, 100)
                    })
        
        if hasattr(item, 'sockets') and item.sockets > 0:
            if not hasattr(item, 'socketed_items') or not item.socketed_items:
                lines.append({
                    "type": "stat",
                    "text": f"插槽: {item.sockets}",
                    "color": (150, 150, 150)
                })
        
        set_id = getattr(item, 'set_id', None)
        if set_id:
            lines.append({"type": "separator"})
            set_name = self._get_set_name(set_id)
            lines.append({
                "type": "set",
                "text": f"套装: {set_name}",
                "color": (100, 200, 100)
            })
            
            set_bonuses = self._get_set_bonuses(set_id)
            for bonus in set_bonuses:
                lines.append({
                    "type": "set",
                    "text": f"  ({bonus['count']}件) {bonus['name']}: {bonus['effect']}",
                    "color": (100, 200, 100)
                })
        
        flavor_text = getattr(item, 'flavor_text', None)
        if flavor_text:
            lines.append({"type": "separator"})
            lines.append({
                "type": "flavor",
                "text": f'"{flavor_text}"',
                "color": (150, 150, 150)
            })
        
        if hasattr(item, 'current_durability') and hasattr(item, 'max_durability'):
            lines.append({"type": "separator"})
            dur_color = (255, 100, 100) if item.current_durability < item.max_durability * 0.3 else (200, 200, 200)
            lines.append({
                "type": "stat",
                "text": f"耐久度: {item.current_durability}/{item.max_durability}",
                "color": dur_color
            })
        
        value = getattr(item, 'value', 0)
        if value > 0:
            lines.append({
                "type": "stat",
                "text": f"出售价格: {value} 金币",
                "color": (255, 215, 0)
            })
        
        return lines
    
    def _get_item_type_name(self, item_type) -> str:
        type_names = {
            "helmet": "头盔",
            "shoulders": "护肩",
            "chest": "胸甲",
            "gloves": "手套",
            "belt": "腰带",
            "pants": "护腿",
            "boots": "靴子",
            "main_hand": "主手武器",
            "off_hand": "副手",
            "amulet": "项链",
            "ring": "戒指",
            "two_hand": "双手武器",
            "sword": "剑",
            "axe": "斧",
            "mace": "锤",
            "dagger": "匕首",
            "staff": "法杖",
            "wand": "魔杖",
            "bow": "弓",
            "crossbow": "弩",
            "shield": "盾牌",
            "potion": "药水",
            "gem": "宝石",
            "rune": "符文",
            "material": "材料",
        }
        
        if hasattr(item_type, 'value'):
            return type_names.get(item_type.value, str(item_type.value))
        return type_names.get(str(item_type), str(item_type))
    
    def _format_affix(self, affix, value) -> str:
        attr_names = {
            "strength": "力量",
            "dexterity": "敏捷",
            "intelligence": "智力",
            "vitality": "体能",
            "armor": "护甲",
            "max_health": "最大生命",
            "max_mana": "最大法力",
            "health_regen": "生命恢复",
            "mana_regen": "法力恢复",
            "attack_power": "攻击力",
            "spell_power": "法术强度",
            "crit_chance": "暴击率",
            "crit_damage": "暴击伤害",
            "attack_speed": "攻击速度",
            "cast_speed": "施法速度",
            "movement_speed": "移动速度",
            "fire_resist": "火焰抗性",
            "cold_resist": "冰冷抗性",
            "lightning_resist": "闪电抗性",
            "poison_resist": "毒素抗性",
            "life_steal": "生命偷取",
            "magic_find": "魔法寻宝",
            "gold_find": "金币寻宝",
        }
        
        attr_name = attr_names.get(affix.attribute, affix.attribute)
        
        is_percentage = affix.attribute.endswith("_percent") or affix.attribute in [
            "crit_chance", "crit_damage", "life_steal",
            "magic_find", "gold_find", "attack_speed", "cast_speed", "movement_speed"
        ]
        
        if is_percentage:
            return f"{value}% {attr_name}"
        else:
            return f"{value} {attr_name}"
    
    def _get_gem_color(self, gem) -> Tuple[int, int, int]:
        gem_type = getattr(gem, 'gem_type', None)
        if gem_type:
            if hasattr(gem_type, 'value'):
                gem_type = gem_type.value
            
            colors = {
                "ruby": (255, 50, 50),
                "sapphire": (50, 100, 255),
                "emerald": (50, 255, 50),
                "topaz": (255, 255, 50),
                "amethyst": (200, 50, 255),
                "diamond": (255, 255, 255),
            }
            return colors.get(gem_type, (200, 200, 200))
        return (200, 200, 200)
    
    def _get_set_name(self, set_id: str) -> str:
        set_names = {
            "immortal_king": "不朽之王的呼唤",
            "tal_rasha": "塔拉夏的战衣",
            "natalya": "娜塔亚的复仇",
            "inarius": "伊纳瑞斯的恩典",
            "sunwuko": "孙吾空的战甲",
            "akkhan": "阿克汉的战铠",
            "zunimassa": "祖尼玛萨的萦绕",
            "shadow": "暗影之装",
        }
        return set_names.get(set_id, set_id)
    
    def _get_set_bonuses(self, set_id: str) -> List[Dict[str, Any]]:
        bonuses = {
            "immortal_king": [
                {"count": 2, "name": "不朽之力", "effect": "力量+100"},
                {"count": 3, "name": "狂暴之心", "effect": "暴击伤害+30%"},
                {"count": 4, "name": "不朽意志", "effect": "所有抗性+50"},
                {"count": 5, "name": "王者降临", "effect": "伤害+20%"},
                {"count": 6, "name": "不朽之王", "effect": "野蛮人技能+1"},
            ],
            "tal_rasha": [
                {"count": 2, "name": "元素协调", "effect": "元素伤害+15%"},
                {"count": 3, "name": "奥术能量", "effect": "法术强度+50"},
                {"count": 4, "name": "元素精通", "effect": "抗性+60"},
                {"count": 5, "name": "大法师", "effect": "魔法师技能+1"},
            ],
        }
        return bonuses.get(set_id, [])
    
    def _render_socket(self, surface: pygame.Surface, line: Dict, y: int):
        text = self.font_small.render(line["text"], True, line["color"])
        surface.blit(text, (self.padding, y))
        
        pygame.draw.rect(surface, line["color"], 
                         (self.padding, y + 14, 10, 10), 1)
    
    def _calculate_height(self, lines: List[Dict]) -> int:
        height = self.padding * 2
        
        for line in lines:
            if line["type"] == "title":
                height += self.title_height
            elif line["type"] == "separator":
                height += 15
            else:
                height += self.line_height
        
        return height
    
    def _adjust_position(self, surface: pygame.Surface, height: int) -> Tuple[int, int]:
        x, y = self.position
        
        x += 15
        y += 15
        
        screen_width = surface.get_width()
        screen_height = surface.get_height()
        
        if x + self.width > screen_width:
            x = screen_width - self.width - 10
        
        if y + height > screen_height:
            y = screen_height - height - 10
        
        return (max(0, x), max(0, y))
    
    def is_visible(self) -> bool:
        return self.visible
