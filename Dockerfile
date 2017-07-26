FROM easypi/alpine-arm

RUN apk update && apk add python2 py-pip py-geoip gcc python-dev linux-headers musl-dev geoip geoip-dev ca-certificates
RUN pip install python-geoip
RUN pip install python-geoip-geolite2
RUN pip install geoip
RUN pip install pyasn
COPY ./ipasn_20160805.dat /
COPY ./ripe-ping.py /
EXPOSE 9001
CMD ["python2", "/ripe-ping.py"]
