"""Platform for sensor integration."""
from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from homeassistant.helpers.entity import Entity
from datetime import datetime, timedelta
import pytz
import aiohttp
import json
import logging

_LOGGER = logging.getLogger(__name__)


# Async function to fetch holiday data
async def fetch_holiday_data():
    url = 'https://www.1823.gov.hk/common/ical/en.json'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                text = await response.text(encoding='utf-8-sig')
                return json.loads(text)
            else:
                return None

# Function to check if a given date is a holiday or a weekend (Saturday or Sunday)
# This remains a synchronous function
def is_holiday_or_weekend(date, holiday_data):
    # Check if the day is Saturday or Sunday
    if date.weekday() == 5 or date.weekday() == 6:  # 5 is Saturday, 6 is Sunday
        return True
    # Check against holiday data
    for event in holiday_data['vcalendar'][0]['vevent']:
        if date == datetime.strptime(event['dtstart'][0], '%Y%m%d').date():
            return True
    return False

bus_schedules = {
    "b_route": {
        "non_holiday": [
            ('06:35', 'B線'), ('06:35', 'B線 9座開出'), ('06:45', 'B線'), ('06:55', 'B線'), ('06:55', 'B線 9座開出'), ('07:05', '9座 開出'), ('07:10', 'B線'), ('07:15', 'B線'), ('07:20', 'B線'), ('07:20', 'B線 9座開出'), ('07:30', 'B線 9座開出'), ('07:35', 'B線'), ('07:40', 'B線'), ('07:45', 'B線'), ('07:50', 'B線 9座開出'), ('07:55', 'B線 9座開出'), ('08:00', 'B線'), ('08:05', 'B線'), ('08:10', 'B線'), ('08:20', 'B線 9座開出'), ('08:25', 'B線'), ('08:30', 'B線'), ('08:35', 'B線'), ('08:45', 'B線 9座開出'), ('08:50', 'B線'), ('08:55', 'B線'), ('09:05', 'B線'), ('09:15', 'B線'), ('09:25', 'B線'), ('09:35', 'B線'), ('09:45', 'B線'), ('09:55', 'B線'), ('10:05', 'B線'), ('10:20', 'B線'), ('10:35', 'B線'), ('10:50', 'B線'), ('11:05', 'B線'), ('11:20', 'B線'), ('11:35', 'B線'), ('11:50', 'B線'), ('12:05', 'B線'), ('12:20', 'B線'), ('12:35', 'B線'), ('12:50', 'B線'), ('13:05', 'B線'), ('13:20', 'B線'), ('13:30', 'B線'), ('13:40', 'B線'), ('13:50', 'B線'), ('14:00', 'B線'), ('14:10', 'B線'), ('14:20', 'B線'), ('14:30', 'B線'), ('14:40', 'B線'), ('14:50', 'B線'), ('15:00', 'B線'), ('15:10', 'B線'), ('15:20', 'B線'), ('15:30', 'B線'), ('15:40', 'B線'), ('15:50', 'B線'), ('16:00', 'B線'), ('16:10', 'B線'), ('16:20', 'B線'), ('16:30', 'B線'), ('16:40', 'B線'), ('16:55', 'B線'), ('17:10', 'B線'), ('17:20', 'B線'), ('17:35', 'B線'), ('17:45', 'B線'), ('18:00', 'B線'), ('18:10', 'B線'), ('18:20', 'B線'), ('18:25', 'B線'), ('18:35', 'B線'), ('18:45', 'B線'), ('18:50', 'B線'), ('19:00', 'B線'), ('19:10', 'B線'), ('19:15', 'B線'), ('19:25', 'B線'), ('19:35', 'B線'), ('19:40', 'B線'), ('19:50', 'B線'), ('20:05', 'B線'), ('20:15', 'B線'), ('20:30', 'B線'), ('20:40', 'B線'), ('20:55', 'B線'), ('21:05', 'B線'), ('21:20', 'B線'), ('21:30', 'B線'), ('21:45', 'B線'), ('21:55', 'B線'), ('22:10', 'B線'), ('22:20', 'B線'), ('22:30', 'B線'), ('22:40', 'B線'), ('22:50', 'B線'), ('23:00', 'B線'), ('23:15', '尾班車,停全座')
        ],
        "holiday": [
            ('06:35', 'B線'), ('06:45', 'B線'), ('06:55', 'B線'), ('07:05', 'B線'), ('07:15', 'B線'), ('07:25', 'B線'), ('07:35', 'B線'), ('07:45', 'B線'), ('07:55', 'B線'), ('08:05', 'B線'), ('08:15', 'B線'), ('08:25', 'B線'), ('08:35', 'B線'), ('08:45', 'B線'), ('08:55', 'B線'), ('09:05', 'B線'), ('09:15', 'B線'), ('09:25', 'B線'), ('09:35', 'B線'), ('09:45', 'B線'), ('10:00', 'B線'), ('10:15', 'B線'), ('10:30', 'B線'), ('10:45', 'B線'), ('11:00', 'B線'), ('11:15', 'B線'), ('11:30', 'B線'), ('11:45', 'B線'), ('12:00', 'B線'), ('12:10', 'B線'), ('12:15', 'B線'), ('12:25', 'B線'), ('12:35', 'B線'), ('12:45', 'B線'), ('12:55', 'B線'), ('13:00', 'B線'), ('13:10', 'B線'), ('13:20', 'B線'), ('13:25', 'B線'), ('13:35', 'B線'), ('13:45', 'B線'), ('13:50', 'B線'), ('14:00', 'B線'), ('14:15', 'B線'), ('14:25', 'B線'), ('14:40', 'B線'), ('14:55', 'B線'), ('15:10', 'B線'), ('15:25', 'B線'), ('15:40', 'B線'), ('15:50', 'B線'), ('16:00', 'B線'), ('16:10', 'B線'), ('16:20', 'B線'), ('16:30', 'B線'), ('16:40', 'B線'), ('16:50', 'B線'), ('17:00', 'B線'), ('17:10', 'B線'), ('17:20', 'B線'), ('17:25', 'B線'), ('17:35', 'B線'), ('17:45', 'B線'), ('17:50', 'B線'), ('18:00', 'B線'), ('18:10', 'B線'), ('18:15', 'B線'), ('18:25', 'B線'), ('18:35', 'B線'), ('18:40', 'B線'), ('18:50', 'B線'), ('19:05', 'B線'), ('19:15', 'B線'), ('19:30', 'B線'), ('19:40', 'B線'), ('19:55', 'B線'), ('20:05', 'B線'), ('20:20', 'B線'), ('20:30', 'B線'), ('20:45', 'B線'), ('20:55', 'B線'), ('21:10', 'B線'), ('21:20', 'B線'), ('21:35', 'B線'), ('21:45', 'B線'), ('21:55', 'B線'), ('22:05', 'B線'), ('22:15', 'B線'), ('22:25', 'B線'), ('22:35', 'B線'), ('22:45', 'B線'), ('23:00', 'B線'), ('23:15', 'B線尾班車 停全座')
        ]
    },
    "c_route": {
        "non_holiday": [
            ('09:15', 'C線 9座開出'), ('10:15', 'C線 9座開出'), ('11:15', 'C線 9座開出'), ('12:15', 'C線 9座開出'), ('13:15', 'C線 9座開出'), ('14:15', 'C線 9座開出'), ('15:15', 'C線 9座開出'), ('16:15', 'C線 9座開出'), ('17:15', 'C線 9座開出'), ('20:15', 'C線 9座開出'), ('21:15', 'C線 9座開出'), ('22:15', '尾班車,9座開出')
        ],
        "holiday": [
            ('06:30', 'C線 9座開出'), ('07:30', 'C線 9座開出'), ('08:30', 'C線 9座開出'), ('09:30', 'C線 9座開出'), ('10:30', 'C線 9座開出'), ('11:30', 'C線 9座開出'), ('14:30', 'C線 9座開出'), ('15:30', 'C線 9座開出'), ('16:30', 'C線 9座開出'), ('19:30', 'C線 9座開出'), ('20:30', 'C線 9座開出'), ('21:30', 'C線 9座開出'), ('22:30', 'C線尾班車 9座開出')
        ]
    }
}

# Function to get the next 'n' schedules based on the current time
def get_next_schedules(route, day_type, current_time, n):
    schedules = bus_schedules[route][day_type]
    future_schedules = [time for time in schedules if time[0] > current_time]
    return future_schedules[:n]

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the sensor platform."""
    sensors = []

    # Fetch holiday data asynchronously
    holiday_data = await fetch_holiday_data()

    # Add title sensors
    sensors.append(BusTitleSensor('b_route', hass, holiday_data))
    sensors.append(BusTitleSensor('c_route', hass, holiday_data))

    # Create 4 sensors for each shuttle route
    for i in range(4):
        sensors.append(BusScheduleSensor('b_route', i, hass, holiday_data))
        sensors.append(BusScheduleSensor('c_route', i, hass, holiday_data))

    async_add_entities(sensors, True)  # The True at the end triggers an update upon entity addition

class BusTitleSensor(SensorEntity):
    """Sensor for displaying shuttle title with holiday information."""

    def __init__(self, route: str, hass, holiday_data):
        """Initialize the sensor."""
        self.route = route
        self.hass = hass
        self.holiday_data = holiday_data
        self._state = "時間"
        self._name = f"shuttle_{self.route[0]}_title"
        self.schedule_next_update()

    @property
    def unique_id(self):
        """Return a unique ID to use for this sensor."""
        return f"shuttle_{self.route[0]}_title"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return "mdi:bus-clock"

    def generate_sensor_name(self):
        """Generate the sensor name based on holiday status."""
        timezone = pytz.timezone('Asia/Hong_Kong')
        now = datetime.now(timezone)
        current_date = now.date()
        holiday_status = "假日" if is_holiday_or_weekend(current_date, self.holiday_data) else "非假日"
        route_name = "穿梭巴士B線 天鑽至南運路" if self.route == 'b_route' else "穿梭巴士C線 天鑽至大埔延長線"
        return f"{route_name} {holiday_status}"

    def update(self):
        """Update the sensor."""
        self._name = self.generate_sensor_name()
        self.schedule_next_update()

    def schedule_next_update(self):
        """Schedule the next update at midnight."""
        now = datetime.now()
        next_midnight = datetime.combine(now.date() + timedelta(days=1), datetime.min.time())
        delay = (next_midnight - now).total_seconds()
        self.hass.helpers.event.async_call_later(delay, lambda _: self.async_schedule_update_ha_state(True))

class BusScheduleSensor(Entity):
    def __init__(self, route: str, index: int, hass, holiday_data):
        """Initialize the sensor."""
        super().__init__()
        self.route = route
        self.index = index
        self.hass = hass
        self.holiday_data = holiday_data
        self._name = f"shuttle_{self.route[0]}_{self.index + 1}"
        self._state = None
        self._attributes = {'departure_time': None, 'route': self.route, 'is_holiday': False}
        self._last_update = pytz.utc.localize(datetime.min)

    @property
    def unique_id(self):
        """Return a unique ID to use for this sensor."""
        return f"shuttle_{self.route[0]}_{self.index + 1}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return "mdi:bus"

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    def should_poll(self):
        """Sensor should be polled."""
        return True

    def update(self):
        """Fetch new state data for the sensor."""
        timezone = pytz.timezone('Asia/Hong_Kong')
        now = datetime.now(timezone)
        current_time = now.strftime('%H:%M')
        current_date = now.date()

        # Determine if today is a holiday or non-holiday
        is_holiday = is_holiday_or_weekend(current_date, self.holiday_data)

        # Fetch the next schedules
        next_schedules = get_next_schedules(self.route, 'holiday' if is_holiday else 'non_holiday', current_time, 4)

        if len(next_schedules) > self.index:
            schedule_time_str, schedule_name = next_schedules[self.index]
            self._name = schedule_name
            schedule_time_naive = datetime.strptime(schedule_time_str, '%H:%M')
            schedule_time = now.replace(hour=schedule_time_naive.hour, minute=schedule_time_naive.minute, second=0, microsecond=0)

            # If the schedule time is earlier than now, assume it's for the next day
            if schedule_time < now:
                schedule_time += timedelta(days=1)

            # Calculate the time difference
            time_diff = schedule_time - now
            seconds_diff = time_diff.total_seconds()

            # Update attributes
            self._attributes['departure_time'] = schedule_time_str
            self._attributes['route'] = self.route.upper()[:1]  # 'B' or 'C'
            self._attributes['is_holiday'] = is_holiday

            # Format the state display
            if seconds_diff <= 0:
                self._state = '已開出'
            elif seconds_diff <= 60:  # Less than 1 minute
                self._state = "<1 分鐘"
            elif seconds_diff <= 3600:  # Less than 1 hour
                self._state = f"{int(seconds_diff // 60)} 分鐘"
            else:  # Longer than 1 hour
                hours = int(seconds_diff // 3600)
                minutes = int((seconds_diff % 3600) // 60)
                self._state = f"{hours} 小時 {minutes} 分鐘"
        else:
            self._state = ''

        # Schedule the next update
        self.schedule_next_update()

    def schedule_next_update(self):
        """Schedule the next update at the start of the next minute."""
        now = datetime.now(pytz.timezone('Asia/Hong_Kong'))
        next_minute = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
        delay = (next_minute - now).total_seconds()
        # Use Home Assistant's event loop to schedule the next update
        self.hass.helpers.event.async_call_later(delay, lambda _: self.async_schedule_update_ha_state(True))
