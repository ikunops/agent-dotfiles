1.k8s核心资源 Pod介绍？

K8s官方文档： https://kubernetes.io/
K8s中文官方文档：  https://kubernetes.io/zh/
K8s Github地址：https://github.com/kubernetes/

**1.1 Pod是什么？**

官方文档：https://kubernetes.io/docs/concepts/workloads/pods/

Pod是Kubernetes 中的最小调度单元， k8s是通过定义一个 Pod的资源，然后在 Pod里面运行容
器，容器需要指定 一个镜像，这样就可以 用来运行具体的服务。一个 Pod封装一个容器（也可以封装多
个容器） ， Pod里的容器共享存储、网络等。也就是说，应该把整个 pod看作虚拟机，然后每个容器相当
于运行在虚拟机的进程。

Pod是需要调度到 k8s集群的工作节点 来运行的 ，具体调度到哪个节点，是根据 scheduler 调度器实
现的。

白话解释：
可以把pod看成是一个“豌豆荚” ，里面有很多“豆子” （容器） 。一个豌豆荚里的豆子，它们吸收着
共同的营养成分、肥料、水分等， Pod和容器的关系也是一样， Pod里面的容器共享 pod的网络、存储
等。

pod相当于一个逻辑主机 --比方说我们想要部署一个 tomcat应用，如果不用容器，我们可能会部署
到物理机 、虚拟机或者云主机上，那么出现 k8s之后，我们就可以 定义一个 pod资源，在 pod里定义一
个把tomcat容器，所以pod充当的是一个逻辑主机的角色 。

**1.1.1 Pod如何管理多个容器 ？**

Pod中可以同时运行多个容器。同一个 Pod中的容器会自动的分配到同一个  node 上。同一个 Pod中
的容器共享资源、网络环境，它们总是被同时调度，在一个 Pod中同时运行多个容器是一种比较高级的
用法，只有当你的容器需要紧密配合协作的时候才考虑用这种模式。例如，你有一个容器作为 web服务
器运行，需要用到共享的 volume，有另一个 “sidecar” 容器来从远端获取资源更新这些文件 。

一些Pod有init容器和应用容器。 在应用程序容器启动之前， 运行初始化容器 。

**1.1.2 Pod 网络**

 Pod是有IP地址的， 每个pod都被分配唯一的 IP地址（IP地址是靠网络插件 calico、flannel、
weave等分配的） ，POD中的容器共享网络名称空间，包括 IP地址和网络端口。  Pod内部的容器可以使
用localhost 相互通信。  Pod中的容器也可以通过网络插件 calico与其他节点的 Pod通信。

**1.1.3 Pod 存储**
创建Pod的时候可以指定 挂载的存储卷。  POD中的所有容器都可以访问共享卷，允许这些容器共享
数据。 Pod只要挂载持久化数据卷， Pod重启之后数据还是会存在的。

**1.2 Pod工作方式**

在K8s中，所有的资源都可以使用一个 yaml文件来创建，创建 Pod也可以使用 yaml配置文件。 或
者使用kubectl run 在命令行创建 Pod（不常用）。

**1.2.1 自主式Pod**
所谓的自主式 Pod，就是直接定义一个 Pod资源，如下：

```bash
[root@xianchaomaster1 ~]# vim pod-tomcat.yaml
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: tomcat -test
  namespace: default
  labels:
    app:  tomcat
spec:
  containers:
  - name:  tomcat -java
    ports:
    - containerPort: 8080
    image: xianchao/tomcat -8.5-jre8:v1
  imagePullPolicy: IfNotPresent

#导入镜像
```
把xianchao -tomcat.tar.gz 上传到xianchaonode1 和xianchaonode2 节点，手动解压：

```bash
[root@xianchaonode1 ~]# docker load -i xianchao -tomcat.tar.gz
[root@xianchaonode 2 ~]# docker load -i xianchao -tomcat.tar.gz

#更新资源清单文件

 [root@xianchaomaster1 ~]# kubectl apply -f pod-tomcat.yaml
#查看pod是否创建成功
[root@xianchaomaster1 ~]# kubectl get pods -o wide -l app=tomcat
NAME          READY   STATUS       IP              NODE
tomcat-test      1/1        Running   10.244.121.45   xianchaonode1
```

但是自主式 Pod是存在一个问题的，假如我们 不小心删除了pod：

```bash
[root@xianchaomaster1 ~]# kubectl delete pods tomcat -test
#查看pod是否还在
[root@xianchaomaster1 ~]# kubectl get pods -l app=tomcat
#结果是空，说明 pod已经被删除了
```

通过上面可以看到，如果直接定义一个 Pod资源，那 Pod被删除，就彻底被删除了，不会再创建一
个新的Pod，这在生产环境还是具有非常大风险的，所以今后我们接触的 Pod，都是控制器管理的。

**1.2.2 控制器管理的 Pod**
常见的管理 Pod的控制器： Replicaset 、Deployment 、Job、CronJob、Daemonset 、Statefulset 。
控制器管理的 Pod可以确保 Pod始终维持在指定的副本数 运行。
如，通过 Deployment 管理Pod

#解压镜像：
把xianchao -nginx.tar.gz 上传到xianchaonode 1和xianchaonode 2节点

```bash
[root@xianchaonode1 ~]# docker load -i xianchao -nginx.tar.gz
[root@xianchaonode 2 ~]# docker load -i xianchao -nginx.tar.gz

#创建一个资源清单文件
[root@xianchaomaster1 ~]# vim nginx -deploy.yaml
```

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx -test
  labels:
    app: nginx -deploy
spec:
  selector:
    matchLabels:
      app: nginx
  replicas: 2
  template:
    metadata:
      labels:
        app: nginx
    spec:

       containers:
      - name: my -nginx
        image: xianchao/nginx:v1
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 80
#更新资源清单文件
```

```bash
[root@xianchaomaster1 ~]# kubectl apply -f nginx-deploy.yaml

#查看Deployment
[root@xianchaomaster1 ~]# kubectl get deploy -l app=nginx -deploy
NAME         READY   UP -TO-DATE   AVAILABLE   AGE
nginx-test       2/2        2            2           1 6s

#查看Replicaset
[root@xianchaomaster1 ~]# kubectl get rs -l app=nginx
NAME                    DESIRED   CURRENT   READY   AGE
nginx-test-75c685fdb7   2         2         2       71s

#查看pod
[root@xianchaomaster1 ~]# kubectl get pods -o wide -l app=nginx
NAME                           READY   STATUS        IP
nginx-test-75c685fdb7 -6d4lx    1/1     Running       10.244.102.69
nginx-test-75c685fdb7 -9s95h    1/1     Running       10.244.102.68

#删除nginx-test-75c685fdb7 -9s95h这个pod
[root@xianchaomaster1 ~]# kubectl delete pods nginx -test-75c685fdb7 -9s95h
[root@xianchaomaster1 ~]# kubectl get pods -o wide -l app=nginx
NAME                           READY   ST ATUS              IP
nginx-test-75c685fdb7 -6d4lx    1/1       Running            10.244.102.69
nginx-test-75c685fdb7 -pr8gh    1/1      Running             10.244.102.70

#发现重新创建一个新的 pod是nginx-test-75c685fdb7 -pr8gh
```

通过上面可以发现通过 deployment 管理的pod，可以确保 pod始终维持在指定副本数量

2.如何创建一个 Pod资源
K8s创建Pod流程

 Pod是Kubernetes 中最基本的部署调度单元，可以包含 container ，逻辑上表示某种应用的一个
实例。例如一个 web站点应用由前端、后端及数据库构建而成，这三个组件将运行在各自的容器中，那
么我们可以创建包含三个 container 的pod。

创建pod流程：

master节点：kubectl -> kube-api -> kubelet -> CRI容器环境初始化

第一步：
客户端提交创建 Pod的请求，可以通过 调用API Server的Rest API接口，也可以通过 kubectl 命令行

 工具。如kubectl apply -f filename. yaml(资源清单文件 )

第二步：
apiserver 接收到pod创建请求后， 会将yaml中的属性信息 (metadata) 写入etcd。
第三步：
apiserver 触发watch机制准备创建 pod，信息转发给调度器 scheduler ，调度器使用调度算法选择
node，调度器将 node信息给apiserver ，apiserver 将绑定的 node信息写入 etcd

调度器用一组规则过滤掉不符合要求的主机。比如 Pod指定了所需要的资源量，那么可用资源比 Pod需
要的资源量少的主机会被过滤掉。

scheduler 查看 k8s api ，类似于通知机制。
首先判断： pod.spec.Node == null?
若为null，表示这个 Pod请求是新来的，需要创建；因此先进行调度计算，找到最 “闲”的node。
然后将信息在 etcd数据库中更新分配结 果：pod.spec.Node = nodeA ( 设置一个具体的节点 )

ps:同样上述操作的各种信息也要写到 etcd数据库中中

第四步：
apiserver 又通过watch机制，调用 kubelet，指定pod信息，调用Docker API 创建并启动 pod内的容
器。

第五步：
创建完成之后反馈给 kubelet, kubelet 又将pod的状态信息给 apiserver,
apiserver 又将pod的状态信息写入 etcd。

**2.1 资源清单YAML文件书写技巧**
如下：

```bash
[root@xianchaomaster1 ~]# vim pod-tomcat.yaml
```

```yaml
apiVersion: v1   #api版本
kind: Pod       #创建的资源
metadata:
  name: tomcat -test  #Pod的名字
  namespace: default    #Pod所在的名称空间
  labels:
    app:  tomcat      #Pod具有的标签
spec:
  containers:
  - name:  tomcat -java   #Pod里容器的名字
    ports:
    - containerPort: 8080   #容器暴露的端口
    image: xianchao/tomcat -8.5-jre8:v1  #容器使用的镜像
  imagePullPolicy: IfNotPresent     #镜像拉取策略

#更新资源清单文件
```

```bash
[root@xianchaomaster1 ~]# kubectl apply -f pod-tomcat.yaml

# Pod资源清单编写技巧
```
通过kubectl explain 查看定义Pod资源包含哪些字段 。

```bash
[root@xianchaomaster1 ~]# kubectl explain pod
```

```yaml
KIND:     Pod
VERSION:  v1
DESCRIPTION:
     Pod is a collection of containers that can run on a host. This resource is
     created by clients and scheduled onto hosts.
```
[Pod是可以在主机上运行的容器的集合。此资源是由客户端创建并安排到主机上。 ]

FIELDS:
   apiVersion  <string>
     APIVersion defines the versioned schema of this representation of an
     object. Servers should convert recognized schemas to the latest internal
     value, and may reject unrecognized values. More info:
     https://git.k8s.io/community/contributor s/devel/sig -architecture/api -
conventions.md#resources
[APIVersion 定义了对象 ,代表了一个版本 。]
   kind <string>
     Kind is a string value representing the REST resource this object
     represents. Servers may infer this from the endpoint the client submits
     requests to. Cannot be updated. In CamelCase. More info:
     https://git.k8s.io/community/contributors/devel/sig -architecture/api -
conventions.md#types -kinds
[Kind是字符串类型的值，代表了要创建的资源 。服务器可以从客户端提交的 请求推断出这个资
源。]
   metadata  <Object>
     Standard object's metadata. More info:
     https://git.k8s.io/community/contributors/devel/sig -architecture/api -
conventions.md#metadata
[metadata 是对象，定义元数据 属性信息的]
   spec <Object>
     Specification of the desired behavior of the pod. More info:
     https://git.k8s.io/community/contributors/devel/sig -architecture/api -
conventions.md#spec -and-status
[spec制定了定义 Pod的规格，里面包含容器的信息 ]
   status <Object>
     Most recently observed status of the pod. This data may not be up to date.

      Populated by the system. Read -only. More info:
     https://git.k8s.io/community/contributors/devel/sig -architecture/api -
conventions.md#spec -and-status
[status表示状态，这个不可以修改 ，定义pod的时候也不需要定义这个字段 ]

```bash
#查看pod.metadata 字段如何定义
[root@xianchaomaster1 ~]# kubectl explain pod.metadata
```

```yaml
KIND:     Pod
VERSION:  v1
RESOURCE: metadata <Object>

# metadata 是对象<Object> ，下面可以有多个字段

DESCRIPTION:
     Standard object's metadata. More info:
     https://git.k8s.io/community/contributors/devel/sig -architecture/api -
conventions.md#metadata
     ObjectMeta is metadata that all persisted resources must have, which
     includes all objects users must create.

FIELDS:
   annotations  <map[string]str ing>
     Annotations is an unstructured key value map stored with a resource that
     may be set by external tools to store and retrieve arbitrary metadata. They
     are not queryable and should be preserved when modifying objects. More
     info: http://kubernetes.io/docs/user -guide/annotations
# annotations 是注解，map类型表示对应的值是 key-value键值对，<string,string> 表示 key和
```
value都是String类型的

"metadata" : {
  "annotations" : {
    "key1" : "value1" ,
    "key2" : "value2"
  }
}

用Annotation 来记录的信息包括：
build信息、release 信息、Docker镜像信息等，例如时间戳、 release id 号、镜像 hash值、docker
registry 地址等；
日志库、监控库、分析库等资源库的地址信息；
程序调试工具信息，例如工具名称、版本号等；
团队的联系信息，例如电话号码、负责人名称、网址等。

    clusterName  <string>
     The name of the cluster which the object belongs to. This is used to
     distinguish resources with same name and namespace in different clusters.
     This field is not set anywhere right now and apiserver is going to ignore
     it if set in create  or update request.
#对象所属群集的名称。这是用来区分不同集群中具有相同名称和命名空间的资源。此字段现在未设
置在任何位置， apiserver 将忽略它，如果设置了就使用设置的值

   creationTimestamp  <string>
   deletionGracePeriodSeconds  <integer>
   deletionTimestamp  <string>
   finalizers  <[]string>
   generateName  <string>
   generation <integer>
   labels <map[string]string>  #创建的资源具有的标签
Map of string keys and values that can be used to organize and categorize
     (scope and select) objects. May match selectors of replication controllers
     and services. More info: http://kubernetes.io/docs/user -guide/labels
#labels 是标签， labels是map类型，map类型表示对应的值是 key-value键值对，
<string,string> 表示 key和value都是String类型的
   managedFields  <[]Object>
   name <string>            #创建的资源的名字
   namespace  <string>       #创建的资源所属的名称空间
Namespace defines the space within which each name must be unique. An empty
namespace is equivalent to the "default" namespace, but "default" is the
canonical representation. Not all objects are required to be scoped to a
namespace - the value of this field for those objects will be empty.
     Must be a DNS_LABEL. Cannot be updat ed. More info:
     http://kubernetes.io/docs/user -guide/namespaces
# namespace s划分了一个空间，在同一个 namesace 下的资源名字是唯一的， 默认的名称空间是
default。
   ownerReferences  <[]Object>
   resourceVersion  <string>
   selfLink  <string>
   uid <string>

```bash
#查看pod.spec 字段如何定义
[root@xianchaomaster1 ~]# kubectl explain pod.spec
```

```yaml
KIND:     Pod
VERSION:  v1
RESOURCE: spec <Object>
DESCRIPTION:
     Specification of the desired behavior of the pod. More info:

      https://git.k8s.io/community/contributors/devel/sig -architecture/api -
conventions.md#spec -and-status
     PodSpec is a description of a pod.
#Pod的spec字段是用来描述 Pod的

FIELDS:
   activeDeadlineSeconds  <integer>
#表示Pod可以运行的最长时间，达到设置的值后， Pod会自动停止。
affinity  <Object>
  #定义亲和性的
   automountServiceAccountToken  <boolean>
   containers  <[]Object> -required -
#containers 是对象列表，用来 定义容器 的，是必须字段。 对象列表  表示下面有很多对象， 对象列
```
表下面的 内容用 - 连接。
   dnsConfig  <Object>
   dnsPolicy  <string>
   enableServiceLinks  <boolean>
   ephemeralContainers  <[]Object>
   hostAliases  <[]Object>
   hostIPC <boolean>
   hostNetwork  <boolean>
   hostPID <boolean>
   hostname  <string>
   imagePullSecrets  <[]Object>
   initContainers  <[]Object>
   nodeName  <string>
   nodeSelector  <map[string ]string>
   overhead  <map[string]string>
   preemptionPolicy  <string>
   priority  <integer>
   priorityClassName  <string>
   readinessGates  <[]Object>
   restartPolicy  <string>
   runtimeClassName  <string>
   schedulerName  <string>
   securityContext  <Object>
   serviceAccount  <string>
   serviceAccountName  <string>
   setHostnameAsFQDN  <boolean>
   shareProcessNamespace  <boolean>
   subdomain  <string>
   terminationGracePeriodSeconds  <integer>
   tolerations  <[]Object>

    topologySpreadConstraints  <[]Objec t>
   volumes <[]Object>

```bash
#查看pod.spec.containers 字段如何定义
[root@xianchaomaster1 ~]# kubectl explain pod.spec.containers
```

```yaml
KIND:     Pod
VERSION:  v1

RESOURCE: containers <[]Object>
DESCRIPTION:
     List of containers belonging to the pod. Containers cannot currently be
     added or removed. There must be at least one container in a Pod. Cannot be
     updated.
     A single application container that you want to run within a pod.
#container 是定义在 pod里面的，一个 pod至少要有一个容器 。

FIELDS:
   args <[]string>
   command <[]string>
   env <[]Object>
   envFrom <[]Object>
   image <string>
#image是用来指定容器需要 的镜像的
   imagePullPolicy  <string>
#镜像拉取策略， pod是要调度到 node节点的，那 pod启动需要镜像，可以根据这个字段设置镜像拉
```
取策略，支持如下三种：
Always：不管本地是否存在镜像，都要重新拉取镜像
Never： 从不拉取镜像
IfNotPresent ：如果本地存在，使用本地的镜像，本地不存在，从官方拉取镜像

   lifecycle  <Object>
   livenessProbe  <Object>
   name <string> -required -
#name是必须字段，用来指定容器名字的
   ports <[]Object>
#port是端口，属于对象列表
   readinessProbe  <Object>
   resources  <Object>
   securityContext  <Object>
   startupProbe  <Object>
   stdin <boolean>
   stdinOnce  <boolean>
   terminationMessagePath  <string>

    terminationMessagePolicy  <string>
   tty <boolean>
   volumeDevices  <[]Object>
   volumeMounts  <[]Object>
   workingDir  <string>

```bash
#查看pod.spec.container.ports 字段如何定义
[root@xianchaomaster1 ~]# kubectl explain pod.spec.containers.ports
```

```yaml
KIND:     Pod
VERSION:  v1
RESOURCE: ports <[]Object>
DESCRIPTION:
     List of ports to expose from the container. Exposing a port here gives the
     system additional information about the network connections a container
     uses, but is primarily informational. Not specifying a port here DOES NOT
     prevent that port from being exposed. Any port which is listening on the
     default "0.0.0.0" address inside a container will be accessible from the
     network. Cannot be updated.

     ContainerPort represents a network port in a single container.
FIELDS:
   containerPort  <integer> -required -
     Number of port to expose on the pod's IP address. This must be a valid port
     number, 0 < x < 65536.
#containerPort 是必须字段，  pod中的容器需要暴露的端口。

   hostIP <string>
     What host IP to bind the external port to.
#将容器中的服务暴露到宿主机的端口上时，可以指定绑定的宿主机  IP。
   hostPort  <integer>
     Number of port to expose on the host. If specified, this must be a valid
     port number, 0 < x < 65536. If HostNetwork is specified, this must match
     ContainerPort. Most containers do not need this.
#容器中的服务 在宿主机上 映射的端口
   name <string>
     If specified, this must be an IANA_SVC_NAME and unique within the pod. Each
     named port in a pod must have a unique name. Name for the port that can be
     referred to by services.
#端口的名字
   protocol  <string>
     Protocol for port. Must be UDP, TCP, or SCTP. Defaults to "TCP".

```
**2.2 通过资源清单文件创建第一个 Pod**

```bash
 [root@xianchaomaster1 ~]# vim pod-first.yaml
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-first
  namespace: default
  labels:
    app:  tomcat -pod-first
spec:
  containers:
  - name:  tomcat -first
    ports:
    - containerPort: 8080
    image: xianchao/tomcat -8.5-jre8:v1
  imagePullPolicy: IfNotPresent

#导入镜像
```
把xianchao -tomcat.tar.gz 上传到xianchaonode1 和xianchaonode2 节点，手动解压：

```bash
[root@xianchaonode1 ~]# docker load -i xianchao -tomcat.tar.gz
[root@xianchaonode2 ~]# docker load -i xianchao -tomcat.tar.gz

#更新资源清单文件
[root@xianchaomaster1 ~]# kubectl apply -f pod-first.yaml

#查看pod是否创建成功
[root@xianchaomaster1 ~]# kubectl get pods -o wide -l app= tomcat-pod-first
NAME          READY   STATUS       IP              NODE
pod-first      1/1        Running   10.244.121.45   xianchaonode1

#查看pod日志
kubectl logs pod-first

#查看pod里指定容器的日志
kubectl logs pod-first  -c tomcat-first

#进入到刚才创建的 pod，刚才创建的 pod名字是web
kubectl exec -it pod-first  -- /bin/bash

#假如pod里有多个容器，进入到 pod里的指定容器，按如下命令：

 kubectl exec -it pod-first  -c  tomcat-first -- /bin/bash
```

我们上面创建的 pod是一个自主式 pod，也就是通过 pod创建一个应用程序，如果 pod出现故障停
掉，那么我们通过 pod部署的应用也就会停掉，不安全，  还有一种控制器管理的 pod，通过控制器创建
pod，可以对 pod的生命周期做管理， 可以定义pod的副本数，如果有一个 pod意外停掉，那么会自动起
来一个pod替代之前的 pod，之后会讲解 pod的控制器

**2.3 通过kubectl run创建Pod**

kubectl run tomcat --image=xianchao/tomcat -8.5-jre8:v1  --image-pull-

```bash
policy='IfNotPresent'  --port=8080
```

3.命名空间
**3.1 什么是命名空间？**
Kubernetes 支持多个虚拟集群，它们底层依赖于同一个物理集群。  这些虚拟集群被称为命名空
间。
命名空间namespace 是k8s集群级别的资源， 可以给不同的用户、租户、环境或项目 创建对应的 命
名空间，例如，可以为 test、devlopment 、production 环境分别创建各自的 命名空间。

**3.2 namespace 应用场景**
命名空间适用于存在很多跨多个团队或项目的用户的场景。对于只有几到几十个用户的集群，根本
不需要创建或考虑命名空间。

**1、查看名称空间及其资源对象**
k8s集群默认提供了几个名称空间用于特定目的，例如， kube-system主要用于运行系统级资源，
存放k8s一些组件的。 而default 则为那些未指定名称空间的资源操作提供一个默认值。

使用kubectl get namespace 可以查看 namespace 资源，使用 kubectl describe namespace
$NAME可以查看特定的名称空间的详细信息。

**2、管理namespace 资源**
namespace 资源属性较少，通常只需要指定名称即可创建，如 “kubectl create namespace
qa”。namespace 资源的名称仅能由字母、数字、下划线、连接线等字符组成。删除 namespace 资
源会级联删 除其包含的所有其他资源对象 。

**3.3 namespacs 使用案例分享**

```bash
#创建一个 test命名空间
[root@xianchaomaster 1~]# kubectl create ns test

#切换命名空间
[root@xianchaomaster 1~]# kubectl  config set -context --current --namespace=kube -system

#切换命名空间后， kubectl get pods 如果不指定 -n，查看的就是 kube-system命名空间的资源
```
了。

```bash
#查看哪些资源 属于命名空间 级别的
[root@xianchaomaster 1~]# kubectl api -resources --namespaced=true
```

**3.4 namespace 资源限额**

```bash
[root@xianchaomaster 1~]# kubectl  config set -context --current –namespace =default
```

namespace 是命名空间，里面 有很多资源，那么我们可以对命名空间资源做个限制，防止该命名空间
部署的资源超过限制。
如何对namespace 资源做限额呢？

```bash
[root@xianchaomaster 1~]# vim namespace -quota.yaml
```

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: mem -cpu-quota
  namespace: test
spec:
  hard:
    requests.cpu: "2"
    requests.memory: 2G i
    limits.cpu: "4"
    limits.memory: 4Gi

#创建的ResourceQuota 对象将在 test名字空间中添加以下限制：
```
每个容器必须设置内存请求（ memory request ） ，内存限额（ memory limit ），cpu请求（cpu
request）和cpu限额（cpu limit ）。
    所有容器的内存请求总额不得超过 2GiB。
    所有容器的内存限额总额不得超过 4 GiB。
    所有容器的 CPU请求总额不得超过 2 CPU。
    所有容器的 CPU限额总额不得超过 4CPU。

```bash
#创建pod时候必须设置资源限额，否则创建失败 ，如下：
[root@xianchaomaster1 ~]# vim pod-test.yaml
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod -test
  namespace: test
  labels:
    app: tomcat -pod-test

 spec:
  containers:
  - name:  tomcat -test
    ports:
    - containerPort: 8080
    image: xianchao/tomcat -8.5-jre8:v1
    imagePullPolicy: IfNotPresent
    resources:
      requests:
        memory: "100Mi"
        cpu: "500m"
      limits:
        memory: "2Gi"
        cpu: "2"

```

```bash
[root@xianchaomaster1 ~]# kubectl apply -f pod-test.yaml
```

4.标签
**4.1 什么是标签？**
标签其实就一对  key/value ，被关联到对象上，比如 Pod,标签的使用我们倾向于能够 表示对象的特
殊特点，就是一眼就看出了这个 Pod是干什么的，标签可以用来划分特定的对象（比如版本，服务类型
等），标签可以在创建一个对象的时候直接 定义，也可以在后期随时修改，每一个对象可以拥有多个标
签，但是， key值必须是唯一的 。创建标签之后 也可以方便我们对资源进行分组管理。 如果对pod打标
签，之后就可以使用标签来查看、删除指定的 pod。
在k8s中，大部分资源都可以打标签 。

**4.2 给pod资源打标签**

```bash
#对已经存在的 pod打标签
[root@xianchaomaster 1~]# kubectl label pods pod -first  release=v1
```
查看标签是否打成功：

```bash
[root@xianchaomaster 1~]# kubectl get pods  pod-first --show-labels
```

显示如下 ,显示如下，说明标签达成功了；
NAME         READY   STATUS    RESTARTS   AGE   LABELS
pod-first    1/1     Running   1          21h   release= v1, app=tomcat-pod-first

**4.3 查看资源标签**

```bash
#查看默认名称空间下 所有pod资源的标签
[root@xianchaomaster 1~]# kubectl get pods --show-labels

 #查看默认名称空间下 指定pod具有的所有标签
[root@xianchaomaster 1~]# kubectl get pods pod-first --show-labels

#列出默认名称空间下 标签key是release 的pod，不显示标签
[root@xianchaomaster 1~]# kubectl get pods -l release

#列出默认名称空间下 标签key是release、值是v1的pod，不显示标签
[root@xianchaomaster 1~]# kubectl get pods -l release=v1

#列出默认名称空间下标签 key是release 的所有pod，并打印对应的标签值
[root@xianchaomaster 1~]# kubectl get pods -L release

#查看所有名称空间下的所有 pod的标签
[root@xianchaomaster1 ~]# kubectl get pods --all-namespace --show-labels

   [root@xianchaomaster1 ~]# kubectl get pods -l release=v1 -L release
NAME        READY   STATUS    RESTARTS   AGE   RELEASE
pod-first   1/1     Running   0          13h   v1
```

5.pod资源清单详细解读

```yaml
apiVersion: v1       # 版本号，例如 v1
kind: Pod       # 资源类型，如 Pod
metadata:       # 元数据
  name: string       # Pod 名字
  namespace: string    # Pod 所属的命名空间
  labels:      # 自定义标签
    - name: string     # 自定义标签名字
  annotations:       # 自定义注释列表
    - name: string
spec:         # Pod 中容器的详细定义
  containers:      # Pod 中容器列表
  - name: string     # 容器名称
    image: string    # 容器的镜像名称
    imagePullPolicy: [Always | Never | IfNotPresent] # 获取镜像的策略  Alawys表示下载镜
```
像 IfnotPresent 表示优先使用本地镜像，否则下载镜像， Nerver表示仅使用本地镜像
    command: [string]    # 容器的启动命令列表，如不指定，使用打包时使用的启动命令
    args: [string]     # 容器的启动命令参数列表
    workingDir: string     # 容器的工作目录
    volumeMounts:    # 挂载到容器内部的存储卷配置
    - name: string     # 引用pod定义的共享存储卷的名称，需用 volumes[] 部分定义的的卷名
      mountPath: string    # 存储卷在容器内 mount的绝对路径，应少于 512字符
      readOnly: boolean    # 是否为只读模式

    - name: string     # 端口号名称
      hostPort: int    # 容器所在主机需要监听的端口号，默认与 Container 相同
      protocol: string     # 端口协议，支持 TCP和UDP，默认TCP
    env:       # 容器运行前需设置的环境变量列表
    - name: string     # 环境变量名称
      value: string    # 环境变量的值
    resources:       # 资源限制和请求的设置
      limits:      # 资源限制的设置
        cpu: string    # cpu的限制，单位为 core数
        memory: string     # 内存限制，单位可以为 Mib/Gib
      requests:      # 资源请求的设置
        cpu: string    # cpu请求，容器启动的初始可用数量
        memory: string     # 内存请求，容器启动的初始可用 内存
    livenessProbe:     # 对Pod内个容器健 康检查的设置，当探测无响应几次后将自动重启该
容器，检查方法有 exec、httpGet 和tcpSocket ，对一个容器只需设置其中一种方法即可
      exec:      # 对Pod容器内检查方式设置为 exec方式
        command: [string]  #exec 方式需要制定的命令或脚本
      httpGet:       # 对Pod内个容器健康检查方法设置为 HttpGet，需要制定 Path、port
        path: string
        port: numbe r
        host: string
        scheme: string
        HttpHeaders:
        - name: string
          value: string
      tcpSocket:     # 对Pod内个容器健康检查方式设置为 tcpSocket 方式
         port: number
       initialDelaySeconds: 0  # 容器启动完成后首次探测的时间，单位为秒
       timeoutSec onds: 0   # 对容器健康检查探测等待响应的超时时间，单位秒，默认 1秒
       periodSeconds: 0    # 对容器监控检查的定期探测时间设置，单位秒，默认 10秒一次
       successThreshold: 0
       failureThreshold: 0
       securityContext:
         privileged:false
    restartPolicy: [Always | Never | OnFailure]#Pod 的重启策略 ，Always表示一旦不管以
何种方式终止运行， kubelet 都将重启， OnFailure 表示只有 Pod以非0退出码退出才重启，
Nerver表示不再重启该 Pod
    nodeSelector: obeject  # 设置NodeSelector 表示将该 Pod调度到包含这个 label的node
上，以key：value的格式指定
    imagePullSecrets:    #Pull 镜像时使用的 secret名称，以 key：secretkey 格式指定
    - name: string

     hostNetwork:false      # 是否使用主机网络模式，默认为 false，如果设置为 true，表示
使用宿主机网络
    volumes:       # 在该pod上定义共享存储卷列表
    - name: string     # 共享存储卷名称  （volumes 类型有很多种）
      emptyDir: {}     # 类型为emtyDir 的存储卷，与 Pod同生命周期的一个临时目录。为空
值
      hostPath: string     # 类型为hostPath 的存储卷，表示挂载 Pod所在宿主机的目录
        path: string     #Pod 所在宿主机的目录，将被用于同期中 mount的目录
      secret:      # 类型为secret的存储卷，挂载集群与定义的 secre对象到容器内部
        scretname: string
        items:
        - key: string
          path: string
      configMap:     # 类型为configMap 的存储卷，挂载预定义的 configMap 对象到容器内部
        name: string
        items:
        - key: string
          path: string

**6. node节点选择器**
我们在创建 pod资源的时候， pod会根据schduler 进行调度，那么默认会调度到随机的一个工作
节点，如果我们想要 pod调度到指定节点或者调度到一些具有相同特点的 node节点，怎么办呢？
可以使用 pod中的nodeName 或者nodeSelector 字段指定要调度到的 node节点

**1、nodeName ：**
指定pod节点运行在哪个具体 node上

```bash
#把tomcat.tar.gz 上传到xianchaonode1 和xianchaonode2 ，手动解压：
[root@xianchaonode1  ~]# docker load -i tomcat.tar.gz
Loaded image: tomcat:8.5 -jre8-alpine
[root@xianchaonode2  ~]# docker load -i tomcat.tar.gz
Loaded image: tomcat:8.5 -jre8-alpine
# 把busybox.tar.gz 上传到xianchaonode1 和xianchaonode2 ，手动解压：
[root@xianchaonode1  ~]# docker load -i busybox.tar.gz
[root@xianchaonode2  ~]# docker load -i busybox.tar.gz

[root@xianchaomaster1  ~]# cat pod -node.yaml
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: demo -pod

   namespace: default
  labels:
    app: myapp
    env: dev
spec:
  nodeName : xianchaonode1
  containers:
  - name:  tomcat -pod-java
    ports:
    - containerPort: 8080
    image: tomcat:8.5 -jre8-alpine
    imagePullPolicy: IfNotPresent
  - name: busybox
    image: busybox:latest
    command:
    - "/bin/sh"
    - "-c"
- "sleep 3600"

```

```bash
[root@xianchaomaster1  ~]# kubectl apply -f pod-node.yaml
#查看pod调度到哪个节点
[root@xianchaomaster1  ~]# kubectl get pods  -o wide
NAME             READY   STATUS    RESTARTS
demo-pod        1/1     Running   0            xianchaonode1

2、nodeSelector ：
```
指定pod调度到具有哪些标签的 node节点上

```bash
#给node节点打标签，打个具有 disk=ceph的标签
[root@xianchaomaster1  ~]# kubectl label nodes xianchaonode2  disk=ceph
node/xianchaonode2  labeled
#定义pod的时候指定要调度到具有 disk=ceph 标签的node上
[root@xianchaomaster1  ~]# cat pod -1.yaml
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: demo -pod-1
  namespace: default
  labels:
    app: myapp
    env: dev
spec:
  nodeSelector:
    disk: ceph

   containers:
  - name:  tomcat -pod-java
    ports:
    - containerPort: 8080
    image: tomcat:8.5 -jre8-alpine
    imagePullPolicy: IfNotPresent

```

```bash
[root@xianchaomaster1  ~]# kubectl apply -f pod-1.yaml
#查看pod调度到哪个节点
[root@xianchaomaster1  ~]# kubectl get pods  -o wide
NAME             READY   STATUS    RESTARTS
demo-pod-1        1/1     Running   0            xianchaonode2
```

**7、污点和容忍度**
**7.1 node节点亲和性**
node节点亲和性调度： nodeAffinity

```bash
[root@xianchaomaster1  ~]# kubectl explain pods.spec.affinity
```

```yaml
KIND:     Pod
VERSION:  v1
RESOURCE: affinity <Object>
DESCRIPTION:
     If specified, the pod's scheduling constraints
    Affinity is a group of affinity scheduling rules.
FIELDS:
   nodeAffinity  <Object>
   podAffinity  <Object>
   podAntiAffinity  <Object>

```

```bash
[root@xianchaomaste r1 ~]#  kubectl explain  pods.spec.affinity.nodeAffinity
```

```yaml
KIND:     Pod
VERSION:  v1
RESOURCE: nodeAffinity <Object>
DESCRIPTION:
     Describes node affinity scheduling rules for the pod.
     Node affinity is a group of node affinity scheduling rules.
FIELDS:
   preferredDuringSchedulingIgnoredDuringExecution  <[]Object>
   requiredDuringSchedulingIgnoredDuringExecution  <Object>

```
prefered 表示有节点尽量满足这个位置定义的亲和性，这不是一个必须的条件，软亲和性
require 表示必须有节 点满足这个位置定义的亲和性，这是个硬性条件，硬亲和性

```bash
[root@xianchaomaster1  ~]# kubectl explain
pods.spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution

```

```yaml
 KIND:     Pod
VERSION:  v1
RESOURCE: requiredDuringSchedulingIgnoredDuringExecution <Object>
DESCRIPTION:
FIELDS:
   nodeSelectorTerms  <[]Object> -required -
     Required. A list of node selector terms. The terms are ORed.

```

```bash
[root@xianchaomaster1  ~]# kubectl explain
pods.spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSe
lectorTerms
```

```yaml
KIND:     Pod
VERSION:  v1
RESOURCE: nodeSelectorTerms <[]Object>
DESCRIPTION:
     Required. A list of node selector terms. The terms are ORed.
     A null or empty node selector term matches no objects. The requirements of
     them are ANDed. The Topolog ySelectorTerm type implements a subset of the
     NodeSelectorTerm.
FIELDS:
   matchExpressions  <[]Object>
   matchFields  <[]Object>
```
matchExpressions ：匹配表达式的
matchFields ： 匹配字段的

```bash
[root@xianchaomaster1  ~]# kubectl explain
pods.spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSe
lectorTerms.matchFields
```

```yaml
KIND:     Pod
VERSION:  v1
RESOURCE: matchFields <[]Object>
DESCRIPTION:

FIELDS:
   key <string> -required -
   values <[]string>

```

```bash
[root@xianchaomaster1  ~]# kubectl explain
pods.spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSe
lectorTerms.matchExpressions
```

```yaml
KIND:     Pod
VERSION:  v1
RESOURCE: matchExpressions <[]Object>

 DESCRIPTION:
FIELDS:
   key <string> -required -
   operator  <string> -required -
   values <[]string>
```
key：检查label
operator ：做等值选则还是不等值选则
values：给定值

例1：使用requiredDuringSchedulingIgnoredDuringExecution 硬亲和性

```bash
#把myapp-v1.tar.gz 上传到xianchaonode2 和xianchaonode1 上，手动解压：
[root@xianchaonode1  ~]# docker load -i myapp-v1.tar.gz
Loaded image: ikubernetes/myapp:v1
[root@xianchaonode2  ~]# docker load -i myapp-v1.tar.gz
Loaded image: ikubernetes/myapp:v1

[root@xianchaomaster1  ~]# cat pod -nodeaffinity -demo.yaml
```

```yaml
apiVersion: v1
kind: Pod
metadata:
        name: pod -node-affinity -demo
        namespace: default
        labels:
            app: myapp
            tier: frontend
spec:
    containers:
    - name: myapp
      image: ikubernetes/myapp:v1
    affinity:
        nodeAffinity:
            requiredDuringSchedulingIgnoredDuringExecution:
                   nodeSelectorTerms:
                   - matchExpressions:
                     - key: zone
                       operator: In
                       values:
                       - foo
                       - bar

```
我们检查当前节点中有任意一个节点拥有 zone标签的值是 foo或者bar，就可以把 pod调度到这
个node节点的foo或者bar标签上的节点上

```bash
[root@xianchaomaster1  ~]# kubectl apply -f pod-nodeaffinity -demo.yaml

 [root@xianchaomaster1  ~]# kubectl get pods -o wide | grep pod -node
pod-node-affinity -demo             0/1     Pending     0   xianchaonode1
```
status的状态是 pending，上面说明没有完成调度，因为没有一个拥有 zone的标签的值是 foo或
者bar，而且使用的是硬亲和性，必须满足条件才能完成调度

```bash
[root@xianchaomaster1  ~]# kubectl lab el nodes xianchaonode1  zone=foo
```
给这个xianchaonode1 节点打上标签 zone=foo ，在查看

```bash
[root@xianchaomaster1  ~]#kubectl get pods -o wide 显示如下：
pod-node-affinity -demo             1/1     Running  0   xianchaonode1
```

例2：使用preferredDuringSchedulingIgnoredDuringExecution 软亲和性

```bash
[root@xianchaomaster1  ~]# cat pod -nodeaffinity -demo-2.yaml
```

```yaml
apiVersion: v1
kind: Pod
metadata:
        name: pod -node-affinity -demo-2
        namespace: default
        labels:
            app: myapp
            tier: frontend
spec:
    containers:
    - name: myapp
      image: ikubernetes/myapp:v1
    affinity:
        nodeAffinity:
            preferredDuringSchedulingIgnoredDuringExecution:
            - preference:
               matchExpressions:
               - key: zone1
                 operator: In
                 values:
                 - foo1
                 - bar1
              weight: 60
```

```bash
[root@xianchaomaster1  ~]# kubectl apply -f pod-nodeaffinity -demo-2.yaml
[root@xianchaomaster1  ~]# kubectl get pods -o wide |grep demo -2
pod-node-affinity -demo-2           1/1     Running     0        xianchaonode1
```

上面说明软亲和性 是可以运行这个 pod的，尽管没有运行这个 pod的节点定义的 zone1标签

Node节点亲和性针对的是 pod和node的关系， Pod调度到node节点的时候匹配的条件

**7.2 Pod节点亲和性**
pod自身的亲和性调度有两种表示形式
podaffinity ：pod和pod更倾向腻在一起，把相近的 pod结合到相近的位置，如同一区域，同一
机架，这样的话 pod和pod之间更好通信，比方说有两个机房，这两个机房部署的集群有 1000台
主机，那么我们希望把 nginx和tomcat都部署同一个地方的 node节点上，可以提高通信效率；

podunaffinity ：pod和pod更倾向不腻在一起，如果部署两套程序，那么这两套程序更倾向于反
亲和性，这样相互之间不会有影响 。

第一个pod随机选则一个节点，做为评判后续的 pod能否到达这个 pod所在的节点上 的运行方
式，这就称为 pod亲和性；我们怎么判定哪些节点是相同位置的，哪些节点是不同位置的；我们
在定义pod亲和性时需要有一个前提，哪些 pod在同一个位置，哪些 pod不在同一个位置，这个
位置是怎么定义的，标准是什么？以节点名称为标准，这个节点名称相同的表示是同一个位置，
节点名称不相同的表示不是一个位置。

```bash
[root@xianchaomaster1  ~]# kubectl explain pods.spec.affinity.podAffinity
```

```yaml
KIND:     Pod
VERSION:  v1
RESOURCE: podAffinity <Object>
DESCRIPTION:
     Describes pod affinity scheduling rules (e.g. co -locate this pod in the
     same node, zone, etc. as some other pod(s)).
     Pod affinity is a group of inter pod affinity scheduling rules.
FIELDS:
   preferre dDuringSchedulingIgnoredDuringExecution  <[]Object>
   requiredDuringSchedulingIgnoredDuringExecution  <[]Object>

```
requiredDuringSchedulingIgnoredDuringExecution ： 硬亲和性
preferredDuringSchedulingIgnoredDuringExecution ：软亲和性

```bash
[root@xianchaomaster1  ~]# kubectl  explain
pods.spec.affinity.podAffinity.requiredDuringSchedulingIgnoredDuringExecution
```

```yaml
KIND:     Pod
VERSION:  v1
RESOURCE: requiredDuringSchedulingIgnoredDuringExecution <[]Object>
DESCRIPTION:
FIELDS:
   labelSelector  <Object>
   namespaces  <[]string>
   topologyKey  <string> -required -

topologyKey ：
```

 位置拓扑的键，这个是必须字段
怎么判断是不是同一个位置：

```bash
rack=rack1
row=row1
```
使用rack的键是同一个位置
使用row的键是同一个位置
labelSelector ：
我们要判断 pod跟别的pod亲和，跟哪个 pod亲和，需要靠 labelSelector ，通过labelSelector
选则一组能作为亲和对象的 pod资源
namespace ：
labelSelector 需要选则一组资源，那么这组资源是在哪个名称空间中呢，通过 namespace 指定，
如果不指定 namespaces ，那么就是当前创建 pod的名称空间

```bash
[root@xianchaomaster1  ~]# kubectl explain
pods.spec.affinity.podAffinity.requiredDuringSchedulingIgnoredDuringExecution.labelSe
lector
```

```yaml
KIND:     Pod
VERSION:  v1
RESOURCE: labelSelecto r <Object>
DESCRIPTION:
     A label query over a set of resources, in this case pods.
     A label selector is a label query over a set of resources. The result of
     matchLabels and matchExpressions are ANDed. An empty label selector matches
     all objects. A null label selector matches no objects.
FIELDS:
   matchExpressions  <[]Object>
   matchLabels  <map[string]string>

```
例1：pod节点亲和性
定义两个 pod，第一个 pod做为基准，第二个 pod跟着它走

```bash
[root@xianchaomaster 1]# kubectl delete pods pod -first
[root@xianchaomaster1  ~]# cat pod -required -affinity -demo.yaml
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod -first
  labels:
    app2: myapp2
    tier: frontend
spec:
    containers:
    - name: myapp
      image: ikubernetes/myapp:v1
```

 ---

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod -second
  labels:
    app: backend
    tier: db
spec:
    containers:
    - name: busybox
      image: busybox:latest
      imagePullPolicy: IfNotPresent
      command: ["sh"," -c","sleep 3600"]
    affinity:
      podAffinity:
         requiredDuringSchedulingIgnoredDuringExecution:
         - labelSelector:
              matchExpressions:
              - {key: app 2, operator: In, values: ["myapp 2"]}
           topologyKey: kubernetes.io/hostname

#上面表示创建的 pod必须与拥有 app=myapp标签的pod在一个节点上
```

```bash
[root@xianchaomaster1  ~]# kubectl apply -f pod-required -affinity -demo.yaml
```
kubectl get pods -o wide 显示如下：
pod-first              running        xianchaonode1
pod-second           running        xianchaonode1

上面说明第一个 pod调度到哪，第二个 pod也调度到哪，这就是 pod节点亲和性

```bash
[root@xianchaomaster1  ~]# kubectl delete -f pod-required -affinity -demo.yaml
```
> **注意：**

```bash
[root@xianchaomaster1 ~]# kubectl get nodes --show-labels
```

例2：pod节点反亲和性
定义两个 pod，第一个 pod做为基准，第二个 pod跟它调度节点相反

```bash
[root@xianchaomaster1  ~]# cat pod -required -anti-affinity -demo.yaml
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod -first
  labels:
    app1: myapp1

     tier: frontend
spec:
    containers:
    - name: myapp
      image: ikubernetes/myapp:v1
---
apiVersion: v1
kind: Pod
metadata :
  name: pod -second
  labels:
    app: backend
    tier: db
spec:
    containers:
    - name: busybox
      image: busybox:latest
      imagePullPolicy: IfNotPresent
      command: ["sh"," -c","sleep 3600"]
    affinity:
      podAntiAffinity:
         requiredDuringSchedulingIgnoredDuringExecution:
         - labelSelector:
              matchExpressions:
              - {key: app 1, operator: In, values: ["myapp 1"]}
           topologyKey: kubernetes.io/hostname
```

```bash
[root@xianchaomaster1  ~]# kubectl apply -f pod-required -anti-affinity -demo.yaml
[root@xianchaomaster1  ~]# kubectl get pods -o wide 显示两个 pod不在一个 node节点上，
```
这就是pod节点反亲和性
pod-first            running        xianchaonode1
pod-second           running        xianchaonode2

```bash
[root@xianchaomaster1  ~]# kubectl delete -f pod-required -anti-affinity -demo.yaml
```

例3：换一个 topologykey

```bash
[root@xianchaomaster1  ~]# kubectl label nodes  xianchaonode2   zone=foo
[root@xianchaomaster1  ~]# kubectl label nodes  xianchaonode1  zone=foo --overwrite
[root@xianchaomaster1]# cat pod -first-required -anti-affinity -demo-1.yaml
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod -first
  labels:

     app3: myapp3
    tier: frontend
spec:
    containers:
    - name: myapp
      image: ikubernetes/myapp:v1

```

```bash
[root@xianchaomaster1]# cat pod -second-required -anti-affinity -demo-1.yaml
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod -second
  labels:
    app: backend
    tier: db
spec:
    containers:
    - name: busybox
      image: busybox:latest
      imagePullPolicy: IfNotPresent
      command: ["sh"," -c","sleep 3600"]
    affinity:
      podAntiAffinity:
         requiredDuringSchedulingIgnoredDuringExecution:
         - labelSelector:
              matchExpressions:
              - {key: app3 ,operator: In, values: ["myapp3"]}
           topologyKey:  zone

```

```bash
[root@xianchaomaster1 affinity]# kubectl apply -f pod-first-required -anti-affinity -
demo-1.yaml

[root@xianchaomaster1 affinity]# ku bectl apply -f pod-second-required -anti-affinity -
demo-1.yaml

[root@xianchaomaster1  ~]#kubectl get pods -o wide 显示如下：
pod-first              running         xianchaonode1
pod-second           pending         <none>
```

第二个节点现是 pending，因为两个节点是同一个位置，现在没有不是同一个位置的 了，而且我们
要求反亲和性，所以就会处于 pending 状态，如果在反亲和性这个位置把 required 改成
preferred ，那么也会运行 。
podaffinity ：pod节点亲和性， pod倾向于哪个 pod

 nodeaffinity ：node节点亲和性， pod倾向于哪个 node

**7.3 污点、容忍度**
给了节点选则的主动权，我们 给节点打一个污点，不容忍的 pod就运行不上来，污点就是定义在
节点上的键值属性数据，可以定决定拒绝那些 pod；
taints是键值数据，用在节点上，定义 污点；
tolerations 是键值数据，用在 pod上，定义容忍度，能容忍哪些污点
pod亲和性是 pod属性；但是污点是节点的属性，污点定义在 nodeSelector 上

```bash
[root@xianchaomaster1 affinity]# kubectl describe nodes xianchaomaster1

Taints:             node-role.kubernetes.io/master:NoSchedule

[root@xianchaomaster1  ~]# kubectl explain node.spec.taints
```

```yaml
KIND:     Node
VERSION:  v1
RESOURCE: taints <[]Object>
DESCRIPTION:
     If specified, the node's taints.
     The node this Taint is attached to has the  "effect" on any pod that does
     not tolerate the Taint.
FIELDS:
   effect <string> -required -
   key <string> -required -
   timeAdded  <string>
   value <string>

```
taints的effect用来定义对 pod对象的排斥等级（效果） ：

NoSchedule ：
仅影响pod调度过程，当 pod能容忍这个节点污点，就可以调度到当前节点，后来这个节点的 污
点改了，加了一个新的污点，使得之前调度的 pod不能容忍了，那这个 pod会怎么处理，对现存
的pod对象不产生影响

NoExecute ：
既影响调度过程，又影响现存的 pod对象，如果现存的 pod不能容忍节点后来加的污点，这个 pod
就会被驱逐

PreferNoSchedule ：
最好不，也可以，是 NoSchedule 的柔性版本

在pod对象定义容忍度的时候支持两种操作：
1.等值密钥： key和value上完全匹配

 2.存在性判断： key和effect必须同时匹配， value可以是空
在pod上定义的容忍度可能不止一个，在节点上定义的污点可能 多个，需要琢个检查容忍度和污
点能否匹配，每一个污点都能被容忍，才能完成调度，如果不能容忍怎么办，那就需要看 pod的
容忍度了

```bash
[root@xianchaomaster1  ~]# kubectl describe nodes xianchaomaster1
```
查看master这个节点是否有污点，显示如下：

上面可以看到 master这个节点的污点是 Noschedule

所以我们创建的 pod都不会调度到 master上，因为我们创建的 pod没有容忍度

```bash
[root@xianchaomaster1  ~]# kubectl describe pods kube -apiserver -xianchaomaster1  -n
kube-system
```
显示如下：

可以看到这个 pod的容忍度是 NoExecute ，则可以调度到 xianchaomaster1 上

管理节点污点

```bash
[root@xianchaomaster1]# kubectl taint –help
```

例1：把xianchaonode2 当成是生产环境专用的，其他 node是测试的

```bash
[root@xianchaomaster1  ~]# kubectl taint node xianchaonode2  node-
type=production:NoSchedule
```

给xianchaonode2 打污点， pod如果不能容忍就不会调度过来）

```bash
[root@xianchaomaster1  ~]# cat pod -taint.yaml
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: taint -pod
  namespace: default
  labels:
    tomcat:  tomcat -pod
spec:
  containers:

   - name:  taint -pod
    ports:
    - containerPort: 8080
    image: tomcat:8.5 -jre8-alpine
imagePullPolicy: IfNotPresent

```

```bash
[root@xianchaomaster1  ~]# kubectl apply -f pod-taint.yaml
[root@xianchaomaster1  ~]# kubectl get pods -o wide
```
显示如下：
taint-pod   running    xianchaonode1

可以看到都被调度到 xianchaonode1 上了，因为 xianchaonode2 这个节点打了污点，而我们在创
建pod的时候没有容忍度，所以 xianchaonode2 上不会有 pod调度上去的

例2：给xianchaonode1 也打上污点

```bash
[root@xianchaomaster1  ~]# kubectl delete -f pod-taint.yaml
[root@xianchaomaster1  ~]#kubectl taint node xianchaonode1  node-type=dev:NoExecute
[root@xianchaomaster1  ~]#kubectl get pods -o wide
```
显示如下：
taint-pod   termaitering
上面可以看到已经存在的 pod节点都被撵走了

```bash
[root@xianchaomaster1  ~]# cat pod -demo-1.yaml
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp -deploy
  namespace: default
  labels:
    app: myapp
    release: canary
spec:
      containers:
      - name: myapp
        image: ikubernetes/myapp:v1
        ports:
        - name: http
          containerPort: 80
      tolerations:
      - key: "node -type"
        operator: "Equal"
        value: "production"
        effect: " NoExecute"

         tolerationSeconds: 3600
```

```bash
[root@xianchaomaster1  ~]# kubectl apply -f pod-demo-1.yaml
[root@xianchaomaster1  ~]# kubectl get pods
myapp-deploy   1/1     Pending   0          11s  xianchaonode2
```

还是显示 pending，因为我们使用的是 equal（等值匹配） ，所以 key和value，effect必须和
node节点定义的污点完全匹配才可以，把上面配置 effect: "NoExecute" 变成
effect: "NoSchedule" 成；
tolerationSeconds: 3600 这行去掉

```bash
[root@xianchaomaster1  ~]# kubectl delete -f pod-demo-1.yaml
[root@xianchaomaster1  ~]# kubectl apply -f pod-demo-1.yaml
[root@xianchaomaster1  ~]# kubectl get pods
myapp-deploy   1/1     running  0          11s  xianchaonode2
```

上面就可以调度到 xianchaonode2 上了，因为在 pod中定义的容忍度能容忍 node节点上的污点

例3：再次修改
修改如下部分：
tolerations:
- key: "node -type"
operator: "Exists"
value: ""
effect: "NoSchedule"

只要对应的键是存在的， exists，其值被自动定义成通配符

```bash
[root@xianchaomaster1 ~]# kubectl delete -f pod-demo-1.yaml
[root@xianchaomaster1  ~]# kubectl apply -f pod-demo-1.yaml
[root@xianchaomaster1  ~]# kubectl get pods
```
发现还是调度到 xianchaonode2 上
myapp-deploy   1/1     running  0          11s  xianchaonode2

再次修改：
tolerations:
- key: "node -type"
operator: "Exists"
value: ""
effect: ""
有一个node-type的键，不管值是什么，不管是什么效果，都能容忍

```bash
[root@xianchaomaster1 ~]# kubectl delete -f pod-demo-1.yaml
[root@xianchaomaster 1 ~]# kubectl apply -f pod-demo-1.yaml
[root@xianchaomaster1  ~]#  kubectl get pods -o wide 显示如下 :
myapp-deploy  running    xianchaonode1
```

可以看到 xianchaonode2 和xianchaonode1 节点上都有 可能有pod被调度

删除污点：

```bash
[root@xianchaomaster1 taint]# kubectl taint nodes xianchaonode1 node -type:NoExecute -
[root@xianchaomaster1 taint]# kubectl taint nodes xianchaonode2 node -type-
```

**8、Pod常见的状态和重启策略**
**8.1 常见的pod状态**
Pod的status定义在PodStatus 对象中，其中有一个 phase字段。它简单描述了 Pod在其生命周
期的阶段。熟悉 Pod的各种状态对我们理解如何设置 Pod的调度策略、重启策略是很有必要的。
下面是 phase 可能的值 ，也就是 pod常见的状态：
挂起（Pending）：我们在请求创建 pod时，条件不满足，调度没有完成，没有任何一个节点能满
足调度条件 ，已经创建了 pod但是没有适合它运行的节点叫做挂起，调度没有完成 ，处于pending
的状态会持续一段时间：包括 调度Pod的时间和通过网络下载镜像的时间 。
运行中（ Running）：Pod已经绑定到了一个节点上， Pod 中所有的容器都已被创建。至少有一个容
器正在运行，或者正处于启动或重启状态。
成功（Succeeded ）：Pod 中的所有容器都被成功终止，并且不会再重启。
失败（Failed）：Pod 中的所有容器都已终止了，并且至少有一个容器是因为失败终止。也就是
说，容器以非 0状态退出或者被系统终止。
未知（Unknown）：未知状态，所谓 pod是什么状态是 apiserver 和运行在 pod节点的kubelet 进
行通信获取状态信息的，如果节点之上的 kubelet 本身出故障，那么 apiserver 就连不上
kubelet，得不到信息了 ，就会看 Unknown

扩展：还有其他状态，如下：
Evicted 状态：出现这种情况，多见于系统内存或 硬盘资源不足，可 df-h查看docker存储所在目
录的资源使用情况，如果百分比大于 85%，就要及时清理下资源，尤其是一些大文件、 docker镜
像。
CrashLoopBackOff ：容器曾经启动了，但可能又异常退出了
Error 状态：Pod 启动过程中发生了错误

**8.2 pod重启策略**
Pod的重启策略（ RestartPolicy ）应用于 Pod内的所有容器，并且仅在 Pod所处的Node上由
kubelet 进行判断和重启操作。当某个容器异常退出或者健康检查失败时， kubelet 将根据
RestartPol icy 的设置来进行相应的操作。

Pod的重启策略包括  Always、OnFailure 和Never，默认值为 Always。
Always：当容器失败时，由 kubelet 自动重启该容器。
OnFailure ：当容器终止运行且退出码不为 0时，由kubelet 自动重启该容器。
Never：不论容器运行状态如何， kubelet 都不会重启该容器。

```bash
[root@xianchaomaster1  ~]# vim pod.yaml
```

```yaml
apiVersion: v1

 kind: Pod
metadata:
  name: demo -pod
  namespace: default
  labels:
    app: myapp
spec:
  restartPolicy: Always
  containers:
  - name:  tomcat -pod-java
    ports:
    - containerPort: 8080
    image: tomcat:8.5 -jre8-alpine
    imagePullPolicy: IfNotPresent

```
**9. Pod生命周期**

**9.1 Init容器**
Pod 里面可以有一个或者多个容器，部署应用的容器可以称为主容器，在创建 Pod时候，Pod 中
可以有一个或多个先于 主容器启动的 Init容器,这个init容器就可以成为初始化容器， 初始化容
器一旦执行完，它从启动开始到初始化代码执行完就退出了，它不会一直存在，所以在主 容器启
动之前执行初始化，初始化容器可以有多个，多个初始化容器是要串行执行的，先执行初始化容
器1，在执行初始化容器 2等，等初始化容器执行完初始化就退出了，然后 再执行主容器，主容器
一退出， pod就结束了，主容器退出的时间点就是 pod的结束点，它俩时间轴是一致的；

Init容器就是做初始化工作的容器。可以有一个或多个，如果多个按照定义的顺序依次执行，只
有所有的 初始化容器 执行完后，主容器才启动。由于一个 Pod里的存储卷是共享的，所以 Init
Container 里产生的数据可以被主容器使用到， Init Container 可以在多种 K8S资源里被使用

 到，如Deployment 、DaemonSet, StatefulSet 、Job等，但都是在 Pod启动时，在主容器启动前
执行，做初始化工作。

Init容器与普通的容器区别是 :
**1、Init 容器不支持  Readiness, 因为它们必须在 Pod就绪之前运行完成**
**2、每个Init容器必须运行成功 ,下一个才能够运行**
**3、如果 Pod 的 Init 容器失败 ,Kubernetes 会不断地重启该  Pod,直到 Init 容器成功为止 ，然**
而,如果Pod对应的restartPolicy 值为 Never,它不会重新启动 。

初始化容器的官方 地址：
https://kubernetes.io/docs/concepts/workloads/pods/init -containers/#init -containers -
in-use

```bash
[root@xianchaomaster1 init]# cat init.yaml
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp -pod
  labels:
    app: myapp
spec:
  containers:
  - name: myapp -container
    image: busybox:1.28
    command: ['sh', ' -c', 'echo The app is running! && sleep 3600']
  initContainers:
  - name: init -myservice
    image: busybox:1.28
    command: ['sh', ' -c', "until nslookup myservice.$(cat
/var/run/secrets/kubernetes.io/serviceaccount/namespace).svc.cluster.local; do
echo waiting for myservice; sleep 2; done"]
  - name: init -mydb
    image: busybox:1.28
    command: ['sh', ' -c', "until nslookup mydb.$(cat
/var/run/secrets/kubernetes.io/serviceaccount/namespace).svc.cluster.local; do
echo waiting for mydb; sleep 2; done"]

```

```bash
[root@xianchaomaster1 init]# kubectl apply -f init.yaml

[root@xianchaomaster1 init]# kubec tl get pods
NAME                          READY   STATUS     RESTARTS   AGE
myapp-pod                     0/1     Init:0/2   0          2m29s

[root@xianchaomaster1 init]# cat service.yaml
---
```

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myservice
spec:
  ports:
  - protocol: TCP
    port: 80
    targetPort: 9376
---
apiVersion: v1
kind: Service
metadata:
  name: mydb
spec:
  ports:
  - protocol: TCP
    port: 80
    targetPort: 9377

```

```bash
[root@xianchaomaster1 init]# kubectl apply -f service.yaml

[root@xianchaomaster1 init]# kubectl get pods
NAME                          READY   STATUS    RESTARTS   AGE
myapp-pod                     1/1     Running   0          3m36s
```

**9.2 主容器**
**1、容器钩子**
初始化容器启动之后，开始启动主容器，在主容器启动之前有一个 post start hook （容器启动后
钩子）和 pre stop hook （容器结束前钩子） ，无论启动后还是结束前所做的事我们可以把它放两
个钩子，这个钩子就表示用户可以用它来钩住一些命令，来执行它，做开场前的预设，结束前的
清理，如 awk有begin，end，和这个效果类似；
postStart ：该钩子在容器被创建后立刻触发，通知容器它已经被创建。如果该钩子对应的 hook
handler 执行失败，则该容器会被杀死，并根据该容器的重启策略决定是否要重启 该容器，这个钩
子不需要传递任何参数 。
preStop：该钩子在容器被删除前触发，其所对应的 hook handler 必须在删除该容器的请求发送
给Docker daemon 之前完成。在该钩子对应的 hook handler 完成后不论执行的结果如何， Docker
daemon会发送一个 SGTERN信号量给 Docker daemon 来删除该容器，这个钩子不需要传递任何参
数。

 在k8s中支持两类对 pod的检测，第一类叫做 livenessprobe （pod存活性探测） ：
存活探针主要作用是，用指定的方式检测 pod中的容器应用是否正常运行，如果检测失败，则认
为容器不健康，那么 Kubelet 将根据Pod中设置的  restartPolicy 来判断Pod 是否要进行重启操
作，如果容器配置中没有配置  livenessProbe ，Kubelet 将认为存活探针探测一直为成功状态。
第二类是状态检 readinessprobe （pod就绪性探测） ： 用于判断容器中应用是否启动完成，当探测
成功后才使 Pod对外提供网络访问，设置容器 Ready状态为true，如果探测失败，则设置容器的
Ready状态为false。

**9.3 创建pod需要经过哪 些阶段？**
当用户创建 pod时，这个请求给 apiserver ，apiserver 把创建请求的状态保存在 etcd中；
接下来apiserver 会请求scheduler 来完成调度，如果调度成功，会把调度的结果（如调度到哪
个节点上了，运行在哪个节点上了，把它更新到 etcd的pod资源状态中）保存在 etcd中，一旦
存到etcd中并且完成更新以后，如调度到 xianchaonode1 上，那么 xianchaonode1 节点上的
kubelet 通过apiserver 当中的状态变化知道有一些任务被执行了，所以此时此 kubelet 会拿到用
户创建时所提交的清单，这个清单会在当前节点上运行或者启动这个 pod，如果创建成功或者失败
会有一个当前状态，当前这个状态会发给 apiserver ，apiserver 在存到etcd中；在这个过程
中，etcd和apiserver 一直在打交道，不停的交互， scheduler 也参与其中，负责调度 pod到合
适的node节点上，这个就是 pod的创建过程

pod在整个生命周期中有非常多的用户行为：
**1、初始化容器完成初始化**
**2、主容器启动后可以做启动后钩子**
**3、主容器结束前可以做结束前钩子**
**4、在主容器运行中可以 做一些健康检测，如 liveness probe ，readness probe**

10.Pod容器探测 和钩子
**10.1 容器钩子： postStart 和preStop**
postStart ：容器创建成功后，运行前的任务，用于资源部署、环境准备等。
preStop：在容器被终止前的任务，用于优雅关闭应用程序、通知其他系统等。

演示postStart 和preStop 用法
......
containers:
- image: sample:v2
     name: war
     lifecycle ：
      postStart:
       exec:
         command:
          - “cp”
          - “/sample.war”
          - “/app”

       prestop:
       httpGet:
        host: monitor.com
        path: /waring
        port: 8080
        scheme: HTTP
......

以上示例中，定义了一个 Pod，包含一个 JAVA的web应用容器，其中设置了 PostStart 和
PreStop 回调函数。即在容器创建成功后，复制 /sample.war 到/app文件夹中。而在容器终止之
前，发送 HTTP请求到http://monitor.com:8080/waring ，即向监控系统发送警告。

优雅的删除资源对象
当用户请求删除含有 pod的资源对象时（如 RC、deployment 等） ，K8S为了让应用程序优雅关闭
（即让应用程序完成正在处理的请求后，再关闭软件） ， K8S提供两种信息通知：
1） 、默认： K8S通知node执行docker stop 命令，docker会先向容器中 PID为1的进程发送系统
信号SIGTERM，然后等待容器中的应用程序终止执行，如果等待时间达到设定的超时时间，或者默
认超时时间（ 30s） ，会继续发送 SIGKILL 的系统信号强行 kill掉进程。

2） 、使用 pod生命周期（利用 PreStop 回调函数） ，它执行在发送终止信号之前。
默认情况下，所有的删除操作的优雅退出时间都在 30秒以内。 kubectl delete 命令支持 --grace-
period=的选项，以运行用户来修改默认值。 0表示删除立即执行，并且立即从 API中删除pod。
在节点上，被设置了立即结束的的 pod，仍然会给一个很短的优雅退出时间段，才会开始被强制杀
死。如下：

```yaml
    spec:
      containers:
      - name: nginx -demo
        image: centos:nginx
        lifecycle:
          preStop:
            exec:
              # nginx -s quit gracefully terminate while SIGTERM triggers a quick
exit
              command: ["/usr/local/nginx/sbin/nginx"," -s","quit"]
        ports:
          - name: http
            containerPort: 80

```
**10.2 存活性探测 livenessProbe 和就绪性探测 readinessProbe**
   livenessProbe ：存活性探测
  许多应用程序经过长时间运行，最终过渡到无法运行的状态，除了重启，无法恢复。通常情况

 下，K8S会发现应用程序已经终止，然后重启应用程序 pod。有时应用程序可能因为某些原因（后
端服务故障等）导致暂时无法对外提供服务，但应用软件没有终止，导致 K8S无法隔离有故障的
pod，调用者可能会访问到有故障的 pod，导致业务不稳定。 K8S提供livenessProbe 来检测容器
是否正常运行，并且对相应状况进行相应的补救措施。

  readinessProbe ：就绪性探测
在没有配置 readinessProbe 的资源对象中， pod中的容器启动完成后，就认为 pod中的应用程序
可以对外提供服务，该 pod就会加入相对应的 service，对外提供服务。但有时一些应用程序启动
后，需要较长时间的加载才能对外服务，如果这时对外提供服务，执行结果必然无法达到预期效
果，影响用户体验。比如使用 tomcat的应用程序来说，并不是简单地说 tomcat启动成功就可以
对外提供服务的，还需要等待 spring容器初始化，数据库连接上等等。

目前LivenessProbe 和ReadinessProbe 两种探针都支持下面三种探测方法：
**1、ExecAction ：在容器中执行指定的命令，如果执行成功，退出码为  0 则探测成功。**
**2、TCPSocketAction ：通过容器的  IP 地址和端口号执行  TCP 检 查，如果能够建立  TCP 连接，**
则表明容器健康。
**3、HTTPGetAction ：通过容器的 IP地址、端口号及路径调用  HTTP Get 方法，如果响应的状态码**
大于等于 200且小于400，则认为容器 健康

探针探测结果有以下值：
**1、Success：表示通过检测。**
**2、Failure：表示未通过检测。**
**3、Unknown：表示检测没有正常进行。**

Pod探针相关的属性：
探针(Probe)有许多可选字段，可以用来更加精确的控制 Liveness 和Readiness 两种探针的行为
    initialDelaySeconds ： Pod启动后首次进行检查的等待时间，单位“秒” 。
    periodSeconds ： 检查的间隔时间，默认为 10s，单位“秒” 。
    timeoutSeconds ： 探针执行检测请求后，等待响应的超时时间，默认为 1s，单位“秒” 。
successThreshold ：连续探测几次成功，才认为探测成功 ，默认为  1，在 Liveness 探针中
必须为1，最小值为 1。

failureThreshold ： 探测失败的重试次数，重试一定次数后将认为失败，在  readiness 探
针中，Pod会被标记为未就绪，默认为  3，最小值为  1

 两种探针区别：
ReadinessProbe 和 livenessProbe 可以使用相同探测方式，只是对  Pod 的处置方式不同：
readinessProbe 当检测失败后，将  Pod 的 IP:Port 从对应的  EndPoint 列表中删除。
livenessProbe 当检测失败后，将杀死容器并根据  Pod 的重启策略来决定作出对应的措施。

Pod探针使用示例：

**1、LivenessProbe 探针使用示例**
（1） 、通过exec方式做健康探测
示例文件  liveness -exec.yaml

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: liveness -exec
  labels:
    app: liveness
spec:
  containers:
  - name: liveness
    image: busybox
    args:                       #创建测试探针探测的文件
    - /bin/sh
    - -c
    - touch /tmp/healthy; sleep 30; rm -rf /tmp/healthy; sleep 600
    livenessProbe:
      initialDelaySeconds: 10   # 延迟检测时间
      periodSeconds: 5          # 检测时间间隔
      exec:
        command:
        - cat
        - /tmp/healthy

```
容器启动设置执行的命令：
    /bin/sh -c "touch /tmp/healthy; sleep 30; rm -rf /tmp/healthy; sleep 600"
容器在初始化后，首先创建一个  /tmp/healthy 文件，然后执行睡眠命令，睡眠  30 秒，到
时间后执行删除  /tmp/healthy 文件命令。而设置的存活探针检检测方式为执行  shell 命令，用
cat 命令输出  healthy 文件的内容，如果能成功执行这条命令，存活探针就认为探测成功，否则
探测失败。在前  30 秒内，由于文件存在，所以存活探针探测时执行  cat /tmp/healthy 命令成
功执行。 30 秒后 healthy 文件被删除，所以执行命令失败， Kubernetes 会根据 Pod 设置的重
启策略来判断，是否重启  Pod。

（2） 、通过HTTP方式做健康探测
示例文件  liveness -http.yaml

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: liveness -http
  labels:
    test: liveness
spec:

   containers:
  - name: liveness
    image: mydlqclub/springboot -helloworld:0.0.1
    livenessProbe:
      initialDelaySeconds: 20   # 延迟加载时间
      periodSeconds: 5          # 重试时间间隔
      timeoutSeconds: 10        # 超时时间设置
      httpGet:
        scheme: HTTP
        port: 8081
        path: /actuator/health

```
上面 Pod 中启动的容器是一个  SpringBoot 应用，其中引用了  Actuator 组件，提供了
/actuator/health 健康检查地址，存活探针可以使用  HTTPGet 方式向服务发起请求，请求  8081
端口的 /actuator/health 路径来进行存活判断：

任何大于或等于 200且小于400的代码表示探测成功。
任何其他代码表示失败。

如果探测失败，则会杀死  Pod 进行重启操作。

httpGet 探测方式有如下可选的控制字段 :
scheme: 用于连接 host的协议，默认为 HTTP。
host：要连接的主机名，默认为 Pod IP，可以在 http request head 中设置host头部。
port：容器上要访问端口号或名称。
path：http服务器上的访问 URI。
httpHeaders ：自定义 HTTP请求headers，HTTP允许重复 headers。

（3） 、通过TCP方式做健康探测
示例文件  liveness -tcp.yaml

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: liveness -tcp
  labels:
    app: liveness
spec:
  containers:
  - name: liveness
    image: nginx
    livenessProbe:
      initialDelaySeconds: 15
      periodSeconds: 20

       tcpSocket:
        port: 80
```
TCP 检查方式和  HTTP 检查方式非常相似，在容器启动  initialDelaySeconds 参数设定的时间
后，kubelet 将发送第一个  livenessProbe 探针，尝试连接容器的  80 端口，如果连接失败则将
杀死 Pod 重启容器。

**2、ReadinessProbe 探针使用示例**

Pod 的ReadinessProbe 探针使用方式和  LivenessProbe 探针探测方法一样，也是支持三种，只
是一个是用于探测应用的存活，一个是判断是否对外提供流量的条件。这里用一个  Springboot
项目，设置  ReadinessProbe 探测 SpringBoot 项目的 8081 端口下的  /actuator/health 接
口，如果探测成功则代表内部程序以及启动，就开放对外提供接口 访问，否则内部应用没有成功
启动，暂不对外提供访问，直到就绪探针探测成功。
示例文件  readiness -exec.yaml

```yaml
apiVersion: v1
kind: Service
metadata:
  name: springboot
  labels:
    app: springboot
spec:
  type: NodePort
  ports:
  - name: server
    port: 8080
    targetPort: 8080
    nodePort: 31180
  - name: management
    port: 8081
    targetPort: 8081
    nodePort: 31181
  selector:
    app: springboot
---
apiVersion: v1
kind: Pod
metadata:
  name: springboot
  labels:
    app: springboot
spec:
  containers:
  - name: springboo t

     image: mydlqclub/springboot -helloworld:0.0.1
    ports:
    - name: server
      containerPort: 8080
    - name: management
      containerPort: 8081
    readinessProbe:
      initialDelaySeconds: 20
      periodSeconds: 5
      timeoutSeconds: 10
      httpGet:
        scheme: HTTP
        port: 8081
        path: /actuator/health

```
**3、ReadinessProbe + LivenessProbe 配合使用示例**
一般程序中需要设置两种探针结合使用，并且也要结合实际情况，来配置初始化检查时间和检测
间隔，下面列一个简单的  SpringBoot 项目的 Deployment 例子。

```yaml
apiVersion: v1
kind: Service
metadata:
  name: springboot
  labels:
    app: springboot
spec:
  type: NodePort
  ports:
  - name: server
    port: 8080
    targetPort: 8080
    nodePort: 31180
  - name: management
    port: 8081
    targetPort: 8081
    nodePort: 31181
  selector:
    app: springboot
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: springboot

   labels:
    app: springboot
spec:
  replicas: 1
  selector:
    matchLabels:
      app: springboot
  template:
    metadata:
      name: springboot
      labels:
        app: springboot
    spec:
      containers:
      - name: readiness
        image: mydlqclub/springboot -helloworld:0.0.1
        ports:
        - name: server
          containerPort: 8080
        - name: management
          containerPort: 8081
        readinessProbe:
          initialDelaySeconds: 20
          periodSeconds: 5
          timeoutSeconds: 10
          httpGet:
            scheme: HTTP
            port: 8081
            path: /actuator/health
         livenessProbe:
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
            httpGet:
              scheme: HTTP
              port: 8081
              path: /actuator/health
```


