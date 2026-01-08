# AI 商品视角转换 Web 应用 - Modal 后端

基于 Modal 的无服务器 GPU 后端，运行 ComfyUI + Qwen-Image-Edit-2511 工作流。

## 功能

- 使用 Modal L40S/A100 GPU 进行 AI 图像生成
- 运行 ComfyUI 工作流进行多视角图像转换
- 支持批量生成多个视角的图片
- 模型缓存避免重复下载

## 目录结构

```
backend/
├── __init__.py           # 包初始化
├── comfyui_modal.py      # Modal 应用主文件
├── model_download.py     # 模型下载脚本
├── types.py              # Pydantic 数据模型
├── requirements.txt      # Python 依赖
└── README.md             # 本文档
```

## 配置说明

### Modal 应用配置

- **GPU**: L40S (可选 A100)
- **Scaledown Window**: 300 秒 (5分钟保活)
- **Timeout**: 600 秒 (10分钟，支持多图生成)
- **Volume**: `qwen-models` 挂载到 `/cache`

### 模型文件

模型缓存在 Modal Volume 中：

| 模型类型 | 文件名 | HuggingFace 来源 |
|---------|--------|-----------------|
| VAE | qwen_image_vae.safetensors | Comfy-Org/Qwen-Image_ComfyUI |
| CLIP | qwen_2.5_vl_7b.safetensors | Comfy-Org/HunyuanVideo_1.5_repackaged |
| UNET | Qwen-Image-Edit-2511.safetensors | Comfy-Org/Qwen-Image-Edit_ComfyUI |
| LoRA | Qwen-Image-Lightning-4steps-V1.0.safetensors | lightx2v/Qwen-Image-Lightning |
| LoRA | Qwen-Image-Lightning-8steps-V1.0.safetensors | lightx2v/Qwen-Image-Lightning |

模型存储路径：
- `/cache/models/vae/qwen_image_vae.safetensors`
- `/cache/models/clip/qwen_2.5_vl_7b.safetensors`
- `/cache/models/unet/Qwen-Image-Edit-2511.safetensors`
- `/cache/models/loras/Qwen-Image-Lightning-4steps-V1.0.safetensors`
- `/cache/models/loras/Qwen-Image-Lightning-8steps-V1.0.safetensors`

## 使用方法

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置 Modal

```bash
modal token new
```

### 下载模型到 Modal Volume (首次部署前必须执行)

```bash
# 下载所有模型到 Modal Volume
modal run backend/comfyui_modal.py::download_models_to_volume

# 验证模型是否下载成功
modal run backend/comfyui_modal.py::verify_models_in_volume
```

### 部署应用

```bash
modal deploy backend/comfyui_modal.py
```

### 本地测试

```bash
modal run backend/comfyui_modal.py
```

## API 端点

### POST /api/generate

生成多视角图像。

**请求体**:
```json
{
  "image": "base64_encoded_image",
  "perspectives": [
    {"id": "front", "name": "正面视角", "prompt": "Next Scene：正面视角"},
    {"id": "left_45", "name": "左侧45°", "prompt": "Next Scene：将镜头向左旋转45度"}
  ],
  "steps": 8,
  "cfg_scale": 3.0,
  "seed": "12345"
}
```

**响应**:
```json
{
  "images": [
    {
      "perspective_id": "front",
      "perspective_name": "正面视角",
      "image": "base64_encoded_result",
      "seed_used": "12345"
    }
  ],
  "total_time": 15.5,
  "original_image": "base64_encoded_original"
}
```

## 相关需求

- Requirement 5.1: Modal 应用使用 L40S 或 A100 GPU
- Requirement 5.2: 使用 @modal.cls 装饰器和 scaledown_window 保活
- Requirement 5.3: 使用 @modal.enter 装饰器启动 ComfyUI 服务器
- Requirement 5.4: 使用 Modal volumes 缓存模型
- Requirement 5.5: 从 HuggingFace 加载模型并缓存
- Requirement 5.6: 支持 qwen_image_vae, qwen_2.5_vl_7b, Qwen-Image-Edit-2511
- Requirement 5.7: 支持 Lightning LoRA 权重
