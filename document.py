import lpod.document

class Document(object):
    def __init__(self, filename):
        self.obj = lpod.document.odf_get_document(filename)
        self.filename = filename
    def write(self, filename):
        self.obj.save(filename)
    def lines(self):
        return self.obj.get_body().get_text(True)