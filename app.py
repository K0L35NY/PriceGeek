from flask import Flask, render_template, request, jsonify, send_file
import logging
import pandas as pd
import os
import ml_model

app = Flask(__name__)

# Set Flask logging level
logging.basicConfig(level=logging.INFO)

# Configure logging for specific libraries to suppress debug logs
logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.getLogger('graphviz').setLevel(logging.WARNING)

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
    logging.info(f"Fetching models for car make: {car_make}")
    models = get_car_models(car_make)
    logging.info(f"Found models: {models}")
    return jsonify(models)

@app.route('/get_car_generations', methods=['POST'])
def fetch_car_generations():
    car_make = request.json.get('car_make')
    car_model = request.json.get('car_model')
    logging.info(f"Fetching generations for car make: {car_make}, model: {car_model}")
    generations = get_car_generations(car_make, car_model)
    logging.info(f"Found generations: {generations}")
    return jsonify(generations)

@app.route('/scrape_auctions', methods=['POST'])
def scrape_auctions_route():
    car_make = request.json.get('car_make')
    car_model = request.json.get('car_model')
    generation = request.json.get('generation')
    logging.info(f"Scraping auctions for car make: {car_make}, model: {car_model}, generation: {generation}")

    url = generate_url(car_make, car_model, generation)
    logging.info(f"Generated URL: {url}")

    auctions = scrape_auctions(url)
    logging.info(f"Scraped auctions: {auctions}")

    if not auctions:
        return jsonify({'error': 'No auction data found'}), 404

    # Save auctions to CSV
    df = pd.DataFrame(auctions)
    csv_filename = 'scraped_auctions.csv'
    df.to_csv(csv_filename, index=False)

    # Preprocess the data and train the model
    df_preprocessed = ml_model.preprocess_data(csv_filename)
    mae, rmse, r2 = ml_model.train_model(df_preprocessed)

    return jsonify({'message': 'Scraping and training completed', 'csv_filename': csv_filename, 'mae': mae, 'rmse': rmse, 'r2': r2})

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)

        # Preprocess the data and train the model
        df_preprocessed = ml_model.preprocess_data(file_path)
        mae, rmse, r2 = ml_model.train_model(df_preprocessed)

        return jsonify({'message': 'File uploaded and training completed', 'mae': mae, 'rmse': rmse, 'r2': r2})

@app.route('/download_csv')
def download_csv():
    csv_filename = request.args.get('filename')
    if csv_filename and os.path.exists(csv_filename):
        return send_file(csv_filename, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404

@app.route('/predict_price', methods=['POST'])
def predict_price():
    data = request.json
    engine_size = float(data.get('engine_size'))
    horsepower = float(data.get('horsepower'))
    mileage = float(data.get('mileage'))
    gearbox = int(data.get('gearbox'))
    fuel_type = int(data.get('fuel_type'))
    production_year = int(data.get('production_year'))

    model = ml_model.load_model()
    predicted_price = ml_model.predict(model, engine_size, horsepower, mileage, gearbox, fuel_type, production_year)

    return jsonify({'predicted_price': predicted_price})


if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True, port=8080)
