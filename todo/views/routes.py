from flask import Blueprint, jsonify
from flask import Blueprint, jsonify, request 
from todo.models import db 
from todo.models.todo import Todo 
from datetime import datetime, timedelta
from sqlalchemy import and_
 
api = Blueprint('api', __name__, url_prefix='/api/v1') 

TEST_ITEM = {
    "id": 1,
    "title": "Watch CSSE6400 Lecture",
    "description": "Watch the CSSE6400 lecture on ECHO360 for week 1",
    "completed": True,
    "deadline_at": "2023-02-27T00:00:00",
    "created_at": "2023-02-20T00:00:00",
    "updated_at": "2023-02-20T00:00:00"
}
 
@api.route('/health') 
def health():
    """Return a status of 'ok' if the server is running and listening to request"""
    return jsonify({"status": "ok"})


@api.route('/todos', methods=['GET']) 
def get_todos(): 
   result = [] 
   #TODO https://stackoverflow.com/questions/14845196/dynamically-constructing-filters-in-sqlalchemy
   query = Todo.query
   completed = request.args.get('completed')
   window = request.args.get('window')
   if completed is not None:
      completed = completed.lower() == 'true'
      query = query.filter_by(completed=completed)
   if window is not None:
      window = int(window)
      now = datetime.utcnow()
      query = query.filter(Todo.deadline_at <= now + timedelta(window))

   todos = query.all()
   for todo in todos: 
      result.append(todo.to_dict()) 
   return jsonify(result)

@api.route('/todos/<int:todo_id>', methods=['GET']) 
def get_todo(todo_id): 
   todo = Todo.query.get(todo_id) 
   if todo is None: 
      return jsonify({'error': 'Todo not found'}), 404 
   return jsonify(todo.to_dict())

@api.route('/todos', methods=['POST']) 
def create_todo(): 
   if 'title' not in request.json:
      return jsonify("error: missing title"), 400

   
   todo = Todo( 
      title=request.json.get('title'), 
      description=request.json.get('description'), 
      completed=request.json.get('completed', False), 
   ) 

   for elem in request.json:
      if elem not in todo.to_dict().keys():
         return jsonify("error: invalid field"), 400

   if 'deadline_at' in request.json: 
      todo.deadline_at = datetime.fromisoformat(request.json.get('deadline_at')) 
 
   # Adds a new record to the database or will update an existing record 
   db.session.add(todo) 
   # Commits the changes to the database, this must be called for the changes to be saved 
   db.session.commit() 
   return jsonify(todo.to_dict()), 201

@api.route('/todos/<int:todo_id>', methods=['PUT']) 
def update_todo(todo_id): 
   todo = Todo.query.get(todo_id) 
   if todo is None: 
      return jsonify({'error': 'Todo not found'}), 404 
 
   if 'id' in request.json and todo_id != request.json['id']:
      return jsonify("error: can't change the id >:("), 400

   for elem in request.json:
      if elem not in todo.to_dict().keys():
         return jsonify("error: invalid field"), 400

   todo.title = request.json.get('title', todo.title) 
   todo.description = request.json.get('description', todo.description) 
   todo.completed = request.json.get('completed', todo.completed) 
   todo.deadline_at = request.json.get('deadline_at', todo.deadline_at) 
   db.session.commit() 
 

   
   return jsonify(todo.to_dict())

@api.route('/todos/<int:todo_id>', methods=['DELETE']) 
def delete_todo(todo_id): 
   todo = Todo.query.get(todo_id) 
   if todo is None: 
      return jsonify({}), 200 
 
   db.session.delete(todo) 
   db.session.commit() 
   return jsonify(todo.to_dict()), 200
 
