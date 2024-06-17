import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

def preprocess_data(file_path):
    try:
        # Load dataset
        df = pd.read_csv(file_path)
    except pd.errors.EmptyDataError:
        raise ValueError("CSV file is empty")

    # Data cleaning and preprocessing
    df.columns = df.columns.str.strip()  # Trim column names

    # Convert relevant columns to numeric values
    df['horsepower'] = df['horsepower'].str.replace(' KM', '').str.replace(' ', '').astype(float)
    df['mileage'] = df['mileage'].str.replace(' km', '').str.replace(' ', '').astype(float)
    df['price'] = df['price'].str.replace(' ', '').astype(float)
    df['engine_size'] = df['engine_size'].str.replace(' cm3', '').str.replace(' ', '').astype(float)

    # Define all possible fuel types and encode them
    fuel_types = ['Benzyna', 'Diesel', 'Benzyna+LPG', 'Benzyna+CNG', 'Elektryczny', 'Etanol', 'Hybryda', 'Wodór']
    fuel_type_mapping = {fuel: idx for idx, fuel in enumerate(fuel_types)}
    df['fuel_type'] = df['fuel_type'].map(fuel_type_mapping)

    # Encoding categorical variables
    df['gearbox'] = LabelEncoder().fit_transform(df['gearbox'])

    # Feature Engineering
    df['car_age'] = 2024 - df['production_year']
    df['mileage_inverse'] = 1 / (df['mileage'] + 1)  # Adding 1 to avoid division by zero

    return df

# Load your data
df = pd.read_csv('scraped_auctions.csv')
df = preprocess_data(df)

# Then perform your train-test split, and proceed with the grid search as before

# Ensure the dataset is loaded and preprocessed correctly
# For demonstration, here's how you might load and split the data
X = df.drop('price', axis=1)
y = df['price']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define and setup the RandomForest and GridSearchCV
rf = RandomForestRegressor(random_state=42)
param_grid = {
    'n_estimators': [100, 200],
    'max_depth': [None, 10, 20],
    'min_samples_leaf': [1, 2, 4]
}
grid_search = GridSearchCV(estimator=rf, param_grid=param_grid, cv=3, n_jobs=-1, scoring='r2')
grid_search.fit(X_train, y_train)

# Retrieve the best parameters and retrain the model
best_params = grid_search.best_params_
model = RandomForestRegressor(**best_params, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

# Evaluation
r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred, squared=False)

print(f"R^2 Score: {r2}")
print(f"MAE: {mae}")
print(f"RMSE: {rmse}")
print(f"Best Parameters: {best_params}")
