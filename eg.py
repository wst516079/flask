import json
from wtforms import Form, BooleanField, StringField, DateTimeField,FieldList, FormField,validators
from wtforms.validators import ValidationError
from flask import Flask, request, jsonify
from flask_mongoengine import MongoEngine
app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'flask',
    'host': 'localhost',
    'port': 27017
}
db = MongoEngine()
db.init_app(app)

class User(db.Document):
    name = db.StringField()
    email = db.StringField()
    def to_json(self):
        return {"name": self.name,
                "email": self.email}

class Book(db.Document):
    name = db.StringField()
    author = db.StringField()
    date = db.DateTimeField()
    def to_json(self):
        return {"name": self.name,
                "author": self.author,
                "date":self.date}

class Read(db.Document):
    user_name = db.ReferenceField(User, required=True)      #https://github.com/MongoEngine/mongoengine/issues/2027
    book_name = db.StringField()
    #book_name = db.ReferenceField(Book, required=True)
    def to_json(self):
        return {"user_name": self.user_name,
             "book_name": self.book_name}
class Hobby(db.EmbeddedDocument):
    name = db.StringField()
    time = db.StringField()
class Relative(db.EmbeddedDocument):
    father = db.StringField()
    mother = db.StringField()
    sister = db.StringField()
class SaveUser(db.Document):
    name = db.StringField()
    password = db.StringField()
    register_datetime = db.DateTimeField()
    hobbies = db.ListField(db.EmbeddedDocumentField(Hobby))
    relatives = db.EmbeddedDocumentField(Relative)
class validHobby(Form):
    name = StringField('name', [validators.Length(min=2, max=25,message='hobbyname')])
    time = StringField('time', [validators.Length(min=2, max=25,message='hobbytime')])
class validRelative(Form):
    father = StringField('father', [validators.Length(min=2, max=25,message='father')])
    mother = StringField('mother', [validators.Length(min=2, max=25,message='mother')])
    sister = StringField('sister', [validators.Length(min=2, max=25,message='sister')])
class validUser(Form):
    name = StringField('name', [validators.Length(min=1, max=25,message='name')])
    password = StringField('password', [validators.Length(min=1, max=7,message='password')])
    register_datetime = DateTimeField('register_datetime')
    hobbies = FieldList(FormField(validHobby))
    validRelative = FormField(validRelative)
@app.route('/', methods=['GET'])
def query_records():
    name = request.args.get('name')
    user = User.objects(name=name).first()
    if not user:
        return jsonify({'error': 'data not found'})
    else:
        return jsonify(user.to_json())

@app.route('/', methods=['PUT'])
def create_record():
    print(request.data)           #{"name":"d","email":"lawfeasdfm"}
    record = json.loads(request.data)
    user = User(name=record['name'],email=record['email'])
    user.save()
    return jsonify(user.to_json())

@app.route('/', methods=['POST'])
def update_record():
    record = json.loads(request.data)
    user = User.objects(name=record['name']).first()
    print(user)
    if not user:
        return jsonify({'error': 'data not found'})
    else:
        user.update(email=record['email'])
    return jsonify(user.to_json())

@app.route('/', methods=['DELETE'])
def delete_record():
    record = json.loads(request.data)
    user = User.objects(name=record['name']).first()
    if not user:
        return jsonify({'error': 'data not found'})
    else:
        user.delete()
    return jsonify(user.to_json())

@app.route('/book', methods=['PUT'])                 #添加书籍
def add_book():
    record = json.loads(request.data)
    book = Book(name=record['name'], author=record['author'], date=record['date'])
    book.save()
    return jsonify(book.to_json())

@app.route('/book', methods=['DELETE'])             #删除书籍
def delete_book():
    record = json.loads(request.data)
    book = Book.objects(name=record['name']).first()
    if not book:
        return jsonify({'error': 'data not found'})
    else:
        book.delete()
    return jsonify(book.to_json())

@app.route('/read', methods=['PUT'])              #读书功能
def read_book():
    record = json.loads(request.data)
    print(record)
    #user = User.objects(name=record['user_name'])
    user = User(name=record['user_name']).save()                 #user 必须save后才能用
    print(user)
    read = Read(user_name=user,book_name=record['book_name'])
    read.save()
    return jsonify(read.to_json())

@app.route('/readlist', methods=['GET'])          #查询user读的所有书
def readlist():
    user_name = request.args.get('user_name')
    print(user_name)
    #user = User.objects(name=user_name)
    user = User(name=user_name).save()      #改了这里《————————————
    print(user)
    test = list(User.objects(name=user_name))   #改了这里《————————————
    read = Read.objects().filter(user_name__in=test)   #双下划线用法http://www.xefan.com/archives/84069.html
    #read = Read.objects(user_name__in=user).order_by('book_name')
    #read = Read.objects(book_name="wstinserttest").order_by('user_name')
    #print(read)
    if not read:
        return jsonify({'error': 'data not found'})
    else:
        result = []
        for r in read:
            result.append(r.book_name)
        str = ','.join(result)
        return str

@app.route('/save', methods=['PUT'])
def save():
    record = json.loads(request.data)
    saveuser = SaveUser(name=record['name'], password=record['password'], register_datetime=record['register_datetime'],
             hobbies=record['hobbies'],relatives=record['relatives']).save()
    return jsonify(saveuser.to_json())


@app.route('/newUser', methods=['POST'])
def newUser():
    record = json.loads(request.data)
    validuser = validUser(name = record['name'],password=record['password'], register_datetime=record['register_datetime'],
                          hobbies =record['hobbies'],validRelative =record['relatives'])
    if validuser.validate():
        save()
        return "success"
    else:
        return jsonify(validuser.errors)
if __name__ == "__main__":
    app.run(debug=True)