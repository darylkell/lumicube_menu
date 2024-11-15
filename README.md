# lumicube_menu

What is it?
------
A menu system that can be employed for the (optional) rear screen of Abstract Foundry's Lumicube.

As the Lumicube has 3 rear buttons, the menu allows the top and bottom buttons to navigate on the rear screen, and the middle button to select an option from the menu that you have selected. In this way you can run scripts from the menu, instead of logging into the Lumicube's web interface.

The provided script demonstrates some default projects (by Abstract Foundry) that can be run from the menu.  Scripts are threaded (credit: original implementation primarily by Discord user DeusP#0015).


How to use it?
------
Have a look at the example script.  It uses object-oriented programming (OOP) to create menus, and items in the menus.  Menus are able to hold other menus, and items. Menus are for displaying other menus and items, while items are for running scripts/functions.<br><br>
You'll need the `Menu`, `Item`, and `ThreadedRunner` classes, so copy those in from the script. They rely on the following imports, so you'll need to import these too:
```
    import queue
    from typing import Callable
    from threading import Thread
```
Now that you have the classes in the script that you'll use to create your menu, you also need functions that you want to run when you select items in the menu you're creating. The example here has copied in code from the Lumicube's default projects and are defined in the following functions: `rain`, `lava` and a modified `stats` function. You'll notice that the two functions that are created later as Items have a task_runner assigned to them. That means the while loop within their function must yield every so often (easiest to add every loop). Use the example script to see how this works.

You need to keep track of the buttons as they are being pressed, so this bit of code sets that up:<br>
```
    buttons_last_pressed = {
        "top": buttons.top_pressed_count,
        "middle": buttons.middle_pressed_count,
        "bottom": buttons.bottom_pressed_count
    }
```

You need a thread runner, which in the example controls the thread painting the led screens:<br>
    `task_runner = ThreadedRunner()`

From there, you're ready to go building your menu:<br>
```   
    main_menu = Menu("main", "Main Menu")
    scripts_menu = Menu(main_menu, "Scripts")

    first_item = Item("Rain", rain, task_runner)
    second_item = Item("Lava", lava, task_runner)
    third_item = Item("Statistics", stats)
```
Here we have created three items, and two menus. One of the menus is placed in the main (top-most) menu.<br>
The items are given a title for the menu, a task_runner object to run in (or ignored if not desired to be run in a thread), and a function that will be called when the item is selected from the menu.
The 'Statistics' function here doesn't get a task_runner assigned to it, as it leaves the thread_runner playing with the led panels and instead is writing stats to the rear screen.  As these are exclusive of each other, the 'Statistics' not having a task_runner allows the rear screen to show some information while the led panels continue unhindered.

Now we place those items in to their 'homes' in the menus we created:
```
    scripts_menu.add_child(first_item)
    scripts_menu.add_child(second_item)
    main_menu.add_child(third_item)
```
It should be noted that the main_menu already has scripts_menu in it from when scripts_menu was initialised, but the items get placed specifically into their homes: one will go in the main menu, the other two will go in the 'Scripts' sub-menu.

You can then draw the menu on the screen:
`menu.draw_menu()`

A global variable 'menu' tracks what Menu is currently being displayed, and then it is drawn. The while loop keeps track of which menu is currently being displayed on screen:

    menu = main_menu
    menu.draw_menu()
    while True:
        menu = menu.check_buttons()

The end result of this example code looks like this on the rear screen:
```      --- Main Menu ---
> Scripts
Statistics
```
You can see in the main menu, that the 'Scripts' menu has been preceded with a '> ' to show that 'Scripts' is another menu that can be navigated into.  'Statistics' doesn't have that '>' symbol - it is a menu item that will run a script.

When you select '> Scripts', the following menu appears on the rear screen:
```       --- Scripts ---
..
Rain
Lava
```
The '..' in the 'Scripts' menu is an option to go back to the main Menu, which is the parent of the 'Scripts' menu.


### Security Warning
------
Please properly vet anything you download from the internet, including this script. It could do anything.
