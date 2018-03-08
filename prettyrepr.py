import functools
import os
from pygments import highlight
from pygments.formatters.terminal256 import Terminal256Formatter
from pygments.lexers import get_lexer_by_name

python_lexer = get_lexer_by_name("python", stripall=True)

style = os.getenv('PRETTYREPR_STYLE', 'monokai')


# https://stackoverflow.com/a/31174427/1472229

sentinel = object()
def rgetattr(obj, attr, default=sentinel):
    if default is sentinel:
        _getattr = getattr
    else:
        def _getattr(obj, name):
            return getattr(obj, name, default)
    return functools.reduce(_getattr, [obj]+attr.split('.'))


def the_repr(obj, fields, format_='%s(%s)', indenter=' '):
    # a repr that tells you as much as possible, in accordance with
    # https://docs.python.org/2/library/functions.html#repr
    attributes = [
        '%s=%r' % (field, rgetattr(obj, field))
        for field in fields
    ]
    cls = '%s' % obj.__class__.__name__
    joiner = ',%s' % indenter
    return format_ % (cls, joiner.join(attributes))


def highlight_python(str_):
    return highlight(str_, python_lexer, Terminal256Formatter(style=style))


def django_repr(obj, **kwargs):
    fields = [field.name for field in obj._meta.concrete_fields]
    return the_repr(obj, fields, **kwargs)


def django_repr_color(obj, **kwargs):
    return highlight_python(django_repr(obj, **kwargs))


def django_repr_indent(obj):
    # what adds the \n that rstrip removes? Check get_lexer_by_name(ensurenl
    return django_repr(obj, format_='%s(\n\t%s\n)', indenter='\n\t').rstrip()


def openpyxl_cell(obj):
    # http://openpyxl.readthedocs.io/en/stable/api/openpyxl.cell.cell.html#openpyxl.cell.cell.Cell
    fields = ('row', 'col_idx', '_value', 'data_type', 'number_format')
    return the_repr(obj, fields, format_='%s(\n\t%s\n)', indenter='\n\t')


def informal_repr(obj, fields=None):
    return the_repr(obj, fields=fields, format_='<%s %s>')


def mongo_repr(obj, **kwargs):
    return the_repr(obj, obj._fields_ordered, **kwargs)


def mongo_repr_color(obj, **kwargs):
    return highlight_python(mongo_repr(obj, **kwargs))


def mongo_repr_color_indent(obj):
    return mongo_repr_color(obj, format_='%s(\n\t%s\n)', indenter='\n\t')


def mongo_repr_color_double_indent(obj):
    return mongo_repr(obj, format_='%s(\n\t\t%s\n\t)', indenter='\n\t\t')
