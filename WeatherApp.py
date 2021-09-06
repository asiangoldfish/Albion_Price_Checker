import tkinter as tk
from PIL import Image, ImageTk
import requests
from tkinter import font

height = 500
width = 600

def test_function(entry):
	print("This is the entry:", entry)


def format_response(weather):
	try:
		name = weather["name"]
		desc = weather["weather"][0]["description"]
		temp = weather["main"]["temp"]

		final_str = "City: %s \nConditions: %s\nTemperature (C): %s" % (name, desc, temp)
	except:
		final_str = "There was a problem retrieving that information"

	return final_str


def get_weather(city):
	weather_key = "c4ad4a27e4630f2961ab1c5453d901c6"
	url = "https://api.openweathermap.org/data/2.5/weather"
	params = {
		"APPID": weather_key,
		"q": city,
		"units": "Metric"
	}
	response = requests.get(url, params=params)
	weather = response.json()

	label["text"] = format_response(weather)

# c4ad4a27e4630f2961ab1c5453d901c6
# api.openweathermap.org/data/2.5/forecast?q={city name},{state code},{country code}&appid={API key}


root = tk.Tk()

canvas = tk.Canvas(root, height=height, width=width)
canvas.pack()

load_img = Image.open("img/earth.jpg")
render = ImageTk.PhotoImage(load_img)
background_label = tk.Label(root, image=render)
background_label.place(relwidth=1, relheight=1)

frame = tk.Frame(root, bg="#8080ff", bd=5)
frame.place(relwidth=0.75, relheight=0.1, relx=0.5, rely=0.1, anchor="n")

entry = tk.Entry(frame, font=("System", 10), justify="center")
entry.place(relwidth=0.65, relheight=1)

button = tk.Button(frame, text="Get Weather", font=("System", 10), command=lambda: get_weather(entry.get()))
button.place(relx=0.7, relwidth=0.3, relheight=1)

lower_frame = tk.Frame(root, bg="#8080ff", bd=10)
lower_frame.place(relx=0.5, rely=0.25, relwidth=0.75, relheight=0.6, anchor="n")

label = tk.Label(lower_frame, font=("System", 15))
label.place(relwidth=1, relheight=1)

root.mainloop()