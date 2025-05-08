FROM ubuntu:20.04

USER root

ENV TZ=America/Los_Angeles
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    apt-get --yes update && \
    apt-get install -y wget build-essential nodejs npm rsync && \
    npm install -g --yes yuglify cssmin uglify-es && \
    wget https://repo.anaconda.com/miniconda/Miniconda3-py39_23.11.0-2-Linux-x86_64.sh && \
    bash Miniconda3-py39_23.11.0-2-Linux-x86_64.sh -b

ENV PATH=/root/miniconda3/bin:${PATH}

RUN conda update -n base -c defaults conda && \
    conda install -y pip ipython && \
    conda install -y -c conda-forge selenium libsass && \
    pip install gunicorn webdriver-manager && \
    mkdir /code

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.6.0/wait /wait
RUN chmod +x /wait

ADD requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir -r /code/requirements.txt
ADD . /code/

ADD docker_init*.sh /code/
RUN chmod +x /code/docker_init*.sh

# Copy environment file and ensure it exists
COPY docker.env /code/.env
RUN touch /code/.env

WORKDIR /code

# Create static directory and collect static files during build
RUN mkdir -p /code/static && \
    python manage.py collectstatic --noinput

CMD /code/docker_init_production.sh