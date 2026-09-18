import tkinter as tk
from gui import WeatherApp

if __name__ == "__main__":
    window = tk.Tk()
    app = WeatherApp(window)
    window.mainloop()