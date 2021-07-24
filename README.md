# adjust-task
**Prerequisites:**
1. Python3  https://www.python.org/downloads/
2. Pipenv   https://pipenv.pypa.io/en/latest/install/ 
3. Docker   https://docs.docker.com/get-docker/
4. Minikube https://minikube.sigs.k8s.io/docs/start/

**This project has been tested on:**\
`Python 3.9.6`\
`Docker version 20.10.7, build f0df350` \
`minikube version: v1.22.0 (commit: a03fbcf166e6f74ef224d4a63be4277d017bb62e)`

although other versions should work as well, I recommend using these or higher.

**How to run:**

1. Checkout this repository, open terminal and make sure you're in the repository's root directory
2. Run `pipvenv install` to activate Python's virtual environment and install required packages
3. Run the script with `python3 main.py -n ruby-server -del=True`\
NOTE:\
`-n`    argument specifies the name of the K8S deployment and docker image\
`-del`  argument is used to determined whether to delete the minikube cluster (if any is present).\
It is recommended to set this argument to true to ensure a fresh cluster is started with correct settings. However it will DELETE your existing minikube cluster, so make sure you do not need it anymore.
4. Your application is deployed to your minikube cluster now.\
 In order to expose it on local host run `minikube tunnel`.\
 Open new terminal window and test with `curl -X GET http://127.0.0.1:8080`\
 some versions of curl will require to pass `--http0.9` option to be able to process server's responses.
 
**Architecture:**

To ensure high availability cluster is stared with 3 nodes.\
Deployment mainfest has Pod Anti-affinity specified to distribute pods across all nodes as much as possible.\
Liveness and Readiness probes are configured to monitor `/healthcheck ` endpoint to ensure the application is ready to accept traffic before any is sent.\
K8S service object ensures traffic is loadbalanced between the pods.\

TODO:
1. Add Horizontal Pod Autoscaler bring more pods up as CPU usage goes up.
2. Add ingress-controller and relevant configuration for the service to utilize reverse proxy advantages
  
