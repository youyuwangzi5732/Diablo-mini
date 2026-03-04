"""
字体管理器 - 处理中文字体支持
"""
import pygame
from typing import Optional, Dict


class FontManager:
    """字体管理器单例类"""
    _instance: Optional['FontManager'] = None
    _fonts: Dict[str, pygame.font.Font] = {}
    
    # 中文字体优先级列表
    CHINESE_FONTS = [
        "Microsoft YaHei UI",
        "Microsoft JhengHei UI",
        "HarmonyOS Sans SC",
        "DengXian",
        "Microsoft YaHei",      # 微软雅黑 (Windows)
        "SimHei",               # 黑体 (Windows)
        "SimSun",               # 宋体 (Windows)
        "Noto Sans CJK SC",     # Noto字体 (Linux)
        "WenQuanYi Micro Hei",  # 文泉驿 (Linux)
        "PingFang SC",          # 苹方 (macOS)
        "Heiti TC",             # 黑体 (macOS)
        "Arial Unicode MS",     # Arial Unicode
    ]
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        self._default_font_name = self._find_chinese_font()
    
    def _find_chinese_font(self) -> str:
        """查找系统中可用的中文字体"""
        for font_name in self.CHINESE_FONTS:
            try:
                test_font = pygame.font.SysFont(font_name, 12)
                # 测试是否能渲染中文字符
                test_surface = test_font.render("测试", True, (255, 255, 255))
                if test_surface.get_width() > 10:  # 如果能正确渲染，宽度应该大于10
                    print(f"[FontManager] 使用字体: {font_name}")
                    return font_name
            except:
                continue
        
        print("[FontManager] 警告: 未找到中文字体，使用默认字体")
        return "Arial"
    
    def get_font(self, size: int, bold: bool = False, italic: bool = False) -> pygame.font.Font:
        """获取指定大小的字体"""
        key = f"{self._default_font_name}_{size}_{bold}_{italic}"
        
        if key not in self._fonts:
            self._fonts[key] = pygame.font.SysFont(
                self._default_font_name, 
                size, 
                bold=bold, 
                italic=italic
            )
        
        return self._fonts[key]
    
    def get_default_font_name(self) -> str:
        """获取默认字体名称"""
        return self._default_font_name


# 全局字体管理器实例
_font_manager: Optional[FontManager] = None


def get_font_manager() -> FontManager:
    """获取字体管理器实例"""
    global _font_manager
    if _font_manager is None:
        _font_manager = FontManager()
    return _font_manager


def get_font(size: int, bold: bool = False, italic: bool = False) -> pygame.font.Font:
    """便捷函数：获取字体"""
    return get_font_manager().get_font(size, bold, italic)


def get_default_font_name() -> str:
    """便捷函数：获取默认字体名称"""
    return get_font_manager().get_default_font_name()
