from pydantic import BaseModel, validator, ValidationError
from typing import Optional, AnyStr, Any

from .additionals import SubRegionEnum, RegionEnum


class BuildingModel(BaseModel):
    id: int
    name: Optional[AnyStr] = None
    region: RegionEnum
    subRegion: SubRegionEnum

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
