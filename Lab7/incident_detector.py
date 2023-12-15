#test
from prometheus_client import start_http_server, Gauge, Counter
import time
import requests
import time
from datetime import datetime
import pandas as pd
from tabulate import tabulate
# Prometheus Metrics
accumulator_metric_ship = Gauge("lab7_incident_accumulator_frontend_2_shipping", "Accumulator for Shipping Service")
accumulator_metric_prodcat = Gauge("lab7_incident_accumulator_frontend_2_productcatalogservice", "Accumulator for Product Catalog Service")
temperature_metric = Gauge("lab7_incident_temperature", "Sum of Accumulators (Temperature)")
sev1_metric = Gauge("lab7_incident_sev1", "Sev 1 Incident")
sev2_metric = Gauge("lab7_incident_sev2", "Sev 2 Incident")
# Accumulator constants
DECAY_FACTOR = 2
SHIP_THRESHOLD = 2
PRODCAT_THRESHOLD = 2
INCIDENT_THRESHOLD = 4

# Initialize accumulators to zero
accumulator_prodcat = 0
accumulator_ship = 0
results_list = []
#header_printed = False

def update_accumulators(anomaly_ship , anomaly_prodcat):
    global accumulator_prodcat, accumulator_ship
    
    # Decay accumulators by DECAY_FACTOR
    '''
    accumulator_prodcat = max(accumulator_prodcat - DECAY_FACTOR, 0)
    accumulator_ship = max(accumulator_ship - DECAY_FACTOR, 0)

    # Bump accumulators based on anomalies
    accumulator_prodcat += 1 if anomaly_prodcat else 0
    accumulator_ship += 1 if anomaly_ship else 0
    '''
    if anomaly_count_ship > 0:
       accumulator_ship += 1
    else:
        accumulator_ship = max(accumulator_ship - 2, 0)
    if anomaly_count_prodcat > 0:
        accumulator_prodcat += 1
    else:
        accumulator_prodcat = max(accumulator_prodcat - 2, 0)

    # Update Prometheus metrics
    #print("accumulator_metric_prodcat.set(accumulator_prodcat)",accumulator_prodcat)
    accumulator_metric_prodcat.set(accumulator_prodcat)
    accumulator_metric_ship.set(accumulator_ship)
    sumACcumulator=accumulator_prodcat + accumulator_ship
    temperature_metric.set(sumACcumulator)


    #ssss
    
    if sumACcumulator > INCIDENT_THRESHOLD:
        if accumulator_ship > SHIP_THRESHOLD and accumulator_prodcat > PRODCAT_THRESHOLD:
            sev1_metric.set(1)
            sev2_metric.set(0)
        elif (accumulator_ship > SHIP_THRESHOLD and accumulator_prodcat == 0) or (accumulator_ship == 0 and accumulator_prodcat > PRODCAT_THRESHOLD):
            sev1_metric.set(0)
            sev2_metric.set(1)
    else:
        sev1_metric.set(0)
        sev2_metric.set(0)  
    #sssss

    # Check for incidents
    '''
    if accumulator_prodcat + accumulator_ship > INCIDENT_THRESHOLD:
        if accumulator_prodcat > 0 and accumulator_ship > 0:
            sev1_metric.set(1)
            sev2_metric.set(0)
            #print("Sev 1 Incident Detected!")
        elif accumulator_prodcat > 0 or accumulator_ship > 0:
            sev1_metric.set(0)
            sev2_metric.set(1)
            #print("Sev 2 Incident Detected.")
    '''
if __name__ == '__main__':
      # Choose a different port than Lab 6 monitor
    start_http_server(8099)
    while True:
        # Retrieve anomaly counts from Prometheus
        anomaly_count_ship = requests.get("http://34.135.43.19:9090/api/v1/query", params={'query': 'lab7_frontend_2_shippingservice_anomaly_count'}).json()['data']['result'][0]['value'][1]

        anomaly_count_prodcat = requests.get("http://34.135.43.19:9090/api/v1/query", params={'query': 'lab7_frontend_2_productcatalogservice_anomaly_count'}).json()['data']['result'][0]['value'][1]
        
        # Convert anomaly counts to integers
        anomaly_count_ship = int(anomaly_count_ship)
        anomaly_count_prodcat = int(anomaly_count_prodcat)
        

        # Convert anomaly counts to boolean
        # Convert anomaly counts to boolean
        
        anomaly_ship = anomaly_count_ship > 0
        anomaly_prodcat = anomaly_count_prodcat > 0
        monitor_start_time = datetime.now()
        timestamp = monitor_start_time.strftime('%Y-%m-%d %H:%M:%S')

        '''
        sev1_value = int(list(sev1_metric.collect())[0].samples[0].value)
        sev2_value = int(list(sev2_metric.collect())[0].samples[0].value)
        tempp= int(list(temperature_metric.collect())[0].samples[0].value)
        '''
        
        row_data = [timestamp, anomaly_ship, anomaly_prodcat,temperature_metric._value.get(), sev1_metric._value.get(), sev2_metric._value.get()]
        results_list.append(row_data)
        
        # Display results in tabular format with headers as metrics and timestamp
        headers = ["Timestamp", "Accumulator_F_2_S", "Accumulator_F_2_P", "Temperature", "Incident_Sev_1", "Incident_Sev_2"]
        print(tabulate(results_list, headers=headers, tablefmt='psql'))
        
        #results_list.append({'Timestamp': timestamp, 'Accumulator_F_2_S': anomaly_count_ship, 'Accumulator_F_2_P': accumulator_prodcat, 'Temperature': tempp, 'Incident_Sev_1':sev1_value, 'Incident_Sev_2':sev2_value})
        #print(pd.DataFrame(results_list))
        # Update accumulators and check for incidents
        update_accumulators(anomaly_ship,anomaly_prodcat)

        time.sleep(5)  # Adjust sleep time based on your desired frequency
