# -*- coding: utf-8 -*-

from gismeteo.parser import GisMeteoParser, _Forecast


class CustomGisMeteoParser(GisMeteoParser):
    '''
    Пример использования GisMeteoParser
    
    Не использовать. Устаревший код.
    '''
    IMAGE_DIR_URL = ''
    
    def html_for_service(self):
        '''
        HTML представление данных для моего сервиса
        '''
        town = self.first_data
        u = [
            u'<h2>Прогноз погоды для %s</h2>' % town.name,
            u'<h4>Предоставлено <a href="http://www.gismeteo.ru/towns/',
            u'%s.htm" title="Gismeteo.ru">Gismeteo.ru</a></h4>' % town.id
        ]
        for f in town.forecasts:
            u.append(u'<hr/><div style="background: url(%s%s.png)' % (self.IMAGE_DIR_URL, f._picture,))
            u.append(u' no-repeat left top;padding-left:75px;line-height:150%;">')
            u.append(u'<div style="font-weight:bold;font-size:110%%;">%s' % f._tod)
            u.append(u', %s</div>' % f._date)
            u.append(u'<div>%s</div>' % f._phenom)
            u.append(u'<div><b>Температура:</b> %s</div>' % f._temp)
            u.append(u'<div><b>Ветер:</b> %s</div>' % f._wind)
            u.append(u'<div><b>Давление:</b> %s</div>' % f._press)
            u.append(u'<div><b>Влажность:</b> %s</div></div>' % f._wet)
        return u''.join(u)
    
    def xml_for_service(self):
        '''
        XML представление данных для моего сервиса
        '''
        town = self.data[0]
        u = [
            '<?xml version="1.0" encoding="utf-8"?>', '<data>'
        ]
        for f in town.forecasts:
            u.append('    <row>')
            for a in _Forecast.DATA:
                if a == '_date':
                    key = 'time'
                else:
                    key = a[1:]
                u.append( '        <%s>%s</%s>' % ( key, getattr(f, a), key ) )
            u.append('    </row>')
        u.append('</data>')
        return u'\n'.join(u)



if __name__ == '__main__':
    gmp = CustomGisMeteoParser(town_id=28367) # для г. Тюмень
    print gmp.xml_for_service()
