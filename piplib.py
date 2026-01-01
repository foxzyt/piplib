import ast
import sys
import subprocess
import os
import glob

def get_imports(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
    except Exception as e:
        print(f"Error while reading {path}: {e}")
        return set()

    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                modules.add(n.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                modules.add(node.module.split('.')[0])
    return modules

def install_modules(modules, current_dir):
    if not modules:
        return

    stdlib = getattr(sys, "stdlib_module_names", set())
    if not stdlib:
        stdlib = {"os", "sys", "math", "random", "time", "json", "re", "subprocess", "ast"}

    local_files = {
        f.replace('.py', '') for f in os.listdir(current_dir) if f.endswith('.py')
    }

    to_install = [
        m for m in modules
        if m not in stdlib
        and m not in sys.builtin_module_names
        and m not in local_files
        and not m.startswith('_')
    ]

    if to_install:
        print(f"Installing: {', '.join(to_install)}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *to_install])
        except subprocess.CalledProcessError:
            print(f"Error installing one or more packages from the group: {to_install}")
def main():
    if len(sys.argv) < 2 or sys.argv[1] != "install":
        print("Usage: piplib install <file.py> ou piplib install -a (to install from all .py files in the current directory)")
        sys.exit(1)

    all_imports = set()
    current_dir = os.getcwd()

    if len(sys.argv) == 3 and sys.argv[2] == "-a":
        files = glob.glob("*.py")
        if not files:
            print("No .py files found in the current directory.")
            return
        print(f"Analyzing all files ({len(files)} files)...")
        for f in files:
            all_imports.update(get_imports(f))
    elif len(sys.argv) == 3:
        path = sys.argv[2]
        if not os.path.exists(path):
            print(f"Error: File '{path}' not found.")
            sys.exit(1)
        all_imports.update(get_imports(path))
    else:
        print("Usage: piplib install <file.py> ou piplib install -a (to install from all .py files in the current directory)")
        sys.exit(1)

    install_modules(all_imports, current_dir)

if __name__ == "__main__":
    main()