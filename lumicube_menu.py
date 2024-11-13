from contextlib import contextmanager
from typing import Callable, Generator, List, Optional, Union
from threading import Event, Thread


### GENERAL NOTES
# a line should be spaced 18px high at font 1
# 13 total lines fit on screen
#
# each loop, a button press will be counted ~600 times, we need to 
# handle that so we only deal with a button press once per main loop


class ThreadedRunner:
	def __init__(self) -> None:
		self.thread = None
		self.stop_event = Event()

	def run(self, callback: Callable) -> None:
		if self.thread and self.thread.is_alive():
			self.stop_event.set()
			self.thread.join()
			time.sleep(0.1)
		self.stop_event.clear()
		self.thread = Thread(target=self.runner, args=(callback,), daemon=True)
		self.thread.start()

	def runner(self, callback: Callable) -> None:
		try:
			for step in callback():
				if self.stop_event.is_set():
					break
		except Exception as e:
			print(f"Error in runner: {e}")
		finally:
			menu.draw_menu()


class Item:
	def __init__(self, text: str, callback: Callable, runner: Optional[ThreadedRunner] = None) -> None:
		self.callback = callback
		self.runner = runner
		# cut off text, max width is 29 characters at std font
		if len(text) > 29:
			self.text = f"{text[:26]}..."
		else:
			self.text = text

	def select(self) -> None:
		if self.runner:
			self.runner.run(self.callback)
		else:
			self.callback()


class Menu:
	def __init__(self, parent: Union[str, 'Menu'], text: str) -> None:
		self.children = []
		self.parent = parent
		self.current_selected = 0  # index that should be highlighted

		if parent != "main":
			self.children.append(parent)  # up a folder
			self.parent.add_child(self)
		
		if len(text) > 29:
			self.text = f"{text[:25]}..."
		else:
			self.text = text

	def add_child(self, child: Union[Item, 'Menu']) -> None:
		self.children.append(child)

	def check_buttons(self) -> 'Menu':
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

	def down(self) -> None:
		"""
		highlight the next child below current or wrap-around
		"""
		self.current_selected = (self.current_selected + 1) % len(self.children)
		self.draw_menu()

	def draw_menu(self) -> None:
		"""
		draw all children on screen, highlighting the relevant current_selected
		menu title at the top
		"""
		title = f" --- {self.text[:19]} ---"
		screen.write_text(0, 0, f"{title:^29}", black, white)  # menu title at the top
		line = 1
		up_folder = f"..{' ' * 27}"
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
						text = f"> {child.text[:27]}"
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
			# can only show 13 rows on screen at a time (minus 1 for menu text = 12)
			children_to_show = self.children[self.current_selected - 11:self.current_selected + 1]
			for i, child in enumerate(children_to_show, self.current_selected - 11):
				text = up_folder if child == self.parent else f"{child.text}{' ' * (29 - len(child.text))}" 
				if i != self.current_selected:
					# a line is 18 pixels high at standard font
					screen.write_text(0, line*18, text, black, white)
				else:
					screen.write_text(0, line*18, text, 1, black, white)
				line += 1
		# black the rest of the screen
		# for i in range(13-line):
		# 	screen.write_text(0, line*18, " "*29, black, white)


	def select(self) -> None:
		"""
		set screen to show all children, and highlight the first child
		"""
		self.draw_menu()

	def up(self) -> None:
		"""
		highlight the next child above current or wrap-around
		"""
		self.current_selected = (self.current_selected - 1) % len(self.children)
		self.draw_menu()


@contextmanager
def clear_screen():
	"""
	Helper function to re-draw the screen black, usage:
	with clear_screen():
		text = "On-screen text"
		screen.write_text(10, 18, text, 1, white, black)
		time.sleep(3)
	"""
	screen.draw_rectangle(0, 0, 320, 240, black)
	try:
		yield
	finally:
		menu.draw_menu()

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

def lava_colour(x: int, y: int, z: int, t: float) -> tuple:
	scale = 0.10
	speed = 0.05
	hue = noise_4d(scale * x, scale * y, scale * z, speed * t)
	return hsv_colour(hue, 1, 1)

def paint_cube(t: float) -> None:
	colours = {}
	for x in range(9):
		for y in range(9):
			for z in range(9):
				if x == 8 or y == 8 or z == 8:
					colour = lava_colour(x, y, z, t)
					colours[x, y, z] = colour
	display.set_3d(colours)

def lava():
	t = 0
	while True:
		paint_cube(t)
		time.sleep(1/30)
		yield "step"
		t += 1

def stats() -> None:
	with clear_screen():
		text = f"IP address: {pi.ip_address()}\n" \
			   f"CPU temp  : {pi.cpu_temp():.1f}\n" \
			   f"CPU usage : {pi.cpu_percent():.1f} %\n" \
			   f"RAM usage : {pi.ram_percent_used():.1f} %\n" \
			   f"Disk usage: {pi.disk_percent():.1f} %\n"
		screen.write_text(10, 18, text, 1, white, black)
		time.sleep(4)


# variable to keep track of button presses
buttons_last_pressed = {
	"top": buttons.top_pressed_count,
	"middle": buttons.middle_pressed_count,
	"bottom": buttons.bottom_pressed_count
}

task_runner = ThreadedRunner()

main_menu = Menu("main", "Main Menu")
scripts_menu = Menu(main_menu, "Scripts")

# menu items that will loop in a thread, affecting the led panels
first_item = Item("Rain", rain, task_runner)
second_item = Item("Lava", lava, task_runner)

# menu item that will run in its own thread, affecting the back screen only while the task_runner works at its current task
third_item = Item("Statistics", stats)

scripts_menu.add_child(first_item)
scripts_menu.add_child(second_item)
main_menu.add_child(third_item)

# menu global variable keeps track of the current menu
menu = main_menu
menu.draw_menu()

# loop so that we can continue to check the buttons being pressed and act accordingly, keeping track of the current menu
while True:
	menu = menu.check_buttons()  # draw new menu, select item, highlight new selections, and keep track of current menu