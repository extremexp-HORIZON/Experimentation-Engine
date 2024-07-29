FROM python:3.9-alpine

COPY . /exp-engine-service
WORKDIR /exp-engine-service
# apline can not build pandas by default
# https://copyprogramming.com/howto/install-pandas-in-a-dockerfile

RUN pip install -r requirements.txt

COPY . .

WORKDIR /exp-engine-service/src
ENV PORT 5556
EXPOSE 5556

ENTRYPOINT [ "python" ]
CMD [ "run.py" ]
