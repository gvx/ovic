import lpod.document

class Document(object):
    def __init__(self, filename):
        self.obj = lpod.document.odf_get_document(filename)
        self.filename = filename
    def write(self, filename):
        self.obj.save(filename)
    def lines(self):
        l = ''
        for i in self.obj.get_body().get_children():
            if i.get_tag() == 'text:sequence-decls':
                continue
            if i.get_tag() == 'text:h':
                l += '#' * int(i.get_attributes()['text:outline-level']) + ' '
            l += i.get_text() or ''
            for j in i.get_children():
                if j.get_tag() == 'text:line-break':
                    l += '\n'
                l += j.get_text() or ''
                l += j.get_tail() or ''
            l += '\n\n'
        return l[:-2]
