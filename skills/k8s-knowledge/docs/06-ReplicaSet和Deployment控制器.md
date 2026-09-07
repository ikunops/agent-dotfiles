k8s控制器： Replicaset 和Deployment

前面我们学习了 Pod，那我们在定义 pod资源时，可以直接创建一个 kind：Pod类型的自主式 pod，
但是这存在一个问题，假如 pod被删除了，那这个 pod就不能自我恢复，就会彻底被删除，线上这种情
况非常危险，所以今天就给大家讲解下 pod的控制器，所谓控制器就是能够管理 pod，监测pod运行状
况，当pod发生故障，可以自动恢复 pod。也就是说能够 代我们去管理 pod中间层，并帮助我们确保每一
个pod资源始终处于我们所定义或者我们所期望的目标状态，一旦 pod资源出现故障，那么控制器会尝

 试重启pod或者里面的容器，如果一直重启有问题的话那么它可能会基于某种策略来进行重新布派或者
重新编排；如果 pod副本数量低于用户所定义的目标数量，它也会自动补全；如果多余，也会自动终止
pod资源。

**1、Replicaset 控制器：概念、原理解读**
**1.1 Replicaset 概述**
ReplicaSet 是kubernetes 中的一种副本控制器 ，简称rs，主要作用是控制由其管理的 pod，使pod
副本的数量始终维持在预设的个数。它的主要作用就是保证一定数量的 Pod能够在集群中正常运行，它
会持续监听这些 Pod的运行状态，在 Pod发生故障 时重启pod，pod数量减少时重新运行新的  Pod副本。
官方推荐不要直接使用 ReplicaSet，用Deployments 取而代之， Deployments 是比ReplicaSet 更高级的
概念，它会管理 ReplicaSet 并提供很多其它有用的特性，最重要的是 Deployments 支持声明式更新，声
明式更新的好处是不会丢失历史变更。 所以Deployment 控制器不直接管理 Pod对象，而是由
Deployment 管理ReplicaSet ，再由ReplicaSet 负责管理 Pod对象。

**1.2 Replicaset 工作原理：如何管理 Pod？**
Replicaset 核心作用在于代用户创建指定数量的 pod副本，并确保 pod副本一直处于满足用户期望
的数量，  起到多退少补的作用，并且还具有自动扩容缩容等机制 。
  Replicaset 控制器主要由三个部分组成：
**1、用户期望的 pod副本数：用来定义由这个控制器管控的 pod副本有几个**
**2、标签选择器：选定哪些 pod是自己管理的，如果通过标签选择器选到的 pod副本数量少于我们**
指定的数量，需要用到下面的组件
**3、pod资源模板：如果集群中现存的 pod数量不够我们定义的副本中期望的数量怎么办，需要新**
建pod，这就需要 pod模板，新建的 pod是基于模板来创建的。

**2、 Replicaset 资源清单文件编写技巧**

```bash
#查看定义 Replicaset 资源需要的字段有哪些？
[root@xianchaomaster1  ~]# kubectl explain rs
```

```yaml
KIND:     ReplicaSet
VERSION:  apps/v1
DESCRIPTION:
     ReplicaSet ensures that a specified number of pod replicas are running at
     any given time.
FIELDS:
   apiVersion  <string>  # 当前资源使用的 api版本，跟 VERSION:  apps/v1 保持一致
   kind <string>     # 资源类型，跟 KIND: ReplicaSet 保持一致
   metadata  <Object> # 元数据，定义 Replicaset 名字的
   spec <Object>     ## 定义副本数、定义标签选择器、定义 Pod模板
   status <Object> # 状态信息，不能改
#查看replicaset 的spec字段如何定义？
```

```bash
[root@xianchaomaster1  ~]# kubectl explain rs.spec
```

```yaml
KIND:     ReplicaSet

 VERSION:  apps/v1
RESOURCE: spec <Object>
DESCRIPTION:
     Spec defines the specification of the desired behavior of the ReplicaSet.
     More info:
     https://git.k8s.io/community/contributors/devel/sig -architecture/api -
conventions.md#spec -and-status
     ReplicaSetSpec is the specification of a ReplicaSet .
FIELDS:
   minReadySeconds  <integer>
   replicas  <integer>  # 定义的pod副本数，根据我们指定的值创建对应数量的 pod
   selector  <Object> -required -  #用于匹配 pod的标签选择器
   template  <Object>      # 定义Pod的模板，基于这个模板定义的所有 pod是一样的

#查看replicaset 的spec.template 字段如何定义？
#对于template 而言，其内部定义的就是 pod，pod模板是一个独立的对象
```

```bash
[root@xianchaomaster1  ~]# kubectl explain rs.spec.template
```

```yaml
KIND:     ReplicaSet
VERSION:  apps/v1
RESOURCE: template <Object>
DESCRIPTION:
     Template is the object that describes the pod that will be created if
     insufficient replicas are detected 。PodTemplateSpec describes the data a pod
should have when created from a
     template
FIELDS:
   metadata  <Object>
   spec <Object>

```

```bash
[root@xianchaomaster1  ~]# kubectl explain rs.spec.template.spec
```

通过上面可以看到， ReplicaSet 资源中有两个 spec字段。第一个 spec声明的是 ReplicaSet 定义多
少个Pod副本（默认将仅部署 1个Pod） 、匹配 Pod标签的选择器 、创建pod的模板。第二个 spec是
spec.template.spec ：主要用于Pod里的容器属性等配置。
.spec.template 里的内容是声明 Pod对象时要定义的各种属性，所以这部分也叫做 PodTemplate
（Pod模板） 。还有一个值 得注意的地方是：在 .spec.selector 中定义的标签选择器必须能够匹配到
spec.template.metadata.labels 里定义的 Pod标签，否则 Kubernetes 将不允许创建 ReplicaSet 。

**3、Replicaset 使用案例：部署 Guestbook 留言板**

```bash
#把frontend.tar.gz 上传到xianchaonode2 和xianchaonode1 上，解压
[root@xianchaonode2 ]# docker load -i frontend.tar.gz
[root@xianchaonode1 ]# docker load -i frontend.tar.gz
#编写一个 ReplicaSet 资源清单

 [root@xianchaomaster1  ~]# cat replicaset.yaml
```

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: frontend
  labels:
    app: guestbook
    tier: frontend
spec:
  replicas: 3
  selector:
    matchLabels:
      tier: frontend
  template:
    metadata:
      labels:
        tier: frontend
    spec:
      containers:
      - name: php -redis
        image: yecc/gcr.io -google_samples -gb-frontend:v3
        imagePullPolicy:  IfNotPre sent
```

```bash
[root@xianchaomaster1  ~]# kubectl apply -f replicaset.yaml
replicaset.apps/frontend created
[root@xianchaomaster1  ~]# kubectl get rs
NAME       DESIRED   CURRENT   READY   AGE
frontend      3          3            3        53m
[root@xianchaomaster1  ~]# kubectl get pods
NAME             READY   STATUS    RESTARTS   AGE
frontend -82p9b   1/1      Running   0            36m
frontend -j6twz    1/1       Running   0            36m
frontend -lcnq6    1/1       Running   0            36m
#pod的名字是由控制器的名字 -随机数组成的

#资源清单详细说明
```

```yaml
apiVersion: apps/v1  #ReplicaSet 这个控制器属于的核心群组
kind: ReplicaSet  # 创建的资源类型
metadata:
  name: frontend  # 控制器的名字
  labels:
    app: guestbook
    tier: frontend
spec:

   replicas: 3   # 管理的pod副本数量
  selector:
    matchLabels:
      tier: frontend  # 管理带有 tier=frontend 标签的pod
  template:  # 定义pod的模板
    metadata:
      labels:
        tier: frontend
#pod标签，一定要有，这样上面控制器就能找到它要管理的 pod是哪些了
    spec:
      containers: # 定义pod里运行的容器
      - name: php -redis #定义容器的名字
        image: yecc/gcr.io -google_samples -gb-frontend:v3
          ports:    # 定义端口
- name: http  # 定义容器的名字
containerPort:  80 # 定义容器暴露的端口

```
**4、Replicaset 管理pod：扩容、缩容、更新**
#Replicaset 实现pod的动态扩容
ReplicaSet 最核心的功能是可以动态扩容和回缩，如果我们觉得两个副本太少了，想要增加，只需
要修改配置文件 replicaset.yaml 里的replicas 的值即可 ，原来replicas: 3，现在变成 replicaset:
4，修改之后，执行如下命令更新：

```bash
[root@xianchaomaster1  ~]# kubectl apply -f replicaset.yaml
replicaset.apps/frontend configured
[root@xianchaomaster1  ~]# kubectl get rs
NAME       DESIRED   CURRENT   READY   AGE
frontend       4            4         4        62m
[root@xianchaomaster1  ~]# kubectl get pods
NAME             READY   STATUS    RESTARTS   AGE
frontend -82p9b    1/1     Running   0          62m
frontend-j6twz     1/1     Running   0          62m
frontend -kzjm7    1/1     Running   0          33s
frontend -lcnq6    1/1     Running   0          62m
      #也可以直接编辑控制器实现扩容
kubectl edit rs frontend  #这个是我们 把请求提交给了 apiserver ，实时修改
[root@xianchaomaster1  ~]# kubectl edit rs frontend
```

把上面的 spec下的replicas 后面的值改成 5，保存退出

```bash
[root@xianchaomaster1  ~]# kubectl get rs
NAME       DESIRED   CURRENT   READY   AGE
frontend   5         5         5       67m
[root@xianchaomaster1  ~]# kubectl get pods
NAME             READY   STATUS    RESTARTS   AGE
frontend -82p9b    1/1     Running   0          67m
frontend -j6twz     1/1     Running   0          67m
frontend -kzjm7    1/1     Running   0          5m6s
frontend -lcnq6    1/1     Run ning   0          67m
frontend -lkl26    1/1     Running   0          13s
#Replicaset 实现pod的动态缩容
```
如果我们觉得 5个Pod副本太多了，想要减少，只需要修改配置文件 replicaset.yaml 里的
replicas 的值即可 ，把replicaset ：4变成replicas : 2，修改之后，执行如下命令更新：

```bash
[root@xianchaomaster1  ~]# kubectl apply -f replicaset.yaml
replicaset.apps/frontend configured
[root@xianchaomaster1  ~]# kubectl get rs
NAME       DESIRED   CURRENT   READY   AGE
frontend   2         2         2       70m
[root@xianchaomaster1  ~]# kubectl get pods
NAME             READY   STATUS    RESTARTS   AGE
frontend -j6twz   1/1     Running   0          70m
frontend -lcnq6   1/1     Running   0          70m

#Replicaset 实现pod的更新
#把myapp-v2.tar.gz 上传到xianchaonode1 和xianchaonode2 上，手动解压
[root@xianchaonode1  ~]# docker load -i myapp-v2.tar.gz
[root@xianchaonode2  ~]# docker load -i myapp-v2.tar.gz

[root@xianchaomaster1  ~]# kubectl edit rs frontend

 #修改镜像 image: yecc/gcr.io -google_samples -gb-frontend:v3 变成- image:
```
ikubernetes/myapp:v2 ，修改之后保存退出

```bash
[root@xianchaomaster1  ~]# kubectl get rs -o wide
NAME       DESIRED   CURRENT   READY        IMAGES
frontend    2         2         2             ikubernetes/myapp:v2
#上面可以看到镜像变成了 ikubernetes/myapp:v2 ，说明滚动升级成功了

[root@xianchaomaster1  ~]# kubectl get pods -o wide
NAME             READY   STATUS    RESTARTS   AGE   IP               NODE
NOMINATED NODE   READINESS GATES
frontend -glb2c   1/1     Running   0          34s   10.244.209.133   xianchaonode1
frontend -lck9t   1/1     Runni ng   0          34s   10.244.187.74    xianchaonode2
[root@xianchaomaster1  ~]# curl 10.244.209.133
div style="width: 50%; margin -left: 20px">
 <h2>Guestbook </h2>
[root@xianchaomaster1  ~]# curl 10.244.209.74
div style="width: 50%; margin-left: 20px">
 <h2>Guestbook </h2>
 #上面可以看到虽然镜像已经更新了，但是原来的 pod使用的还是之前的镜像，新创建的 pod才会
```
使用最新的镜像

```bash
#10.244.209.133 这个ip对应的pod删除
[root@xianchaomaster1  ~]# kubectl delete pods frontend -glb2c
pod "frontend -glb2c" deleted
[root@xianchaomaster1  ~]# kubectl get pods -o wide
NAME             READY   STATUS    RESTARTS   AGE     IP              NODE
frontend -hkhdw   1/1     Running   0          15s     10.244.187.75   xianchaonode2
frontend -lck9t   1/1     Running   0          2m37s   10.244.187.74   xianchaon ode2
#重新生成了一个新的 pod：frontend -hkhdw
[root@xianchaomaster1  ~]# curl 10.244.187.75
Hello MyApp | Version: v2 | <a href="hostname.html">Pod Name</a>
#新生成的 pod的镜像已经变成了 myapp的，说明更新完成了

#如果我们直接修改 replicaset .yaml文件，把 image: yecc/gcr.io -google_samples -gb-
```
frontend:v3 变成- image: ikubernetes/myapp:v2
kubectl apply -f replicaset. yaml
#发现原来的 pod还是用的 frontend :v3这个镜像，没有实现自动更新

生产环境如果升级，可以删除一个 pod，观察一段时间之后没问题再删除另一个 pod，但是这样需要
人工干预多次；实际生产环境一般采用蓝绿发布，原来有一个 rs1，再创建一个 rs2（控制器） ，通过修
改service 标签，修改 service 可以匹配到 rs2的控制器，这样才是蓝绿发布，这个也需要我们精心的
部署规划，我们 有一个控制器就是建立在 rs之上完成的，叫做 Deployment

**5、Deployment 控制器：概念、原理解读**

Deployment 官方文档：
https://kubernetes.io/docs/concepts/workloads/controllers/deployment/

**5.1 Deployment 概述**
Deployment 是kubernetes 中最常用的资源对象， 为ReplicaSet 和Pod的创建提供了一种声明式的
定义方法，在 Deployment 对象中描述一个期望的状态， Deployment 控制器就会按照一定的控制速率把实
际状态改成期望状态，通过定义一个 Deployment 控制器会创建一个新的 ReplicaSet 控制器，通过
ReplicaSet 创建pod，删除Deployment 控制器，也会删除 Deployment 控制器下对应的 ReplicaSet 控制
器和pod资源.

    使用Deployment 而不直接创建 ReplicaSet 是因为Deployment 对象拥有许多 ReplicaSet 没有
的特性，例如滚动升级和回滚 。

扩展：声明式定义 是指直接修改资源清单 yaml文件，然后通过 kubectl apply -f 资源清单 yaml文
件，就可以更改资源

Deployment 控制器是建立在 rs之上的一个控制器，可以管理多个 rs，每次更新镜像版本，都会生
成一个新的 rs，把旧的 rs替换掉，多个 rs同时存在，但是只有一个 rs运行。

rs v1控制三个 pod，删除一个 pod，在rs v2上重新建立一个，依次类推， 直到全部都是由 rs v2
控制，如果rs v2有问题，还可以回滚 ，Deployment 是建构在 rs之上的，多个 rs组成一个
Deployment ，但是只有一个 rs处于活跃状态 .

**5.2 Deployment 工作原理：如何管理 rs和Pod？**
Deployment 可以使用声明式定义 ，直接在命令行通过纯命令的方式完成对应资源版本的内容的修
改，也就是通过打补丁的方式进行修改； Deployment 能提供滚动式自定义自控制的更新；对 Deployment
来讲，我们在实现更新时还可以实现控制更新节奏和更新逻辑 。

互动：什么叫做更新节奏和更新逻辑呢？

比如说Deployment 控制5个pod副本，pod的期望值是 5个，但是升级的时候需要额外多几个
pod，那我们控制器可以控制在 5个pod副本之外还能再增加几个 pod副本；比方说能多一个，但是不能

 少，那么升级的时候就是先增加一个，再删除一个，增加一个删除一个，始终保持 pod副本数是 5个；
还有一种情况，最多允许多一个，最少允许少一个，也就是最多 6个，最少 4个，第一次加一个，删除
两个，第二次加两个，删除两个，依次类推，可以自己控制更新方式，这 种滚动更新需要加
readinessProbe 和livenessProbe 探测，确保pod中容器里的 应用都正常启动了才删除之前的 pod。
启动第一步，刚更新第一批就暂停了也可以；假如目标是 5个，允许一个也不能少，允许最多可以
10个，那一次加 5个即可；这就是我们可以自己控制节奏来控制更新的方法 。

通过Deployment 对象，你可以轻松的做到以下事情：
**1、创建ReplicaSet 和Pod**
**2、滚动升级（不停止旧服务的状态下升级）和回滚应用（将应用回滚到之前的版本）**
**3、平滑地扩容和缩容**
**4、暂停和继续 Deployment**

**6、Deployment 资源清单文件编写技巧**

```bash
#查看Deployment 资源对象 由哪几部分组成
[root@xianchaomaster1  ~]# kubectl explain deployment
```

```yaml
KIND:     Deployment
VERSION:  apps/v1
DESCRIPTION:
     Deployment enables declarative updates for Pods and ReplicaSets.
FIELDS:
   apiVersion  <string>  # 该资源使用的 api版本
   kind <string>            #创建的资源是什么？
   metadata  <Object>       # 元数据，包括资源的名字和名称空间
   spec <Object>           # 定义容器的
   status <Object>       # 状态，不可以修改
#查看Deployment 下的spec字段
```

```bash
[root@xianchaomaster1  ~]# kubectl explain deployment.spec
```

```yaml
KIND:     Deployment
VERSION:  apps/v1
RESOURCE: spec <Object>
DESCRIPTION:
     Specification of the desired behavior of the Deployment.
     DeploymentSpec is the specification of the desired behavior of the
     Deployment.
FIELDS:
    minReadySeconds  <integer>
#Kubernetes 在等待设置的时间后才进行升级
#如果没有设置该值， Kubernetes 会假设该容器启动起来后就提供服务了
paused <boolean>  #暂停，当我们更新的时候创建 pod先暂停，不是立即更新
    progressDeadlineSeconds  <integer>
# k8s 在升级过程中有可能由于各种原因升级卡住（这个时候还没有明确的升级失败） ，比如
```
在拉取被墙的镜像，权限不够等错误。那么这个时候就需要有个  deadline ，在 deadline

 之内如果还卡着，那么就上报这个情况，这个时候这个  Deployment 状态就被标 记为
False，并且注明原因。但是它并不会阻止  Deployment 继续进行卡住后面的操作。完全由用
户进行控制。
    replicas  <integer>  #副本数
    revisionHistoryLimit  <integer> # 保留的历史版本，默认是 10
    selector  <Object> -required - #标签选择器，选择它关联的 pod
    strategy  <Object>     #更新策略
    template  <Object> -required  #定义的pod模板

```bash
#查看Deployment 下的spec.strategy字段
[root@xianchaomaster1  ~]# kubectl explain deploy.spec.strategy
```

```yaml
KIND:     Deployment
VERSION:  apps/v1
RESOURCE: strategy <Object>
DESCRIPTION:
     The deployment strategy to use to replace existing pods with new ones.
     DeploymentStrategy describes how to replace existing pods with new ones.
FIELDS:
   rollingUpdate  <Object>
   type <string>
     Type of deployment. Can be "Recreate" or "RollingUpdate". Default is
     RollingUpdate.
#支持两种更新， Recreate 和RollingUpdate
#Recreate 是重建式更新，删除一个更新一个

#RollingUpdate 滚动更新，定义滚动更新方式，也就是 pod能多几个，少几个
#查看Deployment 下的spec.strategy.rollingUpdate 字段
```

```bash
[root@xianchaomas ter1 ~]# kubectl explain deploy.spec.strategy.rollingUpdate
```

```yaml
KIND:     Deployment
VERSION:  apps/v1
RESOURCE: rollingUpdate <Object>
DESCRIPTION:
     Rolling update config params. Present only if DeploymentStrategyType =
     RollingUpdate.
     Spec to co ntrol the desired behavior of rolling update.
FIELDS:
   maxSurge  <string>
#我们更新的过程当中最多允许超出的指定的目标副本数有几个；
```
它有两种取值方式，第一种直接给定数量 ，第二种根据百分比，百分比表示原本是 5个，最
多可以超出 20%，那就允许多一个 ，最多可以超过 40%，那就允许多两个
   maxUnavailable  <string>
#最多允许几个不可用
假设有5个副本，最多一个不可用，就表示最少有 4个可用

```bash
 #查看Deployment 下的spec.template 字段
#template 为定义Pod的模板， Deployment 通过模板创建 Pod
[root@xianchaomaster1  ~]# kubectl explain deploy.spec.template
```

```yaml
KIND:     Deployment
VERSION:  apps/v1
RESOURCE: template <Object>
DESCRIPTION:
     Template describes the pods that will be created.
     PodTemplateSpec describes the data a pod should have when created from a
template
FIELDS:
   metadata  <Object>  # 定义模板的名字
   spec <Object>
```
deployment.spec.template 为Pod定义的模板，和 Pod定义不太一样， template 中不包含
apiVersion 和Kind属性，要求必须有 metadata 。deployment.spec.template.spec 为容器的
属性信息，其他定义内容和 Pod一致。

```bash
#查看Deployment 下的spec.template.spec 字段
[root@xianchaomaster1  ~]# kubectl explain deploy.spec.template.spec
```

```yaml
KIND:     Deployment
VERSION:  apps/v1
RESOURCE: spec <Object>
DESCRIPTION:
     Specification of the desired behavior of the pod. More info:
     https://git.k8s.io/community/contributors/devel/sig -architecture/api -
conventions.md#spec -and-status
     PodSpec is a description of a pod.
FIELDS:
   activeDeadlineSeconds  <integer>
#activeDeadlineSeconds 表示Pod 可以运行的最长时间，达到设置的该值后， Pod 会自动停
```
止。
   affinity <Object>  #定义亲和性，跟直接创建 pod时候定义亲和性类似
   automountServiceAccountToken  <boolean> # 身份认证相关的
   containers  <[]Object> -required - #定义容器属性
   dnsConfig  <Object>  # 设置Pod的DNS
dnsConfig:
    nameservers:
      - 192.xxx.xxx.6
    searches:
      - xianchao .svc.clust er.local
      - my.dns.search. xianchao
   dnsPolicy  <string> #  dnsPolicy 决定Pod 内预设的DNS 配置策略

 None 无任何策略 ：使用自定义的策略
Default 默认：使用宿主机的 dns配置，/etc/resolv.conf
ClusterFirst 集群DNS优先，与 Default 相反，会预先使用  kube-dns (或 CoreDNS ) 的
信息当预设置参数写入到该  Pod 内的DNS配置。
ClusterFirstWithHostNet 集群 DNS 优先，并伴随着使用宿主机网络 ：同时使用
hostNetwork 与 kube-dns 作为 Pod 预设 DNS 配置。

   enableServiceLinks  <boolean>
   ephemeralContainers  <[]Object> # 定义临时容器
临时容器与其他容器的不同之处在于，它们缺少对资源或执行的保证，并且永远不会
自动重启，因此不适用于构建应用程序。临时容器使用与常规容器相同的  ContainerSpec 段
进行描述 ，但许多字段是不相容且不允许的。
    临时容器没有端口配置，因此像  ports，livenessProbe ，readinessProbe 这样的字段
是不允许的。
    Pod 资源分配是不可变的，因此  resources 配置是不允许的。

临时容器用途：
当由于容器崩溃或容器镜像不包含调试 应用程序而导致  kubectl exec  无用时，临时
容器对于交互式故障排查很有用。

   hostAliases  <[]Object> # 在pod中增加域名解析的
  hostAliases:
  – ip: "10.1.2.2"
    hostnames:
    – "mc.local"
    – "rabbitmq.local"
  – ip: "10.1.2.3"
    hostnames:
    – "redis.local"
    – "mq.local"
   hostIPC <boolean> # 使用主机 IPC
   hostNetwork  <boolean>  # 是否使用宿主机的网络
   hostPID <boolean> # 可以设置容器里是 否可以看到宿主机上的进程。 True可以
   hostname  <string>
   imagePullSecrets  <[]Object>
   initContainers  <[]Object> #定义初始化容器
   nodeName  <string>  #定义pod调度到具体哪个节点上
   nodeSelector  <map[string]string>  #定义节点选择器
   overhead  <map[string]string> # overhead 是1.16引入的字段， 在没有引入  Overhead
之前，只要一个节点的资源可用量大于等于  Pod 的 requests 时，这个  Pod 就可以被调度
到这个节点上。引入  Overhead 之后，只有节点的资源可用量大于等于  Overhead 加上
requests 的和时才能被调度上来 。
   preemptionPolicy  <string>

    priority  <integer>
   priorityClassName  <string>
   readinessGates  <[]Object>
   restartPolicy  <string>   #Pod重启策略
   runtimeClassName  <string>
   schedulerName  <string>
   securityContext  <Object> #是否开启特权模式
   serviceAccount  <string>
   serviceAccountName  <string>
   setHostnameAsFQDN  <boolean>
   shareProcessNamespace  <boolean>
   subdomain  <string>
   terminationGracePeriodSeconds  <integer>
#在真正删除容器之前， K8S会先发终止信号（ kill -15 {pid} ）给容器，默认 30s
   tolerations  <[]Object>  #定义容忍度
   topologySpreadConstraints  <[]Object
   volumes <[]Object>  # 挂载存储卷

**7、Deployment 使用案例：创建一个 web站点**
deployment 是一个三级结构， deployment 管理replicaset ，replicaset 管理pod，
例子：用 deployment 创建一个 pod
#把myapp-blue-v1.tar.g z和myapp-blue-v2.tar.g z上传到xianchaonode1 和xianchaonode2 上，
手动解压：

```bash
[root@xianchaonode1  ~]# docker load -i myapp-blue-v1.tar.gz
[root@xianchaonode2  ~]# docker loa d -i myapp-blue-v1.tar.gz
[root@xianchaonode1  ~]# docker load -i myapp-blue-v2.tar.gz
[root@xianchaonode2  ~]# docker load -i myapp-blue-v2.tar.gz
[root@xianchaomaster1  ~]# cat deploy -demo.yaml
```

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp -v1
spec:
  replicas: 2
  selector:
   matchLabels:
    app: myapp
    version: v1
  template:
   metadata:
    labels:
     app: myapp
     version: v1

    spec:
    containers:
    - name: myapp
      image: janakiramm/myapp:v1
      imagePul lPolicy: IfNotPresent
      ports:
      - containerPort: 80
```
更新资源清单文件：
kubectl apply -f deploy -demo.yaml
#kubectl  apply：表示声明式的定义，既可以创建 资源，也可以 动态更新资源
查看deploy状态：
kubectl get deploy
显示如下：
NAME       READY   UP -TO-DATE   AVAILABLE   AGE
myapp-v1     2/2      2               2           60s
#创建的控制器名字是 myapp-v1
1.NAME ：列出名称空间中 deployment 的名称。
2.READY：显示deployment 有多少副本数 。它遵循 ready/desired 的模式。
3.UP-TO-DATE： 显示已更新到所需状态的副本数。
4.AVAILABLE ： 显示你的可以使用多少个应用程序副本。
5.AGE ：显示应用程序已运行的时间。

kubectl get rs 显示如下：
创建的控制器名字是 myapp-v1
kubectl get rs
显示如下：
AME                     DESIRED   CURRENT   READY   AGE
myapp-v1-67fd9fc9c8     2         2            2       2m35s
#创建deploy的时候也会创建一个 rs（replicaset ），67fd9fc9c8 这个随机数字是我们引用
pod的模板template 的名字的 hash值
1.NAME： 列出名称空间中 ReplicaSet 资源
2DESIRED：显示应用程序的所需副本数，这些副本数是在创建时定义的。这是所需的状态。
3.CURRENT： 显示当前正在运行多少个副本。
4.READY： 显示你的用户可以使用多少个应用程序副本。
5.AGE ：显示应用程序已运行的时间。

请注意， ReplicaSet 的名称始终设置为 [DEPLOYMENT -NAME]-[RANDOM-STRING]。RANDOM-
STRING是随机生成的
kubectl get pods
显示如下：
myapp-v1-67fd9fc9c8 -fcprr   1/1     Running   0           3s
myapp-v1-67fd9fc9c8 -hw4f9   1/1     Running   0          2m21s

```bash
[root@xianchaomaster1  ~]# kubectl get pods -o wide | grep myapp

 myapp-v1-67fd9fc9c8 -fcprr   1/1   Running  0    10.244.187.78   xianchaonode2
myapp-v1-67fd9fc9c8 -hw4f9  1/1   Running   0   10.244.209.136  xianchaonode1
#请求刚才创建的 pod资源
[root@xianchaomaster1  ~]# curl 10.244.187.78
      background -color: blue;
[root@xianchaomaster1  ~]# curl 10.244.209.136
      background -color: blue;
#资源清单文件详细解读
```

```yaml
apiVersion: apps/v1  # deployment 对应的api版本
kind: Deployment    # 创建的资源是 deployment
metadata:
  name: myapp -v1   #deployment 的名字
spec:
  replicas: 2     # deployment 管理的pod副本数
  selector:       # 标签选择器
   matchLabels:  # matchLabels 下定义的标签需要跟 template .metadata .labels定义的标
```
签一致
    app: myapp
    version: v1
  template:

```yaml
   metadata:
    labels:
     app: myapp
     version: v1
   spec:   # 定义容器的属性
    containers:
    - name: myapp
      image: janakiramm/myapp:v1 # 容器使用的镜像
      imagePullPolicy: IfNotPresent  # 镜像拉取策略
      ports:
      - containerPort: 80     # 容器里的应用的端口

```
**8、Deployment 管理pod：扩容、缩容、滚动更新、回滚**

```bash
#通过deployment 管理应用，实现扩容，把副本数变成 3
[root@xianchaomaster1  ~]# cat  d eploy-demo.yaml
```
直接修改 replicas 数量，如下，变成 3

```yaml
spec:
  replicas: 3
```
修改之后保存退出，执行

```bash
[root@xianchaomaster1  ~]# kubectl apply -f deploy -demo.yaml
```
> **注意：apply不同于create，apply可以执行多次； create执行一次，再执行就会报错复 。**
kubectl get pods
显示如下：

 NAME                         READY   STATUS    RESTARTS   AGE
myapp-v1-67fd9fc9c8 -fcprr   1/1     Running   0          15m
myapp-v1-67fd9fc9c8 -h9js5   1/1     Running   0          11s
myapp-v1-67fd9fc9c8 -hw4f9   1/1     Running   0          17m

```bash
#上面可以看到 pod副本数变成了 3个
#查看myapp-v1这个控制器的详细信息
[root@xianchaoma ster1 ~]# kubectl describe deploy myapp -v1
Name:                   myapp -v1
Namespace:              default
CreationTimestamp:      Tue, 30 Mar 2021 12:59:02 +0800
Labels:                 <none>
Annotations:            deployment.kubernetes.io/revision: 1
Selector:               app=myapp,version=v1
Replicas:               3 desired | 3 updated | 3 total | 3 available | 0
unavailable
StrategyType:           RollingUpdate
MinReadySeconds:        0
RollingUpdateStrategy:  25% max unavailable, 25% max surge
Pod Template:
  Labels:  app=myapp
           version=v1
  Containers:
   myapp:
    Image:        janakiramm/myapp:v1
    Port:         80/TCP
    Host Port:    0/TCP
    Environment:  <none>
    Mounts:       <none>
  Volumes:        <none>
Conditions:
  Type           Status  Reason
  ----           ------  ------
  Progressing    True    NewReplicaSetAvailable
  Available      True    MinimumReplicasAvailable
OldReplicaSets:  <none>
NewReplicaSet:   myapp -v1-67fd9fc9c8  (3/3 replicas created)
Events:
  Type    Reason             Age   From                   Message
  ----    ------             ----  ----                   -------
  Normal  ScalingReplicaSet  18m   deployment -controller  Scaled up replica set
myapp-v1-67fd9fc9c8 to 2
  Normal  ScalingReplicaSet  51s   deployment -controller  Scaled up replica set
myapp-v1-67fd9fc9c8 to 3

#通过deployment 管理应用，实现缩容，把副本数变成 2
[root@xianchao master1 ~]# cat  deploy -demo.yaml
```
直接修改 replicas 数量，如下，变成 2

```yaml
spec:
  replicas: 2
```
修改之后保存退出，执行

```bash
[root@xianchaomaster1  ~]# kubectl apply -f deploy -demo.yaml
[root@xianchaomaster1  ~]# kubectl get pods
NAME                         READY   STATUS    RESTARTS   AGE
myapp-v1-67fd9fc9c8 -fcprr    1/1     Running   0          18m
myapp-v1-67fd9fc9c8 -hw4f9   1/1     Running   0          20m

#通过deployment 管理应用，实现滚动更新
```
在一个终端窗口执行如下：

```bash
[root@xianchaomaster1  ~]# kubectl get pods -l app=myapp -w
NAME                        READY   STATUS    RESTARTS   AGE
myapp-v1-67fd9fc9c8 -fcprr   1/1     Running   0          19m
myapp-v1-67fd9fc9c8 -hw4f9   1/1     Running   0          22m
```

打开一个 新的终端 窗口更改镜像版本， 按如下操作：

```bash
[root@xianchaomaster1  ~]# vim deploy -demo.yaml
```
把image: janakiramm/myapp:v1 变成image: janakiramm/myapp:v2
保存退出，执行

```bash
[root@xianchaomaster1  ~]# kubectl apply -f deploy -demo.yaml
```
再回到刚才执行 监测kubectl get pods -l app=myapp -w的那个窗口 ，可以看到信息如下：
NAME                        READY   STATUS    RESTARTS   AGE
myapp-v1-67fd9fc9c8-fcprr   1/1     Running   0          23m
myapp-v1-67fd9fc9c8 -hw4f9   1/1     Running   0          26m
myapp-v1-75fb478d6c -fskpq   0/1     Pending   0          0s
myapp-v1-75fb478d6c -fskpq   0/1     Pending   0          0s
myapp-v1-75fb478d6c -fskpq   0/1     ContainerCreating   0          0s
myapp-v1-75fb478d6c -fskpq   0/1     ContainerCreating   0          1s
myapp-v1-75fb478d6c -fskpq   1/1     Running             0          4s
myapp-v1-67fd9fc9c8 -fcprr   1/1     Terminating         0          24m
myapp-v1-75fb478d6c -x8stq   0/1     Pending             0          0s
myapp-v1-75fb478d6c -x8stq   0/1     Pending             0          0s
myapp-v1-75fb478d6c -x8stq   0/1     ContainerCreating   0          0s
myapp-v1-67fd9fc9c8 -fcprr   1/1     Terminating          0          24m
myapp-v1-75fb478d6c -x8stq   0/1     ContainerCreating   0          1s
myapp-v1-67fd9fc9c8 -fcprr   0/1     Terminating         0          24m
myapp-v1-75fb478d6c -x8stq   1/1     Running             0          1s
myapp-v1-67fd9fc9c8 -hw4f9   1/1     Terminating         0          26m

 myapp-v1-67fd9fc9c8 -hw4f9   1/1     Terminating         0          26m
myapp-v1-67fd9fc9c8 -hw4f9   0/1     Terminating         0          26m
myapp-v1-67fd9fc9c8 -hw4f9   0/1     Terminating         0          26m
myapp-v1-67fd9fc9c8 -hw4f9   0/1     Terminating         0          26m
myapp-v1-67fd9fc9c8 -fcprr   0/1     Terminating         0          24m
myapp-v1-67fd9fc9c8 -fcprr   0/1     Terminating         0          24m

pending 表示正在进行调度， ContainerCreating 表示正在创建一个 pod，running 表示运行
一个pod，running 起来一个 pod之后再Terminating （停掉）一个 pod，以此类推，直到所
有pod完成滚动升级

在另外一个窗口执行

```bash
[root@xianchaomaster1  ~]# kubectl get rs
```
显示如下：
myapp-v1-67fd9fc9c8    0         0         0       27m
myapp-v1-75fb478d6c   2          2         2       79s

```bash
#上面可以看到 rs有两个， 上面那个是升级之前的，已经被停掉，但是可以随时回滚
#查看myapp-v1这个控制器的历史 版本
[root@xianchaomaster1  ~]# kubectl rollout history deployment myapp -v1
deployment.apps/myapp -v1
REVISION  CHANGE -CAUSE
1         <none>
2         <none>
#回滚
[root@xianchaomaster1  ~]# kubectl rollout undo deployment myapp -v1 --to-
revision=1
deployment.apps/myapp -v1 rolled back
[root@xianchaomaster1  ~]# kubectl rollout history deployment myapp -v1
deployment.apps/myapp -v1
REVISION  CHANGE -CAUSE
2         <none>
3         <none>
```

**8.1 自定义滚动更新策略**
maxSurge 和maxUnavailable 用来控制滚动更新的更新策略
取值范围
数值
**1. maxUnavailable: [0, 副本数]**
**2. maxSurge: [0, 副本数]**
> **注意：两者不能同时为 0。**
比例
**1. maxUnavailable: [0%, 100%] 向下取整，比如 10个副本， 5%的话==0.5个，但计算按照 0个；**

**2. maxSurge: [0%, 100%] 向上取整，比如 10个副本， 5%的话==0.5个，但计算按照 1个；**
> **注意：两者不能同时为 0。**
建议配置
**1. maxUnavailable == 0**
**2. maxSurge == 1**
这是我们生产环境提供给用户的默认配置。即 “一上一下，先上后下 ”最平滑原则：
1个新版本 pod ready （结合readiness ）后，才销毁旧版本 pod。此配置适用场景是平滑更新、保
证服务平稳，但也有缺点，就是 “太慢”了。

总结：
maxUnavailable ：和期望的副本数比，不可用副本数最大比例（或最大值） ， 这个值越小，越 能保证
服务稳定，更新越平滑；
maxSurge ：和期望的副本数比，超过期望副本数最大比例（或最大值） ， 这个值调的越大，副本更新
速度越快。

自定义策略：
修改更新策略 ：maxUnavailable=1 ，maxSurge=1

```bash
[root@xianchaomaster1  ~]# kubectl patch deployment myapp -v1 -p
'{"spec":{"strategy":{"rollingUpdate": {"maxSurge":1,"maxUnavailable":1}}}}' -n blue-green
```

查看myapp-v1这个控制器的详细信息

```bash
[root@xianchaomaster1  ~]# kubectl describe deployment myapp -v1 -n blue-green
```

显示如下：
RollingUpdateStrategy:  1 max unavailable, 1 max surge

上面可以看到 RollingUpdateStrategy: 1 max unavailable, 1 max surge
这个rollingUpdate 更新策略变成了刚才设定的，因为我们设定的 pod副本数是 3，1和1表示最少
不能少于 2个pod，最多不能超过 4个pod
这个就是通过控制 RollingUpdateStrategy 这个字段来设置滚动更新策略的

**9、Deployment 资源清单详解**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: portal
  namespace: ms
spec:
  replicas: 1
  selector:
    matchLabels:

       project: ms
      app: portal
  template:
    metadata:
      labels:
        project: ms
        app: portal
    spec:
      containers:
      - name: portal
        image:  xianchao /portal:v1
        imagePullPolicy: Always
        ports:
          - protocol: TCP
            containerPort: 8080
        resources:  # 资源配额
          limits:  # 资源限制，最多可用的 cpu和内存
            cpu: 1
            memory: 1Gi
         requests ： #最少需要多少资源才可以运行 Pod
            cpu: 0.5
            memory: 1Gi
        readinessProbe:
          tcpSocket:
            port: 8080
          initialDelaySeconds: 60
          periodSeconds: 10
        livenessProbe:
          tcpSocket:
            port: 8080
          initialDelaySeconds: 60
          periodSeconds: 10

livenessProbe:
 #存活性探测
#用于判断容器是否存活，即 Pod是否为running 状态，如果 LivenessProbe 探针探测到容器不健康，则
```
kubelet 将kill掉容器，并根据容器的重启策略是否重启。如果一个容器不包含 LivenessProbe 探针，
则Kubelet 认为容器的 LivenessProbe 探针的返回值永远成功。
    tcpSocket:
       port: 8080   #检测8080端口是否存在
    initialDelaySeconds: 60  #Pod启动60s执行第一次检查
periodSeco nds: 10    #第一次检查后每隔 10s检查一次

  readinessProbe:  # 就绪性探测
有时候应用程序可能暂时无法接受请求，比如 Pod已经Running 了，但是容器内应用程序尚未启动成
功，在这种情况下，如果没有 ReadinessProbe ，则Kubernetes 认为它可以处理请求了，然而此时，我们
知道程序还没启动成功是不能接收用户请求的，所以不希望 kubernetes 把请求调度给它，则使用
ReadinessProbe 探针。

ReadinessProbe 和livenessProbe 可以使用相同探测方式，只是对 Pod的处置方式不同，
ReadinessProbe 是将Pod IP:Port 从对应的 EndPoint 列表中删除，而 livenessProbe 则Kill容器并根
据Pod的重启策略来决定作出对应的措施。

ReadinessProbe 探针探测容器是否已准备就绪，如果未准备就绪则 kubernetes 不会将流量转发给此
Pod。

     tcpSocket:
       port: 8080
        initialDelaySeconds: 60
        periodSe conds: 10
#在Pod运行过程中， K8S仍然会每隔 10s检测8080端口


