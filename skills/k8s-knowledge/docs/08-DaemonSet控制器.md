k8s控制器： Daemonset

1  DaemonSet 控制器：概念、原理解读

**1.1 DaemonSet 概述**
DaemonSet控制器能够确保 k8s集群所有 的节点都运行一个相同的 pod副本，当向
k8s集群中增加 node节点时，这个 node节点也会自动创建一个 pod副本，当node节点从

 集群移除，这些 pod也会自动删除；删除 Daemonset 也会删除它们创建的 pod

**1.2 DaemonSet 工作原理 ：如何管理 Pod？**
daemonset 的控制器会监听 kuberntes 的daemonset 对象、pod对象、node对象，这
些被监听的对象之变动，就会触发 syncLoop 循环让kubernetes 集群朝着 daemonset 对象
描述的状态进行演进。

**1.3 Daemonset 典型的应用 场景**

在集群的每个节点上运行存储，比如： glusterd 或 ceph。
在每个节点上运行日志收集 组件，比如： flunentd 、 logstash 、filebeat 等。
在每个节点上运行监控 组件，比如： Prometheus 、 Node Exporter 、collectd 等。

**1.4 DaemonSet 与 Deployment 的区别**
Deployment 部署的副本  Pod 会分布在各个  Node 上，每个  Node 都可能运行好几
个副本。

DaemonSet 的不同之处在于：每个  Node 上最多只能运行一个副本。

2 DaemonSet 资源清单 文件编写技巧

```bash
#查看定义Daemonset 资源需要的字段有哪些？
[root@xianchaomaster1  ~]# kubectl explain ds
```

```yaml
KIND:     DaemonSet
VERSION:  apps/v1

DESCRIPTION:
     DaemonSet represents the configuration of a daemon set.

FIELDS:
   apiVersion  <string>  #当前资源使用的 api版本，跟 VERSION:  apps/v1 保持
```
一致
   kind <string>   #资源类型，跟 KIND:  DaemonSet 保持一致
   metadata  <Object>  #元数据，定义 DaemonSet 名字的
   spec <Object>     #定义容器的
   status <Object>   #状态信息，不能改

```bash
#查看DaemonSet 的spec字段如何定义？
[root@xianchaomaster1  ~]# kubectl explain ds.spec
```

```yaml
KIND:     DaemonSet
VERSION:  apps/v1
RESOURCE: spec <Object>
DESCRIPTION:
     The desired behavior of this daemon set. More info:

      https://git.k8s.io/community/contributors/devel/sig -
architecture/api -conventions.md#spec -and-status
     DaemonSetSpec is the specification of a daemon set.
FIELDS:
   minReadySecon ds <integer>    #当新的pod启动几秒 种后，再 kill掉旧的
pod。
   revisionHistoryLimit  <integer>  #历史版本
   selector  <Object> -required -  #用于匹配 pod的标签选择器
   template  <Object> -required -
#定义Pod的模板，基于这个模板定义的所有 pod是一样的
   updateStrategy  <Object>  #daemonset 的升级策略
#查看DaemonSet 的spec.template 字段如何定义？
#对于template 而言，其内部定义的就是 pod，pod模板是一个独立的对象
```

```bash
[root@xianchaomaster1  ~]# kubectl explain ds.spec.template
```

```yaml
KIND:     DaemonSet
VERSION:  apps/v1
RESOURCE: template <Object>
FIELDS:
   metadata  <Object>
   spec<Object>

```
3 DaemonSet 使用案例 ：部署日志收集组件 fluentd
#把fluentd-2-5-1.tar.gz 上传到xianchaomaster1 和xianchaonode2 和
xianchaonode1 上，解压

```bash
[root@xianchaonode2 ]# docker load -i fluentd_2_5_1.tar.gz
[root@xianchaonode1 ]# docker load -i fluentd_2_5_1.tar.gz
[root@xianchaomaster1 ]# docker load -i fluentd_2_5_1.tar.gz

#编写一个 DaemonSet 资源清单
[root@xianchaomaster1  ~]# cat daemonset.yaml
```

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd -elasticsearch
  namespace: kube -system
  labels:
    k8s-app: fluentd -logging
spec:
  selector:
    matchLabels:
      name: fluentd -elasticsearch
  template:

     metadata:
      labels:
        name: fluentd -elasticsearch
    spec:
      tolerations:
      - key: node -role.kubernetes.io/master
        effect: NoSchedule
      containers:
      - name: fluentd -elasticsearch
        image: xianchao /fluentd:v2.5.1
        resources:
          limits:
            memory: 200Mi
          requests:
            cpu: 100m
            memory: 200Mi
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
      terminationGracePeriodSeconds: 30
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
```

```bash
[root@xianchaomaster1  ~]# kubectl apply -f daemonset.yaml
daemonset.apps/fluentd -elasticsearch created
[root@xianchaomaster1  ~]# kubectl get ds -n kube-system
NAME               DESIRED   CURRENT   READY   UP -TO-DATE   AVAILABLE
fluentd-elasticsearch   3          3          3           3
3
[root@xianchaomaster1  ~]# kubectl get pods -n kube-system -o wide

#通过上面可以看到在 k8s的三个节点均创建了 fluentd这个pod
#pod的名字是 由控制器的名字 -随机数组成的
#资源清单详细说明
```

```yaml
apiVersion: apps/v1  #DaemonSet 使用的api版本

 kind: DaemonSet     # 资源类型
metadata:
  name: fluentd -elasticsearch   # 资源的名字
  namespace: kube -system      # 资源所在的名称空间
  labels:
    k8s-app: fluentd -logging    # 资源具有的标签
spec:
  selector:         # 标签选择器
    matchLabels:
      name: fluentd -elasticsearch
  template:
    metadata:
      labels:  # 基于这回模板定义的 pod具有的标签
        name: fluentd -elasticsearch
    spec:
      tolerations:   # 定义容忍度
      - key: node -role.kubernetes.io/master
        effect: NoSchedule
      containers:    # 定义容器
      - name: fluentd -elasticsearch
        image: xianchao /fluentd:v2.5.1
        resources:   #资源配额
          limits:
            memory: 200Mi
          requests:
            cpu: 100m
            memory: 200Mi
        volumeMounts:
        - name: varlog
          mountPath: /var/log   # 把本地/var/log 目录挂载到容器
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
#把/var/lib/docker/containers /挂载到容器 里
          readOnly: true  # 挂载目录是只读权限
      terminationGracePeriodSeconds: 30   #优雅的关闭服务
      volumes:
      - name: varlog
        hostPath:
          path: /var/log  # 基于本地目录创建一个卷
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers  # 基于本地目录创建一个卷

 4 Daemonset 管理pod：滚动更新

#DaemonSet 实现pod的滚动更新
#查看daemonset 的滚动更新策略
```

```bash
[root@xianchaomaster1  ~]# kubectl explain ds.spec.updateStrategy
```

```yaml
KIND:     DaemonSet
VERSION:  apps/v1
RESOURCE: updateStrategy <Object>
DESCRIPTION:
     An update strategy to replace existing DaemonSet pods with new pods.
     DaemonSetUpdateStrategy is a struct used to control the update
strategy for
     a DaemonSet.
FIELDS:
   rollingUpdate  <Object>
     Rolling update config params. Present only i f type =
"RollingUpdate".
   type <string>
     Type of daemon set update. Can be "RollingUpdate" or "OnDelete".
Default is
     RollingUpdate.
#查看rollingUpdate 支持的更新策略
```

```bash
[root@xianchaomaster1  ~]# kubectl explain
ds.spec.updateStrategy.rollingUpdate
```

```yaml
KIND:     DaemonSet
VERSION:  apps/v1
RESOURCE: rollingUpdate <Object>
DESCRIPTION:
     Rolling update config params. Present only if type =
"RollingUpdate".
     Spec to control the desired behavior of daemon set rolling update.

FIELDS:
   maxUnavailable  <string>

#上面表示 rollingUpdate 更新策略只支持 maxUnavailabe ，先删除在更新；因为我
```
们不支持一个节点运行两个 pod，因此需要先删除一个，在更新一个 。
#更新镜像版本，可以按照如下方法：
kubectl set image daemonsets fluentd-
elasticsearch =ikubernetes/filebeat:5.6.6 -alpine -n kube-system

 kubectl set image daemonsets fluentd -elasticsearch fluentd -

```bash
elasticsearch=ikubernetes/filebeat:5.6.6 -alpine -n kube-system
```

这个镜像启动 pod会有问题，主要是演示 daemonset 如何在命令行更新 pod


