import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import threading
import os
from core import BackgroundRemoverEngine

class AppUI:
    def __init__(self, root):
        self.root = root
        self.root.title("一键背景去除工具 (U²-Net)")
        self.root.geometry("800x600")
        
        # 初始化引擎
        self.engine = BackgroundRemoverEngine()
        self.current_result = None
        self.current_mask = None
        
        self._setup_ui()

    def _setup_ui(self):
        # 顶部控制栏
        control_frame = tk.Frame(self.root, pady=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)
        
        btn_opts = {'padx': 10, 'pady': 5, 'side': tk.LEFT}
        
        self.btn_load = tk.Button(control_frame, text="1. 选择图片", command=self.load_image, bg="#e1e1e1")
        self.btn_load.pack(**btn_opts)
        
        self.status_label = tk.Label(control_frame, text="准备就绪", fg="gray")
        self.status_label.pack(side=tk.LEFT, padx=20)
        
        self.btn_save = tk.Button(control_frame, text="2. 导出 PNG", command=self.save_image, state=tk.DISABLED, bg="#4CAF50", fg="white")
        self.btn_save.pack(side=tk.RIGHT, padx=10)

        # 中间显示区域 (使用 Canvas 方便绘图)
        self.display_frame = tk.Frame(self.root)
        self.display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧：原图
        self.panel_left = tk.Label(self.display_frame, text="原图预览", relief=tk.RIDGE, bg="#f0f0f0")
        self.panel_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # 右侧：结果/蒙版 (这里修改了背景颜色为 white)
        self.panel_right = tk.Label(self.display_frame, text="处理结果", relief=tk.RIDGE, bg="white") 
        self.panel_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        # 底部切换视图
        self.view_var = tk.StringVar(value="result")
        view_frame = tk.Frame(self.root, pady=5)
        view_frame.pack(side=tk.BOTTOM)
        
        tk.Radiobutton(view_frame, text="查看结果图", variable=self.view_var, value="result", command=self.toggle_view).pack(side=tk.LEFT)
        tk.Radiobutton(view_frame, text="查看可视化蒙版", variable=self.view_var, value="mask", command=self.toggle_view).pack(side=tk.LEFT, padx=10)

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.jpeg")])
        if not path:
            return
            
        # 显示原图
        self.original_image_path = path
        img = Image.open(path)
        self._show_image(img, self.panel_left)
        
        # 启动线程处理，避免卡死 UI
        self.status_label.config(text="正在处理中，请稍候...", fg="blue")
        self.btn_load.config(state=tk.DISABLED)
        
        thread = threading.Thread(target=self._process_thread, args=(path,))
        thread.start()

    def _process_thread(self, path):
        result, mask = self.engine.process_image(path)
        
        # 回到主线程更新 UI
        self.root.after(0, lambda: self._update_ui_after_process(result, mask))

    def _update_ui_after_process(self, result, mask):
        self.btn_load.config(state=tk.NORMAL)
        if result:
            self.current_result = result
            self.current_mask = mask
            self.status_label.config(text="处理完成！", fg="green")
            self.btn_save.config(state=tk.NORMAL)
            self.toggle_view() # 刷新显示
        else:
            self.status_label.config(text="处理失败", fg="red")
            messagebox.showerror("错误", "无法处理该图片")

    def toggle_view(self):
        if not self.current_result:
            return
            
        mode = self.view_var.get()
        if mode == "result":
            # 创建一个棋盘格背景来展示透明图 (简单模拟)
            display_img = self._create_checkerboard_bg(self.current_result)
            self._show_image(display_img, self.panel_right)
        else:
            self._show_image(self.current_mask, self.panel_right)

    def _create_checkerboard_bg(self, img_rgba):
        """ 给透明图片加个白色底，方便预览，实际保存还是透明的 """
        # 这里创建一个简单的白色底，模拟棋盘格需要画图比较复杂，暂时用纯白代替
        bg = Image.new("RGBA", img_rgba.size, (255, 255, 255, 255))
        return Image.alpha_composite(bg, img_rgba)

    def _show_image(self, pil_image, label_widget):
        # 缩放图片以适应窗口
        w, h = pil_image.size
        # 限制最大显示尺寸，保持比例
        max_size = 350
        ratio = min(max_size/w, max_size/h)
        new_size = (int(w*ratio), int(h*ratio))
        
        resized = pil_image.resize(new_size, Image.Resampling.LANCZOS)
        tk_img = ImageTk.PhotoImage(resized)
        
        label_widget.config(image=tk_img, text="")
        label_widget.image = tk_img # 保持引用防止被垃圾回收

    def save_image(self):
        if not self.current_result:
            return
        save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png")])
        if save_path:
            self.current_result.save(save_path)
            messagebox.showinfo("成功", f"文件已保存至: {save_path}")