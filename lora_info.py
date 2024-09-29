import os
import torch
import hashlib
import json
import numpy as np
from PIL import Image,ImageSequence,ImageOps
import folder_paths
import node_helpers
directory_path = os.path.dirname(os.path.abspath(__file__))
lora_json = os.path.join(directory_path,"lora.json")
example_image_folder = os.path.join(directory_path,"images")
# 计算文件sha256 hash
def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()      
# 从json文件中获取Lora属性
def get_lora_info(lora_file_name):
    lora_info = None
    with open(lora_json, 'r', encoding='utf-8') as file:
        lora_data = json.load(file)
        lora_data = lora_data['loras']
        lora_info = next((item for item in lora_data if item['name'] == lora_file_name),None)
    return lora_info
class LoraInfo:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        LORA_LIST = sorted(folder_paths.get_filename_list("loras"), key=str.lower)
        return {
            "required": {
                "lora_name": (LORA_LIST, ),
            },
        }
    RETURN_TYPES = ("STRING","STRING","STRING","IMAGE",)
    RETURN_NAMES = ("TRIGGER_WORDS",'LORA_DESCRIPTION','LORA_HASH','EXAMPLE_IMAGE')
    FUNCTION = "lora_info"
    CATEGORY = "YCYY/utils"

    def lora_info(self, lora_name):
        trigger_words = None
        lora_description = None
        example_list = None
        output_image = None
        lora_file_path = folder_paths.get_full_path("loras", lora_name)
        lora_file_name = os.path.splitext(os.path.basename(lora_file_path))[0]
        lora_hash = calculate_sha256(lora_file_path)
        lora_data = get_lora_info(lora_file_name)
        if lora_data is not None:
            trigger_words = lora_data['triggerWords']
            lora_description = lora_data['description']
            example_list = lora_data['example']
        if example_list is not None:
            output_list = []
            image_width = None
            for item in example_list:
                image_path = os.path.join(example_image_folder,item)
                i = Image.open(image_path)
                i = ImageOps.exif_transpose(i)
                image = i.convert("RGB")
                if image_width is None:
                    image_width = image.size[0]
                aspect_ratio = image.size[1]/image.size[0]
                image_height = int(image_width * aspect_ratio)
                image = image.resize((image_width, image_height), Image.LANCZOS)
                image = np.array(image).astype(np.float32) / 255.0
                image = torch.from_numpy(image)[None,]
                output_list.append(image)
            output_image = torch.cat(output_list, dim=1) 
        return (trigger_words,lora_description,lora_hash,output_image)

NODE_CLASS_MAPPINGS = {
    "LoraInfo": LoraInfo
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoraInfo": "Lora Info"
}          