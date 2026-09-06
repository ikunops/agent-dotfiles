k8s持久化存储

在k8s中为什么要做持久化存储？
 在k8s中部署的应用都是以 pod容器的形式运行的， 假如我们部署 MySQL、Redis等数据库 ，需要
对这些数据库产生的数据做备份 。因为Pod是有生命周期的，如果 pod不挂载数据卷， 那pod被删除或
重启后这些数据会随之消失，如果想要长久的保留这些数据就要用到 pod数据持久化存储。

**1、k8s持久化存储 ：emptyDir**

```bash
#查看k8s支持哪些存储
[root@xianchaomaster1  ~]# kubectl explain pods.spec.volumes
```

```yaml
KIND:     Pod
VERSION:  v1
RESOURCE: volumes <[]Object>
DESCRIPTION:
     List of volumes that can be mounted by containers belonging to the pod.
     More info: https://kubernetes.io/docs/concepts/storage/volumes
     Volume represents a named volume in a pod that may be accessed by any
     container in the pod.
FIELDS:
   awsElasticBlockStore  <Object>
   azureDisk  <Object>
   azureFile  <Object>
   cephfs <Object>
   cinder <Object>
   configMap  <Object>
   csi <Object>
   downwardAPI  <Object>
   emptyDir  <Object>
   ephemeral  <Object>
   fc <Object>
   flexVolume  <Object>
   flocker <Object>
   gcePersistentDisk  <Object>
   gitRepo <Object>
   glusterfs  <Object>
   hostPath  <Object>
   iscsi <Object>
   name <string> -required -
   nfs <Object>
   persistentVolumeClaim  <Object>
   photonPersistentDisk  <Object>
   portworxV olume <Object>
   projected  <Object>
   quobyte <Object>
   rbd <Object>
   scaleIO <Object>
   secret <Object>
   storageos  <Object>
   vsphereVolume  <Object>
```

常用的如下：
emptyDir
hostPath
nfs
persistentVolumeClaim
glusterfs
cephfs
configMap
secret

我们想要使用存储卷，需要经历如下步骤
**1、定义pod的volume，这个volume指明它要关联到哪个存储上的**
**2、在容器中要使用 volumemounts 挂载对应的存储**

经过以上两步才能 正确的使用存储卷

emptyDir 类型的Volume是在Pod分配到Node上时被创建， Kubernetes 会在Node上自动分配一个
目录，因此无需指定宿主机 Node上对应的目录文件。  这个目录的初始内容为空，当 Pod从Node上移除
时，emptyDir 中的数据会被永久删除。 emptyDir Volume 主要用于某些应用 程序无需永久保存的临时目
录，多个容器的共享目录等 。

#创建一个 pod，挂载临时目录 emptyDir

Emptydir 的官方网址：
https://kubernetes.io/docs/concepts/storage/volumes#emptydir

```bash
[root@xianchaomaster1  ~]# cat emptydir.yaml
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod -empty
spec:
  containers:
  - name: container -empty
    image: nginx
    volumeMounts:
    - mountPath : /cache
      name: cache -volume
  volumes:
  - emptyDir:
     {}
    name: cache -volume

#更新资源清单文件
```

```bash
[root@xianchaomaster1  ~]# kubectl apply -f emptydir.yaml
pod/pod-empty created
```

查看本机临时目录存在的位置，可用如下方法：

```bash
#查看pod调度到哪个节点
[root@xianchaomaster1  ~]# kubectl get pods -o wide | grep empty
pod-empty      1/1     Running     0       10.244.209.152   xianchaonode1

#查看pod的uid
[root@xianchaomaster1  ~]# kubectl get pods pod -empty -o yaml | grep uid
uid: 38d60544 -8591-468d-b70d-2a66df3a1cf6

#登录到xianchao node1上
[root@xianchaonode1  ~]# tree /var/lib/kubelet/pods/38d60544 -8591-468d-b70d-2a66df3a1cf6
/var/lib/kubelet/pods/38d60544 -8591-468d-b70d-2a66df3a1cf6
├── containers
│   └── container -empty
│       └── c9e06d01
├── etc-hosts
├── plugins
│   └── kubernetes.io~empty -dir
│       ├── cache-volume
│       │   └── ready
│       └── wrapped_default -token-cq5qp
│           └── ready
└── volumes
    ├── kubernetes.io~empty -dir
    │   └── cache-volume
    │       └── aa
    └── kubernetes.io~secret
        └── default-token-cq5qp
            ├── ca.crt -> ..data/ca.crt
            ├── namespace -> ..data/namespace
            └── token -> ..data/token

12 directories, 7 files
```

由上可知，临时目录在本地的 /var/lib/kubelet/pods/38d60544 -8591-468d-b70d-
2a66df3a1cf6/volumes/kubernetes.io~empty -dir/cache -volume/下

**2、k8s持久化存储： hostPath**

 hostPath Volume 是指Pod挂载宿主机上的目录或文件。  hostPath Volume 使得容器可以使用宿主
机的文件系统进行存储 ，hostpath （宿主机路径） ：节点级别的存储卷，在 pod被删除，这个存储卷还是
存在的，不会被删除，所以只要同一个 pod被调度到同一个节点上来，在 pod被删除重新被调度到这个
节点之后，对应的数据依然是存在的。

```bash
#查看hostPath 存储卷的用法
[root@xianchaomaster1  ~]# kubectl explain pods.spec.volumes.hostPath
```

```yaml
KIND:     Pod
VERSION:  v1
RESOURCE: hostPath <Object>
DESCRIPTION:
     HostPath represents a pre -existing file or directory on the host machine
     that is directly exposed to the container. This is generally used for
     system agents or other privileged things that are allowed to see the host
     machine. Most containers will NOT need this. More info:
     https://kubernetes.io/docs/concepts/storage/volumes#hostpath
     Represents a host path mapped into a pod. Host path volumes do not support
     ownership management or SELinux relabeling.
FIELDS:
   path <string> -required -
   type <string>

#把tomcat.tar.gz 上传到xianchaonode2 和xianchaonode1 上，手动解压 ：
```

```bash
[root@xianchaonode2  ~]# docker load -i tomcat.tar.gz
[root@xianchaonode1  ~]# docker load -i tomcat.tar.gz

#创建一个 pod，挂载hostPath 存储卷
[root@xianchaomaster1  ~]# cat hostpath.yaml
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: test -hostpath
spec:
  containers:
  - image: nginx
    name: test -nginx
    volumeMounts:
    - mountPath: /test -nginx
      name: test -volume
  - image: tomcat:8.5 -jre8-alpine
    name: test -tomcat
    volumeMounts:
    - mountPath: /test -tomcat

       name: test -volume
  volumes:
  - name: test -volume
    hostPath:
      path: /data1
      type: DirectoryOrCreate

```
> **注意：**
# DirectoryOrCreate 表示本地有/data1目录，就用本地的，本地没有就会在 pod调度到的节点自
动创建一个

```bash
#更新资源清单文件
[root@xianchaomaster1  ~]# kubectl apply -f hostpath.yaml
pod/test -hostpath created

#查看pod调度到了哪个 物理节点
[root@xianchaomaster1  ~]# kubectl get pods -o wide | grep hostpath
test-hostpath      2/2     Running        10.244.209.153   xianchaonode1
#由上面可以知道 pod调度到了 xianchaonode1 上，登录到 xianchaonode1 机器，查看是否在这台机
```
器创建了存储目录

```bash
[root@xianchaonode1  ~]# ll /data1/
total 0
#上面可以看到 已经创建了存储目录 /data1，这个/data1会作为pod的持久化存储目录

#在xianchaonode1 上的/data1下创建一个目录
[root@xianchaonode1  ~]# cd /data1/
[root@xianchaonode1  data1]# mkdir aa
#测试存储卷是否可以正常使用 ,登录到nginx容器

[root@xianchaomaster1  ~]# kubectl exec -it test-hostpath -c test-nginx -- /bin/bash
root@test -hostpath:/# cd /test -nginx/
#/test-nginx/目录存在，说明已经把宿主机目录挂载到了容器里
root@test -hostpath:/test -nginx# ls
aa

#测试存储卷是否可以正常使用 ,登录到tomcat容器
[root@xianchaomaster1  ~]# kubectl exec -it test-hostpath -c test-tomcat -- /bin/bash
root@test -hostpath:/usr/local/tomcat# cd /test -tomcat/
#/test-tomcat/目录存在，说明已经把宿主机目录挂载到了容器里
root@test -hostpath:/test -tomcat# ls
aa

#通过上面测试可以看到， 同一个pod里的test-nginx和test-tomcat这两个容器是共享存储卷
```

 的。

hostpath存储卷缺点：
单节点
pod删除之后重新创建必须调度到同一个 node节点，数据才不会丢失

可以用分布式存储：
nfs，cephfs，glusterfs

**3、k8s持久化存储： nfs**
上节说的 hostPath 存储，存在单点故障， pod挂载hostPath 时，只有 调度到同一个节点，数据才不
会丢失。那可以使用 nfs作为持久化存储 。
**1、搭建nfs服务**
以k8s的控制节点作为 NFS服务端

```bash
[root@xianchaomaster1  ~]# yum install nfs -utils -y
#在宿主机 创建NFS需要的共享目录
[root@xianchaomaster1  ~]# mkdir /data/volumes -pv
mkdir: created directory ‘/data’
mkdir: created directory ‘/data/volumes’
#配置nfs共享服务器上的 /data/volumes 目录
[root@xianchaomaster1  ~]# systemctl start nfs
[root@xianchaomaster1  ~]# vim /etc/exports
/data/volumes 192.168. 40.0/24(rw,no_root_squash)
#no_root_squash: 用户具有根目录的完全管理访问权限
#使NFS配置生效
[root@xianchaomaster1  ~]# exportfs -arv
exporting 192.168.40.0 /24:/data/volumes
[root@xianchaomaster1  ~]# service nfs start
Redirecting to /bin/systemctl start nfs.service
#设置成开机自启动
[root@xianchaomaster1  ~]# systemctl enable nfs
#查看nfs是否启动成功
[root@xianchaomaster1  ~]# systemctl status nfs
   Active: active
```
看到nfs是active，说明nfs正常启动了
#xianchaonode2 和xianchaonode1 上也安装 nfs驱动
yum install nfs -utils -y
systemctl enable nfs

在xianchaonode1 上手动挂载试试：

```bash
[root@xianchaonode1 ~]# mkdir /test
[root@xianchaonode1 ~]# mount 192.168.40.180:/data/volumes /test/

 [root@xianchaonode1 ~]# df -h
192.168.40.180:/data/volumes   50G  5.2G   45G  11% /test

#nfs可以被正常挂载
#手动卸载：
[root@xianchaonode1 ~]# umount /test

#创建Pod，挂载NFS共享出来的目录
```

Pod挂载nfs的官方地址：
https://kubernetes.io/zh/docs/concepts/storage/volumes/

```bash
[root@xianchaomaster1  ~]# cat nfs.yaml
```

```yaml
apiVersion: v1
kind: Pod
metadata:
 name: test -nfs-volume
spec:
 containers:
 - name: test -nfs
   image: nginx
   imagePullPolicy: IfNotPresent
   ports:
   - containerPort: 80
     protocol: TCP
   volumeMounts:
   - name: nfs -volumes
     mountPath: /usr/share/nginx/html
 volumes:
 - name: nfs -volumes
   nfs:
    path: /data/volu mes
server: 192.168. 40.180

```
> **注：path:  /data/volumes #nfs 的共享目录**
server：192.168.40.180 是xianchaomaster1 机器的ip，这个是安装 nfs服务的地址

```bash
#更新资源清单文件
[root@xianchaomaster1  ~]# kubectl apply -f nfs.yaml
#查看pod是否创建成功
[root@xianchaomaster1  volumes]# kubectl get pods -o wide | grep nfs
test-nfs-volume         1/1     Running   10.244.187.108   xianchaonode2

 #登录到nfs服务器，在共享目录创建一个 index.html
root@xianchaomaster1  volumes]# pwd
/data/volumes
[root@xianchaomaster1  volumes]# cat index.html
Hello, Everyone
My name is xianchao

#请求pod，看结果
[root@xianchaomaster1  volumes]# curl 10.244.187.108
hello, Welcome to xianchao
#通过上面可以看到，在共享目录创建的 index.html 已经被pod挂载了
#登录到pod验证下
[root@xianchaomaster1  volumes]# kubectl exec -it test-nfs-volume  -- /bin/bash
root@test -nfs-volume:/# cat /usr/share/nginx/html/index.html
Hello, Everyone
My name is xianchao

#上面说明挂载 nfs存储卷成功了， nfs支持多个客户端挂载，可以创建 多个pod，挂载同一个 nfs
```
服务器共享出来的目录 ；但是nfs如果宕机了，数据也就丢失了，所以需要使用分布式存储，常见的分
布式存储有 glusterfs 和cephfs

**4、k8s持久化存储：  PVC**

参考官网 :
https://kubernetes.io/docs/concepts/storage/persistent -volumes/#access -modes

**4.1.1 k8s PV是什么？**
PersistentVolume （PV）是群集中的一块存储，由管理员配置或使用存储类动态配置。  它是集群中
的资源，就像 pod是k8s集群资源一样。  PV是容量插件，如 Volumes，其生命周期独立于使用 PV的任
何单个pod。

**4.1.2 k8s PVC是什么？**
PersistentVolumeClaim （PVC）是一个持久化存储卷，我们在创建 pod时可以定义这个类型的存储
卷。 它类似于一个 pod。 Pod消耗节点资源， PVC消耗PV资源。 Pod可以请求特定级别的资源（ CPU和
内存） 。 pvc在申请pv的时候也可以请求特定的大小和访问模式（例如，可以一次读写或多次只读） 。

**4.1.3 k8s PVC和PV工作原理**
PV是群集中的资源。  PVC是对这些资源的请求。
PV和PVC之间的相互作用遵循以下生命周期：

（1）pv的供应方式

 可以通过两种方式配置 PV：静态或动态。

静态的：
集群管理员创建了许多 PV。它们包含可供群集用户使用的实际存储的详细信息。它们存在于
Kubernetes API 中，可供使用。

动态的：
当管理员创建的静态 PV都不匹配用户的 PersistentVolumeClaim 时，群集可能会尝试为 PVC专门动
态配置卷。此配置基于 StorageClasses ，PVC必须请求存储类，管理员必须创建并配置该类，以便进行
动态配置。

（2）绑定
用户创建 pvc并指定需要的资源和访问模式。在找到可用 pv之前，pvc会保持未绑定状态

（3）使用
a）需要找一个存储服务器，把它划分成多个存储空间；
b）k8s管理员可以把这些存储空间定义成多个 pv；
c）在pod中使用pvc类型的存储卷之前需要先创建 pvc，通过定义需要使用的 pv的大小和对应的
访问模式，找到合适的 pv；
d）pvc被创建之后，就可以当成存储卷来使用了，我们在定义 pod时就可以使用这个 pvc的存储
卷
e）pvc和pv它们是一一对应的关系， pv如果被pvc绑定了，就不能被其他 pvc使用了；
f）我们在创建 pvc的时候，应该确保和底下的 pv能绑定，如果没有合适的 pv，那么pvc就会处
于pending 状态。

（4）回收策略
当我们创建 pod时如果使用 pvc做为存储卷，那么它会和 pv绑定，当删除 pod，pvc和pv绑定就会
解除，解除之后和 pvc绑定的pv卷里的数据需要怎么处理，目前，卷可以保留，回收或删除 ：
Retain
Recycle （不推荐使用， 1.15可能被废弃了）
Delete
**1、Retain**
当删除pvc的时候， pv仍然存在，处于 released 状态，但是它不能被其他 pvc绑定使用，里面的数
据还是存在的，当我们下次再使用的时候，数据还是存在的，这个是默认的回收策略

Delete
删除pvc时即会从 Kubernetes 中移除PV，也会从相关的外部设施中删除存储资产

**4.1.4 创建pod，使用pvc作为持久化存储卷**
**1、创建nfs共享目录**

```bash
#在宿主机创建 NFS需要的共享目录
[root@xianchaomaster1  ~]# mkdir /data/volume_test/v{1,2,3,4,5,6,7,8,9,10} -p

 #配置nfs共享宿主机上的 /data/volume _test/v1..v10目录
[root@xianchaomaster1  ~]# cat /etc/exports
/data/volumes 192.168.40.0 /24(rw,no_root_squash)
/data/volume_test/v1 192.168.40.0 /24(rw,no_root_squash)
/data/volume_test/v2 192.168.40.0 /24(rw,no_root_squash)
/data/volume_test/v3 192.168.40.0 /24(rw,no_root_squash)
/data/volume_test/v4 192.168.40.0 /24(rw,no_root_squash)
/data/volume_test/v5 192.168.40.0 /24(rw,no_root_squash)
/data/volume_test/v6 192.168.40.0 /24(rw,no_root_squash)
/data/volume_test/v7 192.168.40.0 /24(rw,no_root_squash)
/data/volume_test/v8 192.168.40.0 /24(rw,no_root_squash)
/data/volume_test/v9 192.168.40.0 /24(rw,no_root_squash)
/data/vol ume_test/v10 192.168.40.0 /24(rw,no_root_squash)
#重新加载配置，使配置成效
[root@xianchaomaster1  ~]# exportfs -arv
```

**2、如何编写 pv的资源清单文件**

```bash
#查看定义 pv需要的字段
[root@xianchaomaster1  ~]# kubectl explain pv
```

```yaml
KIND:     PersistentVolume
VERSION:  v1
DESCRIPTION:
     PersistentVolume (PV) is a storage resource provisioned by an
     administrator. It is analogous to a node. More info:
     https://kubernetes.io/docs/concepts/storage/persistent -volumes
FIELDS:
   apiVersion  <string>s
   kind <string>
   metadata  <Object>
   spec <Object>

#查看定义 nfs类型的pv需要的字段
```

```bash
[root@xianchaomaster1  ~]# kubectl explain pv.spec.nfs
```

```yaml
KIND:     PersistentVolume
VERSION:  v1
RESOURCE: nfs <Object>
FIELDS:
   path <string> -required -
   readOnly  <boolean>
   server <string> -required-

```
**3、创建pv**

 参考：https://kubernetes.io/zh/docs/concepts/storage/persistent -volumes/#reclaiming

```bash
[root@xianchaomaster1  ~]# cat pv.yaml
```

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name:  v1
spec:
  capacity:
    storage: 1Gi   #pv的存储空间容量
  accessModes: ["ReadWriteOnce"]
  nfs:
    path: /data/volume_test/v1  #把nfs的存储空间创建成 pv
    server: 192.168. 40.180     #nfs服务器的地址
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name:  v2
spec:
  capacity:
      storage: 2Gi
  accessModes: ["ReadWriteMany"]
  nfs:
    path: /data/volume_test/v2
    server: 192.168.40.180
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name:  v3
spec:
  capacity:
      storage: 3Gi
  accessModes: ["ReadOnlyMany"]
  nfs:
    path: /data/volume_test/v3
    server: 192.168.40.180
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name:  v4

 spec:
  capacity:
      storage: 4Gi
  accessModes: ["ReadWriteOnce","ReadWriteMany"]
  nfs:
    path: /data/volume_test/v4
    server: 192.168.40.180
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name:  v5
spec:
  capacity:
      storage: 5Gi
  accessModes: ["ReadWriteOnce","ReadWriteMany"]
  nfs:
    path: /data/volume_test/v5
    server: 192.168.40.180
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name:  v6
spec:
  capacity:
      storage: 6Gi
  accessModes: ["ReadWriteOnce","ReadWriteMany"]
  nfs:
    path: /data/volume_test/v6
    server: 192.168.40.180
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name:  v7
spec:
  capacity:
      storage: 7Gi
  accessModes: ["ReadWriteOnce","ReadWriteMany"]
  nfs:
    path: /data/volume_test/v7
    server: 192.168.40.180
```

 ---

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name:  v8
spec:
  capacity:
      storage: 8Gi
  accessModes: ["ReadWriteOnce","ReadWriteMany"]
  nfs:
    path: /data/volume_test/v8
    server: 192.168.40.180
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name:  v9
spec:
  capacity:
      storage: 9Gi
  accessModes: ["ReadWriteOnce","ReadWriteMany"]
  nfs:
    path: /data/volume_test/v9
    server: 192.168.40.180
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name:  v10
spec:
  capacity:
      storage: 10Gi
  accessModes: ["ReadWriteOnce","ReadWriteMany"]
  nfs:
    path: /data/volume_test/v10
server: 192.168.40.180

#更新资源清单文件
```

```bash
[root@xianchaomaster1  ~]# kubectl apply -f pv.yaml
persistentvolume/v1 created
persistentvolum e/v2 created
persistentvolume/v3 created
persistentvolume/v4 created

 persistentvolume/v5 created
persistentvolume/v6 created
persistentvolume/v7 created
persistentvolume/v8 created
persistentvolume/v9 created
persistentvolume/v10 create d

#查看pv资源
[root@xianchaomaster1  ~]# kubectl get pv
NAME   CAPACITY   ACCESS MODES   RECLAIM POLICY    STATUS
v1       1Gi              RWO              Retain           Available
v10      10Gi             RWO,RWX        Retain           Available
v2       2Gi               RWX             Retain           Available
v3       3Gi               ROX              Retain           Available
v4       4Gi               RWO,RWX        Retain           Available
v5       5Gi               RWO,RWX        Retain           Available
v6       6Gi               RWO,RWX        Retain           Available
v7       7Gi               RWO,RWX        Retain           Available
v8       8Gi               RWO,RWX        Retain           Available
v9       9Gi               RWO,RWX        Retain           Available
#STATUS是Available ，表示pv是可用的
```

**4、创建pvc，和符合条件的 pv绑定**

```bash
[root@xianchaomaster1  ~]# cat pvc.yaml
```

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my -pvc
spec:
  accessModes: ["ReadWriteMany"]
  resources:
    requests:
      storage: 2Gi

#更新资源清单文件
```

```bash
[root@xianchaomaster1  ~]# kubectl apply -f pvc.yaml
persistentvolumeclaim/my -pvc created
#查看pv和pvc
[root@xianchaomaster1  ~]# kubectl get pv
NAME  CAPACITY  ACCESS MODES  RECLAIM POLICY  STATUS    CLAIM
v1      1Gi        RWO               Retain           Available
v10     10Gi       RWO,RWX         Retain           Available
v2       2Gi        RWX              Retain           Bound       default/my -pvc

 v3       3Gi         ROX             Retain           Available
v4       4Gi        RWO,RWX        Retain           Available
v5       5Gi        RWO,RWX        Retain           Available
v6       6Gi        RWO,RWX        Retain           Available
v7       7Gi        RWO,RWX        Retain           Available
v8       8Gi        RWO,RWX        Retain           Available
v9       9Gi        RWO,RWX        Retain           Available
#STATUS是Bound，表示这个 pv已经被my-pvc绑定了
[root@xianchaomaster1  ~]# kubectl get pvc
NAME     STATUS   VOLUME   CAPACITY   ACCESS MODES
my-pvc     Bound       v2         2Gi         RWX
```
pvc的名字-绑定到pv-绑定的是 v2这个pv-pvc可使用的容量是 2G

**5、创建pod，挂载pvc**

```bash
[root@xianchaomaster1  ~]# cat pod_pvc.yaml
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod -pvc
spec:
  containers:
  - name: nginx
    image: nginx
    volumeMounts:
    - name: nginx -html
      mountPath: /usr/share/nginx/html
  volumes:
  - name: nginx -html
    persistentVolumeClaim:
      claimName: my -pvc
#更新资源清单文件
```

```bash
[root@xianchaomaster1  ~]# kubectl apply -f pod_pvc.yaml
pod/pod-pvc created
#查看pod状态
[root@xianchaom aster1 ~]# kubectl get pods | grep pod -pvc
pod-pvc                              1/1     Running     0          27s
#通过上面可以看到 pod处于running 状态，正常运行
```

> **注：使用pvc和pv的注意事项**
**1、我们每次创建 pvc的时候，需要事先有划分好的 pv，这样可能不方便，那么可以在创建 pvc的时**
候直接动态创建一个 pv这个存储类， pv事先是不存在的
**2、pvc和pv绑定，如果使用默认的回收策略 retain，那么删除 pvc之后，pv会处于released 状**
态，我们想要继续使用这个 pv，需要手动删除 pv，kubectl delete pv pv_name ，删除pv，不会删除 pv

 里的数据，当我们重新创建 pvc时还会和这个最匹配的 pv绑定，数据还是原来数据，不会丢失 。

**5、 k8s存储类： storageclass**
上面介绍的 PV和PVC模式都是需要先创建好 PV，然后定义好 PVC和pv进行一对一的 Bond，但是如
果PVC请求成千上万，那么就需要创建成千上万的 PV，对于运维人员来说维护成本很高， Kubernetes 提
供一种自动创建 PV的机制，叫 StorageClass ，它的作用就是创建 PV的模板。 k8s集群管理员通过创建
storageclass 可以动态生成一个存储卷 pv供k8s pvc使用。

每个StorageClass 都包含字段 provisioner ，parameters 和reclaimPolicy 。

具体来说， StorageClass 会定义以下两部分：
**1、PV的属性 ，比如存储的大小、类型等；**
**2、创建这种 PV需要使用到的存储插件，比如 Ceph、NFS等**

有了这两部分信息， Kubernetes 就能够根据用户提交的 PVC，找到对应的 StorageClass ，然后
Kubernetes 就会调用  StorageClass 声明的存储插件，创建出需要的 PV。

```bash
#查看定义 的storageclass 需要的字段
[root@xianchaomaster1  ~]# kubectl explain storageclass
```

```yaml
KIND:     StorageClass
VERSION:  storage.k8s.io/v1
DESCRIPTION:
     StorageClass describes the parameters for a class of storage for which
     PersistentVolumes can be dynamically provisioned.
     StorageClasses are non -namespaced; the name of the storage class according
     to etcd is in ObjectMeta.Name.
FIELDS:
   allowVolumeExpansion  <boolean>
   allowedTopologies  <[]Object>
   apiVersi on <string>
   kind <string>
   metadata  <Object>
   mountOptions  <[]string>
   parameters  <map[string]string>
   provisioner  <string> -required -
   reclaimPolicy  <string>
   volumeBindingMode  <string>

```
provisioner ：供应商，storageclass 需要有一个供应者，用来确定我们使用什么样的存储来创 建
pv，常见的provisioner 如下

（https://kubernetes.io/zh/docs/concepts/storage/storage -classes/ ）：

provisioner 既可以由内部供应商 提供，也可以由外部供应商提供，如果是外部供应商可以参考
https://github.com/kubernetes -incubator/external -storage/ 下提供的方法创建 。

https://github.com/kubernete s-sigs/sig -storage-lib-external -provisioner

以NFS为例，要想使用 NFS，我们需要一个 nfs-client的自动装载程序， 称之为provisioner ，这
个程序会使用我们已经配置好的 NFS服务器自动创建持久卷，也就是自动帮我们创建 PV。

reclaimPolicy ：回收策略

allowVolumeExpansion ：允许卷扩展， PersistentVolume 可以配置 成可扩展。将此功能设置为 true
时，允许用户通过编辑相应的  PVC 对象来调整卷大小。当基础存储类的 allowVolumeExpansion 字段设
置为 true 时，以下类型的卷支持卷扩展。

> **注意：此功能仅用于扩容卷，不能用于缩小卷。**

**5.1 安装nfs provisioner ，用于配合存储类动态生成 pv**
#把nfs-subdir-external -provisioner.tar.gz 上传到xianchaonode2 和xianchaonode1 上，手
动解压

```bash
[root@xianchaonode2  ~]# docker load -i nfs-subdir-external -provisioner.tar.gz
[root@xianchaonode1  ~]# docker load -i nfs-subdir-external -provisioner.tar.gz

[root@xianchaomaster1  nfs]# cat serviceaccount.yaml
```

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: nfs -provisioner

```

```bash
[root@xianchaomaster1  nfs]# kubectl apply -f serviceaccount.yaml
serviceaccount/nfs -provisioner created
```

扩展：什么是 sa？
sa的全称是serviceaccount 。
serviceaccount 是为了方便 Pod里面的进程调用 Kubernetes API 或其他外部服务而设计的 。

指定了serviceaccount 之后，我们把 pod创建出来了，我们在使用这个 pod时，这个 pod就有了
我们指定的账户的权限了 。

**2、对sa授权**

```bash
[root@xianchaomaster1 ]# kubectl create clusterrolebinding nfs-provisioner -
clusterrolebinding --clusterrole=cluster -admin --serviceaccount=default:nfs -
provisioner
```

**3、安装nfs-provisioner 程序**

```bash
[root@xianchaomaster1  ~]# mkdir /data/nfs_pro  -p
#把/data/nfs_pr o变成nfs共享的目录
[root@xianchaomaster1  ~]# cat /etc/exports
/data/volumes 192.168.40.0 /24(rw,no_root_squash)
/data/volume_test/v1 192.168.40.0 /24(rw,no_root_squash)
/data/volume_test/v2 192.168.40.0 /24(rw,no_root_squash)
/data/volume_test/v3 192.168.40.0 /24(rw,no_root_squash)
/data/volume_test /v4 192.168.40.0 /24(rw,no_root_squash)
/data/volume_test/v5 192.168.40.0 /24(rw,no_root_squash)
/data/volume_test/v6 192.168.40.0 /24(rw,no_root_squash)
/data/volume_test/v7 192.168.40.0 /24(rw,no_root_squash)
/data/volume_test/v8 192.168.40.0 /24(rw,no_root_s quash)
/data/volume_test/v9 192.168.40.0 /24(rw,no_root_squash)
/data/volume_test/v10 192.168.40.0 /24(rw,no_root_squash)

 /data/nfs_pro 192.168.40.0 /24(rw,no_root_squash)

[root@xianchaomaster1  ~]# exportfs -arv
exporting 192.168.40.0 /24:/data/nfs_pro
exporting 192.168.40.0 /24:/data/volume_test/v10
exporting 192.168.40.0 /24:/data/volume_test/v9
exporting 192.168.40.0 /24:/data/volume_test/v8
exporting 192.168.40.0 /24:/data/volume_test/v7
exporting 192.168.40.0 /24:/data/volume_test/v6
exporting 192.168.40.0 /24:/data/volume_test/v5
exporting 192.168.40.0 /24:/data/volume_test/v4
exporting 192.168.40.0 /24:/data/volume_test/v3
exporting 192.168.40.0 /24:/data/volume_test/v2
exporting 192.168.40.0 /24:/data/volume_test/v1
exporting 192.168.40.0 /24:/data/volumes

[root@xianchaomaster1  ~]# cat nfs -deployment.yaml
```

```yaml
kind: Deployment
apiVersion: apps/v1
metadata:
  name: nfs -provisioner
spec:
  selector:
    matchLabels:
       app: nfs -provisioner
  replicas: 1
  strategy:
    type: Recreate
  template:
    metadata:
      labels:
        app: nfs -provisioner
    spec:
      serviceAccount: nfs -provisioner
      containers:
        - name: nfs -provisioner
          image: registry.cn -beijing.aliyuncs.com/mydlq/nfs -subdir-external-
provisioner:v4.0.0
          volumeMounts:
            - name: nfs -client-root
              mountPath: /persistentvolumes
          env:
            - name: PROVISIONER_NAME

               value: example.com/nfs
            - name: NFS_SERVER
              value: 192.168.40.180
            - name: NFS_PATH
              value: /data/nfs_pro
      volumes:
        - name: nfs -client-root
          nfs:
            server: 192.168.40.180
            path: /data/nfs_pro
#更新资源清单文件
```

```bash
[root@xianchaomaster1  ~]# kubectl apply -f nfs-deployment.yaml
deployment.apps/nfs -provisioner created
#查看nfs-provisioner 是否正常运行
[root@xianchaomaster1  nfs]# kubectl get pods | grep nfs
nfs-provisioner -cd5589cfc -pjwsq      1/1     Running
```

**5.2 创建storageclass ，动态供给 pv**

```bash
[root@xianchaomaster1 ]# cat nfs -storageclass.yaml
```

```yaml
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: nfs
provisioner: example.com/nfs
```

```bash
[root@xianchaomaster1 ]# kubectl apply -f nfs-storageclass.yaml
#查看storageclass 是否创建成功
[root@xianchaomaster1  nfs]# kubectl get storageclass
NAME   PROVISIONER       RECLAIMPOLICY   VOLUMEBINDINGMODE
nfs       example.com/nfs         Delete          Immediate
#显示内容如上，说明 storageclass 创建成功了
```

> **注意：provisioner 处写的example.com/nfs 应该跟安装 nfs provisioner 时候的env下的**
PROVISIONER_NAME 的value值保持一致 ，如下：
env:
    - name: PROVISIONER_NAME
     value: example.com/nfs

**5.3 创建pvc，通过storageclass 动态生成pv**

```bash
[root@xianchaomaster1 ]# cat claim.yaml
```

```yaml
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: test -claim1

 spec:
  accessModes:  ["ReadWriteMany"]
  resources:
    requests:
      storage: 1Gi
  storageClassName:  nfs
```

```bash
[root@xianchaomaster1 ]# kubectl apply -f claim.yaml
persistentvolumeclaim/test -claim1 created
#查看是否动态生成了 pv，pvc是否创建成功 ，并和pv绑定
[root@xianchaomaster1  nfs]# kubectl get pvc

#通过上面可以看到 test-claim1的pvc已经成功创建了，绑定的 pv是pvc-da737fb7 -3ffb-43c4-
```
a86a-2bdfa7f201e2 ，这个pv是由storageclass 调用nfs provisioner 自动生成的 。

步骤总结：
**1、供应商：创建一个 nfs provisioner**
**2、创建storageclass ，storageclass 指定刚才创建的供应商**
**3、创建pvc，这个pvc指定storageclass**

**5.4 创建pod，挂载storageclass 动态生成的 pvc：test-claim1**

```bash
[root@xianchaomaster1 ]# cat read -pod.yaml
```

```yaml
kind: Pod
apiVersion: v1
metadata:
  name: read -pod
spec:
  containers:
  - name: read -pod
    image: nginx
    volumeMounts:
      - name: nfs -pvc
        mountPath: /usr/share/nginx/html
  restartPolicy: "Never"
  volumes:
    - name: nfs -pvc
      persistentVolumeClaim:
        claimName: test -claim1
#更新资源清单文件
```

```bash
[root@xianchaomaster1  nfs]# kubectl apply -f read-pod.yaml

 pod/read -pod created
#查看pod是否创建 成功
[root@xianchaomaster1  nfs]# kubectl get pods | grep read
read-pod                             1/1     Running     0
```


