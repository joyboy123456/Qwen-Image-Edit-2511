"""
Deploy ComfyUI service to Modal without CLI encoding issues
"""
import sys
import os
import subprocess

# Set UTF-8 encoding for stdout
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Change to project directory
os.chdir(r'f:\1\comfyui')

print("=" * 60)
print("Deploying ComfyUI service to Modal...")
print("=" * 60)

# Run modal deploy command
result = subprocess.run(
    [sys.executable, "-m", "modal", "deploy", "backend/comfyui_modal.py"],
    capture_output=False,
    text=True
)

if result.returncode == 0:
    print("\n" + "=" * 60)
    print("SUCCESS: ComfyUI service deployed!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Go to https://modal.com/apps")
    print("2. Find the 'qwen-image-edit' app")
    print("3. Copy the API endpoint URL")
    print("4. Configure it in your frontend")
else:
    print("\n" + "=" * 60)
    print("Deployment may have completed with warnings")
    print("Check Modal web console for details")
    print("=" * 60)

sys.exit(result.returncode)
