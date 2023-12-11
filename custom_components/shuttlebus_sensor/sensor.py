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

timezone = pytz.timezone('Asia/Hong_Kong')

bus_schedule = {
    ('b', False): {'description': '南運路 非假日', 'schedule': [{'time': '06:35', 'info': 'B線'}, {'time': '06:35', 'info': 'B線 9座開出'}, {'time': '06:45', 'info': 'B線'}, {'time': '06:55', 'info': 'B線'}, {'time': '06:55', 'info': 'B線 9座開出'}, {'time': '07:05', 'info': '9座 開出'}, {'time': '07:10', 'info': 'B線'}, {'time': '07:15', 'info': 'B線'}, {'time': '07:20', 'info': 'B線'}, {'time': '07:20', 'info': 'B線 9座開出'}, {'time': '07:30', 'info': 'B線 9座開出'}, {'time': '07:35', 'info': 'B線'}, {'time': '07:40', 'info': 'B線'}, {'time': '07:45', 'info': 'B線'}, {'time': '07:50', 'info': 'B線 9座開出'}, {'time': '07:55', 'info': 'B線 9座開出'}, {'time': '08:00', 'info': 'B線'}, {'time': '08:05', 'info': 'B線'}, {'time': '08:10', 'info': 'B線'}, {'time': '08:20', 'info': 'B線 9座開出'}, {'time': '08:25', 'info': 'B線'}, {'time': '08:30', 'info': 'B線'}, {'time': '08:35', 'info': 'B線'}, {'time': '08:45', 'info': 'B線 9座開出'}, {'time': '08:50', 'info': 'B線'}, {'time': '08:55', 'info': 'B線'}, {'time': '09:05', 'info': 'B線'}, {'time': '09:15', 'info': 'B線'}, {'time': '09:25', 'info': 'B線'}, {'time': '09:35', 'info': 'B線'}, {'time': '09:45', 'info': 'B線'}, {'time': '09:55', 'info': 'B線'}, {'time': '10:05', 'info': 'B線'}, {'time': '10:20', 'info': 'B線'}, {'time': '10:35', 'info': 'B線'}, {'time': '10:50', 'info': 'B線'}, {'time': '11:05', 'info': 'B線'}, {'time': '11:20', 'info': 'B線'}, {'time': '11:35', 'info': 'B線'}, {'time': '11:50', 'info': 'B線'}, {'time': '12:05', 'info': 'B線'}, {'time': '12:20', 'info': 'B線'}, {'time': '12:35', 'info': 'B線'}, {'time': '12:50', 'info': 'B線'}, {'time': '13:05', 'info': 'B線'}, {'time': '13:20', 'info': 'B線'}, {'time': '13:30', 'info': 'B線'}, {'time': '13:40', 'info': 'B線'}, {'time': '13:50', 'info': 'B線'}, {'time': '14:00', 'info': 'B線'}, {'time': '14:10', 'info': 'B線'}, {'time': '14:20', 'info': 'B線'}, {'time': '14:30', 'info': 'B線'}, {'time': '14:40', 'info': 'B線'}, {'time': '14:50', 'info': 'B線'}, {'time': '15:00', 'info': 'B線'}, {'time': '15:10', 'info': 'B線'}, {'time': '15:20', 'info': 'B線'}, {'time': '15:30', 'info': 'B線'}, {'time': '15:40', 'info': 'B線'}, {'time': '15:50', 'info': 'B線'}, {'time': '16:00', 'info': 'B線'}, {'time': '16:10', 'info': 'B線'}, {'time': '16:20', 'info': 'B線'}, {'time': '16:30', 'info': 'B線'}, {'time': '16:40', 'info': 'B線'}, {'time': '16:55', 'info': 'B線'}, {'time': '17:10', 'info': 'B線'}, {'time': '17:20', 'info': 'B線'}, {'time': '17:35', 'info': 'B線'}, {'time': '17:45', 'info': 'B線'}, {'time': '18:00', 'info': 'B線'}, {'time': '18:10', 'info': 'B線'}, {'time': '18:20', 'info': 'B線'}, {'time': '18:25', 'info': 'B線'}, {'time': '18:35', 'info': 'B線'}, {'time': '18:45', 'info': 'B線'}, {'time': '18:50', 'info': 'B線'}, {'time': '19:00', 'info': 'B線'}, {'time': '19:10', 'info': 'B線'}, {'time': '19:15', 'info': 'B線'}, {'time': '19:25', 'info': 'B線'}, {'time': '19:35', 'info': 'B線'}, {'time': '19:40', 'info': 'B線'}, {'time': '19:50', 'info': 'B線'}, {'time': '20:05', 'info': 'B線'}, {'time': '20:15', 'info': 'B線'}, {'time': '20:30', 'info': 'B線'}, {'time': '20:40', 'info': 'B線'}, {'time': '20:55', 'info': 'B線'}, {'time': '21:05', 'info': 'B線'}, {'time': '21:20', 'info': 'B線'}, {'time': '21:30', 'info': 'B線'}, {'time': '21:45', 'info': 'B線'}, {'time': '21:55', 'info': 'B線'}, {'time': '22:10', 'info': 'B線'}, {'time': '22:20', 'info': 'B線'}, {'time': '22:30', 'info': 'B線'}, {'time': '22:40', 'info': 'B線'}, {'time': '22:50', 'info': 'B線'}, {'time': '23:00', 'info': 'B線'}, {'time': '23:15', 'info': 'B線 停全座'}]},
    ('b', True): {'description': '南運路 假日', 'schedule': [{'time': '06:35', 'info': 'B線'}, {'time': '06:45', 'info': 'B線'}, {'time': '06:55', 'info': 'B線'}, {'time': '07:05', 'info': 'B線'}, {'time': '07:15', 'info': 'B線'}, {'time': '07:25', 'info': 'B線'}, {'time': '07:35', 'info': 'B線'}, {'time': '07:45', 'info': 'B線'}, {'time': '07:55', 'info': 'B線'}, {'time': '08:05', 'info': 'B線'}, {'time': '08:15', 'info': 'B線'}, {'time': '08:25', 'info': 'B線'}, {'time': '08:35', 'info': 'B線'}, {'time': '08:45', 'info': 'B線'}, {'time': '08:55', 'info': 'B線'}, {'time': '09:05', 'info': 'B線'}, {'time': '09:15', 'info': 'B線'}, {'time': '09:25', 'info': 'B線'}, {'time': '09:35', 'info': 'B線'}, {'time': '09:45', 'info': 'B線'}, {'time': '10:00', 'info': 'B線'}, {'time': '10:15', 'info': 'B線'}, {'time': '10:30', 'info': 'B線'}, {'time': '10:45', 'info': 'B線'}, {'time': '11:00', 'info': 'B線'}, {'time': '11:15', 'info': 'B線'}, {'time': '11:30', 'info': 'B線'}, {'time': '11:45', 'info': 'B線'}, {'time': '12:00', 'info': 'B線'}, {'time': '12:10', 'info': 'B線'}, {'time': '12:15', 'info': 'B線'}, {'time': '12:25', 'info': 'B線'}, {'time': '12:35', 'info': 'B線'}, {'time': '12:45', 'info': 'B線'}, {'time': '12:55', 'info': 'B線'}, {'time': '13:00', 'info': 'B線'}, {'time': '13:10', 'info': 'B線'}, {'time': '13:20', 'info': 'B線'}, {'time': '13:25', 'info': 'B線'}, {'time': '13:35', 'info': 'B線'}, {'time': '13:45', 'info': 'B線'}, {'time': '13:50', 'info': 'B線'}, {'time': '14:00', 'info': 'B線'}, {'time': '14:15', 'info': 'B線'}, {'time': '14:25', 'info': 'B線'}, {'time': '14:40', 'info': 'B線'}, {'time': '14:55', 'info': 'B線'}, {'time': '15:10', 'info': 'B線'}, {'time': '15:25', 'info': 'B線'}, {'time': '15:40', 'info': 'B線'}, {'time': '15:50', 'info': 'B線'}, {'time': '16:00', 'info': 'B線'}, {'time': '16:10', 'info': 'B線'}, {'time': '16:20', 'info': 'B線'}, {'time': '16:30', 'info': 'B線'}, {'time': '16:40', 'info': 'B線'}, {'time': '16:50', 'info': 'B線'}, {'time': '17:00', 'info': 'B線'}, {'time': '17:10', 'info': 'B線'}, {'time': '17:20', 'info': 'B線'}, {'time': '17:25', 'info': 'B線'}, {'time': '17:35', 'info': 'B線'}, {'time': '17:45', 'info': 'B線'}, {'time': '17:50', 'info': 'B線'}, {'time': '18:00', 'info': 'B線'}, {'time': '18:10', 'info': 'B線'}, {'time': '18:15', 'info': 'B線'}, {'time': '18:25', 'info': 'B線'}, {'time': '18:35', 'info': 'B線'}, {'time': '18:40', 'info': 'B線'}, {'time': '18:50', 'info': 'B線'}, {'time': '19:05', 'info': 'B線'}, {'time': '19:15', 'info': 'B線'}, {'time': '19:30', 'info': 'B線'}, {'time': '19:40', 'info': 'B線'}, {'time': '19:55', 'info': 'B線'}, {'time': '20:05', 'info': 'B線'}, {'time': '20:20', 'info': 'B線'}, {'time': '20:30', 'info': 'B線'}, {'time': '20:45', 'info': 'B線'}, {'time': '20:55', 'info': 'B線'}, {'time': '21:10', 'info': 'B線'}, {'time': '21:20', 'info': 'B線'}, {'time': '21:35', 'info': 'B線'}, {'time': '21:45', 'info': 'B線'}, {'time': '21:55', 'info': 'B線'}, {'time': '22:05', 'info': 'B線'}, {'time': '22:15', 'info': 'B線'}, {'time': '22:25', 'info': 'B線'}, {'time': '22:35', 'info': 'B線'}, {'time': '22:45', 'info': 'B線'}, {'time': '23:00', 'info': 'B線'}, {'time': '23:15', 'info': 'B線 停全座'}]},
    ('c', False): {'description': '大埔延長線 非假日', 'schedule': [{'time': '09:15', 'info': 'C線 9座開出'}, {'time': '10:15', 'info': 'C線 9座開出'}, {'time': '11:15', 'info': 'C線 9座開出'}, {'time': '12:15', 'info': 'C線 9座開出'}, {'time': '13:15', 'info': 'C線 9座開出'}, {'time': '14:15', 'info': 'C線 9座開出'}, {'time': '15:15', 'info': 'C線 9座開出'}, {'time': '16:15', 'info': 'C線 9座開出'}, {'time': '17:15', 'info': 'C線 9座開出'}, {'time': '20:15', 'info': 'C線 9座開出'}, {'time': '21:15', 'info': 'C線 9座開出'}, {'time': '22:15', 'info': 'C線 9座開出'}]},
    ('c', True): {'description': '大埔延長線 假日', 'schedule': [{'time': '06:30', 'info': 'C線 9座開出'}, {'time': '07:30', 'info': 'C線 9座開出'}, {'time': '08:30', 'info': 'C線 9座開出'}, {'time': '09:30', 'info': 'C線 9座開出'}, {'time': '10:30', 'info': 'C線 9座開出'}, {'time': '11:30', 'info': 'C線 9座開出'}, {'time': '14:30', 'info': 'C線 9座開出'}, {'time': '15:30', 'info': 'C線 9座開出'}, {'time': '16:30', 'info': 'C線 9座開出'}, {'time': '19:30', 'info': 'C線 9座開出'}, {'time': '20:30', 'info': 'C線 9座開出'}, {'time': '21:30', 'info': 'C線 9座開出'}, {'time': '22:30', 'info': 'C線 9座開出'}]}
}

# Global variable to store holiday data
holiday_data = {}

# Async function to fetch and update holiday data
async def fetch_and_update_holiday_data():
    url = 'https://www.1823.gov.hk/common/ical/en.json'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                text = await response.text(encoding='utf-8-sig')
                new_data = json.loads(text)

                # Update the global holiday data
                holiday_data.clear()
                holiday_data.update(new_data)

# Refresh and update holiday data
async def check_and_refresh_holiday_data(hass):
    # Determine the last date in the holiday data
    if not holiday_data or 'vcalendar' not in holiday_data or not holiday_data['vcalendar'][0]['vevent']:
        return  # Can't determine the last date, so don't do anything

    last_event = holiday_data['vcalendar'][0]['vevent'][-1]
    last_holiday_date = datetime.strptime(last_event['dtstart'][0], '%Y%m%d').date()

    # Check if the current date is the same or later than the last holiday date
    current_date = datetime.now(timezone).date()
    if current_date >= last_holiday_date:
        # Fetch new data as the current date is the same or later than the last holiday
        await fetch_and_update_holiday_data()

# Function to check if a given date is a holiday or a weekend (Saturday or Sunday)
# This remains a synchronous function
def is_holiday_or_weekend():
    now = datetime.now(timezone)
    date = now.date()
    # Check if the day is Saturday or Sunday
    if date.weekday() == 5 or date.weekday() == 6:  # 5 is Saturday, 6 is Sunday
        return True
    # Check against holiday data
    for event in holiday_data['vcalendar'][0]['vevent']:
        start_date = datetime.strptime(event['dtstart'][0], '%Y%m%d').date()
        end_date = datetime.strptime(event['dtend'][0], '%Y%m%d').date()
        if start_date <= date < end_date:  # Check if date falls within the holiday range
            return True
    return False

# Function to get the next 'n' schedules based on the current time
def get_next_schedules(route, is_holiday, current_time, n):
    # Access the schedule data directly using the route and holiday status
    schedule_data = bus_schedule.get((route, is_holiday), {}).get('schedule', [])
    # Filter the future schedules based on the current time
    future_schedules = [sched for sched in schedule_data if sched['time'] > current_time]
    # Return the first 'n' future schedules
    return future_schedules[:n]

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    # Fetch and update holiday data at startup
    await fetch_and_update_holiday_data()
    # Schedule daily check for new holiday data
    hass.helpers.event.async_track_time_change(
        lambda now: check_and_refresh_holiday_data(hass),
        hour=0, minute=0, second=0
    )
    """Set up the sensor platform."""
    sensors = []
    # Retrieve unique routes from bus_schedule
    unique_routes = set(route for route, _ in bus_schedule.keys())
    # Add title sensors for each unique route
    for route in unique_routes:
        sensors.append(BusTitleSensor(route, hass))
        # Create 4 schedule sensors for each route
        for i in range(4):
            sensors.append(BusScheduleSensor(route, i, hass))
    async_add_entities(sensors, True)  # The True at the end triggers an update upon entity addition

class BusTitleSensor(SensorEntity):
    """Sensor for displaying shuttle title with holiday information."""

    def __init__(self, route: str, hass):
        """Initialize the sensor."""
        self.route = route
        self.hass = hass
        self._name = None
        self.entity_id = f"sensor.shuttlebus_route_{self.route}_title"
        self.update()

    @property
    def name(self):
        """Return the name for this sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return "班次"

    def should_poll(self):
        """Sensor should not be polled."""
        return False

    def update(self):
        """Update the sensor."""
        # Access the description directly using the route and holiday status
        schedule_key = (self.route, is_holiday_or_weekend())
        self._name = bus_schedule.get(schedule_key, {}).get('description', '')
        self.schedule_next_update()

    def schedule_next_update(self):
        """Schedule the next update at midnight."""
        now = datetime.now(timezone)
        next_midnight = timezone.localize(datetime.combine(now.date() + timedelta(days=1), datetime.min.time()))
        delay = (next_midnight - now).total_seconds()
        self.hass.helpers.event.async_call_later(delay, lambda _: self.async_schedule_update_ha_state(True))

class BusScheduleSensor(Entity):
    def __init__(self, route: str, index: int, hass):
        """Initialize the sensor."""
        self.route = route
        self.index = index
        self.hass = hass
        self._name = '⠀'
        self._state = '⠀'
        self._icon = '⠀'
        self._attributes = {}
        self.entity_id = f"sensor.shuttlebus_route_{self.route}_{self.index + 1}"
        self.update()

    @property
    def name(self):
        """Return the name for this sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return self._icon

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    def should_poll(self):
        """Sensor should not be polled."""
        return False

    def update(self):
        """Fetch new state data for the sensor."""
        now = datetime.now(timezone)
        current_time = now.strftime('%H:%M')
        is_holiday = is_holiday_or_weekend()

        # Fetch the next schedules
        next_schedules = get_next_schedules(self.route, is_holiday, current_time, 4)

        if len(next_schedules) > self.index:
            schedule_item = next_schedules[self.index]
            schedule_time_str = schedule_item['time']
            schedule_info = schedule_item['info']

            schedule_time_naive = datetime.strptime(schedule_time_str, '%H:%M')
            schedule_time = now.replace(hour=schedule_time_naive.hour, minute=schedule_time_naive.minute, second=0, microsecond=0)

            # If the schedule time is earlier than now, assume it's for the next day
            if schedule_time < now:
                schedule_time += timedelta(days=1)

            # Calculate the time difference
            time_diff = schedule_time - now
            seconds_diff = time_diff.total_seconds()

            # Update attributes
            self._name = schedule_info
            self._icon = "mdi:bus"
            self._attributes['departure_time'] = schedule_time_str
            self._attributes['route'] = self.route
            self._attributes['is_holiday'] = is_holiday

            # Format the state display
            if seconds_diff <= 0:
                self._state = '已開出'
            elif seconds_diff <= 60:  # Less than 1 minute
                self._state = "<1分鐘"
            elif seconds_diff <= 3600:  # Less than 1 hour
                self._state = f"{int(seconds_diff // 60)}分鐘"
            else:  # Longer than 1 hour
                hours = int(seconds_diff // 3600)
                minutes = int((seconds_diff % 3600) // 60)
                self._state = f"{hours}:{minutes:02}小時"
        else:
            # No more schedules for the day
            self._name = '⠀'
            self._state = '⠀'
            self._icon = '⠀'
            self._attributes = {}

        # Schedule the next update
        self.schedule_next_update()

    def schedule_next_update(self):
        """Schedule the next update at the start of the next minute."""
        now = datetime.now(timezone)
        next_minute = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
        delay = (next_minute - now).total_seconds()
        # Use Home Assistant's event loop to schedule the next update
        self.hass.helpers.event.async_call_later(delay, lambda _: self.async_schedule_update_ha_state(True))