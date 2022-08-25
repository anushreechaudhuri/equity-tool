# Building Upgrade Equity Tool

The equity tool is a mapping and reporting tool built using Streamlit and Carto.

## Installation and Deployment with Docker (recommended)

In your server, use the [docker platform](https://docs.docker.com/get-docker/) to install the Equity Tool.

```bash
docker pull anuc/equity-tool:latest
docker run -it -p DESIRED_PORT_NUMBER_HERE:8501 anuc/equity-tool:latest
```

To leave the app running in the background, remove ```-it``` from the second command.

## Installation Without Docker

You can find guides on [this Streamlit blog](https://docs.streamlit.io/knowledge-base/deploy/deploy-streamlit-heroku-aws-google-cloud) to deploy to popular cloud services by cloning this GitHub repository and self-hosting the data.

## Structure
All app files are in ```equity-tool/streamlit```. The main page of the app is at 1_👋_Welcome.py. Subpages, which appear in the sidebar, are located in ```equity-tool/streamlit/pages```.

The files in ```equity-tool/process``` include all scripts used to clean and format the data.
## Contributing
Please email to gain access to the datasets to run this app locally.
## License
[MIT](https://choosealicense.com/licenses/mit/)
