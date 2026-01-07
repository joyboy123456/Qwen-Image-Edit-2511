# 🎨 ComfyUI + Qwen-Image-Edit 2511 一键部署

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/joyboy123456/Qwen-Image-Edit-2511/blob/main/ComfyUI_Qwen_2511.ipynb)

基于 **Qwen-Image-Edit 2511** 模型的 ComfyUI 多视角图像编辑工作流，支持一键部署到 Google Colab。

## ✨ 功能特性

- ✅ **一键部署** - 自动安装 ComfyUI 和所有依赖
- ✅ **模型自动下载** - 包括 Qwen-2.5-VL、VAE、UNET
- ✅ **多视角 LoRA** - 支持镜头转换和 Lightning 加速
- ✅ **预装节点** - 所有工作流必需节点开箱即用
- ✅ **节点检测** - 启动前自动检查缺失节点
- ✅ **工作流预置** - 内置多角度人物展示工作流

## 🚀 快速开始

### 在 Colab 中运行（推荐）

1. 点击上方的 "Open in Colab" 按钮
2. 按顺序运行每个 Cell：
   - **Step 1:** 安装 ComfyUI 和依赖
   - **Step 2:** 安装自定义节点
   - **Step 3:** 下载模型文件
   - **Step 3.5:** 检查节点完整性（可选）
   - **Step 4:** 导入工作流
   - **Step 5:** 启动 ComfyUI

3. 等待 Cloudflare 隧道链接生成
4. 在浏览器中打开链接，开始使用！

### 本地运行

⚠️ **注意：** 此 Notebook 专为 Google Colab 优化，本地运行需要修改：
- 移除 `apt-get` 和 Cloudflared 相关代码
- 调整路径（`/content/ComfyUI` → 本地路径）
- 确保已安装 Python 3.10+ 和 CUDA

## 📦 模型清单

| 类型 | 文件名 | 大小 | 用途 |
|------|--------|------|------|
| VAE | qwen_image_vae.safetensors | ~500MB | 图像编解码 |
| CLIP | qwen_2.5_vl_7b_fp8_scaled.safetensors | ~4GB | 文本理解 |
| UNET | qwen_image_edit_2511_bf16.safetensors | ~8GB | 图像生成 |
| LoRA | Qwen-Image-Lightning-4steps | ~100MB | 4步加速 |
| LoRA | Qwen-Image-Lightning-8steps | ~100MB | 8步高质量 |
| LoRA | 镜头转换.safetensors | ~236MB | 多视角转换 |

**总大小：** 约 13GB

## 🎯 工作流说明

### 内置工作流：多角度人物展示

**节点拓扑：**
```
LoadImage → ImageScale → VAEEncode ─┐
                ↓                     ├→ KSampler → VAEDecode → SaveImage
CLIPLoader → TextEncode ──────────┘
UNETLoader → 镜头转换 LoRA → Lightning LoRA → ModelSampling → CFGNorm ↗
```

**关键参数：**
- **采样器：** Euler
- **步数：** 8 steps（使用 Lightning LoRA）
- **CFG Scale：** 3.0
- **调度器：** Simple

### 使用示例提示词

```
# 正向提示词（Node #115）：
"Next Scene：将镜头向左旋转45度"
"从上方俯视拍摄"
"切换到侧面视角"
"拉近镜头特写"

# 负向提示词（Node #3）：
留空即可
```

## 🔧 自定义节点

此项目预装以下节点：

- [Comfyui-QwenEditUtils](https://github.com/lrzjason/Comfyui-QwenEditUtils) - Qwen 编辑工具
- [ComfyUI-GGUF](https://github.com/city96/ComfyUI-GGUF) - GGUF 格式支持
- [was-node-suite-comfyui](https://github.com/ltdrdata/was-node-suite-comfyui) - WAS 工具集
- [ComfyUI-Easy-Use](https://github.com/yolain/ComfyUI-Easy-Use) - 简化工作流
- [ComfyUI-Manager](https://github.com/ltdrdata/ComfyUI-Manager) - 节点管理器

## ⚠️ 常见问题

### Q: 启动后有红色节点怎么办？

**A:** 在 Colab 环境中：
1. **不要使用 Manager 安装节点**（需要手动重启，很麻烦）
2. 点击 `Runtime → Interrupt execution` 停止运行
3. 重新运行 `Step 5` 启动 ComfyUI
4. 如果问题依旧，检查 Step 2 是否成功安装所有节点

### Q: 模型下载失败怎么办？

**A:**
- 检查 Colab 网络连接
- 尝试重新运行 Step 3
- 使用 `aria2c` 支持断点续传，可多次运行

### Q: 为什么不能在本地 Windows 运行？

**A:** 此 Notebook 包含 Linux 专用命令：
- `apt-get` - Linux 包管理器
- `cloudflared` - 需要 Linux 版本
- 路径使用 `/content/` 前缀

如需本地运行，请：
1. 手动安装 ComfyUI
2. 下载模型到对应目录
3. 导入工作流 JSON 文件

### Q: 生成速度慢怎么办？

**A:**
- Colab 免费版使用 T4 GPU（约 30-60秒/张）
- 升级到 Colab Pro 可使用 V100/A100
- 调整 Lightning LoRA 权重（0.6-1.0）
- 减少采样步数（最低 4 steps）

## 📚 相关资源

- [Qwen-Image-Edit 官方仓库](https://huggingface.co/Qwen/Qwen-Image-Edit-2511)
- [ComfyUI 官方文档](https://github.com/comfyanonymous/ComfyUI)
- [多视角 LoRA](https://huggingface.co/dx8152/Qwen-Edit-2509-Multiple-angles)
- [Lightning LoRA](https://huggingface.co/lightx2v/Qwen-Image-Lightning)

## 📄 许可证

本项目采用 MIT 许可证。

模型许可证请参考各自的 HuggingFace 页面。

## 🙏 致谢

- Qwen 团队提供的强大图像编辑模型
- ComfyUI 社区的节点开发者们
- Google Colab 提供的免费 GPU 资源

---

**Star ⭐ 这个项目，如果它对你有帮助！**
