from pygments import highlight
from pygments.formatters.terminal256 import Terminal256Formatter
from pygments.lexers import get_lexer_by_name

python_lexer = get_lexer_by_name("python", stripall=True)


def the_repr(obj, fields, format_='%s(%s)', indenter=' '):
    # a repr that tells you as much as possible, in accordance with
    # https://docs.python.org/2/library/functions.html#repr
    attributes = [
        '%s=%r' % (field, getattr(obj, field))
        for field in fields
    ]
    cls = '%s' % obj.__class__.__name__
    joiner = ',%s' % indenter
    return format_ % (cls, joiner.join(attributes))


def mongo_repr(obj, **kwargs):
    return the_repr(obj, obj._fields_ordered, **kwargs)


def django_repr(obj):
    fields = [_ for _ in obj.__dict__.keys() if _ != '_state']
    return highlight_python(the_repr(obj, fields))


def informal_repr(obj, fields=None):
    return the_repr(obj, fields=fields, format_='<%s %s>')


def coloured_mongo_repr(obj, **kwargs):
    return highlight_python(mongo_repr(obj, **kwargs))


def indented_coloured_mongo_repr(obj):
    return coloured_mongo_repr(obj, format_='%s(\n\t%s\n)', indenter='\n\t')


def double_indented_mongo_repr(obj):
    return mongo_repr(obj, format_='%s(\n\t\t%s\n\t)', indenter='\n\t\t')


def dict_repr(dict_, fields, format_, indenter):
    joiner = ',%s' % indenter
    return format_ % joiner.join(fields)


def double_indented_dict(dict_):
    fields = ['%r: %r' % (x, y) for x, y in dict_.items()]
    format_ = '{\n\t\t%s\n\t}'
    indenter = '\n\t\t'
    return dict_repr(dict_, fields, format_, indenter)


def highlight_python(str_):
    return highlight(str_, python_lexer, Terminal256Formatter(style='monokai'))
