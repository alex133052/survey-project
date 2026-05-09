import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.gui import SurveyApp
import tkinter as tk

def main():
    root = tk.Tk()
    app = SurveyApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()