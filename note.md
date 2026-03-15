kubectl config view --minify --raw

kubectl scale deployment --all --replicas=0 -n dev-argocd

http://argocd.manhhung20033004.io.vn:32777


kubectl apply -f https://raw.githubusercontent.com/flannel-io/flannel/master/Documentation/kube-flannel.yml

kubectl taint nodes --all node-role.kubernetes.io/control-plane- 


## install on master, worker
mkdir -p /opt/cni/bin

curl -L https://github.com/containernetworking/plugins/releases/download/v1.5.1/cni-plugins-linux-amd64-v1.5.1.tgz \
| tar -C /opt/cni/bin -xz

###
helm install istio-base istio/base -n istio-system --set defaultRevision=default --create-namespace
helm install istiod istio/istiod -n istio-system --wait
helm ls -n istio-system
kubectl create namespace istio-ingress
helm install istio-ingress istio/gateway -n istio-ingress --wait

##
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.29/samples/addons/kiali.yaml
kubectl port-forward svc/kiali -n istio-system 20001

##
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.29/samples/addons/prometheus.yaml
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.29/samples/addons/grafana.yaml
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.29/samples/addons/jaeger.yaml

##
curl -L https://istio.io/downloadIstio | sh -

    cd istio-1.29.1
    export PATH=$PWD/bin:$PATH

##
while true; do curl http://172.18.0.5/productpage; done

## Cai api-gateway cua istio

istioctl install --set components.ingressGateways[0].name=istio-ingressgateway \
--set components.ingressGateways[0].enabled=true -y

## install metrics kube metrics server