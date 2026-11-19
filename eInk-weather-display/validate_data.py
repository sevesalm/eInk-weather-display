from logging import Logger
from typing import Annotated, Mapping, TypeVar
from pydantic import Field, TypeAdapter, ValidationError
from type_alias import ObservationDataItem, ForecastDataItem, RadiationDataItem

T = TypeVar('T')

# Built once at import; each maps an ISO timestamp to one row of parameters and requires at least one row
observation_data_adapter = TypeAdapter(Annotated[Mapping[str, ObservationDataItem], Field(min_length=1)])
radiation_data_adapter = TypeAdapter(Annotated[Mapping[str, RadiationDataItem], Field(min_length=1)])
forecast_data_adapter = TypeAdapter(Annotated[Mapping[str, ForecastDataItem], Field(min_length=1)])


def validate_data(data: object, adapter: TypeAdapter[T], logger: Logger) -> T:
  try:
    return adapter.validate_python(data)
  except ValidationError as e:
    logger.error('Schema validation failed: %s', e)
    raise Exception('Schema validation failed') from e
