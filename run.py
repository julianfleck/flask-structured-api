import os
import sys
from dotenv import load_dotenv
from app.main import create_app

# Disable frozen modules warning globally
os.environ['PYDEVD_DISABLE_FILE_VALIDATION'] = '1'

# Load environment variables
load_dotenv()


def run_app(debug=True, use_debugpy=False):
    """Run the Flask application with optional remote debugging support"""
    print(f"🚀 Starting app with debug={debug}, debugpy={use_debugpy}")

    if use_debugpy and not os.environ.get('WERKZEUG_RUN_MAIN'):
        try:
            import debugpy
            debugpy_port = int(os.getenv('DEBUGPY_PORT', '5678'))
            print(f"🔍 Attempting to start debugpy on port {debugpy_port}")
            debugpy.listen(('0.0.0.0', debugpy_port))
            print(f"🐛 Debugpy is listening on port {debugpy_port}")
        except ImportError:
            print("⚠️  debugpy not installed. Run: pip install debugpy")
            return
        except Exception as e:
            print(f"⚠️  Failed to initialize debugger: {e}")
            return

    app = create_app()
    if not app:
        print("❌ Failed to create Flask app")
        return

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 5000))

    print(f"🚀 Starting server on {host}:{port} (Debug: {debug})")
    app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=True,
        reloader_type='stat'
    )


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Run Flask API with optional remote debugging")
    parser.add_argument("--debugpy", action="store_true",
                        help="Enable remote debugging with debugpy")
    parser.add_argument("--no-debug", action="store_true",
                        help="Disable Flask debug mode")
    args = parser.parse_args()

    # Set Python flags via environment
    os.environ['PYTHONFLAGS'] = '-X frozen_modules=off'
    run_app(debug=not args.no_debug, use_debugpy=args.debugpy)
