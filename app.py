from flask import Flask, render_template, request, jsonify
from scraper import get_car_models
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

car_makes = [
    'BMW', 'Volkswagen', 'Audi', 'Ford', 'Mercedes-Benz', 'Opel', 'Toyota',
    'Skoda', 'Renault', 'Peugeot', 'Abarth', 'Acura', 'Aiways', 'Aixam',
    'Alfa Romeo', 'Alpine', 'Asia', 'Aston Martin', 'Austin', 'Autobianchi',
    'Baic', 'Bentley', 'BMW-ALPINA', 'Brilliance', 'Bugatti', 'Buick', 'BYD',
    'Cadillac', 'Casalini', 'Caterham', 'Cenntro', 'Changan', 'Chatenet',
    'Chevrolet', 'Chrysler', 'Citroën', 'Cupra', 'Dacia', 'Daewoo', 'Daihatsu',
    'DeLorean', 'DFM', 'DFSK', 'DKW', 'Dodge', 'Doosan', 'DR MOTOR',
    'DS Automobiles', 'e.GO', 'Elaris', 'FAW', 'Ferrari', 'Fiat', 'Fisker',
    'Gaz', 'Geely', 'Genesis', 'GMC', 'GWM', 'HiPhi', 'Honda', 'Hongqi',
    'Hummer', 'Hyundai', 'Ineos', 'Infiniti', 'Inny', 'Isuzu', 'Iveco', 'JAC',
    'Jaguar', 'Jeep', 'Jetour', 'Jinpeng', 'Kia', 'KTM', 'Lada', 'Lamborghini',
    'Lancia', 'Land Rover', 'Leapmotor', 'LEVC', 'Lexus', 'Ligier', 'Lincoln',
    'Lixiang', 'Lotus', 'LTI', 'Lucid', 'Lynk & Co', 'MAN', 'Maserati',
    'MAXIMUS', 'Maxus', 'Maybach', 'Mazda', 'McLaren', 'Mercury', 'MG',
    'Microcar', 'MINI', 'Mitsubishi', 'Morgan', 'NIO', 'Nissan', 'Nysa',
    'Oldsmobile', 'Omoda', 'Opel', 'Piaggio', 'Plymouth', 'Polestar', 'Polonez',
    'Pontiac', 'Porsche', 'RAM', 'Renault', 'Rolls-Royce', 'Rover', 'Saab',
    'Saturn', 'Seat', 'Seres', 'Shuanghuan', 'Skywell', 'Smart', 'SsangYong',
    'Subaru', 'Suzuki', 'Syrena', 'Tarpan', 'Tata', 'Tesla', 'Trabant', 'Triumph',
    'Uaz', 'Vauxhall', 'VELEX', 'Volkswagen', 'Volvo', 'Voyah', 'Warszawa',
    'Wartburg', 'Wołga', 'XPeng', 'Zaporożec', 'Zastava', 'ZEEKR', 'Żuk'
]

@app.route('/')
def home():
    return render_template('index.html', car_makes=car_makes)

@app.route('/get_car_models', methods=['POST'])
def fetch_car_models():
    car_make = request.json.get('car_make')
    logging.debug(f"Fetching models for car make: {car_make}")
    models = get_car_models(car_make)
    logging.debug(f"Found models: {models}")
    return jsonify(models)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
