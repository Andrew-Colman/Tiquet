from flask import jsonify, g, request, Blueprint
from middlewares.protected_route import protected_route
from models import Tasks, Lists
from uuid import uuid4
from database.db import db

task = Blueprint('task', __name__)


@task.route('/tasks/<task_id>', methods=['GET', 'DELETE'])
@protected_route
def task_root(task_id):
    user_id = g.user.get('id')
    method = request.method

    if method == 'GET':
        requested_task = Tasks.query.filter_by(id=task_id).first()
        
        if requested_task.user_id != user_id:
            return jsonify(msg="You can't perform this action."), 403

        response = {
            'uid': requested_task.uid,
            'id': requested_task.id,
            'title': requested_task.title,
            'createdAt': requested_task.createdAt,
            'description': requested_task.description,
        }
        return jsonify(response), 200
    elif method == 'DELETE':
        requested_task = Tasks.query.filter_by(id=task_id).first()

        if requested_task.user_id != user_id:
            return jsonify(msg="You can't perform this action."), 403

        db.session.delete(requested_task)
        db.session.commit()

        return jsonify(msg="Task deleted"), 200

@task.route('/tasks/<task_id>/update-list', methods=['PUT'])
@protected_route
def update_task_list(task_id):
    req_data = request.get_json()
    list_id = req_data.get('listId')
    user_id = g.user.get('id')

    if list_id == None or task_id == None:
        return jsonify(msg="Missing params"), 400

    requested_list = Lists.query.filter_by(id=list_id).first()

    if requested_list.user_id != user_id:
        return jsonify(msg="You can't perform this action."), 403

    requested_task = Tasks.query.filter_by(id=task_id).first()
    requested_task.list_id = list_id
    
    db.session.commit()

    return jsonify(msg="Task updated"), 200

@task.route('/tasks/<task_id>/update-description', methods=['PUT'])
@protected_route
def update_task_description(task_id):
    req_data = request.get_json()
    description = req_data.get('description')
    user_id = g.user.get('id')

    if description == None:
        return jsonify(msg="Missing param: description"), 400

    requested_task = Tasks.query.filter_by(id=task_id).first()

    if user_id != requested_task.user_id:
        return jsonify(msg="You can't perform this action."), 403
    elif requested_task.description == description:
        return jsonify(msg="New description can't be the same as the old one."), 400
    
    requested_task.description = description
    db.session.commit()

    return jsonify(msg="Task updated"), 200