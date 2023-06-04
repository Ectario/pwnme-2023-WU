FROM ubuntu:rolling as build

WORKDIR /app/

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
    libssl-dev \
    gcc

COPY ./main.c /app/

RUN gcc -s -O3 -o chall.bin main.c -lssl -lcrypto \
        -Wl,-z,relro,-z,now -D_FORTIFY_SOURCE=1

FROM ubuntu:rolling

WORKDIR /app/

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
    libssl-dev \
    socat

COPY --from=build /app/chall.bin /app/

RUN useradd --system player -U && \
    chmod u+s /app/chall.bin

RUN echo "PWNME{3ll1pt1c_cUrv3s_4r3_s0_S3xy_m4th3maticaly_sp34k1ng}" > /app/flag.txt
RUN chown player:player /app/chall.bin
USER player

ENTRYPOINT ["socat","TCP-LISTEN:3000,reuseaddr,fork","EXEC:'./chall.bin',stderr"]
