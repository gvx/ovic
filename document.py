import lpod.document

class Cursor(object):
    def __init__(self, document, par, offset):
        self.document = document
        self.set_par_(par)
        self.set_offset(offset)
    def set_par_(self, par):
        if par is not None:
            maxpar = len(self.document.obj.get_body().get_children()) - 1
            if par < 0:
                par = 0
            elif par > maxpar:
                par = maxpar
        self.par = par
    def set_par(self, par):
        self.set_par_(par)
        self.set_offset(self.offset)
    def set_offset(self, offset):
        if self.par is not None and offset is not None:
            elem = self.document.obj.get_body().get_children()[self.par]
            maxoffset = len(elem.get_text(True))
            if offset < 0:
                offset = 0
            elif offset > maxoffset:
                offset = maxoffset
        self.offset = offset


class Document(object):
    def __init__(self, filename):
        self.obj = lpod.document.odf_get_document(filename)
        self.filename = filename
        self.caret = Cursor(self, 0, 0)
        self.sel_end = Cursor(self, None, None)
        self.camera = Cursor(self, 0, 0)
    def write(self, filename):
        self.obj.save(filename)
    def move_selection(self, delta_par, delta_offset):
        sel = self.sel_end
        if sel.par is None:
            sel.par = self.caret.par
        if sel.offset is None:
            sel.offset = self.caret.offset
        sel.set_par_(sel.par + delta_par)
        sel.set_offset(sel.offset + delta_offset)
    def set_selection(self, new_par, new_offset):
        sel = self.sel_end
        sel.set_par_(new_par)
        sel.set_offset(new_offset)
    def move_caret(self):
        self.caret = self.sel_end
        self.sel_end = Cursor(self, None, None)
    def _pars(self):
        return self.obj.get_body().get_children()
    def update_screen(self, size):
        pass
    def from_offset(self, size, par, offset):
        _pars[par]
    def lines(self):
        l = []
        for i in self._pars():
            if i.get_tag() == 'text:sequence-decls':
                continue
            if i.get_tag() == 'text:h':
                l.append(('heading', '#' * int(i.get_attributes()['text:outline-level']) + ' ' + (i.get_text() or '')))
            else:
                l.append(i.get_text() or '')
            for j in i.get_children():
                if j.get_tag() == 'text:line-break':
                    l.append(('soft break', ' \n'))
                else:
                    l.append(('span', j.get_text() or ''))
                l.append(j.get_tail() or '')
            l.append('\n\n')
        return l[:-1]
