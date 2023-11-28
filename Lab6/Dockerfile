# Use a Python image as the base image
FROM python:3
RUN wget -O /usr/local/bin/dumb-init https://github.com/Yelp/dumb-init/releases/download/v1.2.5/dumb-init_1.2.5_x86_64
RUN chmod +x /usr/local/bin/dumb-init
# Copy repo contents into working directory
COPY . /app
WORKDIR /app
#Copy training data 
COPY trainingsdata.json /app/trainingsdata.json  

# Copy your Python script into the container
#COPY pmon.py /app/pmon.py

# Install required Python packages

RUN pip install prometheus-api-client prometheus_client prophet requests numpy pandas datetime scikit-learn plotly 
# Dumb init
ENTRYPOINT ["/usr/local/bin/dumb-init", "--"]
# Run the Python script
#CMD ["python", "monitor.py"]
# Add minute to pull as parameter 
CMD ["python", "monitor.py", "1"]
#CMD ["python", "monitor.py", "-t1", "-T1", "-f2", "-m0"]
