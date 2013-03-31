import curses
import urwid
from document import Document
from editor import Editor

class Window(urwid.Frame):
    def __init__(self, filename):
        self.filename = filename
        self.document = Document(self.filename)
        self.edit = Editor(self)
        self.edit.set_edit_text(self.document.lines())
        fill = urwid.Filler(self.edit, valign='top')
        self.statusbar = urwid.Text(u'')
        super(Window, self).__init__(fill, footer=self.statusbar)
    def set_status(self, text):
        self.statusbar.set_text(text)
    def run(self):
        loop = urwid.MainLoop(self)
        loop.run()
