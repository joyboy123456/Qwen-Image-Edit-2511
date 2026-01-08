"""
AI 商品视角转换 Web 应用 - 模型下载脚本

从 HuggingFace 下载 Qwen-Image-Edit-2511 模型和相关 LoRA 权重。
使用 huggingface_hub 库进行下载，支持断点续传和缓存。

Requirements:
- 5.5: 从 HuggingFace 加载模型
- 5.6: 支持 qwen_image_vae, qwen_2.5_vl_7b, Qwen-Image-Edit-2511
- 5.7: 支持 Lightning LoRA 权重
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ModelInfo:
    """模型信息"""
    name: str                    # 本地文件名
    repo_id: str                 # HuggingFace 仓库 ID
    filename: str                # HuggingFace 文件路径
    subfolder: Optional[str]     # HuggingFace 子文件夹
    local_dir: str               # 本地目录类型 (vae, clip, unet, loras)


# ============================================================================
# 模型配置
# ============================================================================

# 模型下载配置
# 基于 Colab notebook 中的下载链接
MODELS: List[ModelInfo] = [
    # VAE - qwen_image_vae.safetensors
    # https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/vae/qwen_image_vae.safetensors
    ModelInfo(
        name="qwen_image_vae.safetensors",
        repo_id="Comfy-Org/Qwen-Image_ComfyUI",
        filename="qwen_image_vae.safetensors",
        subfolder="split_files/vae",
        local_dir="vae",
    ),
    
    # CLIP - qwen_2.5_vl_7b.safetensors (fp8 scaled version)
    # https://huggingface.co/Comfy-Org/HunyuanVideo_1.5_repackaged/resolve/main/split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors
    ModelInfo(
        name="qwen_2.5_vl_7b.safetensors",
        repo_id="Comfy-Org/HunyuanVideo_1.5_repackaged",
        filename="qwen_2.5_vl_7b_fp8_scaled.safetensors",
        subfolder="split_files/text_encoders",
        local_dir="clip",
    ),
    
    # UNET - Qwen-Image-Edit-2511.safetensors (bf16 version)
    # https://huggingface.co/Comfy-Org/Qwen-Image-Edit_ComfyUI/resolve/main/split_files/diffusion_models/qwen_image_edit_2511_bf16.safetensors
    ModelInfo(
        name="Qwen-Image-Edit-2511.safetensors",
        repo_id="Comfy-Org/Qwen-Image-Edit_ComfyUI",
        filename="qwen_image_edit_2511_bf16.safetensors",
        subfolder="split_files/diffusion_models",
        local_dir="unet",
    ),
    
    # LoRA - Lightning 4-steps
    # https://huggingface.co/lightx2v/Qwen-Image-Lightning/resolve/main/Qwen-Image-Lightning-4steps-V1.0.safetensors
    ModelInfo(
        name="Qwen-Image-Lightning-4steps-V1.0.safetensors",
        repo_id="lightx2v/Qwen-Image-Lightning",
        filename="Qwen-Image-Lightning-4steps-V1.0.safetensors",
        subfolder=None,
        local_dir="loras",
    ),
    
    # LoRA - Lightning 8-steps
    # https://huggingface.co/lightx2v/Qwen-Image-Lightning/resolve/main/Qwen-Image-Lightning-8steps-V1.0.safetensors
    ModelInfo(
        name="Qwen-Image-Lightning-8steps-V1.0.safetensors",
        repo_id="lightx2v/Qwen-Image-Lightning",
        filename="Qwen-Image-Lightning-8steps-V1.0.safetensors",
        subfolder=None,
        local_dir="loras",
    ),
]


def get_model_url(model: ModelInfo) -> str:
    """
    获取模型的 HuggingFace 下载 URL
    
    Args:
        model: 模型信息
        
    Returns:
        完整的下载 URL
    """
    base_url = f"https://huggingface.co/{model.repo_id}/resolve/main"
    if model.subfolder:
        return f"{base_url}/{model.subfolder}/{model.filename}"
    return f"{base_url}/{model.filename}"


def download_model_with_hf_hub(
    model: ModelInfo,
    cache_dir: Path,
    force_download: bool = False,
) -> Path:
    """
    使用 huggingface_hub 下载模型
    
    Args:
        model: 模型信息
        cache_dir: 缓存目录
        force_download: 是否强制重新下载
        
    Returns:
        下载后的文件路径
    """
    from huggingface_hub import hf_hub_download
    
    # 目标目录
    target_dir = cache_dir / model.local_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / model.name
    
    # 如果文件已存在且不强制下载，直接返回
    if target_path.exists() and not force_download:
        print(f"✅ {model.name} 已存在于缓存")
        return target_path
    
    print(f"📥 下载 {model.name}...")
    print(f"   仓库: {model.repo_id}")
    print(f"   文件: {model.subfolder}/{model.filename}" if model.subfolder else f"   文件: {model.filename}")
    
    try:
        # 使用 hf_hub_download 下载
        downloaded_path = hf_hub_download(
            repo_id=model.repo_id,
            filename=f"{model.subfolder}/{model.filename}" if model.subfolder else model.filename,
            local_dir=str(target_dir),
            local_dir_use_symlinks=False,
            force_download=force_download,
        )
        
        # 如果下载的文件名与目标文件名不同，重命名
        downloaded_path = Path(downloaded_path)
        if downloaded_path.name != model.name:
            # 移动文件到目标位置
            import shutil
            shutil.move(str(downloaded_path), str(target_path))
            # 清理可能的空目录
            try:
                downloaded_path.parent.rmdir()
            except OSError:
                pass
        
        print(f"✅ {model.name} 下载完成")
        return target_path
        
    except Exception as e:
        print(f"❌ {model.name} 下载失败: {e}")
        raise


def download_all_models(
    cache_dir: Path,
    force_download: bool = False,
) -> Dict[str, Path]:
    """
    下载所有模型
    
    Args:
        cache_dir: 缓存目录
        force_download: 是否强制重新下载
        
    Returns:
        模型名称到文件路径的映射
    """
    print("=" * 60)
    print("📦 开始下载 Qwen-Image-Edit-2511 模型...")
    print("=" * 60)
    
    results = {}
    failed = []
    
    for model in MODELS:
        try:
            path = download_model_with_hf_hub(model, cache_dir, force_download)
            results[model.name] = path
        except Exception as e:
            failed.append((model.name, str(e)))
    
    print("\n" + "=" * 60)
    if failed:
        print("⚠️ 以下模型下载失败:")
        for name, error in failed:
            print(f"   - {name}: {error}")
    else:
        print("✅ 所有模型下载成功!")
    print("=" * 60)
    
    return results


def verify_models(cache_dir: Path) -> Dict[str, bool]:
    """
    验证模型文件是否存在
    
    Args:
        cache_dir: 缓存目录
        
    Returns:
        模型名称到存在状态的映射
    """
    results = {}
    for model in MODELS:
        target_path = cache_dir / model.local_dir / model.name
        results[model.name] = target_path.exists()
    return results


def get_missing_models(cache_dir: Path) -> List[ModelInfo]:
    """
    获取缺失的模型列表
    
    Args:
        cache_dir: 缓存目录
        
    Returns:
        缺失的模型列表
    """
    missing = []
    for model in MODELS:
        target_path = cache_dir / model.local_dir / model.name
        if not target_path.exists():
            missing.append(model)
    return missing


# ============================================================================
# 命令行入口
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="下载 Qwen-Image-Edit-2511 模型")
    parser.add_argument(
        "--cache-dir",
        type=str,
        default="/cache/models",
        help="模型缓存目录 (默认: /cache/models)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="强制重新下载所有模型",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="仅验证模型是否存在",
    )
    
    args = parser.parse_args()
    cache_dir = Path(args.cache_dir)
    
    if args.verify:
        print("🔍 验证模型文件...")
        results = verify_models(cache_dir)
        for name, exists in results.items():
            status = "✅" if exists else "❌"
            print(f"   {status} {name}")
    else:
        download_all_models(cache_dir, force_download=args.force)
