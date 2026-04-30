from flask import Flask, render_template, request, jsonify, session
import pandas as pd
import numpy as np
import pickle
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'expense_secret_key_123'  # For session management

# Known valid categorical values (must match training data)
VALID_OCCUPATIONS = ['Business', 'Freelancer', 'Salaried', 'Student']
VALID_CITY_TYPES  = ['Rural', 'Semi-Urban', 'Urban']

# Load model and encoders — absolute path so it works from any CWD
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'model.pkl')
model_data = None

def load_model():
    global model_data
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, 'rb') as f:
            model_data = pickle.load(f)
    else:
        print("Model file not found. Please run train_model.py first.")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/expense')
def expense_input():
    return render_template('expense.html')

@app.route('/result')
def result():
    prediction_data = session.get('prediction_data')
    if not prediction_data:
        return render_template('expense.html')
    return render_template('result.html', data=prediction_data)

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/predict', methods=['POST'])
def predict():
    if model_data is None:
        load_model()
        if model_data is None:
            return jsonify({'error': 'Model not loaded'}), 500

    try:
        data = request.json
        date_obj = datetime.strptime(data['date'], '%Y-%m-%d')
        
        input_data = {
            'age': int(data['age']),
            'occupation': data['occupation'],
            'monthly_income': float(data['monthly_income']),
            'city_type': data['city_type'],
            'day': date_obj.day,
            'month': date_obj.month,
            'weekday': date_obj.weekday(),
            'is_weekend': 1 if date_obj.weekday() >= 5 else 0,
            'food': float(data['food']),
            'transport': float(data['transport']),
            'rent': float(data['rent']),
            'entertainment': float(data['entertainment']),
            'utilities': float(data['utilities']),
            'shopping': float(data['shopping']),
            'others': float(data['others'])
        }

        # Validate categorical fields against known training labels
        occ  = data['occupation']
        city = data['city_type']
        known_occ  = list(model_data['le_occ'].classes_)
        known_city = list(model_data['le_city'].classes_)

        if occ not in known_occ:
            return jsonify({
                'error': f"Invalid occupation '{occ}'. Valid options: {known_occ}"
            }), 400
        if city not in known_city:
            return jsonify({
                'error': f"Invalid city_type '{city}'. Valid options: {known_city}"
            }), 400

        input_df = pd.DataFrame([input_data])
        input_df['occupation'] = model_data['le_occ'].transform(input_df['occupation'].astype(str))
        input_df['city_type']  = model_data['le_city'].transform(input_df['city_type'].astype(str))

        X = input_df[model_data['features']]
        prediction = model_data['model'].predict(X)[0]
        
        prediction_result = {
            'prediction': round(prediction, 2),
            'range': f"₹{round(prediction * 0.95, 2)} - ₹{round(prediction * 1.05, 2)}",
            'input_data': data # Store original data for display
        }
        
        session['prediction_data'] = prediction_result
        return jsonify({'status': 'success', 'redirect': '/result'})

    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    load_model()
    app.run(debug=True, port=5000)
