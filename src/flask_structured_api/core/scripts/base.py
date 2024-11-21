import os
import sys


class ScriptBase:
    @classmethod
    def setup_environment(cls):
        """Setup script environment"""
        # Force development mode for scripts
        os.environ['FLASK_ENV'] = 'development'
        os.environ['PYDEVD_DISABLE_FILE_VALIDATION'] = '1'
        os.environ['PYTHONPATH'] = '/app/src'
        os.environ['DEBUGPY_ENABLE'] = ''  # Disable debugger for scripts

        # Disable frozen modules at runtime
        sys.frozen = False

    @classmethod
    def run(cls, func):
        """Run script with proper environment setup"""
        cls.setup_environment()
        try:
            result = func()
            return 0 if result is None or result is True else 1
        except Exception as e:
            print(f"❌ Script failed: {e}")
            return 1
