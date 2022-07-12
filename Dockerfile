FROM python:3

ENV TZ=America/Chicago
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /serv
COPY . /serv
RUN python -m pip install -r /serv/requirements.txt

CMD ["bash"]
