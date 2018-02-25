import curses

screen = curses.initscr()
screen.immedok(True)

try:

    box1 = curses.newwin(2, 12, 1, 1)
    box1.immedok(True)

    box1.box()
    box1.addstr("Time")
    box1.addstr

    screen.getch()

finally:
    curses.endwin()
