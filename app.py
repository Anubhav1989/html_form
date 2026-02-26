from flask import Flask, request, jsonify, render_template
import mysql.connector
import joblib
import numpy as np

app = Flask(__name__)
model = joblib.load("model1.pkl")

@app.route('/')
def home():
    return render_template('form.html')

@app.route('/submit_form', methods=['POST'])
def submit_form():
    gender = request.form['gender']
    cough = request.form['cough']
    city = request.form['city']
    age = request.form['age']
    fever = request.form['fever']

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="xpdb"
    )
    cursor = conn.cursor()
    cursor.execute("INSERT INTO covid_toy (gender, cough, city, age, fever) VALUES (%s, %s, %s, %s, %s)", 
                   (gender, cough, city, age, fever))
    conn.commit()
    cursor.close()
    conn.close()

    input_data = np.array([int(gender), int(cough), int(city), int(age), int(fever)]).reshape(1, -1)
    prediction = model.predict(input_data)
    result = "Covid Positive" if prediction[0] == 1 else "Covid Negative"

    return f"Prediction: {result}"

if __name__ == "__main__":
    app.run(debug=True)
