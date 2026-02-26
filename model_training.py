import mysql.connector, pandas as pd, joblib
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

conn = mysql.connector.connect(host="localhost", user="root", password="1234", database="xpdb")
df = pd.read_sql("SELECT * FROM covid_toy", conn)
conn.close()

df=df.dropna()

lb = LabelEncoder()
df['gender'] = lb.fit_transform(df['gender'])
df['cough'] = lb.fit_transform(df['cough'])
df['city'] = lb.fit_transform(df['city'])
df['age'] = df['age'].astype(int)
df['has_covid'] = lb.fit_transform(df['has_covid'])

X = df[['gender','cough','city','age','fever']]
y = df['has_covid']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = LogisticRegression()
model.fit(X_train, y_train)

joblib.dump(model, "model1.pkl")
print("Model trained and saved successfully!")
