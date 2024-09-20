FROM python:3.11.7

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERD 1

WORKDIR /app

RUN apt-get update && apt-get install -y \
	build_essential \
	libpq-dev \
	&& rm -rf /var/lib/apt/lists/*

COPY ../requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY ../ .

ENV FLASK_APP=run.py
ENV FLASK_ENV=production
EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0", "run:app"]