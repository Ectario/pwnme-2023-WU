FROM alpine:3.16.0

ARG DEBIAN_FRONTEND=noninteractive
WORKDIR /app/

RUN apk add socat python3 py-pip

RUN python3 -m pip install pycryptodome

COPY ./server.py /app/

RUN addgroup -S ctf && \
    adduser -S player -G ctf && \
    chmod u+s /app/server.py


ARG FLAG
RUN echo "PWNME{h4st4rd_br0adc4st_d3str0y_s1mple_p4dd1ng}" >> /app/flag.txt

RUN chown player:ctf /app/server.py
USER player

ENTRYPOINT ["socat","TCP-LISTEN:3000,reuseaddr,fork","EXEC:'python3.10 /app/server.py',stderr"]