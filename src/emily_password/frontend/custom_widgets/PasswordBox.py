
from urwid import WidgetWrap, AttrMap, Text


class PasswordBox(WidgetWrap):
    edit_text = AttrMap(Text("  Edit  ", align="center"), "reversed")
    input_text = AttrMap(Text("  Input  ", align="center"), None)
    history_text = AttrMap(Text("  History  ", align="center"), None)

    def __init__(self, password: Password):
        self.password = password

        self.edit_contents = [Columns([Text(key.capitalize()), CustomEdit(edit_text=str(value))]) for key, value in password.display().items()]

        self.history_contents = [Text("Todo")]
        self.input_contents = [Text("Todo")]

        self.edit_box = ListBox(SimpleFocusListWalker(self.edit_contents))
        self.history_box = ListBox(SimpleFocusListWalker(self.history_contents))
        self.input_box = ListBox(SimpleFocusListWalker(self.input_contents))

        self.all_boxes = [self.edit_box, self.history_box, self.input_box]

        self.box = self.edit_box

        # Header

        self.column_list = [self.edit_text, self.history_text, self.input_text]
        self.columns = Columns([Padding(item, align="center", width="pack") for item in self.column_list])
        self.columns.focus_position = 0

        header = Padding(Pile([
            LineBox(Text(password.title, align="center")),
            self.columns,
            Text("")]
        ), align="center", width=("relative", 90))

        # Footer

        footer = Padding(Pile([Text(("hint", "(Press Enter to confirm the change)\n(Press Ctrl+X to undo)\n(Press Ctrl+S to save and exit)\n\n"))]), align="center", width=("relative", 90))

        # Rest

        display_box = Padding(self.box, align="center", width=("relative", 85))




        super().__init__(Frame(display_box, header, footer))

    def keypress(self, size, key):
        match key.split(" "):
            case *_, "enter":
                self.handle_save_and_exit()
                self.handle_done()

            case *maybe_rev, "tab":
                self.handle_change_focus(bool(maybe_rev))

            case "ctrl", "x":
                self.handle_undo()

            case "ctrl", "s":
                self.handle_save_and_exit()

            case ("up",) | ("down",):
                self.handle_move_cursor(key)

            case _:
                super().keypress(size, key)

    @property
    def focus(self):
        return self.columns.focus_position

    @focus.setter
    def focus(self, value):
        self.columns.focus_position = value

    @property
    def edit_key(self):
        return self.edit_box.focus[0].text

    @property
    def _edit_key(self):
        return self.edit_box.focus[0]

    @property
    def edit_value(self):
        return self.edit_box.focus[1].get_edit_text()

    @property
    def _edit_value(self):
        return self.edit_box.focus[1]

    def _exit(self):
        # TODO: set_passwords()
        ...

    def refresh_boxes(self):
        self._w.body.original_widget = self.all_boxes[self.focus]

    def handle_change_focus(self, reverse: bool = False):
        self.column_list[self.focus].set_attr_map({None: None})
        self.focus = (self.focus - 2 * reverse + 1) % len(self.column_list)
        self.column_list[self.focus].set_attr_map({None: "reversed"})

        self.refresh_boxes()

    def handle_done(self):
        self.password.set_attribute(self.edit_key, self.edit_value)
        self._exit()

    def handle_undo(self):
        text = self.password.get_attribute(self.edit_key)
        self._edit_value.set_edit_text(text)
        self._edit_value.set_edit_pos(len(text))

    def handle_save_and_exit(self):
        for column in self.edit_box.body:
            key, value = column.widget_list
            self.password.set_attribute(key.text, value.get_edit_text())

        self._exit()

    def handle_move_cursor(self, key: str):
        max_len = len(self.password.display())
        if self.edit_box.focus_position == max_len - 1 and key == "down":
            pos = 0
        elif self.edit_box.focus_position == 0 and key == "up":
            pos = max_len - 1

        elif key == "up":
            pos = self.edit_box.focus_position - 1
        else:
            pos = self.edit_box.focus_position + 1

        self.edit_box.focus_position = pos

