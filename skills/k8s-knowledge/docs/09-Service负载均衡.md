k8s四层负载均衡 -service 知识点解读

**1.1 四层负载均衡 Service：概念、原理解读**
**1.1.1 为什么要有 Service？**
在kubernetes 中，Pod是有生命周期的，如果 Pod重启它的 IP很有可能会发生变化。如果我们的服
务都是将 Pod的IP地址写死， Pod挂掉或者重启，和刚才重启的 pod相关联的其他服务将会找不到它所
关联的Pod，为了解决这个问题，在 kubernetes 中定义了 service 资源对象， Service 定义了一个服务

 访问的入口，客户端通过这个入口即可访问服务背后的应用集群实例， service 是一组Pod的逻辑集合，
这一组Pod能够被Service 访问到，通常是通过 Label Selector 实现的。
可以看下面的图：

**1、pod ip经常变化， service 是pod的代理，我们客户端访问，只需要访问 service，就会把请求**
代理到Pod

**2、pod ip在k8s集群之外无法访问，所以需要创建 service，这个service 可以在k8s集群外访问**
的。

**1.1.2 Service 概述**
service 是一个固定接入层，客户 端可以通过访问 service 的ip和端口访问到service 关联的后端
pod，这个service 工作依赖于在 kubernetes 集群之上部署的一个附件，就是 kubernetes 的dns服务
（不同kubernetes 版本的dns默认使用的也是不一样的， 1.11之前的版本使用的是 kubeDNs，较新的版
本使用的是 coredns），service 的名称解析是依赖于 dns附件的，因此在部署完 k8s之后需要 再部署dns
附件，kubernetes 要想给客户端提供网络功能，需要依赖第三方的网络插件（ flannel，calico等）。每
个K8s节点上都有一个组件叫做 kube-proxy，kube-proxy这个组件将始终监视着 apiserver 中有关
service 资源的变动信息 ，需要跟 master之上的apiserver 交互，随时连接到 apiserver 上获取任何一
个与service 资源相关的资源变动状态 ，这种是通过 kubernetes 中固有的一种请求方法 watch（监视）
来实现的，一旦有 service 资源的内容发生变动（如创建，删除） ， kube-proxy都会将它转化成当前节点
之上的能够实现 service 资源调度，把我们请求调度到后端特定的 pod资源之上的规则，这个规则可能
是iptables ，也可能是 ipvs，取决于 service 的实现方式 。

**1.1.3 Service 工作原理**
k8s在创建Service 时，会根据标签选择器 selector(lable selector) 来查找Pod，据此创建与
Service同名的endpoint 对象，当 Pod 地址发生变化时， endpoint 也会随之发生变化， service 接收前
端client请求的时候，就会通过 endpoint ，找到转发到 哪个Pod进行访问的地址。 (至于转发到哪个节
点的Pod，由负载均衡 kube-proxy决定)

**1.1.4 kubernetes 集群中有三类 IP地址**
**1、Node Network（节点网络） ：物理节点或者虚拟节点的网络，如 ens33接口上的网路地址**

```bash
 [root@xianchaomaster1  ~]# ip addr
2: ens33: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP
    link/ether 00:0c:29:87:60:d5 brd ff:ff:ff:ff:ff:ff
inet 192.168.1.63/24 brd 192.168.1.255 scope global noprefixroute ens33
```

**2、Pod network （pod 网络） ，创建的Pod具有的IP地址**

```bash
[root@xianchao master1 ~]# kubectl get pods -o wide
NAME             READY   STATUS          IP               NODE
frontend -h78gw   1/1       Running       10.244.187.76     xianchaonode2
```
Node Network和Pod network 这两种网络地址是我们实实在在配置的，其中节点网络地址是配置在
节点接口之上，而 pod网络地址是配置在 pod资源之上的，因此这些地址都是配置在某些设备之上的，
这些设备可能是硬件，也可能是软件模拟的

**3、Cluster Network （集群地址， 也称为service network ） ，这个地址是虚拟的地址（ virtual**
ip） ，没有配置在某个接口上，只是出现在 service 的规则当中 。

```bash
[root@xianchaomaster1  ~]# kubectl get svc
NAME               TYPE        CLUSTER -IP      EXTERNAL -IP   PORT(S)
kubernetes         ClusterIP   10.96.0.1           <none>        443/TCP
```

**1.2 创建Service 资源**

```bash
#查看定义 Service 资源需要的字段有哪些？
[root@xianchaomaster1  ~]# kubectl explain service
```

```yaml
KIND:     Service
VERSION:  v1
DESCRIPTION:
     Service is a named abstraction of software service (for example, mysql)
     consisting of local port (for example 3306) that the proxy listens on, and
     the selector that determines which pods will answer requests sent th rough
     the proxy.
FIELDS:
   apiVersion  <string>  #service 资源使用的 api组
   kind <string>           #创建的资源类型
   metadata  <Object>      #定义元数据
   spec <Object>

#查看service 的spec字段如何定义？
```

```bash
[root@xianchaomaster1  ~]# kubectl explain service.spec
```

```yaml
KIND:     Serv ice
VERSION:  v1
RESOURCE: spec <Object>
DESCRIPTION:
     Spec defines the behavior of a service.

      https://git.k8s.io/community/contributors/devel/sig -architecture/api -
conventions.md#spec -and-status
     ServiceSpec describes the attributes that a user creates on a service.
FIELDS:
   allocateLoadBalancerNodePorts  <boolean>
   clusterIP  <string>
#动态分配的地址，也可以自己在创建的时候指定，创建之后就改不了了
   clusterIPs  <[]string >
   externalIPs  <[]string>
   externalName  <string>
   externalTrafficPolicy  <string>
   healthCheckNodePort  <integer>
   ipFamilies  <[]string>
   ipFamilyPolicy  <string>
   loadBalancerIP  <string>
   loadBalancerSourceRanges  <[]string>
   ports <[]Object>  #定义service 端口，用来和后端 pod建立联系
   publishNotReadyAddresses  <boolean>
   selector  <map[string]string> #通过标签选择器选择关联的 pod有哪些
   sessionAffinity  <string>
   sessionAffinityConfig  <Object>
#service 在实现负载均衡的时候还支持 sessionAffinity ，sessionAffinity
```
什么意思？会话联系，默认是 none，随机调度的（基于 iptables 规则调度的） ；如果我们定义
sessionAffinity 的client ip ，那就表示把来自同一客户端的 IP请求调度到同一个 pod上
   topologyKeys  <[]string>
   type <string>  #定义service 的类型

**1.2.1 Service 的四种类型**

```bash
#查看定义 Service.spec.type 需要的字段有哪些？
 [root@xianchaomaster1  ~]# kubectl explain service.spec.type
```

```yaml
KIND:     Service
VERSION:  v1
FIELD:    type <string>
DESCRIPTION:
     type determines how the Service is exposed. Defaults to  ClusterIP . Valid
     options are ExternalName , ClusterIP , NodePort , and LoadBalancer .
     "ClusterIP" allocates a cluster -internal IP address for load -balancing to
     endpoints. Endpoints are determined by the selector or if that is not
     specified, by manual construction of an Endpoints object or EndpointSlice
     objects. If clusterIP is "None", no virtual IP is allocated and the
     endpoints are published as a set of endpoints rather than a virtual IP.
     "NodePort" builds on ClusterIP and allocates a port on every node which
     routes to the same endpoints as t he clusterIP. "LoadBalancer" builds on
```

      NodePort and creates an external load -balancer (if supported in the current
     cloud) which routes to the same endpoints as the clusterIP. "ExternalName"
     aliases this service to the specified externalName.  Several other fields do
     not apply to ExternalName services. More info:
     https://kubernetes.io/docs/concepts/services -networking/service/#publishing -
services -service-types

**1、ExternalName ：**
适用于k8s集群内部容器访问外部资源 ，它没有selector ，也没有定义任何的端口和 Endpoint 。
以下Service 定义的是将prod名称空间中的 my-service 服务映射到 my.database.example.com

```yaml
kind: Service
apiVersion: v1
metadata:
  name: my -service
  namespace: prod
spec:
  type: ExternalName
  externalName: my.database.example.com
```
当查询主机  my-service.prod.svc.cluster.local 时，群集 DNS将返回值为
my.database.example.com 的CNAME记录。

service 的FQDN 是： <service_name>.<namespace>.svc.cluster.local
                   my-service.prod. svc.cluster.local

**2、ClusterIP ：**
通过k8s集群内部 IP暴露服务，选择该值，服务只能够在集群内部访问，这也是默认的
ServiceType 。

**3、NodePort :**
通过每个 Node节点上的IP和静态端口暴露 k8s集群内部的 服务。通过请求 <NodeIP>:<NodePort> 可
以把请求代理到内部的 pod。Client----->NodeIP:NodePort ----->Service Ip:ServicePort ----

**4、LoadBalancer :**
使用云提供商的负载 均衡器，可以向外部 暴露服务。外部的负载均衡器可以路由到 NodePort 服务和
ClusterIP  服务。

**1.2.2 Service 的端口**

```bash
#查看service 的spec.ports字段如何定义？
[root@xianchaomaster1  ~]# kubectl explain service.spec.ports
```

```yaml
KIND:     Service
VERSION:  v1

 RESOURCE: ports <[]Object>
DESCRIPTION:
     The list of ports that are exposed by this service. More info:
     https://kubernetes.io/docs/concepts/services -networking/service/#virtual -ips-
and-service-proxies
     ServicePort contains information on service's port.
FIELDS:
   appProtocol  <string>
   name <string>  #定义端口的名字
   nodePort  <integer>
|#宿主机上映射的端口， 比如一个 Web应用需要被 k8s集群之外的 其他用户访问，那么需要配置
```
type=NodePort ，若配置nodePort=30001 ，那么其他机器就可以通过浏览器访问 scheme://k8s 集群中的
任何一个节点 ip:30001即可访问到该服务，例如 http://192.168.1.63:30001 。如果在k8s中部署
MySQL数据库，MySQL可能不需要被外界访问，只需被内部服务访问，那么 就不需要设置 NodePort
   port <integer> -required -  #service 的端口，这个是 k8s集群内部服务可访问的端口
   protocol  <string>
   targetPort  <string>
# targetPort 是pod上的端口，从 port和nodePort 上来的流量，经过 kube-proxy流入到后端 pod
的targetPort 上，最后进入容器。与制作容器时暴露的端口一致（使用 DockerFile 中的EXPOSE） ，例如
官方的nginx暴露80端口。

**1.4 创建Service：type类型是ClusterIP**
**1、创建Pod**

```bash
#把nginx.tar.gz 上传到xianchaonode2 和xianchaonode1 ，手动解压
[root@xianchaonode1  ~]# docker load -i nginx.tar.gz
[root@xianchaonode2  ~]# docker load -i nginx.tar.gz
[root@xianchaomaster1  ~]# cat pod_test.yaml
```

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my -nginx
spec:
  selector:
    matchLabels:
      run: my-nginx
  replicas: 2
  template:
    metadata:
      labels:
        run: my-nginx
    spec:
      containers:

       - name: my -nginx
        image: nginx
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 80  #pod中的容器需要暴露的端口

#更新资源清单文件
```

```bash
[root@xianchaomaster1  ~]# kubectl apply -f pod_test.yaml

#查看刚才创建的 Pod ip地址
[root@xianchaomaster1  ~]# kubectl get pods -l run=my -nginx -o wide
NAME                             STATUS           IP                   NODE
my-nginx-5b56ccd65f -26vcz       Running          10.244. 187.101      xianchaonode2
my-nginx-5b56ccd65f -95n7p       Running         10.244.209.149      xianchaonode1

#请求pod ip地址，查看结果
[root@xianchaomaster1  ~]# curl 10.244.187.101
<!DOCTYPE html>
<html>
<h1>Welcome to nginx!</h1>
</body>
</html>

[root@xianchaomaster1  ~]# curl 10.244.209.149
<!DOCTYPE html>
<html>
<h1>Welcome to nginx!</h1>
</body>
</html>

[root@xianchaomaster1  ~]# kubectl exec -it my-nginx-5b56ccd65f -26vcz -- /bin/bash
root@my-nginx-5b56ccd65f -26vcz:/# curl 10.244.209.149
<!DOCTYPE htm l>
<html>
<h1>Welcome to nginx!</h1>
</html>
root@my-nginx-5b56ccd65f -26vcz:/#exit
```

需要注意的是， pod虽然定义了容器端口，但是 不会使用 调度到该节点上的 80端口，也不会使用任
何特定的 NAT规则去路由流量到 Pod上。 这意味着可以在同一个节点上运行多个  Pod，使用相同的容器
端口，并且可以从集群中任何其他的 Pod或节点上使用 IP的方式访问到它们。

误删除其中一个 Pod：

```bash
 [root@xianchaomaster1  service]# kubectl delete pods my -nginx-5b56ccd65f -26vcz
pod "my-nginx-5b56ccd65f -26vcz" deleted
[root@xianchaomaster1  service]# kubectl get pods -l run=my -nginx -o wide
NAME                          STATUS         IP               NODE
my-nginx-5b56ccd65f -7xzr4    Running       10.244.187.102   xianchaonode2
my-nginx-5b56ccd65f -95n7p     Running     10.244.209.149   xianchaonode1
```

通过上面可以看到重新生成了一个 pod ：my-nginx-5b56ccd65f -7xzr4，ip是10.244.187.102 ，在
k8s中创建pod，如果pod被删除了，重新生成的 pod ip地址会发生变化，所以需要 在pod前端加一个
固定接入层。接下来创建 service：

查看pod标签：

```bash
[root@xianchaomaster1 service]# kubectl get pods --show-labels
```

**2、创建Service**

```bash
[root@xianchaomaster1  service]# cat service_test.yaml
```

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my -nginx
  labels:
    run: my-nginx
spec:
  type: ClusterIP
  ports:
  - port: 80   #service 的端口，暴露给 k8s集群内部服务访问
    protocol: TCP
    targetPort: 80    #pod容器中定义的端口
  selector:
    run: my-nginx  #选择拥有 run=my-nginx标签的pod

```
上述yaml文件将创建一个  Service，具有标签 run=my-nginx的Pod，目标TCP端口 80，并且在一
个抽象的 Service 端口（targetPort ：容器接收流量的端口； port：抽象的  Service 端口，可以使任何
其它 Pod访问该 Service 的端口）上暴露。

```bash
[root@xianchaomaster1  service]# kubectl apply -f service_test.yaml
service/my -nginx created

[root@xianchaomaster1  ~]# kube ctl get svc -l run=my -nginx
NAME       TYPE        CLUSTER -IP      EXTERNAL -IP   PORT(S)   AGE
my-nginx   ClusterIP   10.99.198.177    <none>        80/TCP    143m

#在k8s控制节点访问 service 的ip:端口就可以把请求代理到后端 pod

 [root@xianchaomaster1  ~]# curl 10.99.198.177:80
<!DOCTYPE html>
<html>
<h1>Welcome to nginx!</h1>
</html>
#通过上面可以看到请求 service IP:port 跟直接访问 pod ip:port看到的结果一样，这就说明
```
service 可以把请求代理到它所关联的后端 pod
> **注意：上面的10.99.198.177:80 地址只能是在 k8s集群内部可以访问，在外部无法访问，比方说我**
们想要通过浏览器访问，那么是访问不通的，如果想要在 k8s集群之外访问，是需要把 service type类
型改成nodePort 的

```bash
#查看service 详细信息
[root@xianchaomaster1  ~]# kubectl describe svc my -nginx
Name:              my -nginx
Namespace:         default
Labels:            run=my -nginx
Annotations:       <none>
Selector:          run=my -nginx
```

```yaml
Type:              ClusterIP
IP Families:       <none>
IP:                10.99.198.177
IPs:               10.99.198.177
Port:              <unset>  80/TCP
TargetPort:        80/TCP
Endpoints:         10.244.187.102:80,10.244.209.149:80
Session Affinity:  None
Events:            <none>

```

```bash
[root@xianchaomaster1  ~]# kubectl get ep my -nginx
NAME       ENDPOINTS                             AGE
my-nginx   10.244.187.102:80,10.244.209.149:80   142m
```

service 可以对外提供统一固定的 ip地址，并将请求重定向至集群中的 pod。其中“将请求重定向
至集群中的 pod”就是通过 endpoint 与selector 协同工作实现。 selector 是用于选择 pod，由
selector 选择出来的 pod的ip地址和端口号，将会被记录在 endpoint 中。endpoint 便记录了所有 pod
的ip地址和端口号。当一个请求访问到 service 的ip地址时，就会从 endpoint 中选择出一个 ip地址
和端口号，然后将请求重定向至 pod中。具体把请求代理到哪个 pod，需要的就是 kube-proxy的轮询实
现的。service 不会直接到 pod，service 是直接到 endpoint 资源，就是地址加端口，再由 endpoint 再
关联到pod。

service只要创建完成，我们就可以直接解析它的服务名，每一个服务创建完成后都会在集群 dns中
动态添加一个资源记录，添加完成后我们就可以解析了 ，资源记录格式是：
SVC_NAME.NS_NAME.DOMAIN.LTD.

 服务名.命名空间 .域名后缀
集群默认的域名后缀是 svc.cluster.local.
就像我们上面创建的 my-nginx这个服务，它的完整名称解析就是
my-nginx.default.svc.cluster.local

```bash
[root@xianchaomaster1  ~]# kubectl exec -it my-nginx-5b56ccd65f -7xzr4 -- /bin/bash
root@my-nginx-5b56ccd65f -7xzr4:/# curl my -nginx.default.svc.cluster.local
<!DOCTYPE html>
<h1>Welcome to nginx!</h1>
root@my-nginx-5b56ccd65f -7xzr4:/# exit
```
**1.6 创建Service：type类型是NodePort**
**1、创建一个 pod资源**

```bash
[root@xianchaomaster1  ~]# cat pod_nodeport.yaml
```

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my -nginx-nodeport
spec:
  selector:
    matchLabels:
      run: my-nginx-nodeport
  replicas: 2
  template:
    metadata:
      labels:
        run: my-nginx-nodeport
    spec:
      containers:
      - name: my -nginx-nodeport -container
        image: nginx
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 80
#更新资源清单文件
```

```bash
[root@xianchaomaster1  ~]# kubectl apply -f pod_nodeport.yaml
deployment.apps/my -nginx-nodeport created
#查看pod是否创建成功
[root@xianchaomaster1  ~]# kubectl get pods -l run=my -nginx-nodeport
NAME                                 READY   STATUS    RESTARTS   AGE
my-nginx-nodeport -6f8c64fc6c-86wnc   1/1     Running   0          67s
my-nginx-nodeport -6f8c64fc6c -8wrpq   1/1     Running   0          67s
```

**2、创建service，代理pod**

```bash
[root@xianchaomaster1  ~]# cat service_nodeport.yaml

```

```yaml
 apiVersion: v1
kind: Service
metadata:
  name: my -nginx-nodeport
  labels:
    run: my-nginx-nodeport
spec:
  type: NodePort
  ports:
  - port: 80
    protocol: TCP
    targetPort: 80
    nodePort: 30380
  selector:
    run: my-nginx-nodeport

#更新资源清单文件
```

```bash
[root@xianchaomaster1  ~]# kubectl apply -f service_nodeport.yaml
service/my -nginx-nodeport created

#查看刚才创建的 service
[root@xianchaomaster1  ~]# kubectl get svc -l run=my -nginx-nodeport
NAME                TYPE       CLUSTER -IP     EXTERNAL -IP   PORT(S)
my-nginx-nodeport   NodePort   10.100.156.7   <none>        80:30380/TCP
#访问service
[root@xianchaomaster1  ~]# curl 10.100.156.7
<!DOCTYPE html>
<h1>Welcome to nginx!</h1>
</html>
```

> **注意：**
**10.100.156.7 是k8s集群内部的 service ip地址，只能在 k8s集群内部访问，在集群外无法访问。**

#在集群外访问 service
root@xianchaomaster1  ~]# curl 192.168.1.63:30380
<!DOCTYPE html>
<h1>Welcome to nginx!</h1>
</html>

#在浏览器访问 service

服务请求走向： Client-→node ip:30380->service ip:80 -→pod ip:container port
              Client ->192.168.1.63:30380 ->10.100.156.7:80 ->pod ip:80

**1.7 创建Service：type类型是ExternalName**

  应用场景：跨名称空间访问
需求：default 名称空间下的 client 服务想要访问 nginx-ns名称空间下的 nginx-svc服务

需要把busybox.tar.gz 上传到xianchaonode2 和xianchaonode1 上，手动解压，

```bash
[root@xianchaomaster1  exter]# docker load -i busybox.tar.gz
[root@xianchaomaster1  exter]# cat client.yaml
```

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: client
spec:
  replicas: 1
  selector:
    matchLabels:
      app: busybox
  template:
   metadata:
    labels:
      app: busybox
   spec:
     containers:
     - name: busybox
       image: busybox
       command: ["/bin/sh"," -c","sleep 36000"]
```

```bash
[root@xianchaomaster1  exter]# kubectl apply -f client.yaml
[root@xianchaomaster1  exter]# cat client_svc.yaml
```

```yaml
apiVersion: v1
kind: Service

 metadata:
  name: client -svc
spec:
  type: ExternalName
  externalName: nginx -svc.nginx -ns.svc.cluster.local
  ports:
  - name: http
    port: 80
    targetPort: 80

#该文件中指定了到  nginx-svc 的软链，让使用者感觉就好像调用自己命名空间的服务一样。
#查看pod是否正常运行
```

```bash
[root@xianchaomaster1  exter]# kubectl get pods
NAME                                 READY   STATUS      RESTARTS
client-76b6556d97 -xk7mg              1/1     Running      0
[root@xianchaomaster1  exter]# kubectl apply -f client_svc.y aml

[root@xianchaomaster1  exter]# kubectl create ns nginx -ns
[root@xianchaomaster1  exter]# cat server_nginx.yaml
```

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  namespace: nginx -ns
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
  template:
   metadata:
    labels:
      app: nginx
   spec:
     containers:
     - name: nginx
       image: nginx
       imagePullPolicy: IfNotPresent
```

```bash
[root@xianchaomaster1  exter]# kubectl apply -f server_nginx.yaml
#查看pod是否创建成功
[root@xianchaomaster1  exter]# kubectl get pods -n nginx-ns
NAME                     READY   STATUS    RESTARTS   AGE
nginx-7cf7d6dbc8 -lzm6j   1/1     Running   0          10m

 [root@xianchaomaster1  exter]# cat nginx_svc.yaml
```

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx -svc
  namespace: nginx -ns
spec:
  selector:
    app: nginx
  ports:
   - name: http
     protocol: TCP
     port: 80
     targetPort: 80
```

```bash
[root@xianchaomaster1  exter]# kubectl apply -f nginx_svc.yaml
#登录到client pod
[root@xianchaomast er1 exter]# kubectl exec -it  client -76b6556d97 -xk7mg -- /bin/sh
/ # wget -q -O - client-svc.default.svc.cluster.local
    wget -q -O - nginx-svc.nginx -ns.svc.cluster.local
```
上面两个请求的结果一样

**1.8 k8s最佳实践：映射外部服务案例分享**
场景1：k8s集群引用外部的 mysql数据库
在xianchaonode2 上安装mysql数据库：

```bash
[root@xianchaonode2  ~]# yum install mariadb -server.x86_64 -y
[root@xianchaonode2  ~]# systemctl start mariadb
[root@xianchaomaster1  mysql]# cat mysql_service.yaml
```

```yaml
apiVersion: v1
kind: Service
metadata:
  name: mysql
spec:
  type: ClusterIP
  ports:
  - port: 3306
```

```bash
[root@xianchaomaster1  mysql]# kubectl apply -f mysql_service.yaml
service/mysql created
[root@xianchaomaster1  mysql]# kubectl get svc | grep mysql
mysql               ClusterIP      10.107.232.103              330 6/TCP

root@xianchaomaster1  mysql]# kubectl describe svc mysql
Name:              mysql
Namespace:         default

 Labels:            <none>
Annotations:       <none>
Selector:          <none>
```

```yaml
Type:              ClusterIP
IP Families:       <none>
IP:                10.107.232.103
IPs:               10.107.232.103
Port:              <unset>  3306/TCP
TargetPort:        3306/TCP
Endpoints:         <none>  #还没有endpoint
Session Affinity:  None
Events:            <none>
```

```bash
[root@xianchaomaster1  mysql]# cat mysql_endpoint.yaml
```

```yaml
apiVersion: v1
kind: Endpoints
metadata:
  name: mysql
subsets:
- addresses:
  - ip: 192.168. 40.182
  ports:
  - port: 3306

```

```bash
[root@xianchaomaster1  mysql]# kubectl apply -f mysql_endpoint.yaml
endpoints/mysql created
[root@xianchaomaster1  mysql]# kubectl describe svc mysql
Name:              mysql
Namespace:         default
Labels:            <none>
Annotations:       <none>
Selector:          <none >
```

```yaml
Type:              ClusterIP
IP Families:       <none>
IP:                10.107.232.103
IPs:               10.107.232.103
Port:              <unset>  3306/TCP
TargetPort:        3306/TCP
Endpoints:         192.168.1.62:3306  # 这个就是定义的外部数据库
Session Affinity:  None
Events:            <none>
```
上面配置 就是将外部 IP地址和服务引入到 k8s集群内部，由 service 作为一个代理来达到能够访问
外部服务的目的。

**1.9 Service 代理：kube-proxy组件详解**
**1.9.1 kube-proxy组件介绍**
Kubernetes service 只是把应用对外提供服务的方式做了抽象，真正的应用跑在 Pod中的
container 里，我们的请求转到 kubernetes nodes 对应的nodePort 上，那么 nodePort上的请求是如何
进一步转到提供后台服务的 Pod的呢？ 就是通过 kube-proxy实现的：
kube-proxy部署在k8s的每一个 Node节点上，是 Kubernetes 的核心组件， 我们创建一个  service
的时候， kube-proxy 会在iptables 中追加一些规则，为我们实现路由与负载均衡的功能。 在k8s1.8之
前，kube-proxy默认使用的是 iptables 模式，通过各个 node节点上的 iptables 规则来实现 service 的
负载均衡，但是随着 service 数量的增大， iptables 模式由于线性查找匹配、全量更新等特点，其性能
会显著下降。从 k8s的1.8版本开始， kube-proxy引入了IPVS模式，IPVS模式与iptables 同样基于
Netfilter ，但是采用的 hash表，因此当 service 数量达到一定规模时， hash查表的速度优势就会显现
出来，从而提高 service 的服务性能。

service 是一组pod的服务抽象，相当于一组 pod的LB，负责将请求分发给对应的 pod。service 会
为这个LB提供一个 IP，一般称为 cluster IP 。kube-proxy的作用主要是负责 service 的实现，具体来
说，就是实现了内部从 pod到service 和外部的从 node port 向service 的访问。
**1、kube-proxy其实就是管理 service 的访问入口，包括集群内 Pod到Service 的访问和集群外访问**
service。
**2、kube-proxy管理sevice的Endpoints ，该service 对外暴露一个 Virtual IP ，也可以称为是**
Cluster IP, 集群内通过访问这个 Cluster IP:Port 就能访问到集群内对应的 serivce 下的Pod。

**1.9.2 kube-proxy三种工作模式**
**1、Userspace 方式：**

Client Pod 要访问Server Pod 时，它先将请求发给内核空间中的 service iptables 规则，由它再
将请求转给监听在指定套接字上的 kube-proxy的端口， kube-proxy处理完请求，并分发请求到指定

 Server Pod 后,再将请求转发给内核空间中的 service ip，由service iptables 将请求转给各个节点中
的Server Pod 。
这个模式有很大的问题，客户端请求先进入内核空间的，又进去用户空间访问 kube-proxy，由
kube-proxy封装完成后再进去内核空间的 iptables ，再根据 iptables 的规则分发给各节点的用户空间
的pod。由于其需要来回在用户空间和内核空间交互通信，因此效率很差。 在Kubernetes 1.1 版本之
前，userspace 是默认的代理模型。

**2、iptables 方式：**

客户端IP请求时，直接请求本地内核 service ip ，根据iptables 的规则直接将请求转发到到 各
pod上，因为使用 iptable NAT 来完成转发，也存在不可忽视的性能损耗。另外，如果集群中存上万的
Service/Endpoint ，那么Node上的iptables rules 将会非常庞大，性能还会再打折
iptables 代理模式由 Kubernetes 1.1 版本引入，自 1.2版本开始成为默认类型。

**3、ipvs方式：**

Kubernetes 自1.9-alpha版本引入了 ipvs代理模式，自 1.11版本开始成为默认设置。客户端
请求时到达内核空间时，根据 ipvs的规则直接分发到各 pod上。kube-proxy会监视Kubernetes
Service 对象和Endpoints ，调用netlink 接口以相应地创建 ipvs规则并定期与 Kubernetes  Service 对
象和Endpoints 对象同步 ipvs规则，以确保 ipvs状态与期望一致。访问服务时，流量将被重定向到其
中一个后端 Pod。与iptables 类似，ipvs基于netfilter 的 hook 功能，但使用 哈希表作为底层数据结
构并在内核空间中工作。这意味着 ipvs可以更快地重定向流量，并且在同步代理规则时具有更好的性
能。此外， ipvs为负载均衡算法提供了更多选项，例如：
rr：轮询调度
lc：最小连接数
dh：目标哈希
sh：源哈希
sed：最短期望延迟
nq：不排队调度

如果某个服务后端 pod发生变化，标签选择器适应的 pod又多一个，适应的信息会立即反映到
apiserver 上,而kube-proxy一定可以 watch到etc中的信息变化，而将它立即转为 ipvs或者iptables
中的规则，这一切都是动态和实时的，删除一个 pod也是同样的原理。如图：

> **注:**
以上不论哪种， kube-proxy都通过watch的方式监控着 apiserver 写入etcd中关于Pod的最新状
态信息,它一旦检查到一个 Pod资源被删除了或新建了，它将立即将这些变化，反应再 iptables 或 ipvs
规则中，以便 iptables 和ipvs在调度Clinet Pod 请求到Server Pod 时，不会出现 Server Pod 不存在
的情况。自 k8s1.11以后,service 默认使用 ipvs规则，若 ipvs没有被激活，则降级使用 iptables 规
则.

**1.9.3 kube-proxy生成的iptables 规则分析**

**1、service 的type 类型是 ClusterIp ，iptables 规则分析**

在k8s创建的service，虽然有 ip地址，但是 service 的ip是虚拟的，不存在物理机上的，是在
iptables 或者ipvs规则里的。

```bash
[root@xianchaomaster1]# kubectl apply -f pod_test.yaml
[root@xianchaomaster1]# kubectl apply -f service_test.yaml

[root@xianchaomaster1 service]# kubectl get svc -l run=my -service
NAME       TYPE        CLUSTER -IP     EXTERNAL -IP   PORT(S)   AGE
my-ngin x   ClusterIP   10.98.63.235   <none>        80/TCP    75s

[root@xianchaomaster1 service]# kubectl get pods -l run=my -nginx -o wide
NAME                        READY   STATUS    RESTARTS   AGE   IP
my-nginx -69f769d56f -6fn7b   1/1     Runn ing   0          13m   10.244.121.22
my-nginx -69f769d56f -xzj5l   1/1     Running   0          13m   10.244.121.21

[root@xianchaomaster1 service]# iptables -t nat -L | grep 10.98.63.235
KUBE -MARK -MASQ  tcp  -- !10.244.0.0/16        10.98.63.235         /*
default/my -nginx cluster IP */ tcp dpt:http
KUBE -SVC-L65ENXXZWWSAPRCR  tcp  --  anywhere             10.98.63.235
/* default/my -nginx cluster IP */ tcp dpt:http

[root@xianchaomaster1 service]# iptables -t nat -L | grep KUBE -SVC-
L65ENXXZWWSAPRCR
KUBE -SVC-L65ENXXZWWSAPRCR  tcp  --  anywhere             10.98.63.235
/* default/my -nginx cluster IP */ tcp dpt:http
Chain KUBE -SVC-L65ENXXZWWSAPRCR (1 references)

[root@xianchaomaster1 service]# iptables -t nat -L | grep 10. 244.121.22
KUBE -MARK -MASQ  all  --  10.244.121.22        anywhere             /*
default/my -nginx */
DNAT       tcp  --  anywhere             anywhere             /* default/my -nginx
*/ tcp to:10.244.121.22:80

[root@xianchaomaster1 service]# iptables -t nat -L | grep 10.244.121.21
KUBE -MARK -MASQ  all  --  10.244.121.21        anywhere             /*
default/my -nginx */
DNAT       tcp  --  anywhere             anywhere             /* default/my -nginx
*/ tcp to:10.244.121.21:80

#通过上面可以看到之前创建的 service，会通过 kube-proxy在iptables 中生成一个规则，来实现
```
流量路由，有一系列目标为  KUBE-SVC-xxx 链的规则，每条规则都会匹配某个目标  ip 与端口。也就是
说访问某个  ip:port 的请求会由  KUBE-SVC-xxx 链来处理。这个目标  IP 其实就是 service ip 。

**2、service 的type 类型是 nodePort ，iptables 规则分析**

```bash
[root@xianchaomaster1]# kubectl apply -f pod_nodeport.yaml
[root@xianchaomaster1]# kubectl apply -f service_nodeport.yaml

[root@xianchaomaster1 service]# kubectl get pods -l  run=my -nginx-nodeport
NAME                                 READY   STATUS    R ESTARTS   AGE

 my-nginx-nodeport -649c945f85 -l2hj6   1/1     Running   0          21m
my-nginx-nodeport -649c945f85 -zr47r   1/1     Running   0          21m

[root@xianchaomaster1 service]# kubectl get svc -l run=my -nginx-nodeport
NAME                TYPE       CLUSTER-IP       EXTERNAL -IP   PORT(S)        AGE
my-nginx-nodeport   NodePort   10.104.251.190   <none>        80:30380/TCP   22m

[root@xianchaomaster1 service]# iptables -t nat -S | grep 30380
-A KUBE-NODEPORTS -p tcp -m comment --comment "default/my -nginx-nodeport" -m tcp --dport
30380 -j KUBE-MARK-MASQ
-A KUBE-NODEPORTS -p tcp -m comment --comment "default/my -nginx-nodeport" -m tcp --dport
30380 -j KUBE-SVC-J5QV2XWG4FEBPH3Q

[root@xianchaomaster1 service]# iptables -t nat -S | grep KUBE -SVC-J5QV2XWG 4FEBPH3Q
-N KUBE-SVC-J5QV2XWG4FEBPH3Q
-A KUBE-NODEPORTS -p tcp -m comment --comment "default/my -nginx-nodeport" -m tcp --dport
30380 -j KUBE-SVC-J5QV2XWG4FEBPH3Q
-A KUBE-SERVICES -d 10.104.251.190/32 -p tcp -m comment --comment "default/my -nginx-
nodeport c luster IP" -m tcp --dport 80 -j KUBE-SVC-J5QV2XWG4FEBPH3Q
-A KUBE-SVC-J5QV2XWG4FEBPH3Q -m comment --comment "default/my -nginx-nodeport" -m statistic
--mode random --probability 0.50000000000 -j KUBE-SEP-XRUO23GXY67LXLQN
-A KUBE-SVC-J5QV2XWG4FEBPH3Q -m comment --comment "default/my -nginx-nodeport" -j KUBE-SEP-
IIBDPNPJZXXASELC

[root@xianchaomaster1 service]# iptables -t nat -S | grep KUBE -SEP-XRUO23GXY67LXLQN
-N KUBE-SEP-XRUO23GXY67LXLQN
-A KUBE-SEP-XRUO23GXY67LXLQN -s 10.244.102.90/32 -m comment --comment "default/my -nginx-
nodeport" -j KUBE-MARK-MASQ
-A KUBE-SEP-XRUO23GXY67LXLQN -p tcp -m comment --comment "default/my -nginx-nodeport" -m tcp
-j DNAT --to-destination 10.244.102.90:80
-A KUBE-SVC-J5QV2XWG4FEBPH3Q -m comment --comment "default/my -nginx-nodeport" -m statistic
--mode random --probability 0.50000000000 -j KUBE-SEP-XRUO23GXY67LXLQN

[root@xianchaomaster1 service]# iptables -t nat -S | grep KUBE -SEP-IIBDPNPJZXXASELC
-N KUBE-SEP-IIBDPNPJZXXASELC
-A KUBE-SEP-IIBDPNPJZXXASELC -s 10.244.121.23/32 -m comment --comment "default/my -nginx-
nodeport" -j KUBE-MARK-MASQ
-A KUBE-SEP-IIBDPNPJZXXASELC -p tcp -m comment --comment "default/my -nginx-nodeport" -m tcp
-j DNAT --to-destination 10.244.121.23:80
-A KUBE-SVC-J5QV2XWG4FEBPH3Q -m comment --comment "default/my -nginx-nodeport" -j KUBE-SEP-
IIBDPNPJZXXASELC
```

**1.10 Service 服务发现： coredns 组件详解**
DNS是什么？
DNS全称是Domain Name System ：域名系统， 是整个互联网的电话簿，它能够将可被人理解的域名
翻译成可被机器理解 IP地址，使得互联网的使用者不再需要直接接触很难阅读和理解的 IP地址。域名
系统在现在的互联网中非常重要，因为服务 器的 IP 地址可能会经常变动，如果没有了  DNS，那么可能
IP 地址一旦发生了更改，当前服务器的客户端就没有办法连接到目标的服务器了，如果我们为  IP 地址
提供一个『别名』并在其发生变动时修改别名和  IP 地址的关系，那么我们就可以保证集群对外提供的
服务能够相对稳定地被其他客户端 访问。DNS 其实就是一个分布式的树状命名系统，它就像一个去中心
化的分布式数据库，存储着从域名到  IP 地址的映射。

CoreDNS？
CoreDNS 其实就是一个  DNS 服务，而  DNS 作为一种常见的服务发现手段，所以很 多开源项目以及
工程师都会使用  CoreDNS 为集群提供服务发现的功能， Kubernetes 就在集群中使用  CoreDNS 解决服务
发现的问题。  作为一个加入  CNCF（Cloud Native Computing Foundation ）的服务 ， CoreDNS 的实现
非常简单。

验证coredns

```bash
#把dig.tar.gz 上传到xianchaonode2 和xianchaonode1 机器上，手动解压：
[root@xianchaonode2  ~]# docker load -i dig.tar.gz
[root@xianchaonode1  ~]# docker load -i dig.tar.gz
[root@xianchaomaster1  ~]# cat dig.yaml
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: dig
  namespace: default
spec:
  containers:
  - name: dig
    image:  xianchao/dig:latest
    command:
      - sleep
      - "3600"
    imagePullPolicy: IfNotPresent
  restartPolicy: Always
#更新资源清单文件
```

```bash
[root@xianchaomaster1  ~]# kubectl apply -f dig.yaml
pod/dig configured
#查看默认名称空间的 kubernetes 服务
[root@xianchaomaster1  ~]# kubectl get svc | grep k ubernetes
kubernetes          ClusterIP      10.96.0.1        443/TCP        5d13h
#解析dns，如有以下返回说明 dns安装成功
[root@xianchaomaster1  ~]# kubectl exec -it dig -- nslookup kubernetes

 Server:  10.96.0.10
Address:  10.96.0.10#53
Name: kubernetes.default.svc.cluster. local
Address: 10.96.0.1

kubernetes.default.svc.cluster.local
```
服务名.名称空间 .默认后缀

 在k8s中创建service 之后，service默认的FQDN是<service
name>.<namespace>.svc.cluster.local ，那么k8s集群内部的服务就可以通过 FQDN访问


