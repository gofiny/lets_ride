FROM python:3.9

RUN mkdir -p /usr/src/app/
WORKDIR /usr/src/app/

EXPOSE 8000

COPY . /usr/src/app/
RUN pip install --no-cache-dir -r req.txt

CMD ["uvicorn", "app:app", "--workers 2"]