from flask import Flask, render_template, request, jsonify, send_file, session
import pandas as pd
import numpy as np
import os
import logging
from scraper import get_car_models, get_car_generations, generate_url, scrape_auctions
import ml_model

app = Flask(__name__)
app.secret_key = '1234'

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

    # Save data to CSV
    csv_filename = os.path.join('uploads', 'scraped_auctions.csv')
    df = pd.DataFrame(auctions)
    df.to_csv(csv_filename, index=False)
    session['data_source'] = csv_filename  # Store CSV path in session

    print_unique_values(df)  # Assuming this function only prints values and doesn't affect data

    # Process and train model
    df_preprocessed = ml_model.preprocess_data(csv_filename)
    mae, rmse, r2 = ml_model.train_model(df_preprocessed)

    return jsonify({
        'message': 'Scraping and training completed',
        'csv_filename': csv_filename,
        'mae': mae,
        'rmse': rmse,
        'r2': r2
    })

def print_unique_values(df):
    # Print unique fuel types
    unique_fuel_types = np.sort(df['fuel_type'].dropna().unique())
    print("Unique Fuel Types:", unique_fuel_types)

    # For each fuel type, print unique engine sizes that appear more than once
    for fuel_type in unique_fuel_types:
        fuel_type_mask = df['fuel_type'] == fuel_type
        engine_sizes = df.loc[fuel_type_mask, 'engine_size'].dropna()
        engine_size_counts = engine_sizes.value_counts()
        unique_engine_sizes = engine_size_counts[engine_size_counts > 1].index.sort_values()
        print(f"Fuel Type {fuel_type}: Unique Engine Sizes:", unique_engine_sizes)

        # For each engine size, print unique horsepower values
        for engine_size in unique_engine_sizes:
            engine_size_mask = df['engine_size'] == engine_size
            unique_horsepowers = np.sort(df.loc[fuel_type_mask & engine_size_mask, 'horsepower'].dropna().unique())
            print(f"Fuel Type {fuel_type}, Engine Size {engine_size}: Unique Horsepowers:", unique_horsepowers)

    # Print unique production years
    unique_production_years = np.sort(df['production_year'].dropna().unique())
    print("Unique Production Years:", unique_production_years)

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
        session['data_source'] = file_path  # Store path in session

        df = pd.read_csv(file_path)
        print_unique_values(df)  # Print unique values for fuel types, engine sizes, horsepowers, and production years

        df_preprocessed = ml_model.preprocess_data(file_path)
        mae, rmse, r2 = ml_model.train_model(df_preprocessed)

        return jsonify({'message': 'File uploaded and training completed', 'mae': mae, 'rmse': rmse, 'r2': r2}), file_path

# Mapping from fuel type string to integer for model prediction
fuel_type_mapping = {
    'Benzyna': 0,
    'Diesel': 1,
    'Benzyna+LPG': 2,
    'Benzyna+CNG': 3,
    'Elektryczny': 4,
    'Etanol': 5,
    'Hybryda': 6,
    'Wodór': 7
}

@app.route('/predict_price', methods=['POST'])
def predict_price():
    data = request.json
    try:
        fuel_type_str = data.get('fuel_type')
        fuel_type = fuel_type_mapping.get(fuel_type_str, -1)

        if fuel_type == -1:
            return jsonify({'error': 'Invalid fuel type'}), 400

        engine_size = float(data.get('engine_size').replace(' cm3', '').replace(' ', ''))
        horsepower = float(data.get('horsepower').replace(' KM', '').replace(' ', ''))
        mileage = float(data.get('mileage'))
        gearbox = int(data.get('gearbox'))
        production_year = int(data.get('production_year'))
    except (ValueError, TypeError) as e:
        return jsonify({'error': 'Invalid input data: ' + str(e)}), 400

    model = ml_model.load_model()
    predicted_price = ml_model.predict(model, engine_size, horsepower, mileage, gearbox, fuel_type, production_year)

    return jsonify({'predicted_price': predicted_price})


def get_dataframe():
    file_path = session.get('data_source')
    if file_path and os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        return pd.DataFrame()  # Return an empty DataFrame if path is not set or file does not exist

@app.route('/get_fuel_types', methods=['GET'])
def get_fuel_types():
    df = get_dataframe()  # Ensure this function correctly fetches your DataFrame
    if not df.empty:
        fuel_types = df['fuel_type'].dropna().unique().tolist()
        return jsonify(fuel_types)
    return jsonify([]), 404

@app.route('/get_engine_sizes', methods=['POST'])
def get_engine_sizes():
    fuel_type = request.json.get('fuel_type')
    df = get_dataframe()
    engine_sizes = df[df['fuel_type'] == fuel_type]['engine_size'].dropna().unique().tolist()
    return jsonify(sorted(engine_sizes))

@app.route('/get_horsepowers', methods=['POST'])
def get_horsepowers():
    engine_size = request.json.get('engine_size')
    df = get_dataframe()
    horsepowers = df[df['engine_size'] == engine_size]['horsepower'].dropna().unique().tolist()
    return jsonify(sorted(horsepowers))

@app.route('/get_production_years', methods=['GET'])
def get_production_years():
    df = get_dataframe()
    production_years = df['production_year'].dropna().unique().tolist()
    return jsonify(sorted(production_years))

@app.route('/download_csv')
def download_csv():
    csv_path = session.get('data_source')  # Assuming 'data_source' session variable holds the path to the CSV file
    if csv_path and os.path.exists(csv_path):
        return send_file(csv_path, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404



if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True, port=8080)
