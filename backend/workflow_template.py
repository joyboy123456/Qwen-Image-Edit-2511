"""
AI 商品视角转换 Web 应用 - ComfyUI 工作流模板

定义 ComfyUI API 格式的工作流 JSON 模板，用于 Qwen-Image-Edit-2511 多视角图像生成。

工作流节点说明：
- LoadImage (31): 加载用户上传的图片
- ImageScaleToTotalPixels (39): 缩放图片到合适尺寸（1 megapixel）
- VAELoader (22): 加载 qwen_image_vae.safetensors
- CLIPLoader (76): 加载 qwen_2.5_vl_7b.safetensors
- UNETLoader (77): 加载 Qwen-Image-Edit-2511.safetensors
- LoraLoaderModelOnly (125): 加载 4-steps LoRA (strength: 0.8)
- LoraLoaderModelOnly (20): 加载 8-steps LoRA (strength: 1.0)
- TextEncodeQwenImageEditPlus (115): 正向提示词编码（用户输入的视角描述）
- TextEncodeQwenImageEditPlus (3): 负向提示词编码（空字符串）
- ModelSamplingAuraFlow (2): 模型采样配置 (shift: 3)
- CFGNorm (1): CFG 归一化 (strength: 1)
- VAEEncode (10): 图片编码为 latent
- KSampler (14): 采样器（steps: 8, cfg: 3, sampler: euler, scheduler: simple）
- VAEDecode (12): latent 解码为图片
- SaveImage (80): 保存生成的图片

Requirements:
- 6.1: 实现 ComfyUI 工作流执行器处理多角度视图工作流
- 6.2: 配置所有必需的节点
"""

from typing import Any, Dict

# ============================================================================
# 动态参数占位符
# ============================================================================

# 这些占位符将在运行时被实际值替换
INPUT_IMAGE_PLACEHOLDER = "__INPUT_IMAGE__"
PROMPT_PLACEHOLDER = "__PROMPT__"
SEED_PLACEHOLDER = "__SEED__"
STEPS_PLACEHOLDER = "__STEPS__"
CFG_PLACEHOLDER = "__CFG__"
OUTPUT_PREFIX_PLACEHOLDER = "__OUTPUT_PREFIX__"


# ============================================================================
# ComfyUI API 格式工作流模板
# ============================================================================

def get_workflow_template() -> Dict[str, Any]:
    """
    获取 ComfyUI API 格式的工作流模板
    
    返回一个包含所有节点配置的字典，动态参数使用占位符。
    
    Returns:
        Dict[str, Any]: 工作流模板字典
    """
    return {
        # VAELoader - 加载 VAE 模型
        "22": {
            "class_type": "VAELoader",
            "inputs": {
                "vae_name": "qwen_image_vae.safetensors"
            }
        },
        
        # CLIPLoader - 加载 CLIP 模型
        "76": {
            "class_type": "CLIPLoader",
            "inputs": {
                "clip_name": "qwen_2.5_vl_7b.safetensors",
                "type": "stable_diffusion",
                "device": "default"
            }
        },
        
        # UNETLoader - 加载 UNET 模型
        "77": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": "Qwen-Image-Edit-2511.safetensors",
                "weight_dtype": "default"
            }
        },
        
        # LoraLoaderModelOnly - 加载 4-steps LoRA
        "125": {
            "class_type": "LoraLoaderModelOnly",
            "inputs": {
                "model": ["77", 0],
                "lora_name": "Qwen-Image-Lightning-4steps-V1.0.safetensors",
                "strength_model": 0.8
            }
        },
        
        # LoraLoaderModelOnly - 加载 8-steps LoRA
        "20": {
            "class_type": "LoraLoaderModelOnly",
            "inputs": {
                "model": ["125", 0],
                "lora_name": "Qwen-Image-Lightning-8steps-V1.0.safetensors",
                "strength_model": 1.0
            }
        },
        
        # LoadImage - 加载用户上传的图片
        "31": {
            "class_type": "LoadImage",
            "inputs": {
                "image": INPUT_IMAGE_PLACEHOLDER,
                "upload": "image"
            }
        },
        
        # ImageScaleToTotalPixels - 缩放图片
        "39": {
            "class_type": "ImageScaleToTotalPixels",
            "inputs": {
                "image": ["31", 0],
                "upscale_method": "lanczos",
                "megapixels": 1,
                "resolution_steps": 1
            }
        },
        
        # VAEEncode - 编码图片为 latent
        "10": {
            "class_type": "VAEEncode",
            "inputs": {
                "pixels": ["39", 0],
                "vae": ["22", 0]
            }
        },
        
        # TextEncodeQwenImageEditPlus - 正向提示词编码（用户输入）
        "115": {
            "class_type": "TextEncodeQwenImageEditPlus",
            "inputs": {
                "clip": ["76", 0],
                "vae": ["22", 0],
                "image1": ["39", 0],
                "text": PROMPT_PLACEHOLDER
            }
        },
        
        # TextEncodeQwenImageEditPlus - 负向提示词编码（空字符串）
        "3": {
            "class_type": "TextEncodeQwenImageEditPlus",
            "inputs": {
                "clip": ["76", 0],
                "vae": ["22", 0],
                "image1": ["39", 0],
                "text": ""
            }
        },
        
        # ModelSamplingAuraFlow - 模型采样配置
        "2": {
            "class_type": "ModelSamplingAuraFlow",
            "inputs": {
                "model": ["20", 0],
                "shift": 3
            }
        },
        
        # CFGNorm - CFG 归一化
        "1": {
            "class_type": "CFGNorm",
            "inputs": {
                "model": ["2", 0],
                "strength": 1
            }
        },
        
        # KSampler - 采样器
        "14": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["1", 0],
                "positive": ["115", 0],
                "negative": ["3", 0],
                "latent_image": ["10", 0],
                "seed": SEED_PLACEHOLDER,
                "control_after_generate": "randomize",
                "steps": STEPS_PLACEHOLDER,
                "cfg": CFG_PLACEHOLDER,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1.0
            }
        },
        
        # VAEDecode - 解码 latent 为图片
        "12": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["14", 0],
                "vae": ["22", 0]
            }
        },
        
        # SaveImage - 保存生成的图片
        "80": {
            "class_type": "SaveImage",
            "inputs": {
                "images": ["12", 0],
                "filename_prefix": OUTPUT_PREFIX_PLACEHOLDER
            }
        }
    }


# ============================================================================
# 默认参数值
# ============================================================================

DEFAULT_STEPS = 8
DEFAULT_CFG = 3.0
DEFAULT_SEED = None  # None 表示随机种子
DEFAULT_OUTPUT_PREFIX = "ComfyUI"
