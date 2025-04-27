#!/bin/bash
# Delete existing resources
kubectl delete -f deployments/ -f services/ -f configmaps/ -f storage/ -f secrets/ -f jobs/

kubectl get pods