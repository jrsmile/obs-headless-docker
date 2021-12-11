FROM dorowu/ubuntu-desktop-lxde-vnc
LABEL maintainer "jrsmile"

ENV DEBIAN_FRONTEND noninteractive

ENV OBS_VERSION 27.1.3-0obsproject1~focal
RUN apt-get update \
    && apt-get install -y software-properties-common curl \
    && add-apt-repository "ppa:obsproject/obs-studio" \
    && add-apt-repository "ppa:savoury1/multimedia" \
    && add-apt-repository "ppa:savoury1/graphics" \
    && add-apt-repository "ppa:savoury1/ffmpeg4" \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    ffmpeg \
    obs-studio \
    vlc \
    qt5-image-formats-plugins \
    srt-tools \
    build-essential \
    tclsh \
    pkg-config \
    cmake \
    libssl-dev \ 
    zlib1g-dev \
    git \
    openssl \
    python3-pip \
    && apt-get autoclean \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Add obs websocket

RUN curl -sL -o "/tmp/obs-websocket.deb" 'https://github.com/obsproject/obs-websocket/releases/download/4.9.1/obs-websocket_4.9.1-1_amd64.deb' && \
    sudo dpkg -i "/tmp/obs-websocket.deb"

# Add SLS Server

WORKDIR /tmp
RUN git clone https://github.com/Haivision/srt.git && cd srt && ./configure && make && make install

#RUN git clone https://github.com/Edward-Wu/srt-live-server.git && cd srt-live-server && make && cp bin/sls /usr/local/bin/
#RUN git clone https://github.com/odensc/srt-live-server.git && cd srt-live-server && make && cp bin/sls /usr/local/bin/
RUN git clone https://github.com/jrsmile/srt-live-server.git && cd srt-live-server && make && cp bin/sls /usr/local/bin/

COPY sls.conf /etc/sls/

COPY supervisor-sls.conf /etc/supervisor/conf.d/


# add scene switch logic

RUN pip install obs-websocket-py fastapi "uvicorn[standard]"

COPY supervisor-logic.conf /etc/supervisor/conf.d/

COPY logic.py /opt/

COPY obs-settings/ /root/.config/obs-studio/

COPY media/ /root/media/

# autostart obs and start streaming

COPY supervisor-obs.conf /etc/supervisor/conf.d/

# relay output stream to twitch
COPY startup.sh /
COPY supervisor-twitch.conf /opt
