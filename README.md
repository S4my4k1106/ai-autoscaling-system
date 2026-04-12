# AI-Based Predictive Auto-Scaling System

## Overview
This project predicts system resource usage using Machine Learning and helps in making intelligent auto-scaling decisions. It uses both real-time system data and external datasets to train a predictive model.

## Features
- Real-time system metrics collection (CPU, Memory, Network)
- Data cleaning and preprocessing
- Hybrid dataset (external + local)
- Machine Learning model for prediction
- Memory usage prediction based on CPU and network traffic

## Tech Stack
- Python
- pandas
- scikit-learn
- psutil
- Linux

## Project Structure
ai-based-loadbalancing-system/
├── collector/
│   └── collector.py
├── data/
│   ├── cleaned_dataset.csv
│   └── metrics.csv
├── ml/
│   ├── train.py
│   ├── test.py
│   └── model.pkl
├── README.md

## Workflow
1. Collect real-time system data using collector.py  
2. Clean and preprocess external dataset  
3. Combine datasets  
4. Train Machine Learning model  
5. Predict memory usage  

## How to Run

1. Collect Data  
python3 collector/collector.py  

2. Train Model  
python3 ml/train.py  

3. Test Model  
python3 ml/test.py  

## Model Details
- Input: CPU usage, Network traffic  
- Output: Memory usage  
- Algorithm: Linear Regression  

## Dataset
The project uses:
- External dataset (cleaned)
- Real-time generated dataset  

Note: Dataset is not included due to size limitations. It can be regenerated using the collector script.

## Use Case
This system helps in:
- Predicting resource usage  
- Preventing system overload  
- Supporting auto-scaling decisions in cloud environments  

## Future Work
- Docker containerization  
- Kubernetes-based auto-scaling  
- FastAPI integration  
- Real-time deployment  

## Author
-- Disha 
-- Neeharika 
-- Samyak 
