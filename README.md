Обработчик данных gismeteo на Python
====================================

О пакете
--------

Загружает данные с сервиса gismeteo.ru и обрабатывает их.

Установка
---------

```bash
$ pip install gismeteo
```

Использование
-------------

Со встроенным кешированием.

По известному ID населенного пункта в сервисе:
```python
gmp = GisMeteoParser(town_id=28367)
```
или по известному URL населенного пункта в сервисе:
```python
gmp = GisMeteoParser(url='http://informer.gismeteo.ru/xml/28367.xml')
```
или из файла XML-данных в файловой системе (собственный кеш)
```python
gmp = GisMeteoParser(filename='cache.xml')
```
или из объекта XML-данных:
```python
gmp = GisMeteoParser(xml=xml_data)
```

Далее:
все сформированные данные, список (хотя обычно один город)
```python
data = gmp.data
```
или только первый город
```python
data = gmp.first_data
```

Далее все это можно использовать в шаблоне для вывода

Есть не очень красивый пример использования в модуле ``custom_parser``

Можно определить собственный класс - наследник ``GisMeteoParser`` и сформировать 
данные нужным вам образом. Для этого можно исследовать класс ``_Forecast``
примерно так: ``_Forecast.__dict__`` и выбрать все необходимые вам данные - 
все они там есть. Если впоследствии кому-то понадобится более удобная форма -
выведу все атрибуты как надо. Меня пока и так устраивает.

Если нет необходимости использовать встроенный механизм кеширования, 
то параметр ``use_builtin_cache`` надо выставить в ``False``. Если же он используется,
то можно задать ``cache_dir_path`` и ``cache_file_name``, иначе файл кеша
будет писаться в ту же директорию, откуда запускается скрипт.

Разрешение на обработку
-----------------------

Лицензия gismeteo.ru: http://www.gismeteo.ru/informers/offer/
