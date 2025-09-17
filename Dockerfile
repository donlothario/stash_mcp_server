FROM python:3.12.11-alpine3.22

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
RUN python3 -m pip install .

CMD ["stash_mcp_server"]
