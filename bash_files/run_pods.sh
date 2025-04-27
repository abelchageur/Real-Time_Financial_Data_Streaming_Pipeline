# /bin/bash
# kubectl logs $(kubectl get pods -l app=sparkstreaming -o name)
# kubectl exec -it $(kubectl get pods -l app=spark-master -o name) -- /bin/bash
# docker build --no-cache -t fintech/spark-streaming:latest ./spark
# docker build --no-cache -t fintech/spark-streaming:latest ./streamlit
# docker build --no-cache -t fintech/streamlit:latest ./streamlit
# kubectl delete -f deployments/data-processing-deployments.yaml
# kubectl delete -f deployments/spark-deployments.yaml 
# kubectl apply -f deployments/data-processing-deployments.yaml
# kubectl apply -f deployments/spark-deployments.yaml 





docker run -d -p 5000:5000 --name registry registry:2

docker build --no-cache -t fintech/data-ingestion:latest ./ingestion
docker build --no-cache -t fintech/spark-streaming:latest ./spark
docker build --no-cache -t fintech/spark-streaming:latest ./streamlit

kubectl apply -f secrets/

# Créer les ConfigMaps
kubectl apply -f configmaps/
# Créer les services
kubectl apply -f services/
# Déployer Zookeeper, Kafka et Cassandra
kubectl apply -f deployments/zookeeper-deployment.yaml
kubectl apply -f deployments/kafka-deployment.yaml
kubectl apply -f deployments/kafka-ui-deployment.yaml
kubectl apply -f deployments/cassandra-deployment.yaml

kubectl wait --for=condition=ready pod -l app=cassandra --timeout=10s
kubectl apply -f jobs/kafka-topics_job.yaml
kubectl wait --for=condition=ready pod -l app=cassandra --timeout=300s
# Initialiser Cassandra
kubectl apply -f jobs/cassandra-init-job.yaml
# Déployer Spark
kubectl apply -f deployments/spark-deployments.yaml
# Déployer les applications de traitement de données
kubectl apply -f deployments/data-processing-deployments.yaml
