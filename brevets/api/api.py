# Streaming Service

from flask import Flask, request, abort
from flask_restful import Resource, Api

from passlib.hash import sha256_crypt as pwd_context

from itsdangerous import (TimedJSONWebSignatureSerializer \
                                  as Serializer, BadSignature, \
                                  SignatureExpired)

import csv
import os

from pymongo import MongoClient

client = MongoClient('mongodb://' + os.environ['MONGODB_HOSTNAME'], 27017)
db = client.brevetsdb

app = Flask(__name__)
api = Api(app)
app.secret_key = "SomeString"


def csv_form(topk, d):
    times = json_form(topk, d)
    csv_times = []
    csv_times.append(",".join(list(times[0].keys())))

    for item in times:
        csv_times.append(",".join(list(item.values())))

    return csv_times

def json_form(topk, d):
    times = []
    for item in db.vals.find({},{ "_id": 0}):
        times.append(item)

    if d:
        for item in times:
            del item[d]

    if topk > 0:
        return times[:topk]

    return times

def get_users():
        names = {}
        for user in db.users.find():
            names.update({user['username']: user['hashed']})

        #app.logger.debug(names.values())
        return names

def verify_password(password):
    password = pwd_context.using(salt=app.secret_key).encrypt(password)
    users = get_users()

    return password in users.values()


def gen_token(expiration=600):
    s = Serializer(app.secret_key, expires_in=expiration)
    #app.logger.debug("token set")
    return {'token': s.dumps(0).decode('utf8'), 'duration': expiration}

def verify_auth_token(token):
    s = Serializer(app.secret_key)
    try:
        data = s.loads(token)
    except SignatureExpired:
        return 0   # valid token, but expired
    except BadSignature:
        return 0    # invalid token

    app.logger.debug("token authorized")
    return 1



class Users(Resource):
    def get(self):
        return get_users()


class ClearUsers(Resource):
    def get(self):
        db.users.drop()

        return None

class Register(Resource):
    def get(self):
        username = request.args.get('username')
        hashed = request.args.get('hashed')

        db.users.insert_one({"username": username, "hashed": hashed})

        return {"username": username, "hashed": hashed}, 201

        pass

class Token(Resource):
    def get(self):
        password = request.args.get('password', default='')
        hashed = request.args.get('hashed', default='')

        if hashed in get_users().values():
            return gen_token()

        elif verify_password(password):
            return gen_token()

        else:
            abort(401)


class ListAll(Resource):
    def get(self):
        d=''
        k=-1
        token = request.args.get('token', default = '')
        if verify_auth_token(token):
            return json_form(k, d)

        else:
            abort(401)

class ListAll_Type(Resource):
    def get(self, dtype):
        d=''
        k = request.args.get('top', type=int, default=-1)
        token = request.args.get('token', default = '')
        if verify_auth_token(token):
            if dtype == 'csv':
                return csv_form(k, d)

            return json_form(k, d)
        else:
            abort(401)

class ListOpenOnly(Resource):
    def get(self):
        d='close'
        k=-1
        token = request.args.get('token', default = '')
        if verify_auth_token(token):
            return json_form(k, d)

        else:
            abort(401)

class ListOpenOnly_Type(Resource):
    def get(self, dtype):
        d='close'
        k = request.args.get('top', type=int, default=-1)
        token = request.args.get('token', default = '')
        if verify_auth_token(token):
            if dtype == 'csv':
                return csv_form(k, d)

            return json_form(k, d)
        else:
            abort(401)

class ListCloseOnly(Resource):
    def get(self):
        d='open'
        k=-1
        token = request.args.get('token', default = '')
        if verify_auth_token(token):
            return json_form(k, d)

        else:
            abort(401)

class ListCloseOnly_Type(Resource):
    def get(self, dtype):
        d='open'
        k = request.args.get('top', type=int, default=-1)
        token = request.args.get('token', default = '')
        if verify_auth_token(token):
            if dtype == 'csv':
                return csv_form(k, d)

            return json_form(k, d)
        else:
            abort(401)

#resources

api.add_resource(Users, '/users')
api.add_resource(ClearUsers, '/clearUsers')

api.add_resource(Register, '/register')
api.add_resource(Token, '/token')

api.add_resource(ListAll, '/listAll')
api.add_resource(ListAll_Type, '/listAll/<string:dtype>')

api.add_resource(ListOpenOnly, '/listOpenOnly')
api.add_resource(ListOpenOnly_Type, '/listOpenOnly/<string:dtype>')

api.add_resource(ListCloseOnly, '/listCloseOnly')
api.add_resource(ListCloseOnly_Type, '/listCloseOnly/<string:dtype>')

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
