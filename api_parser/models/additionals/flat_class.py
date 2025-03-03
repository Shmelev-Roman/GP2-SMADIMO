from enum import Enum


class ClassTypeEnum(str, Enum):
    economy = "Эконом"
    comfort = "Комфорт"
    business = "Бизнес"
    premium = "Премиум"
    dmo = "ДМО"
    dlo = "ДЛО"
