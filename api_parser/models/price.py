from typing_extensions import Self

from pydantic import BaseModel, validator, model_validator, ValidationError
from typing import Optional, Any


from .additionals import RegionEnum, SubRegionEnum, ClassTypeEnum, FlatTypeEnum


class PriceListItem(BaseModel):
    region: RegionEnum
    subRegion: SubRegionEnum
    classType: ClassTypeEnum
    flatType: FlatTypeEnum
    minPrice: float
    hasDecoration: Optional[str]    # boolean
    isApartments: str   # boolean
    isFinished: str     # boolean
    finishYear: Optional[int]

    @validator('region', pre=True)
    def validate_region(cls, region: Any) -> str:
        try:
            return RegionEnum[region].value
        except KeyError:
            raise ValidationError(f'Unexpected region - {region}')

    @validator('subRegion', pre=True)
    def validate_sub_region(cls, subRegion: Any) -> str:
        try:
            return SubRegionEnum[subRegion].value
        except KeyError:
            raise ValidationError(f'Unexpected subRegion - {subRegion}')

    @validator('classType', pre=True)
    def validate_class_type(cls, classType: Any) -> str:
        try:
            return ClassTypeEnum[classType].value
        except KeyError:
            raise ValidationError(f'Unexpected classType - {classType}')

    @validator('flatType', pre=True)
    def validate_flat_type(cls, flatType: Any) -> str:
        try:
            return FlatTypeEnum[flatType].value
        except KeyError:
            raise ValidationError(f'Unexpected flatType - {flatType}')

    @validator('minPrice', pre=True)
    def validate_min_price(cls, value):
        if value <= 0:
            raise ValidationError('min_price must be greater than 0')
        return value

    @validator('hasDecoration', 'isApartments', 'isFinished', pre=True)
    def validate_boolean_value(cls, value: Any) -> Self:
        if value is None:
            return value

        if isinstance(value, bool):
            return "Да" if value else "Нет"
        raise ValueError('Value must be a boolean')

    @model_validator(mode='after')
    def validate_finish_year(cls, values):
        if not values.isFinished == 'Да' and values.finishYear is None:
            raise ValidationError('finish_year must be provided if is_finished is False')
        return values
