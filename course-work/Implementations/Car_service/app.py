from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:acerpredator@localhost/autoservice'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'acerpredator'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

db = SQLAlchemy(app)
jwt = JWTManager(app)

# Database Models
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    vin = db.Column(db.String(17), unique=True, nullable=False)
    client = db.relationship('Client', backref=db.backref('cars', lazy=True))

class Repair(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    repair_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.String(255), nullable=False)
    cost = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    car = db.relationship('Car', backref=db.backref('repairs', lazy=True))

# Create the database
with app.app_context():
    db.create_all()


# Authentication
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    if username == 'admin' and password == 'password':  # Replace with real authentication
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token)
    return jsonify({'msg': 'Bad credentials'}), 401

# CRUD Operations for Clients
@app.route('/clients', methods=['GET'])
@jwt_required()
def get_clients():
    clients = Client.query.all()
    return jsonify([{'id': c.id, 'first_name': c.first_name, 'last_name': c.last_name, 'phone_number': c.phone_number, 'email': c.email} for c in clients])

@app.route('/clients', methods=['POST'])
@jwt_required()
def create_client():
    data = request.json
    new_client = Client(
        first_name=data['first_name'],
        last_name=data['last_name'],
        phone_number=data['phone_number'],
        email=data['email']
    )
    db.session.add(new_client)
    db.session.commit()
    return jsonify({'msg': 'Client created successfully'}), 201

@app.route('/clients/search', methods=['GET'])
@jwt_required()
def search_clients():
    phone = request.args.get('phone')
    clients = Client.query.filter(Client.phone_number == phone).all()
    return jsonify([{'id': c.id, 'first_name': c.first_name, 'last_name': c.last_name, 'phone_number': c.phone_number, 'email': c.email} for c in clients])

@app.route('/clients/<int:id>', methods=['PUT'])
@jwt_required()
def update_client(id):
    client = Client.query.get_or_404(id)
    data = request.json
    client.first_name = data.get('first_name', client.first_name)
    client.last_name = data.get('last_name', client.last_name)
    client.phone_number = data.get('phone_number', client.phone_number)
    client.email = data.get('email', client.email)
    db.session.commit()
    return jsonify({'msg': 'Client updated successfully'})

@app.route('/clients/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_client(id):
    client = Client.query.get_or_404(id)
    db.session.delete(client)
    db.session.commit()
    return jsonify({'msg': 'Client deleted successfully'})


# CRUD Operations for Cars
@app.route('/cars', methods=['GET'])
@jwt_required()
def get_cars():
    cars = Car.query.all()
    return jsonify([{'id': c.id, 'make': c.make, 'model': c.model, 'year': c.year, 'vin': c.vin, 'client_id': c.client_id} for c in cars])

@app.route('/cars/search', methods=['GET'])
@jwt_required()
def search_cars():
    vin = request.args.get('vin')
    cars = Car.query.filter(Car.vin == vin).all()
    return jsonify([{'id': c.id, 'make': c.make, 'model': c.model, 'year': c.year, 'vin': c.vin, 'client_id': c.client_id} for c in cars])

@app.route('/cars', methods=['POST'])
@jwt_required()
def create_car():
    data = request.json
    new_car = Car(
        client_id=data['client_id'],
        make=data['make'],
        model=data['model'],
        year=data['year'],
        vin=data['vin']
    )
    db.session.add(new_car)
    db.session.commit()
    return jsonify({'msg': 'Car created successfully'}), 201

@app.route('/cars/<int:id>', methods=['PUT'])
@jwt_required()
def update_car(id):
    car = Car.query.get_or_404(id)
    data = request.json
    car.make = data.get('make', car.make)
    car.model = data.get('model', car.model)
    car.year = data.get('year', car.year)
    car.vin = data.get('vin', car.vin)
    db.session.commit()
    return jsonify({'msg': 'Car updated successfully'})

@app.route('/cars/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_car(id):
    car = Car.query.get_or_404(id)
    db.session.delete(car)
    db.session.commit()
    return jsonify({'msg': 'Car deleted successfully'})

# CRUD Operations for Repairs
@app.route('/repairs', methods=['GET'])
@jwt_required()
def get_repairs():
    repairs = Repair.query.all()
    return jsonify([{'id': r.id, 'car_id': r.car_id, 'repair_date': r.repair_date, 'description': r.description, 'cost': str(r.cost), 'status': r.status} for r in repairs])

@app.route('/repairs/search', methods=['GET'])
@jwt_required()
def search_repairs():
    status = request.args.get('status')
    repairs = Repair.query.filter(Repair.status == status).all()
    return jsonify([{'id': r.id, 'car_id': r.car_id, 'repair_date': r.repair_date, 'description': r.description, 'cost': str(r.cost), 'status': r.status} for r in repairs])

@app.route('/repairs', methods=['POST'])
@jwt_required()
def create_repair():
    data = request.json
    new_repair = Repair(
        car_id=data['car_id'],
        repair_date=datetime.strptime(data['repair_date'], '%Y-%m-%d %H:%M:%S'),
        description=data['description'],
        cost=data['cost'],
        status=data['status']
    )
    db.session.add(new_repair)
    db.session.commit()
    return jsonify({'msg': 'Repair created successfully'}), 201

@app.route('/repairs/<int:id>', methods=['PUT'])
@jwt_required()
def update_repair(id):
    repair = Repair.query.get_or_404(id)
    data = request.json
    repair.description = data.get('description', repair.description)
    repair.cost = data.get('cost', repair.cost)
    repair.status = data.get('status', repair.status)
    db.session.commit()
    return jsonify({'msg': 'Repair updated successfully'})

@app.route('/repairs/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_repair(id):
    repair = Repair.query.get_or_404(id)
    db.session.delete(repair)
    db.session.commit()
    return jsonify({'msg': 'Repair deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True)
