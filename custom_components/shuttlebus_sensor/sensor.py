"""Platform for sensor integration."""
from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.event import call_later, async_track_time_change

from datetime import datetime, timedelta
import pytz
import aiohttp
import json
import os

# Global variable
bus_schedule = {}
holiday_data = {}
timezone = pytz.timezone('Asia/Hong_Kong')

# Async function to fetch and update bus schedule from web
async def fetch_and_update_bus_schedule_www():
    url = 'https://raw.githubusercontent.com/shing6326/hacs-the-regent-shuttle/master/custom_components/shuttlebus_sensor/data/bus_schedule.json'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    text = await response.text(encoding='utf-8-sig')
                    loaded_dict = json.loads(text)
                    updated_schedule = {}

                    for key, value in loaded_dict.items():
                        try:
                            route, holiday_flag = key.split('_')
                            updated_schedule[(route, holiday_flag == 'True')] = value
                        except ValueError:
                            # Handle the error (e.g., log it, skip the item, etc.)
                            print(f"Invalid key format: {key}")

                    bus_schedule.clear()
                    bus_schedule.update(updated_schedule)
    except Exception as e:
        # Handle other exceptions (e.g., network errors, JSON parsing errors)
        print(f"Failed to fetch or update bus schedule: {e}")

# Async function to fetch and update holiday data from web
async def fetch_and_update_holiday_data_www():
    url = 'https://www.1823.gov.hk/common/ical/en.json'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    text = await response.text(encoding='utf-8-sig')
                    new_data = json.loads(text)
                    if 'vcalendar' in new_data and new_data['vcalendar'][0]['vevent']:
                        # Update the global holiday data
                        holiday_data.clear()
                        holiday_data.update(new_data)
                    else:
                        print("Invalid holiday data format received.")
                else:
                    print(f"Failed to fetch holiday data: HTTP Status {response.status}")
    except Exception as e:
        # Handle exceptions (e.g., network errors, JSON parsing errors)
        print(f"Failed to fetch or update holiday data: {e}")

# Async function to fetch and update bus schedule from file
async def fetch_and_update_bus_schedule_file():
    file_path = os.path.join(os.path.dirname(__file__), 'data/bus_schedule.json')
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            loaded_dict = json.load(file)
            bus_schedule.clear()
            bus_schedule.update({(key.split('_')[0], key.split('_')[1] == 'True'): value for key, value in loaded_dict.items()})
    except Exception as e:
        print(f"Error loading bus schedule from JSON file: {e}")

# Async function to fetch and update holiday data from file
async def fetch_and_update_holiday_data_file():
    file_path = os.path.join(os.path.dirname(__file__), 'data/en.json')
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            new_data = json.load(file)
            holiday_data.clear()
            holiday_data.update(new_data)
    except Exception as e:
        print(f"Error loading holiday data from JSON file: {e}")

async def fetch_and_update_bus_schedule():
    try:
        await fetch_and_update_bus_schedule_www()
    except Exception as e:
        print(f"Failed to fetch bus schedule from the web: {e}")

async def fetch_and_update_holiday_data():
    try:
        await fetch_and_update_holiday_data_www()
    except Exception as e:
        print(f"Failed to fetch holiday data from the web: {e}")

# Refresh and update holiday data
async def check_and_refresh_holiday_data():
    # Determine the last date in the holiday data
    if not holiday_data or 'vcalendar' not in holiday_data or not holiday_data['vcalendar'][0]['vevent']:
        await fetch_and_update_holiday_data()  # Can't determine the last date, force refresh
    else:
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
    # Fetch and update bus schedule data at startup
    await fetch_and_update_bus_schedule()
    # Schedule daily check for new bus schedule data
    async_track_time_change(
        hass,
        lambda now: hass.create_task(fetch_and_update_bus_schedule()),
        hour=23, minute=55, second=0
    )
    # Fetch and update holiday data at startup
    await fetch_and_update_holiday_data()
    # Schedule daily check for new holiday data
    async_track_time_change(
        hass,
        lambda now: hass.create_task(check_and_refresh_holiday_data()),
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
        # Schedule the next update at midnight.
        now = datetime.now(timezone)
        next_midnight = timezone.localize(datetime.combine(now.date() + timedelta(days=1), datetime.min.time()))
        delay = (next_midnight - now).total_seconds()
        call_later(self.hass, delay, lambda _: self.schedule_update_ha_state(True))

class BusScheduleSensor(SensorEntity):
    """Sensor for displaying shuttle bus schedule details"""
    def __init__(self, route: str, index: int, hass):
        """Initialize the sensor."""
        self.route = route
        self.index = index
        self.hass = hass
        self._name = '⠀'
        self._state = '⠀'
        self._icon = "mdi:void"
        self._attributes = {}
        self.entity_id = f"sensor.shuttlebus_route_{self.route}_{self.index + 1}"

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
            self._attributes = {}
            if self.index == 0:
                self._name = "尾班車已開出"
                self._state = '⠀'
                self._icon = "mdi:information-outline"
            else:
                self._name = '⠀'
                self._state = '⠀'
                self._icon = "mdi:void"

        # Schedule the next update at the start of the next minute.
        now = datetime.now(timezone)
        next_minute = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
        delay = (next_minute - now).total_seconds()
        call_later(self.hass, delay, lambda _: self.schedule_update_ha_state(True))
