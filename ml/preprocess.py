import pandas as pd

df = pd.read_csv("data/vmCloud_data.csv")
df = df[['cpu_usage', 'memory_usage', 'network_traffic', 'timestamp']]
df = df.rename(columns={
    'cpu_usage': 'cpu',
    'memory_usage': 'memory',
    'network_traffic': 'network_traffic',
    'timestamp': 'timestamp'
})
df = df.dropna()
df.to_csv("data/cleaned_dataset.csv", index=False)
print(f"Done! Cleaned dataset shape: {df.shape}")
print(df.head())

real = pd.read_csv("data/metrics.csv")


df = pd.concat([df, real], ignore_index=True)
df = df.dropna()

print(f"Merged dataset shape: {df.shape}")