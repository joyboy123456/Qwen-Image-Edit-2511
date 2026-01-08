"""
Download only VAE model to Modal Volume
"""
import modal

app = modal.App("download-vae")
vol = modal.Volume.from_name("qwen-models")

image = modal.Image.debian_slim(python_version="3.11").pip_install("huggingface_hub")

@app.function(image=image, volumes={"/cache": vol}, timeout=1800)
def download_vae():
    from huggingface_hub import hf_hub_download
    from pathlib import Path
    import shutil

    cache_dir = Path("/cache/models")
    target_dir = cache_dir / "vae"
    target_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Downloading VAE model...")
    print("=" * 60)

    try:
        print("Repo: Comfy-Org/Qwen-Image_ComfyUI")
        print("File: split_files/vae/qwen_image_vae.safetensors")

        downloaded_path = hf_hub_download(
            repo_id="Comfy-Org/Qwen-Image_ComfyUI",
            filename="split_files/vae/qwen_image_vae.safetensors",
            local_dir=str(target_dir),
            local_dir_use_symlinks=False,
        )

        print(f"Downloaded to: {downloaded_path}")

        # Check if file exists
        target_path = target_dir / "qwen_image_vae.safetensors"
        downloaded_path = Path(downloaded_path)

        if downloaded_path.name != "qwen_image_vae.safetensors":
            print(f"Renaming {downloaded_path} to {target_path}")
            shutil.move(str(downloaded_path), str(target_path))

            # Clean up empty directories
            try:
                for parent in downloaded_path.parents:
                    if parent == target_dir:
                        break
                    if parent.exists() and not any(parent.iterdir()):
                        parent.rmdir()
                        print(f"Removed empty dir: {parent}")
            except OSError as e:
                print(f"Warning: Could not clean up directories: {e}")

        # Verify file exists
        if target_path.exists():
            size_mb = target_path.stat().st_size / (1024 * 1024)
            print(f"SUCCESS: VAE model downloaded ({size_mb:.1f} MB)")
            print(f"Location: {target_path}")
        else:
            print(f"ERROR: File not found at {target_path}")
            return False

    except Exception as e:
        print(f"ERROR: Failed to download VAE: {e}")
        raise

    print("=" * 60)
    print("Committing volume changes...")
    vol.commit()
    print("Done!")
    print("=" * 60)

    return True

@app.local_entrypoint()
def main():
    result = download_vae.remote()
    if result:
        print("\nVAE model successfully downloaded!")
    else:
        print("\nVAE model download failed!")
