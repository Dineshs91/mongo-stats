import time
import curses


class Screen:
    def __init__(self, stdscr, row=0, col=0):
        self.stdscr = stdscr

        # These are the initial coordinates of the cursor.
        # These will be updated as text is printed on to the screen.
        # init row and col should never be updated once initialised.
        self.init_row = row
        self.init_col = col

        self.row = row
        self.col = col

        # Initialize curses.
        curses.start_color()
        curses.use_default_colors()
        stdscr.nodelay(1)

        # Create an init pair with green color.
        curses.init_pair(1, curses.COLOR_GREEN, -1)

    def print(self, text, label=None, same_row=False):
        # Clear before writing.
        self.stdscr.clrtoeol()
        if label == "heading":
            self.col = 0
            self.stdscr.addstr(self.row, self.col, text, curses.color_pair(1))
        else:
            if self.col == 0:
                self.col = 3
            self.stdscr.addstr(self.row, self.col, text)

        if not same_row:
            self.row += 1
            self.col = 0
        else:
            # Update col cursor position.
            self.col += len(text) + 2

    def start(self):
        self.stdscr.refresh()
        char = self.stdscr.getch()
        if char == 113:
            return False
        return True

    def clear(self):
        self.row = self.init_row
        self.col = self.init_col

    def sleep(self, secs, stdscr):
        """
        Sleeping for a long time will freeze the screen for the user.
        Pressing a `q` button won't get processed until the sleep
        time is over.

        This custom sleep, sleeps over steps of `freq` values, so that
        we can response to `q` faster.
        """
        freq = 0.1

        while True:
            time.sleep(freq)
            secs -= freq

            char = stdscr.getch()
            if char == 113:
                exit(0)

            if secs <= 0:
                return
