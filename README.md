# Who's Home

Simple service that allows infrastructure spread out in unknown networks to call home and indicate where they are located. Should probably not be trusted, but gives an indication.

# Setup

## Server

Hosted on Kubernetes somewhere public. Requires a secret to be configured to work

> kubectl create secret generic jwt-secrets --from-literal=secret=supersecret

Then simply apply the deployment

> kubectl apply -f kustomize/deployment.yaml