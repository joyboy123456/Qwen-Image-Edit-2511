"""
Direct Python script to trigger model download without CLI encoding issues
"""
import sys
import os

# Set UTF-8 encoding for stdout
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Change to backend directory
backend_dir = r'f:\1\comfyui\backend'
os.chdir(backend_dir)

# Add backend to path
sys.path.insert(0, backend_dir)

# Import modal
import modal

# Get the app
from download_models_simple import app, download_models

print("Starting model download...")
print("This will run in detached mode on Modal cloud.")
print("=" * 60)

# Run the function remotely
with app.run():
    result = download_models.remote()
    print("=" * 60)
    print("Model download completed!")
    print("=" * 60)
