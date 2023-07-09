"""Constants for the hass_day_state integration."""

from enum import Enum

PLATFORM = "hass_day_state"
CONF_TYPE: str = "type"
CONF_NAME: str = "name"
CONF_VALUE: str = "value"
CONF_FROM: str = "from"
CONF_TO: str = "to"
CONF_SENSORS: str = "sensors"
CONF_DEFAULT_STATE: str = "default_state"
CONF_STATES: str = "states"


class StateType(Enum):
    """Enum class for state types."""

    elevation = "elevation"
    time = "time"
