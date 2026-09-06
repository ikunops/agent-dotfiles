
**1、自动（弹性） 扩缩容背景分析**

背景：
弹性伸缩是根据用户的业务需求和策略，自动 “调整”其“弹性资源 ”的管理服务。通过弹
性伸缩功能，用户可设置定时、周期或监控策略，恰到好处地增加或减少 “弹性资源 ”，并完
成实例配置，保证业务平稳健康运行

在实际工作中，我们常常需要做一些扩容缩容操作， 如：电商 平台在618和双十一 搞秒
杀活动；由于资源紧张、工作负载降低等都需要对服务实例数进行扩缩容操作。

在k8s中扩缩容分为两种：

**1、Node层面：**
对K8s物理节点扩容和缩容 ，根据业务规模实现物理节点自动扩缩容

**2、Pod层面：**
我们一般会使用 Deployment 中的 replicas参数， 设置多个副本集来保证服务的高可用，
但是这是一个固定的值，比如我们设置 10个副本，就会启 10个pod 同时 running来
提供服务。 如果这个服务平时流量很少的时候，也是 10个pod同时在 running，而流
量突然暴增时，又可能出现 10个pod不够用的情况。 针对这种情况怎么办？就需要 扩
容和缩容

**2、k8s中自动伸缩的方案**
2.1、HPA
Kubernetes HPA （Horizontal Pod Autoscaling ）：Pod水平自动伸缩

通过此功能， 只需简单的配置， 便可以利用监控指标 （ cpu使用率、 磁盘、 自定义的 等）
自动的扩容或缩容服务中 Pod数量，当业务需求增加时，系统将无缝地自动增加适量
pod容器，提高系统稳定性。

要想实现自动扩缩容，需要先考虑如下几点：

1.通过哪些指标决定扩缩容？
HPA v1版本可以根据 CPU使用率来进行自动扩缩容：
但是并非所有的系统都可以仅依靠 CPU或者 Memory 指标来扩容，对于大多数  Web
应用的后端来说，基于每秒的请求数量进行弹性伸缩来处理突发流量会更加的靠谱，所
以对于一个自动扩缩容系统来说，我们不能局限于 CPU、Memory 基础监控数据，每秒
请求数 RPS等自定义指标也是十分重要 。

HPA v2版本可以根据自定义的指标进行自动扩缩容

> **注意： hpa v1只能基于 cpu做扩容所用**
      hpa v2可以基于内存和自定义的指标做扩容和缩容

2.如何采集资源指标？
如果我们的系统默认依赖 Prometheus ，自定义的 Metrics指标则可以从各种数据源或
者exporter 中获取，基于拉模型的 Prometheus 会定期从数据源中拉取数据。  也可以
基于 metrics -server自动获取节点和 pod的资源指标

3.如何实现自动扩缩容？
K8s的HPA controller 已经实现了一套简单的自动扩缩容逻辑，默认情况下，每 30s检
测一次指标， 只要检测到了配置 HPA的目标值， 则会计算出预期的工作负载的副本数，
再进行扩缩容操作。同时，为了避免过于频繁的扩缩容，默认在 5min内没有重新扩缩
容的情况下，才会触发扩缩容。  HPA本身的算法相对比较保守，可能并不适用于很多
场景。例如，一个快速的流量突发场景，如果正处在 5min内的 HPA稳定期，这个时候
根据 HPA的策略，会导致无法扩容。

 2.2、KPA
KPA（Knative Pod Autoscaler ）：基于请求 数对 Pod自动扩缩容 ，KPA 的主要限制在于
它不支持基于  CPU 的自动扩缩容。

**1、根据并发请求数实现自动扩缩容**
**2、设置扩缩容边界实现自动扩缩容**

扩缩容边界指应用程序提供服务的最小和最大 Pod数量。通过设置应用程序提供服务
的最小和最 大Pod数量实现自动扩缩容。
相比 HPA，KPA会考虑更多的场景，其中一个比较重要的是流量突发的时候

2.3、VPA
kubernetes  VPA（Vertical Pod Autoscaler ），垂直 Pod 自动扩缩容， VPA会基于 Pod的
资源使用情况自动为集群设置资源占用的限制，从而让集群将 Pod调度到有足够资源
的最佳节点上。 VPA也会保持最初容器定义中资源 request和limit的占比。
它会根据容器资源使用率自动设置 pod的CPU和内存的 requests，从而允许在节点上
进行适当的调度，以便为每个  Pod 提供适当的 可用的节点 。它既可以缩小过度请求资
源的容器，也可以根据其使用情况随时提升资源不足的容量。

**3、利用 HPA基于 CPU指标实现 pod自动扩缩容**
HPA全称是 Horizontal Pod Aut oscaler，翻译成中文是 POD水平自动伸缩，  HPA可以
基于 CPU利用率对 deployment 中的 pod数量进行自动扩缩容（除了 CPU也可以基
于自定义的指标进行自动扩缩容） 。 pod自动缩放不适用于无法缩放的对象，比如
DaemonSets 。
HPA由Kubernetes API 资源和控制器实现 。控制器会周期性的获取平均 CPU利用率，
并与目标值相比较后调整 deployment 中的副本数量。

**3.1 HPA工作原理**

HPA 是根据指标来进行自动伸缩的，目前 HPA 有两个版本 –v1和v2beta

HPA 的API有三个版本，通过 kubectl api -versions | grep autoscal 可看到
autoscaling/v1
autoscaling/v2beta1
autoscaling/v2beta2

autoscaling/v1 只支持基于 CPU 指标的缩放；
autoscaling/v2beta1 支持 Resource Metrics （资源指标，如 pod 内存）和 Custom Metrics
（自定义指标）的缩放；
autoscaling/v2beta2 支持 Resource Metrics （资源指标，如 pod 的内存）和 Custom Metrics
（自定义指标）和 ExternalMetrics （额外指标）的缩放，但是目前也仅仅是处于 beta 阶段
指标从哪里来 ？

K8S 从1.8版本开始， CPU、内存等资源的 metrics 信息可以通过  Metrics API 来获取，用户可
以直接获取这些 metrics 信息（例如通过执行 kubect top 命令）， HPA 使用这些 metics 信息来
实现动态伸缩。

Metrics server ：
**1、Metrics server 是K8S 集群资源使用情况的聚合器**
**2、从 1.8版本开始， Metrics server 可以通过 yaml 文件的方式进行部署**
**3、Metrics server 收集所有 node 节点的 metrics 信息**

HPA 如何运作？

 HPA 的实现是一个控制循环，由 controller manager 的--horizontal -pod-autoscaler -sync -
period 参数指定周期（默认值为 15秒）。每个周期内， controller manager 根据每个
Horizon talPodAutoscaler 定义中指定的指标查询资源利用率。 controller manager 可以从
resource metrics API （pod 资源指标）和 custom metrics API （自定义指标）获取指标。

然后，通过现有 pods 的CPU 使用率的平均值（计算方式是最近的 pod 使用量（最近一分钟的平均
值， 从 metrics -server 中获得） 除以设定的每个 Pod 的CPU 使用率限额） 跟目标使用率进行比较，
并且在扩容时，还要遵循预先设定的副本数限制： MinReplicas <= Repli cas <= MaxReplicas 。

计算扩容后 Pod 的个数： sum( 最近一分钟内某个 Pod 的CPU 使用率的平均值 )/CPU 使用上限的
整数+1

流程：
**1、创建 HPA 资源，设定目标 CPU 使用率限额，以及最大、最小实例数**
**2、收集一组中（ PodSelector ）每个 Pod 最近一分钟内的 CPU 使用率，并计算平均值**
**3、读取 HPA 中设定的 CPU 使用限额**
**4、计算：平均值之和 /限额，求出目标调整的实例个数**
**5、目标调整的实例数不能超过 1中设定的最大、最小实例数，如果没有超过，则扩容；超过，则扩**
容至最大的实例个数
**6、回到 2，不断循环**

**3.2 安装数据采集组件 metrics -server**
metrics -server 是一个集群范围内的资源数据集和工具，同样的， metrics -server 也只是显示数
据，并不提供数据存储服务，主要关注的是资源度量 API的实现，比如 CPU、文件描述符、内存、
请求延时等指标， metric -server 收集数据给 k8s集群内使用，如 kubectl,hpa,scheduler 等
1.部署 metrics -server组件
#通过离线方式获取镜像
需要的镜像是： k8s.gcr.io/metrics -server -amd64:v0.3.6 和k8s.gcr.io/addon -resizer:1.8.4
镜像所在地址在课件，可自行下载，如果大家机器不能访问外部网络，可以把镜像上传
到k8s的各个节点，按如下方法手动解压：
docker load -i metrics -server -amd64 -0-3-6.tar.gz
docker load -i addon.tar.gz
#部署 metrics -server服务
#在/etc/kubernetes/manifests 里面改 一下 apiserver 的配置
> **注意：这个是 k8s在1.7的新特性，如果是 1.16 版本的可以不用添加， 1.17 以后要添加。这个参**
数的作用是 Aggregation 允许在不修改 Kubernetes 核心代码的同时扩展 Kubernetes API 。

```bash
[root@ xianchaomaster1  ~]# vim /etc/kubernetes/manifests/kube -apiserver.yaml
```
增加如下内容：
- --enable -aggregator -routing=true

重新更新 apiserver 配置：

```bash
[root@ xianchaomaster1  ~]# kubectl apply -f  /etc/kubernetes/manifests/kube -
apiserver.yaml
[root@ xianchaomaster1  ~]# kubectl apply -f metrics.yaml
#验证 metrics -server是否部署成功
[root@ xianchaomaster1  ~]# kubectl get pods -n kube -system | grep me trics
metrics -server -6595f875d6 -ml5pc            2/2     Running            0
#测试 kubectl  top命令
[root@ xianchaomaster1  ~]# kubectl top nodes
NAME       CPU(cores)   CPU%   MEMORY(bytes)   MEMORY%
xianchaomaster1    673m         11%    2518Mi          44%
xianchaonode1    286m         4%     1305Mi          22%

[root@ xianchaomaster1  ~]# kubectl top pods -n kube -system
NAME                                       CPU(cores)   MEMORY(bytes)
calico -kube -controllers -6949477b58 -xbt82   3m           13Mi
calico -node -4t7bs                          118m         55Mi
calico -node -hbx75                          105m         88Mi
calico -node -hdr45                          92m          95Mi
coredns -7f89b7bc75 -prt8x                   9m           13Mi
coredns -7f89b7bc75 -xncd5                   8m           11Mi
etcd-xianchaomaster1                               62m          44Mi
kube -apiserver                             0m           0Mi
kube -apiserver -xianchaomaster1                     204m         332Mi
kube -controller -manager -xianchaomaster1            64m          48Mi
kube -proxy -6hwqz                           1m           17Mi
kube -proxy -jhlhv                           1m           19Mi
kube -proxy -wx64x                           2m           12Mi
kube -scheduler -xianchaomaster1                     10m          22Mi
metrics -server -6595f875d6 -ml5pc            3m           16Mi
```

**3.3 创建 php-apache服务，利用 HPA进行自动扩缩容。**
#基于 dockerfile 构建一个 PHP-apache项目
1）创建并运行一个 php-apache服务
使用 dockerfile 构建一个新的镜像，在 k8s的xianchaomaster1 节点构建

```bash
 [root@ xianchaomaster1  ~]# mkdir php
[root@ xianchaomaster1  ~]# cd php/
[root@xianchaomaster1 ~]# docker load -i php.tar.gz
[root@ xianchaomaster1  php]# cat dockerfile
FROM php:5 -apache
ADD index.php /var/www/html/index.php
RUN chmod a+rx index.php
[root@ xianchaom aster1  php]# cat index.php
<?php
$x = 0.0001;
for ($i = 0; $i <= 1000000;$i++) {
$x += sqrt($x);
  }
 echo "OK!";
?>
#构建镜像
[root@ xianchaomaster1  php]# docker build -t xianchao/hpa -example:v1 .
#打包镜像
[root@xianchaomaster1 php]# docker save -o hpa-example.tar.gz xianchao/hpa -
example:v1
[root@xianchaomaster1 php]# scp hpa -example.tar.gz xianchaonode1:/root/

#解压镜像
```
可以把镜像传到 k8s的各个工作节点，通过 docker load -i hpa -example.tar.gz 进行解
压：

```bash
[root@xianchaonode1 ~]# docker load -i hpa -example.tar.gz

#通过 deployment 部署一个 php-apache服务
[root@ xianchaomaster1  ~]# cat php -apache.yaml
```

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: php -apache
spec:
  selector:
    matchLabels:
      run: php -apache
  replicas: 1
  template:
    metadata:
      labels:
        run: php -apache
    spec:

       containers:
      - name: php -apache
        image: xianchao /hpa-example:v1
        ports:
        - containerPort: 80
        resources:
          limits:
            cpu: 500m
          requests:
            cpu: 200m
---
apiVersion: v1
kind: Service
metadata:
    name: php -apache
    labels:
      run: php -apache
spec:
  ports:
  - port: 80
  selector:
   run: php -apache

#更新资源清单文件
```

```bash
[root@ xianchaomaster1  ~]# kubectl apply -f php -apache.yaml
deploy ment.apps/php -apache created
service/php -apache created
#验证 php是否部署成功
[root@ xianchaomaster1  ~]# kubectl get pods
NAME                            READY   STATUS    RESTARTS   AGE
php-apache -7d8fdb687c -bq8c7   1/1     Running    0            31s
```

**3.4 创建 HPA**
php-apache服务正在运行， 使用 kubectl autoscale 创建自动缩放器， 实现对 php-apache
这个 deployment 创建的 pod自动扩缩容，下面的命令将会创建一个 HPA，HPA将会
根据 CPU，内存等资源指标增加或减少副本数，创建一个可以实现如下目的的 hpa：
1）让副本数维持在 1-10个之间（这里副本数指的是通过 deployment 部署的 pod的副
本数）
2）将所有 Pod的平均 CPU使用率维持在 50％（通过 kubectl top看到的每个 pod如果
是200毫核，这意味着平均 CPU利用率为100毫核）

```bash
#给上面 php-apache这个 deployment 创建 HPA
[root@ xianchaomaster1  ~]# kubectl autoscale deployment php -apache --cpu-
percent=50 --min=1 --max=10
#上面命令解释说明
```
kubectl autoscale deployment php -apache （php-apache表示 deployment 的名字）  -
-cpu-percent=50 （表示 cpu使用率不超过 50%） --min=1（最少一个 pod）
--max=10（最多 10个pod）

```bash
#验证 HPA是否创建成功
[root@ xianchaomaster1  ~]# kubectl get hpa
```

> **注：由于我们没有向服务器发送任何请求，因此当前 CPU消耗为 0％（TARGET列显示**
了由相应的 deployment 控制的所有 Pod的平均值） 。

**3.5 压测 php-apache服务，只是针对 CPU做压测**
#把busybox.tar.gz 和nginx -1-9-1.tar.gz上传到 xianchaonode1 上，手动解压：
docker load -i busybox.tar.gz
docker load -i nginx -1-9-1.tar.gz
启动一个容器，并将无限查询循环发送到 php-apache服务（复制 k8s的master节点
的终端，也就是打开一个新的终端窗口） ：

```bash
[root@xianchaomaster1]#  kubectl run v1 -it --image=busybox --image -pull-
policy=IfNotPresent /bin/sh
```

登录到容器之后，执行如下命令
/# while true; do wget -q -O- http://php -apache.default.svc.cluster.local;  done
在一分钟左右的时间内，我们通过执行以下命令来看到更高的 CPU负载
kubectl get hpa
显示如下：
NAME         REFERENCE               TARGETS    MINPODS   MAXPODS
REPLICAS
php-apache   Deployment/php -apache   231%/50%    1        10           4
上面可以看到， CPU消耗已经达到 256％，每个 pod的目标 cpu使用率是 50%，所以，
php-apache这个 deployment 创建的 pod副本数将调整为 5个副本，为什么是 5个副
本，因为 256/50=5
kubectl get pod
显示如下：
NAME                          READY   STATUS    RESTARTS   AGE

 php-apache -5694767d56 -b2kd7   1/1     Running   0          18s
php-apache -5694767d56 -f9vzm   1/1     Running   0          2s
php-apache -5694767d56 -hpgb5   1/1     Running   0          18s
php-apache -5694767d56 -mmr88   1/1     Running   0          4h13m
php-apache -5694767d56 -zljkd      1/1     Running   0          18s

kubectl get deployment php -apache
显示如下：
NAME         READY   UP -TO-DATE   AVAILABLE   AGE
php-apache   5/5     5            5           2h1m

> **注意：可能需要几分钟来稳定副本数。由于不以任何方式控制负载量，因此最终副本数**
可能会与此示例不同。
停止对 php-apache服务压测， HPA会自动对 php-apache这个 deployment 创建的 pod
做缩容
停止向 php-apache这个服务发送查询请求，在 busybox 镜像创建容器的终端中，通过
<Ctrl>+ C把刚才 while请求停止，然后，我们将验证结果状态（大约一分钟后） ：
kubectl get hpa
显示如下：

kubectl get deployment php -apache
显示如下：
php-apache        1/1     1            1           5s
通过上面可以看到， CPU利用率下降到 0，因此 HPA自动将副本数缩减到 1。
> **注意：自动缩放副本可能需要几分钟。**

**4、利用 HPA基于内存指标实现 pod自动扩缩容**
**1、创建一个 nginx的pod**

```bash
[root@ xianchaomaster1  ~]# cat nginx.yaml
```

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx -hpa
spec:
  selector:
    matchLabels:
      app: nginx
  replicas: 1
  template:

     metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.9.1
        imagePullPolicy : IfNotPresent
        ports:
        - containerPort: 80
          name: http
          protocol: TCP
        resources:
          requests:
            cpu: 0.01
            memory: 25Mi
          limits:
            cpu: 0.05
            memory: 60Mi
---
apiVersion: v1
kind: Service
metadata:
  name: nginx
  labels:
    app: nginx
spec:
  selector:
    app: nginx
  type: NodePort
  ports:
  - name: http
    protocol: TCP
    port: 80
    targetPort: 80

#更新资源清单文件
```

```bash
[root@ xianchaomaster1  ~]# kubectl apply -f nginx.yaml
deployment.apps/nginx -hpa created
service/nginx created
```
**2、验证 nginx是否运行**

```bash
[root@ xianchaomaster1  ~]# kubectl get pods
NAME                          READY   STATUS    RESTARTS   AGE

 nginx -hpa-fb74696c -6m6st      1/1     Running   0          28s
```
> **注意：**
nginx的pod里需要有如下字段，否则 hpa会采集不到内存指标
 resources:
    requests:
      cpu: 0.01
      memory: 25Mi
    limits:
       cpu: 0.05
       memory: 60Mi
**3、创建一个 hpa**

```bash
[root@ xianchaomaster1  ~]# cat hpa -v1.yaml
```

```yaml
apiVersion: autoscaling/v2beta1
kind: HorizontalPodAutoscaler
metadata:
  name: nginx -hpa
spec:
    maxReplicas: 10
    minReplicas: 1
    scaleTargetRef:
      apiVersion: apps/v1
      kind: Deployment
      name: nginx -hpa
    metrics:
    - type: Resource
      resource:
        name: memory
        targetAverageUtilization: 60

#更新资源清单文件
```

```bash
[root@ xianchaomaster1  ~]# kubectl apply -f hpa -v1.yaml
horizontalpodautoscaler.autoscaling/n ginx-hpa created
#查看创建的 hpa
[root@ xianchaomaster1  ~]# kubectl get hpa
NAME         REFERENCE           TARGETS   MINPODS   MAXPODS

 REPLICAS
nginx -hpa    Deployment/nginx -hpa    5%/60%    1         10        1
5
```
**4、压测 nginx的内存， hpa会对 pod自动扩缩容**
登录到上面 通过 pod创建的 nginx，并生成一个文件，增加内存

```bash
[root@xianchaomaster1]# kubectl exec -it nginx -hpa-fb74696c -6m6st   -- /bin/sh
#压测
# dd if=/dev/zero of=/tmp/a

#打开新的终端
[root@ xianchaomaster1  ~]# kubectl get hpa
NAME         REFERENCE     TARGETS   MINPODS   MAXPODS   REPLICAS
AGE
nginx -hpa    Deployment/nginx -hpa    200%/60%    1         10        1
```

上面的 targets列可看到 200%/60% ，200%表示当前 内存使用率， 60%表示所有 pod的内
存使用率维持在 60%，现在内存使用率达到 200%，所以 pod增加到 4个

```bash
[root@ xianchaomaster1  ~]# kubectl get deployment
```
显示如下：
NAME         READY   UP-TO-DATE   AVAILABLE   AGE
nginx -hpa    4/4     4            4           25m

```bash
[root@ xianchaomaster1  ~]# kubectl get pods
```
显示如下 :
NAME                          READY   STATUS    RESTARTS   AGE
nginx -hpa-bb598885d -j4kcp     1/1     Running   0          25m
nginx -hpa-bb598885d -rj5hk     1/1     Running   0          63s
nginx -hpa-bb598885d -twv9c     1/1     Running   0          18s
nginx -hpa-bb598885d -v9ft5     1/1     Running   0          63s

**5、取消对 nginx内存的压测， hpa会对 pod自动缩容**

```bash
[root@ xianchaomaster1  ~]# kubectl exe c -it nginx -hpa-fb74696c -6m6st  -- /bin/sh
```
删除/tmp/a这个文件

```bash
# rm -rf /tmp/a
[root@ xianchaomaster1  ~]# kubectl get hpa
```
显示如下 ,可看到内存使用率已经降到 5%:
NAME        REFERENCE              TARGETS   MINPODS   MAXPODS
REPLICAS   AGEnginx -hpa   Deployment/nginx -
hpa   5%/60 %    1         10        1          26m

```bash
[root@ xianchaomaster1  ~]# kubectl get deployment
```
显示如下， deployment 的pod又恢复到 1个了：

 NAME         READY   UP -TO-DATE   AVAILABLE   AGE
nginx -hpa    1/1     1            1           38m

扩展：查看 v2版本的 hpa如何定义？

```bash
[root@xianchaomaster1 ~]#  kubectl get hpa.v2beta2.autoscaling -o yaml > 1.yaml
```

**5、VPA实现 Pod自动扩缩容**
Vertical Pod Autoscaler （VPA）：垂直 Pod自动扩缩容， 用户无需为其 pods中的容器设置最
新的资源 request。配置后，它将根据使用情况自动设置 request，从而允许在节点上进行适
当的调度，以便为每个 pod提供适当的资源量。

**6.1 安装 vpa**

```bash
[root@xianchaonode1 ~]# docker load -i vpa-admission -controller_0_8_0.tar.gz
Loaded image: scofield/vpa -admission -controller:0.8.0
[root@xianchaonode1 ~]# do cker load -i vpa-recommender_0_8_0.tar.gz
Loaded image: scofield/vpa -recommender:0.8.0
[root@xianchaonode1 ~]# docker load -i vpa-updater_0_8_0.tar.gz
Loaded image: scofield/vpa -updater:0.8.0

[root@xianchaomaster1~]#unzip  autoscaler -vertical -pod-autosca ler-0.8.0.zip
[root@xianchaomaster1 ~]# cd  /root/autoscaler -vertical -pod-autoscaler -0.8.0/vertical -
pod-autoscaler/deploy
```
修改 admission -controller -deployment.yaml 里的 image：
image:  scofield/vpa -admission -controller:0.8.0
imagePullPolicy: IfNotPresent

修改 recommender -deployment.yaml 里的 image：
image: scofield/vpa -recommender:0.8.0
imagePullPolicy: IfNotPresent

修改 updater -deployment.yaml 文件里的 image：
image: scofield/vpa -updater:0.8.0
imagePullPolicy: IfNotPresent

```bash
[root@xianchaomaster1]# cd /root/autoscaler -vertic al-pod-autoscaler -0.8.0/vertical -pod-
autoscaler/hack

 [root@xianchaomaster1 hack]# ./vpa -up.sh

#验证 vpa是否部署成功：
[root@xianchaomaster1]# kubectl get pods -n kube -system | grep vpa
vpa-admission -controller -777694497b -6rrd4   1/1     Running   0          86s
vpa-recommender -64f6765bd9 -ckmvf         1/1     Running   0          86s
vpa-updater -c5474f4c7 -vq82f                 1/1     Running   0         8 6s
```

**6.2 测试 VPA实现 pod自动扩缩容**
**6.2.1 updateMode: "Off"**
**1、部署一个 nginx服务,部署到 namespace: vpa 名称空间下 ：**

```bash
[root@xianchaomaster1 ~]# mkdir vpa
[root@xianchaomaster1 ~]# cd vpa/
[root@xianchaomaster1 vpa]# kubectl create ns vpa
[root@xianchaomaster1 vpa]# cat vpa -1.yaml
```

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: nginx
  name: nginx
  namespace: vpa
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - image: nginx
        name: nginx
        imagePullPolicy: IfNotP resent
        resources:
          requests:

             cpu: 200m
            memory: 300Mi

```

```bash
[root@xianchaomaster1 vpa]# kubectl apply -f vpa -1.yaml
[root@xianchaomaster1 vpa]# kubectl get pods -n vpa
NAME                     READY   STATUS    RESTARTS   AGE
nginx -5f598bd784 -fknwq   1/1     Running   0          6s
nginx -5f598bd784 -ljq75    1/1     Running   0          6s
```

**2、在nginx管理的 pod前端创建四层代理 Service**

```bash
[root@xianchaomaster1 vpa]# cat vpa -service -1.yaml
```

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx
  namespace: vpa
spec:
  type: NodePort
  ports:
  - port: 80
    targetPort: 80
  selector:
app: nginx

```

```bash
[root@xianchaomaster1 vpa]# kubectl apply -f vpa -service -1.yaml
[root@xianchaomaster1 vpa]# kubectl get svc -n vpa
NAME    TYPE       CLUSTER -IP     EXTERNAL -IP   PORT(S)        AGE
nginx   NodePort   10.109.35.41   <none>        80:31957/TCP   3m28s
[root@xianchaomaster1 vpa]# curl -I 192.168.40.180:31957
HTTP/1.1 200 OK
#显示 200说明代理没问题
```

**3、创建 VPA**
先使用 updateMode: "Off" 模式，这种模式仅获取资源推荐 值，但是 不更新 Pod

```bash
[root@xianchaomaster1 vpa]# cat vpa -nginx.yaml
```

```yaml
apiVersion: autoscaling.k8s.io/v1beta2
kind: VerticalPodAutoscaler
metadata:
  name: nginx -vpa
  namespace: vpa
spec:
  targetRef:

     apiVersion: "apps/v1"
    kind: Deployment
    name: nginx
  updatePoli cy:
    updateMode: "Off"
  resourcePolicy:
    containerPolicies:
    - containerName: "nginx"
      minAllowed:
        cpu: "500m"
        memory: "100Mi"
      maxAllowed:
        cpu: "2000m"
        memory: "2600Mi"

```

```bash
[root@xianchaomaster1 vpa]# kubectl apply -f vpa -nginx.yaml
[root@xianchaomaster1 vpa]# kubectl get vpa -n vpa
NAME        AGE
nginx -vpa   6s
```

查看 vpa详细信息：

```bash
[root@xianchaomaster1 vpa]#  kubectl  describe  vpa nginx -vpa   -n vpa
Name:         nginx -vpa
Namespa ce:    vpa
Labels:       <none>
Annotations:  <none>
API Version:  autoscaling.k8s.io/v1
```

```yaml
Kind:         VerticalPodAutoscaler
Metadata:
  Creation Timestamp:  2021 -07-15T04:40:48Z
  Generation:          2
  Managed Fields:
    API Version:  autoscaling.k8s. io/v1beta2
    Fields Type:  FieldsV1
    fieldsV1:
      f:metadata:
        f:annotations:
          .:
          f:kubectl.kubernetes.io/last -applied -configuration:
      f:spec:
        .:
        f:resourcePolicy:
          .:

           f:containerPolicies:
        f:targetRef:
          .:
          f:apiVersion:
          f:kind:
          f:name:
        f:updatePolicy:
          .:
          f:updateMode:
    Manager:      kubectl -client -side-apply
    Operation:    Update
    Time:         2021 -07-15T04:40:48Z
    API Version:  autoscaling.k8s.io/v1
    Fields Type:  FieldsV1
    fieldsV1:
      f:status:
        .:
        f:conditions:
        f:recommendation:
          .:
          f:containerRecommendations:
    Manager :         recommender
    Operation:       Update
    Time:            2021 -07-15T04:41:34Z
  Resource Version:  385606
  Self Link:
/apis/autoscaling.k8s.io/v1/namespaces/vpa/verticalpodautoscalers/nginx -vpa
  UID:               fe00ca65 -7dd3 -495f-bcba -b1e602f01fb3
Spec:
  Resource Policy:
    Container Policies:
      Container Name:  nginx
      Max Allowed:
        Cpu:     2000m
        Memory:  2600Mi
      Min Allowed:
        Cpu:     500m
        Memory:  100Mi
  Target Ref:
    API Version:  apps/v1
    Kind:         Deployment
    Name:         nginx
  Update Policy:
```

     Update Mode:  Off
Status:
  Conditi ons:
    Last Transition Time:  2021 -07-15T04:41:34Z
    Status:                True

```yaml
    Type:                  RecommendationProvided
  Recommendation:
    Container Recommendations:
      Container Name:  nginx
      Lower Bound:
        Cpu:     500m
        Memory:  262144k
      Target:
        Cpu:     500m
        Memory:  262144k
      Uncapped Target:
        Cpu:     25m
        Memory:  262144k
      Upper Bound:
        Cpu:     1349m
        Memory:  1410936619
Events:          <none>

```
Lower Bound:           下限值
Target:                推荐值
Upper Bound:           上限值
Uncapped Target:       如果没有为 VPA提供最小或最大边界，则表示目标利
用率

上面结果表示 ，推荐的  Pod 的 CPU 请求为 500m，推荐的内存请求为  262144k
字节。

```bash
#压测 nginx
[root@xianchaomaster1 vpa]# yum -y install htt pd-tools ab
[root@xianchaomaster1 vpa]#  ab -c 100 -n 10000000 http://192.168.40.180:31957/

#过几分钟后观察 VPA Recommendation 变化
[root@xianchaomaster1 vpa]#  kubectl  describe  vpa nginx -vpa   -n vpa
Recommendation:
    Container Recommendations:
      Container Name:  nginx
      Lower Bound:

         Cpu:     500m
        Memory:  262144k
      Target:
        Cpu:     763m
        Memory:  262144k
      Uncapped Target:
        Cpu:     763m
        Memory:  262144k
      Upper Bound:
        Cpu:     2
        Memory:  934920074
Events:          <none>
```
从以上信息可以看出， VPA对Pod给出了推荐值： Cpu: 763m，因为我们这里设置了
updateMode: "Off" ，所以不会更新 Pod

```bash
[root@xianchaomaster1 vpa]# kubectl get pods -n vpa
NAME                     R EADY   STATUS    RESTARTS   AGE
nginx -5f598bd784 -fknwq   1/1     Running   0          79m
nginx -5f598bd784 -ljq75   1/1     Running   0          79m

6.2.2  updateMode: " On"
```
**1、现在我把 updateMode: "Auto" ，看看 VPA会有什么动作**
这里我把 resources 改为：memory: 50Mi ，cpu: 100m

```bash
[root@xianchaomaster1 vpa]# cat vpa -nginx -1.yaml
```

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: nginx
  name: nginx
  namespace: vpa
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:

       labels:
        app: nginx
    spec:
      containers:
      - image: nginx
        imagePullPolicy: IfNotPresent
        name: nginx
        resources:
          requests:
            cpu: 100m
            memory: 50Mi

```

```bash
[root@xianchaomaster1 vpa]# kubectl apply -f vpa -nginx -1.yaml
[root@xianchaomaster1 vpa]# kubectl get pods -n vpa
NAME                    READY   STATUS    RESTARTS   AGE
nginx -b75478445 -jxp5d   1/1     Running   0          30s
nginx -b75478445 -psh2j   1/1     Running   0          30s
```

**2、再次部署 vpa**

```bash
[root@xianchaomaster1 vpa]# cat vpa -nginx.yaml
```

```yaml
apiVersion: autoscaling.k8s.io/v1beta2
kind: VerticalPodAutoscaler
metadata:
  name: nginx -vpa-2
  namespace: vpa
spec:
  targetRef:
    apiVersion: "apps/v1"
    kind: Deployment
    name: nginx
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: "nginx"
      minAllowed:
        cpu: "500m"
        memory: "100Mi"
      maxAllowed:
        cpu: "2000m"
        memory: "2600Mi"

```

```bash
 [root@xianchaomaster1 vpa]# kubectl apply -f vpa -nginx.yaml
verticalpodautoscaler.autoscaling.k8s.io/nginx -vpa-2 created
[root@xianchaomaster1 vpa]# kubectl get vpa -n vpa
NAME          MOD E   CPU    MEM       PROVIDED   AGE
nginx -vpa     Off    500m   262144k   True       72m
nginx -vpa-2   Auto                               9s
```

**3、再次压测**

```bash
[root@xianchaomaster1 vpa]#  ab -c 100 -n 10000000 http://192. 168.40.180:31957/
```

**4、几分钟后，使用 describe 查看 vpa详情，只关注 Container Recommendations**

```bash
[root@xianchaomaster1 ~]#  kubectl  describe  vpa nginx -vpa   -n vpa |tail -n 20
```

Target变成了Cpu: 656m ，Memory: 262144k

**5、来看下 event事件**

```bash
[root@xianchaomaster1 ~]# kubectl get event -n vpa
```

从输出信息可以 看到，vpa执行了 EvictedByVPA ，自动停掉了 nginx，然后使用  VPA推荐的
资源启动了新的 nginx
，我们查看下 nginx的pod可以得到确认

```bash
[root@xianchaomaster1 ~]# kubectl get pods -n vpa
NAME                    READY   STATUS    RESTARTS   AGE
nginx -b75478445 -9sd46   1/1     Running   0          15h
[root@xianchaomaster1 ~]# kubectl describe  pods nginx -b75478445 -9sd46 -n vpa

Name:         nginx -b75478445 -9sd46
Namespace:    vpa
Priority:     0
Node:         xianchaonode1/192.168.40.181
Start Time:   Thu, 15 Jul 2021 14:13:34 +0800
Labels:       app=nginx
              pod-template -hash=b75478445
Annotations:  cni.projectcalico.org/podIP: 10.244.121.28/32
              cni.projectcalico.org/podIPs: 10.244.121.28/32
Status:       Running
IP:           10.244.121.28
IPs:
  IP:           10.244.121.2 8
Controlled By:  ReplicaSet/nginx -b75478445
Containers:
  nginx:
    Container ID:
docker://f9d7ac11769acef2801c7d9a1090f4ece4ebe22e1eb4f128659617b1467a069d
    Image:          nginx
    Image ID:       docker -

 pullable://nginx@sha256:353c20f74d9b6aee359 f30e8e4f69c3d7eaea2f610681c4a95849a2fd
7c497f9
    Port:           <none>
    Host Port:      <none>
    State:          Running
      Started:      Thu, 15 Jul 2021 14:13:35 +0800
    Ready:          True
    Restart Count:  0
    Requests:
      cpu:        656m
      memory:    262144k
```

再回头看看部署文件

现在可以知道 VPA做了哪些事了吧。当然，随着服务的负载的变化， VPA的推荐值也会不
断变化。当目前运行的 pod的资源达不到 VPA的推荐值，就会执行 pod驱逐，重新部署新
的足够资源的服务。

VPA使用限制 ：
不能与 HPA（Horizontal Pod Autoscaler ）一起使用
Pod比如使用副本控制器，例如属于 Deployment 或者 StatefulSet

VPA有啥好处 ：
Pod 资源用其所需，所以集群节点使用效率高。
Pod 会被安排到具有适当可用资源的节点上。
不必运行基准测试任务来确定  CPU 和内存请求的合适值。
VPA 可以随时调整  CPU 和内存请求，无需人为操作，因此可以减少维护时间。

VPA是Kubernetes 比较新的功能，还没有在生产环境大规模实践过，不建议在线上环境使
用自动更新模式，但是使用推荐模式你可以更好了解服务的资源使用情况。

**6、kubernetes  cluster -autoscaler**
**1、什么是  cluster -autoscaler**
Cluster Autoscaler (CA) 是一个独立程序，是用来弹性伸缩 kubernetes 集群的。它可以

 自动根据部署应用所请求 的资源量来动态的伸缩集群。 当集群容量不足时，它会自动去
Cloud Provider （支持  GCE、GKE 和 AWS）创建新的  Node，而在  Node 长时间资源
利用率很低时自动将其删除以节省开支。

项目地址： https://github.com/kubernetes/autoscaler

**2、Cluster Autoscaler 什么时候伸缩集群 ?**

在以下情况下，集群自动扩容或者缩放：
扩容：由于资源不足，某些 Pod无法在任何当前节点上进行调度

缩容: Node节点资源利用率较低时，且此 node节点上存在的 pod都能被重新调度到
其他 node节点上运行

**3、什么时候集群节点不会被  CA 删除?**
1）节点上有 pod被 PodDisruptionBudget 控制器限制。
2）节点上有命名空间是  kube-system 的pods。
3）节点上的 pod不是被控制器创建，例如不是被 deployment, replica set, job, stateful
set创建。
4）节点上有 pod使用了本地存储
5）节点上 pod驱逐后无处可去，即没有其他 node能调度这个 pod
6）节点有注解： "cluster -autoscaler.kubernetes.io/scale -down -disabled": "true"( 在CA
1.0.3或更高版本中受支持 )

扩展：什么是 PodDisruptionBudget ？
通过 PodDisruptionBudget 控制器可以设置应用 POD集群处于运行状态最低个数，也
可以设置应用 POD集群处于运行状态的最低百分比，这样可以保证在主动销毁应用
POD的时候，不会一次性销毁太多的应用 POD，从而保证业务不中断

**4、Horizontal Pod Autoscaler 如何与  Cluster Autoscaler 一起使用 ?**
Horizontal Pod Autoscaler 会根据当前 CPU负载更改部署或副本集的副本数。如果负
载增加， 则 HPA将创建新的副本， 集群中可能有足够的空间， 也可能没有足够的空间。
如果没有足够的资源， CA将尝试启动一些节点，以便 HPA创建的 Pod可以运行。如果
负载减少， 则 HPA将停止某些副本。 结果， 某些节点可能变得利用率过低或完全为空，
然后 CA将终止这些不需要的节点。

扩展：如何防止节点被 CA删除?
节点可以打上以下标签：
"cluster -autoscaler.kubernetes.io/scale -down -disabled": "true"

可以使用  kubectl 将其添加到节点 (或从节点删除 )：
$ kubectl annotate node  <nodename>  cluster -autoscaler.kubernetes.io/scale -down -

```bash
disabled=true
```

**5、Cluster Autoscaler 支持那些云厂商 ?**
GCE https://kubernetes.io/docs/concepts/cluster -administration/cluster -management/
Google云服务商

GKE https://cloud.goo gle.com/container -engine/docs/cluster -autoscaler
Google  kubernetes 服务

AWS（亚 马 逊 ） https://github.com/kubernetes/autoscaler/blob/master/cluster -
autoscaler/cloudprovider/aws/README.md

Azure（ 微 软 ）  https://github.com/kubernetes/autoscaler/blob/master/cluster -
autoscaler/cloudprovider/azure/README.md

Alibaba Cloud https://github.com/kubernetes/autoscaler/blob/master/cluster -
autoscaler/cloudprovider/alicloud/README.md

OpenStack Magnum https://github.com/kubernetes/autoscaler/blob/master/cluster -
autoscaler/cloudprovider/magnum/README.md

DigitalOcean https://github.com/kubernetes/autoscaler/blob/master/cluster -
autoscaler/cloudprovider/digitalocean/README.md

CloudStack https://github.com/kubernetes/autoscaler/blob/master/cluster -
autoscaler/cloudprovider/cloudstack/README.md

Exoscale https://github.com/kubernetes/autoscaler/blob/master/cluster -
autoscaler/cloudprovider/exoscale/README.md

Packet https://githu b.com/kubernetes/autoscaler/blob/master/cluster -
autoscaler/cloudprovider/packet/README.md

OVHcloud https://github.com/kubernetes/autoscaler/blob/master/cluster -
autoscaler/cloudprovider/ovhcloud/README.md

Linode https://github.com/kubernetes/autoscaler/blob/master/cluster -
autoscaler/cloudprovider/linode/README.md

Hetzner https://github.com/kubernetes/autoscaler/blob/master/cluster -
autoscaler/cloudprovider/hetzner/README.md

Cluster API   https://github.com/kubernetes/autoscaler/blob/master/cluster -
autoscaler/cloudprovider/clusterapi/README.md

**7、kubernetes  KPA**
Github： https://knative.dev/docs/install/

安装参考：
https://knative.dev/docs/install/install -serving -with-yaml/


