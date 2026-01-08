"""
Deploy ComfyUI app using Python SDK directly
"""
import sys
import os

# Set UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Change to backend directory
backend_dir = r'f:\1\comfyui\backend'
os.chdir(backend_dir)
sys.path.insert(0, backend_dir)

print("=" * 60)
print("Deploying ComfyUI service using Python SDK...")
print("=" * 60)

try:
    # Import the app
    from comfyui_modal import app

    print("\nApp loaded successfully!")
    print(f"App name: {app.name}")

    # Deploy the app
    print("\nDeploying app...")
    print("This may take a few minutes...")
    print("-" * 60)

    # Use app.deploy() method
    deployment = app.deploy(name="qwen-image-edit")

    print("-" * 60)
    print("\nDeployment completed!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Visit: https://modal.com/apps")
    print("2. Find 'qwen-image-edit' app")
    print("3. Copy the 'generate' endpoint URL")
    print("4. Configure it in your frontend")
    print("=" * 60)

except Exception as e:
    print(f"\nError during deployment: {e}")
    print("\nTrying alternative method...")

    # Alternative: use modal.deploy
    try:
        import modal
        print("\nUsing modal.deploy()...")

        # This will trigger deployment
        from comfyui_modal import app

        # The app should auto-deploy when imported
        print("App imported. Check Modal web console for deployment status.")
        print("Visit: https://modal.com/apps")

    except Exception as e2:
        print(f"Alternative method also failed: {e2}")
        print("\nPlease deploy manually using:")
        print("  modal deploy backend/comfyui_modal.py")
        print("Or check the Modal web console.")
