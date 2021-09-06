"""
This program fetches data from the Albion Online Data Project and displays the price on an interactive GUI.
"""

import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
from data import item_selections


def loading_screen():
	img = "img/albion_logo.png"
	img_load = ImageTk.PhotoImage(Image.open(img))
	label = tk.Label(root, image=img_load)
	label.pack()


"""
Developer tools to test features during development.
"""
toggle_loading_screen = False

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

category_options = items_list

category_options_list = list()
for key in category_options:
	category_options_list.append(key)  # Appends item types into a new list so the drop down menu works

# Item type selection - sub category
sub_cat_options = list()
sub_cat_index = 0
for key in range(len(items_list)):
	values = items_list.values()
	values_list = list(values)
	# print(values_list[key])
	sub_cat_options.append(values_list[key])
	key += 1

# Set default key
category_options_default = tk.StringVar()
category_options_default.set(category_options_list[0])

category_options_dropdown = tk.OptionMenu(canvas, category_options_default, *category_options_list)
category_options_dropdown.pack(pady=20)

root.resizable(False, False)  # Disable resizing app window
root.mainloop()
