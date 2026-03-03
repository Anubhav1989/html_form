from flask import Flask, redirect, render_template,request, url_for
import numpy as np,joblib,mysql.connector

app=Flask(__name__)

@app.route('/')
def home():
    return render_template('form.html')

model=joblib.load('covid_model.pkl')

#Patient form
@app.route('/patient_form')
def patient_form():
    return render_template('patient_form.html')

@app.route('/submit_patient', methods=['POST'])
def submit_patient():
    name=request.form['name']
    age=request.form['age']
    gender=request.form['gender']
    city=request.form['city']

    conn=mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="covid_db"
    )
    cursor=conn.cursor()
    cursor.execute("INSERT INTO patients (name, age, gender, city) VALUES (%s, %s, %s, %s)", (name, age,gender,city))
    conn.commit()
    patient_id=cursor.lastrowid
    cursor.close()
    conn.close()

    return redirect(url_for('symptom_form', patient_id=patient_id))

#Symptom form
@app.route('/symptom_form')
def symptom_form():
    patient_id=request.args.get('patient_id')
    return render_template('symptom_form.html', patient_id=patient_id)

@app.route('/submit_symptoms', methods=['POST'])
def submit_symptoms():
    patient_id=request.form['patient_id']
    cough=request.form['cough']
    fever=request.form['fever']

    conn=mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="covid_db"
    )
    cursor=conn.cursor()
    cursor.execute("INSERT INTO symptoms (patient_id, cough, fever) VALUES (%s, %s, %s)",
                   (patient_id, cough, fever))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('medical_history_form', patient_id=patient_id))

#Medical history form
@app.route('/medical_history_form')
def medical_history_form():
    patient_id=request.args.get('patient_id')
    return render_template('medical_history_form.html', patient_id=patient_id)

@app.route('/submit_medical_history', methods=['POST'])
def submit_medical_history():
    patient_id=request.form['patient_id']
    vaccination=request.form['vaccination']
    chronic_disease=request.form['chronic_disease']
    
    conn=mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="covid_db"
    )
    cursor=conn.cursor()
    cursor.execute("INSERT INTO medical_history (patient_id, vaccination, chronic_disease) VALUES (%s, %s, %s)", (patient_id, vaccination, chronic_disease))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('prediction_form', patient_id=patient_id))

#Prediction form
@app.route('/prediction_form')
def prediction_form():
    patient_id = request.args.get('patient_id')
    return render_template('prediction_form.html',patient_id=patient_id)

@app.route('/predict', methods=['POST'])
def submit_prediction():
    patient_id = request.form['patient_id']
    
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="covid_db"
    )
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM patients WHERE patient_id=%s", (patient_id,))
    p = cursor.fetchone()
    cursor.execute("SELECT * FROM symptoms WHERE patient_id=%s", (patient_id,))
    s = cursor.fetchone()
    cursor.execute("SELECT * FROM medical_history WHERE patient_id=%s", (patient_id,))
    m = cursor.fetchone()

    cursor.close()
    conn.close()

    if not p: return f"Error: No patient record found for ID {patient_id}." 
    if not s: return f"Error: No symptoms recorded for patient {patient_id}. Please complete the symptom form." 
    if not m: return f"Error: No medical history recorded for patient {patient_id}. Please complete the medical history form."

    chronic_flag = 0 if m['chronic_disease'].lower() == "none" else 1

    input_data = np.array([
        int(p['gender']),
        int(p['age']),
        int(s['cough']),
        int(s['fever']),
        int(m['vaccination']),
        chronic_flag
    ]).reshape(1, -1)

    prediction = model.predict(input_data)
    result = "Positive" if prediction[0] == 1 else "Negative"

    conn = mysql.connector.connect( 
        host="localhost",
        user="root",
        password="1234", 
        database="covid_db" 
        ) 
    cursor = conn.cursor() 
    cursor.execute("INSERT INTO predictions (patient_id, result) VALUES (%s, %s)", (patient_id, result)) 
    conn.commit() 
    cursor.close() 
    conn.close()

    return f"COVID-19 Prediction for patient {patient_id}: {result}"

if __name__=="__main__":
    app.run(debug=True) 