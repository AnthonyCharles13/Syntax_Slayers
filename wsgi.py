import click, pytest, sys, csv
from flask import Flask
from flask.cli import with_appcontext, AppGroup
from App.models import *
from App.database import db, get_migrate
from App.main import create_app
from App.controllers import ( create_user, get_all_users_json, get_all_users )

# This commands file allow you to create convenient CLI commands for testing controllers

app = create_app()
migrate = get_migrate(app)

# This command creates and initializes the database
@app.cli.command("init", help="Creates and initializes the database")
def initialize():
    db.drop_all()
    db.create_all()
    csv_file = 'csv/megaGymDataset.csv'

    try:
        with open(csv_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Handle missing or empty fields
                for key, value in row.items():
                    if value == '':
                        row[key] = None
                
                # Create Exercise object and add to database
                exercise = Exercise(
                    title=row['Title'],
                    description=row['Desc'],
                    exercise_type=row['Type'],
                    bodypart=row['BodyPart'],
                    equipment=row['Equipment'],
                    level=row['Level'],
                    rating=float(row['Rating']) if row['Rating'] else None,
                    rating_desc=row['RatingDesc']
                )
                db.session.add(exercise)

        # Commit changes to the database
        db.session.commit()
        print("Exercises initialized successfully.")

    except Exception as e:
        # Rollback changes and print error message
        db.session.rollback()
        print("Error initializing exercises:", e)
    create_user('bob', 'bobpass')
    print('database intialized')

'''
User Commands
'''

# Commands can be organized using groups

# create a group, it would be the first argument of the comand
# eg : flask user <command>
user_cli = AppGroup('user', help='User object commands') 

# Then define the command and any parameters and annotate it with the group (@)
@user_cli.command("create", help="Creates a user")
@click.argument("username", default="rob")
@click.argument("password", default="robpass")
def create_user_command(username, password):
    create_user(username, password)
    print(f'{username} created!')

# this command will be : flask user create bob bobpass

@user_cli.command("list", help="Lists users in the database")
@click.argument("format", default="string")
def list_user_command(format):
    if format == 'string':
        print(get_all_users())
    else:
        print(get_all_users_json())

app.cli.add_command(user_cli) # add the group to the cli

'''
Test Commands
'''

test = AppGroup('test', help='Testing commands') 

@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "App"]))
    

app.cli.add_command(test)