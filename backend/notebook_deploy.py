# Modal Notebook 部署脚本
# 请在 Modal Web 控制台的 Notebooks 中运行此代码

import modal

# 定义应用
app = modal.App("qwen-image-edit")

# 模型缓存卷
vol = modal.Volume.from_name("qwen-models", create_if_missing=True)

# Docker 镜像配置
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install(
        "git",
        "wget",
        "aria2",
        "libgl1-mesa-glx",
        "libglib2.0-0",
    )
    .pip_install(
        "torch==2.1.0",
        "torchvision==0.16.0",
        "torchaudio==2.1.0",
        "comfy-cli",
        "fastapi",
        "uvicorn",
        "pydantic",
        "huggingface_hub",
        "Pillow",
    )
    .run_commands(
        "comfy --skip-prompt install --nvidia",
    )
    .run_commands(
        "cd /root/comfy/ComfyUI/custom_nodes && "
        "git clone https://github.com/lrzjason/Comfyui-QwenEditUtils && "
        "git clone https://github.com/city96/ComfyUI-GGUF && "
        "git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack was-node-suite-comfyui && "
        "git clone https://github.com/yolain/ComfyUI-Easy-Use",
    )
)

print("Image configuration complete!")
print("Now deploying the full app from local file...")
print("\nPlease run this in your local terminal:")
print("  cd f:\\1\\comfyui")
print("  modal deploy backend/comfyui_modal.py")
print("\nOr copy the entire comfyui_modal.py content to a Modal Notebook and deploy from there.")
