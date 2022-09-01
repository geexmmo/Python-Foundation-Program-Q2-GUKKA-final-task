FROM python:3.9-slim
RUN apt-get update
RUN apt-get --assume-yes install postgresql-client
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY *.py /app/
COPY delaystart.sh /app/
RUN chmod +x delaystart.sh
CMD ["./delaystart.sh","postgres-finaltask", "python3", "-m", "gunicorn", "-w", "1" ,"app:app" ,"-b" ,"0.0.0.0:5000"]