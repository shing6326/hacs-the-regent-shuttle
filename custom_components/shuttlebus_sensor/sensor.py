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


# Async function to fetch holiday data
async def fetch_holiday_data():
    url = 'https://www.1823.gov.hk/common/ical/en.json'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
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
            ('06:35', ''), ('06:35', '9座開出'), ('06:45', ''), ('06:55', ''), ('06:55', '9座開出'), ('07:05', '9座 開出'), ('07:10', ''), ('07:15', ''), ('07:20', ''), ('07:20', '9座開出'), ('07:30', '9座開出'), ('07:35', ''), ('07:40', ''), ('07:45', ''), ('07:50', '9座開出'), ('07:55', '9座開出'), ('08:00', ''), ('08:05', ''), ('08:10', ''), ('08:20', '9座開出'), ('08:25', ''), ('08:30', ''), ('08:35', ''), ('08:45', '9座開出'), ('08:50', ''), ('08:55', ''), ('09:05', ''), ('09:15', ''), ('09:25', ''), ('09:35', ''), ('09:45', ''), ('09:55', ''), ('10:05', ''), ('10:20', ''), ('10:35', ''), ('10:50', ''), ('11:05', ''), ('11:20', ''), ('11:35', ''), ('11:50', ''), ('12:05', ''), ('12:20', ''), ('12:35', ''), ('12:50', ''), ('13:05', ''), ('13:20', ''), ('13:30', ''), ('13:40', ''), ('13:50', ''), ('14:00', ''), ('14:10', ''), ('14:20', ''), ('14:30', ''), ('14:40', ''), ('14:50', ''), ('15:00', ''), ('15:10', ''), ('15:20', ''), ('15:30', ''), ('15:40', ''), ('15:50', ''), ('16:00', ''), ('16:10', ''), ('16:20', ''), ('16:30', ''), ('16:40', ''), ('16:55', ''), ('17:10', ''), ('17:20', ''), ('17:35', ''), ('17:45', ''), ('18:00', ''), ('18:10', ''), ('18:20', ''), ('18:25', ''), ('18:35', ''), ('18:45', ''), ('18:50', ''), ('19:00', ''), ('19:10', ''), ('19:15', ''), ('19:25', ''), ('19:35', ''), ('19:40', ''), ('19:50', ''), ('20:05', ''), ('20:15', ''), ('20:30', ''), ('20:40', ''), ('20:55', ''), ('21:05', ''), ('21:20', ''), ('21:30', ''), ('21:45', ''), ('21:55', ''), ('22:10', ''), ('22:20', ''), ('22:30', ''), ('22:40', ''), ('22:50', ''), ('23:00', ''), ('23:15', '尾班車,停全座')
        ],
        "holiday": [
            ('06:35', ''), ('06:45', ''), ('06:55', ''), ('07:05', ''), ('07:15', ''), ('07:25', ''), ('07:35', ''), ('07:45', ''), ('07:55', ''), ('08:05', ''), ('08:15', ''), ('08:25', ''), ('08:35', ''), ('08:45', ''), ('08:55', ''), ('09:05', ''), ('09:15', ''), ('09:25', ''), ('09:35', ''), ('09:45', ''), ('10:00', ''), ('10:15', ''), ('10:30', ''), ('10:45', ''), ('11:00', ''), ('11:15', ''), ('11:30', ''), ('11:45', ''), ('12:00', ''), ('12:10', ''), ('12:15', ''), ('12:25', ''), ('12:35', ''), ('12:45', ''), ('12:55', ''), ('13:00', ''), ('13:10', ''), ('13:20', ''), ('13:25', ''), ('13:35', ''), ('13:45', ''), ('13:50', ''), ('14:00', ''), ('14:15', ''), ('14:25', ''), ('14:40', ''), ('14:55', ''), ('15:10', ''), ('15:25', ''), ('15:40', ''), ('15:50', ''), ('16:00', ''), ('16:10', ''), ('16:20', ''), ('16:30', ''), ('16:40', ''), ('16:50', ''), ('17:00', ''), ('17:10', ''), ('17:20', ''), ('17:25', ''), ('17:35', ''), ('17:45', ''), ('17:50', ''), ('18:00', ''), ('18:10', ''), ('18:15', ''), ('18:25', ''), ('18:35', ''), ('18:40', ''), ('18:50', ''), ('19:05', ''), ('19:15', ''), ('19:30', ''), ('19:40', ''), ('19:55', ''), ('20:05', ''), ('20:20', ''), ('20:30', ''), ('20:45', ''), ('20:55', ''), ('21:10', ''), ('21:20', ''), ('21:35', ''), ('21:45', ''), ('21:55', ''), ('22:05', ''), ('22:15', ''), ('22:25', ''), ('22:35', ''), ('22:45', ''), ('23:00', ''), ('23:15', '尾班車,停全座')
        ]
    },
    "c_route": {
        "non_holiday": [
            ('09:15', '9座開出'), ('10:15', '9座開出'), ('11:15', '9座開出'), ('12:15', '9座開出'), ('13:15', '9座開出'), ('14:15', '9座開出'), ('15:15', '9座開出'), ('16:15', '9座開出'), ('17:15', '9座開出'), ('20:15', '9座開出'), ('21:15', '9座開出'), ('22:15', '尾班車,9座開出')
        ],
        "holiday": [
            ('06:30', '9座開出'), ('07:30', '9座開出'), ('08:30', '9座開出'), ('09:30', '9座開出'), ('10:30', '9座開出'), ('11:30', '9座開出'), ('14:30', '9座開出'), ('15:30', '9座開出'), ('16:30', '9座開出'), ('19:30', '9座開出'), ('20:30', '9座開出'), ('21:30', '9座開出'), ('22:30', '尾班 車,9座開出')
        ]
    }
}

# Fetch holiday data
holiday_data = fetch_holiday_data()

# Function to get the next 'n' schedules based on the current time
def get_next_schedules(route, day_type, current_time, n):
    schedules = bus_schedules[route][day_type]
    future_schedules = [time for time in schedules if time[0] > current_time]
    return future_schedules[:n]

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the sensor platform."""
    sensors = []

    # Create 4 sensors for each shuttle route
    for i in range(4):
        sensors.append(BusScheduleSensor('b_route', i))
        sensors.append(BusScheduleSensor('c_route', i))

    async_add_entities(sensors)

async def async_update_data():
    """Fetch new state data for the sensor."""
    try:
        bus_schedules = get_bus_schedules()
        return bus_schedules
    except Exception as e:
        _LOGGER.error("An exception occurred while fetching bus schedules: %s", e)
        return {}

class BusScheduleSensor(Entity):
    def __init__(self, route: str, index: int):
        """Initialize the sensor."""
        super().__init__()
        self.route = route
        self.index = index
        self._state = None
        self._attributes = {}
        self._last_update = pytz.utc.localize(datetime.min)

    @property
    def unique_id(self):
        """Return a unique ID to use for this sensor."""
        return f"{self.route}_{self.index + 1}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"shuttle_{self.route[0]}_{self.index + 1}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return "mdi:bus"

    def should_poll(self):
        """Sensor should be polled."""
        return True

    def update(self):
        """Fetch new state data for the sensor."""
        # Determine current time and date type
        timezone = pytz.timezone('Asia/Hong_Kong')
        now = datetime.now(timezone)
        current_time = now.strftime('%H:%M')
        current_date = now.date()

        # Determine if today is a holiday or non-holiday
        day_type = 'holiday' if is_holiday_or_weekend(current_date, holiday_data) else 'non_holiday'

        # Fetch the next schedules
        next_schedules = get_next_schedules(self.route, day_type, current_time, 4)

        if len(next_schedules) > self.index:
            schedule_time_str = next_schedules[self.index][0]
            schedule_time_naive = datetime.strptime(schedule_time_str, '%H:%M')
            schedule_time = now.replace(hour=schedule_time_naive.hour, minute=schedule_time_naive.minute, second=0, microsecond=0)

            # If the schedule time is earlier than now, assume it's for the next day
            if schedule_time < now:
                schedule_time += timedelta(days=1)

            # Calculate the time difference
            time_diff = schedule_time - now
            seconds_diff = time_diff.total_seconds()

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
