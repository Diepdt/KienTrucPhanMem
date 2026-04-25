import os
import sys
import subprocess


def run_creation(service_dir, cmd):
    proc = subprocess.run([sys.executable, 'manage.py', 'shell', '-c', cmd], cwd=service_dir, capture_output=True, text=True)
    print(f"--- {os.path.basename(service_dir)} ---")
    if proc.stdout:
        print(proc.stdout.strip())
    if proc.stderr:
        print(proc.stderr.strip())
    return proc.returncode


def main():
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    tasks = [
        (
            'manager-service',
            "from manager.models import Manager\nobj, created = Manager.objects.get_or_create(email='manager@gmail.com', defaults={'name':'Manager','is_active':True})\nif created:\n    obj.set_password('12345678')\n    obj.save()\n    print('manager created')\nelse:\n    print('manager exists')",
        ),
        (
            'staff-service',
            "from staff.models import Staff\nobj, created = Staff.objects.get_or_create(email='staff@gmail.com', defaults={'name':'Staff','is_active':True,'role':'staff'})\nif created:\n    obj.set_password('12345678')\n    obj.save()\n    print('staff created')\nelse:\n    print('staff exists')",
        ),
    ]

    exit_codes = []
    for service, cmd in tasks:
        service_dir = os.path.join(base, service)
        if not os.path.isdir(service_dir):
            print(f"Service folder not found: {service_dir}")
            exit_codes.append(1)
            continue
        rc = run_creation(service_dir, cmd)
        exit_codes.append(rc)

    if any(c != 0 for c in exit_codes):
        print('One or more creations failed. Check output above.')
        sys.exit(1)
    print('Done.')


if __name__ == '__main__':
    main()
