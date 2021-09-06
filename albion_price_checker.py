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


def update_sub_cat(event):
	global sub_cat_options_list, sub_dropdown

	sub_cat_options_value.set("Item Type")
	sub_dropdown["menu"].delete(0, "end")

	selected_name = category_options_value.get()

	# Insert list of new functions
	sub_cat_options_list = items_list.get(selected_name)  # Refresh list
	for name in sub_cat_options_list:
		sub_dropdown["menu"].add_command(label=name, command=tk._setit(sub_cat_options_value, name))


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
category_options_selected = "None"

category_options = items_list

category_options_list = list()
for key in category_options:
	category_options_list.append(key)  # Appends item types into a new list so the drop down menu works

sub_cat_options_list = []  # Sub category items list


# Set default key
category_options_value = tk.StringVar()
category_options_value.set(category_options_list[0])
category_options_value_default = category_options_value

category_options_dropdown = tk.OptionMenu(canvas, category_options_value, *category_options_list, command=update_sub_cat)
category_options_dropdown.pack(pady=10)

# Sub category list
sub_cat_options_value = tk.StringVar()
sub_cat_options_value.set("Item Type")

sub_cat_options_list = items_list.get(category_options_value.get())

sub_dropdown = tk.OptionMenu(canvas, sub_cat_options_value, *sub_cat_options_list)
sub_dropdown.pack(pady=10)


root.resizable(False, False)  # Disable resizing app window
root.mainloop()
