"""
AI 商品视角转换 Web 应用 - Modal 后端

基于 Modal 的无服务器 GPU 后端，运行 ComfyUI + Qwen-Image-Edit-2511 工作流。
核心功能：用户上传商品/人物图片，选择多个目标视角，批量生成多张不同视角的图片。

Requirements:
- 5.1: Modal 应用使用 L40S 或 A100 GPU
- 5.2: 使用 @modal.cls 装饰器和 scaledown_window 保活
- 5.3: 使用 @modal.enter 装饰器启动 ComfyUI 服务器
- 5.4: 使用 Modal volumes 缓存模型
- 5.5: 从 HuggingFace 加载模型并缓存
- 5.6: 支持 qwen_image_vae, qwen_2.5_vl_7b, Qwen-Image-Edit-2511
- 5.7: 支持 Lightning LoRA 权重
- 10.1: 模型加载失败时记录错误并返回服务不可用响应
- 10.2: 图像生成失败时返回描述性错误消息
- 10.5: 生成超时后返回超时错误
"""

import modal
import subprocess
import os
import shutil
import logging
from pathlib import Path
from typing import List, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Modal 应用配置
# ============================================================================

app = modal.App("qwen-image-edit")

# 模型缓存卷 - 避免重复下载模型 (Requirement 5.4)
vol = modal.Volume.from_name("qwen-models", create_if_missing=True)

# ============================================================================
# Docker 镜像配置
# ============================================================================

# 模型下载函数 - 在镜像构建时执行
def download_models():
    """
    下载所有模型到缓存目录
    
    此函数在 Modal 镜像构建时执行，将模型下载到 /cache/models 目录。
    """
    from huggingface_hub import hf_hub_download
    import os
    from pathlib import Path
    
    cache_dir = Path("/cache/models")
    
    # 模型配置
    models = [
        # VAE
        {
            "name": "qwen_image_vae.safetensors",
            "repo_id": "Comfy-Org/Qwen-Image_ComfyUI",
            "filename": "split_files/vae/qwen_image_vae.safetensors",
            "local_dir": "vae",
        },
        # CLIP
        {
            "name": "qwen_2.5_vl_7b.safetensors",
            "repo_id": "Comfy-Org/HunyuanVideo_1.5_repackaged",
            "filename": "split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors",
            "local_dir": "clip",
        },
        # UNET
        {
            "name": "Qwen-Image-Edit-2511.safetensors",
            "repo_id": "Comfy-Org/Qwen-Image-Edit_ComfyUI",
            "filename": "split_files/diffusion_models/qwen_image_edit_2511_bf16.safetensors",
            "local_dir": "unet",
        },
        # LoRA - 4 steps
        {
            "name": "Qwen-Image-Lightning-4steps-V1.0.safetensors",
            "repo_id": "lightx2v/Qwen-Image-Lightning",
            "filename": "Qwen-Image-Lightning-4steps-V1.0.safetensors",
            "local_dir": "loras",
        },
        # LoRA - 8 steps
        {
            "name": "Qwen-Image-Lightning-8steps-V1.0.safetensors",
            "repo_id": "lightx2v/Qwen-Image-Lightning",
            "filename": "Qwen-Image-Lightning-8steps-V1.0.safetensors",
            "local_dir": "loras",
        },
    ]
    
    print("=" * 60)
    print("📦 下载 Qwen-Image-Edit-2511 模型...")
    print("=" * 60)
    
    for model in models:
        target_dir = cache_dir / model["local_dir"]
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / model["name"]
        
        if target_path.exists():
            print(f"✅ {model['name']} 已存在")
            continue
        
        print(f"📥 下载 {model['name']}...")
        print(f"   仓库: {model['repo_id']}")
        print(f"   文件: {model['filename']}")
        
        try:
            downloaded_path = hf_hub_download(
                repo_id=model["repo_id"],
                filename=model["filename"],
                local_dir=str(target_dir),
                local_dir_use_symlinks=False,
            )
            
            # 重命名文件到目标名称
            downloaded_path = Path(downloaded_path)
            if downloaded_path.name != model["name"]:
                import shutil
                shutil.move(str(downloaded_path), str(target_path))
                # 清理空目录
                try:
                    for parent in downloaded_path.parents:
                        if parent == target_dir:
                            break
                        parent.rmdir()
                except OSError:
                    pass
            
            print(f"✅ {model['name']} 下载完成")
        except Exception as e:
            print(f"❌ {model['name']} 下载失败: {e}")
            raise
    
    print("=" * 60)
    print("✅ 所有模型下载完成!")
    print("=" * 60)


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
        # 安装 ComfyUI
        "comfy --skip-prompt install --nvidia",
    )
    .run_commands(
        # 安装自定义节点
        "cd /root/comfy/ComfyUI/custom_nodes && "
        "git clone https://github.com/lrzjason/Comfyui-QwenEditUtils && "
        "git clone https://github.com/city96/ComfyUI-GGUF && "
        "git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack was-node-suite-comfyui && "
        "git clone https://github.com/yolain/ComfyUI-Easy-Use",
    )
)

# ============================================================================
# 模型路径配置
# ============================================================================

COMFYUI_ROOT = Path("/root/comfy/ComfyUI")
CACHE_ROOT = Path("/cache")

# 模型目录映射：缓存目录 -> ComfyUI 目录
MODEL_PATHS = {
    "vae": {
        "cache": CACHE_ROOT / "models" / "vae",
        "comfyui": COMFYUI_ROOT / "models" / "vae",
    },
    "clip": {
        "cache": CACHE_ROOT / "models" / "clip",
        "comfyui": COMFYUI_ROOT / "models" / "clip",
    },
    "unet": {
        "cache": CACHE_ROOT / "models" / "unet",
        "comfyui": COMFYUI_ROOT / "models" / "diffusion_models",  # ComfyUI 使用 diffusion_models 目录
    },
    "loras": {
        "cache": CACHE_ROOT / "models" / "loras",
        "comfyui": COMFYUI_ROOT / "models" / "loras",
    },
}

# 模型文件列表 (Requirements 5.6, 5.7)
MODELS = {
    "vae": ["qwen_image_vae.safetensors"],
    "clip": ["qwen_2.5_vl_7b.safetensors"],
    "unet": ["Qwen-Image-Edit-2511.safetensors"],
    "loras": [
        "Qwen-Image-Lightning-4steps-V1.0.safetensors",
        "Qwen-Image-Lightning-8steps-V1.0.safetensors",
    ],
}

# ============================================================================
# 预设视角提示词
# ============================================================================

PERSPECTIVE_PROMPTS = {
    "front": "Next Scene：正面视角",
    "left_45": "Next Scene：将镜头向左旋转45度",
    "right_45": "Next Scene：将镜头向右旋转45度",
    "top_down": "Next Scene：将镜头转为俯视",
    "bottom_up": "Next Scene：将镜头转为微微仰视",
    "close_up": "Next Scene：将镜头转为特写镜头",
    "wide_angle": "Next Scene：将镜头转为广角镜头",
    "move_forward": "Next Scene：将镜头向前移动",
    "move_backward": "Next Scene：将镜头向后移动",
    "move_left": "Next Scene：将镜头向左移动",
    "move_right": "Next Scene：将镜头向右移动",
}


# ============================================================================
# ComfyUI 服务类
# ============================================================================

@app.cls(
    image=image,
    gpu="L40S",  # Requirement 5.1: L40S 或 A100 GPU
    scaledown_window=300,  # Requirement 5.2: 5分钟保活
    volumes={"/cache": vol},  # Requirement 5.4: 模型缓存卷
    timeout=600,  # 10分钟超时（支持多图生成）
)
class ComfyUI:
    """
    ComfyUI 服务类
    
    使用 Modal 的 @modal.cls 装饰器配置 GPU 和容器设置。
    使用 @modal.enter 装饰器在容器启动时启动 ComfyUI 服务器。
    
    Requirements:
    - 5.3: 使用 @modal.enter 装饰器启动 ComfyUI 服务器
    - 5.8: 暴露 FastAPI 端点
    """
    
    port: int = 8188
    comfyui_process: subprocess.Popen = None
    
    @modal.enter()
    def launch_comfy_background(self):
        """
        容器启动时启动 ComfyUI 服务器 (Requirement 5.3)
        
        1. 设置模型符号链接
        2. 启动 ComfyUI 后台服务
        3. 等待服务器健康检查通过
        
        Requirements:
        - 10.1: 模型加载失败时记录错误
        """
        import time
        
        print("=" * 60)
        print("🚀 启动 ComfyUI 服务器...")
        print("=" * 60)
        
        # 1. 设置模型符号链接
        try:
            self._setup_model_symlinks()
        except Exception as e:
            # Requirement 10.1: 记录模型加载错误
            logger.error(f"Failed to setup model symlinks: {e}")
            raise RuntimeError(f"Model setup failed: {e}")
        
        # 2. 启动 ComfyUI 后台服务
        print(f"\n📡 启动 ComfyUI 服务器 (端口: {self.port})...")
        
        # 使用 comfy launch --background 启动
        cmd = f"comfy launch --background -- --port {self.port} --listen 127.0.0.1"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            error_msg = f"ComfyUI 启动命令失败: {result.stderr}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            raise RuntimeError(f"Failed to start ComfyUI: {result.stderr}")
        
        print(f"✅ ComfyUI 启动命令执行成功")
        
        # 3. 等待服务器健康检查通过
        print("\n⏳ 等待 ComfyUI 服务器就绪...")
        try:
            self._poll_server_health(max_retries=60, delay=2.0)
        except RuntimeError as e:
            # Requirement 10.1: 记录服务器启动失败
            logger.error(f"ComfyUI server health check failed: {e}")
            raise
        
        print("\n" + "=" * 60)
        print("✅ ComfyUI 服务器已就绪!")
        print("=" * 60)
    
    def _setup_model_symlinks(self):
        """
        将缓存的模型链接到 ComfyUI 目录 (Requirement 5.5)
        
        这样可以避免每次容器启动时重新下载模型。
        模型从 /cache/models 目录链接到 ComfyUI 的 models 目录。
        
        Requirements:
        - 10.1: 模型加载失败时记录错误
        
        Raises:
            RuntimeError: 当必需的模型文件缺失时
        """
        print("\n🔗 设置模型符号链接...")
        
        missing_models = []
        
        for model_type, paths in MODEL_PATHS.items():
            cache_dir = paths["cache"]
            comfyui_dir = paths["comfyui"]
            
            # 确保 ComfyUI 目录存在
            comfyui_dir.mkdir(parents=True, exist_ok=True)
            
            # 如果缓存目录不存在，记录警告
            if not cache_dir.exists():
                warning_msg = f"缓存目录不存在: {cache_dir}"
                logger.warning(warning_msg)
                print(f"⚠️ {warning_msg}")
                # 记录所有缺失的模型
                for model_file in MODELS.get(model_type, []):
                    missing_models.append(f"{model_type}/{model_file}")
                continue
            
            # 为每个模型文件创建符号链接
            for model_file in MODELS.get(model_type, []):
                cache_file = cache_dir / model_file
                comfyui_file = comfyui_dir / model_file
                
                if not cache_file.exists():
                    warning_msg = f"模型文件不存在: {cache_file}"
                    logger.warning(warning_msg)
                    print(f"⚠️ {warning_msg}")
                    missing_models.append(f"{model_type}/{model_file}")
                    continue
                
                # 如果目标已存在，先删除
                if comfyui_file.exists() or comfyui_file.is_symlink():
                    comfyui_file.unlink()
                
                # 创建符号链接
                try:
                    os.symlink(cache_file, comfyui_file)
                    print(f"   ✅ {model_file} -> {comfyui_dir.name}/")
                except OSError as e:
                    error_msg = f"创建符号链接失败 {model_file}: {e}"
                    logger.error(error_msg)
                    raise RuntimeError(error_msg)
        
        # 检查是否有必需的模型缺失
        if missing_models:
            error_msg = f"以下模型文件缺失: {', '.join(missing_models)}"
            logger.error(error_msg)
            # 不抛出异常，让 ComfyUI 启动时报告具体错误
            print(f"⚠️ {error_msg}")
            print("   请运行 download_models_to_volume 下载模型")
        
        print("🔗 模型符号链接设置完成")
    
    def _poll_server_health(self, max_retries: int = 60, delay: float = 2.0) -> bool:
        """
        检查 ComfyUI 服务器健康状态
        
        轮询 ComfyUI 的 /system_stats 端点，直到服务器就绪或超时。
        
        Args:
            max_retries: 最大重试次数
            delay: 重试间隔（秒）
            
        Returns:
            bool: 服务器是否健康
            
        Raises:
            RuntimeError: 服务器启动超时
        """
        import time
        import urllib.request
        import urllib.error
        
        url = f"http://127.0.0.1:{self.port}/system_stats"
        
        for i in range(max_retries):
            try:
                with urllib.request.urlopen(url, timeout=5) as response:
                    if response.status == 200:
                        print(f"   ✅ ComfyUI 服务器健康检查通过 (尝试 {i + 1}/{max_retries})")
                        return True
            except (urllib.error.URLError, urllib.error.HTTPError) as e:
                if i % 5 == 0:  # 每 5 次打印一次状态
                    print(f"   ⏳ 等待中... (尝试 {i + 1}/{max_retries})")
            except Exception as e:
                print(f"   ⚠️ 健康检查异常: {e}")
            
            time.sleep(delay)
        
        raise RuntimeError(f"ComfyUI server failed to start after {max_retries * delay} seconds")
    
    def _check_server_health(self) -> bool:
        """
        检查 ComfyUI 服务器当前是否健康
        
        Returns:
            bool: 服务器是否健康
        """
        import urllib.request
        import urllib.error
        
        url = f"http://127.0.0.1:{self.port}/system_stats"
        
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                return response.status == 200
        except (urllib.error.URLError, urllib.error.HTTPError, Exception):
            return False
    
    # ========================================================================
    # 单图推理方法 (Requirement 6.5, 6.6)
    # ========================================================================
    
    @modal.method()
    def infer_single(
        self,
        input_image_base64: str,
        prompt: str,
        steps: int = 8,
        cfg: float = 3.0,
        seed: Optional[str] = None,
        output_prefix: str = "qwen_output",
    ) -> bytes:
        """
        执行单个工作流并返回生成的图片
        
        Args:
            input_image_base64: Base64 编码的输入图片
            prompt: 用户提示词（视角描述）
            steps: 生成步数 (4-8)
            cfg: CFG 强度 (1.0-5.0)
            seed: 随机种子（可选）
            output_prefix: 输出文件前缀
            
        Returns:
            bytes: 生成的图片字节数据
            
        Raises:
            RuntimeError: 当 ComfyUI 服务器不健康时
            TimeoutError: 当工作流执行超时时
            
        Requirements:
            - 6.5: 缩放输入图片使用 ImageScaleToTotalPixels
            - 6.6: 使用 VAEDecode 解码 latent 输出为图片
            - 10.2: 图像生成失败时返回描述性错误消息
        """
        import base64
        import json
        import time
        import uuid
        import urllib.request
        import urllib.error
        from PIL import Image
        import io
        
        # 确保服务器健康 - Requirement 10.1
        if not self._check_server_health():
            error_msg = "ComfyUI server is not healthy"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        # 1. 保存输入图片到 ComfyUI input 目录
        client_id = uuid.uuid4().hex[:8]
        input_filename = f"input_{client_id}.png"
        input_path = COMFYUI_ROOT / "input" / input_filename
        input_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 解码 base64 图片并保存
        try:
            image_data = base64.b64decode(input_image_base64)
            with open(input_path, "wb") as f:
                f.write(image_data)
        except Exception as e:
            error_msg = f"Failed to save input image: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        print(f"📷 输入图片已保存: {input_filename}")
        
        # 2. 创建工作流
        try:
            from .workflow_executor import create_workflow, save_workflow_to_file
            
            workflow = create_workflow(
                input_image=input_filename,
                prompt=prompt,
                steps=steps,
                cfg=cfg,
                seed=seed,
                output_prefix=f"{output_prefix}_{client_id}",
            )
        except Exception as e:
            error_msg = f"Failed to create workflow: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        # 3. 保存工作流到临时文件
        workflow_path = COMFYUI_ROOT / "temp" / f"workflow_{client_id}.json"
        workflow_path.parent.mkdir(parents=True, exist_ok=True)
        save_workflow_to_file(workflow, workflow_path)
        
        print(f"📝 工作流已保存: {workflow_path.name}")
        
        # 4. 通过 ComfyUI API 执行工作流 - Requirement 10.2, 10.5
        try:
            output_image = self._execute_workflow_via_api(workflow, client_id, output_prefix)
        except TimeoutError as e:
            logger.error(f"Workflow execution timed out: {e}")
            raise
        except Exception as e:
            error_msg = f"Workflow execution failed: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        # 5. 清理临时文件
        try:
            input_path.unlink()
            workflow_path.unlink()
        except Exception as e:
            logger.warning(f"Failed to cleanup temp files: {e}")
        
        return output_image
    
    def _execute_workflow_via_api(
        self,
        workflow: dict,
        client_id: str,
        output_prefix: str,
        timeout: int = 120,
    ) -> bytes:
        """
        通过 ComfyUI API 执行工作流
        
        Args:
            workflow: 工作流字典
            client_id: 客户端 ID
            output_prefix: 输出文件前缀
            timeout: 超时时间（秒）
            
        Returns:
            bytes: 生成的图片字节数据
            
        Raises:
            TimeoutError: 当工作流执行超时时 (Requirement 10.5)
            RuntimeError: 当工作流执行失败时 (Requirement 10.2)
        """
        import json
        import time
        import urllib.request
        import urllib.error
        
        api_url = f"http://127.0.0.1:{self.port}"
        
        # 1. 提交工作流到队列
        prompt_data = {
            "prompt": workflow,
            "client_id": client_id,
        }
        
        try:
            req = urllib.request.Request(
                f"{api_url}/prompt",
                data=json.dumps(prompt_data).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode("utf-8"))
                prompt_id = result.get("prompt_id")
                
                # 检查是否有错误
                if "error" in result:
                    error_msg = f"ComfyUI rejected workflow: {result.get('error')}"
                    logger.error(error_msg)
                    raise RuntimeError(error_msg)
                    
        except urllib.error.URLError as e:
            error_msg = f"Failed to submit workflow to ComfyUI: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except urllib.error.HTTPError as e:
            error_msg = f"ComfyUI API error: {e.code} - {e.reason}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        print(f"📤 工作流已提交: prompt_id={prompt_id}")
        
        # 2. 轮询等待执行完成 - Requirement 10.5
        start_time = time.time()
        last_status_check = 0
        
        while time.time() - start_time < timeout:
            elapsed = time.time() - start_time
            
            # 每 10 秒打印一次状态
            if elapsed - last_status_check >= 10:
                print(f"   ⏳ 等待生成完成... ({int(elapsed)}s / {timeout}s)")
                last_status_check = elapsed
            
            # 检查历史记录
            try:
                with urllib.request.urlopen(f"{api_url}/history/{prompt_id}", timeout=5) as response:
                    history = json.loads(response.read().decode("utf-8"))
                    
                    if prompt_id in history:
                        # 检查是否有错误
                        status = history[prompt_id].get("status", {})
                        if status.get("status_str") == "error":
                            error_messages = status.get("messages", [])
                            error_msg = f"ComfyUI workflow failed: {error_messages}"
                            logger.error(error_msg)
                            raise RuntimeError(error_msg)
                        
                        outputs = history[prompt_id].get("outputs", {})
                        # 查找 SaveImage 节点的输出 (node 80)
                        if "80" in outputs:
                            images = outputs["80"].get("images", [])
                            if images:
                                # 获取第一张图片
                                image_info = images[0]
                                filename = image_info.get("filename")
                                subfolder = image_info.get("subfolder", "")
                                
                                print(f"   ✅ 生成完成: {filename}")
                                
                                # 从 ComfyUI 获取图片
                                return self._get_image_from_comfyui(filename, subfolder)
            except urllib.error.HTTPError as e:
                if e.code != 404:
                    logger.warning(f"Error checking history: {e}")
            except Exception as e:
                logger.warning(f"Error checking history: {e}")
            
            time.sleep(1)
        
        # Requirement 10.5: 超时错误
        error_msg = f"Workflow execution timed out after {timeout} seconds"
        logger.error(error_msg)
        raise TimeoutError(error_msg)
    
    def _get_image_from_comfyui(self, filename: str, subfolder: str = "") -> bytes:
        """
        从 ComfyUI 获取生成的图片
        
        Args:
            filename: 图片文件名
            subfolder: 子文件夹
            
        Returns:
            bytes: 图片字节数据
        """
        import urllib.request
        import urllib.parse
        
        params = urllib.parse.urlencode({
            "filename": filename,
            "subfolder": subfolder,
            "type": "output",
        })
        
        url = f"http://127.0.0.1:{self.port}/view?{params}"
        
        with urllib.request.urlopen(url, timeout=30) as response:
            return response.read()
    
    # ========================================================================
    # 批量生成 API 端点 (Requirements 4.6, 4.7, 4.8, 4.9, 9.1, 9.2)
    # ========================================================================
    
    @modal.fastapi_endpoint(method="POST")
    def generate(self, request: dict):
        """
        API 端点：接收批量生成请求
        
        POST /api/generate
        
        Request Body:
            {
                "image": "base64 encoded image",
                "perspectives": [
                    {"id": "left_45", "name": "左侧45°", "prompt": "Next Scene：将镜头向左旋转45度"},
                    ...
                ],
                "steps": 8,
                "cfg_scale": 3.0,
                "seed": "12345"  // optional
            }
        
        Response:
            {
                "images": [
                    {
                        "perspective_id": "left_45",
                        "perspective_name": "左侧45°",
                        "image": "base64 encoded result",
                        "seed_used": "12345"
                    },
                    ...
                ],
                "total_time": 12.5,
                "original_image": "base64 encoded original"
            }
        
        Requirements:
            - 4.6: 验证请求参数
            - 4.7: 为每个选中的视角执行工作流
            - 4.8: 支持批量生成多个视角
            - 4.9: 返回所有生成的图片
            - 9.1: POST /api/generate 端点
            - 9.2: 接受 image, perspectives, steps, cfg_scale, seed 参数
            - 10.1: 模型加载失败时返回服务不可用响应
            - 10.2: 图像生成失败时返回描述性错误消息
            - 10.5: 生成超时后返回超时错误
        """
        import base64
        import time
        from fastapi import Response
        from fastapi.responses import JSONResponse
        
        start_time = time.time()
        
        print("\n" + "=" * 60)
        print("📥 收到生成请求")
        print("=" * 60)
        
        # ====================================================================
        # 0. 检查服务器健康状态 (Requirement 10.1)
        # ====================================================================
        if not self._check_server_health():
            logger.error("ComfyUI server is not healthy")
            return JSONResponse(
                status_code=503,
                content={
                    "error": "service_unavailable",
                    "message": "AI 服务暂时不可用，请稍后重试"
                }
            )
        
        # ====================================================================
        # 1. 验证请求参数 (Requirement 4.6)
        # ====================================================================
        
        # 验证 image
        image_base64 = request.get("image")
        if not image_base64:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "validation_error",
                    "message": "image is required"
                }
            )
        
        # 验证 base64 图片格式
        try:
            # 尝试解码 base64
            image_data = base64.b64decode(image_base64)
            if len(image_data) < 100:  # 太小不可能是有效图片
                raise ValueError("Image data too small")
        except Exception as e:
            logger.warning(f"Invalid image data: {e}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": "invalid_image",
                    "message": f"无效的 base64 图片数据: {str(e)}"
                }
            )
        
        # 验证 perspectives
        perspectives = request.get("perspectives", [])
        if not perspectives:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "validation_error",
                    "message": "at least one perspective is required"
                }
            )
        
        # 验证每个 perspective 的格式
        for i, p in enumerate(perspectives):
            if not isinstance(p, dict):
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "validation_error",
                        "message": f"perspective[{i}] must be an object"
                    }
                )
            if not p.get("prompt"):
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "validation_error",
                        "message": f"perspective[{i}].prompt is required"
                    }
                )
        
        # 验证 steps (4-8)
        steps = request.get("steps", 8)
        if not isinstance(steps, int) or steps < 4 or steps > 8:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "invalid_params",
                    "message": "steps must be an integer between 4 and 8"
                }
            )
        
        # 验证 cfg_scale (1.0-5.0)
        cfg_scale = request.get("cfg_scale", 3.0)
        if not isinstance(cfg_scale, (int, float)) or cfg_scale < 1.0 or cfg_scale > 5.0:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "invalid_params",
                    "message": "cfg_scale must be a number between 1.0 and 5.0"
                }
            )
        
        # 获取 seed（可选）
        seed = request.get("seed")
        
        print(f"   📊 参数验证通过:")
        print(f"      - 视角数量: {len(perspectives)}")
        print(f"      - Steps: {steps}")
        print(f"      - CFG Scale: {cfg_scale}")
        print(f"      - Seed: {seed or 'random'}")
        
        # ====================================================================
        # 2. 批量生成图片 (Requirements 4.7, 4.8)
        # ====================================================================
        
        generated_images = []
        
        for i, perspective in enumerate(perspectives):
            perspective_id = perspective.get("id", str(i))
            perspective_name = perspective.get("name", f"视角{i+1}")
            prompt = perspective.get("prompt", "")
            
            print(f"\n   🎨 生成视角 {i+1}/{len(perspectives)}: {perspective_name}")
            print(f"      Prompt: {prompt[:50]}...")
            
            try:
                # 调用单图推理方法
                img_bytes = self.infer_single.local(
                    input_image_base64=image_base64,
                    prompt=prompt,
                    steps=steps,
                    cfg=cfg_scale,
                    seed=seed,
                    output_prefix=f"qwen_{perspective_id}",
                )
                
                # 将结果添加到列表
                generated_images.append({
                    "perspective_id": perspective_id,
                    "perspective_name": perspective_name,
                    "image": base64.b64encode(img_bytes).decode("utf-8"),
                    "seed_used": seed if seed else "random",
                })
                
                print(f"      ✅ 生成成功 ({len(img_bytes)} bytes)")
                
            except TimeoutError as e:
                # Requirement 10.5: 超时错误
                error_msg = f"视角 '{perspective_name}' 的生成超时"
                logger.error(f"Generation timeout for {perspective_name}: {e}")
                print(f"      ❌ {error_msg}")
                return JSONResponse(
                    status_code=504,
                    content={
                        "error": "timeout",
                        "message": error_msg
                    }
                )
            except RuntimeError as e:
                # Requirement 10.2: 生成失败
                error_msg = f"视角 '{perspective_name}' 的图像生成失败: {str(e)}"
                logger.error(f"Generation failed for {perspective_name}: {e}")
                print(f"      ❌ {error_msg}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "error": "generation_error",
                        "message": error_msg
                    }
                )
            except Exception as e:
                # 其他未知错误
                error_msg = f"视角 '{perspective_name}' 生成时发生未知错误: {str(e)}"
                logger.error(f"Unknown error for {perspective_name}: {e}")
                print(f"      ❌ {error_msg}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "error": "generation_error",
                        "message": error_msg
                    }
                )
        
        # ====================================================================
        # 3. 返回结果 (Requirement 4.9)
        # ====================================================================
        
        total_time = time.time() - start_time
        
        print(f"\n" + "=" * 60)
        print(f"✅ 批量生成完成!")
        print(f"   - 生成图片数: {len(generated_images)}")
        print(f"   - 总耗时: {total_time:.2f} 秒")
        print("=" * 60)
        
        return JSONResponse(
            content={
                "images": generated_images,
                "total_time": round(total_time, 2),
                "original_image": image_base64,
            },
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            }
        )


# ============================================================================
# 本地测试入口
# ============================================================================

@app.local_entrypoint()
def main():
    """本地测试入口"""
    print("Modal app 'qwen-image-edit' is configured.")
    print(f"GPU: L40S")
    print(f"Scaledown window: 300 seconds")
    print(f"Volume: qwen-models mounted at /cache")


# ============================================================================
# 模型下载函数 (用于预热缓存卷)
# ============================================================================

@app.function(
    image=image,
    volumes={"/cache": vol},
    timeout=3600,  # 1小时超时，模型下载可能需要较长时间
)
def download_models_to_volume():
    """
    下载所有模型到 Modal Volume
    
    此函数用于预热缓存卷，将模型下载到 /cache/models 目录。
    运行方式: modal run backend/comfyui_modal.py::download_models_to_volume
    
    Requirements:
    - 5.5: 从 HuggingFace 加载模型
    - 5.6: 支持 qwen_image_vae, qwen_2.5_vl_7b, Qwen-Image-Edit-2511
    - 5.7: 支持 Lightning LoRA 权重
    """
    download_models()
    
    # 提交卷更改
    vol.commit()
    print("✅ 模型已保存到 Modal Volume")


@app.function(
    image=image,
    volumes={"/cache": vol},
    timeout=60,
)
def verify_models_in_volume():
    """
    验证 Modal Volume 中的模型文件
    
    运行方式: modal run backend/comfyui_modal.py::verify_models_in_volume
    """
    from pathlib import Path
    
    cache_dir = Path("/cache/models")
    
    print("🔍 验证模型文件...")
    print("=" * 60)
    
    all_exist = True
    for model_type, model_files in MODELS.items():
        print(f"\n📁 {model_type}:")
        for model_file in model_files:
            file_path = cache_dir / model_type / model_file
            if file_path.exists():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                print(f"   ✅ {model_file} ({size_mb:.1f} MB)")
            else:
                print(f"   ❌ {model_file} (不存在)")
                all_exist = False
    
    print("\n" + "=" * 60)
    if all_exist:
        print("✅ 所有模型文件已就绪!")
    else:
        print("⚠️ 部分模型文件缺失，请运行 download_models_to_volume 下载")
    print("=" * 60)
