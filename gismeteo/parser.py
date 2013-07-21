# -*- coding: utf-8 -*-
'''
Лицензия gismeteo.ru: http://www.gismeteo.ru/informers/offer/

Использование (со встроенным кешированием):
по известному ID населенного пункта в сервисе:
>>> gmp = GisMeteoParser(town_id=28367)
или по известному URL населенного пункта в сервисе:
>>> gmp = GisMeteoParser(url='http://informer.gismeteo.ru/xml/28367.xml')
или из файла XML-данных в файловой системе (собственный кеш)
>>> gmp = GisMeteoParser(filename='cache.xml')
или из объекта XML-данных:
>>> gmp = GisMeteoParser(xml=xml_data)

Далее:
все сформированные данные, список (хотя обычно один город)
>>> data = gmp.data
или только первый город
>>> data = gmp.first_data

Далее все это можно использовать в шаблоне для вывода

Есть не очень красивый пример использования в модуле custom_parser

Можно определить собственный класс - наследник GisMeteoParser и сформировать 
данные нужным вам образом. Для этого можно исследовать класс _Forecast 
примерно так: _Forecast.__dict__ и выбрать все необходимые вам данные - 
все они там есть. Если впоследствии кому-то понадобится более удобная форма -
выведу все атрибуты как надо. Меня пока и так устраивает.

Если нет необходимости использовать встроенный механизм кеширования, 
то параметр use_builtin_cache надо выставить в False. Если же он используется,
то можно задать cache_dir_path и cache_file_name, иначе файл кеша
будет писаться в ту же директорию, откуда запускается скрипт.
'''

from xml.dom import minidom
import urllib, datetime, os, time

import conditions as C



# кодировка XML-документа данных
SOURCE_CODING = 'cp1251'



class _Town(object):
    '''
    Населенный пункт для которого предназначен прогноз погоды.
    В конструктор принимает валидную XML-строку определенного формата.
    '''
    
    # перечень атрибутов узла населенного пункта
    ATTR_KEYS = ['name', 'id', 'forecasts']
    
    def __init__(self, node):
        if not isinstance(node, minidom.Element):
            raise Exception('Parameter `node` must be instance of minidom.Element')
        self.name = node.getAttribute('sname').encode(SOURCE_CODING)
        self.name = urllib.unquote(self.name).decode(SOURCE_CODING)
        self.id = node.getAttribute('index')
        self.forecasts = []
        self.latitude = node.getAttribute('latitude')
        self.longitude = node.getAttribute('longitude')
        # выбираем все прогнозы
        for f in node.getElementsByTagName('FORECAST'):
            self.forecasts.append( _Forecast(f) )





class _Forecast(object):
    '''
    Прогноз погоды на определенный период дня (каждые 6 часов, от 0 до 3)
    '''
    
    # перечень атрибутов узла прогноза
    ATTR_KEYS = ['day', 'month', 'year', 'hour', 'tod', 'predict', 'weekday']
    # перечень дочерних узлов и их атрибутов
    NODES = {
        'PHENOMENA':   ['cloudiness', 'precipitation'],
        'PRESSURE':    ['max', 'min'],
        'TEMPERATURE': ['max', 'min'],
        'WIND':        ['max', 'min', 'direction'],
        'RELWET':      ['max', 'min'],
        'HEAT':        ['max', 'min'],
    }
    # атрибуты полученных данных и их человекопонятное описание
    DATA = {
        '_chk':     u'Сортер',
        '_picture': u'Изображение',
        '_tod':     u'Время дня',
        '_date':    u'Дата',
        '_phenom':  u'Погода', 
        '_temp':    u'Температура', 
        '_wind':    u'Ветер', 
        '_press':   u'Давление', 
        '_wet':     u'Влажность',
    }
    
    # если не нужно два значения - берем среднее (True)
    TEMP_IS_AVERAGE = False
    
    
    def __init__(self, node):
        if not isinstance(node, minidom.Element):
            raise Exception('Parameter `node` must be instance of minidom.Element')
        struct = _Forecast.NODES
        for a in _Forecast.ATTR_KEYS:
            setattr(self, a, node.getAttribute(a))
        for p in node.childNodes:
            if p.nodeType == p.ELEMENT_NODE and p.localName in struct.keys():
                tag_name = p.tagName
                for a in struct.get(tag_name):
                    setattr(self, '%s.%s' % (tag_name, a), p.getAttribute(a))
        self.__format()
    
    
    def __format(self):
        '''
        Форматирование всех атрибутов данных к нужному виду
        '''
        for t in _Forecast.DATA.keys():
            getattr(self, '_Forecast__fmt%s' % t)()
    
    
    def __fmt_chk(self):
        '''
        Период дня вида YYYYMMDDX. Где X - conditions.TOD
        '''
        setattr(
            self, '_chk', '%s%s%s%s' % (self.year, self.month, self.day, self.tod)
        )
    
    
    def __fmt_picture(self):
        '''
        Форматирование названия изображения
        '''
        val = self.get('PHENOMENA.cloudiness')\
           or self.get('PHENOMENA.precipitation')\
           or False
        setattr(self, '_picture', C.PICTURE.get(val, 'empty'))
    
    
    def __fmt_tod(self):
        '''
        Форматирование периода дня
        '''
        tod = self.get('tod')
        setattr(self, '_tod', C.TOD.get(tod, ''))
    
    
    def __fmt_date(self):
        '''
        Форматирование даты
        '''
        si = self.safe_int
        t = datetime.date.today()
        year = si(self.get('year')) or t.year
        month = str(si(self.get('month')) or t.month)
        day = si(self.get('day')) or t.day
        weekday = self.get('weekday')
        date = u'%s, %s %s %s' % (
            C.WEEKDAY.get(weekday, ''), day, C.MONTH.get(month, ''), year
        )
        setattr(self, '_date', date)
    
    
    def __fmt_phenom(self):
        '''
        Форматирование описания погоды
        '''
        s = []
        prec = self.get('PHENOMENA.precipitation')
        prec = C.PRECIPITATION.get(prec)
        if prec: s.append(prec)
        cloud = self.get('PHENOMENA.cloudiness')
        cloud = C.CLOUDINESS.get(cloud)
        if cloud: s.append(cloud)
        setattr(self, '_phenom', u', '.join(s))
            
    
    def __fmt_temp(self):
        '''
        Форматирование температуры воздуха
        '''
        def add_plus(n): return u'%s%s' % ('+' if n > 0 else '', n)
        t = ''; tt = []; is_avg = _Forecast.TEMP_IS_AVERAGE 
        nmin = self.get('TEMPERATURE.min')
        nmax = self.get('TEMPERATURE.max')
        if nmin != '':
            tt.append( self.safe_int(nmin) )
        if nmax != '':
            tt.append( self.safe_int(nmax) )
        tt.sort()
        if is_avg and len(tt) == 2:
            aver = (tt[0] + tt[1]) / 2
            t = add_plus(aver)
        elif not is_avg and len(tt) == 2:
            if tt[0] <= 0 and tt[1] <= 0: tt.reverse()
            t = u' '.join(map(add_plus, tt))
        elif not is_avg and len(tt) == 1:
            t = add_plus(tt[0])
        setattr(self, '_temp', u'%s°C' % t)
    
    
    def __fmt_wind(self):
        '''
        Форматирование направления и силы ветра
        '''
        nmin = self.get('WIND.min')
        nmax = self.get('WIND.max')
        ndir = self.get('WIND.direction')
        setattr(self, '_wind', u'%s %s-%s м/с' % (C.DIRECTION.get(ndir), nmin, nmax))
    
    
    def __fmt_press(self):
        '''
        Форматирование атмосферного давления
        '''
        nmin = self.get('PRESSURE.min')
        nmax = self.get('PRESSURE.max')
        setattr(self, '_press', u'%s-%s мм.рт.ст.' % (nmin, nmax))
    
    
    def __fmt_wet(self):
        '''
        Форматирование показателей влажности
        '''
        nmin = self.get('RELWET.min')
        nmax = self.get('RELWET.max')
        setattr(self, '_wet', u'%s-%s%%' % (nmin, nmax))
    
    
    def safe_int(self, n):
        '''
        Утилитарный метод приведения к целому
        '''
        try:
            return int(n)
        except:
            return 0
    
    
    def get(self, key):
        '''
        Утилитарный метод получения значения атрибута или пустой строки
        '''
        try:
            return getattr(self, key)
        except:
            return ''





class GisMeteoParser(object):
    '''
    Преобразует XML данные сервиса GisMeteo в объект вида:
    [
        {
            name      : unicode    название населенного пунтка на русском
            id        : int    ID города в сервисе
            latitude  : float    широта населенного пунтка
            longitude : float    долгота населенного пунтка
            forecasts : [    прогнозы по периодам дня
                day   : 
                month :
                year  :
                hour  :
                tod   :
                predict:
                weekday:
                _chk     : Сортер
                _picture : Изображение
                _tod     : Время дня
                _date    : Дата
                _phenom  : Погода
                _temp    : Температура
                _wind    : Ветер
                _press   : Давление
                _wet     : Влажность
                ...
            ]
        }
        ...
    ]
    '''
    
    USE_BUILTIN_CACHE = True
    SERVICE_URL = 'http://informer.gismeteo.ru/xml/'
    CACHE_DIR_PATH = '.'
    CACHE_FILE_NAME = 'gismeteo_cache.xml'
    
    def __init__(self, filename=None, xml=None, url=None, town_id=None, 
                 use_builtin_cache=True, cache_dir_path=None, cache_file_name=None):
        '''
        Принимает полный путь файла XML-данных, или объект XML данных,
        или URL сервиса для извлечения данных или ID населенного пункта
        в сервисе для формирования URL и извлечения из сервиса.
        
        Если нет необходимости использовать встроенный механизм кеширования,
        то параметр use_builtin_cache надо выставить в False. Если же он
        используется, то можно задать cache_dir_path и cache_file_name,
        иначе файл кеша  будет писаться в ту же директорию,
        откуда запускается скрипт.
        '''
        self.__data = []
        self.__xml = None
        self.USE_BUILTIN_CACHE = use_builtin_cache
        if cache_dir_path:
            self.CACHE_DIR_PATH = cache_dir_path
        if cache_file_name:
            self.CACHE_FILE_NAME = cache_file_name
        # если определено имя XML файла данных для разбора
        if filename:
            self.__xml = minidom.parse(filename)
        # если определен объект XML для разбора
        elif xml:
            self.__xml = xml
        # если задан ID населенно пункта в сервисе - формируем URL
        elif town_id:
            url = '%s%s.xml' % (self.SERVICE_URL, town_id,)
        if url:
            self.CACHE_FILE_NAME = url.split('/')[-1]
            self.__xml = minidom.parseString(self.__get_data(url))
        if not self.__xml:
            raise Exception('GisMeteoParser need data source: filename, url, XML-string or town ID.')
        self.__data_parse()
    
    
    @property
    def data(self):
        '''
        Список всех населенных пунктов с прогнозами к ним
        '''
        return self.__data
    
    
    @property
    def first_data(self):
        '''
        Данные первого населенного пункта с прогнозами
        '''
        try:
            return self.__data[0]
        except IndexError:
            return None
    
    
    def __data_parse(self):
        '''
        Разбор XML-данных
        '''
        for t in self.__xml.getElementsByTagName('TOWN'):
            self.__data.append( _Town(t) )
    
    
    def __get_data(self, url):
        '''
        Выбирает XML-данные для разбора
        '''
        if self.USE_BUILTIN_CACHE:
            return self.__get_from_cache(url)
        else:
            return self.__get_from_url(url)
    
    
    def __get_from_cache(self, url):
        '''
        Выбирает данные из встроенного кеша, если он есть и актуален
        '''
        cache = self.__cache_fullpath()
        now = time.mktime(datetime.datetime.now().timetuple())
        if os.path.isfile(cache) and (now - os.path.getmtime(cache) < 3600 * 6):
            return open(cache, 'r').read()
        else:
            return self.__get_from_url(url)
    
    
    def __get_from_url(self, url):
        '''
        Выбирает данные с сервиса и кеширует их, если USE_BUILTIN_CACHE
        '''
        data = None
        try:
            fh = urllib.urlopen(url)
            data = fh.read()
            fh.close()
        except IOError:
            pass
        if data and self.USE_BUILTIN_CACHE:
            fh = open(self.__cache_fullpath(), 'w')
            fh.write(data)
            fh.close()
        return data
    
    
    def __cache_fullpath(self):
        '''
        Формирует путь к файлу из CACHE_DIR_PATH и CACHE_FILE_NAME
        '''
        return os.path.join(self.CACHE_DIR_PATH, self.CACHE_FILE_NAME)
