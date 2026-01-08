"""
Check Modal Volume contents
"""
import modal

app = modal.App("check-volume")
vol = modal.Volume.from_name("qwen-models")

@app.function(volumes={"/cache": vol})
def check_models():
    """Check if models exist in volume"""
    from pathlib import Path

    cache_dir = Path("/cache/models")

    print("=" * 60)
    print("Checking models in volume...")
    print("=" * 60)

    if not cache_dir.exists():
        print("ERROR: /cache/models directory does not exist!")
        return False

    models = {
        "vae": ["qwen_image_vae.safetensors"],
        "clip": ["qwen_2.5_vl_7b.safetensors"],
        "unet": ["Qwen-Image-Edit-2511.safetensors"],
        "loras": [
            "Qwen-Image-Lightning-4steps-V1.0.safetensors",
            "Qwen-Image-Lightning-8steps-V1.0.safetensors",
        ],
    }

    all_exist = True
    for model_type, model_files in models.items():
        print(f"\n{model_type}:")
        for model_file in model_files:
            file_path = cache_dir / model_type / model_file
            if file_path.exists():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                print(f"  OK: {model_file} ({size_mb:.1f} MB)")
            else:
                print(f"  MISSING: {model_file}")
                all_exist = False

    print("\n" + "=" * 60)
    if all_exist:
        print("SUCCESS: All models are present!")
    else:
        print("ERROR: Some models are missing!")
    print("=" * 60)

    return all_exist

@app.local_entrypoint()
def main():
    result = check_models.remote()
    if not result:
        print("\nYou need to download models first!")
        print("Run: modal run backend/comfyui_modal.py::download_models_to_volume")
