FROM nvidia/cuda:11.1.1-cudnn8-devel-ubuntu20.04

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /translation-app/Backend

COPY ./Backend/requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]