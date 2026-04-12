import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib

external = pd.read_csv("data/cleaned_dataset.csv")

local = pd.read_csv("data/metrics.csv", names=["cpu", "network", "memory"])

data = pd.concat([external, local])

data = data.sample(frac=1).reset_index(drop=True)

X = data[["cpu", "network"]]
y = data["memory"]

model = LinearRegression()
model.fit(X, y)

joblib.dump(model, "ml/model.pkl")

print("Model trained successfully!")
