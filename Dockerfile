FROM ubuntu:hirsute
RUN apt update
RUN apt upgrade -y
ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true
RUN apt install -y sqlite3
RUN apt install -y portaudio19-dev
RUN apt install -y libffi-dev gcc musl-dev python3-dev 
RUN apt install -y pulseaudio socat pulseaudio-utils
RUN apt update --fix-missing -y
RUN apt install -y alsa alsa-utils alsa-tools ffmpeg
RUN apt install -y python3-pyaudio

# RUN apt install -y python3-cryptography
RUN apt install -y python3-pip
RUN apt install -y python3-numpy python3-scipy
# RUN apt install -y build-essential libzbar-dev libzbar0
RUN apt install -y libssl-dev
RUN apt install -y nano


# FROM alpine:3
# RUN apk update && apk upgrade
# RUN apk add sqlite
# RUN apk add python3
# RUN apk add portaudio portaudio-dev
# RUN apk add libffi-dev gcc musl-dev python3-dev
# RUN apk add pulseaudio socat pulseaudio-alsa alsa-plugins-pulse
# RUN apk add alsa-utils alsa-utils-doc alsa-lib alsaconf ffmpeg
# RUN apk add py-cryptography
# RUN apk add py3-pip
# RUN apk add nano

ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

RUN pip install --upgrade pip
COPY requirements.txt requirements.txt

RUN mkdir records

ADD detectSoundPi.py .
ADD detectSoundESP.py .
ADD braided.json .
ADD googleS2T.py .
ADD filter.py .
ADD start.py .
# ADD css400.db .
ADD web.py .
RUN mkdir templates
COPY templates/ templates/

RUN python3 -m pip install -r requirements.txt


EXPOSE 10555 8888 6543 5000 4444
EXPOSE 4444/udp

CMD [ "python3", "start.py" ]
