# GitHub 设置和发布指南

## 1. 创建GitHub仓库

1. 访问 https://github.com
2. 点击右上角的 "+" 按钮，选择 "New repository"
3. 仓库名称: `watermark-app` 或 `add_watermarks_plus`
4. 描述: "Windows desktop application for adding watermarks to images"
5. 选择 "Public" (公开仓库)
6. 不要勾选 "Initialize this repository with a README"
7. 点击 "Create repository"

## 2. 上传代码到GitHub

```bash
# 初始化git仓库（如果还没有）
git init

# 添加所有文件
git add .

# 创建初始提交
git commit -m "Initial commit: Complete watermark application with all features"

# 添加远程仓库（替换YOUR_USERNAME为你的GitHub用户名）
git remote add origin https://github.com/YOUR_USERNAME/watermark-app.git

# 推送到GitHub
git push -u origin main
```

## 3. 创建Release

### 方法一：通过GitHub网页界面

1. 在GitHub仓库页面，点击 "Releases"
2. 点击 "Create a new release"
3. 填写以下信息：
   - **Tag version**: `v1.0.0`
   - **Release title**: `v1.0.0 - 水印添加器首个正式版本`
   - **Description**:
     ```
     ## 功能特点
     - 支持文本和图片水印
     - 实时预览和拖拽定位
     - 九宫格位置预设
     - 水印模板保存和管理
     - 批量图片处理
     - 支持多种图片格式 (JPEG, PNG, BMP, TIFF)
     
     ## 系统要求
     - Windows 10 或更高版本
     - 无需安装额外软件
     
     ## 使用方法
     1. 下载 WatermarkApp.exe
     2. 双击运行
     3. 导入图片，设置水印，导出结果
     ```
4. 在 "Attach binaries" 部分，上传 `release/WatermarkApp.exe` 文件
5. 点击 "Publish release"

### 方法二：通过Git命令行

```bash
# 创建标签
git tag -a v1.0.0 -m "Release version 1.0.0"

# 推送标签到GitHub
git push origin v1.0.0

# 然后通过GitHub网页界面创建release并上传exe文件
```

## 4. 验证Release链接

创建release后，README中的链接应该指向：
- **Releases页面**: `https://github.com/YOUR_USERNAME/watermark-app/releases`
- **Issues页面**: `https://github.com/YOUR_USERNAME/watermark-app/issues`

## 5. 更新README中的链接

确保README.md中的链接使用正确的GitHub用户名：

```markdown
### 方法一：直接运行（推荐）
1. 从 [Releases](../../releases) 页面下载最新版本的 `WatermarkApp.exe`
2. 双击运行，无需安装

### 方法二：从源码运行
1. 克隆仓库：
   ```bash
   git clone https://github.com/YOUR_USERNAME/watermark-app.git
   cd watermark-app
   ```

如有问题或建议，请在 [Issues](../../issues) 页面提出。
```

## 6. 创建PDF文档

创建一个名为 `github_url.pdf` 的文件，包含以下内容：

```
GitHub 仓库信息

项目名称: 水印添加器 (Watermark App)
GitHub 地址: https://github.com/YOUR_USERNAME/watermark-app
Releases 页面: https://github.com/YOUR_USERNAME/watermark-app/releases

项目描述:
一个功能完整的Windows桌面水印添加应用程序，支持文本和图片水印，
具备实时预览、模板管理、批量处理等高级功能。

主要功能:
- 支持多种图片格式 (JPEG, PNG, BMP, TIFF)
- 文本水印：自定义字体、颜色、透明度
- 图片水印：支持PNG透明图片
- 实时预览和拖拽定位
- 九宫格位置预设
- 水印旋转和透明度调节
- 批量图片处理
- 水印模板保存和管理
- Windows可执行文件 (.exe)

技术栈:
- Python 3.7+
- tkinter (GUI)
- Pillow (图像处理)
- PyInstaller (打包)

下载地址:
在GitHub仓库的Releases页面可以下载最新版本的Windows可执行文件：
https://github.com/YOUR_USERNAME/watermark-app/releases

许可证: MIT License
```

## 注意事项

1. **替换用户名**: 将所有的 `YOUR_USERNAME` 替换为你的实际GitHub用户名
2. **检查链接**: 确保所有链接都指向正确的GitHub页面
3. **文件大小**: WatermarkApp.exe 大约35MB，上传可能需要一些时间
4. **测试下载**: 创建release后，测试下载链接是否正常工作

## 常见问题

**Q: 为什么点击Releases链接找不到可执行文件？**
A: 需要先在GitHub上创建Release并上传exe文件，链接才会有效。

**Q: 如何更新README中的链接？**
A: 使用相对路径 `../../releases` 和 `../../issues` 会自动指向正确的GitHub页面。

**Q: 如何确保exe文件可以下载？**
A: 在GitHub Release页面中，exe文件应该显示在 "Assets" 部分，用户可以直接点击下载。

