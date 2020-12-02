FROM python:3.8
COPY . /headpage
WORKDIR /headpage
RUN pip3 install --upgrade pip && \
    pip3 install --trusted-host pypi.python.org -r requirements.txt && \
    ./reset_db.sh
EXPOSE 8000
ENTRYPOINT ["python3", "src/manage.py","runserver","0.0.0.0:8000"]
