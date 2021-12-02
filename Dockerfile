FROM python:3
RUN apt-get update && \
    apt-get install -y openssl c3270
WORKDIR /web3270
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
RUN openssl req -x509 -nodes -days 365 \
    -subj  "/C=CA/ST=QC/O=web3270 Inc/CN=3270.web" \
    -newkey rsa:2048 -keyout ca.key \
    -out ca.csr
ADD run.sh index.html server.py web3270.ini login.html favicon.ico 3270-Regular.woff ./
RUN chmod +x run.sh
VOLUME ["/config","/certs"]
EXPOSE 80 443
ENTRYPOINT ["/web3270/run.sh"]
