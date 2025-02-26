import tkinter as tk
from gui.main_window import MainWindow

def main():
    root = tk.Tk()  # Creates the main application window
    app = MainWindow(root)  # Initialize our custom main window
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    root.mainloop()  # Run the app

if __name__ == "__main__":
    main()
