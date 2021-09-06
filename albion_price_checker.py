import tkinter as tk
from PIL import ImageTk, Image
from data import item_selections

def loading_screen():
	img = "img/albion_logo.png"
	img_load = ImageTk.PhotoImage(Image.open(img))
	label = tk.Label(root, image=img_load)
	label.pack()


# Developer settings
toggle_loading_screen = False

# Application window
root = tk.Tk()

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

# loading_screen
if toggle_loading_screen:<
	loading_logo = "img/albion_.png"
	loading_logo_converted = ImageTk.PhotoImage(file=loading_logo, master=canvas)
	loading_label = tk.Label(canvas, image=loading_logo_converted)
	loading_label.pack()
	loading_label.after(3000, loading_label.destroy)

# clicked = tk.StringVar()
# clicked.set()
# drop = tk.OptionMenu(canvas, clicked, *options)
# drop.pack()
#
# my_button = tk.Button(canvas, text="Show Selection", command=show).pack()

print(item_selections.printstr())

root.resizable(False, False)  # Disable resizing app window
root.mainloop()