"""
打包脚本 - 直接运行此脚本进行打包
"""
import subprocess
import sys
import os
import shutil

def main():
    print("=" * 50)
    print("  Diablo Mini - 最小化打包")
    print("=" * 50)
    print()
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("[1/4] 检查PyInstaller...")
    try:
        import PyInstaller
        print(f"  PyInstaller 版本: {PyInstaller.__version__}")
    except ImportError:
        print("  正在安装PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller", "-q"])
        print("  安装完成")
    
    print()
    print("[2/4] 清理旧文件...")
    if os.path.exists("build"):
        shutil.rmtree("build")
        print("  已删除 build 目录")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
        print("  已删除 dist 目录")
    
    print()
    print("[3/4] 开始打包...")
    print("  这可能需要几分钟，请耐心等待...")
    print()
    
    spec_file = os.path.join(script_dir, "build_minimal.spec")
    
    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", spec_file, "--clean", "--noconfirm"],
        cwd=script_dir
    )
    
    print()
    print("[4/4] 检查结果...")
    
    exe_path = os.path.join(script_dir, "dist", "DiabloMini.exe")
    if os.path.exists(exe_path):
        size_bytes = os.path.getsize(exe_path)
        size_mb = size_bytes / (1024 * 1024)
        
        print()
        print("=" * 50)
        print("  打包成功！")
        print("=" * 50)
        print()
        print(f"  文件位置: {exe_path}")
        print(f"  文件大小: {size_mb:.2f} MB ({size_bytes:,} 字节)")
        print()
    else:
        print()
        print("打包失败！请检查错误信息。")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
