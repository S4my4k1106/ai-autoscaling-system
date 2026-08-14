import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import pickle


df = pd.read_csv("data/training_data.csv")


df = df.sample(n=min(100000, len(df)), random_state=42)


X = df[['cpu', 'network_traffic']]
y = df['memory']


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


model = RandomForestRegressor(n_estimators=50, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)


y_pred = model.predict(X_test)
print(f"R² Score: {r2_score(y_test, y_pred):.4f}")
print(f"MAE: {mean_absolute_error(y_test, y_pred):.4f}")


with open("ml/model_memory.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model saved as ml/model_memory.pkl")