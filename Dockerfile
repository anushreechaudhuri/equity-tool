FROM debian:stable-slim

## Basic dependencies
RUN apt-get clean && apt-get update -y -qq
RUN apt-get install -y curl git build-essential

# Install Anaconda3
ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"
RUN apt-get install -y wget && rm -rf /var/lib/apt/lists/*
RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh

# Set the conda version!
RUN conda --version
RUN conda install python=3.8

WORKDIR /app
RUN apt-get update
COPY streamlit/packages.txt packages.txt
RUN xargs apt-get install -y  <packages.txt
RUN xargs apt-get install -y build-essential
RUN conda install -c conda-forge gdal
RUN conda install -c conda-forge fiona
RUN python -m pip install --upgrade pip
COPY streamlit/requirements.txt ./requirements.txt
RUN python -m pip install -r requirements.txt
EXPOSE 8501
COPY . /app
WORKDIR /app/streamlit
CMD ["streamlit","run","1_👋_Welcome.py"]
