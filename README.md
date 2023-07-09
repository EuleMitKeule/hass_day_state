[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Code Quality](https://github.com/EuleMitKeule/hass_day_state/actions/workflows/quality.yml/badge.svg)](https://github.com/EuleMitKeule/hass_day_state/actions/workflows/quality.yml)

# HASS Day State

HASS Day State allows you to create sensor entities in Home Assistant that split up the day into predefined states.<br>
This is useful for creating automations that behave differently based on combinations sun elevation and current time.

## Installation

You can install this integration using the custom repository option in [HACS](https://hacs.xyz/).<br>

1. Add the repository URL to the list of custom repositories in HACS
2. Select and install the integration in HACS
3. Restart Home Assistant
4. Configure your entities

## Configuration

To create the entities you need to define them in your `configuration.yaml` file.<br>
For a full example of all available options see [examples](examples/configuration.yaml).

```yaml
sensor:
- platform: hass_day_state
  sensors:
  - unique_id: kuche_day_state
    friendly_name: Küche Day State
    default_state: day
    states:
    - type: elevation
      name: evening
      value: 3.5
    - type: time
      name: night
      from: "01:00"
      to: "05:30"
```

The states will get sorted automatically so that the highest reached state will be selected.<br>
Time states have priority over elevation states.<br>
Elevation values always mean that the current elevation needs to be less than the specified value for the state to be reached.
