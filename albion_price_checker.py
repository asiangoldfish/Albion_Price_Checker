"""
This program fetches data from the Albion Online Data Project and displays the price on an interactive GUI.
"""
import json
import tkinter as tk
import urllib.request
from tkinter import ttk
from PIL import ImageTk, Image
from data import item_selections, Formatted_Items_List
import pandas as pd
import requests
from urllib.request import urlopen
import os.path


class MyLabels(tk.Label):
	def __init__(self, master=None, result_list=None, column=0, row=0):
		self.master = master
		self.result_list = result_list
		self.column = column
		self.row = row
		self.search_labels_list = ["Item Archetype", "Item Type", "Tier", "Enchantment", "Quality", "City"]
		self.result_labels_list = ["Name", "City", "Min Buy Price", "Min Buy Price Date", "Max Sell Price", "Max Sell Price Date"]

	# Creates labels in a grid
	def search_labels(self):
		for i in range(len(self.search_labels_list)):
			label_var = tk.StringVar()
			label_var.set(self.search_labels_list[i])
			my_label = tk.Label(self.master, width=20, height=1, textvar=label_var, bg="grey")
			my_label.grid(column=0, row=i)

	def result_labels(self):
		for i in range(len(self.result_labels_list)):
			label_var = tk.StringVar()
			label_var.set(self.result_labels_list[i])
			my_label = tk.Label(self.master, width=15, height=1, textvar=label_var, bg="orange")
			my_label.grid(column=0, row=i)

	def result_item_labels(self):
		for i in range(len(self.result_list)):
			label_var = tk.StringVar()
			label_var.set(self.result_list[i])
			my_label = tk.Label(self.master, width=15, height=1, textvar=label_var, bg="green")
			my_label.grid(column=self.column, row=i)



class OutputData:
	def __init__(self, master, item_id, item_image_label):
		self.item_id = item_id
		self.master = master
		self.item_image_label = item_image_label
		self.url = f"https://render.albiononline.com/v1/item/{self.item_id}.png?locale=en"


def loading_screen(master, path):
	img_load = ImageTk.PhotoImage(Image.open(path))
	label = tk.Label(master, image=img_load)
	label.pack()


def update_sub_cat(event):
	global sub_cat_options_list, sub_dropdown

	sub_cat_options_value.set("Item Type")
	sub_dropdown["menu"].delete(0, "end")

	selected_name = category_options_value.get()

	# Insert list of new functions
	sub_cat_options_list = items_list.get(selected_name)  # Refresh list
	for name in sub_cat_options_list:
		sub_dropdown["menu"].add_command(label=name, command=tk._setit(sub_cat_options_value, name))


def get_results():
	"""
	Get the results based on the user input from OptionMenus. Creates an API get request as a formatted string.
	Outputs the API return.
	"""
	global enchant_value, sub_cat_options_value, tier_value, result_canvas, quality_value, city_value

	"""
	Generate URI
	"""
	def fetch_data(DataFrame, keyword):
		"""Makes it quicker to fetch data from the pandas dataframe"""
		return DataFrame.iloc[0][keyword]

	base_url = "https://www.albion-online-data.com/api/v2/stats/Prices/"

	# Item data
	item_id = convert_name_to_id(sub_cat_options_value, tier_value, enchant_value)
	enchantment_level = enchant_value.get()
	tier = tier_value.get()

	# Query
	item_query = f"{item_id}.json"
	tier_query = f"{tier}"

	# Retrieve and analyse data
	pd.set_option("display.max_columns", 11)
	df = pd.read_json(f"{base_url}{item_query}?locations=Caerleon&qualities=2")
	name = fetch_data(df, "item_id")
	city = fetch_data(df, "city")
	buy_price_min = fetch_data(df, "buy_price_min")
	buy_price_min_date = fetch_data(df, "buy_price_min_date")
	sell_price_max = fetch_data(df, "sell_price_max")
	sell_price_max_date = fetch_data(df, "sell_price_max_date")

	print(df)

	# Update result labels with item meta data
	result_list = [name, city, buy_price_min, buy_price_min_date, sell_price_max, sell_price_max_date]
	result_labels = MyLabels(master=result_canvas, result_list=result_list, column=1)
	result_labels.result_item_labels()
	update_item_image(item_id)  # Update item image label


def reformat_json(obj):
	# text = json.dumps(obj, sort_keys=True, indent=4)
	text = json.dumps(obj, sort_keys=True, indent=4)
	return text


def convert_name_to_id(item_name, item_tier, enchant_value):
	global tier_list
	# Fetch input from user
	user_input = item_name.get()
	item_tier = item_tier.get()
	enchant_value = enchant_value.get()

	# Convert tier into rarity name, i.e. "Expert's" instead of T5
	output_tier = ""
	tier_ranking = ["Beginner's", "Novice's", "Journeyman's", "Adept's", "Expert's", "Master's", "Grandmaster's", "Elder's"]
	for tier_id in range(len(tier_list)):
		if tier_id + 1 == int(item_tier):
			output_tier = tier_ranking[tier_id]

	item_label = f"{output_tier} {user_input}"  # Combines the item name like seen in-game
	item_id_from_dic = list(Formatted_Items_List.items_list.keys())[list(Formatted_Items_List.items_list.values()).index(item_label)]  # Retrieves the item_id. More info found here: https://stackoverflow.com/a/13149770

	if enchant_value == "None":
		item_id = f"{item_id_from_dic}"
	else:
		item_id = f"{item_id_from_dic}@{enchant_value}"

	return item_id


def save_image(item_id):
	url = f"https://render.albiononline.com/v1/item/{item_id}.png?locale=en"
	urllib.request.urlretrieve(url, "img/item_img.png")


def update_item_image(item_id):
	global item_image_label, canvas
	save_image(item_id)
	new_image = Image.open("img/item_img.png")
	new_image = new_image.resize((100, 100), Image.ANTIALIAS)
	new_image = ImageTk.PhotoImage(new_image)
	# Update image
	item_image_label.config(image=new_image)
	item_image_label.image = new_image



"""
Developer tools to test features during development.
"""
toggle_loading_screen = False

"""
Application settings
"""
# Application window
root = tk.Tk()
root.title("Albion  Price Checker")
root.iconbitmap("img/ao_bitmap_logo.ico")

# Calculate user screen center
screen_width = root.winfo_screenwidth()  # Get monitor width
screen_height = root.winfo_screenheight()  # Get monitor height
center_x = int(screen_width/2 - 700 / 2)  # Get screen center x
center_y = int(screen_height/2 - 390 / 2)  # Get screen center y

root.geometry(f'{700}x{390}+{center_x}+{center_y}')  # Place app window

# Initial app window size
canvas = tk.Canvas(root)
canvas.pack(expand="yes", fill="both")
canvas_image_load = ImageTk.PhotoImage(file="img/albion_bg.png")
canvas.create_image(0, 0, image=canvas_image_load, anchor="nw")

"""
Widgets
"""
# Canvas for searching
search_canvas = tk.Canvas(canvas)
search_canvas.pack(side="left")

# Canvas for results
result_canvas = tk.Canvas(canvas)
result_canvas.pack(side="right")

# Loading_screen
if toggle_loading_screen:
	loading_logo = "img/albion_.png"
	loading_logo_converted = ImageTk.PhotoImage(file=loading_logo, master=canvas)
	loading_label = tk.Label(canvas, image=loading_logo_converted)
	loading_label.pack()
	loading_label.after(3000, loading_label.destroy)

"""
The following blocks of codes implements drop down menu systems for interactive selection of items to price check.
"""
# Item type selection
items_list = item_selections.equip_category()
category_options_selected = "None"

category_options = items_list

category_options_list = list()
for key in category_options:
	category_options_list.append(key)  # Appends item types into a new list so the drop down menu works

sub_cat_options_list = []  # Sub category items list

# Make labels
select_label = MyLabels(search_canvas)
select_label.search_labels()

result_label = MyLabels(result_canvas)
result_label.result_labels()

result_item_list = ["Name", "City", "Min Buy Price", "Min Buy Price Date", "Max Sell Price", "Max Sell Price Date"]
result_item_label = MyLabels(master=result_canvas, result_list=result_item_list, column=1)
result_item_label.result_item_labels()

# result_item_label = MyLabels(result_canvas, column=1)
# result_item_label.result_labels_list(result_list=["Hello World!"])

# Set default key
category_options_value = tk.StringVar()
category_options_value.set(category_options_list[0])
category_options_value_default = category_options_value

category_options_dropdown = tk.OptionMenu(search_canvas, category_options_value, *category_options_list, command=update_sub_cat)
category_options_dropdown.grid(column=1, row=0, padx=5, pady=5)

# Sub category list
sub_cat_options_value = tk.StringVar()
sub_cat_options_value.set("Broadsword")

sub_cat_options_list = items_list.get(category_options_value.get())

sub_dropdown = tk.OptionMenu(search_canvas, sub_cat_options_value, *sub_cat_options_list)
sub_dropdown.grid(column=1, row=1, padx=5, pady=5)

# Item Tier
tier_value = tk.StringVar()
tier_value.set("4")
tier_list = ["1", "2", "3", "4", "5", "6", "7", "8"]

tier_dropdown = tk.OptionMenu(search_canvas, tier_value, *tier_list)
tier_dropdown.grid(column=1, row=2, padx=5, pady=5)

# Enchantment list
enchant_value = tk.StringVar()
enchant_value.set("None")
enchantment_list = ["None", "1", "2", "3"]

enchant_dropdown = tk.OptionMenu(search_canvas, enchant_value, *enchantment_list)
enchant_dropdown.grid(column=1, row=3, padx=5, pady=5)

# Quality list
quality_value = tk.StringVar()
quality_value.set("Normal")
quality_list = ["Normal", "Good", "Outstanding", "Excellent", "Masterpiece"]
quality_dropdown = tk.OptionMenu(search_canvas, quality_value, *quality_list)
quality_dropdown.grid(column=1, row=4, padx=5, pady=5)

# City list
city_value = tk.StringVar()
city_value.set("Caerleon")
city_list = ["Caerleon", "Lymhurst", "Bridgewatch", "Martlock", "Thetford", "FortSterling"]
city_dropdown = tk.OptionMenu(search_canvas, city_value, *city_list)
city_dropdown.grid(column=1, row=5, padx=5, pady=5)

# Submit button
submit_button = tk.Button(search_canvas, text="Submit Request", command=get_results)
submit_button.grid(column=1, row=6, padx=5, pady=5)

# image = ImageTk.PhotoImage(Image.open("img/item_img.png"))
# image_label = tk.Label(canvas, image=image)
# image_label.pack()
# print(image_label)
# print(image)

# Item image label
if not os.path.isfile("img/item_img.png"):  # Check if file exists
	save_image()

image_file = Image.open("img/item_img.png")
image_file = image_file.resize((100, 100), Image.ANTIALIAS)
item_image = ImageTk.PhotoImage(image_file)  # This global variable is to bypass Python's garbage disposal
item_image_label = tk.Label(master=result_canvas, image=item_image)
item_image_label.grid(column=3, row=0)

root.resizable(False, False)  # Disable resizing app window
root.mainloop()
