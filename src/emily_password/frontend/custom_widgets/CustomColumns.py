from abc import ABC, abstractmethod

from urwid import AttrMap, Text, Columns


class ColumnFocus:
    focus = None

    def set_focus(self, obj):
        self.focus = obj

    def set_text(self, text):
        self.focus.search_text = text
        return self

    def update(self):
        self.focus.update()
        return self


column_focus = ColumnFocus()


class PossibleColumn(ABC):
    name: str
    switch_key: str
    indicator: AttrMap
    search_text = ""
    display_text: Text
    select_pw_attr: callable

    def __init__(self):
        self.display_text.set_text(str(self))

    def to_title(self):
        return self.name

    def update(self):
        if column_focus.focus is self:
            self.indicator.set_attr_map({None: "good"})
        else:
            self.indicator.set_attr_map({None: None})
        self.display_text.set_text(str(self))

    def render_status(self):
        self.update()
        return Columns([(3, self.indicator), self.display_text], )

    def accept_keypress(self, key):
        if key == self.switch_key:
            column_focus.set_focus(self)

    def __str__(self):
        return f"{self.name}: {self.switch_key.replace('meta', 'alt')}" + f" ({self.search_text})" * bool(self.search_text)

    @abstractmethod
    def select_pw_attr(self, pw):
        ...


class PossibleColumnTitle(PossibleColumn):
    name = "Title"
    switch_key = "meta q"
    indicator = AttrMap(Text("◯", align="center"), None)
    display_text = Text("")

    def select_pw_attr(self, pw):
        return pw.title


class PossibleColumnEmail(PossibleColumn):
    name = "Email"
    switch_key = "meta w"
    indicator = AttrMap(Text("◯", align="center"), None)
    display_text = Text("")

    def select_pw_attr(self, pw):
        return pw.email


class PossibleColumnUsername(PossibleColumn):
    name = "Username"
    switch_key = "meta e"
    indicator = AttrMap(Text("◯", align="center"), None)
    display_text = Text("")

    def select_pw_attr(self, pw):
        return pw.username
