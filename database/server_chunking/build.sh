docker build -t server-chunking-app -f DockerFile .

docker run -d -p 8000:8000 server-chunking-app