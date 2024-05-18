# Value Saver

This integration saves a specific value every midnight and retains it across Home Assistant restarts.

## Installation

1. Ensure HACS is installed in your Home Assistant instance.
2. Add this repository to HACS.
3. Install the "Value Saver" integration via HACS.
4. Restart Home Assistant.

## Configuration

Add the following to your `configuration.yaml`:

```yaml
  - platform: value_saver
    entity_to_save: sensor.your_sensor_here
