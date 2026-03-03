import pandas as pd
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="covid_db"
)

query="""
SELECT p.patient_id, p.age, p.gender, s.cough, s.fever, m.vaccination, s.has_covid
FROM patients p
JOIN symptoms s ON p.patient_id = s.patient_id
JOIN medical_history m ON p.patient_id = m.patient_id;
"""

df=pd.read_sql(query, conn)
conn.close()

x=df.drop(columns='has_covid')
y=df['has_covid']

from sklearn.model_selection import train_test_split
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

from sklearn.linear_model import LogisticRegression
lr=LogisticRegression()
lr.fit(x_train, y_train)

import joblib
joblib.dump(lr, 'covid_model.pkl')
