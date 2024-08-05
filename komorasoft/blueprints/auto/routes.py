from flask import request, jsonify, render_template, redirect, url_for, Blueprint
from flask_login import current_user, login_required
from komorasoft.app import db
from komorasoft.blueprints.auto.models import Schedule, ActuatorEvent
from komorasoft.blueprints.actuators.models import Actuator
from datetime import datetime, timedelta
from typing import List, Optional

auto = Blueprint('auto', __name__, static_folder='static', template_folder='templates')

@auto.route('/')
def index():
    return render_template('auto/index.html')

@auto.route('/add_schedule', methods=['POST'])
@login_required
def add_schedule():
    # try:
    #     data = request.get_json()
    #     name = data.get('name', 'protokol')
    #     description = data.get('description', 'najboljši protokol')
    #     start_time = datetime.fromisoformat(data.get('start_time', datetime.now().isoformat()))
    # except:
    name = request.form.get('name')
    description = request.form.get('description')
    start_time = request.form.get('start_time')
    start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M')
    existing_schedule = Schedule.query.filter_by(name=name).first()
    if existing_schedule:
        return render_template('auto/schedule_exists.html')
    else:
        schedule = Schedule(name=name, description=description, start_time=start_time)
        db.session.add(schedule)
        db.session.commit()
        return render_template('auto/index.html')

@auto.route('/edit_schedule', methods=['POST'])
@login_required
def edit_schedule():
    schedule_id = request.form.get('schedule_id')
    name = request.form.get('name')
    description = request.form.get('description')
    start_time = request.form.get('start_time')
    start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M')
    print(name,start_time)

    schedule = Schedule.query.filter(Schedule.schedule_id == schedule_id).first()
    schedule.name = name
    schedule.description = description
    schedule.start_time = start_time
    db.session.commit()
    return render_template('auto/index.html')

@auto.route('/remove_schedule', methods=['POST'])
@login_required
def remove_schedule():
    schedule_id = request.form.get('schedule_id')
    print(schedule_id)
    schedule = Schedule.query.filter_by(schedule_id=schedule_id).first()
    print(schedule)
    db.session.delete(schedule)
    db.session.commit()
    return render_template('auto/index.html')

@auto.route('/get_schedule/<schedule_id>', methods=['GET'])
def get_schedule(schedule_id):
    schedule = Schedule.query.filter_by(schedule_id=schedule_id).first()
    if schedule:
        return jsonify({
            'schedule_id': schedule.schedule_id,
            'name': schedule.name,
            'description': schedule.description,
            'start_time': schedule.start_time.isoformat()  # Use ISO format for datetime
        })
    return jsonify({'error': 'Schedule not found'}), 404


@auto.route('/add_event', methods=['POST'])
@login_required
def add_event():
    actuator_name = request.form.get('izbran_aktuator')
    state = True if request.form.get('status_aktuatorja')=="on" else False
    dnevi = request.form.get('dni')
    ure = request.form.get('ur')
    minute = request.form.get('minut')
    sekunde = request.form.get('sekund')
    offset = timedelta(days=int(dnevi),hours=int(ure),minutes=int(minute),seconds=int(sekunde))
    schedule_id = request.form.get('createEventScheduleId')

    existing_schedule = Schedule.query.filter_by(schedule_id=schedule_id).first() 
    existing_actuator = Actuator.query.filter_by(name=actuator_name).first() 
    if existing_schedule: # check if Schedule exists
        if existing_actuator: # check if Actuator exists
            existing_event = ActuatorEvent.query.filter_by(actuator_name=actuator_name, offset=offset, schedule_id=schedule_id).first() # check if event exists
            if existing_event:
                print('Event in the selected schedule already exists!')
                return render_template('/auto/event_exists.html')
            else:
                event = ActuatorEvent(actuator_name=actuator_name, state=state, offset=offset, schedule_id=schedule_id) # create a new event for this actuator and schedule
                db.session.add(event)
                db.session.commit()
                return render_template('/auto/index.html')
        else:
            return jsonify({'message': f'No actuator: {actuator_name} found!'}), 404
    else:
        return jsonify({'message': f'No schedule with the ID: {schedule_id} found!'}), 404

@auto.route('/remove_event', methods=['POST'])
@login_required
def remove_event():
    event_id = request.form.get('event_id')
    event = ActuatorEvent.query.filter_by(id=event_id).first()
    if event:
        db.session.delete(event)
        db.session.commit()
        return render_template('auto/index.html')
    else:
        return jsonify({'message': f'No event found with ID {event_id}'}), 404

@auto.route('/edit_event', methods=['POST'])
@login_required
def edit_event():
    event_id = request.form.get('editEventId')
    event = ActuatorEvent.query.filter_by(id=event_id).first()
    if event:
        actuator = request.form.get('izbran_aktuator')
        state = request.form.get('status_aktuatorja')
        print(state)
        state = True if request.form.get('status_aktuatorja') == "on" else False
        day = request.form.get('dniE')
        hour = request.form.get('urE')
        minute = request.form.get('minutE')
        second = request.form.get('sekundE')
        offset = timedelta(days=int(day),hours=int(hour),minutes=int(minute),seconds=int(second))
        event.actuator_name = actuator
        event.state = state
        event.offset = offset
        db.session.commit()
        return render_template('auto/index.html')
    else:
        return jsonify({'message': f'No event found with ID {event_id}'}), 404


@auto.route('/get_event/<eventId>', methods=['GET'])
def get_event(eventId):
    event = ActuatorEvent.query.filter_by(id=eventId).first()
    if event: # get total seconds
        days = event.offset.days # extract days
        additional_seconds = event.offset.seconds # extract the rest of the seconds
        hours = additional_seconds // 3600 # extract hours
        minutes = (additional_seconds % 3600) // 60
        seconds = additional_seconds % 60

        return jsonify({
            'id': event.id,
            'name': event.actuator_name,
            'offset': event.offset.total_seconds(),
            'state': event.state,
            'schedule_id': event.schedule_id,
            'days': days,
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds
        })
    return jsonify({'error': 'Schedule not found'}), 404


@auto.route('/get_schedules')
def get_schedules():
    schedules = Schedule.query.all()
    return jsonify([{
        'schedule_id': schedule.schedule_id,
        'name': schedule.name,
        'description': schedule.description,
        'start_time': schedule.start_time.isoformat()
    } for schedule in schedules]), 200

@auto.route('/get_events')
def get_events():
    events = ActuatorEvent.query.all()
    return jsonify([{
        'id': event.schedule_id,
        'event_id':event.id,
        'actuator_name': event.actuator_name,
        'state': event.state,
        'offset': event.offset.total_seconds()
    } for event in events]), 200

@auto.route('/get_actuator_events', methods=['GET'])
def get_actuator_events():
    def serialize_actuator_event(event, abs_time):
        return {
            'id': event.id,
            'actuator_name': event.actuator_name,
            'state': event.state,
            'offset': event.offset.total_seconds(),
            'schedule_id': event.schedule_id,
            'absolute_time': abs_time.strftime('%Y-%m-%d %H:%M:%S')  # Format the absolute time as a string
        }

    schedule_id = request.args.get('schedule_id')
    schedule = Schedule.query.filter_by(schedule_id=schedule_id).first()
    
    if not schedule:
        return jsonify({'error': 'Schedule not found'}), 404

    events = ActuatorEvent.query.filter_by(schedule_id=schedule_id).order_by(ActuatorEvent.offset.asc()).all()
    
    events_list = []
    for event in events:
        abs_time = schedule.start_time + event.offset
        events_list.append(serialize_actuator_event(event, abs_time))

    return jsonify(events_list)

@auto.route('/get_actuators', methods=['GET'])
def get_actuators():
    actuators = Actuator.query.all()  # Assuming Actuator is your model
    return jsonify([{'sid': actuator.sid, 'name': actuator.name} for actuator in actuators])


@auto.route('/test', methods=['POST'])
def test():
    print("testing")
    return "Test"
