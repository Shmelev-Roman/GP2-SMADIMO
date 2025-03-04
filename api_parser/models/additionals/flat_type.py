from enum import Enum


class FlatTypeEnum(str, Enum):
    one_room = "Одна"
    two_room = "Две"
    three_room = "Три"
    four_room = "Четыре"
    studio = "Студия"
    euro_one_room = "Одна [ЕВРО]"
    euro_two_room = "Две [ЕВРО]"
    euro_three_room = "Три [ЕВРО]"
    euro_four_room = "Четыре [ЕВРО]"
