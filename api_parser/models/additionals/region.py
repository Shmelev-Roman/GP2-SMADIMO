from enum import Enum


class RegionEnum(str, Enum):
    moscow = "Москва"
    moscow_area = "Московская область"
    saint_petersburg = "Санкт-Петербург"
    saint_petersburg_area = "Ленинградская область"


class SubRegionEnum(str, Enum):
    cao = "Москва ЦАО (Центральный административный округ)"
    sao = "Москва САО (Северный административный округ)"
    svao = "Москва СВАО (Северо-Восточный административный округ)"
    vao = "Москва ВАО (Восточный административный округ)"
    uvao = "Москва ЮВАО (Юго-Восточный административный округ)"
    uao = "Москва ЮАО (Южный административный округ)"
    uzao = "Москва ЮЗАО (Юго-Западный административный округ)"
    zao = "Москва ЗАО (Западный административный округ)"
    szao = "Москва СЗАО (Северо-Западный административный округ)"
    zlao = "Москва ЗлАО (Зеленоградский административный округ)"

    nao = "Новая Москва НАО (Новомосковский административный округ)"
    tao = "Новая Москва ТАО (Троицкий административный округ)"

    near_moscow_area = "Ближайшее Подмосковье"
    dmo_north = "Дальнее Подмосковье (Север)"
    dmo_south = "Дальнее Подмосковье (Юг)"
    dmo_west = "Дальнее Подмосковье (Запад)"
    dmo_east = "Дальнее Подмосковье (Восток)"

    saint_petersburg = "Санкт-Петербург"

    near_saint_petersburg_area = "Ближайшая Ленинградская область"
    dlo_north = "Дальняя Ленинградская область (Север)"
    dlo_south = "Дальняя Ленинградская область (Юг)"
    dlo_west = "Дальняя Ленинградская область (Запад)"
    dlo_east = "Дальняя Ленинградская область (Восток)"
