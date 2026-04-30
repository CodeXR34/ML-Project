import pandas as pd
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error
import pickle
import os
from datetime import datetime, timedelta

def generate_dataset(n_rows=5000):
    print(f"Generating {n_rows} rows of synthetic data...")
    
    np.random.seed(42)
    
    occupations = ['Student', 'Salaried', 'Business', 'Freelancer']
    city_types = ['Urban', 'Semi-Urban', 'Rural']
    
    data = {
        'age': np.random.randint(18, 65, n_rows),
        'occupation': np.random.choice(occupations, n_rows),
        'monthly_income': np.random.randint(20000, 150000, n_rows),
        'city_type': np.random.choice(city_types, n_rows),
        'date': [datetime(2023, 1, 1) + timedelta(days=np.random.randint(0, 365)) for _ in range(n_rows)]
    }
    
    df = pd.DataFrame(data)
    
    # Calculate expenses with realistic correlations
    def calculate_expenses(row):
        income = row['monthly_income']
        is_weekend = row['date'].weekday() >= 5
        city = row['city_type']
        
        # Base percentages
        food = income * np.random.uniform(0.1, 0.2)
        transport = income * np.random.uniform(0.05, 0.1)
        
        # Rent varies by city type
        rent_pct = 0.3 if city == 'Urban' else (0.2 if city == 'Semi-Urban' else 0.1)
        rent = income * rent_pct + np.random.uniform(-1000, 1000)
        
        # Entertainment higher on weekends
        ent_base = 0.05 if not is_weekend else 0.15
        entertainment = income * np.random.uniform(ent_base - 0.02, ent_base + 0.05)
        
        utilities = income * np.random.uniform(0.03, 0.07)
        shopping = income * np.random.uniform(0.05, 0.15)
        others = income * np.random.uniform(0.02, 0.05)
        
        return pd.Series([food, transport, rent, entertainment, utilities, shopping, others])

    expense_cols = ['food', 'transport', 'rent', 'entertainment', 'utilities', 'shopping', 'others']
    df[expense_cols] = df.apply(calculate_expenses, axis=1)
    
    df['total_expense'] = df[expense_cols].sum(axis=1)
    
    # Add overspending habit (simulated)
    df['overspending_habit'] = (df['total_expense'] > df['monthly_income'] * 0.8).astype(int)
    
    df.to_csv('expenses.csv', index=False)
    print("Dataset saved as expenses.csv")
    return df

def train_model():
    if not os.path.exists('expenses.csv'):
        df = generate_dataset()
    else:
        df = pd.read_csv('expenses.csv')
        df['date'] = pd.to_datetime(df['date'])

    # Feature Engineering
    df['day'] = df['date'].dt.day
    df['month'] = df['date'].dt.month
    df['weekday'] = df['date'].dt.weekday
    df['is_weekend'] = (df['weekday'] >= 5).astype(int)

    # Encoding
    le_occ = LabelEncoder()
    df['occupation'] = le_occ.fit_transform(df['occupation'].astype(str))
    
    le_city = LabelEncoder()
    df['city_type'] = le_city.fit_transform(df['city_type'].astype(str))

    # Features and Target
    features = ['age', 'occupation', 'monthly_income', 'city_type', 'day', 'month', 'weekday', 'is_weekend',
                'food', 'transport', 'rent', 'entertainment', 'utilities', 'shopping', 'others']
    X = df[features]
    y = df['total_expense']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Training Random Forest Regressor...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    print(f"Model Trained. Mean Absolute Error: {mae:.2f}")

    # Save model and encoders
    model_data = {
        'model': model,
        'le_occ': le_occ,
        'le_city': le_city,
        'features': features
    }
    
    with open('model.pkl', 'wb') as f:
        pickle.dump(model_data, f)
    print("Model and encoders saved as model.pkl")

if __name__ == "__main__":
    train_model()
