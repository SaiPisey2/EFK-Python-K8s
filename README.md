# EFK-Python-K8s
This project deploys an EFK stack (Elasticsearch, Fluentbit, Kibana) along with a Python application in Kubernetes, integrating Prometheus and Grafana for monitoring. It provides efficient log aggregation, search, and visualization, as well as real-time performance metrics.

### Project Contents
- Setup EKS Cluster
- Setup ElasticSearch
- Setup Kibana
- Setup Python app
- Setup Fluentbit
- Setup Prometheus
- Setup Grafana

### Prerequisites
- Install aws cli from [here](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- Install kubectl utility from [here](https://kubernetes.io/docs/tasks/tools/)
- Install Helm from here [here](https://helm.sh/docs/intro/install/)

### Setup EKS Cluster
 - Go to AWS console and go to EKS
 - Create Cluster with role `eksClusterRole`
 - After creation, create node groups with role `AmazonEKSNodeRole`
 - In the IAM section, attach `AmazonEBSCSIDriverPolicy` to `AmazonEKSNodeRole`
 - In the cluster Add ons section install `EBS Plugin`
 - Enter this command to connect to the cluster `aws eks update-kubeconfig --region <region> --name <cluster-name>`

### Setup ElasticSearch
 - Go to [elasticsearch](elasticsearch/)
```
kubectl create namespace python-efk
helm repo add elastic https://helm.elastic.co
helm install elasticsearch .
```

### Setup Kibana
- Go to [kibana](kibana/)
```
helm repo add elastic https://helm.elastic.co
helm install kibana .
```
#### Elastic Search and Kibana should be able to connect with each other.

### Setup Python app
- Go to [python-app](python-app/k8/)
```
kubectl apply -f .
```
This will deploy the python app to python-efk namespace.
It also contains a horizontal pod autoscaler which would autoscale the pod when utilization crosses 75%.

### Setup Fluent bit
- Go to [fluentbit](fluent-bit/)
```
Kubectl apply -f .
```
This will deploy fluent bit in python-efk namespace
Make sure to change to change the input filter and output according to the elasticsearch configs
```
[INPUT]
        Name tail
        Path /var/log/containers/python-app-deploy*.log
        multiline.parser docker, cri
        Tag kube.*
        Mem_Buf_Limit 5MB
        Skip_Long_Lines On
[OUTPUT]
        Name es
        Match kube.*
        Host efk-stack-master
        Port 9200
        Index python-app-logs
        tls On
        tls.verify Off
        HTTP_User elastic
        HTTP_Passwd elastic123!
        Logstash_Format On
        Retry_Limit False
        Suppress_Type_Name On
```

This should forward the logs in Elasticsearch
In kibana under index management you should be able to see this,
![image](https://github.com/user-attachments/assets/b9edc5c9-b62c-44d4-bbbc-c6fcea94863f)

And Kibana Dashboard will look something like this
![image](https://github.com/user-attachments/assets/279fa1b4-13db-417d-b498-90f35a842412)


### Setup Prometheus
- Go to [prometheus](prometheus/)
```
kubectl create namespace prometheus
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus . -n prometheus
```
This will deploy prometheus operator inside kubernetes cluster

### Setup Grafana
 - Go to [grafana](grafana/)
```
helm repo add grafana https://grafana.github.io/helm-charts
helm install grafana . -n prometheus
```
Once Grafana is up, add prometheus connector
Grafana dashboard will look like this
![grafana](https://github.com/user-attachments/assets/644132fd-83db-4616-8559-c9008dbd5459)


## Thank you. Have a good day!
