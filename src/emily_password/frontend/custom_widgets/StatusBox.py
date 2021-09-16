# This is deprecated
from urwid import Columns, LineBox, Overlay


class StatusBox(Columns):
    def __init__(self, bottom, box):
        body = []
        super().__init__([LineBox(box), LineBox(box)], )
        self.original_widget = Overlay(self,
                                       bottom,
                                       align="center",
                                       width=("relative", 80),
                                       valign="bottom",
                                       height=("relative", 20)
                                       )
