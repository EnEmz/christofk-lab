import subprocess
import sys

def install_package(package):
    try:
        print("Installing {}...".format(package))
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except subprocess.CalledProcessError as e:
        print("Failed to install {}: {}".format(package, e))

def main():
    requirements_file = r'.\christofk-lab\requirements\requirements_27_pip.txt'
    with open(requirements_file, 'r') as f:
        requirements = f.readlines()

    for package in requirements:
        package = package.strip()
        if package:
            install_package(package)

if __name__ == "__main__":
    main()