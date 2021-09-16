import shutil
import signal

from functools import partial
from types import SimpleNamespace

from urwid import Columns, LineBox

try:
    from .constants import *
    from .config import *
    from .crypt import *
    from .custom_widgets.CascadingBoxes import CascadingBoxes
    from .custom_widgets.CustomSignals import CustomSignals


except ImportError:
    from constants import *
    from config import *
    from crypt import *
    from custom_widgets.CascadingBoxes import CascadingBoxes
    from custom_widgets.CustomSignals import CustomSignals






class FileStatus(Enum):
    found = 1
    changed = 2
    not_found = 3

    @classmethod
    def from_config(cls, config_entry):
        if config_entry:
            return cls.found
        return cls.not_found


class MyMainLoop:
    def __init__(self):
        self.status = SimpleNamespace(
            # Stuff from config
            encrypted_file=FileStatus.from_config(config.encrypted_file_contents()),
            salt_file=FileStatus.from_config(config.salt()),
            demo_mode=config["is_demo"],

            # Actual status
            unlocked=False,
            password=None,

        )

        self.setup_graceful_exit()

        self.menu = None
        self.settings = None
        self.stored_passwords = None

        self.top = CascadingBoxes(main_loop=self)

        if try_no_password and (pw := unlock_with_password("")):
            self.stored_passwords = pw
            self.status.unlocked = True
            self.password = ""

        self.draw_menu()

        # TODO: Salt

    def setup_graceful_exit(self):
        signal.signal(signal.SIGHUP, self.quit)
        signal.signal(signal.SIGINT, self.quit)
        signal.signal(signal.SIGQUIT, self.quit)
        signal.signal(signal.SIGABRT, self.quit)
        signal.signal(signal.SIGTERM, self.quit)

    def draw_menu(self):
        menu_sections = []

        if not self.status.unlocked:
            menu_sections.append(menu_button(f"Unlock the Database", self.unlock_database))
        else:
            menu_sections.append(menu_button("Select a password", self.select_password))
            menu_sections.append(menu_button("Change the master-password", self.set_new_password))
            menu_sections.append(menu_button("Visit the history", self.todo))

        self.make_settings()
        menu_sections.append(Divider("╌"))
        menu_sections.append(self.settings)

        self.menu = menu("Password Manager", menu_sections)

        self.top.__init__(self.menu, main_loop=self)

    def make_settings(self):
        self.settings = sub_menu("Settings", [
            Subsection("Random Password Settings"),
            ConfigButton("password_length", self.todo),
            ConfigButton("password_contents", self.todo),
            ConfigButton("show_password_num_initial", self.todo),

            Subsection("Password Mapping"),
            ConfigButton("exit", self.todo, the_config=config["password_input_mapping"]),
            ConfigButton("website", self.todo, the_config=config["password_input_mapping"]),
            ConfigButton("username", self.todo, the_config=config["password_input_mapping"]),
            ConfigButton("email", self.todo, the_config=config["password_input_mapping"]),
            ConfigButton("password", self.todo, the_config=config["password_input_mapping"]),

            Subsection("File Settings"),
            ConfigButton("encrypted_file_name", self.todo),
            ConfigButton("salt_file_name", self.todo),
            ConfigButton("is_demo", self.todo),
            ConfigButton("demo_prefix", self.todo),

        ], self.top)

    def error_on_not_unlocked(self):
        if not self.status.unlocked:
            # Give an error
            text = "\n\nThis operation is currently not possible!\n\nPlease unlock the database first!\n\n"
            b = Button("OK")
            connect_signal(b, "click", self.top.box_up)
            f = Filler(GridFlow([AttrMap(b, None, focus_map="reversed")], 7, 15, 1, "center"))
            box = Frame(f, Text(("error", text), align="center"))
            self.top.open_non_linebox(box)
            return True
        return False

    def set_new_password(self, *_):
        if self.error_on_not_unlocked():
            return

        text = f"\n\nPlease enter your new password!" + "\n" * 4
        second_text = 7 * " " + f"(Press enter to confirm the input)\n" + 7 * " " + "(Press Ctrl+W to delete the entire string)\n\n"
        password_box0 = CustomEdit("  >>>  ", mask="*")
        text_between = Text("\n\n\n")
        password_box1 = CustomEdit("  >>>  ", mask="*")

        status_text = Text("")
        error_text = Text("", align="center")
        status_attr = AttrMap(status_text, None)
        error_attr = AttrMap(error_text, None)

        first_confirm = False

        def check_keypress(*_):
            nonlocal first_confirm
            if password_box0.get_edit_text() != password_box1.get_edit_text():
                error_text.set_text("That did not work - the passwords don't match!\n")
                error_attr.set_attr_map({None: "error"})

            elif first_confirm is False:
                error_text.set_text("Please press enter again to confirm the password!\n")
                error_attr.set_attr_map({None: "good"})
                first_confirm = True

            else:
                self.status.password = password_box0.get_edit_text()
                self.top.reset_focus()

        def change_focus(*_):
            walker.focus = abs(2 - walker.get_focus()[1])
            it = walker.get_focus()[0]
            it.set_edit_pos(len(it.get_edit_text()))

        def detect_status(*_):
            # Reset the confirmation
            nonlocal first_confirm
            first_confirm = False

            if password_box0.get_edit_text() == password_box1.get_edit_text():
                status_text.set_text(9 * " " + u" ◯ Matching\n\n")
                status_attr.set_attr_map({None: "good"})
            else:
                status_text.set_text(9 * " " + u" ◯ Not Matching\n\n")
                status_attr.set_attr_map({None: "error"})

        detect_status()

        for item in [password_box0, password_box1]:
            connect_signal(item, "done", check_keypress)
            connect_signal(item, "change_focus", change_focus)
            connect_signal(item, "postchange", detect_status)

        walker = SimpleFocusListWalker([password_box0, text_between, password_box1])
        box = Frame(ListBox(walker), Text(("input", text), align="center"), Pile([error_attr, status_attr, Text(("hint", second_text))]))

        self.top.open_non_linebox(box)

    def create_new_database(self, *_):
        self.status.unlocked = True
        self.stored_passwords = []

        # Password prompt
        self.set_new_password()

    def select_password(self, *_):
        if self.stored_passwords is None:
            raise ValueError(f"The stored passwords aren't there!")

        def handle_text(*_):
            text = search_box.get_edit_text()
            column_focus.set_text(text).update()
            set_passwords()

        def compute_best_password_match():
            return Password.select_matching_items_from_list(self.stored_passwords, columns, column_focus.focus)

        def set_passwords():
            best = compute_best_password_match()
            Password.set_columns_from_list(best, columns, content)
            cols = [Columns(item, dividechars=2) for item in content]
            table.body = SimpleFocusListWalker([AttrMap(item, None, focus_map="reversed") for item in cols[:len(best)]])

        def handle_change_column(column):
            column_focus.set_focus(column)
            box.focus_position = "header"
            search_box.set_edit_text(column.search_text)
            search_box.set_edit_pos(len(column.search_text))
            for item in columns:
                item.update()

            self.quit()
            # raise ValueError(f"{history.dump()}")

        def switch_focus(*_):
            try:
                if box.focus_position == "header":
                    box.focus_position = "body"
                    table.focus_position = 0
                else:
                    box.focus_position = "header"
            except IndexError:
                box.focus_position = "header"

        def reset(*_):
            column_focus.set_focus(columns[0])
            box.focus_position = "header"

            search_box.set_edit_text("")
            for item in columns:
                item.search_text = ""
                item.update()

            set_passwords()

        def open_password(*_):
            try:
                best = compute_best_password_match()[0]
            except IndexError:
                return

            edit_text = AttrMap(Text("  Edit  ", align="center"), "reversed")
            input_text = AttrMap(Text("  Input  ", align="center"), None)
            history_text = AttrMap(Text("  History  ", align="center"), None)

            pad = partial(Padding, align="center", width="pack")
            col_list = [edit_text, history_text, input_text]
            col = Columns([pad(item) for item in col_list])
            col.focus_position = 0
            header = Padding(Pile([
                LineBox(Text(best.title, align="center")),
                col,
                Text("")]
            ), align="center", width=("relative", 90))
            footer = Padding(Pile([Text(("hint", "(Press Enter to confirm the change)\n(Press Ctrl+X to undo)\n(Press Ctrl+S to save and exit)\n\n"))]), align="center", width=("relative", 90))

            attrs = best.__dict__
            values = [CustomEdit(edit_text=str(item)) for item in attrs.values()]

            def handle_done(*_):
                pos = edit_box.focus_position
                text = values[pos].get_edit_text()
                best.set_attribute(list(attrs.keys())[pos], text)
                set_passwords()

            def _change_focus(add: bool = True):
                # TODO
                col_list[col.focus_position].set_attr_map({None: None})
                col.focus_position = (col.focus_position + 2 * add - 1) % len(col_list)

                col_list[col.focus_position].set_attr_map({None: "reversed"})
                display_box.original_widget = all_boxes[col.focus_position]

            def handle_change_focus(*_):
                _change_focus(True)

            def handle_reverse_change_focus(*_):
                _change_focus(False)

            def handle_undo(*_):
                pos = edit_box.focus_position
                text = list(attrs.values())[pos]
                values[pos].set_edit_text(text)
                values[pos].set_edit_pos(len(text))
                pass

            def handle_save_and_exit(*_):
                for key, value in zip(attrs, values):
                    best.set_attribute(key, value.get_edit_text())
                set_passwords()
                self.top.box_up()

            def handle_move_cursor(key):
                # Wrap around
                if edit_box.focus_position == len(attrs) - 1 and key == "down":
                    pos = 0
                elif edit_box.focus_position == 0 and key == "up":
                    pos = len(attrs) - 1

                elif key == "up":
                    pos = edit_box.focus_position - 1
                else:
                    pos = edit_box.focus_position + 1

                edit_box.focus_position = pos

            for item in values:
                connect_signal(item, "done", handle_done)
                connect_signal(item, "change_focus", handle_change_focus)
                connect_signal(item, "reverse_change_focus", handle_reverse_change_focus)

                connect_signal(item, "undo", handle_undo)
                connect_signal(item, "save_and_exit", handle_save_and_exit)
                connect_signal(item, "move_cursor", handle_move_cursor)

            edit_box = ListBox(SimpleFocusListWalker(
                [Columns([Text(attr.capitalize()), item]) for attr, item in zip(attrs, values)]
            ))

            history_box = ListBox(SimpleFocusListWalker(
                [Columns([Text(attr), item]) for attr, item in zip(attrs, values)]
            ))

            input_box = ListBox(SimpleFocusListWalker(
                [Columns([Text(attr.upper()), item]) for attr, item in zip(attrs, values)]
            ))

            all_boxes = [edit_box, history_box, input_box]

            display_box = Padding(edit_box, align="center", width=("relative", 85))

            password_box = PasswordBox(best)


            self.top.open_non_linebox(password_box)

            print()

        #

        search_box = CustomEdit("")
        connect_signal(search_box, "postchange", handle_text)

        header = Pile([Text("Search (Case ignored):"), LineBox(search_box), Text("Results:")])

        # Make the columns
        columns = [PossibleColumnTitle(), PossibleColumnEmail(), PossibleColumnUsername()]
        column_focus.set_focus(columns[0])
        # search_box.register_columns(set(columns))

        content = [[CustomText("", wrap="ellipsis") for i in range(len(columns))] for _ in range(config["show_password_num_initial"])]

        # Connect signals
        for row in [[search_box]] + content:
            for item in row:
                connect_signal(item, "done", open_password)
                connect_signal(item, "meta_done", open_password)
                connect_signal(item, "change_focus", switch_focus)
                connect_signal(item, "change_column", handle_change_column)
                connect_signal(item, "delete_all", reset)
                item.register_columns(set(columns))

        table_header = Pile([Columns([Text(item.to_title(), align="center") for item in columns]), Divider("╌")])
        table = ListBox(SimpleFocusListWalker([]))
        set_passwords()

        inner = LineBox(Pile([("pack", table_header), table]))

        searching_for = Pile([Text("Selecting by:"), GridFlow([item.render_status() for item in columns], 30, 0, 0, LEFT)])

        footer = Pile([searching_for, Text("XXX", align="center")])

        # Final box
        box = Frame(inner, header, footer)
        box.focus_position = "header"

        self.top.open_non_linebox(box, height=("relative", 100), width=("relative", 100))

    def todo(self, button):
        response = Text(["TODO: ", button.label, "\n"])
        done = menu_button("Ok", self.top.reset_focus)
        self.top.open_non_linebox(Filler(Pile([response, done])))

    def unlock_database(self, *_):
        # First check for problems
        #   → Database does not exist

        if self.handle_database_not_exist():
            return

        # Password prompt
        text = f"\n\nPlease enter your password!"
        second_text = 7 * " " + f"(Press enter to confirm the input)\n\n" + 7 * " " + "(Press Ctrl+W to delete the entire string)\n\n"
        password_box = CustomEdit("  >>>  ", mask="*")

        error_text = Text("\n\n\n", align="center")
        error_attr = AttrMap(error_text, None)

        def check_keypress(*_):
            self.status.password = password_box.get_edit_text()
            # Now unlock the database
            if pw := unlock_with_password(self.status.password):
                self.stored_passwords = pw
                self.status.unlocked = True
                self.top.box_up()
                self.draw_menu()
            else:
                error_text.set_text("That did not work!\n\n\n")
                error_attr.set_attr_map({None: "error"})
                pass

        connect_signal(password_box, "done", check_keypress)

        box = Frame(Filler(password_box), Text(("input", text), align="center"), Pile([error_attr, Text(("hint", second_text))]))

        self.top.open_non_linebox(box)

    def handle_database_not_exist(self):
        if self.status.encrypted_file == FileStatus.found:
            return

        error_text = f"This may happen as a result of deleting / renaming the database, located at {path(config['encrypted_file_name'])!r}.\n"
        good_text = f"If you are using this program for the first time, this message is totally normal.\n"
        help_text = f"Do you want to create a new database?"

        messages = [Text(("error", "\n! WARNING !\nNo database found\n\n"), align="center"), Text(("error", error_text)),
                    Text(("good", good_text)), Text(help_text)]

        yes = Button("Yes")
        no = Button("No")

        connect_signal(yes, "click", self.create_new_database)
        connect_signal(no, "click", self.top.box_up)

        yes_display = AttrMap(yes, None, focus_map="reversed")
        no_display = AttrMap(no, None, focus_map="reversed")

        box = Frame(Filler(GridFlow([yes_display, no_display], 7, 15, 1, "center")), Pile(SimpleFocusListWalker(messages)))

        self.top.open_non_linebox(box)

        return True

    # def handle_clean_file(self):
    #     if self.status.clean_file != FileStatus.found:
    #         return False
    #
    #     self.load_passwords_from_str(config.clean_file_contents())
    #     self.draw_menu()
    #     return True

    def load_passwords_from_str(self, st: str):
        self.stored_passwords = Password.list_from_string(st)
        self.status.unlocked = True

    def quit(self, *args, **kwargs):
        raise ExitMainLoop()


def mainloop():
    term_size = shutil.get_terminal_size((-1, -1))
    if not check_terminal:
        pass
    elif term_size == (-1, -1):
        print("Your Terminal did not get detected… What is wrong?")
        return
    elif term_size.lines < num_min_lines or term_size.columns < num_min_cols:
        print(f"You Terminal is set to an unreasonable size: Please provide at least ({num_min_lines} Lines × {num_min_cols} Cols)")
        return

    palette = [
        ("reversed", "standout", ""),
        ("error", "dark red", ""),
        ("good", "dark green", ""),
        ("input", "dark blue", ""),
        ("hint", "yellow", ""),
    ]

    pwmgr = MyMainLoop()

    MainLoop(pwmgr.top, palette=palette).run()
    print(history.dump())
    print("Bye bye!")
