"""Sensor module for hass_day_state component."""

import logging
from datetime import date, datetime
from decimal import Decimal

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import (
    CONF_FRIENDLY_NAME,
    CONF_NAME,
    CONF_SENSORS,
    CONF_TYPE,
    CONF_UNIQUE_ID,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.typing import StateType as HassStateType

from .const import (
    CONF_DEFAULT_STATE,
    CONF_FROM,
    CONF_STATES,
    CONF_TO,
    CONF_VALUE,
    StateType,
)
from .day_state import DefaultDayState, ElevationDayState, TimeDayState

_LOGGER = logging.getLogger(__name__)

ELEVATION_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_TYPE): cv.enum(StateType),
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_VALUE): vol.Any(float, int),
    }
)

TIME_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_TYPE): cv.enum(StateType),
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_FROM): cv.time,
        vol.Required(CONF_TO): cv.time,
    }
)

STATE_SCHEMA = vol.Any(ELEVATION_SCHEMA, TIME_SCHEMA)

SENSOR_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_UNIQUE_ID): cv.string,
        vol.Optional(CONF_FRIENDLY_NAME): cv.string,
        vol.Required(CONF_DEFAULT_STATE): cv.string,
        vol.Optional(CONF_STATES): cv.ensure_list(STATE_SCHEMA),
    }
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {vol.Required(CONF_SENSORS): cv.ensure_list(SENSOR_SCHEMA)}
)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType = None,
) -> None:
    """Set up the hass_day_state sensor platform."""

    _ = discovery_info

    async_add_entities(await _async_create_entities(hass, config))


async def _async_create_entities(
    hass: HomeAssistant, config: ConfigType
) -> list[SensorEntity]:
    """Create the sensor entities."""

    entities: list[HassDayStateSensor] = []

    for sensor_config in config[CONF_SENSORS]:
        elevation_states: list[ElevationDayState] = []
        time_states: list[TimeDayState] = []

        default_state = DefaultDayState(
            hass,
            sensor_config[CONF_DEFAULT_STATE],
        )

        for state_config in sensor_config[CONF_STATES]:
            state_type = StateType(state_config[CONF_TYPE])

            if state_type == StateType.elevation:
                elevation_states.append(
                    ElevationDayState(
                        hass,
                        state_config[CONF_NAME],
                        state_config[CONF_VALUE],
                    )
                )
            elif state_type == StateType.time:
                time_states.append(
                    TimeDayState(
                        hass,
                        state_config[CONF_NAME],
                        state_config[CONF_FROM],
                        state_config[CONF_TO],
                    )
                )
            else:
                raise ValueError(f"Unknown state type: {state_type}")

        entities.append(
            HassDayStateSensor(
                sensor_config[CONF_UNIQUE_ID],
                sensor_config.get(CONF_FRIENDLY_NAME, None),
                default_state,
                elevation_states,
                time_states,
            )
        )

    return entities


class HassDayStateSensor(SensorEntity):
    """Representation of a hass_day_state sensor."""

    def __init__(
        self,
        unique_id: str | None,
        friendly_name: str | None,
        default_state: DefaultDayState,
        elevation_states: list[ElevationDayState],
        time_states: list[TimeDayState],
    ) -> None:
        """Initialize the sensor."""

        self._attr_unique_id = unique_id
        self._friendly_name = friendly_name
        self._default_state = default_state
        self._elevation_states = sorted(
            elevation_states, key=lambda state: state.sort_key
        )
        self._time_states = sorted(
            time_states, key=lambda state: state.sort_key, reverse=True
        )

    @property
    def name(self) -> str | None:
        """Return the name of the sensor."""

        return self._friendly_name

    @property
    def native_value(self) -> HassStateType | date | datetime | Decimal:
        """Return the state of the sensor."""

        for time_state in self._time_states:
            if time_state.is_fulfilled:
                return time_state.name

        for elevation_state in self._elevation_states:
            if elevation_state.is_fulfilled:
                return elevation_state.name

        return self._default_state.name
