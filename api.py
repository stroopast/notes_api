from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, marshal, abort

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)
api = Api(app)

class NoteModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f"Note(name = {self.title}, content = {self.content}, created_at = {self.created_at})"

note_args = reqparse.RequestParser()
note_args.add_argument('title', type=str, required=True, help="Title cannot be blank")
note_args.add_argument('content', type=str, required=True, help="Content cannot be blank")
note_args.add_argument('created_at', type=str, required=False)

noteFields = {
    'id':fields.Integer,
    'title':fields.String,
    'content':fields.String,
    'created_at':fields.DateTime,
}

class Notes(Resource):
    @marshal_with(noteFields)
    def get(self):
        notes = NoteModel.query.all()
        return notes
    
    @marshal_with(noteFields)
    def post(self):
        args = note_args.parse_args()
        note = NoteModel(title=args["title"], content=args["content"])
        db.session.add(note)
        db.session.commit()
        notes = NoteModel.query.all()
        return notes, 201

class Note(Resource):
    @marshal_with(noteFields)
    def get(self, id):
        note = NoteModel.query.filter_by(id=id).first()
        if not note:
            abort(404, message='Note not found')
        return note
    
    @marshal_with(noteFields)
    def patch(self, id):
        args = note_args.parse_args()
        note = NoteModel.query.filter_by(id=id).first()
        if not note:
            abort(404, message='Note not found')

        if args["title"]:
            note.title = args["title"]
        if args["content"]:
            note.content = args["content"]

        note.created_at = db.func.current_timestamp()
        db.session.commit()
        return note


    @marshal_with(noteFields)
    def delete(self, id):
        note = NoteModel.query.filter_by(id=id).first()
        if not note:
            abort(404, message='Note not found')
        db.session.delete(note)
        db.session.commit()
        
        return note, 200

    

api.add_resource(Notes, '/api/notes/')
api.add_resource(Note, '/api/notes/<int:id>')

@app.route('/')
def home():
    return '<h1> Flask REST API </h1>'

if __name__ == '__main__':
    app.run(debug=True)