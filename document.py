import lpod.document

class Document(object):
    def __init__(self, filename):
        self.obj = lpod.document.odf_get_document(filename)
        self.filename = filename
    def write(self, filename):
        self.obj.save(filename)
    def lines(self):
        l = []
        for i in self.obj.get_body().get_children():
            if i.get_tag() == 'text:sequence-decls':
                continue
            if i.get_tag() == 'text:h':
                l.append(('bold', '#' * int(i.get_attributes()['text:outline-level']) + ' ' + (i.get_text() or '')))
            else:
                l.append(('blue', i.get_text() or ''))
            for j in i.get_children():
                if j.get_tag() == 'text:line-break':
                    l.append('\n')
                l.append(j.get_text() or '')
                l.append(j.get_tail() or '')
            l.append('\n\n')
        return l[:-1]
