"""
Simple model download script without Unicode characters
"""
import modal

app = modal.App("download-models")
vol = modal.Volume.from_name("qwen-models", create_if_missing=True)

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("huggingface_hub")
)

@app.function(
    image=image,
    volumes={"/cache": vol},
    timeout=3600,
)
def download_models():
    """Download all models to Modal Volume"""
    from huggingface_hub import hf_hub_download
    from pathlib import Path
    import shutil

    cache_dir = Path("/cache/models")

    # Model configurations
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
    print("Downloading Qwen-Image-Edit-2511 models...")
    print("=" * 60)

    for model in models:
        target_dir = cache_dir / model["local_dir"]
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / model["name"]

        if target_path.exists():
            print(f"SKIP: {model['name']} already exists")
            continue

        print(f"Downloading: {model['name']}")
        print(f"  Repo: {model['repo_id']}")
        print(f"  File: {model['filename']}")

        try:
            downloaded_path = hf_hub_download(
                repo_id=model["repo_id"],
                filename=model["filename"],
                local_dir=str(target_dir),
                local_dir_use_symlinks=False,
            )

            # Rename file to target name
            downloaded_path = Path(downloaded_path)
            if downloaded_path.name != model["name"]:
                shutil.move(str(downloaded_path), str(target_path))
                # Clean up empty directories
                try:
                    for parent in downloaded_path.parents:
                        if parent == target_dir:
                            break
                        parent.rmdir()
                except OSError:
                    pass

            print(f"SUCCESS: {model['name']} downloaded")
        except Exception as e:
            print(f"ERROR: {model['name']} failed: {e}")
            raise

    print("=" * 60)
    print("All models downloaded successfully!")
    print("=" * 60)

    # Commit volume changes
    vol.commit()
    print("Volume changes committed!")

@app.local_entrypoint()
def main():
    download_models.remote()
