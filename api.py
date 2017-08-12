from flask import Flask, request
from flask_restful import Api, Resource, abort
from pymongo import MongoClient
from secrets import token_hex

errors = {
    'Conflict': {
        'message': "An employee with that name already exists.",
        'status': 409
    },
    'Forbidden': {
        'message': "The key you have specified is invalid or you are using a forbidden method",
        'status': 403
    },
    'Unauthorized': {
        'message': 'You are attempting to access this resource without authorization',
        'status': 401,
        'extra': 'Most likely, your IP is forbidden'
    }
}
# define with key as the name of an already defined werkzeug error

app = Flask(__name__)

api = Api(app, errors=errors, catch_all_404s=True)

# mongo client instance below
client =

# database object below
db =

post_template = ('name', 'department')


def parse(data, template):
    if all(key in data for key in template):
        pass
    else:
        abort(400)


def query(args,
          query={},
          single=False,
          sp_args=['include', 'exclude', 'regex', 'key'],
          ):
    _filter = {}
    for key in args:
        if key not in sp_args:
            query[key] = args[key]
        elif key == 'include':
            _filter.update({key: 1 for key in args['include'].split(",")})
        elif key == 'exclude':
            _filter.update({key: 0 for key in args['exclude'].split(",")})
        elif key == 'regex':
            field_regex = args['regex'].split(",")
            query[field_regex[0]] = {'$regex': field_regex[1]}

    f_filter = _filter if _filter else None
    if single is False:
        return list(db.employees.find(query, f_filter))
    elif single is True:
        return db.employees.find_one(query, f_filter)


class EmployeeList(Resource):
    def get(self):
        return query(request.args.to_dict())

    def put(self):
        data = request.get_json()

        parse(data, post_template)
        if db.employees.find(data).count() > 0:
            abort(409)
        else:
            data['_id'] = data['department'].upper() + token_hex(2)
            db.employees.insert(data)
            return {'Status': 'Success'}


class EmployeeProfile(Resource):
    def get(self, _id):
        return query(request.args.to_dict(), {'_id': _id}, True)

    def delete(self, _id):
        db.employees.remove({'_id': _id})
        return {'Status': 'Success'}


class DepartmentList(Resource):
    def get(self, department):
        return query(request.args.to_dict(), {'department': department})


class ToList(Resource):
    def get(self, field):
        return {field: db.employees.distinct(field)}


class ApiIndex(Resource):
    def get(self):
        return {'Endpoints':
                [str(rule) for rule in app.url_map.iter_rules()][:-1]
                }


api.add_resource(ApiIndex, '/api/v1/', endpoint='index')
api.add_resource(EmployeeList, '/api/v1/employees/', endpoint='list')
api.add_resource(
    EmployeeProfile, '/api/v1/employees/<_id>/', endpoint='profile')
api.add_resource(DepartmentList, '/api/v1/employees/department/<department>/',
                 endpoint='department_list')
api.add_resource(ToList, '/api/v1/employees/lists/<field>/',
                 endpoint='to_list')

if __name__ == "__main__":
    app.run()
