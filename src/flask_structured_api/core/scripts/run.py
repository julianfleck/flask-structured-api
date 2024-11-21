"""Script runner to avoid runtime warnings"""
from importlib import import_module
from .base import ScriptBase


def main():
    """Run the specified script"""
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m flask_structured_api.core.scripts.run <script_name>")
        sys.exit(1)

    script_name = sys.argv[1]
    try:
        module = import_module(
            f"flask_structured_api.core.scripts.{script_name}")
        if hasattr(module, "main"):
            sys.exit(ScriptBase.run(module.main))
        else:
            print(f"No main function found in {script_name}")
            sys.exit(1)
    except ImportError as e:
        print(f"Script {script_name} not found: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
