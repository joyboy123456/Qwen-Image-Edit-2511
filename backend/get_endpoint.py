"""
Get Modal app endpoint URL
"""
import sys
import os

# Set UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

os.chdir(r'f:\1\comfyui')

try:
    import modal

    print("=" * 60)
    print("Searching for qwen-image-edit app endpoints...")
    print("=" * 60)

    # List all apps
    from modal import App

    # Try to get the app
    app = App.lookup("qwen-image-edit", create_if_missing=False)

    if app:
        print(f"\nFound app: {app.name}")
        print(f"App ID: {app.app_id}")

        # Get functions
        functions = app.list_functions()

        if functions:
            print("\nEndpoints:")
            for func in functions:
                if hasattr(func, 'web_url'):
                    print(f"  - {func.name}: {func.web_url}")
                else:
                    print(f"  - {func.name} (no web URL)")
        else:
            print("\nNo functions found")

        print("\n" + "=" * 60)
        print("To get the full URL, visit:")
        print("https://modal.com/apps")
        print("=" * 60)
    else:
        print("\nApp not found. It may not be deployed yet.")

except Exception as e:
    print(f"\nError: {e}")
    print("\nPlease check the Modal web console at:")
    print("https://modal.com/apps")
