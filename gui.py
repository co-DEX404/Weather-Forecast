import tkinter as tk
from tkinter import messagebox
import threading
import requests

from weather_service import geocode_location, generate_weather_report

DARK_BLUE = "#27374D"
BLUE_GRAY = "#526D82"
LIGHT_BLUE = "#9DB2BF"
PALE_BLUE = "#DDE6ED"

class WeatherApp:
    def __init__(self, window):
        self.window = window
        self.window.title("12 Hour Weather App")
        self.window.geometry("600x400")

        self.window.configure(bg=LIGHT_BLUE)

        tk.Label(
            window,
            text="Weather Forecast",
            font=("Arial", 18, "bold"),
            bg=LIGHT_BLUE,
            fg=DARK_BLUE
        ).pack(pady=15)

        tk.Label(window, 
                 text="Enter your location: ",
                 bg=LIGHT_BLUE,
                 fg=DARK_BLUE
        ).pack()

        self.location_entry = tk.Entry(window, 
                                       width=35, 
                                       font=("Arial",12),
                                       bg="#FFFFFF",
                                       fg=DARK_BLUE,
                                       insertbackground=DARK_BLUE,
                                       relief="flat")
        self.location_entry.pack(pady=5, ipady=6)

        self.weather_button = tk.Button(
            window,
            text="Get Weather",
            command=self.get_weather_from_input,
            font=("Arial", 11, "bold"),
            bg=DARK_BLUE,
            fg="white",
            activebackground=BLUE_GRAY,
            activeforeground="white",
            relief="flat",
            borderwidth=0,
            cursor="hand2",
            padx=5,
            pady=5
        )
        self.weather_button.pack(pady=10)

        self.weather_button.bind(
            "<Enter>",
            lambda event: self.weather_button.configure(bg=BLUE_GRAY)
        )

        self.weather_button.bind(
            "<Leave>",
            lambda event: self.weather_button.configure(bg=DARK_BLUE)
        )

        self.status_label = tk.Label(window, 
                                     text="",
                                     font=("Arial", 10),
                                     bg="#9DB2BF",
                                     fg="#526D82"
        )
        self.status_label.pack()

        self.result_label = tk.Label(
            window,
            text="Enter a location, then click Get Weather.",
            justify="left",
            wraplength=540,
            font=("Consolas", 11),
            bg=LIGHT_BLUE,
            fg=DARK_BLUE,
            padx=20,
            pady=20,
            relief="flat",
        )
        self.result_label.pack(padx=20, pady=15, fill="x")

    def on_button_hover(self, event):
        self.weather_button.config(bg=LIGHT_BLUE)

    def on_button_leave(self, event):
        self.weather_button.config(bg=BLUE_GRAY)

    def get_weather_from_input(self):
        location_name = self.location_entry.get().strip()

        if not location_name:
            messagebox.showwarning("Missing Location", "Please enter a location.")
            return

        self.weather_button.config(state="disabled")
        self.status_label.config(text="Getting weather data...")
        self.result_label.config(text="")

        threading.Thread(
            target=self.get_weather_worker,
            args=(location_name,),
            daemon=True
        ).start()

    def get_weather_worker(self, location_name):
        try:
            coordinates, error = geocode_location(location_name)

            if error:
                self.window.after(0, self.show_error, error)
                return

            latitude, longitude = coordinates
            report, advice = generate_weather_report(latitude, longitude)

            self.window.after(0, self.show_result, report, advice)

        except requests.RequestException:
            self.window.after(
                0,
                self.show_error,
                "Could not connect to the weather service."
            )

    def show_result(self, report, advice):
        self.status_label.config(text="Weather Data Updated.", fg=DARK_BLUE)
        self.result_label.config(text=f"{report}\n\nAdvice : {advice}")
        self.weather_button.config(state="normal")

    def show_error(self, error_message):
        self.status_label.config(text="Could not get weather data.", fg=DARK_BLUE)
        self.result_label.config(text=error_message)
        self.weather_button.config(state="normal")
