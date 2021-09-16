from urwid import signals, emit_signal


class CustomSignals:
    _metaclass_ = signals.MetaSignals
    signals = ["done", "meta_done", "change_focus", "reverse_change_focus", "change_column", "delete_all", "undo",
               "save_and_exit", "move_cursor"]

    @staticmethod
    def handle_signal(obj, key):
        if key == "enter":
            emit_signal(obj, "done")
        elif key == "meta enter":
            emit_signal(obj, "meta_done")
        elif key == "tab":
            emit_signal(obj, "change_focus")
        elif key == "shift tab":
            emit_signal(obj, "reverse_change_focus")
        elif key == "meta ctrl w":
            emit_signal(obj, "delete_all")
        elif key == "ctrl x":
            emit_signal(obj, "undo")
        elif key == "ctrl s":
            emit_signal(obj, "save_and_exit")
        elif key in ["up", "down"]:
            emit_signal(obj, "move_cursor", key)
        else:
            return False
        return True
