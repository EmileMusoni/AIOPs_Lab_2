import time
from datetime import datetime, timedelta
import json
import pandas as pd
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
from prometheus_api_client import PrometheusConnect

from prometheus_client import CollectorRegistry, Gauge, push_to_gateway, start_http_server, write_to_textfile


# Connect to Prometheus
prometheus_url = 'http://host.docker.internal:9090'
#prometheus_url = 'http://host.docker.internal:9090'
prom = PrometheusConnect(url=prometheus_url)

# Define Prometheus push gateway URL
push_gateway_url = 'http://host.docker.internal:9091'  # Replace with the correct push gateway URL

# Define time periods
train_duration = timedelta(minutes=5)
test_duration = timedelta(minutes=1)

#results_df = pd.DataFrame(columns=['Timestamp', 'MAE', 'MAPE', 'Anomalies'])
# Create metrics only once
registry = CollectorRegistry()
mae_metric = Gauge('mean_absolute_error', 'Mean Absolute Error', labelnames=['instance', 'job'])
mape_metric = Gauge('mean_absolute_percentage_error', 'Mean Absolute Percentage Error', labelnames=['instance', 'job'])
anomaly_count_metric = Gauge('anomaly_count', 'Number of Anomalies', labelnames=['instance', 'job'])

start_http_server(8089)

results_list = []
while True:
    # Calculate time ranges
    end_time = datetime.now()
    start_time_train = end_time - train_duration
    start_time_test = end_time - test_duration

    # Query
    query_train = f'request_time_train{{job="app_one"}}[1m] offset 1m'
    query_test = f'request_time_test{{job="app_one"}}[1m] offset 1m'

    response_train = prom.custom_query(query_train)
    response_test = prom.custom_query(query_test)

    df_train = pd.DataFrame(response_train[0]['values'], columns=['ds', 'y'])
    df_train['ds'] = df_train['ds'].apply(lambda sec: datetime.fromtimestamp(float(sec)))
    print(df_train)

     # Wait for one minute before fetching testing metrics
    time.sleep(60)  # Sleep for 1 minute
    
    df_test = pd.DataFrame(response_test[0]['values'], columns=['ds', 'y'])
    df_test['ds'] = df_test['ds'].apply(lambda sec: datetime.fromtimestamp(float(sec)))
    print(df_test)
    # Build a new Prophet model for each iteration
    model = Prophet(interval_width=0.99, yearly_seasonality=False, weekly_seasonality=False, daily_seasonality=False)
    
    # Fit the model
    model.fit(df_train)

    # Make predictions
    forecast = model.predict(df_test)

    # Merge actual and predicted values
    performance = pd.merge(df_test, forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']], on='ds')
    
    print(performance)
    # Check MAE value
    performance_MAE = mean_absolute_error(performance['y'], performance['yhat'])
    print(f'The MAE for the model is {performance_MAE}')

    # Check MAPE value
    performance_MAPE = mean_absolute_percentage_error(performance['y'], performance['yhat'])
    print(f'The MAPE for the model is {performance_MAPE}')
    # Create an anomaly indicator
    performance['anomaly'] = performance.apply(lambda rows: 1 if ((float(rows.y)<rows.yhat_lower)|(float(rows.y)>rows.yhat_upper)) else 0, axis = 1)
    # Check the number of anomalies
    performance['anomaly'].value_counts()

    # Take a look at the anomalies
    anomalies = performance[performance['anomaly']==1].sort_values(by='ds')
    #anomalies

 
    num_anomalies = performance['anomaly'].sum()
 
    timestamp = end_time.strftime('%Y-%m-%d %H:%M:%S')

     
    results_list.append({'Timestamp': timestamp, 'MAE': performance_MAE, 'MAPE': performance_MAPE, 'Anomalies': num_anomalies})

    print(pd.DataFrame(results_list))
  
    # Set metric values
    mae_metric.labels(instance='pmon:8089', job='pmon').set(performance_MAE)
    mape_metric.labels(instance='pmon:8089', job='pmon').set(performance_MAPE)
    anomaly_count_metric.labels(instance='pmon:8089', job='pmon').set(num_anomalies)

   
    # Push metrics to Prometheus
    push_to_gateway(push_gateway_url, job='pmon', registry=registry)

  
    
    time.sleep(60)  # 300 seconds = 5 minutes