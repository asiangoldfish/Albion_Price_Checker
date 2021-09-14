"""
This program fetches data from the Albion Online Data Project and displays the price on an interactive GUI.
"""
import json
import tkinter as tk
import urllib.request
from PIL import ImageTk, Image
from data import item_selections, Formatted_Items_List
import pandas as pd
import os.path
from datetime import datetime, date
import configparser
import sys


class MyConfig(configparser.ConfigParser):
	def __init__(self):
		super().__init__()

		self.read("data/config.ini")


class MyLabels(tk.Label):
	def __init__(self, master=None, result_list=None, column=0, row=0):
		super().__init__()
		self.master = master
		self.result_list = result_list
		self.column = column
		self.row = row
		self.search_labels_list = ["Item Archetype", "Item Type", "Tier", "Enchantment", "Quality", "City"]
		self.result_labels_list = json.loads(config.get("API Results", "result_labels_list"))

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


class ContentCanvas(tk.Canvas):
	def __init__(self, master, image=None, highlightthickness=None, highlightbackground=None):
		super().__init__(master=master, highlightthickness=highlightthickness, highlightbackground=highlightbackground)
		self.master = master  # Widget to parent to
		self.image = image  # Background image
		# self.layout_method = layout_method  # How to layout (pack, grid or place)

	def layout_canvas(self, layout_method=None, side=None, fill=None, column=0, row=0, padx=0, pady=0, expand="no"):
		"""
		Layout the canvas. This method is similar to tkinter's pack method. Raises an error message
		if none or incorrect layout method has been specified as argument.

		:param layout_method: "Pack", "grid"
		:param side: "right" or "left".
		:param fill: "x", "y" or "both".
		:param column Column of the grid to place the widget in.
		:param row Row of the grid to place the widget in.
		:param padx Padding in x direction.
		:param pady Padding in y direction.
		:param expand Specify if the widget should expand as child widgets is added or alter in size.
		"""
		if layout_method is None:
			error_message = "This method requires the layout method to be specified: pack, grid"
			raise ValueError(error_message)
		elif layout_method == "pack":
			self.pack(expand=expand, side=side, fill=fill, padx=padx, pady=pady)
		elif layout_method == "grid":
			self.grid(column=column, row=row, padx=padx, pady=pady)
		else:
			error_message = "Incorrect layout method has been specified. Please choose pack, grid"
			raise ValueError(error_message)

	def canvas_title(self):
		"""
		Use this method to create a title label for the canvas
		:return:
		"""
		return None


class ItemThumbnail(tk.Label):
	"""
	Hello world!
	"""
	def __init__(self, master, size_x=75, size_y=75, image=None):
		super().__init__(master=master)
		self.image = image
		self.size_x = size_x
		self.size_y = size_y

	def update_image(self, item_id="T4_MAIN_SWORD", update=False):
		"""
		Updates the item thumbnail. If the file doesn't exist on disk, then creates a new file with default thumbnail.

		:param update Bool. If true, then updates the item thumbnail.
		:return: Boolean
		"""
		# Checks if the file exists on disk
		if not os.path.isfile("img/item_img.png"):
			update = True

		# Writes the new item thumbnail to disk
		if update:
			url = f"https://render.albiononline.com/v1/item/{item_id}.png?locale=en"
			url_write = urllib.request.urlretrieve(url, "img/item_img.png")  # Writes to disk

		# Updates the item thumbnail
		new_image = Image.open("img/item_img.png")
		new_image = new_image.resize((self.size_x, self.size_y), Image.ANTIALIAS)  # Resize image to fit current format
		new_image = ImageTk.PhotoImage(new_image)
		self.config(image=new_image)  # Updates image on the label
		self.image = new_image

		return new_image


class ApiPrice:
	def __init__(self, item_archetype, item_type, tier_value, enchant_value, quality_value, city):
		self.item_archetype = item_archetype
		self.item_type = item_type
		self.tier_value = tier_value
		self.enchant_value = enchant_value
		self.quality_value = quality_value
		self.city = city

		self.base_url = "https://www.albion-online-data.com/api/v2/stats/Prices/"  # URL of the API without queries
		self.quality = self.quality_index(quality_list, quality_value.get())
		self.city = city_value.get()

	def get_item_id(self):
		"""
		Puts together item name, tier and enchantment level and converts it to the
		matching item_id.
		"""
		"""
		1. Put together the item_id based on the item name, tier and enchantment level
		1.1 Get the user input for item name, tier and enchantment level.
		1.2 Loop through all item_ids and match it with the item name. If a match has
			has been found, then add the tier and enchantment level
		2. Check if the item id is valid. Send an error message to user if not.
		3. Return the item_id
		"""
		# Gets the values of the user inputs
		input_name = self.item_type.get()
		input_tier = self.tier_value.get()
		input_enchantment = self.enchant_value.get()

		# Declares vars for each component that will be used to find the item_id
		item_name = ""
		item_enchantment = 0

		"""In the following code blocks, the item_tier will be identified"""

		# Convert tier into rarity name, i.e. "Expert's" instead of T5
		tiers_list = json.loads(config.get("Item Data", "tier_list"))  # Gets tier list from config file
		tiers_ranking = json.loads(config.get("Item Data", "tier_ranking"))  # List of the name of each tier

		for i in range(len(tiers_ranking)):
			if input_tier == tiers_list[i]:
				item_tier = tiers_ranking[i]

		"""In the following code blocks, the item_name will be identified"""

		item_label = f"{item_tier} {input_name}"  # Combines the item name like seen in-game

		# Based on item tier and input name, get the item_id w/o enchantment from the dict in Formatted_Items_List.py
		item_from_dict = list(Formatted_Items_List.items_list.keys())[
			list(Formatted_Items_List.items_list.values()).index(
				item_label)]  # Retrieves the item_id. More info found here: https://stackoverflow.com/a/13149770

		print(item_from_dict)

	@staticmethod
	def fetch_data(dataframe, keyword):
		"""
		Makes it quicker to fetch data from the pandas dataframe.

		:param dataframe: pandas class
		:param str keyword: column name
		:return: element in the first row and the given column
		"""
		return dataframe.iloc[0][keyword]

	@staticmethod
	def quality_index(index_quality_list, selected_quality):
		"""Converts the item quality index to its literal name."""
		index = 0
		for i in range(len(index_quality_list)):
			if index_quality_list[i] == selected_quality:
				index = i
		return index

	@staticmethod
	def is_item_id_valid(item_id):
		"""Idiot proof for programmers to ensure that the correct item_id was passed"""
		try:
			item_id = convert_name_to_id(sub_cat_options_value, tier_value, enchant_value)
		except ValueError:
			print("""ERROR: Please pass the correct item_id format and name. This error is to make sure that you
			don't make this mistake.
			"The error is found in the ApiPrice class.""")
			sys.exit(1)  # Force exits the program
		return item_id


def center_window(master):
	master.eval('tk::PlaceWindow . center')  # Center windows


def loading_screen(master, path):
	img_load = ImageTk.PhotoImage(Image.open(path))
	label = tk.Label(master, image=img_load)
	label.pack()


def update_sub_cat(event):
	global sub_cat_options_list, sub_dropdown

	sub_cat_options_value.set("Item Type")
	sub_dropdown["menu"].delete(0, "end")

	selected_name = archetype_options_value.get()

	# Insert list of new functions
	sub_cat_options_list = items_list.get(selected_name)  # Refresh list
	for name in sub_cat_options_list:
		sub_dropdown["menu"].add_command(label=name, command=tk._setit(sub_cat_options_value, name))


def get_results():
	"""
	Get the results based on the user input from OptionMenus. Creates an API get request as a formatted string.
	Outputs the API return.
	"""
	global enchant_value, sub_cat_options_value, tier_value, result_canvas, quality_value, city_value, quality_list, item_thumbnail

	# Generate URL
	def fetch_data(dataframe, keyword):
		"""Makes it quicker to fetch data from the pandas dataframe"""
		return dataframe.iloc[0][keyword]

	def quality_index(index_quality_list, selected_quality):
		index = 0
		for i in range(len(index_quality_list)):
			if index_quality_list[i] == selected_quality:
				index = i
		return index

	base_url = "https://www.albion-online-data.com/api/v2/stats/Prices/"

	# Item data
	try:
		item_id = convert_name_to_id(sub_cat_options_value, tier_value, enchant_value)
	except ValueError:
		item_id = "none"

	quality = quality_index(quality_list, quality_value.get())
	city = city_value.get()



	item_query = f"{item_id}.json"
	quality_query = f"{quality}"
	city_query = f"{city}"

	# Retrieve and analyse data
	pd.set_option("display.max_columns", 11)
	send_url = f"{base_url}{item_query}?locations={city_query}&qualities={quality_query}"
	df = pd.read_json(send_url)  # Makes a pandas dataframe/datatable

	# Fetched variables from data frame
	city = fetch_data(df, "city")
	buy_price_min = fetch_data(df, "buy_price_min")
	buy_price_min_date = fetch_data(df, "buy_price_min_date")
	sell_price_max = fetch_data(df, "sell_price_max")
	sell_price_max_date = fetch_data(df, "sell_price_max_date")

	# Checks if price is valid
	invalid_data = "No Data"
	if buy_price_min == 0:
		buy_price_min = invalid_data
		buy_price_min_date = invalid_data
	if sell_price_max == 0:
		sell_price_max = invalid_data
		sell_price_max_date = invalid_data

	# Checks the delta time between sys time and the API data

	# Buy order
	if buy_price_min_date != invalid_data:
		old_buy_time = buy_price_min_date.split("T")  # Old time
		buy_price_min_date = time_dif(old_buy_time)  # New time

	# Sell order
	if sell_price_max_date != invalid_data:
		old_sell_time = sell_price_max_date.split("T")  # Old time
		sell_price_max_date = time_dif(old_sell_time)  # New time

		# Sets time as "Today" if latest update is today
		if sell_price_max_date == 0:
			sell_price_max_date = "Today"
		else:
			sell_price_max_date = f"{sell_price_max_date} days ago"

	# Update result labels with item meta data
	result_list = [item_id, city, buy_price_min, buy_price_min_date, sell_price_max, sell_price_max_date]
	result_labels = MyLabels(master=result_canvas, result_list=result_list, column=1)
	result_labels.result_item_labels()

	# Update item image label
	item_image = item_thumbnail
	item_image.update_image(update=True, item_id=item_id)


def time_dif(to_time):
	"""
	Gets the time difference between system or input time, input time. Format must be:
	yyyy-mm-dd

	:param str to_time: Time to measure to
	:return: days difference
	"""

	now = datetime.now()
	now_date_y = now.strftime("%Y")
	now_date_m = now.strftime("%m")
	now_date_d = now.strftime("%d")

	now_date_formatted = date(int(now_date_y), int(now_date_m), int(now_date_d))

	to_date_y = to_time[0][0:4]
	to_date_m = to_time[0][5:7]
	to_date_d = to_time[0][8:10]

	to_date_formatted = date(int(to_date_y), int(to_date_m), int(to_date_d))

	delta_date = to_date_formatted - now_date_formatted

	return_delta_days = delta_date.days

	return return_delta_days * -1


def reformat_json(obj):
	# text = json.dumps(obj, sort_keys=True, indent=4)
	text = json.dumps(obj, sort_keys=True, indent=4)
	return text


def convert_name_to_id(item_name, item_tier, item_enchant_value):
	global tier_list
	# Fetch input from user
	user_input = item_name.get()
	item_tier = item_tier.get()
	item_enchant_value = item_enchant_value.get()

	# Convert tier into rarity name, i.e. "Expert's" instead of T5
	output_tier = ""
	tier_ranking = json.loads(config.get("Item Data", "tier_ranking"))
	for tier_id in range(len(tier_list)):
		if tier_id + 1 == int(item_tier):
			output_tier = tier_ranking[tier_id]

	item_label = f"{output_tier} {user_input}"  # Combines the item name like seen in-game
	item_id_from_dic = list(Formatted_Items_List.items_list.keys())[
		list(Formatted_Items_List.items_list.values()).index(
			item_label)]  # Retrieves the item_id. More info found here: https://stackoverflow.com/a/13149770

	if item_enchant_value == "None":
		item_id = f"{item_id_from_dic}"
	else:
		item_id = f"{item_id_from_dic}@{item_enchant_value}"

	return item_id


def error_msg():

	# Create new error window
	error_root = tk.Tk()
	error_root.title("ERROR!")
	error_root.iconbitmap("img/ao_bitmap_logo.ico")

	my_label = tk.Label(error_root, text="ERROR! Please Check Item Info", width=35, height=3)
	my_label.pack(padx=0, pady=0)
	center_window(error_root)


"""
Configuration related variables
"""
config = MyConfig()

"""
Developer tools to test features during development.
"""
toggle_loading_screen = False

"""
Super widgets and application window
"""
# Application window
root = tk.Tk()
root.title("Albion Price Checker")
root.iconbitmap("img/ao_bitmap_logo.ico")

# Calculate user screen center and set resolution || NOTE: STILL NOT PERFECT
root.geometry(config.get("DEFAULT", "resolution")) # Set window dimensions
center_window(root) # Center window

# Master canvas
bg_canvas = ContentCanvas(root, highlightthickness=0)
bg_canvas.layout_canvas("pack", expand="yes", fill="both")
bg_canvas_image_load = ImageTk.PhotoImage(file="img/albion_bg.png")
bg_canvas.create_image(0, 0, image=bg_canvas_image_load, anchor="nw")

"""
Widgets
"""
# Background image of the two main canvases
treasure_bg_width = 206
treasure_bg_height = 320
treasure_bg = Image.open("img/treasure_bg.png")
treasure_bg = treasure_bg.resize((treasure_bg_width*2, treasure_bg_height*2), Image.ANTIALIAS)
treasure_bg = ImageTk.PhotoImage(treasure_bg)

highlight_colour = "#e6c8ae"

# Canvas where the user searches for the item
search_canvas = ContentCanvas(bg_canvas, highlightthickness=1, highlightbackground=highlight_colour)
search_canvas.layout_canvas("pack", side="left", fill="y")
search_canvas.create_image(0, 0, image=treasure_bg, anchor="nw")

# Canvas where the results appear
result_canvas = ContentCanvas(bg_canvas, highlightthickness=1, highlightbackground=highlight_colour)
result_canvas.layout_canvas("pack", side="right", fill="y")
result_canvas.create_image(0, 0, image=treasure_bg, anchor="nw")

"""
Loading screen. Still needs a lot of work!
"""
# Loading_screen
if toggle_loading_screen:
	loading_logo = "img/albion_.png"
	loading_logo_converted = ImageTk.PhotoImage(file=loading_logo)
	loading_label = tk.Label(bg_canvas, image=loading_logo_converted)
	loading_label.pack()
	loading_label.after(3000, loading_label.destroy)

"""
The following widgets implement drop down menu systems for interactive selection of items to price check.
"""
# List of items that the user can choose between
items_list = item_selections.equip_archetype()
items_list_keys = list(items_list)  # Returns all the keys in the equip_list dictionary

# Make labels for user search and result data
select_label = MyLabels(search_canvas)
select_label.search_labels()

result_label = MyLabels(result_canvas)
result_label.result_labels()

result_item_list = json.loads(config.get("API Results", "retrieve_data"))  # Loads the default values for the labels
result_item_label = MyLabels(master=result_canvas, result_list=result_item_list, column=1)
result_item_label.result_item_labels()

# archetype list - List of item archetypes
archetype_options_list = list()
for key in items_list:
	archetype_options_list.append(key)  # Appends item types into a new list so the drop down menu works

archetype_options_value = tk.StringVar()  # This is the selected value of the dropdown menu
archetype_options_value.set(archetype_options_list[0])  # Sets the default value for the dropdown menu

archetype_options_dropdown = tk.OptionMenu(search_canvas, archetype_options_value, *archetype_options_list,
                                          command=update_sub_cat)
archetype_options_dropdown.grid(column=1, row=0, padx=5, pady=5)

# Sub archetype list - list of item types
sub_cat_options_value = tk.StringVar()  # Value of the selected item in the dropdown menu
sub_cat_options_value.set("Broadsword")  # Sets the default value of the dropdown menu
sub_cat_options_list = items_list.get(archetype_options_value.get())  # Gets the available items based on item archetype

sub_dropdown = tk.OptionMenu(search_canvas, sub_cat_options_value, *sub_cat_options_list)
sub_dropdown.grid(column=1, row=1, padx=5, pady=5)

# Item Tier
tier_value = tk.StringVar()
tier_value.set(json.loads(config.get("Item Data", "tier_list"))[3])  # Gets the default value from the config file
tier_list = json.loads(config.get("Item Data", "tier_list"))  # Gets the list of available tiers from config file

tier_dropdown = tk.OptionMenu(search_canvas, tier_value, *tier_list)
tier_dropdown.grid(column=1, row=2, padx=5, pady=5)

# Enchantment list
enchant_value = tk.StringVar()
enchant_value.set(json.loads(config.get("Item Data", "enchantment_list"))[0])
enchantment_list = json.loads(config.get("Item Data", "enchantment_list"))

enchant_dropdown = tk.OptionMenu(search_canvas, enchant_value, *enchantment_list)
enchant_dropdown.grid(column=1, row=3, padx=5, pady=5)

# Quality list
quality_value = tk.StringVar()
quality_list = json.loads(config.get("Item Data", "item_quality"))
quality_value.set(quality_list[0])
quality_dropdown = tk.OptionMenu(search_canvas, quality_value, *quality_list)
quality_dropdown.grid(column=1, row=4, padx=5, pady=5)

# City list
city_value = tk.StringVar()
city_value.set(json.loads(config.get("World", "cities"))[1])
city_list = json.loads(config.get("World", "cities"))
city_dropdown = tk.OptionMenu(search_canvas, city_value, *city_list)
city_dropdown.grid(column=1, row=5, padx=5, pady=5)

# Submit button
submit_button = tk.Button(search_canvas, text="Submit Request", command=get_results)
submit_button.grid(column=1, row=6, padx=5, pady=5)

# Item thumbnail
item_thumbnail = ItemThumbnail(master=result_canvas)
item_thumbnail.update_image()
item_thumbnail.grid(column=1)

"""
Here, API calls is setup. The following new variables are not strictly necessary, but it makes
readability and working with much easier. All the variables are objects of the tk.StringVar class and are the objects
that the user selects with the dropdown menus.
"""
item_archetype = archetype_options_value  # Item archetype
item_type = sub_cat_options_value  # Item type
tier_value = tier_value  # Item tier
enchant_value = enchant_value  # Item Enchantment level
quality_value = quality_value # Item Quality
city = city_value  # Filter what city to search in

api_call = ApiPrice(item_archetype, item_type, tier_value, enchant_value, quality_value, city)
api_call.get_item_id()


root.resizable(False, False)  # Disable resizing app window
root.mainloop()
