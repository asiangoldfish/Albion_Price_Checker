"""
This program fetches data from the Albion Online Data Project and displays the price on an interactive GUI.
"""
import configparser
import json
import os.path
import tkinter as tk
from datetime import datetime, date
import urllib.request

import pandas as pd
from PIL import ImageTk, Image

from data import item_selections, Formatted_Items_List


class MyConfig(configparser.ConfigParser):
	def __init__(self):
		super().__init__()

		self.read("data/config.ini")


class MyLabels(tk.Label):
	def __init__(self, master=None, column=0, row=0):
		super().__init__()
		self.master = master
		self.column = column
		self.row = row

		self.search_labels_list = json.loads(config.get("Other Labels Default", "search_labels_list"))
		self.result_labels_list = json.loads(config.get("API Results", "result_labels_list"))

		self.labels_list = list()  # List of all labels that a method creates

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

	def result_item_labels(self, labels_value=None):
		"""
		Fetches data from the config file about what types of data will be retrieved. Stores these in a list.
		Then, creates a number of labels. The number depends on the length of the list. Finally, adds the newly
		created labels in the labels_list class attribute.

		This method is also used to update the labels with new data. To do this, it deletes currently existing labels
		in the labels_list attribute and fills it with new labels containing updated data.
		"""
		# List from the config file
		data_placeholder = json.loads(config.get("API Results", "result_labels_list"))

		# Fills the label values with placeholders. Used to create the labels upon starting the app.
		if labels_value is None:
			labels_value = list()
			for i in range(len(data_placeholder)):
				labels_value.append("N/A")

		# Clears the list of labels
		if len(self.labels_list) > 0:
			self.labels_list.clear()

		# Creates new labels and adds them to the list of labels.
		for i in range(len(data_placeholder)):
			label_var = tk.StringVar()
			label_var.set(labels_value[i])
			my_label = tk.Label(self.master, width=25, height=1, textvar=label_var, bg="green")
			my_label.grid(column=self.column, row=i)
			self.labels_list.append(my_label)


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

	@staticmethod
	def canvas_title():
		"""
		Use this method to create a title label for the canvas
		:return:
		"""
		return None


class ItemThumbnail(tk.Label):
	"""
	Thumbnail for the searched item. This is updated every time the user successfully
	searches for a new item price.
	"""

	def __init__(self, master, size_x=75, size_y=75, image=None):
		super().__init__(master=master)
		self.image = image
		self.size_x = size_x
		self.size_y = size_y

	def update_image(self, item_id, update=False):
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
			url_write = urllib.request.urlretrieve(url, "img/item_img.png")

		# Updates the item thumbnail
		new_image = Image.open("img/item_img.png")
		new_image = new_image.resize((self.size_x, self.size_y), Image.ANTIALIAS)  # Resize image to fit current format
		new_image = ImageTk.PhotoImage(new_image)
		self.config(image=new_image)  # Updates image on the label
		self.image = new_image

		return new_image


# Manages item price requests
class ApiPrice:
	# This class takes care of user input and converting them into a request sent to the Albion Data Project server. Also updates
	# labels with results from the server.
	def __init__(self, item_category, item_branch, tier, enchantment, quality_level, city_val):
		# Variables needed to find the id of the user selected item
		self.item_archetype = item_category.get()
		self.item_type = item_branch.get()
		self.tier_value = tier.get()
		self.enchant_value = enchantment.get()
		self.quality_value = quality_level.get()

		# Base URL for the API call
		self.base_url = "https://www.albion-online-data.com/api/v2/stats/Prices/"  # URL of the API without queries
		self.city = city_val.get()  # Filter what city to search the item in

		# Variables used to populate the result labels.
		self.item_id = self.get_item_id()

	def update_class_attributes(self):
		"""
		This class uses global vars to fetch data from the outer scope, updating all class attributes used
		to make the API call.
		"""
		global archetype_options_value, item_type_value, tier_value, enchant_value, quality_value, city_value
		self.item_archetype = archetype_options_value.get()
		self.item_type = item_type.get()
		self.tier_value = tier_value.get()
		self.enchant_value = enchant_value.get()
		self.quality_value = quality_value.get()
		self.city = city.get()
		self.item_id = self.get_item_id()

	def get_item_id(self):
		"""
		Puts together item name, tier and enchantment level and converts it to the
		matching item_id.
		"""
		# Gets the values of the user inputs
		input_name = self.item_type
		input_tier = self.tier_value
		input_enchant = self.enchant_value

		"""In the following code blocks, the item_tier will be identified"""

		# Convert tier into rarity name, i.e. "Expert's" instead of T5
		tiers_list = json.loads(config.get("Item Data", "tier_list"))  # Gets tier list from config file
		tiers_ranking = json.loads(config.get("Item Data", "tier_ranking"))  # List of the name of each tier

		for i in range(len(tiers_ranking)):
			if input_tier == tiers_list[i]:
				item_tier = tiers_ranking[i]

		"""In the following code blocks, the item_name will be identified"""

		# Throws an error message if user has not selected an item type
		if input_name == json.loads(config.get("Other Labels Default", "search_labels_list"))[1]:
			# The below line is broken on Linux systems. Needs a fix, but is non-critical.
			#error_msg(text="ERROR! Please Check Item Info")
			pass

		item_label = f"{item_tier} {input_name}"  # Combines the item name like seen in-game

		# Based on item tier and input name, get the item_id w/o enchantment from the dict in Formatted_Items_List.py
		item_from_dict = list(Formatted_Items_List.items_list.keys())[
			list(Formatted_Items_List.items_list.values()).index(
				item_label)]  # Retrieves the item_id. More info found here: https://stackoverflow.com/a/13149770

		# Add enchantment level to the item_id
		if input_enchant == "None":
			item_id = item_from_dict
			return item_id
		else:
			item_id = f"{item_from_dict}@{input_enchant}"
			return item_id

	@staticmethod
	def fetch_data(dataframe, keyword):
		"""
		Makes it quicker to fetch data from the pandas dataframe.

		:param dataframe: pandas class
		:param str keyword: column name
		:return: element in the first row and the given column
		"""
		return dataframe.iloc[0][keyword]

	def data_from_api(self):
		"""
		1. Put together the url for the API call
		2. Make the api call and store it in a variable
		3. Make the dataframe with pandas and use the read_json method
		4. Use the self.fetch_data method to obtain various data that we can use to populate
			labels down the line
		"""
		# Gets the quality ID of the quality name
		item_quality_list = json.loads(config.get("Item Data", "item_quality"))
		item_quality_id = item_quality_list.index(self.quality_value)

		# URL for the API call
		url = f"{self.base_url}{self.item_id}.json?locations={self.city}&qualities={item_quality_id + 1}"
		# Datatable with pandas' dataframe
		pd.set_option("display.max_columns", 11)
		df = pd.read_json(url)
		return df

	def update_labels(self, labels_object, item_image_object):
		"""Analysis data from the datatable and feeds them to the labels to update."""
		# Updates all class attributes, otherwise they will use the default values
		self.update_class_attributes()

		df = self.data_from_api()

		# Updates class attributes to fetch the new user inputs
		self.update_class_attributes()

		# Fetches data from data table df using fetch_data method.
		item_id = self.fetch_data(df, "item_id")
		my_city = self.fetch_data(df, "city")
		sell_price_min = self.fetch_data(df, "sell_price_min")
		sell_price_min_date = self.fetch_data(df, "sell_price_min_date")
		buy_price_max = self.fetch_data(df, "buy_price_max")
		buy_price_max_date = self.fetch_data(df, "buy_price_max_date")

		# Formats the name, from item ID to the same item name as in-game
		item_id = Formatted_Items_List.items_list.get(item_id)

		# Formats the date and time so it instead shows how many days since last update. Formats to "over 30 days"
		# if last update was over 30 days ago
		sell_price_min_date = time_dif(sell_price_min_date)
		if sell_price_min_date > 30:
			sell_price_min_date = "Over 30 days ago"
		else:
			sell_price_min_date = f"{sell_price_min_date} days ago"

		buy_price_max_date = time_dif(buy_price_max_date)
		if buy_price_max_date > 30:
			buy_price_max_date = "Over 30 days ago"
		else:
			buy_price_max_date = f"{buy_price_max_date} days ago"

		# Appends all data to a list, used to feed the result item labels
		data_list = [item_id, my_city, sell_price_min, sell_price_min_date, buy_price_max, buy_price_max_date]
		labels_object.result_item_labels(labels_value=data_list)

		# Updates item image label
		item_image_object.update_image(update=True, item_id=self.item_id)



def center_window(master):
	master.eval('tk::PlaceWindow . center')  # Center windows


def loading_screen(master, path):
	img_load = ImageTk.PhotoImage(Image.open(path))
	label = tk.Label(master, image=img_load)
	label.pack()


def update_item_list(event):
	global item_type_list, item_list_dropdown
	
	item_list_dropdown["menu"].delete(0, "end")

	# Insert list of new functions
	item_type_list = list(items_list.get(archetype_options_value.get()))  # Refresh list
	for name in item_type_list:
		item_list_dropdown["menu"].add_command(label=name, command=tk._setit(item_type_value, name))
	
	item_type_value.set(item_type_list[0])

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
	to_date_y = to_time[0:4]
	to_date_m = to_time[5:7]
	to_date_d = to_time[8:10]

	to_date_formatted = date(int(to_date_y), int(to_date_m), int(to_date_d))

	delta_date = to_date_formatted - now_date_formatted

	return_delta_days = delta_date.days

	return return_delta_days * -1


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


# Broken code on Linux systems. Needs fix, but is non-critical.
def error_msg(text):
	# Create new error window
	error_root = tk.Tk()
	error_root.title("ERROR!")
	error_root.iconbitmap("img/ao_bitmap_logo.ico")

	my_label = tk.Label(error_root, text=text, width=35, height=3)
	my_label.pack(padx=0, pady=0)
	center_window(error_root)


def update_user_input():
	global archetype_options_value, item_type_value, tier_value, enchant_value, quality_value, city_value
	return [archetype_options_value, item_type_value, tier_value, enchant_value, quality_value, city_value]


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
# root.iconbitmap("img/ao_bitmap_logo.ico")

# Calculate user screen center and set resolution || NOTE: STILL NOT PERFECT
root.geometry(config.get("DEFAULT", "resolution"))  # Set window dimensions
center_window(root)  # Center window

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
treasure_bg = treasure_bg.resize((treasure_bg_width * 2, treasure_bg_height * 2), Image.ANTIALIAS)
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
# Return all the item archetypes in the equip_list dictionary
items_list_keys = list(items_list)

# Make labels for user search
select_label = MyLabels(search_canvas)
select_label.search_labels()

# Make labels for result data
result_label = MyLabels(result_canvas)
result_label.result_labels()

result_item_list = json.loads(config.get("API Results", "retrieve_data"))  # Loads the default values for the labels
result_item_label = MyLabels(master=result_canvas, column=1)
result_item_label.result_item_labels()

# archetype list - List of item archetypes
archetype_options_list = list()	# Initialize archetype list
for key in items_list:
	archetype_options_list.append(key)	# Append item types into a new list so the drop down menu works

archetype_options_value = tk.StringVar()  # This is the selected value of the dropdown menu
archetype_options_value.set(archetype_options_list[0])  # Sets the default value for the dropdown menu

archetype_options_dropdown = tk.OptionMenu(search_canvas, archetype_options_value, *archetype_options_list,
                                           command=update_item_list)
archetype_options_dropdown.grid(column=1, row=0, padx=5, pady=5)

# Item type list - list of item types
item_type_value = tk.StringVar()  # Value of the selected item in the dropdown menu
item_type_value.set("Broadsword")  # Sets the default value of the dropdown menu
item_type_list = items_list.get(archetype_options_value.get())  # Gets the available items based on item archetype

item_list_dropdown = tk.OptionMenu(search_canvas, item_type_value, *item_type_list)
item_list_dropdown.grid(column=1, row=1, padx=5, pady=5)

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

# Item thumbnail
item_thumbnail = ItemThumbnail(master=result_canvas)
default_thumbnail_img = "T4_MAIN_SWORD"
item_thumbnail.update_image(item_id=default_thumbnail_img)
item_thumbnail.grid(column=1)

"""
Here, API calls is setup. The following new variables are not strictly necessary, but it makes
readability and working with much easier. All the variables are objects of the tk.StringVar class and are the objects
that the user selects with the dropdown menus.
"""
item_archetype = archetype_options_value
item_type = item_type_value  # Item type
tier_value = tier_value  # Item tier
enchant_value = enchant_value  # Item Enchantment level
quality_value = quality_value  # Item Quality
city = city_value  # Filter what city to search in

api_call = ApiPrice(item_archetype, item_type, tier_value, enchant_value, quality_value, city)

"""Submit button to update item prices and data"""
submit_button = tk.Button(search_canvas, text="Submit Request",
                          command=lambda: api_call.update_labels(result_item_label, item_thumbnail))
submit_button.grid(column=1, row=6, padx=5, pady=5)

root.resizable(False, False)  # Disable resizing app window
root.mainloop()
