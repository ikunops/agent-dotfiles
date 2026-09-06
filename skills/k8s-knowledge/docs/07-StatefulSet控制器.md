k8s控制器： Stateful set

**1.1 Statefulset 控制器 ：概念、原理解读**
StatefulSet 是为了 管理有状态服务的问题而设计 的

 扩展：
有状态服务？
StatefulSet 是有状态的集合，管理有状态的服务， 它所管理的 Pod 的名称不能随意变化。数据
持久化的目录也是不一样，每一个 Pod 都有自己独有的数据持久化存 储目录。 比如 MySQL 主
从、redis 集群等 。

无状态服务？
RC、Deployment 、DaemonSet 都是管理无状态的服务，它们所管理的 Pod 的IP、名字，启
停顺序等都是随机的 。个体对整体无影响，所有 pod 都是共用一个数据卷的，部署的 tomcat 就
是无状态的服务 ，tomcat 被删除，在启动一个新的 tomcat ，加入到集群即可，跟 tomcat 的名
字无关 。

StatefulSet 由以下几个部分组成：
**1. Headless Service ：用来定义 pod 网路标识， 生成可解析的 DNS 记录**
**2. volumeClaimTemplates ：存储卷申请模板，创建 pvc，指定 pvc名称大小，自动创建**
pvc，且 pvc由存储类供应 。
**3. StatefulSet ：管理 pod 的**

扩展： 什么是 Headl ess service?
Headless  service 不分配 clusterIP ，headless service 可以通过解析 service 的DNS, 返回所
有Pod 的dns和ip地址 (statefulSet 部署的 Pod 才有 DNS) ，普通的 service, 只能通过解析
service 的DNS 返回 service 的ClusterIP 。

为什么要 用headless  service （没有 service  ip的service ）？
在使用 Deployment 时，创建的Pod 名称是没有顺序的，是随机字符串，在 用statefulset 管理
pod 时要求 pod 名称必须是有序 的 ，每一个 pod 不能被随意取代， pod 重建后 pod 名称还是
一样的。 因为 pod IP 是变化的，所以 要用 Pod 名称来识别 。pod 名称是 pod 唯一性的标识符，
必须持久稳定有效 。这时候要用到无头服务，它可以给每个 Pod 一个唯一的名称 。

1.headless service 会为 service 分配一个 域名

<service name>.$<namespace name>.svc.cluster.local

K8s中资源的全局 FQDN 格式:
  Service_NAME.NameSpace_NAME.Domain.LTD.
  Domain.LTD.=svc.cluster.local.      #这是默认 k8s集群的域名。

FQDN 全称 Fully Qualified Domain Name
即全限定域名：同时带有主机名和域名的名称
FQDN = Hostname + DomainName
如 主机名是  xianchao

 域名是  baidu.com

```bash
FQDN= xianchao .baidu.com
```

2.StatefulSet 会为关联的 Pod 保持一个不变的 Pod Name
statefulset 中Pod 的名字格式为 $(StatefulSet name) -$(pod 序号)

3.StatefulSet 会为关联的 Pod 分配一个 dnsName
$<Pod Name>.$<service name>.$<namespace name>.svc.cluster.local

为什么要 用volumeClaimTemplate ？
对于有状态应用都会用到持久化存储，比如 mysql 主从，由于主从数据库的数据是不能存放在一
个目录下的，每个 mysql 节点都需要有自己独立的存储空间。而在 deployment 中创建的存储卷
是一个共享的存储卷，多个 pod 使用同一个存储卷，它们数据是同步的，而 statefulset 定义中
的每一个 pod 都不能使用同一个存储卷，这就需要使用 volumeClainTemplate ，当在使用
statefulset 创建 pod 时，volumeClainTemplate 会自动生成一个 PVC，从而请求绑定一个
PV，每一个 pod 都有自己专用的存储卷。 Pod、PVC 和PV对应的关系图如下：

**1.2 Statefulset 资源清单 文件编写技巧**

```bash
#查看定义 Statefulset 资源需要的字段
[root@ xianchaomaster1  ~]# kubectl explain statefulset
```

```yaml
KIND:     StatefulSet
VERSION:  apps/v1
DESCRIPTION:
     StatefulSet represents a set of pods with consistent identities. Identities
     are defined as:
     - Network: A single stable DNS and hostname.
     - Storage: As many VolumeClaims as requested. The StatefulSet guarantees
```

      that a given network identity will always map to the same storage identity.
FIELDS:
   apiVersion  <string>  #定义 statefulset 资源需要使用的api版本
   kind <string>           #定义的资源类型
   metadata  <Object>      #元数据
   spec  <Object>           #定义容器相关的信息

```bash
#查看 statefulset .spec 字段如何定义？
[root@ xianchaomaster1  ~]# kubectl explain statefulset.spec
```

```yaml
KIND:     StatefulSet
VERSION:  apps/v1
RESOURCE: spec <Object>
DESCRIPTION:
     Spec defines the desired identities of pods in this set.
     A StatefulSetSpec is the specification of a StatefulSet.
FIELDS:
   podManagementPolicy  <string>  #pod 管理策略
   replicas  <integer>   #副本数
   revisionHistoryLimit  <integer>  #保留的历史版本
   selector  <Object> -required - #标签选择器，选择它所关联的 pod
   serviceName  <string> -required -  #headless  service 的名字
   template  <Object> -required -     #生成 pod 的模板
   updateStrategy  <Object>    #更新策略
   volumeClaimTemplates  <[]Object>  #存储卷申请模板

#查看 statefulset 的spec .template 字段如何定义？
#对于 template 而言，其内部定义的就是 pod，pod 模板是一个独立的对象
```

```bash
[root@ xianchaomaster1  ~]# kubectl explain statefulset.spec.template
```

```yaml
KIND:     StatefulSet
VERSION:  apps/v1
RESOURCE: template <Object>
DESCRIPTION:
     template is the object that describes the pod that will be created if
     insufficient replicas are detecte d. Each pod stamped out by the StatefulSet
     will fulfill this Template, but have a unique identity from the rest of the
     StatefulSet.
     PodTemplateSpec describes the data a pod should have when created from a
     template
FIELDS:
   metadata  <Object>
   spec  <Object>   #定义容器属性的

 通过上面可以看到， statefulset 资源中有两个 spec 字段。第一个 spec 声明的是 statefulset 定
```
义多少个 Pod 副本（默认将仅部署 1个Pod）、匹配 Pod 标签的选择器 、创建 pod 的模板 、存
储卷申请模板， 第二个 spec 是spec. template.spec ：主要 用于 Pod 里的容器属性等配置。
.spec.template 里的内容是声明 Pod 对象时要定义的各种属性，所以这部分也叫做
PodTemplate （Pod 模板）。还有一个值得注意的地方是：在 .spec.selector 中定义的标签选择
器必须能够匹配到 spec.template.metadata.labels 里定义的 Pod 标签，否则 Kubernetes 将
不允许创建 statefulset 。

**1.3 Statefulset 使用案例 ：部署 web 站点**

```bash
#创建存储类
[root@ xianchaomaster1  ~]# cat class -web.yaml
```

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nfs-web
provisioner: example.com/nfs
#更新资源清单文件
```

```bash
[root@ xianchaomaster1  ~]# kubectl apply -f class -web.yaml

  #把nginx 的离线压缩包 nginx .tar.gz 上传到 xianchaonode1 、xianchaonode2 上，手动解
```
压：

```bash
  [root@ xianchaonode1  ~]# docker load -i nginx.tar.gz
#编写一个 Statefulset 资源清单 文件
[root@ xianchaomaster1  ~]# cat statefulset.yaml
```

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx
  labels:
     app: nginx
spec:
  ports:
  - port: 80
    name: web
  clusterIP: None
  selector:
    app: nginx
---
apiVersion: apps/v1
kind: StatefulSet

 metadata:
  name: web
spec:
  selector:
    matchLabels:
      app: nginx
  serviceName: "nginx"
  replicas: 2
  template:
    metadata:
     labels:
       app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx
        ports:
        - containerPort: 80
          name: web
        volumeMounts:
        - name: www
          mountPath: /usr/share/nginx/html
  volum eClaimTemplates:
  - metadata:
      name: www
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: " nfs-web"
      resources:
        requests:
          storage: 1Gi
#更新资源清单文件
```

```bash
[root@ xianchaomaster1  ~]# kubectl apply -f statefulset.yaml
service/nginx created
statefulset.apps/web created
      #查看 statefulset 是否创建成功
[root@ xianchaomaster1  ~]# kubectl get statefulset
NAME   READY   AGE
web      2/2      42s
#查看 pod
[root@ xianchaomaster1  ~]# kubectl get pods -l app=nginx
NAME    READY   STATUS    RESTARTS   AGE
web-0   1/1     Running   0          2m17s

 web-1   1/1     Running   0          115s

#通过上面可以看到创建的 pod 是有序的

#查看 headless  service
[root@ xianchaomaster1  ~]# kubectl get svc -l app=nginx
NAME    TYPE        CLUSTER -IP   EXTERNAL -IP   PORT(S)   AGE
nginx    ClusterIP      None         <none>        80/TCP    3m19s

#查看 pvc
[root@ xianchaomaster1  ~]# kubectl get pv c
[root@xianchaomaster1 statefulset]# kubectl get pvc
NAME          STATUS   VOLUME                                     CAPACITY
ACCESS MODES   STORAGECLASS   AGE
www -web-0     Bound    pvc -39a9755f -3248 -49ff-8f9e-5b068b609c8f   1Gi
RWO,RWX        nfs -web        7m45s
www-web-1     Bound    pvc -be93d4a3 -1aca -44cc -802f -ddeb38c05018   1Gi
RWO,RWX        nfs -web        7m41s

#查看 pv
[root@ xianchaomaster1  ~]# kubectl get pv
[root@xianchaomaster1 statefulset]# kubectl get pv
NAME                                       CAPACITY   ACCESS MODES
RECLAIM POLICY   STATUS      CLAIM                 STORAGECLASS   REASON
AGE
pvc-39a9755f -3248 -49ff-8f9e-5b068b609c8f   1Gi        RWO,RWX        Delete
Bound       default/www -web-0     nfs -web                 8m3s
pvc-be93d4a3 -1aca -44cc -802f -ddeb38c05018   1Gi        RWO,RWX        Delete
Bound       default/www -web-1     nfs -web                 7m59s

#查看 pod 主机名
[root@ xianchaomaster1  ~]# for i in 0 1; do kubectl exec web -$i -- sh -c
'hostname';done
web-0
web-1

#使用 kubectl  run运行一个提供 nslookup 命令的容器的， 这个命令来自于 dnsutils 包，通过
```
对pod 主机名执行 nslookup ，可以检查它们在集群内部的 DNS 地址：

```bash
[root@ xianchaomaster1  ~]# kubectl exec -it web -1 -- /bin/bash
root@web -1:/# apt -get update
root@web -1:/# apt -get install dnsutils -y

root@web -1:/# nslookup web -0.nginx.default.svc.cluster.local

 Server:   10.96.0.10
Address:  10.96.0.10#53
Name:  web-0.nginx.default.svc.cluster.local

#statefulset 创建的 pod 也是有 dns记录的
Address: 10.244.209.154   #解析的是 pod 的ip地址

root@web -1:/# nslookup nginx.default.svc.cluster.local
Server:   10.96.0.10
Address:  10.96.0.10#53

Name:  nginx.default.svc.cluster.local   #查询 service  dns，会把对应的 pod ip解析出来
Address: 10.244.209.139

Name:  nginx.default.svc.cluster.local
Address: 10.244.209.140

root@web -1:/# dig -t A nginx.default.svc.cluster.local @10.96.0.10
; <<>> DiG 9.11.5 -P4-5.1+deb10u3 -Debian <<>> -t A nginx.default.svc.cluster.local
@10.96.0.10
;; global options: +cmd
;; Got answer:
;; WARNING: .local is reserved for Multicast DNS
;; You are currently testing what happens when an mDNS query is leaked to DNS
;; ->>HEADER<< - opcode: QUERY, status: NOERROR, id: 27207
;; flags: qr aa rd; QUERY: 1, ANSWER: 2, AUTHORITY: 0, ADDITIONAL: 1
;; WARNING: recursion requested but not available

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
; COOKIE: f2f17492cf38ad44 (echoed)
;; QUESTION SECTION:
;nginx.default.svc.cluster.local. IN  A

;; ANSWER SECTION:
nginx.default.svc.cluster.local. 30 IN  A 10.244.209.139
nginx.default.svc.cluster.l ocal. 30 IN  A 10.244.209.140

;; Query time: 0 msec
;; SERVER: 10.96.0.10#53(10.96.0.10)
;; WHEN: Fri Apr 09 15:10:40 UTC 2021
;; MSG SIZE  rcvd: 166
```

 dig的使用
dig -t A nginx.default.svc.cluster.local @10.96.0.10
格式如下：
@来指定域名服务器
A 为解析类型  ，A记录
-t 指定要解析的类型

A记录：
  A记录是解析域名到 IP

资源清单详细解读：

```yaml
apiVersion: v1   #定义 api版本
kind: Service    #定义要创建的资源： service
metadata:
  name: nginx    #定义 service 的名字
  labels:
     app: nginx   #service 的标签
spec:
  ports:
  - port: 80
    name: web
  clusterIP: None   #创建一个没有 ip的service
  selector:
    app: nginx      #选择拥有 app=nginx 标签的 pod
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  selector:
    matchLabels:
      app: nginx
  serviceName: "nginx"   #headless  service 的名字
  replicas: 2               #副本数
  template:               #定义 pod 的模板
    metadata:
     labels:
       app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx

         imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 80
          name: web
        volumeMounts:
        - name: www
          mountPath: /usr/share/nginx/html
  volumeClaimTemplates:      #存储卷申请模板
  - metadata:
      name: www
    spec:
      accessModes: ["ReadWriteOnce"]
storageClassName: " nfs-web"  #指定从哪个存储类申请 pv
      resources:
        requests:
          storage: 1Gi    #需要 1G的pvc，会自动跟符合条件的 pv绑定

```
扩展：
举例说明 service  和headless  service 区别：
**1、通过 deployment 创建 pod，pod 前端创建一个 service**

```bash
[root@ xianchaomaster1  ~]# cat deploy -service.yaml
```

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my -nginx
  labels:
    run: my -nginx
spec:
  type: ClusterIP
  ports:
  - port: 80   #service 的端口，暴露给 k8s集群内部服务访问
    protocol: TCP
    targetPort: 80    #pod 容器中定义的端口
  selector:
    run: my -nginx  # 选择拥有 run=my -nginx 标签的 pod
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my -nginx
spec:
  selector:
    matchLabels:

       run: my -nginx
  replicas: 2
  template:
    metadata:
      labels:
        run: my -nginx
    spec:
      containers:
      - name: my -nginx
        image: busybox
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 80
        command:
          - sleep
          - "3600"

#更新资源清单文件
```

```bash
[root@ xianchaomaster1  ~]# kubectl apply -f deploy -service.yaml
#查看 service
[root@ xianchaomaster1  ~]# kubectl get svc -l run=my -nginx
NAME       TYPE        CLUSTER -IP     EXTERNAL -IP   PORT(S)
my-nginx   ClusterIP     10.100.89.90   <none>        80/TCP
#查看 pod
[root@ xianchaomaster1  ~]# kubectl get pods -l run=my -nginx
NAME                        READY   STATUS    RESTARTS   AGE
my-nginx -58f74fc5b6 -jzbvk   1/1     Running   0          70s
my-nginx -58f74fc5b6 -n9lqv   1/1     Running   0          53s
#通过上面可以看到 deployment 创建的 pod 是随机生成的

#进入到 web-1的pod
[root@ xianchaomaster1  ~]# kubectl exec -it web -1 -- /bin/bash
root@web -1:/# nslookup my -nginx.default.svc.cluster.local
Server:   10.96.0.10
Address:  10.96.0.10#53

Name:  my-nginx.default.svc.cluster.local
Address: 10.100.89.90    #解析的是 service 的ip地址
```

**1.4 Statefulset 管理 pod：扩容、缩容、更新**

 #Statefulset 实现 pod 的动态扩容
如果我们觉得两个副本太少了，想要增加，只需要修改配置文件 statefulset .yaml 里的 replicas
的值即可 ，原来 replicas: 2，现在变成 replicaset: 3，修改之后，执行如下命令更新：

```bash
[root@ xianchaomaster1  ~]# kubectl apply -f statefulset.yaml
service/nginx unchanged
statefulset.apps/web configured
[root@ xianchaomaster1  ~]# kubectl get sts
NAME   READY   AGE
web    3/3     60m
      [root@ xianchaomaster1  ~]# kubectl get pods -l app=nginx
NAME    READY   STATUS    RESTARTS   AGE
web-0   1/1     Running   0          61m
web-1   1/1     Running   0          60m
web-2   1/1     Running   0          79s

      #也可以直接编辑控制器实现扩容
[root@ xianchaomaster1  ~]# kubectl edit sts web
#这个是我们 把请求 提交给了 apiserver ，实时修改
```

把上面的 spec 下的 replicas 后面的值改成 4，保存退出

```bash
[root@ xianchaomaster1  ~]#  kubectl get pods -l app=nginx
NAME    READY   STATUS    RESTARTS   AGE
web-0   1/1     Running   0          62m
web-1   1/1     Running   0          62m
web-2   1/1     Running   0          3m13s
web-3   1/1     Running   0          26s

#Statefulset 实现 pod 的动态缩容
```
如果我们觉得 4个Pod 副本太多了 ，想要 减少，只需要修改配置文件 statefulset .yaml 里的
replicas 的值即可 ，把 replicaset ：4变成 replicas : 2，修改之后，执行如下命令更新：

```bash
[root@ xianchaomaster1  ~]# kubectl apply -f statefulset.yaml
service/nginx unchanged
statefulset.apps/web configured
[root@ xianchaomaster1  ~]#  kubectl get pods -l app=nginx
NAME    READY   STATUS    RESTARTS   AGE
web-0   1/1     Running   0          64m
web-1   1/1     Runnin g   0          64m

#Statefulset 实现 pod 的更新
# myapp.tar.gz 上传到 xianchaonode1 上，手动解压
```
把[root@ xianchaonode1  ~]# docker load -i myapp.tar.gz

```bash
[root@ xianchaomaster1  ~]# kubectl edit sts web
#修改镜像 nginx 变成- image: ikubernetes/myapp:v2 ，修改之后保存退出
[root@ xianchaomaster1  ~]# kubectl get pods -o wide -l app=nginx
NAME    READY   STATUS    RESTARTS   AGE   IP               NODE
NOMINATED NODE   READINESS GATES
web-0   1/1     Running   0          18s   10.244.209.156   xianchaonode1
web-1   1/1     R unning   0          36s   10.244.187.115   xianchaonode2
#查看 pod 详细信息
[root@ xianchaomaster1  ~]# kubectl describe pods web -0
```

通过上面可以看到 pod 已经使用刚才更新的镜像 ikubernetes/myapp:v2 了


