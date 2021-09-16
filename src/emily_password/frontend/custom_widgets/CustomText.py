from urwid import emit_signal, Edit

from lucy_password.custom_widgets.CustomSignals import CustomSignals


class ChangeColumn:
    columns = []
    columns_keypress = set()

    def handle_column(self, key):
        if key.casefold() in self.columns_keypress:
            emit_signal(self, "change_column", next(item for item in self.columns if item.switch_key.casefold() == key.casefold()))
        else:
            return False
        return True

    def register_columns(self, content: set):
        self.columns = content
        self.columns_keypress = [item.switch_key.casefold() for item in content]


class CustomEdit(Edit, CustomSignals, ChangeColumn):
    def keypress(self, size, key):
        if self.handle_signal(self, key):
            pass
        elif self.handle_column(key):
            pass
        elif key == "ctrl w":
            self.set_edit_text("")
        else:
            super().keypress(size, key)


class CustomText(Text, CustomSignals, ChangeColumn):
    _selectable = True

    def keypress(self, size, key):
        if self.handle_signal(self, key):
            pass
        elif self.handle_column(key):
            pass

        return key

