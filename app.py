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
    time.sleep(5)
   #g.set(t)


if __name__ == '__main__':
    start_http_server(8000)
    while True:
        #emit_data(random.random())
        emit_data()
