FROM python:3.10.4
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
RUN python3 -m pip install ibm_db
EXPOSE 5000
CMD python ./app.py

