"""
AI 商品视角转换 Web 应用 - ComfyUI 工作流执行器

实现工作流参数注入和执行逻辑。

Requirements:
- 6.3: 使用用户提供的提示词配置 TextEncodeQwenImageEditPlus 节点
- 6.4: 使用用户提供的参数配置 KSampler 节点（steps, cfg, seed）
- 6.5: 缩放输入图片使用 ImageScaleToTotalPixels
- 6.6: 使用 VAEDecode 解码 latent 输出为图片
"""

import copy
import json
import random
from pathlib import Path
from typing import Any, Dict, Optional, Union

from .workflow_template import (
    get_workflow_template,
    INPUT_IMAGE_PLACEHOLDER,
    PROMPT_PLACEHOLDER,
    SEED_PLACEHOLDER,
    STEPS_PLACEHOLDER,
    CFG_PLACEHOLDER,
    OUTPUT_PREFIX_PLACEHOLDER,
    DEFAULT_STEPS,
    DEFAULT_CFG,
    DEFAULT_OUTPUT_PREFIX,
)


# ============================================================================
# 工作流参数注入
# ============================================================================

def inject_workflow_parameters(
    workflow: Dict[str, Any],
    input_image: str,
    prompt: str,
    steps: int = DEFAULT_STEPS,
    cfg: float = DEFAULT_CFG,
    seed: Optional[Union[int, str]] = None,
    output_prefix: str = DEFAULT_OUTPUT_PREFIX,
) -> Dict[str, Any]:
    """
    将用户参数注入到工作流模板中
    
    Args:
        workflow: 工作流模板字典
        input_image: 输入图片文件名（已保存到 ComfyUI input 目录）
        prompt: 用户提示词（视角描述）
        steps: 生成步数 (4-8)
        cfg: CFG 强度 (1.0-5.0)
        seed: 随机种子（None 表示随机）
        output_prefix: 输出文件前缀
    
    Returns:
        Dict[str, Any]: 注入参数后的工作流字典
        
    Requirements:
        - 6.3: 注入用户提示词到 TextEncodeQwenImageEditPlus 节点
        - 6.4: 注入 KSampler 参数（steps, cfg, seed）
    """
    # 深拷贝工作流，避免修改原始模板
    result = copy.deepcopy(workflow)
    
    # 处理种子值
    if seed is None:
        seed_value = random.randint(0, 2**63 - 1)
    elif isinstance(seed, str):
        seed_value = int(seed) if seed.isdigit() else random.randint(0, 2**63 - 1)
    else:
        seed_value = seed
    
    # 注入输入图片路径 (LoadImage 节点 - node 31)
    result = _inject_input_image(result, input_image)
    
    # 注入用户提示词 (TextEncodeQwenImageEditPlus 节点 - node 115)
    result = _inject_prompt(result, prompt)
    
    # 注入 KSampler 参数 (node 14)
    result = _inject_ksampler_params(result, steps, cfg, seed_value)
    
    # 注入输出前缀 (SaveImage 节点 - node 80)
    result = _inject_output_prefix(result, output_prefix)
    
    return result


def _inject_input_image(workflow: Dict[str, Any], input_image: str) -> Dict[str, Any]:
    """
    注入输入图片路径到 LoadImage 节点
    
    Args:
        workflow: 工作流字典
        input_image: 输入图片文件名
    
    Returns:
        Dict[str, Any]: 更新后的工作流字典
    """
    if "31" in workflow:
        workflow["31"]["inputs"]["image"] = input_image
    return workflow


def _inject_prompt(workflow: Dict[str, Any], prompt: str) -> Dict[str, Any]:
    """
    注入用户提示词到 TextEncodeQwenImageEditPlus 节点
    
    Requirement 6.3: 使用用户提供的提示词配置 TextEncodeQwenImageEditPlus 节点
    
    Args:
        workflow: 工作流字典
        prompt: 用户提示词
    
    Returns:
        Dict[str, Any]: 更新后的工作流字典
    """
    if "115" in workflow:
        workflow["115"]["inputs"]["text"] = prompt
    return workflow


def _inject_ksampler_params(
    workflow: Dict[str, Any],
    steps: int,
    cfg: float,
    seed: int,
) -> Dict[str, Any]:
    """
    注入 KSampler 参数
    
    Requirement 6.4: 使用用户提供的参数配置 KSampler 节点（steps, cfg, seed）
    
    Args:
        workflow: 工作流字典
        steps: 生成步数
        cfg: CFG 强度
        seed: 随机种子
    
    Returns:
        Dict[str, Any]: 更新后的工作流字典
    """
    if "14" in workflow:
        workflow["14"]["inputs"]["steps"] = steps
        workflow["14"]["inputs"]["cfg"] = cfg
        workflow["14"]["inputs"]["seed"] = seed
    return workflow


def _inject_output_prefix(workflow: Dict[str, Any], output_prefix: str) -> Dict[str, Any]:
    """
    注入输出文件前缀到 SaveImage 节点
    
    Args:
        workflow: 工作流字典
        output_prefix: 输出文件前缀
    
    Returns:
        Dict[str, Any]: 更新后的工作流字典
    """
    if "80" in workflow:
        workflow["80"]["inputs"]["filename_prefix"] = output_prefix
    return workflow


# ============================================================================
# 工作流创建和保存
# ============================================================================

def create_workflow(
    input_image: str,
    prompt: str,
    steps: int = DEFAULT_STEPS,
    cfg: float = DEFAULT_CFG,
    seed: Optional[Union[int, str]] = None,
    output_prefix: str = DEFAULT_OUTPUT_PREFIX,
) -> Dict[str, Any]:
    """
    创建一个完整的工作流，包含所有用户参数
    
    Args:
        input_image: 输入图片文件名
        prompt: 用户提示词
        steps: 生成步数 (4-8)
        cfg: CFG 强度 (1.0-5.0)
        seed: 随机种子
        output_prefix: 输出文件前缀
    
    Returns:
        Dict[str, Any]: 完整的工作流字典
    """
    template = get_workflow_template()
    return inject_workflow_parameters(
        workflow=template,
        input_image=input_image,
        prompt=prompt,
        steps=steps,
        cfg=cfg,
        seed=seed,
        output_prefix=output_prefix,
    )


def save_workflow_to_file(workflow: Dict[str, Any], filepath: Union[str, Path]) -> Path:
    """
    将工作流保存到 JSON 文件
    
    Args:
        workflow: 工作流字典
        filepath: 保存路径
    
    Returns:
        Path: 保存的文件路径
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(workflow, f, indent=2, ensure_ascii=False)
    
    return filepath


def load_workflow_from_file(filepath: Union[str, Path]) -> Dict[str, Any]:
    """
    从 JSON 文件加载工作流
    
    Args:
        filepath: 文件路径
    
    Returns:
        Dict[str, Any]: 工作流字典
    """
    filepath = Path(filepath)
    
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================================
# 工作流验证
# ============================================================================

def validate_workflow_parameters(
    steps: int,
    cfg: float,
    seed: Optional[Union[int, str]] = None,
) -> tuple[bool, str]:
    """
    验证工作流参数是否在有效范围内
    
    Args:
        steps: 生成步数
        cfg: CFG 强度
        seed: 随机种子
    
    Returns:
        tuple[bool, str]: (是否有效, 错误消息)
    """
    # 验证 steps (4-8)
    if not isinstance(steps, int) or steps < 4 or steps > 8:
        return False, f"steps must be an integer between 4 and 8, got {steps}"
    
    # 验证 cfg (1.0-5.0)
    if not isinstance(cfg, (int, float)) or cfg < 1.0 or cfg > 5.0:
        return False, f"cfg must be a number between 1.0 and 5.0, got {cfg}"
    
    # 验证 seed (可选，必须是数字字符串或整数)
    if seed is not None:
        if isinstance(seed, str):
            if seed and not seed.isdigit():
                return False, f"seed must be a numeric string, got '{seed}'"
        elif not isinstance(seed, int):
            return False, f"seed must be an integer or numeric string, got {type(seed).__name__}"
    
    return True, ""


# ============================================================================
# 工作流节点 ID 常量
# ============================================================================

# 节点 ID 映射，方便引用
NODE_IDS = {
    "vae_loader": "22",
    "clip_loader": "76",
    "unet_loader": "77",
    "lora_4steps": "125",
    "lora_8steps": "20",
    "load_image": "31",
    "image_scale": "39",
    "vae_encode": "10",
    "text_encode_positive": "115",
    "text_encode_negative": "3",
    "model_sampling": "2",
    "cfg_norm": "1",
    "ksampler": "14",
    "vae_decode": "12",
    "save_image": "80",
}
