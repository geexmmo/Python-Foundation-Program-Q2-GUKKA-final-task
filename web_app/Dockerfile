FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY *.py /app/
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]