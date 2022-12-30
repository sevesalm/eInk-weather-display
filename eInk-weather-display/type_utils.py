from typing import Optional, TypeVar

T = TypeVar('T')


def assertNotNone(obj: Optional[T]) -> T:
  try:
    assert obj is not None
  except (AssertionError):
    raise AssertionError('Unexpected None')
  return obj
