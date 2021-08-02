FROM python:3.7


RUN pip install pymongo
RUN pip install flask

ADD . /src/

CMD cd /src/ && python index.py