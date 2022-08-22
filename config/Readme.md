# Как добавить настройки в Админ панель

* Перейти в папку config и открыть файл ***admin_constance_config.py***
* Добавить ключ в словарь ***CONSTANCE_CONFIG***:
  ```python 
  CONSTANCE_CONFIG['NAME_OF_YOUR_SETTINGS'] = ('default_value', 'help text')
  ```
* Добавить такой же ключ в словарь ***CONSTANCE_CONFIG_FIELDSETS:***
  ```python
  CONSTANCE_CONFIG_FIELDSETS = {
    'General Options': ('SITE_NAME', 'SITE_DESCRIPTION'),
    'Theme Options': ('THEME',),
  }
  ```

# Как получить доступ к настройке из кода

#### Для получения доступа к параметру настрйки, необходимо импортировать объект настройки:

```python
from constance import config

if config.NAME_OF_YOUR_SETTINGS == "Your value":
    "Do something"
```

[Ссылка на документация](https://django-constance.readthedocs.io/en/latest/)

# Настройка кэширования

### Кэш настроен на LocMemCache

```python

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
```

### Для доступа к кэшу из View.py:

```python
from django.core.cache import cache
from constance import config

cache_name = cache.get('name_of_cache')
if not cache_name:
    "Do some"
    cache.set('name_of_cache', config.YOUR_CACHE_TIME)
```

### После этого нужно зайти в файл ***signals.py*** и добавить название вашего кэша в словарь:

```python
from enum import Enum

class CacheTypeKeys(Enum):
    CLEAR_SELLER_CACHE = 'name_of_your_cache'
```

## Если будут вопросы пишите, звоните.