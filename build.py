#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build script for creating Windows executable
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("PyInstaller is already installed")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building executable...")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=WatermarkApp",
        "watermark_app.py"
    ]
    
    # Add icon only if it exists
    if os.path.exists("icon.ico"):
        cmd.append("--icon=icon.ico")
        print("Using custom icon: icon.ico")
    else:
        print("No custom icon found, using default")
    
    try:
        subprocess.run(cmd, check=True)
        print("Build successful!")
        
        # Copy additional files if needed
        dist_dir = Path("dist")
        if dist_dir.exists():
            print(f"Executable created in: {dist_dir.absolute()}")
            
            # Create release directory
            release_dir = Path("release")
            release_dir.mkdir(exist_ok=True)
            
            # Copy executable
            exe_file = dist_dir / "WatermarkApp.exe"
            if exe_file.exists():
                shutil.copy2(exe_file, release_dir)
                print(f"Executable copied to: {release_dir.absolute()}")
                
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        return False
    
    return True

def create_readme():
    """Create README file for the release"""
    readme_content = """# 水印添加器 (Watermark App)

## 功能特点

### 文件处理
- 支持单张图片拖拽或批量导入
- 支持主流格式：JPEG, PNG, BMP, TIFF
- 完整的透明通道支持
- 可选择输出格式（PNG/JPEG）
- 自定义文件命名规则

### 水印类型
- **文本水印**：自定义文本、字体、颜色、透明度
- **图片水印**：支持PNG透明图片、缩放、透明度调节

### 水印布局
- 实时预览
- 九宫格位置预设
- 鼠标拖拽自定义位置
- 任意角度旋转

### 配置管理
- 保存/加载水印模板
- 自动保存上次设置
- 模板管理功能

## 使用方法

1. 运行 `WatermarkApp.exe`
2. 点击"导入图片"或"导入文件夹"添加图片
3. 在左侧设置水印参数
4. 在预览区域查看效果
5. 设置导出参数并点击"导出所有图片"

## 系统要求

- Windows 10 或更高版本
- 无需安装额外软件

## 注意事项

- 为防止覆盖原文件，不允许导出到原图片目录
- PNG格式保持透明通道，JPEG格式转换为白底
- 建议使用PNG格式的水印图片以获得最佳效果

---

© 2025 Watermark App
"""
    
    with open("release/README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("README.txt created")

def main():
    """Main build process"""
    print("Starting build process...")
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Build executable
    if build_executable():
        create_readme()
        print("\nBuild process completed successfully!")
        print("Check the 'release' directory for the executable and documentation.")
    else:
        print("Build process failed!")

if __name__ == "__main__":
    main()
