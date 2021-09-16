from urwid import *


class CascadingBoxes(WidgetPlaceholder):
    max_box_levels = 4

    def __init__(self, box=None, main_loop=None):
        super(CascadingBoxes, self).__init__(SolidFill("\\"))
        self.main_loop = main_loop
        self.box_level = 0

        # TODO: Status Box
        # self.status_box = BoxAdapter(Filler(GridFlow([Text("a"), Text("b")], 20, 5, 0, CENTER), BOTTOM), 12)
        # if box is not None and not isinstance(box, LineBox):
        #     box = LineBox(box)
        #
        # box = Frame(box, footer=self.status_box)

        if box:
            self.open_non_linebox(box)

    def open_box(self, box, align="center", width=("relative", 80), valign="middle", height=("relative", 80), min_width=24, min_height=8):
        self.original_widget = Overlay(box,
                                       self.original_widget,
                                       align=align, width=width,
                                       valign=valign, height=height,
                                       min_width=min_width, min_height=min_height,
                                       left=self.box_level * 3,
                                       right=(self.max_box_levels - self.box_level - 1) * 3,
                                       top=self.box_level * 2,
                                       bottom=(self.max_box_levels - self.box_level - 1) * 2)

        self.box_level += 1
        pass

    def open_non_linebox(self, box, **kwargs):
        self.open_box(LineBox(box), **kwargs)

    def keypress(self, size, key):
        if key == "esc" and self.box_level > 1:
            self.box_up()
        else:
            return super(CascadingBoxes, self).keypress(size, key)

    def box_up(self, *_):
        if self.box_level > 1:
            self.original_widget = self.original_widget[0]
            self.box_level -= 1

    def reset_focus(self, *_):
        while self.box_level > 1:
            self.box_up()
        self.main_loop.draw_menu()


def menu_button(caption, callback):
    button = Button(caption)

    connect_signal(button, "click", callback)
    return AttrMap(button, None, focus_map="reversed")


def sub_menu(caption, choices, top):
    contents = menu(caption, choices)

    def open_menu(button):
        return top.open_non_linebox(contents)

    return menu_button([caption, " ..."], open_menu)


def menu(title, choices):
    body = [Text(title), Divider("-")]
    body.extend(choices)
    return ListBox(SimpleFocusListWalker(body))


def subsection(name, is_first: bool = False):
    ret = AttrMap(Text(" " + name), None), Divider("-")

    if is_first:
        return ret
    return Divider("-"), *ret


class ConfigButton(WidgetWrap):
    def __init__(self, config_entry, callback, the_config=None):
        # AttrMap(SelectableIcon(caption), None, focus_map="reversed")
        #
        # connect_signal(self, "click", callback)
        self.config_entry = config_entry
        self.config = the_config or config
        wid = GridFlow(
            (Text(config_name_mapping[self.config_entry]),
             self.get_correct_button(callback)),
            cell_width=50,
            h_sep=0,
            v_sep=2,
            align="center",
        )
        wid.focus_position = 1
        super().__init__(
            wid
        )

    def get_correct_button(self, callback):
        the_text = str(self.config[self.config_entry])
        match self.config_entry:
            case "encrypted_file_name" | "salt_file_name" | \
                 "temp_file_name" | "demo_prefix" | "password_contents":
                return menu_button(the_text, callback)

            case "password_length" | "show_password_num_initial":
                return menu_button(the_text, callback)

            case "exit" | "website" | "username" | "email" | "password":
                return menu_button(the_text, callback)

            case "is_demo":
                return menu_button(the_text, callback)

            case _:
                return


class Subsection(WidgetWrap):
    def __init__(self, name):
        super().__init__(Pile(
            (Divider("─"),
             Text(name, align="center"),
             Divider("╌"))
        ))
