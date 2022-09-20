# HAProxy x SteadyBreeze

This repo contains modifications made to HAProxy load balancer with the goal of allowing the consideration of electricity prices / market when allocating resources across multiple different electricity price regions.

## Getting Started
First download Docker and run the commands below on the host machine (powershell or terminal). If no errors occurred, the HAProxy server should be visible in localhost:8000

```
docker build -t my-haproxy .
docker network create --subnet=172.18.0.0/16 haproxy_network1
docker run -d --net haproxy_network1  --ip 172.18.0.22 -p 8000:80 --name my-running-haproxy my-haproxy
```

For running the Python servers cd to python_server and run the commands below. Note that if you want to run multiple servers change the python-server to a unique value for all servers (e.g. python-server1…n) and for each separate instance the servers must run in unique ports of the host machine. This is specified with the first port in --publish header. For each separate instance the port before the colon must be changed to a specific one. The port after the colon must always be 5000 as the containers always open port 5000 for the flask server.

```
docker build --tag python-server .
docker run --publish 5000:5000 python-server
```

**Note that when adding new servers to haproxy.cfg file’s backends the host must be set to host.docker.internal.**

Then inside the haproxy container you can run:

```
/bin/bash
./test_load.sh
```

This will run a script that sends repeated requests to the load balancer using curl.