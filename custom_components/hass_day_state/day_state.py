"""Class for day state."""

from abc import ABC
from datetime import datetime, time

import pytz
from homeassistant.core import HomeAssistant


class DayState(ABC):
    """Abstract class for day state."""

    def __init__(self, hass: HomeAssistant, name: str) -> None:
        self._hass = hass
        self._name = name

    @property
    def is_fulfilled(self) -> bool:
        """Return whether the day state is fulfilled."""

        raise NotImplementedError

    @property
    def name(self) -> str:
        """Return the name of the day state."""

        return self._name.lower()

    @property
    def sort_key(self) -> float:
        """Return the sort key of the day state."""

        raise NotImplementedError


class DefaultDayState(DayState):
    """Class for default day state."""

    @property
    def is_fulfilled(self) -> bool:
        return True

    @property
    def sort_key(self) -> float:
        return float("inf")


class ElevationDayState(DayState):
    """Class for elevation day state."""

    def __init__(self, hass: HomeAssistant, name: str, value: float) -> None:
        super().__init__(hass, name)
        self._value = value

    @property
    def is_fulfilled(self) -> bool:
        return self._hass.states.get("sun.sun").attributes["elevation"] < self._value

    @property
    def sort_key(self) -> float:
        return self._value


class TimeDayState(DayState):
    """Class for time day state."""

    def __init__(
        self, hass: HomeAssistant, name: str, from_time: time, to_time: time
    ) -> None:
        super().__init__(hass, name)
        self._from_time = from_time
        self._to_time = to_time

    @property
    def is_fulfilled(self) -> bool:
        # get current time in local timezone

        time_zone = pytz.timezone(self._hass.config.time_zone)
        now = datetime.now(time_zone).time()

        return self._from_time <= now <= self._to_time

    @property
    def sort_key(self) -> float:
        return self._from_time.hour + self._from_time.minute / 60
