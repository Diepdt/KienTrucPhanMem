#!/usr/bin/env python
import os
import sys
from pathlib import Path

# Thêm parent directory vào path để import clean module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clean.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Django không được cài đặt") from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
