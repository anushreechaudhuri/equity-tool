FROM python:3.8
WORKDIR /app
COPY streamlit/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
EXPOSE 8501
COPY . /app
WORKDIR /app/streamlit
ENTRYPOINT ["streamlit", "run"]
CMD ["1_👋_Welcome.py"]