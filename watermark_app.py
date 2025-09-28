#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows Watermark Application
A desktop application for adding watermarks to images
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from tkinter.font import families
import os
import json
from PIL import Image, ImageDraw, ImageFont, ImageTk, ImageEnhance
import math
from pathlib import Path
import shutil

class WatermarkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("水印添加器 - Watermark App")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Initialize variables
        self.images = []  # List of loaded images
        self.current_image_index = 0
        self.preview_image = None
        self.preview_with_watermark = None
        self.watermark_x = 0
        self.watermark_y = 0
        self.dragging = False
        
        # Watermark settings
        self.watermark_text = tk.StringVar(value="Sample Watermark")
        self.watermark_font_family = tk.StringVar(value="Arial")
        self.watermark_font_size = tk.IntVar(value=36)
        self.watermark_color = "#FFFFFF"
        self.watermark_opacity = tk.IntVar(value=50)
        self.watermark_rotation = tk.IntVar(value=0)
        self.watermark_position = tk.StringVar(value="center")
        self.watermark_image_path = tk.StringVar()
        self.watermark_type = tk.StringVar(value="text")
        self.watermark_scale = tk.IntVar(value=100)
        
        # Export settings
        self.output_format = tk.StringVar(value="PNG")
        self.jpeg_quality = tk.IntVar(value=95)
        self.filename_prefix = tk.StringVar()
        self.filename_suffix = tk.StringVar(value="_watermarked")
        self.scale_width = tk.IntVar()
        self.scale_height = tk.IntVar()
        self.scale_percent = tk.IntVar(value=100)
        
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Create main frames
        self.create_menu()
        self.create_main_frames()
        self.create_image_list_frame()
        self.create_preview_frame()
        self.create_watermark_settings_frame()
        self.create_export_settings_frame()
        
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="导入图片", command=self.import_images)
        file_menu.add_command(label="导入文件夹", command=self.import_folder)
        file_menu.add_separator()
        file_menu.add_command(label="导出所有", command=self.export_all_images)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # Template menu
        template_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="模板", menu=template_menu)
        template_menu.add_command(label="保存模板", command=self.save_template)
        template_menu.add_command(label="加载模板", command=self.load_template)
        template_menu.add_command(label="管理模板", command=self.manage_templates)
        
    def create_main_frames(self):
        """Create main layout frames"""
        # Left panel for image list and settings
        self.left_frame = ttk.Frame(self.root, width=300)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.left_frame.pack_propagate(False)
        
        # Right panel for preview
        self.right_frame = ttk.Frame(self.root)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def create_image_list_frame(self):
        """Create image list frame"""
        # Image list frame
        list_frame = ttk.LabelFrame(self.left_frame, text="图片列表", padding=5)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Buttons
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(btn_frame, text="导入图片", command=self.import_images).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="导入文件夹", command=self.import_folder).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="清空", command=self.clear_images).pack(side=tk.LEFT)
        
        # Image listbox with scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        self.image_listbox = tk.Listbox(list_container, selectmode=tk.SINGLE)
        scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.image_listbox.yview)
        self.image_listbox.config(yscrollcommand=scrollbar.set)
        
        self.image_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.image_listbox.bind('<<ListboxSelect>>', self.on_image_select)
        
    def create_preview_frame(self):
        """Create preview frame"""
        preview_frame = ttk.LabelFrame(self.right_frame, text="预览", padding=5)
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # Preview canvas with scrollbars
        canvas_frame = ttk.Frame(preview_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.preview_canvas = tk.Canvas(canvas_frame, bg="white")
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.preview_canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.preview_canvas.xview)
        
        self.preview_canvas.config(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.preview_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind mouse events for dragging
        self.preview_canvas.bind("<Button-1>", self.on_canvas_click)
        self.preview_canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.preview_canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
    def create_watermark_settings_frame(self):
        """Create watermark settings frame"""
        settings_frame = ttk.LabelFrame(self.left_frame, text="水印设置", padding=5)
        settings_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Watermark type selection
        type_frame = ttk.Frame(settings_frame)
        type_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(type_frame, text="水印类型:").pack(side=tk.LEFT)
        ttk.Radiobutton(type_frame, text="文本", variable=self.watermark_type, 
                       value="text", command=self.update_preview).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Radiobutton(type_frame, text="图片", variable=self.watermark_type, 
                       value="image", command=self.update_preview).pack(side=tk.LEFT, padx=(5, 0))
        
        # Text watermark settings
        self.text_frame = ttk.Frame(settings_frame)
        self.text_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(self.text_frame, text="水印文本:").pack(anchor=tk.W)
        text_entry = ttk.Entry(self.text_frame, textvariable=self.watermark_text)
        text_entry.pack(fill=tk.X, pady=(0, 5))
        text_entry.bind('<KeyRelease>', lambda e: self.update_preview())
        
        # Font settings
        font_frame = ttk.Frame(self.text_frame)
        font_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(font_frame, text="字体:").pack(side=tk.LEFT)
        font_combo = ttk.Combobox(font_frame, textvariable=self.watermark_font_family, 
                                 values=list(families()), state="readonly", width=15)
        font_combo.pack(side=tk.LEFT, padx=(5, 0))
        font_combo.bind('<<ComboboxSelected>>', lambda e: self.update_preview())
        
        ttk.Label(font_frame, text="大小:").pack(side=tk.LEFT, padx=(10, 0))
        size_spin = ttk.Spinbox(font_frame, from_=8, to=200, textvariable=self.watermark_font_size, width=8)
        size_spin.pack(side=tk.LEFT, padx=(5, 0))
        size_spin.bind('<KeyRelease>', lambda e: self.update_preview())
        
        # Color and opacity
        color_frame = ttk.Frame(self.text_frame)
        color_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(color_frame, text="选择颜色", command=self.choose_color).pack(side=tk.LEFT)
        
        self.color_label = tk.Label(color_frame, text="■", fg=self.watermark_color, font=("Arial", 16))
        self.color_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Image watermark settings
        self.image_frame = ttk.Frame(settings_frame)
        
        ttk.Button(self.image_frame, text="选择水印图片", command=self.choose_watermark_image).pack(fill=tk.X, pady=(0, 5))
        
        scale_frame = ttk.Frame(self.image_frame)
        scale_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(scale_frame, text="缩放比例:").pack(side=tk.LEFT)
        scale_spin = ttk.Spinbox(scale_frame, from_=10, to=500, textvariable=self.watermark_scale, width=8)
        scale_spin.pack(side=tk.RIGHT)
        scale_spin.bind('<KeyRelease>', lambda e: self.update_preview())
        
        # Common settings
        common_frame = ttk.Frame(settings_frame)
        common_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Opacity
        opacity_frame = ttk.Frame(common_frame)
        opacity_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(opacity_frame, text="透明度:").pack(side=tk.LEFT)
        opacity_scale = ttk.Scale(opacity_frame, from_=0, to=100, variable=self.watermark_opacity, 
                                 orient=tk.HORIZONTAL, command=lambda v: self.update_preview())
        opacity_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Rotation
        rotation_frame = ttk.Frame(common_frame)
        rotation_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(rotation_frame, text="旋转角度:").pack(side=tk.LEFT)
        rotation_scale = ttk.Scale(rotation_frame, from_=-180, to=180, variable=self.watermark_rotation, 
                                  orient=tk.HORIZONTAL, command=lambda v: self.update_preview())
        rotation_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Position presets
        pos_frame = ttk.LabelFrame(settings_frame, text="位置预设", padding=5)
        pos_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Grid layout for position buttons
        positions = [
            ("左上", "top_left"), ("上中", "top_center"), ("右上", "top_right"),
            ("左中", "middle_left"), ("居中", "center"), ("右中", "middle_right"),
            ("左下", "bottom_left"), ("下中", "bottom_center"), ("右下", "bottom_right")
        ]
        
        for i, (text, value) in enumerate(positions):
            row, col = divmod(i, 3)
            btn = ttk.Button(pos_frame, text=text, width=6,
                           command=lambda v=value: self.set_position_preset(v))
            btn.grid(row=row, column=col, padx=1, pady=1)
            
    def create_export_settings_frame(self):
        """Create export settings frame"""
        export_frame = ttk.LabelFrame(self.left_frame, text="导出设置", padding=5)
        export_frame.pack(fill=tk.X)
        
        # Output format
        format_frame = ttk.Frame(export_frame)
        format_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(format_frame, text="输出格式:").pack(side=tk.LEFT)
        ttk.Radiobutton(format_frame, text="PNG", variable=self.output_format, value="PNG").pack(side=tk.LEFT, padx=(5, 0))
        ttk.Radiobutton(format_frame, text="JPEG", variable=self.output_format, value="JPEG").pack(side=tk.LEFT, padx=(5, 0))
        
        # JPEG quality
        quality_frame = ttk.Frame(export_frame)
        quality_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(quality_frame, text="JPEG质量:").pack(side=tk.LEFT)
        ttk.Scale(quality_frame, from_=1, to=100, variable=self.jpeg_quality, 
                 orient=tk.HORIZONTAL).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Filename settings
        name_frame = ttk.LabelFrame(export_frame, text="文件名设置", padding=3)
        name_frame.pack(fill=tk.X, pady=(0, 5))
        
        prefix_frame = ttk.Frame(name_frame)
        prefix_frame.pack(fill=tk.X, pady=(0, 2))
        ttk.Label(prefix_frame, text="前缀:").pack(side=tk.LEFT)
        ttk.Entry(prefix_frame, textvariable=self.filename_prefix, width=15).pack(side=tk.RIGHT)
        
        suffix_frame = ttk.Frame(name_frame)
        suffix_frame.pack(fill=tk.X)
        ttk.Label(suffix_frame, text="后缀:").pack(side=tk.LEFT)
        ttk.Entry(suffix_frame, textvariable=self.filename_suffix, width=15).pack(side=tk.RIGHT)
        
        # Export button
        ttk.Button(export_frame, text="导出所有图片", command=self.export_all_images).pack(fill=tk.X, pady=(5, 0))
        
    def import_images(self):
        """Import images through file dialog"""
        filetypes = [
            ("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
            ("JPEG文件", "*.jpg *.jpeg"),
            ("PNG文件", "*.png"),
            ("BMP文件", "*.bmp"),
            ("TIFF文件", "*.tiff *.tif"),
            ("所有文件", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=filetypes
        )
        
        for file_path in files:
            self.add_image(file_path)
            
    def import_folder(self):
        """Import all images from a folder"""
        folder_path = filedialog.askdirectory(title="选择图片文件夹")
        if not folder_path:
            return
            
        supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif')
        
        for file_path in Path(folder_path).rglob('*'):
            if file_path.suffix.lower() in supported_formats:
                self.add_image(str(file_path))
                
    def add_image(self, file_path):
        """Add an image to the list"""
        try:
            # Test if image can be opened
            with Image.open(file_path) as img:
                # Add to list
                self.images.append(file_path)
                filename = os.path.basename(file_path)
                self.image_listbox.insert(tk.END, filename)
                
                # Select the first image if this is the first one
                if len(self.images) == 1:
                    self.image_listbox.selection_set(0)
                    self.current_image_index = 0
                    self.load_current_image()
                    
        except Exception as e:
            messagebox.showerror("错误", f"无法加载图片 {file_path}: {str(e)}")
            
    def clear_images(self):
        """Clear all images"""
        self.images.clear()
        self.image_listbox.delete(0, tk.END)
        self.preview_canvas.delete("all")
        self.current_image_index = 0
        
    def on_image_select(self, event):
        """Handle image selection"""
        selection = self.image_listbox.curselection()
        if selection:
            self.current_image_index = selection[0]
            self.load_current_image()
            
    def load_current_image(self):
        """Load and display the current image"""
        if not self.images or self.current_image_index >= len(self.images):
            return
            
        try:
            image_path = self.images[self.current_image_index]
            self.preview_image = Image.open(image_path)
            
            # Convert to RGB if necessary (for JPEG export)
            if self.preview_image.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparency
                background = Image.new('RGB', self.preview_image.size, (255, 255, 255))
                if self.preview_image.mode == 'P':
                    self.preview_image = self.preview_image.convert('RGBA')
                background.paste(self.preview_image, mask=self.preview_image.split()[-1] if self.preview_image.mode == 'RGBA' else None)
                self.preview_image_rgb = background
            else:
                self.preview_image_rgb = self.preview_image.copy()
                
            self.update_preview()
            
        except Exception as e:
            messagebox.showerror("错误", f"无法加载图片: {str(e)}")
            
    def update_preview(self):
        """Update the preview with watermark"""
        if not self.preview_image:
            return
            
        try:
            # Create a copy of the image
            preview = self.preview_image.copy()
            
            # Apply watermark
            preview = self.apply_watermark(preview)
            
            # Resize for display (maintain aspect ratio)
            display_size = (800, 600)
            preview.thumbnail(display_size, Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage for display
            self.preview_photo = ImageTk.PhotoImage(preview)
            
            # Clear canvas and display image
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(0, 0, anchor=tk.NW, image=self.preview_photo)
            
            # Update scroll region
            self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))
            
        except Exception as e:
            print(f"Preview update error: {str(e)}")
            
    def apply_watermark(self, image):
        """Apply watermark to image"""
        if self.watermark_type.get() == "text":
            return self.apply_text_watermark(image)
        else:
            return self.apply_image_watermark(image)
            
    def apply_text_watermark(self, image):
        """Apply text watermark"""
        if not self.watermark_text.get().strip():
            return image
            
        # Create a copy with RGBA mode for transparency
        watermarked = image.convert('RGBA')
        
        # Create transparent overlay
        overlay = Image.new('RGBA', watermarked.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Get font
        try:
            font = ImageFont.truetype(f"{self.watermark_font_family.get()}.ttf", self.watermark_font_size.get())
        except:
            try:
                font = ImageFont.truetype("arial.ttf", self.watermark_font_size.get())
            except:
                font = ImageFont.load_default()
                
        # Get text size
        text = self.watermark_text.get()
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Calculate position
        x, y = self.calculate_watermark_position(watermarked.size, (text_width, text_height))
        
        # Convert color and apply opacity
        color = self.hex_to_rgba(self.watermark_color, self.watermark_opacity.get())
        
        # Draw text
        if self.watermark_rotation.get() != 0:
            # Create rotated text
            text_img = Image.new('RGBA', (text_width * 2, text_height * 2), (255, 255, 255, 0))
            text_draw = ImageDraw.Draw(text_img)
            text_draw.text((text_width // 2, text_height // 2), text, font=font, fill=color)
            text_img = text_img.rotate(self.watermark_rotation.get(), expand=1)
            
            # Calculate new position after rotation
            new_width, new_height = text_img.size
            x -= (new_width - text_width) // 2
            y -= (new_height - text_height) // 2
            
            overlay.paste(text_img, (x, y), text_img)
        else:
            draw.text((x, y), text, font=font, fill=color)
            
        # Composite with original image
        watermarked = Image.alpha_composite(watermarked, overlay)
        
        # Convert back to original mode if needed
        if image.mode != 'RGBA':
            watermarked = watermarked.convert(image.mode)
            
        return watermarked
        
    def apply_image_watermark(self, image):
        """Apply image watermark"""
        if not self.watermark_image_path.get() or not os.path.exists(self.watermark_image_path.get()):
            return image
            
        try:
            # Load watermark image
            watermark_img = Image.open(self.watermark_image_path.get())
            
            # Scale watermark
            scale_factor = self.watermark_scale.get() / 100.0
            new_size = (int(watermark_img.width * scale_factor), int(watermark_img.height * scale_factor))
            watermark_img = watermark_img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Apply opacity
            if watermark_img.mode != 'RGBA':
                watermark_img = watermark_img.convert('RGBA')
                
            # Apply opacity
            opacity = self.watermark_opacity.get() / 100.0
            alpha = watermark_img.split()[-1]
            alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
            watermark_img.putalpha(alpha)
            
            # Rotate if needed
            if self.watermark_rotation.get() != 0:
                watermark_img = watermark_img.rotate(self.watermark_rotation.get(), expand=1)
                
            # Calculate position
            x, y = self.calculate_watermark_position(image.size, watermark_img.size)
            
            # Apply watermark
            watermarked = image.convert('RGBA')
            watermarked.paste(watermark_img, (x, y), watermark_img)
            
            # Convert back to original mode if needed
            if image.mode != 'RGBA':
                watermarked = watermarked.convert(image.mode)
                
            return watermarked
            
        except Exception as e:
            print(f"Image watermark error: {str(e)}")
            return image
            
    def calculate_watermark_position(self, image_size, watermark_size):
        """Calculate watermark position based on settings"""
        img_width, img_height = image_size
        wm_width, wm_height = watermark_size
        
        position = self.watermark_position.get()
        
        if position == "top_left":
            return 10, 10
        elif position == "top_center":
            return (img_width - wm_width) // 2, 10
        elif position == "top_right":
            return img_width - wm_width - 10, 10
        elif position == "middle_left":
            return 10, (img_height - wm_height) // 2
        elif position == "center":
            return (img_width - wm_width) // 2, (img_height - wm_height) // 2
        elif position == "middle_right":
            return img_width - wm_width - 10, (img_height - wm_height) // 2
        elif position == "bottom_left":
            return 10, img_height - wm_height - 10
        elif position == "bottom_center":
            return (img_width - wm_width) // 2, img_height - wm_height - 10
        elif position == "bottom_right":
            return img_width - wm_width - 10, img_height - wm_height - 10
        else:
            # Custom position
            return self.watermark_x, self.watermark_y
            
    def hex_to_rgba(self, hex_color, opacity):
        """Convert hex color to RGBA with opacity"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        alpha = int(255 * opacity / 100)
        return rgb + (alpha,)
        
    def choose_color(self):
        """Choose watermark color"""
        color = colorchooser.askcolor(color=self.watermark_color, title="选择水印颜色")
        if color[1]:
            self.watermark_color = color[1]
            self.color_label.config(fg=self.watermark_color)
            self.update_preview()
            
    def choose_watermark_image(self):
        """Choose watermark image"""
        filetypes = [
            ("图片文件", "*.png *.jpg *.jpeg *.bmp *.tiff"),
            ("PNG文件", "*.png"),
            ("所有文件", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="选择水印图片",
            filetypes=filetypes
        )
        
        if file_path:
            self.watermark_image_path.set(file_path)
            self.update_preview()
            
    def set_position_preset(self, position):
        """Set watermark position preset"""
        self.watermark_position.set(position)
        self.update_preview()
        
    def on_canvas_click(self, event):
        """Handle canvas click for dragging"""
        self.dragging = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        
    def on_canvas_drag(self, event):
        """Handle canvas drag"""
        if self.dragging and self.preview_image:
            # Calculate relative position on original image
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            if hasattr(self, 'preview_photo'):
                # Get actual displayed image size
                display_width = self.preview_photo.width()
                display_height = self.preview_photo.height()
                
                # Calculate scale factor
                original_width, original_height = self.preview_image.size
                scale_x = original_width / display_width
                scale_y = original_height / display_height
                
                # Update watermark position
                self.watermark_x = int(event.x * scale_x)
                self.watermark_y = int(event.y * scale_y)
                
                # Set to custom position
                self.watermark_position.set("custom")
                self.update_preview()
                
    def on_canvas_release(self, event):
        """Handle canvas release"""
        self.dragging = False
        
    def export_all_images(self):
        """Export all images with watermarks"""
        if not self.images:
            messagebox.showwarning("警告", "没有图片可导出")
            return
            
        # Choose output directory
        output_dir = filedialog.askdirectory(title="选择输出目录")
        if not output_dir:
            return
            
        # Check if output directory is same as any input directory
        for image_path in self.images:
            input_dir = os.path.dirname(image_path)
            if os.path.samefile(input_dir, output_dir):
                messagebox.showerror("错误", "输出目录不能与输入目录相同，以防止覆盖原文件")
                return
                
        success_count = 0
        
        for i, image_path in enumerate(self.images):
            try:
                # Load image
                with Image.open(image_path) as img:
                    # Apply watermark
                    watermarked = self.apply_watermark(img)
                    
                    # Generate output filename
                    original_name = Path(image_path).stem
                    original_ext = Path(image_path).suffix
                    
                    prefix = self.filename_prefix.get()
                    suffix = self.filename_suffix.get()
                    
                    if self.output_format.get() == "PNG":
                        ext = ".png"
                    else:
                        ext = ".jpg"
                        # Convert to RGB for JPEG
                        if watermarked.mode in ('RGBA', 'LA'):
                            background = Image.new('RGB', watermarked.size, (255, 255, 255))
                            background.paste(watermarked, mask=watermarked.split()[-1] if watermarked.mode == 'RGBA' else None)
                            watermarked = background
                            
                    output_filename = f"{prefix}{original_name}{suffix}{ext}"
                    output_path = os.path.join(output_dir, output_filename)
                    
                    # Save image
                    if self.output_format.get() == "JPEG":
                        watermarked.save(output_path, "JPEG", quality=self.jpeg_quality.get())
                    else:
                        watermarked.save(output_path, "PNG")
                        
                    success_count += 1
                    
            except Exception as e:
                messagebox.showerror("错误", f"导出图片失败 {image_path}: {str(e)}")
                
        messagebox.showinfo("完成", f"成功导出 {success_count}/{len(self.images)} 张图片")
        
    def save_template(self):
        """Save current settings as template"""
        template_name = tk.simpledialog.askstring("保存模板", "请输入模板名称:")
        if not template_name:
            return
            
        template_data = {
            'watermark_text': self.watermark_text.get(),
            'watermark_font_family': self.watermark_font_family.get(),
            'watermark_font_size': self.watermark_font_size.get(),
            'watermark_color': self.watermark_color,
            'watermark_opacity': self.watermark_opacity.get(),
            'watermark_rotation': self.watermark_rotation.get(),
            'watermark_position': self.watermark_position.get(),
            'watermark_type': self.watermark_type.get(),
            'watermark_image_path': self.watermark_image_path.get(),
            'watermark_scale': self.watermark_scale.get(),
            'output_format': self.output_format.get(),
            'jpeg_quality': self.jpeg_quality.get(),
            'filename_prefix': self.filename_prefix.get(),
            'filename_suffix': self.filename_suffix.get()
        }
        
        # Create templates directory if it doesn't exist
        templates_dir = "templates"
        os.makedirs(templates_dir, exist_ok=True)
        
        template_file = os.path.join(templates_dir, f"{template_name}.json")
        
        try:
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("成功", f"模板已保存: {template_name}")
        except Exception as e:
            messagebox.showerror("错误", f"保存模板失败: {str(e)}")
            
    def load_template(self):
        """Load a template"""
        templates_dir = "templates"
        if not os.path.exists(templates_dir):
            messagebox.showwarning("警告", "没有找到模板目录")
            return
            
        template_files = [f for f in os.listdir(templates_dir) if f.endswith('.json')]
        if not template_files:
            messagebox.showwarning("警告", "没有找到模板文件")
            return
            
        # Create selection dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("选择模板")
        dialog.geometry("300x200")
        dialog.resizable(False, False)
        
        tk.Label(dialog, text="选择要加载的模板:").pack(pady=10)
        
        listbox = tk.Listbox(dialog)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        for template_file in template_files:
            template_name = os.path.splitext(template_file)[0]
            listbox.insert(tk.END, template_name)
            
        def load_selected():
            selection = listbox.curselection()
            if selection:
                template_name = listbox.get(selection[0])
                self.load_template_file(template_name)
                dialog.destroy()
                
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="加载", command=load_selected).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
    def load_template_file(self, template_name):
        """Load template from file"""
        template_file = os.path.join("templates", f"{template_name}.json")
        
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
                
            # Apply template data
            self.watermark_text.set(template_data.get('watermark_text', ''))
            self.watermark_font_family.set(template_data.get('watermark_font_family', 'Arial'))
            self.watermark_font_size.set(template_data.get('watermark_font_size', 36))
            self.watermark_color = template_data.get('watermark_color', '#FFFFFF')
            self.watermark_opacity.set(template_data.get('watermark_opacity', 50))
            self.watermark_rotation.set(template_data.get('watermark_rotation', 0))
            self.watermark_position.set(template_data.get('watermark_position', 'center'))
            self.watermark_type.set(template_data.get('watermark_type', 'text'))
            self.watermark_image_path.set(template_data.get('watermark_image_path', ''))
            self.watermark_scale.set(template_data.get('watermark_scale', 100))
            self.output_format.set(template_data.get('output_format', 'PNG'))
            self.jpeg_quality.set(template_data.get('jpeg_quality', 95))
            self.filename_prefix.set(template_data.get('filename_prefix', ''))
            self.filename_suffix.set(template_data.get('filename_suffix', '_watermarked'))
            
            # Update UI
            self.color_label.config(fg=self.watermark_color)
            
            # Show/hide appropriate frames
            if self.watermark_type.get() == "text":
                self.text_frame.pack(fill=tk.X, pady=(0, 5))
                self.image_frame.pack_forget()
            else:
                self.image_frame.pack(fill=tk.X, pady=(0, 5))
                self.text_frame.pack_forget()
                
            self.update_preview()
            messagebox.showinfo("成功", f"模板已加载: {template_name}")
            
        except Exception as e:
            messagebox.showerror("错误", f"加载模板失败: {str(e)}")
            
    def manage_templates(self):
        """Manage templates (delete)"""
        templates_dir = "templates"
        if not os.path.exists(templates_dir):
            messagebox.showwarning("警告", "没有找到模板目录")
            return
            
        template_files = [f for f in os.listdir(templates_dir) if f.endswith('.json')]
        if not template_files:
            messagebox.showwarning("警告", "没有找到模板文件")
            return
            
        # Create management dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("管理模板")
        dialog.geometry("300x250")
        dialog.resizable(False, False)
        
        tk.Label(dialog, text="选择要删除的模板:").pack(pady=10)
        
        listbox = tk.Listbox(dialog, selectmode=tk.MULTIPLE)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        for template_file in template_files:
            template_name = os.path.splitext(template_file)[0]
            listbox.insert(tk.END, template_name)
            
        def delete_selected():
            selections = listbox.curselection()
            if not selections:
                messagebox.showwarning("警告", "请选择要删除的模板")
                return
                
            if messagebox.askyesno("确认", f"确定要删除选中的 {len(selections)} 个模板吗?"):
                for i in reversed(selections):
                    template_name = listbox.get(i)
                    template_file = os.path.join(templates_dir, f"{template_name}.json")
                    try:
                        os.remove(template_file)
                        listbox.delete(i)
                    except Exception as e:
                        messagebox.showerror("错误", f"删除模板失败 {template_name}: {str(e)}")
                        
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="删除选中", command=delete_selected).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="关闭", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
    def save_settings(self):
        """Save current settings"""
        settings = {
            'watermark_text': self.watermark_text.get(),
            'watermark_font_family': self.watermark_font_family.get(),
            'watermark_font_size': self.watermark_font_size.get(),
            'watermark_color': self.watermark_color,
            'watermark_opacity': self.watermark_opacity.get(),
            'watermark_rotation': self.watermark_rotation.get(),
            'watermark_position': self.watermark_position.get(),
            'watermark_type': self.watermark_type.get(),
            'watermark_scale': self.watermark_scale.get(),
            'output_format': self.output_format.get(),
            'jpeg_quality': self.jpeg_quality.get(),
            'filename_prefix': self.filename_prefix.get(),
            'filename_suffix': self.filename_suffix.get()
        }
        
        try:
            with open('settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Save settings error: {str(e)}")
            
    def load_settings(self):
        """Load saved settings"""
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    
                # Apply settings
                self.watermark_text.set(settings.get('watermark_text', 'Sample Watermark'))
                self.watermark_font_family.set(settings.get('watermark_font_family', 'Arial'))
                self.watermark_font_size.set(settings.get('watermark_font_size', 36))
                self.watermark_color = settings.get('watermark_color', '#FFFFFF')
                self.watermark_opacity.set(settings.get('watermark_opacity', 50))
                self.watermark_rotation.set(settings.get('watermark_rotation', 0))
                self.watermark_position.set(settings.get('watermark_position', 'center'))
                self.watermark_type.set(settings.get('watermark_type', 'text'))
                self.watermark_scale.set(settings.get('watermark_scale', 100))
                self.output_format.set(settings.get('output_format', 'PNG'))
                self.jpeg_quality.set(settings.get('jpeg_quality', 95))
                self.filename_prefix.set(settings.get('filename_prefix', ''))
                self.filename_suffix.set(settings.get('filename_suffix', '_watermarked'))
                
                # Update color label
                self.color_label.config(fg=self.watermark_color)
                
        except Exception as e:
            print(f"Load settings error: {str(e)}")
            
    def on_closing(self):
        """Handle application closing"""
        self.save_settings()
        self.root.destroy()

def main():
    import tkinter.simpledialog
    
    root = tk.Tk()
    app = WatermarkApp(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Show/hide watermark type frames initially
    if app.watermark_type.get() == "text":
        app.text_frame.pack(fill=tk.X, pady=(0, 5))
    else:
        app.image_frame.pack(fill=tk.X, pady=(0, 5))
    
    root.mainloop()

if __name__ == "__main__":
    main()
