from flask import request, render_template, redirect, url_for, Blueprint
from flask_login import current_user, login_required

from komorasoft.app import db
from komorasoft.blueprints.auto.models import Schedule, ActuatorEvent, timedelta, datetime, List, Optional

auto = Blueprint('auto', __name__, static_folder='static', template_folder='templates')


@auto.route('/')
def index():
    schedules = Schedule.query.all()
    events = ActuatorEvent.query.all()
    return render_template('auto/index.html', schedules=schedules, events=events)

@auto.route('/add_schedule', methods=['GET','POST'])
@login_required
def add_schedule(name: str="protokol", description: str="najboljši protokol", start_time: datetime=datetime(2024,8,5,6,0,33)) -> str:
        print("adding the schedule")
        schedule = Schedule(name=name,description=description,start_time=start_time)
        db.session.add(schedule)
        db.session.commit()
        return f"Event added: {schedule}"

@auto.route('/add_event', methods=['POST'])
@login_required
def add_event():
        data = request.get_json()
        actuator_name = data.get('actuator_name')
        state = data.get('state')
        offset = timedelta(seconds=int(data.get('offset')))
        schedule_id = data.get('schedule_id')
        existing_schedule = Schedule.query.filter_by(schedule_id=schedule_id).first()
        if existing_schedule:
            existing_event = ActuatorEvent.query.filter_by(actuator_name=actuator_name,offset=offset).first()
            if existing_event:
                return 'Event already exists!'
            else:
                print("Inserting a new event!")
                event = ActuatorEvent(actuator_name=actuator_name, state=state, offset=offset, schedule_id=existing_schedule.schedule_id)
                db.session.add(event)
                db.session.commit()
                return f"Event added: {event}"
        else:
            return f"No schedule with the ID: {schedule_id} found!"


@auto.route('/remove_event', methods=['POST'])
@login_required
def remove_event(self, event_id: str):
    event = ActuatorEvent.query.get(event_id)
    if event:
        db.session.delete(event)
        db.session.commit()
        return f"Event removed with ID {event_id}"
    else:
        return f"No event found with ID {event_id}"

@auto.route('/update_event', methods=['POST'])
@login_required
def update_event(self, event_id: str, new_offset: Optional[timedelta] = None, new_state: Optional[bool] = None):
    event = ActuatorEvent.query.get(event_id)
    if event:
        if new_offset:
            event.offset = new_offset
        if new_state:
            event.state = new_state
        db.session.commit()
        return f"Event updated: {event}"
    else:
        return f"No event found with ID {event_id}"

@auto.route('/get_events', methods=['POST'])
@login_required
def get_events(self) -> List[ActuatorEvent]:
    return self.events

@auto.route('/get_events_for_actuator', methods=['POST'])
@login_required
def get_events_for_actuator(self, actuator_name: str) -> List[ActuatorEvent]:
    return [event for event in self.events if event.actuator_name == actuator_name]

@auto.route('/set_start_time', methods=['POST'])
@login_required
def set_start_time(self, start_time: datetime):
    self.start_time = start_time
    db.session.commit()

@auto.route('/get_absolute_time', methods=['POST'])
@login_required
def get_absolute_time(self, event: ActuatorEvent) -> Optional[datetime]:
    if self.start_time:
        return self.start_time + event.offset
    return None

@auto.route('/update_name', methods=['POST'])
@login_required
def update_name(self, new_name: str):
    self.name = new_name
    db.session.commit()