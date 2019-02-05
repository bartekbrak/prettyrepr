import functools
import os
from pygments import highlight
from pygments.formatters.terminal256 import Terminal256Formatter
from pygments.lexers import get_lexer_by_name
from django.db.models.fields.reverse_related import ManyToOneRel

python_lexer = get_lexer_by_name("python", stripall=True)
style = os.getenv('PRETTYREPR_STYLE', 'monokai')
sentinel = object()
django_repr = None

_debug = 1

CHAR = ' '
DEPTH = 2
TAB = 4


def debug(*args, **kwargs):
    if _debug:
        print('DEBUG', args, kwargs)


def rgetattr(obj, attr, default=sentinel):
    # https://stackoverflow.com/a/31174427/1472229
    if default is sentinel:
        _getattr = getattr
    else:
        def _getattr(inner_obj, name):
            return getattr(inner_obj, name, default)
    return functools.reduce(_getattr, [obj]+attr.split('.'))


def resolve_attrs(obj, fields, done, level=0):
    for field in fields:
        if field == 'parent':
            yield f'{field}=BAD_FIELD'
            continue
        if done is None:
            done = set()
            debug(field)
        resolved = rgetattr(obj, field)
        from django.db.models import ManyToManyField
        if resolved.__class__.__name__ == 'ManyRelatedManager':
            yield f'{field}=M2M({resolved.count()})'
            continue
        if resolved.__class__.__name__ == 'RelatedManager':
            # yield f'{field}=dupsko'
            yield f'{field}=O2M({resolved.count()})'
            continue
        # if subfield has our coloured repr, don't do it, or you'll get gibberish like '...8;5;197m>[39m[...'
        from django.db import models
        is_relation = getattr(resolved, 'id', None)
        if is_relation and level == DEPTH:
            yield f'{field}=TOO_DEEP'
            continue
        # is_relation = isinstance(resolved, models.Model) and resolved.is_relation
        is_done = (field.__class__, is_relation) in done
        if is_relation and not is_done:
            done.add((field.__class__, resolved.id))
            # RECURSION HERE
            yield '%s=%s' % (field, resolved.__repr__.nocolor(resolved, done=done, level=level+1))
        else:
            if is_relation and is_done:
                yield '%s=%s (hidden to avoid doom cycle)' % (field, resolved.id)
            else:
                # RECURSION HERE?
                yield '%s=%s' % (field, repr(resolved))


def the_repr(obj, fields, format_='%s(%s)', indenter=' ', done=None, level=0):
    # topmost_call = done is None
    # if topmost_call:
    #     done = set()
    # done.add(obj.id)
    # a repr that tells you as much as possible, in accordance with
    # https://docs.python.org/2/library/functions.html#repr
    cls = '%s' % obj.__class__.__name__
    joiner = ',%s' % indenter
    return format_ % (cls, joiner.join(resolve_attrs(obj, fields, done, level=level)))


def highlight_python(str_):
    return highlight(str_, python_lexer, Terminal256Formatter(style=style))


def django_repr(obj, done=None, level=0, **kwargs):
    fields = [field.name for field in obj._meta.concrete_fields]
    related = [_.get_accessor_name() for _ in obj._meta.related_objects]
    m2m = [_.name for _ in obj._meta.many_to_many]
    fields = fields + related + m2m
    return the_repr(obj=obj, fields=fields, done=done, level=level, **kwargs)



def django_repr_color(obj, done=None, level=0, **kwargs):
    return highlight_python(django_repr(obj=obj, done=None, level=level, **kwargs))


def django_repr_indent(obj, done=None, level=0):
    # what adds the \n that rstrip removes? Check get_lexer_by_name(ensurenl
    move = CHAR * (level+1) * TAB
    return django_repr(obj, format_=f'%s(\n{move}%s\n{CHAR * level * TAB})', indenter=f'\n{move}', done=done, level=level).rstrip()


def django_repr_color_indent(obj, done=None, level=0):
    move = CHAR * (level + 1) * TAB
    return django_repr_color(obj, format_=f'%s(\n{move}%s\n{CHAR * level * TAB})', indenter=f'\n{move}', done=done, level=level).rstrip()


# def openpyxl_cell(obj):
#     # http://openpyxl.readthedocs.io/en/stable/api/openpyxl.cell.cell.html#openpyxl.cell.cell.Cell
#     fields = ('row', 'col_idx', '_value', 'data_type', 'number_format')
#     return the_repr(obj, fields, format_='%s(\n\t%s\n)', indenter='\n\t')
#
#
# def informal_repr(obj, fields=None):
#     return the_repr(obj, fields=fields, format_='<%s %s>')
#
#
# def mongo_repr(obj, **kwargs):
#     return the_repr(obj, obj._fields_ordered, **kwargs)
#
#
# def mongo_repr_color(obj, **kwargs):
#     return highlight_python(mongo_repr(obj, **kwargs))
#
#
# def mongo_repr_color_indent(obj):
#     return mongo_repr_color(obj, format_='%s(\n\t%s\n)', indenter='\n\t')
#
#
# def mongo_repr_color_double_indent(obj):
#     return mongo_repr(obj, format_='%s(\n\t\t%s\n\t)', indenter='\n\t\t')

django_repr_color.nocolor = django_repr
django_repr_color_indent.nocolor = django_repr_indent
# mongo_repr_color.nocolor = mongo_repr
# mongo_repr_color_indent.nocolor = mongo_repr
# mongo_repr_color_double_indent.nocolor = mongo_repr




def monkey(variant=django_repr_color_indent):
    from django.db import models
    if not hasattr(models.Model, '__old_repr__'):
        models.Model.__old_repr__ = models.Model.__repr__
    models.Model.__repr__ = variant
