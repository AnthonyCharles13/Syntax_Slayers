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

@user_views.route('/signup', methods=['GET'])
def get_signup_page():
    return render_template('signup.html')
'''
@user_views.route('/signup', methods=['POST'])
def signup_user_action():
    data = request.form
    flash(f"User {data['username']} created!")
    create_user(data['username'], data['password'])
    token = login(data['username'], data['password'])

    if not token:
        flash('Username already taken'), 401
        return redirect(url_for('user_views.get_signup_page'))
    else:
        flash('Login Successful')
        response = redirect(url_for('index_views.get_index_page'))
        set_access_cookies(response, token) 
        return response
'''

@user_views.route('/signup', methods=['POST'])
def signup_user_action():
    data = request.form
    username = data['username']
    password = data['password']
    
    # Check if the username already exists
    existing_user = get_user_by_username(username)
    if existing_user:
        flash('Username already taken')
        return redirect(url_for('user_views.get_signup_page'))

    # Create the new user
    create_user(username, password)
    flash('Account created!')

    # Log in the newly created user
    token = login(username, password)

    # Redirect the user based on login result
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

# Route to render the routines page
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
        # If no routine_id provided, render the page without a selected routine
        return render_template('routines.html', user_routines=user_routines)


# Route to handle creation of a new routine
@user_views.route('/routines', methods=['POST'])
@jwt_required()
def create_routine():
    user_id = current_user.id
    routine_name = request.form.get('routine-name')

    # Check if routine name is empty
    if not routine_name:
        flash('Routine name cannot be empty.', 'error')
        return redirect(url_for('user_views.get_routines_page'))

    # Check if routine with the same name already exists for the user
    existing_routine = UserRoutine.query.filter_by(user_id=user_id, routine_name=routine_name).first()
    if existing_routine:
        flash('Routine name already exists. Please choose a different name.', 'error')
        return redirect(url_for('user_views.get_routines_page'))

    # Create the new routine
    new_routine = UserRoutine(routine_name=routine_name, user_id=user_id)
    db.session.add(new_routine)
    db.session.commit()
    flash('New routine created successfully!', 'success')
    return redirect(url_for('user_views.get_routines_page'))
'''
# Route to delete a routine
@user_views.route('/routines/<int:routine_id>', methods=['DELETE'])
@jwt_required()
def delete_routine(routine_id):
    user_id = jwt_current_user.id
    routine_to_delete = UserRoutine.query.get(routine_id)

    # Check if the routine belongs to the current user
    if routine_to_delete and routine_to_delete.user_id == user_id:
        db.session.delete(routine_to_delete)
        db.session.commit()
        flash('Routine deleted successfully!', 'success')
    else:
        flash('You do not have permission to delete this routine.', 'error')

    return redirect(url_for('user_views.get_routines_page'))
'''
'''
# Route to add an exercise to a routine
@user_views.route('/routines/<int:routine_id>/add-exercise', methods=['POST'])
@jwt_required()
def add_exercise_to_routine(routine_id):
    user_id = jwt_current_user.id
    exercise_id = request.form.get('exercise_id')

    # Check if the exercise and routine belong to the current user
    routine = UserRoutine.query.get(routine_id)
    exercise = Exercise.query.get(exercise_id)
    if routine and exercise and routine.user_id == user_id:
        routine.add_exercise(exercise_id)
        flash('Exercise added to routine successfully!', 'success')
    else:
        flash('Failed to add exercise to routine.', 'error')

    return redirect(url_for('user_views.get_routines_page'))
'''

@user_views.route('/routines/<int:routine_id>/add-exercise', methods=['POST'])
@jwt_required()
def add_exercise_to_routine(routine_id):
    exercise_id = request.json.get('exercise_id')

    # Check if exercise and routine exist
    exercise = Exercise.query.get(exercise_id)
    routine = UserRoutine.query.get(routine_id)
    if not exercise or not routine:
        return jsonify({'error': 'Exercise or routine not found'}), 404

    # Check if routine belongs to current user
    if routine.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 401

    # Add exercise to routine
    if routine.add_exercise(exercise_id):
        db.session.commit()
        return jsonify({'message': 'Exercise added to routine successfully'}), 200
    else:
        return jsonify({'error': 'Failed to add exercise to routine'}), 500

# Route to delete a routine
@user_views.route('/routines/<string:routine_name>', methods=['POST'])
@jwt_required()
def delete_routine(routine_name):
    # Fetch all instances of the routine by name for the current user
    routines_to_delete = UserRoutine.query.filter_by(routine_name=routine_name, user_id=current_user.id).all()

    # Check if any routines were found
    if routines_to_delete:
        # Delete each instance of the routine
        for routine in routines_to_delete:
            db.session.delete(routine)
        db.session.commit()
        flash('Routine deleted successfully!', 'success')
    else:
        flash('You do not have any routines with this name.', 'error')

    return redirect(url_for('user_views.get_routines_page'))