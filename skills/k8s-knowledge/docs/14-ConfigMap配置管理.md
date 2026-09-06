配置管理中心 configmap

**1.1 Configmap 概述**
**1.1.1 什么是Configmap ？**
Configmap 是k8s中的资源对象， 用于保存非机密性的配置的， 数据可以用 key/value
键值对的形式保存，也可通过文件的形式保存 。

**1.1.2 Configmap 能解决哪些问题 ？**

 我们在部署服务的时候，每个服务都有自己的配置文件，如果一台服务器上部署多个
服务：nginx、tomcat、apache等，那么这些配置都存在这个节点上， 假如一台服务
器不能满足线上高并发的要求，需要对服务器扩容，扩容之后的服务器还是需要部署
多个服务 ：nginx、tomcat、apache，新增加的服务器上还是要管理这些服务的配置 ，
如果有一个服务出现问题， 需要修改配置文件， 每台物理节点上的配置都需要修改，
这种方式肯定满足不了线上 大批量的配置变更 要求。 所以，k8s中引入了 Configmap
资源对象，可以当成 volume挂载到pod中，实现统一的配置管理 。

**1、Configmap是k8s中的资源，  相当于配置文件，可以 有一个或者多个 Configmap ；**
**2、Configmap 可以做成 Volume，k8s pod启动之后，通过  volume 形式映射到容器内**
部指定目录上；
**3、容器中应用程序按照原有方式读取容器特定目录上的配置文件。**
**4、在容器看来，配置文件就像是打包在容器内部特定目录，整个过程对应用没有任何**
侵入。

**1.1.3 Configmap 应用场景**
**1、使用k8s部署应用，当你将应用配置写进代码中，更新配置时也需要打包镜像，**
configmap 可以将配置信息和 docker镜像解耦 ，以便实现镜像的可移植性和可复用
性，因为一个 configMap 其实就是一系列配置信息的集合，可直接注入到 Pod中给容
器使用。configmap 注入方式有两种，一种将 configMap 做为存储卷，一种是将
configMap 通过env中configMapKeyRef 注入到容器中 。

**2、使用微服务架构的话，存在多个服务共用配置的情况，如果每个服务中单独一份配**
置的话，那么更新配置就很麻烦，使用 configmap 可以友好的进行配置共享。

**1.1.4 局限性**
ConfigMap 在设计上不是用来保存大量数据的。在 ConfigMap中保存的数据不可超过 1
MiB。如果你需要保存超出此尺寸限制的数据， 可以考虑挂载存储卷或者使用独立的数
据库或者文件服务。

**1.2 Configmap 创建方法**

**1.2.1 命令行直接创建**
直接在命令行中指定 configmap 参数创建， 通过--from-literal 指定参数

```bash
[root@xianchaomaster1  ~]# kubectl create configmap tomcat -config --from-
literal=tomcat_port=8080 --from-literal=server_name=myapp.tomcat.com
[root@xianchaomaster1  ~]# kubectl describe configmap tomcat -config
Name:         tomcat -config
Namespace:    default
Labels:       <none>
Annotations:  <none>
Data
====
server_name:
----
myapp.tomcat.com
tomcat_port:
----
8080
Events:  <none>
```

**1.2.2 通过文件创建**
通过指定文件创建一个 configmap ，--from-file=<文件>

```bash
[root@xianchaomaster1  ~]# vim nginx.conf
server {
  server_name www.nginx.com;
  listen 80;
  root /home/nginx/www /
}
#定义一个 key是www，值是nginx.conf中的内容
[root@xianchaomaster1  ~]# kubectl create configmap www -nginx --from-
file=www=./nginx.conf
[root@xianchaomaster1  ~]# kubectl describe configmap www -nginx
Name:         www -nginx
Namespace:    default
Labels:       <none>
Annotations:  <none>

Data
====
www:
----
server {
  server_name www.nginx.com;

   listen 80;
  root /home/nginx/www/
}
```

**1.2.3 指定目录创建 configmap**

```bash
[root@xianchaomaster1  ~]# mkdir test -a
[root@xianchaomaster1  ~]# cd test -a/
[root@xianchaomaster1  test-a]# cat my -server.cnf
server-id=1
[root@xianchaomaster1  test-a]# cat my -slave.cnf
server-id=2
#指定目录创建 configmap
[root@xianchaomaster1  test-a]# kubectl create configmap mysql -config --
from-file=/root/test -a/
#查看configmap 详细信息
[root@xianchaomaster1  test-a]# kubectl describe configmap mysql -config
Name:         mysql -config
Namespace:    default
Labels:       <none>
Annotations:  <none>
Data
====
my-server.cnf:
----
server-id=1
my-slave.cnf:
----
server-id=2
Events:  <none>
```

**1.2.4 编写configmap 资源清单 YAML文件**

```bash
[root@xianchaomaster1  mysql]# cat mysql -configmap.yaml
```

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mysql
  labels:
    app: mysql
data:
  master.cnf: |
    [mysqld]
    log-bin
```

```bash
     log_bin_trust_function_creators=1
    lower_case_table_names=1
  slave.cnf: |
    [mysqld]
    super-read-only
    log_bin_trust_function_creators=1
```

**1.3 使用Configmap**
**1.3.1 通过环境变量引入： 使用configMapKeyRef**

```bash
#创建一个存储 mysql配置的configmap
[root@xianchaomaster1  ~]# cat mysql -configmap.yaml
```

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mysql
  labels:
    app: mysql
data:
    log: "1"
    lower: "1"
```

```bash
[root@xianchaomaster1  ~]# kubectl apply -f mysql-configmap.yaml
#创建pod，引用Configmap 中的内容
[root@xianchaomaster1  ~]# cat mysql -pod.yaml
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mysql -pod
spec:
  containers:
  - name: mysql
    image: busybox
    command: [ "/bin/sh", " -c", "sleep 3600" ]
    env:
    - name: log_bin   # 定义环境变量 log_bin
      valueFrom:
        configMapKeyRef:
          name: mysql     # 指定configmap 的名字
          key: log # 指定configmap 中的key
    - name: lower   # 定义环境变量 lower
      valueFrom:
        configMapKeyRef:
          name: mysql

           key: lower
  restartPolicy: Never
#更新资源清单文件
```

```bash
[root@xianchaomaster1  ~]# kubectl apply -f mysql-pod.yaml
[root@xianchaomaster1  ~]# kubectl exec -it mysql-pod -- /bin/sh
/ # printenv
log_bin=1
lower=1
```
**1.3.2 通过环境变量引入： 使用envfrom**

```bash
[root@xianchaomaster1  ~]# cat mysql -pod-envfrom.yaml
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mysql -pod-envfrom
spec:
  containers:
  - name: mysql
    image: busybox
    imagePullPolicy: IfNotPresent
    command: [ "/bin/sh", " -c", "sleep 3600" ]
    envFrom:
    - configMapRef:
       name: mysql     # 指定configmap 的名字
  restartPolicy: Never

#更新资源清单文件
```

```bash
[root@xianchaomaster1  ~]# kubectl apply -f mysql-pod-envfrom.yaml
[root@xianchaomaster1  ~]# kubectl exec -it mysql -pod-envfrom -- /bin/sh
/ # printenv
lower=1
log=1
```

**1.3.3 把configmap 做成volume，挂载到 pod**

```bash
[root@xianchaomaster1  ~]# cat mysql -configmap.yaml
```

```yaml
apiVersion: v1
kind: Config Map
metadata:
  name: mysql
  labels:
    app: mysql
data:
    log: "1"
    lower: "1"

     my.cnf: |
      [mysqld]
```

```bash
      Welcome= xianchao
[root@xianchaomaster1  ~]# kubectl apply -f mysql-configmap.yaml
[root@xianchaomaster1  ~]# cat mysql -pod-volume.yaml
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mysql -pod-volume
spec:
  containers:
  - name: mysql
    image: busybox
    command: [ "/bin/sh"," -c","sleep 3600" ]
    volumeMounts:
    - name: mysql -config
      mountPath: /tmp /config
  volumes:
  - name: mysql -config
    configMap:
      name: mysql
  restartPolicy: Never
```

```bash
[root@xianchaomaster1  ~]# kubectl apply -f mysql-pod-volume.yaml
[root@xianchaomaster1  ~]# kubectl exec -it mysql -pod-volume -- /bin/sh
/ # cd /tmp/config/
/tmp/config # ls
log    lower    my.cnf
```

**1.4 Configmap 热更新**

```bash
[root@xianchaomaster 1~]# kubectl edit configmap mysql
```
把logs: “1” 变成log: “2”

保存退出

```bash
[root@xianchaomaster 1~]# kubectl exec -it mysql -pod-volume -- /bin/sh
/ # cat /tmp/config/log
2
#发现log值变成了 2，更新生效了
```

> **注意：**
更新 ConfigMap 后：
使用该 ConfigMap 挂载的 Env 不会同步更新

使用该 ConfigMap 挂载的 Volume 中的数据需要一段时间（实测大概 10秒）才能同
步更新


