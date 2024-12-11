FROM python:3.9.13
LABEL maintainer="mnie"

COPY . .

RUN python3 -m pip install pip --upgrade
RUN pip3 install .

CMD ["kids_box"]

EXPOSE 8000
