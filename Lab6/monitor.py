
from __future__ import print_function  # Add this line at the beginning of your script
import requests
from prometheus_client import start_http_server, Gauge, Summary, Histogram, Counter
import sys
from prometheus_api_client import PrometheusConnect
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
from prophet import Prophet
import numpy as np
import pandas as pd
from datetime import datetime
import time
from urllib.parse import urlencode
import json
import math


def main(minutes_to_pull):

    url_test_datab = 'histogram_quantile(0.5, sum by (le) (rate(istio_request_duration_milliseconds_bucket{app="frontend", destination_app="shippingservice", reporter="source"}[1m])))'
    #test_urlb = "http://34.135.93.63:9090"
    test_urlb = "http://prometheus.istio-system:9090"
    #test_url = "http://34.135.93.63:9090/api/v1/query"
    promb = PrometheusConnect(url=test_urlb)
    g_req50 = Gauge("frontend_to_shipping_req_50", "request seconds frontend to shipping service" )
    g_req50.set(0)
    

    mae_metric = Gauge("prophet_mae", "Mean Absolute Error for Prophet Model")
    mape_metric = Gauge("prophet_mape", "Mean Absolute Percentage Error for Prophet Model")
    anomaly_metric = Gauge("prophet_anomaly", "Number of Anomalies Detected")
    y_min_metric = Gauge("prophet_y_min", "Min Value of y in Test Data")
    y_metric = Gauge("prophet_y", "Actual Value of y in Test Data")
    y_max_metric = Gauge("prophet_y_max", "Max Value of y in Test Data")

    f = open("trainingsdata.json")
    prom = json.load(f)
   
    df_train = pd.DataFrame(prom['data']['result'][0]['values'])
    df_train.columns = ['ds', 'y']
    
    df_train['ds'] = df_train['ds'] - df_train['ds'].iloc[0]
    df_train['ds'] = df_train['ds'].apply(lambda sec: datetime.fromtimestamp(sec))
    df_train['y']=df_train['y'].astype(float)
    model = Prophet(interval_width=0.99, yearly_seasonality=False, weekly_seasonality=False, daily_seasonality=False,growth='flat')
    model.add_seasonality(name='hourly', period=1/24, fourier_order=5)
    model.fit(df_train)
    
    monitor_start_time = datetime.now()
    results_list = []
    while True:

        response_test = promb.custom_query(url_test_datab)
        #Response value
        req_50_value=response_test[0]['value'][1]
        req_50_value = req_50_value.strip()
     
        if req_50_value.lower() != "nan":
            
            g_req50.set(req_50_value)

            df_test = pd.DataFrame([{'ds': response_test[0]['value'][0], 'y': response_test[0]['value'][1]}])
            
            test_start_ds = df_test['ds'].iloc[0]
            df_test['ds'] = df_test['ds'] - test_start_ds

            df_test['ds'] = df_test['ds'].apply(lambda sec: datetime.fromtimestamp(sec))
            
            forecast = model.predict(df_test)
            performance = pd.merge(df_test, forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']], on='ds')

            print(performance)

            y_min_metric.set(performance['yhat_lower'].values[0])
            y_metric.set(performance['y'].values[0])
            y_max_metric.set(performance['yhat_upper'].values[0])

            performance_MAE = mean_absolute_error(performance['y'], performance['yhat'])
            print(f'The MAE for the model is {performance_MAE}')

            mae_metric.set(performance_MAE)

            performance_MAPE = mean_absolute_percentage_error(performance['y'], performance['yhat'])
            print(f'The MAPE for the model is {performance_MAPE}')

            mape_metric.set(performance_MAPE)

            performance['anomaly'] = performance.apply(lambda rows: 1 if ((float(rows.y) < rows.yhat_lower) or (float(rows.y) > rows.yhat_upper)) else 0, axis=1)

            performance['anomaly'].value_counts()

            anomalies = performance[performance['anomaly'] == 1].sort_values(by='ds')
            anomalies

            timestamp = monitor_start_time.strftime('%Y-%m-%d %H:%M:%S')
            num_anomalies = performance['anomaly'].sum()
            anomaly_metric.set(num_anomalies)

            results_list.append({'Timestamp': timestamp, 'MAE': performance_MAE, 'MAPE': performance_MAPE, 'Anomalies': num_anomalies})
            print(pd.DataFrame(results_list))

            time.sleep(minutes_to_pull*60)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 monitor.py <minutes_to_pull>")
        sys.exit(1)
    minutes_to_pull = int(sys.argv[1])
    #minutes_to_pull = 1
    start_http_server(8099)
    main(minutes_to_pull)

