from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional
import threading
import h5py
import uuid
import os

@dataclass
class ActuatorEvent:
    id: str
    actuator_name: str
    state: str
    offset: timedelta  # Time offset from the start of the schedule

@dataclass
class Schedule:
    name: str
    schedule_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    start_time: Optional[datetime] = None  # The time when the schedule starts
    events: List[ActuatorEvent] = field(default_factory=list)
    created: Optional[datetime] = field(default_factory=lambda: datetime.now())
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)

    def add_event(self, actuator_name: str, state: str, offset: timedelta):
        with self._lock:
            event_id = str(uuid.uuid4())
            event = ActuatorEvent(id=event_id, actuator_name=actuator_name, state=state, offset=offset)
            self.events.append(event)
            print(f"Event added: {event}")

    def remove_event(self, event_id: str):
        with self._lock:
            original_count = len(self.events)
            self.events = [event for event in self.events if event.id != event_id]
            if len(self.events) < original_count:
                print(f"Event removed with ID {event_id}")
            else:
                print(f"No event found with ID {event_id}")

    def update_event(self, event_id: str, new_offset: Optional[timedelta] = None, new_state: Optional[str] = None):
        with self._lock:
            found = False
            for event in self.events:
                if event.id == event_id:
                    if new_offset:
                        event.offset = new_offset
                    if new_state:
                        event.state = new_state
                    found = True
                    print(f"Event updated: {event}")
                    break
            if not found:
                print(f"No event found with ID {event_id}")

    def get_events(self) -> List[ActuatorEvent]:
        with self._lock:
            return list(self.events)

    def get_events_for_actuator(self, actuator_name: str) -> List[ActuatorEvent]:
        with self._lock:
            return [event for event in self.events if event.actuator_name == actuator_name]

    def set_start_time(self, start_time: datetime):
        with self._lock:
            self.start_time = start_time

    def get_absolute_time(self, event: ActuatorEvent) -> Optional[datetime]:
        if self.start_time:
            return self.start_time + event.offset
        return None

    def save_to_file(self, filename: str):
        with self._lock:
            save_path = "../measurements/"
            if not os.path.exists(save_path):
                os.makedirs(save_path)
                print("Folder {save_path} created!")
            with h5py.File(os.path.join(save_path,filename), 'w') as f:
                f.attrs['name'] = self.name
                f.attrs['schedule_id'] = self.schedule_id
                f.attrs['start_time'] = self.start_time.isoformat() if self.start_time else ""
                f.attrs['created'] = self.created.isoformat() if self.created else ""
                events_group = f.create_group('events')
                events_group.attrs['description'] = "The list of all events (event is when the actuator changes the state).\
                                                        Field 'offset' represents the time in seconds from schedule 'start_time'\
                                                        to the actuator state change."
                for i, event in enumerate(self.events):
                    event_group = events_group.create_group(str(i))
                    event_group.attrs['id'] = event.id
                    event_group.attrs['actuator_name'] = event.actuator_name
                    event_group.attrs['state'] = event.state
                    event_group.attrs['offset'] = event.offset.total_seconds()  # Store offset in seconds

    @classmethod
    def load_from_file(cls, filename: str) -> 'Schedule':
        load_path = "../measurements/"
        with h5py.File(os.path.join(load_path,filename), 'r') as f:
            name = f.attrs['name']
            schedule_id = f.attrs['schedule_id']
            start_time_str = f.attrs['start_time']
            start_time = datetime.fromisoformat(start_time_str) if start_time_str else None
            created_time_str = f.attrs['created']
            created = datetime.fromisoformat(created_time_str) if created_time_str else None
            events = []
            for event_id in f['events']:
                event_group = f['events'][event_id]
                event = ActuatorEvent(
                    id=event_group.attrs['id'],
                    actuator_name=event_group.attrs['actuator_name'],
                    state=event_group.attrs['state'],
                    offset=timedelta(seconds=event_group.attrs['offset'])  # Convert seconds back to timedelta
                )
                events.append(event)
            return cls(name=name, schedule_id=schedule_id, start_time=start_time, events=events, created=created)

# # Usage example
# schedule = Schedule(name="Main Schedule")
# schedule.set_start_time(datetime(2024, 7, 30, 15, 0))
# schedule.add_event("actuator1", "on", timedelta(hours=1))
# schedule.add_event("actuator1", "off", timedelta(hours=2, minutes=12, seconds=45))
# schedule.add_event("actuator1", "on", timedelta(hours=5, minutes=15, seconds=23))
# schedule.add_event("actuator1", "off", timedelta(hours=12, minutes=44, seconds=14))
# # Save the schedule to a file
# schedule.save_to_file('schedule.h5')

# # Load the schedule from a file
# loaded_schedule = Schedule.load_from_file('schedule.h5')
# print(f"Loaded Schedule ID: {loaded_schedule.schedule_id}")
# print(f"Schedule Start Time: {loaded_schedule.start_time}")
# for event in loaded_schedule.get_events():
#     abs_time = loaded_schedule.get_absolute_time(event)
#     print(f"Loaded Event: {event}, Absolute Time: {abs_time}")

# # Add two more events
# schedule.add_event("actuator1", "on", timedelta(hours=3))
# schedule.add_event("actuator1", "off", timedelta(hours=51, minutes=1, seconds=7))

# # Save the schedule to a file
# schedule.save_to_file('schedule.h5')

# # Load the schedule from a file
# loaded_schedule = Schedule.load_from_file('schedule.h5')
# print(f"Loaded Schedule ID: {loaded_schedule.schedule_id}")
# print(f"Schedule Start Time: {loaded_schedule.start_time}")
# for event in loaded_schedule.get_events():
#     abs_time = loaded_schedule.get_absolute_time(event)
#     print(f"Loaded Event: {event}, Absolute Time: {abs_time}")
