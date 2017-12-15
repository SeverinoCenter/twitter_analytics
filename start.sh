docker build -t kuberlytics/twitter:latest -t kuberlytics/twitter:v0.1 .
docker-compose -f docker-compose-CeleryExecutor.yml up -d
