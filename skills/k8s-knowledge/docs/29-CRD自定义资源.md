 目录
Kubernetes 二次开发之自定义 CRD 资源 ................................ ................................ ........................  2
**3.9 自定义 CRD 资源 ................................ ................................ ................................ ...............  2**
**3.9.1 通过 crd资源创建自定义资源，即自定义一个 Restful API ： ................................ .. 2**
**3.9.2 创建自定义资源的对象  ................................ ................................ ..............................  4**

Kubernetes 二次开发之自定义 CRD 资源

**3.9 自定义 CRD 资源**

**3.9.1 通过 crd资源创建自定义资源，即自定义一个 Restful API ：**
cat  crontab -crd.yaml

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: crontabs.stable.example.com
spec:
  group: stable.example.com
  versions:
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                cronSpec:
                  type: string
                image:
                  type: string
                replicas:
                  type: integer

   scope: Namespaced
  names:
    plural: crontabs
    singular: crontab
    kind: CronTab
    shortNames:
    - ct

```
Yaml文件注解：
metadata .name 是用户自定义资源中自己自定义的一个名字。一般我们建议使用 “顶级域
名.xxx.APIGroup ”这样的格式 ，名称必须与下面的 spec .Group 字段匹配，格式为 :
<plural>.<group>

spec 用于指定该  CRD 的 group 、version 。比如在创建  Pod 或者 Deploym ent 时，它的
group 可能为  apps/v1 或者 apps/v1beta1 之类，这里我们也同样需要去定义  CRD 的 group 。

group: stable.example.com  #组名称
  versions:
    - name: v1
      #指定组下的版本

served: true
#每个版本都可以通过服务标志启用 /禁用
storage: true
#必须将一个且只有一个版本标记为存储版本。

 scope: Namespaced
#指定 crd资源作用范围在命名空间或集群

names 指的是它的  kind 是什么，比如  Deployment 的 kind 就是 Deployment ，Pod 的
kind 就是 Pod，这里的  kind 被定义为了 CronTab

plural 字段就是一个昵称，比如当一些字段或者一些资源的名字比较长时，可以用该字段自定义一
些昵称来简化它的长度；

 singular: crontab
# 在CLI(shell 界面输入的参数 )上用作别名并用于显示的单数名称

    shortNames:
    - ct

# 短名称允许短字符串匹配 CLI上的资源，就是能通过 kubectl 在查看资源的时候使用该资源的简
名称来获取。

创建自定义 contab 资源
$ kubectl apply  -f crontab -crd.yaml

查看 crd
kubectl get crd

查看自定义 crontab 资源的信息
$ kubectl get crontab

**3.9.2 创建自定义资源的对象**
根据 crd对象资源创建出来的 RESTful API，来创建 crontab 类型资源对象
cat  my-crontab.yaml

```yaml
apiVersion: "stable.example.com/v1"
kind: CronTab
metadata:
  name: my -new-cron -object
spec:
  cronSpec: " * * * * * *"
image: busybox

kubectl apply -f my-crontab.yaml

#查看资源
kubectl get CronTab
```
显示如下：
NAME                 AGE
my-new-cron -object   9s
提示：可以看到对应类型资源已经创建成功；以上示例只是单纯的 crd的使用示例，没有任何实质的
作用。

作业：
示例：部署 mongodb -aperator
**1、项目 地址**
https://github.com/mongodb/mongodb -kubernetes -operator.git

找到 0.5.0,看这个版本对应使用

示例：部署 mongodb -aperator

**1、项目 地址**
https://github.com/mongodb/mongodb -kubernetes -operator.git

把课件里的压缩包传上来，手动解压
unzip mongodb -kubernetes -operator -0.5.0.zip

**2、创建名称空间 mongodb ，并进入到 mongodb -kubernetes -operator 目录应用 crd资源，**
创建自定义资源类型

```bash
[root@ xianchaomaster1  ~] kubectl create ns mongodb

[root@ xianch aomaster1  ~]# cd mongodb -kubernetes -operator -0.5.0

[root@ xianchaomaster1  mongodb -kubernetes -operator -0.5.0]# kubectl apply -f
deploy/crds/mongodb.com_mongodbcommunity_crd.yaml

#查看 mongodb 是否创建成功
kubectl get crd/mongodbcommunity.mongodb.com
```

**3、安装 operator**

```bash
[root@ xianchaomaster1  mongodb -kubernetes -operator -0.5.0]# kubectl apply -f
deploy/operator/ -n mongodb
```

提示： mongodb -kubernetes -operator 这个项目是将自定义控制器和自定义资源类型分开实现
的；其 operator 只负责创建和监听对应资源类型的变化，在资源有变化时，实例化为对应资源对
象，并保持对应资源对象状态吻合用户期望状态；上述四个清单中主要是创建了一个 sa账户，并对
对应的 sa用户授权；

验证：查看 operator 是否正常运行

```bash
[root@ xianchaomaster1  mongodb -kubernetes -operator -0.5.0]# kubectl get pods -n
mongodb
NAME                                           READY   STATUS    RESTARTS
AGE
mongodb -kubernetes -operator -7f8c55db45 -tmpk5   1/1     Running   0
44s
```

验证：使用自定义资源类型创建一个 mongodb 副本集集群

```bash
[root@ xianchaomaster1  mongod b-kubernetes -operator -0.5.0]# cat
deploy/crds/mongodb.com_v1_mongodbcommunity_cr.yaml

[root@ xianchaomaster1  mongodb -kubernetes -operator -0.5.0]# kubectl apply -f
deploy/crds/mongodb.com_v1_mongodbcommunity_cr.yaml -n mongodb

 [root@ xianchaomaster1  mongodb -kubernetes -operator -0.5.0]# kubectl get pods -n
mongodb
NAME                                           READY   STATUS    RESTARTS
AGE
example -mongodb -0                              0/2     Pending   0          66s
```

提示：这里可以看到对应 pod 处于 pending 状态；
  查看 pod 详细信息

```bash
[root@ xianchaomaster1  mongodb -kubernetes -operator -0.5.0]# kubectl describe
pod/example -mongodb -0 -n mongodb|grep -A 10 "Events"
Events:
  Type     Reason            Age   From               Message
  ----     ------             ----  ----               -------
  Warning  FailedScheduling  116s  default -scheduler  0/2 nodes are available: 2 pod
has unbound immediate PersistentVolumeClaims.
  Warning  FailedScheduling  116s  default -scheduler  0/2 nodes are available: 2 pod
has unbound immediate PersistentVolumeClaims.
```

 提示：这里提示没有可以用的 pvc；
  删除 mongodb 名称空间下 pvc
kubectl get pvc -n mongodb

kubectl delete pvc --all -n mongodb

 创建 pv和pvc

```bash
[root@ xianchaomaster1  ~]# cat pv -demo.yaml
```

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: nfs -pv-v1
  labels:
    app: example -mongodb -svc
spec:
  capacity:
    storage: 1Gi
  volumeMode: Filesystem
  accessModes: ["ReadWriteOnce","ReadWriteMany","ReadOnlyMany"]
  persistentVolumeReclaimPolicy: Retain
  mountOptions:
  - hard
  - nfsvers=4.1
  nfs:

     path: /data/p1
    server: 192.168.40.180
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: nfs -pv-v2
  labels:
    app: example -mongodb -svc
spec:
  capac ity:
    storage: 1Gi
  volumeMode: Filesystem
  accessModes: ["ReadWriteOnce","ReadWriteMany","ReadOnlyMany"]
  persistentVolumeReclaimPolicy: Retain
  mountOptions:
  - hard
  - nfsvers=4.1
  nfs:
    path: /data/p2
    server: 192.168.40.180
---

apiVersion: v1
kind: PersistentVolume
metadata:
  name: nfs -pv-v3
  labels:
    app: example -mongodb -svc
spec:
  capacity:
    storage: 1Gi
  volumeMode: Filesystem
  accessModes: ["ReadWriteOnce","ReadWriteMany","ReadOnlyMany"]
  persistentVolumeReclaimPolicy: Retain
  mountOptions:
  - hard
  - nfsvers=4.1
  nfs:
    path: /data/p3
    server: 192.168.40.180

```

```bash
[root@ xianchaomaster1  ~]# mkdir /data/p1

 [root@ xianchaomaster1  ~]# mkdir /data/p2
[root@ xianchaomaster1  ~]# mkdir /data/p3
[root@xianchaomaster1  ~]# cat /etc/exports
/data/v1  *(rw,no_root_squash)
/data/p1  *(rw,no_root_squash)
/data/p2  *(rw,no_root_squash)
/data/p3  *(rw,no_root_squash)

[root@ xianchaomaster1  ~]# exportfs -arv
[root@ xianchaomaster1  ~]# kubectl apply -f pv-demo.yaml
```

创建 pvc资源

```bash
[root@ xianchaomaster1  ~]# cat pvc -demo.yaml
```

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data -volume -example -mongodb -0
  namespace: mongodb
spec:
  accessModes:
    - ReadWriteMany
  volumeMode: Filesystem
  resources:
    requests:
      storage: 500Mi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data -volume -example -mongodb -1
  namespace: mongodb
spec:
  accessModes:
    - ReadWriteMany
  volumeMode: Filesystem
  resources:
    requests:
      storage: 500Mi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data -volume -example -mongodb -2

   namespace: mongodb
spec:
  accessModes:
    - ReadWriteMany
  volumeMode: Filesystem
  resources:
    requests:
      storage: 500M

```

```bash
[root@ xianchaomaster1  ~]# kubectl apply -f pvc -demo.yaml
[root@master01 ~]# kubectl get pods -n mongodb
NAME                                                  READY    STATUS     RESTARTS    AGE
example -mongodb -0                              2/2     Running    0          8m
example -mongodb -1                              2/2     Running    0          111s
example -mongodb -2                              2/2     Running    0          48s
mongodb -kubernetes -operator -7d557bcc95 -th8js    1/1     Running    0          9m19s
```


