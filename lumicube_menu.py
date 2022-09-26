import queue
from typing import Callable
from threading import Thread


# a line should be spaced 18 high at font 1
# 13 lines fit on screen

# each loop, a button press will be counter ~600 times, handle that so we
# only deal with a button press once per loop
buttons_last_pressed = {
	"top": buttons.top_pressed_count,
	"middle": buttons.middle_pressed_count,
	"bottom": buttons.bottom_pressed_count
}


thread_queue = queue.Queue()
def runner(callback):
	try:
		for step in callback():
			try:
				action = thread_queue.get_nowait()
				if action == "stop":
					print("stop thread")
					break
			except Exception as e:
				pass
	except:
		menu.draw_menu()

class ThreadedRunner:
	def __init__(self):
		self.thread = None

	def run(self, callback):
		if self.thread:
			thread_queue.put("stop")
			self.thread.join()
		print(runner)
		self.thread = Thread(target=runner, args=[callback])
		self.thread.start()

class Item:
	def __init__(self, text: str, runner, callback: Callable):
		self.callback = callback
		self.runner = runner
		# cut off text, max width is 29 characters at std font
		if len(text) > 29:
			self.text = text[:26] + "..."
		else:
			self.text = text

	def select(self):
		if self.runner:
			self.runner.run(self.callback)
		else:
			self.callback()

class Menu:
	def __init__(self, parent, text: str):
		self.children = []
		if parent != "main":
			self.children.append(parent)  # up a folder
		self.parent = parent
		self.current_selected = 0  # index that should be highlighted
		if len(text) > 29:
			self.text = text[:25] + "..."
		else:
			self.text = text
		if not self.parent == "main":
			self.parent.add_child(self)

	def add_child(self, child):
		self.children.append(child)

	def check_buttons(self):
		if buttons.top_pressed and buttons_last_pressed["top"] != buttons.top_pressed_count:
			buttons_last_pressed["top"] = buttons.top_pressed_count
			self.up()
		elif buttons.bottom_pressed and buttons_last_pressed["bottom"] != buttons.bottom_pressed_count:
			buttons_last_pressed["bottom"] = buttons.bottom_pressed_count
			self.down()
		elif buttons.middle_pressed and buttons_last_pressed["middle"] != buttons.middle_pressed_count:
			buttons_last_pressed["middle"] = buttons.middle_pressed_count
			selected = self.children[self.current_selected]
			selected.select()
			# will return new menu or stay the current menu if selected was an item
			return selected if isinstance(selected, Menu) else self
		return self

	def down(self):
		# highlight the next child below current (or bottom-most)
		if self.current_selected == (len(self.children) - 1):
			return
		self.current_selected += 1
		self.draw_menu()

	def draw_menu(self):
		# draw all children on screen, highlighting the relevant current_selected
		# menu title at the top
		title = f" --- {self.text[:19]} ---"
		screen.write_text(0, 0, f"{title:^29}", black, white)  # menu title at the top
		line = 1
		up_folder = ".." + " " * 27
		if self.current_selected < 12:  # account for menu taking up a line
			for i in range(13):
				if i < len(self.children):
					child = self.children[i]
				else:
					child = None
				if not child:
					screen.write_text(0, line*18, " "*29, black, white)
				else:
					if child == self.parent:
						text = up_folder
					elif isinstance(child, Menu):
						text = "> " + child.text[:27]
					else:
						text = child.text
					#text = up_folder if child == self.parent else child.text
					text += " " * (29 - len(text))  # clear text artifacts on the line
					if i != self.current_selected:
						# a line is 18 pixels high at standard font
						screen.write_text(0, line*18, text, black, white)
					else:
						screen.write_text(0, line*18, text, 1, black, white)
				line += 1
		else:
			# can only show 13 rows on screen (minus 1 for menu text = 12)
			children_to_show = self.children[self.current_selected-11:self.current_selected+1]
			for i, child in enumerate(children_to_show, self.current_selected-11):
				text = up_folder if child == self.parent else f"{child.text}{' ' * (len(child.text) - 29)}" 
				if i != self.current_selected:
					# a line is 18 pixels high at standard font
					screen.write_text(0, line*18, text, black, white)
				else:
					screen.write_text(0, line*18, text, 1, black, white)
				line += 1
		# black the rest of the screen
		# for i in range(13-line):
		# 	screen.write_text(0, line*18, " "*29, black, white)

	def select(self):
		# set screen to show all children, and highlight the first child (not the .. parent menu)
		self.draw_menu()

	def up(self):
		# highlight the next child below current (or top-most)
		if self.current_selected == 0:
			return
		self.current_selected -= 1
		self.draw_menu()

def rain():
	display.set_all(black)
	rows = [[0 for x in range(16)] for y in range(8)]
	while True:
		# Shift all rows down
		rows.pop(0)
		# Create a new row
		top_row = rows[-1]
		new_top_row = []
		for prev_pixel in top_row:
			new_pixel = 0
			# If the previous pixel was the start of a drop, create the
			# droplet tail by reducing the brightness for the new pixel
			if prev_pixel > 0:
				new_pixel = prev_pixel - 0.4
				new_pixel = max(new_pixel, 0.0)
			# Sometimes generate a new droplet
			elif random.random() < 0.1:
				new_pixel = 1
			new_top_row.append(new_pixel)
		rows.append(new_top_row)
		# Convert the brightness values to LED colours
		leds = {}
		for y in range(0,8):
			for x in range(0,16):
				leds[(x, y)] = hsv_colour(0.6, 1, rows[y][x])
		display.set_leds(leds)
		time.sleep(1/15)
		yield "step"

# Generate a lava lamp effect using OpenSimplex noise.

def lava_colour(x, y, z, t):
	scale = 0.10
	speed = 0.05
	hue = noise_4d(scale * x, scale * y, scale * z, speed * t)
	return hsv_colour(hue, 1, 1)

def paint_cube(t):
	colours = {}
	for x in range(9):
		for y in range(9):
			for z in range(9):
				if x == 8 or y == 8 or z == 8:
					colour = lava_colour(x, y, z, t)
					colours[x,y,z] = colour
	display.set_3d(colours)

def lava():
	t = 0
	while True:
		paint_cube(t)
		time.sleep(1/30)
		yield "step"
		t += 1

def stats():
	screen.draw_rectangle(0, 0, 320, 240, black)
	text = f"IP address: {pi.ip_address()}\n" \
		f"CPU temp  : {pi.cpu_temp():.1f}\n" \
		f"CPU usage : {pi.cpu_percent():.1f}\n" \
    	f"RAM usage : {pi.ram_percent_used():.1f}\n" \
    	f"Disk usage: {pi.disk_percent():.1f}\n"
	screen.write_text(10, 18, text, 1, white, black)
	time.sleep(4)
	menu.draw_menu()


main_menu = Menu("main", "Main Menu")
scripts_menu = Menu(main_menu, "Scripts")

task_runner = ThreadedRunner()
first_item = Item("Rain", task_runner, rain)
second_item = Item("Lava", task_runner, lava)
third_item = Item("Statistics", None, stats)

scripts_menu.add_child(first_item)
scripts_menu.add_child(second_item)
main_menu.add_child(third_item)

menu = main_menu
menu.draw_menu()
while True:
	menu = menu.check_buttons()  # draw new menu, select item, highlight new selections, and keep track of current menu
