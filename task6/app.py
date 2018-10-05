from flask import Flask, request, jsonify
from functools import wraps
from pymongo import MongoClient
from bson.json_util import dumps

app = Flask(__name__)

myclient = MongoClient("mongodb://localhost:27017/")
mydb = myclient["mydatabase"]
mycol = mydb["calculations"]
newcol = mydb["last_operations"]

@app.route('/')
def hello():
    return "Hello World"

def inverse(func):
    @wraps(func)

    def decorated_function(*args, **kwargs):

        try:
            op = request.get_json()["op"]

            if op == "+":
                op = "-"
            elif op == "-":
                op = "+"
            elif op == "/":
                op = "*"
            elif op == "*":
                op = "/"


            request.get_json()["op"] = op

            return func(*args, **kwargs)

        except:
            response = {"message": "Operation not supported"}
            return jsonify(response)

    return decorated_function


def arithmaticOperation(op1, op2, op):
    if op == "+":
        return op1 + op2
    if op == "-":
        return op1 - op2
    if op == "*":
        return op1 * op2
    if op == "/":
        return op1/op2

def allowedOperation(op):
    allowedOps = ["+", "-", "*", "/"]
    if op in allowedOps:
        return True
    return False

def getCollectionsFromDB(col):
    docs = []
    docs.append("total_records: {}" .format(col.count()))
    for x in col.find({},{ "_id": 0}):
        docs.append(x)
    return docs

def getLastOperations(op, limit):
    return newcol.find({"op": op},{"_id": 1, "op": 1, "op1": 1, "op2": 1, "result": 1}).sort('_id', -1).limit(limit)

def addIntoCollections(col, _list):
    if len(_list) > 0:
        for x in _list:
            col.insert_one(x)
        return True
    return False

def lastOperationsTask():

    add = list(getLastOperations("+", 4))
    sub = list(getLastOperations("-", 4))
    mul = list(getLastOperations("*", 4))
    div = list(getLastOperations("/", 4))

    x=newcol.delete_many({})
    print(x.deleted_count, " documents deleted.")

    addIntoCollections(newcol, add)
    addIntoCollections(newcol, sub)
    addIntoCollections(newcol, mul)
    addIntoCollections(newcol, div)

@app.route('/calc', methods=['POST'])
def calc():

    data = request.get_json()

    try:
        op1 = data["op1"]
        op2 = data["op2"]
        op = data["op"]
        

        if not allowedOperation(op):
            response = { 'status': 501,
                         'message': 'This operation ({}) is not supported by the API' .format(op)}
            return jsonify(response)

        result = arithmaticOperation(op1, op2, op)
        response = { 'status': 200,
                     'result': result }

        mydict = { "op": op, "op1": op1, "op2": op2, "result": result }
        x = mycol.insert_one(mydict)
        y = newcol.insert_one(mydict)

        print ("{} inserted successfully\n" .format(mydict))

        lastOperationsTask()

        return jsonify(response)

    except:
        response = { 'status': 500,
                     'message': 'Operator(op) or Operands(op1, op2) missing from the request' }
        return jsonify(response)

def flush(col):
    col.delete_many({})
    return True

@app.route('/calculations', methods=['GET'])
def calculations():
    return jsonify(getCollectionsFromDB(mycol))

@app.route('/lastops', methods=['GET'])
def lastops():
    return jsonify(getCollectionsFromDB(newcol))

@app.route('/flushdb', methods=['GET'])
def flushDB():
    flush(newcol)
    flush(mycol)

    return jsonify({"status" : 200, "message": "Databases flushed successfully"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
