import os
import numpy as np
import pandas as pd
import joblib
import matplotlib  # Import before pyplot to set the backend
matplotlib.use('Agg')  # Use a non-GUI backend
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder, KBinsDiscretizer

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def preprocess_data(file_path):
    try:
        df = pd.read_csv(file_path)
    except pd.errors.EmptyDataError:
        raise ValueError("CSV file is empty")

    df.columns = df.columns.str.strip()
    df = df.dropna()

    # Clean and convert columns
    df['horsepower'] = df['horsepower'].str.extract('(\d+)').astype(float)
    df['mileage'] = df['mileage'].str.extract('(\d+)').astype(float).fillna(0)
    df['price'] = df['price'].str.replace(' ', '').astype(float)
    df['engine_size'] = df['engine_size'].str.extract('(\d+)').astype(float)

    # Mapping fuel types
    fuel_types = ['Benzyna', 'Diesel', 'Benzyna+LPG', 'Benzyna+CNG', 'Elektryczny', 'Etanol', 'Hybryda', 'Wodór']
    fuel_type_mapping = {fuel: idx for idx, fuel in enumerate(fuel_types)}
    df['fuel_type'] = df['fuel_type'].map(fuel_type_mapping)

    df['gearbox'] = LabelEncoder().fit_transform(df['gearbox'])

    # Feature Engineering
    df['car_age'] = 2024 - df['production_year']

    # Mileage Transformations
    df['mileage_log'] = np.log(df['mileage'] + 1)
    df['mileage_inverse'] = 1 / (df['mileage'] + 1)

    # Mileage bins
    mileage_bins = KBinsDiscretizer(n_bins=5, encode='ordinal', strategy='quantile')
    df['mileage_bin'] = mileage_bins.fit_transform(df[['mileage']])

    return df

def train_model(df):
    ensure_dir('models/')
    ensure_dir('static/plots/')
    ensure_dir('static/plots/histograms/')
    ensure_dir('static/plots/scatter_plots/')
    ensure_dir('static/plots/correlation/')

    if df.empty:
        raise ValueError("No data to train the model")
    X = df.drop('price', axis=1)
    y = df['price']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    joblib.dump((model, X_train.columns), 'models/car_price_predictor_model.pkl')

    feature_importances = pd.Series(model.feature_importances_, index=X_train.columns)
    plt.figure(figsize=(10, 6))
    feature_importances.nlargest(10).plot(kind='barh')
    plt.savefig('plots/feature_importance.png')
    plt.close()

    # Save histograms and scatter plots
    save_histograms(df, ['engine_size', 'horsepower', 'mileage', 'price'], 'plots/histograms/')
    save_scatter_plots(df, [('mileage', 'price'), ('horsepower', 'price')], 'plots/scatter_plots/')
    save_correlation_matrix(df, ['engine_size', 'horsepower', 'mileage', 'price', 'production_year'], 'plots/correlation/')

    y_pred = model.predict(X_test)
    return mean_absolute_error(y_test, y_pred), mean_squared_error(y_test, y_pred, squared=False), r2_score(y_test, y_pred)

def save_histograms(df, columns, directory):
    for column in columns:
        plt.figure(figsize=(10, 6))
        sns.histplot(df[column], kde=True)
        plt.title(f'Histogram of {column}')
        plt.xlabel(column)
        plt.ylabel('Frequency')
        plt.savefig(f"{directory}/{column}_histogram.png")
        plt.close()

def save_scatter_plots(df, plot_pairs, directory):
    for x, y in plot_pairs:
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=df, x=x, y=y)
        plt.title(f'{x} vs {y}')
        plt.xlabel(x)
        plt.ylabel(y)
        plt.savefig(f"{directory}/{x}_vs_{y}.png")
        plt.close()

def save_correlation_matrix(df, columns, directory):
    plt.figure(figsize=(10, 8))
    corr_matrix = df[columns].corr()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Correlation Matrix')
    plt.savefig(f"{directory}/correlation_matrix.png")
    plt.close()

def load_model():
    return joblib.load('models/car_price_predictor_model.pkl')

def predict(model_data, engine_size, horsepower, mileage, gearbox, fuel_type, production_year):
    model, feature_names = model_data
    car_age = 2024 - production_year
    mileage_log = np.log(mileage + 1)
    mileage_inverse = 1 / (mileage + 1)
    input_features = pd.DataFrame({
        'engine_size': [engine_size],
        'horsepower': [horsepower],
        'mileage': [mileage],
        'mileage_log': [mileage_log],
        'mileage_inverse': [mileage_inverse],
        'gearbox': [gearbox],
        'fuel_type': [fuel_type],
        'car_age': [car_age],
        'production_year': [production_year]
    }, columns=feature_names).fillna(0)
    prediction = model.predict(input_features)
    return round(prediction[0], -2)
