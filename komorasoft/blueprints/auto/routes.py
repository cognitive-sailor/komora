from flask import request, jsonify, render_template, redirect, url_for, Blueprint
from flask_login import current_user, login_required
from komorasoft.app import db
from komorasoft.blueprints.auto.models import Schedule, ActuatorEvent
from datetime import datetime, timedelta
from typing import List, Optional

auto = Blueprint('auto', __name__, static_folder='static', template_folder='templates')

@auto.route('/')
def index():
    return render_template('auto/index.html')

@auto.route('/add_schedule', methods=['POST'])
@login_required
def add_schedule():
    try:
        data = request.get_json()
        name = data.get('name', 'protokol')
        description = data.get('description', 'najboljši protokol')
        start_time = datetime.fromisoformat(data.get('start_time', datetime.now().isoformat()))
    except:
        name = request.form.get('name')
        description = request.form.get('description')
        start_time = request.form.get('start_time')
        start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M')
        print(start_time)

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

    schedule = Schedule.query.filter(Schedule.schedule_id == schedule_id).first()
    schedule.schedule_name = name
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


@auto.route('/add_event', methods=['POST'])
@login_required
def add_event():
    data = request.get_json()
    print(data)
    actuator_name = data.get('actuator_name')
    state = data.get('state')
    offset = timedelta(seconds=int(data.get('offset')))
    schedule_id = data.get('schedule_id')

    existing_schedule = Schedule.query.filter_by(schedule_id=schedule_id).first()
    if existing_schedule:
        existing_event = ActuatorEvent.query.filter_by(actuator_name=actuator_name, offset=offset, schedule_id=schedule_id).first()
        if existing_event:
            print('Event is selected schedule already exists!')
            return jsonify({'message': 'Event is selected schedule already exists!'}), 400
        else:
            event = ActuatorEvent(actuator_name=actuator_name, state=state, offset=offset, schedule_id=schedule_id)
            db.session.add(event)
            db.session.commit()
            return jsonify({'message': f'Event added: {event.actuator_name}'}), 201
    else:
        return jsonify({'message': f'No schedule with the ID: {schedule_id} found!'}), 404

@auto.route('/remove_event/<event_id>', methods=['DELETE'])
@login_required
def remove_event(event_id: str):
    event = ActuatorEvent.query.get(event_id)
    if event:
        db.session.delete(event)
        db.session.commit()
        return jsonify({'message': f'Event removed with ID {event_id}'}), 200
    else:
        return jsonify({'message': f'No event found with ID {event_id}'}), 404

@auto.route('/edit_event/<event_id>', methods=['PUT'])
@login_required
def edit_event(event_id: str):
    data = request.get_json()
    event = ActuatorEvent.query.get(event_id)
    if event:
        if 'offset' in data:
            event.offset = timedelta(seconds=int(data['offset']))
        if 'state' in data:
            event.state = data['state']
        db.session.commit()
        return jsonify({'message': f'Event updated: {event.actuator_name}'}), 200
    else:
        return jsonify({'message': f'No event found with ID {event_id}'}), 404


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
