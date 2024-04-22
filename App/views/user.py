from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required
from flask_jwt_extended import current_user, set_access_cookies

from.index import index_views
from App.models import Exercise, UserRoutine, db
from App.controllers import (
    create_user,
    get_all_users,
    get_all_users_json,
    jwt_required,
    login,
    get_user_by_username,
    get_all_exercises
)

user_views = Blueprint('user_views', __name__, template_folder='../templates')

@user_views.route('/users', methods=['GET'])
def get_user_page():
    users = get_all_users()
    return render_template('users.html', users=users)

@user_views.route('/users', methods=['POST'])
def create_user_action():
    data = request.form
    flash(f"User {data['username']} created!")
    create_user(data['username'], data['password'])
    return redirect(url_for('user_views.get_user_page'))


@user_views.route('/api/users', methods=['GET'])
def get_users_action():
    users = get_all_users_json()
    return jsonify(users)

@user_views.route('/api/users', methods=['POST'])
def create_user_endpoint():
    data = request.json
    user = create_user(data['username'], data['password'])
    return jsonify({'message': f"user {user.username} created with id {user.id}"})

@user_views.route('/static/users', methods=['GET'])
def static_user_page():
  return send_from_directory('static', 'static-user.html')




@user_views.route('/signup', methods=['GET'])
def get_signup_page():
    return render_template('signup.html')

@user_views.route('/signup', methods=['POST'])
def signup_user_action():
    data = request.form
    username = data['username']
    password = data['password']
    
    existing_user = get_user_by_username(username)
    if existing_user:
        flash('Username already taken')
        return redirect(url_for('user_views.get_signup_page'))

    create_user(username, password)
    flash('Account created!')

    token = login(username, password)

    if token:
        flash('Login Successful')
        response = redirect(url_for('index_views.get_index_page'))
        set_access_cookies(response, token)
        return response
    else:
        flash("Failed to log in after signup")
        return redirect(url_for('user_views.get_signup_page'))


@user_views.route('/exercises', methods=['GET'])
@user_views.route('/exercises/<int:exercise_id>', methods=['GET'])
@jwt_required()
def get_exercise_page(exercise_id=1):
    exercises = Exercise.query.all()
    user_routines = UserRoutine.get_user_routines(current_user.id)
    if exercise_id:
        selected_exercise=Exercise.query.filter_by(id=exercise_id).first()
    return render_template('exercises.html', exercises=exercises, selected_exercise=selected_exercise, user_routines=user_routines)

@user_views.route('/exercises/<int:selected_exercise_id>', methods=['POST'])
@jwt_required()
def add_exercise_to_routine(selected_exercise_id=None):
    routine_name = request.form.get('routine_name')

    if not routine_name or not selected_exercise_id:
        return jsonify({'error': 'Routine name or exercise ID not provided'}), 400

    user_id = current_user.id

    new_routine = UserRoutine(routine_name=routine_name, user_id=user_id, exercise_id=selected_exercise_id)
    db.session.add(new_routine)
    db.session.commit()
    flash("Exercise added to routine")
    return redirect(url_for('user_views.get_exercise_page'))


@user_views.route('/routines', methods=['GET'])
@user_views.route('/routines/<int:routine_id>', methods=['GET'])
@jwt_required()
def get_routines_page(routine_id=None):
    user_id = current_user.id
    user_routines = UserRoutine.get_user_routines(user_id)

    if routine_id is not None:
        selected_routine = UserRoutine.query.get(routine_id)
        if selected_routine and selected_routine.user_id == current_user.id:
            exercises = selected_routine.get_exercises()
            return render_template('routines.html', user_routines=user_routines, selected_routine=selected_routine, exercises=exercises)
        else:
            flash('You do not have permission to view this routine.', 'error')
            return redirect(url_for('user_views.get_routines_page'))
    else:
        return render_template('routines.html', user_routines=user_routines)

@user_views.route('/routines', methods=['POST'])
@jwt_required()
def create_routine():
    user_id = current_user.id
    routine_name = request.form.get('routine-name')

    if not routine_name:
        flash('Routine name cannot be empty.', 'error')
        return redirect(url_for('user_views.get_routines_page'))

    existing_routine = UserRoutine.query.filter_by(user_id=user_id, routine_name=routine_name).first()
    if existing_routine:
        flash('Routine name already exists. Please choose a different name.', 'error')
        return redirect(url_for('user_views.get_routines_page'))

    new_routine = UserRoutine(routine_name=routine_name, user_id=user_id)
    db.session.add(new_routine)
    db.session.commit()
    flash('New routine created successfully!', 'success')
    return redirect(url_for('user_views.get_routines_page'))


@user_views.route('/routines/<int:routine_id>/exercises/<int:exercise_id>', methods=['POST'])
@jwt_required()
def delete_exercise_from_routine(routine_id, exercise_id):
    user_id = current_user.id

    selected_routine = UserRoutine.query.filter_by(id=routine_id).first()
    if selected_routine:
        routine_name = selected_routine.routine_name
    else:
        flash('Routine not found', 'error')
        return redirect(url_for('user_views.get_routines_page'))
    
    user_routine = UserRoutine.query.filter_by(user_id=user_id, routine_name=routine_name, exercise_id=exercise_id).first()
    if user_routine:
        db.session.delete(user_routine)
        db.session.commit()
        flash('Exercise removed from routine successfully', 'success')
    else:
        flash('Exercise not found in the selected routine', 'error')
    
    return redirect(url_for('user_views.get_routines_page'))


@user_views.route('/routines/<int:routine_id>', methods=['POST'])
@jwt_required()
def delete_routine(routine_id):
    user_id = current_user.id
    selected_routine = UserRoutine.query.filter_by(id=routine_id).first()

    if selected_routine:
        routine_name = selected_routine.routine_name
    else:
        flash('Routine not found', 'error')
        return redirect(url_for('user_views.get_routines_page'))

    user_routines = UserRoutine.query.filter_by(user_id=user_id, routine_name=routine_name).all()
    if user_routines:
        for user_routine in user_routines:
            db.session.delete(user_routine)
        db.session.commit()
        flash('Routine deleted successfully', 'success')
    else:
        flash('Routine not found', 'error')
    
    return redirect(url_for('user_views.get_routines_page'))
