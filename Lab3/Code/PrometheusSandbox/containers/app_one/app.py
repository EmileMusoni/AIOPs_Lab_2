from prometheus_client import start_http_server, Gauge, Histogram
import random
import time

#g = Gauge('demo_gauge', 'Description of demo gauge')
# Define the first gauge metric
gauge_m1 = Gauge('app1_gauge1', 'Random gauge metric between 0 and 1')

# Define the first histogram metric with custom buckets
histogram_m1 = Histogram('app1_histogram1', 'Random histogram metric between 0 and 1', buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])

# Define the second gauge metric
gauge_m2 = Gauge('app1_gauge2', 'Random gauge metric between 0 and 0.6')

# Define the second histogram metric with custom buckets
histogram_m2 = Histogram('app1_histogram2', 'Random histogram metric between 0 and 0.6', buckets=[0.1, 0.2, 0.3, 0.4, 0.5])


#for lab 3
# Define the gauge metric for request_time_train with a threshold of 0.6
request_time_train = Gauge('request_time_train', 'Simulated request time for training (clipped at 0.6)', labelnames=['type'])
request_time_train.labels(type='train')

# Define the gauge metric for request_time_test
request_time_test = Gauge('request_time_test', 'Simulated request time for testing', labelnames=['type'])
request_time_test.labels(type='test')

#end for lab 3


#def emit_data(t):
def emit_data():
    """Emit fake data"""
    # time.sleep(t)
    # Generate random values for the metrics
    random_value_1 = random.uniform(0, 1.0)  # Random value between 0 and 1
    random_value_2 = random.uniform(0, 0.6)  # Random value between 0 and 0.6

    # Set the gauge metric values
    gauge_m1.set(random_value_1)
    gauge_m2.set(random_value_2)

    # Record the histogram metric values
    histogram_m1.observe(random_value_1)
    histogram_m2.observe(random_value_2)

    # Sleep for a while before updating again

    #for lab 3
     # Generate random values for request_time_train and request_time_test
    random_value_train = min(random.uniform(0, 0.6), 0.6)  # Clip values at 0.6 for training
    random_value_test = random.uniform(0, 1.0)  # Random value between 0 and 1 for testing

        # Set the gauge metric values
     # Set the gauge metric values with label values
    request_time_train.labels(type='train').set(random_value_train)
    request_time_test.labels(type='test').set(random_value_test)
   # request_time_train.set(random_value_train)
    #request_time_test.set(random_value_test)
    #end for lab3

    time.sleep(5)
   #g.set(t)


if __name__ == '__main__':
    start_http_server(8000)
    while True:
        #emit_data(random.random())
        emit_data()
