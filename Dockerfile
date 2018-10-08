FROM python

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "main.py"]

