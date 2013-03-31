import urwid
from urwid.util import move_prev_char, move_next_char

class Editor(urwid.Edit):
    def __init__(self, master, *args, **kwargs):
        super(Editor, self).__init__(multiline=True, *args, **kwargs)
        self.mode = 'n'
        self.master = master
        self.status_labels = {'i': u' -- INSERT --                            {col},{row}', 'n': u'{filename:40} {col},{row}'}
    def set_mode(self, mode, size=None):
        self.mode = mode
        if size is not None:
            self.draw_statusbar(size)
    def draw_statusbar(self, size):
        x, y = self.get_cursor_coords(size)
        self.master.set_status(self.status_labels[self.mode].format(col=x+1, row=y+1, filename=self.master.document.filename))
    def render(self, size, focus=False):
        self.draw_statusbar(size)
        return super(Editor, self).render(size, focus)
    def keypress(self, size, key):
        if self.mode == 'n':
            p = self.edit_pos
            if key == 'i':
                self.set_mode('i', size)
            elif key == 'h':
                if p == 0:
                    return
                p = move_prev_char(self.edit_text, 0, p)
                self.set_edit_pos(p)
            elif key == 'j':
                x, y = self.get_cursor_coords(size)
                pref_col = self.get_pref_col(size)
                assert pref_col is not None
                if not self.move_cursor_to_coords(size, pref_col, y + 1):
                    return
            elif key == 'k':
                x, y = self.get_cursor_coords(size)
                pref_col = self.get_pref_col(size)
                assert pref_col is not None
                if not self.move_cursor_to_coords(size, pref_col, y - 1):
                    return
            elif key == 'l':
                if p >= len(self.edit_text):
                    return
                p = move_next_char(self.edit_text, p, len(self.edit_text))
                self.set_edit_pos(p)
            elif key == ':':
                self.command_start(':')
            elif key == '/':
                self.command_start('/')
        elif self.mode == 'i':
            if key == 'esc':
                self.set_mode('n', size)
            else:
                super(Editor, self).keypress(size, key)
    def command_start(self, char):
        self.master.contents['footer'] = (CommandEdit(self, char), self.master.contents['footer'][1])
        self.master.focus_position = 'footer'
    def command_done(self, edit):
        self.master.focus_position = 'body'
        self.master.contents['footer'] = (self.master.statusbar, self.master.contents['footer'][1])
        if not edit.edit_text:
            return
        cmd = edit.edit_text[len(edit.initchar):]
        if cmd in ('x', 'q'):
            raise urwid.ExitMainLoop()

class CommandEdit(urwid.Edit):
    def __init__(self, master, initchar, *args, **kwargs):
        super(CommandEdit, self).__init__(*args, **kwargs)
        self.master = master
        self.initchar = initchar
        self.set_edit_text(self.initchar)
        self.set_edit_pos(len(self.initchar))
    def keypress(self, size, key):
        if key == 'enter':
            self.master.command_done(self)
        elif self._command_map[key] == urwid.CURSOR_LEFT and self.edit_pos <= len(self.initchar):
            pass
        elif (key == 'backspace' and self.edit_pos <= len(self.initchar)) or key == 'esc':
            self.set_edit_text(u'')
            self.master.command_done(self)
        else:
            super(CommandEdit, self).keypress(size, key)
