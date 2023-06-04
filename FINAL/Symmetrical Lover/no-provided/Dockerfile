FROM alpine:3.16.0

ARG DEBIAN_FRONTEND=noninteractive
WORKDIR /app/

RUN apk add socat python3 py-pip

RUN python3 -m pip install pycryptodome

COPY ./server.py ./utils.py /app/

RUN addgroup -S ctf && \
    adduser -S player -G ctf && \
    chmod u+s /app/server.py

RUN echo "PWNME{b4d_sch3ma_ar3n_t_g00d_on_crypt0gr4phy___}" > /app/flag.txt
RUN chown player:ctf /app/server.py
USER player

ENTRYPOINT ["socat","TCP-LISTEN:3000,reuseaddr,fork","EXEC:'python3.10 /app/server.py',stderr"]