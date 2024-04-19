from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user as jwt_current_user, set_access_cookies

from.index import index_views

from App.controllers import (
    create_user,
    get_all_users,
    get_all_users_json,
    jwt_required,
    login,
    get_user_by_username
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
    flash(f"User {username} created!")

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