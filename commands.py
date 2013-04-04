@register('w')
def n_motion(document, editor, count, size):
    pass

@register('l')
def n_motion(document, editor, count, size):
    document.move_selection(0, count)

@register('h')
def n_motion(document, editor, count, size):
    document.move_selection(0, -count)

@register('gg')
def n_motion(document, editor, count, size):
    document.set_selection(count - 1, 0)

@register('G')
def n_motion(document, editor, count, size):
    document.set_selection((count-1) or float('+inf'), 0)

@register('d')
def n_command(document, editor, count, size):
    pass #delete area between document.caret and document.sel_end

@register('x', immediate=True)
def n_command(document, editor, count, size):
    pass #delete count characters

@register('quit')
def ex_command(document, editor, count, size):
    import urwid
    raise urwid.ExitMainLoop()

@register('w')
@register('write')
def ex_command(document, editor, count, size):
    document.write(document.filename)
