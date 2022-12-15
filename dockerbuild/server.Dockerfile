FROM wh1isper/debian-python-3.8

RUN rm -rf /etc/pip.conf && mkdir -p /opt/rtc


WORKDIR /opt/rtc
RUN pip install fint_rtc_server
COPY dockerbuild/fps.toml /opt/rtc

# example file here
RUN mkdir -p /var/fint/rtc-room && mkdir -p /var/fint/rtc-server/anonymous
COPY dockerbuild/example/* /var/fint/rtc-server/anonymous/

EXPOSE 8080

CMD ["fps-uvicorn"]

# docker build -t wh1isper/fint-rtc-server -f dockerbuild/server.Dockerfile .
