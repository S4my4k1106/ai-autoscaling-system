import pandas as pd
import joblib

model = joblib.load("ml/model.pkl")

cpu = float(input("Enter CPU: "))
network = float(input("Enter Network: "))

data = pd.DataFrame([[cpu, network]], columns=["cpu", "network"])

prediction = model.predict(data)

print(f"Predicted Memory: {prediction[0]}")
