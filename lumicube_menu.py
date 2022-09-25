import time
from typing import Callable

# a line should be spaced 18 high at font 1
# 13 lines fit on screen

# each loop, a button press will be counter ~600 times, handle that so we
# only deal with a button press once per loop

buttons_last_pressed = {
	"top": buttons.top_pressed_count,
	"middle": buttons.middle_pressed_count,
	"bottom": buttons.bottom_pressed_count
}

class Item:
	def __init__(self, parent, text: str, callback: Callable):
		self.callback = callback
		self.parent = parent
		parent.add_child(self)
		# cut off text, max width is 29 characters at std font
		if len(text) > 29: 
			self.text = text[:26] + "..."
		else:
			self.text = text

	def select(self):
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
		if self.current_selected < 12:  # account for menu taking up a line
			for i, child in enumerate(self.children):  
				text = ".." if child == self.parent else child.text
				if i != self.current_selected:
					# a line is 18 pixels high at standard font
					screen.write_text(0, line*18, text, black, white)
				else:
					screen.write_text(0, line*18, text, 1, black, white) 
				line += 1
		else:
			line = 1
			# can only show 13 rows on screen (minus 1 for menu text = 12)
			children_to_show = self.children[self.current_selected-11:self.current_selected+1]
			for i, child in enumerate(children_to_show, self.current_selected-11):
				text = ".." if child == self.parent else child.text
				if i != self.current_selected:
					# a line is 18 pixels high at standard font
					screen.write_text(0, line*18, text, black, white)
				else:
					screen.write_text(0, line*18, text, 1, black, white) 	
				line += 1

	def select(self):
		# set screen to show all children, and highlight the first child (not the .. parent menu)
		self.draw_menu()

	def up(self):
		# highlight the next child below current (or top-most)
		if self.current_selected == 0:
			return
		self.current_selected -= 1
		self.draw_menu()
			

main_menu = Menu("main", "Main Menu")
first_menu = Menu(main_menu, "First Sub-Menu")
second_menu = Menu(main_menu, "Second Sub-Menu")
first_first_menu = Menu(first_menu, "First Sub-Sub-Menu")

first_item = Item(main_menu, "first item", lambda: print("first item selected"))
second_item = Item(first_menu, "second item", lambda: print("second item selected"))
third_item = Item(first_first_menu, "second item", lambda: print("third item selected"))

menu = main_menu
menu.draw_menu()
while True:
	menu = menu.check_buttons()  # draw new menu, select item, highlight new selections, and keep track of current menu
