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

        # Table heading color
        curses.init_pair(2, curses.COLOR_YELLOW, -1)

    def start(self):
        self.stdscr.refresh()
        char = self.stdscr.getch()
        if char == 113:
            return False
        return True

    def print(self, text, label=None, same_row=False):
        # Clear before writing.
        self.stdscr.clrtoeol()
        if label == "heading":
            self.col = 0

            # For heading make sure there is an empty line before.
            self.row += 1
            self.stdscr.addstr(self.row, self.col, text, curses.color_pair(1))
        else:
            if self.col == 0:
                self.col = 3

            # Print only if the text can be displayed in the visible screen.
            # Otherwise the window has to be maximised.
            if (self.col + len(text)) < self.stdscr.getmaxyx()[1]:
                self.stdscr.addstr(self.row, self.col, text)

        if not same_row:
            self.row += 1
            self.col = 0
        else:
            # Update col cursor position.
            self.col += len(text) + 2

    def print_table(self, headings, rows):
        """
        Send a list of headings and list of dict objects in rows.

        Ex:
        headings = ['s.no', 'name']
        rows = [
            {
                "s.no": 1,
                "name": "John Doe"
            },
            {
                "s.no": 2,
                "name": "Red John"
            }
        ]

        s.no     name
         1     John Doe
         2     Red John
        """
        self.stdscr.clrtoeol()
        # Store the max length of each column in the table. This includes the heading and
        # the actual text.
        headings_col_pos = {}
        for heading in headings:
            headings_col_pos[heading] = len(heading) + 2

        for row in rows:
            for key in row.keys():
                value = row[key]

                if len(value) > headings_col_pos[key]:
                    headings_col_pos[key] = len(value) + 2

        # print headings
        for heading in headings:
            if (self.col + headings_col_pos[heading]) < self.stdscr.getmaxyx()[1]:
                self.stdscr.addstr(self.row, self.col, heading, curses.color_pair(2))
                self.col += headings_col_pos[heading] + 3
            else:
                break

        self.row += 1
        self.col = self.init_col

        # print rows
        for row in rows:
            for heading in headings:
                if (self.col + headings_col_pos[heading]) < self.stdscr.getmaxyx()[1]:
                    self.stdscr.addstr(self.row, self.col, row[heading])
                    self.col += headings_col_pos[heading] + 3
                else:
                    break

            self.row += 1
            self.col = self.init_col

    def clear(self):
        self.row = self.init_row
        self.col = self.init_col

    def sleep(self, secs, stdscr):
        """
        Sleeping for a long time will freeze the screen for the user.
        Pressing a `q` button won't get processed until the sleep
        time is over.

        This custom sleep, sleeps in steps of `freq` values, so that
        we can respond to `q` faster.
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
