#Set of global utilities
import sys
import platform
import os

def get_OS():
    my_os = platform.system()
    my_os = str(my_os)
    if my_os == "Linux":
        return "Linux"
    elif my_os == "Windows":
        return "Windows"
    elif my_os == "Darwin":
        return "MacOS"
    else:
        return "Unknown OS"

def get_path():
    if getattr(sys, 'frozen', True): ##BEING RAN FROM PYINSTALLER
        pass
    else:
        pass

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_current_path():
    if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app 
    # path into variable _MEIPASS'.
        application_path = sys._MEIPASS
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))

    print(os.getcwd())
    return application_path

def get_correct_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    print(get_OS())