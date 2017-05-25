from flask import Flask, request, redirect, make_response
from flask.ext.autodoc.autodoc import Autodoc
import json, re, sys, os

app = Flask(__name__)
auto = Autodoc(app)

@app.route('/', methods=['GET'])
@auto.doc()
def index():
    return redirect("documentation")

@app.route('/notes', methods=['GET','POST'])
@auto.doc()
def get_notes():
    '''
        Get all notes for a single user.
        Provide access token as URL parameter.
    '''
    token = request.args.get('token', '')
    if token == '': return make_response("Token Required", 401)
    if not valid_token(token): return make_response("Invalid Token",401)
    return make_response(contents_of_file('data/'+token),200,{'Content-Type':'application/json'})

@app.route('/notes/add', methods=['POST'])
@auto.doc()
def add_note():
    '''
        Add a note for a single user.
        id (int), note(string) as parameters
        Provide access token as URL parameter.
    '''
    token = request.args.get('token', '')
    id_num = request.args.get('id', '')
    note = request.args.get('note', '')
    if token == '': return make_response("Token Required", 401)
    if not valid_token(token): return make_response("Invalid Token",401)
    if id_num == '': return make_response('Id Required', 400)
    if note == '': return make_response('Note Required', 400)
    new_note = {'id':int(id_num), 'note':note}
    data = open('data/'+token, "r").read()
    notes = json.loads(data)
    notes.append(new_note)
    data = json.dumps(notes)
    write_to_file("data/"+token, data)
    return "Added note: " + str(id_num)

@app.route('/notes/delete/<int:to_delete>', methods=['DELETE'])
@auto.doc()
def delete_note(to_delete):
    '''
        Delete a note for a single user.
        Note id as argument (i.e .../delete/1?param=val...)
        Provide access token as URL parameter.
    '''
    token = request.args.get('token', '')
    if token == '': return make_response("Token Required", 401)
    if not valid_token(token): return make_response("Invalid Token",401)
    data = open('data/'+token, "r").read()
    notes = json.loads(data)
    notes = [note for note in notes if not note['id'] == to_delete]
    data = json.dumps(notes)
    write_to_file("data/"+token, data)
    return "Deleted note: " + str(to_delete)

@app.route('/token', methods=['GET'])
@auto.doc()
def getToken():
    '''
        Get access token for user.
        Provide username and password as URL parameters.
    '''
    username = request.args.get('username', '')
    password = request.args.get('password', '')
    if username == '': return make_response('Username required', 400)
    if password =='': return make_response('Password required', 400)
    if not valid_login(username, password): return make_response('Invalid credentials', 401)
    return token_for(username)


@app.route('/create_user', methods=['POST'])
@auto.doc()
def create_user():
    '''
        Create a user account.
        Provide username and password as URL parameters.
    '''
    if request.method == 'POST':
        username = request.args.get('username')
        password = request.args.get('password')
        if username == '': return 'Username required'
        if password == '': return 'Password required'
        # check valid username and pass
        if not valid_username_password(username):
            return ('Invalid username or password, can only contain letters and numbers and be less than 100 characters long',400, None)
        #check if h a c k e r m a n
        if username == 'hackerman': return "<img src='http://i2.kym-cdn.com/entries/icons/original/000/021/807/4d7.png'>"
        # check if user exists
        if user_exists(username):
            return ('User with that name already exists.' , 401, None)
        create_user(username, password)
        return 'User ' + username + ' created.'

@app.route('/documentation')
def documentation():
    return auto.html()

def valid_login(username, password):
    return password == open('users/' + username, 'r').read()

def valid_token(token):
        return os.path.exists('data/'+token)


def token_for(username):
    return open('tokens/'+username, 'r').read()

def valid_username_password(s):
    return re.match('^[A-Za-z0-9]*$', s) and len(s) > 0 and len(s) < 100


def user_exists(username):
    return os.path.exists('users/'+username)

def create_user(username, password):
    f = open('users/'+username, 'w')
    f.write(password)
    f.close()
    token = create_user_token(username)
    create_user_file(token)

def create_user_file(username):
    default_note = json.dumps([{'id': 0, 'note':'Welcome to the notes api, where you can store all your notes in a totally secure file on our server.'}])
    f = open('data/'+username, 'w')
    f.write(default_note)
    f.close()

def create_user_token(username):
    ord_str = ''.join([str(ord(c))+'-' for c in username])
    sum_ord = sum([ord(c) for c in username])
    token = ord_str + str(sum_ord)
    f = open('tokens/'+username, 'w')
    f.write(token)
    f.close()
    return token

def contents_of_file(filename):
    f = open(filename, 'r')
    d = f.read()
    f.close()
    return d

def write_to_file(filename, d):
    with open(filename, 'w') as f:
        f.write(d)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='5000')
