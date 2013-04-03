import urwid
from urwid.util import move_prev_char, move_next_char

class Editor(urwid.Edit):
    def __init__(self, master, *args, **kwargs):
        super(Editor, self).__init__(multiline=True, *args, **kwargs)
        self.mode = 'n'
        self.master = master
        self.edit_attr = []
        self.count = ''
        self.status_labels = {'i': u' -- INSERT --                            {col},{row}', 'n': u'{filename:40} {col},{row}  {count}', ':':'', '/':''}
        self.commands = {
            'n': {},
            'v': {},
            ':': {},
            '/': {},
        }
        self.reset_command_path()
        __builtins__['register'] = self.register_command
        import commands
    def register_command(self, activation, immediate=False):
        def register_func(f):
            modes, command_or_motion = f.__name__.split('_')
            f.command_or_motion = command_or_motion
            f.immediate = immediate
            if modes == 'ex':
                modes = ':'
                activate = [activation] #since ex commands are linebuffered, we want a simple mapping, not some strange path
            else:
                activate = activation #hack to fake nonlocals
            for mode in modes:
                tmp = self.commands[mode]
                for nex in activate[:-1]:
                    if nex not in tmp:
                        tmp[nex] = {}
                    elif callable(tmp[nex]):
                        raise Exception("command is the prefix of another (" + str(activation) + ")")
                    tmp = tmp[nex]
                if activate[-1] in tmp:
                    raise Exception("command is the prefix of another (" + str(activation) + ")")
                tmp[activate[-1]] = f
        return register_func
    def reset_command_path(self):
        self.path = self.commands[self.mode]
        self.count = ''
        self.future_command = None
    def set_mode(self, mode, size=None):
        self.mode = mode
        self.reset_command_path()
        if size is not None:
            self.draw_statusbar(size)
    def draw_statusbar(self, size):
        x, y = self.get_cursor_coords(size)
        self.master.set_status(self.status_labels[self.mode].format(col=x+1, row=y+1, filename=self.master.document.filename, count=self.count))
    def render(self, size, focus=False):
        self.draw_statusbar(size)
        return super(Editor, self).render(size, focus)
    def keypress(self, size, key):
        if self.mode == 'n':
            p = self.edit_pos
            if key.isdigit():
                self.count += key
                self.draw_statusbar(size)
            elif key == 'i':
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
            else:
                if key in self.path:
                    self.path = self.path[key]
                    if callable(self.path):
                        if self.path.command_or_motion == 'motion':
                            self.path(document=self.master.document, editor=self, count=int(self.count or '1', 10), size=size)
                            if self.future_command:
                                self.future_command(document=self.master.document, editor=self, count=int(self.count or '1', 10), size=size)
                            else:
                                self.master.document.move_caret()
                                self.move_cursor_to_coords(size, self.master.document.caret.offset, self.master.document.caret.par)
                            self.reset_command_path()
                        elif self.path.immediate:
                            self.path(document=self.master.document, editor=self, count=int(self.count or '1', 10), size=size)
                            self.reset_command_path()
                        else:
                            self.future_command = self.path
                else:
                    self.reset_command_path()
        elif self.mode == 'i':
            if key == 'esc':
                self.set_mode('n', size)
            elif key == 'meta enter':
                self.insert_text('\n')
            elif key == 'enter':
                self.insert_text('\n\n')
            else:
                super(Editor, self).keypress(size, key)
    def command_start(self, char):
        self.set_mode(char)
        self.master.contents['footer'] = (CommandEdit(self, char), self.master.contents['footer'][1])
        self.master.focus_position = 'footer'
    def command_done(self, edit):
        self.master.focus_position = 'body'
        self.master.contents['footer'] = (self.master.statusbar, self.master.contents['footer'][1])
        if not edit.edit_text:
            return
        cmd = edit.edit_text[len(edit.initchar):]
        if cmd in self.path:
            self.path[cmd](document=self.master.document, editor=self, count=int(self.count or '1', 10), size=None)
        elif cmd in ('x', 'q'):
            raise urwid.ExitMainLoop()
        self.set_mode('n')
    def get_text(self):
        return self.edit_text, self.edit_attr
    def set_edit_markup(self, markup):
        self.edit_text, self.edit_attr = urwid.decompose_tagmarkup(markup)

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
