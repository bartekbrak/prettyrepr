# Prettyrepr WIP

A collection of `__repr__` functions utilizing colours and indentation so your debug sessions give you less headeache.

This is not a production code, don't expect stability or completeness, however this library will make your life easier.
# How to install and use

```
pip install --upgrade git+git://github.com/bartekbrak/prettyrepr.git
```

### django

```
$ grep -A 3 'import pretty_repr' developer_django_settings.py
import pretty_repr
from django.db import models
models.Model.__repr__ = pretty_repr.django_repr
```

WIP !
