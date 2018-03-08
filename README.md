# Prettyrepr

A collection of `__repr__` functions utilizing colours and indentation so your debug sessions give you less headeache.

This is not exactly production code, don't expect stability or completeness,
however this library will make your life easier.


# Install

```
# Straight from the oven, freshest
pip install --upgrade git+git://github.com/bartekbrak/prettyrepr.git
# Easier, stabler but not always fresher.
pip install prettyrepr
```


# Use
### django

```
$ grep -A 3 'import pretty_repr' developer_django_settings.py
import prettyrepr
from django.db import models
models.Model.__repr__ = prettyrepr.django_repr
```

# todo
- tests, tox
- more use cases

Changelog
- 2018.03.08.02:
    -  support recursive dotted attr notation like `'user.email'`
- 2018.03.08:
    - rename to prettyrepr, no dashes, no underscores
    - clean
    - django repr uses `_meta.concrete_fields`
    - use ``.format`
    - remove dicr reprs, use pprint/pformat
    - add openpyxl_cell
- 3:
    - working code, deprecated
