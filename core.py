import io
import numpy as np
from rembg import remove
from PIL import Image

class BackgroundRemoverEngine:
    def __init__(self):
        # 模型会在第一次运行时自动下载，缓存在用户目录下
        pass

    def process_image(self, input_image_path):
        """
        读取图片并移除背景
        :return: (PIL.Image 对象 [RGBA], PIL.Image 对象 [Mask])
        """
        try:
            # 打开图片
            with open(input_image_path, 'rb') as i:
                input_data = i.read()
                
            # 使用 rembg 进行一键抠图，返回字节数据
            output_data = remove(input_data)
            
            # 转换为 PIL Image 对象
            result_image = Image.open(io.BytesIO(output_data)).convert("RGBA")
            
            # 提取蒙版 (Alpha 通道即为蒙版)
            # Alpha 通道中：0是透明（背景），255是实体（前景）
            mask = result_image.split()[3] 
            
            return result_image, mask
            
        except Exception as e:
            print(f"Error in processing: {e}")
            return None, None