# FROM ${naerm_core_image_name}:${naerm_core_image_tag}
ARG naerm_core_image_name=harbor.naerm.team/naerm-images/naerm_core
ARG naerm_core_image_tag=1.26.0

FROM ${naerm_core_image_name}:${naerm_core_image_tag}

RUN apt-get update

RUN apt-get -y install libgeos-dev


COPY . /PyDSS

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools

WORKDIR /PyDSS
RUN pip install -e .

ENV PYTHONPATH=/PyDSS/PyDSS/api/src

WORKDIR /PyDSS/PyDSS/api/src

EXPOSE 5000/tcp

# Change directory to the src folder
# python main.py -l ../logging.yaml -e ../endpoints.yaml -c config.yaml
CMD [ "python", "main.py", "-l", "../logging.yaml", "-e", "../endpoints.yaml", "-c", "config.yaml" ]
