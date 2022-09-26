# lumicube_menu

_What is it?_<br>
A menu system that can be employed for the (optional) rear screen of Abstract Foundry's Lumicube.

As the Lumicube has 3 rear buttons, the menu allows the top and bottom buttons to navigate on the rear screen, and the middle button to select an option from the menu that you have selected. In this way you can run scripts from the menu, instead of logging into the Lumicube's web interface.

The provided script demonstrates some default projects (by Abstract Foundry) that can be run from the menu.  

<br><br>
_How to use it?_<br>
Have a look at the example script.  It uses object-oriented programming (OOP) to create menus, and items in the menus.  Menus are able to hold other menus, and items. Menus are for displaying other menus and items, while items are for running scripts/functions.
You need to keep track of the buttons as they are being pressed, so this bit of code sets that up:
`buttons_last_pressed = {
	"top": buttons.top_pressed_count,
	"middle": buttons.middle_pressed_count,
	"bottom": buttons.bottom_pressed_count
}`
You also need a queue to run the threads:
`thread_queue = queue.Queue()`
And a thread runner:
`task_runner = ThreadedRunner()`

From there, you're ready to go building your menu:
`main_menu = Menu("main", "Main Menu")
scripts_menu = Menu(main_menu, "Scripts")

first_item = Item("Rain", task_runner, rain)
second_item = Item("Lava", task_runner, lava)
third_item = Item("Statistics", None, stats)`
Here we have created three items, and two menus. One of the menus is placed in the main (top-most) menu.
The items are given a title for the menu, a task_runner object to run in (or None if not desired to be run in a thread), and a function that will be called when the item is selected from the menu.

Now we place those items in to their 'homes' in the menu:
`scripts_menu.add_child(first_item)
scripts_menu.add_child(second_item)
main_menu.add_child(third_item)`
It should be noted that he main_menu already has scripts_menu in it from when scripts_menu was initialised, but the items get placed specifically into their homes: one will go in the main menu, the other will go in the scripts_menu sub-menu.

You can then draw the menu on the screen:
`menu.draw_menu()`

This while loop keeps track of which menu is currently being displayed on screen:
`menu = main_menu
while True:
	menu = menu.check_buttons()`
