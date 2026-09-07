配置管理中心 Secret

1 Secret概述
**1.1 Secret是什么？**
上面我们学习的 Configmap 一般是用来存放明文数据的，如配置文件，对于一些敏感
数据，如密码、私钥等数据时，要用 secret类型。

 Secret解决了密码、 token、秘钥等敏感数据的配置问题，而不需要把这些敏感数据
暴露到镜像或者 Pod Spec 中。Secret可以以Volume或者环境变量的方式使用。

要使用 secret，pod 需要引用  secret。Pod 可以用两种方式使用  secret：作为
volume 中的文件被挂载到  pod 中的一个或者多个容器里，或者当  kubelet 为 pod 拉取
镜像时使用。

secret可选参数 有三种:
generic: 通用类型，通常用于存储密码数据。
  tls：此类型仅用于存储私钥和证书。
  docker-registry: 若要保存 docker仓库的认证信息的话，就必须使用此种类型来创
建。

Secret类型：
Service Account ：用于被 serviceaccount 引用。serviceaccout 创建时
Kubernetes 会默认创建对应的  secret。Pod 如果使用了  serviceaccount ，对应的
secret 会自动挂载到  Pod 的 /run/secrets/kubernetes.io/serviceaccount 目录
中。

Opaque：base64编码格式的 Secret，用来存储密码、秘钥等。 可以通过 base64 --
decode解码获得原始数据，因此安全性弱

kubernetes.io/dockerconfigjson ：用来存储私有 docker registry 的认证信息。

**1.2 使用Secret**

**1、通过环境变量引入 Secret**

```bash
#把mysql的root用户的password 创建成secret
[root@xianchaomaster1  ~]# kubectl create secret generic mysql -password --
from-literal=password= xianchao pod**lucky66
[root@xianchaomaster1  ~]# kubectl get secret
NAME                          TYPE                                  DATA
AGE
mysql-password                Opaque                                1
30s
[root@xianchaomaster1  ~]# kubectl describe secret mysql -password
Name:         mysql -password
Namespace:    default
Labels:       <none>
Annotations:  <none>
```

```yaml
Type:  Opaque
Data
====

 password:  20bytes
#password 的值是加密的，
#但secret的加密是一种伪加密，它仅仅是将数据做了 base64的编码.

#创建pod，引用secret
```

```bash
[root@xianchaomaster1  ~]# cat pod -secret.yaml
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod -secret
  labels:
     app: myapp
spec:
  containers:
  - name: myapp
    image: ikubernetes/myapp:v1
    ports:
    - name: http
      containerPort: 80
    env:
     - name: MYSQL_ROOT_PASSWORD   # 它是Pod启动成功后 ,Pod中容器的环境变量
```
名.
       valueFrom:
          secretKeyRef:
            name: mysql -password  # 这是secret的对象名
            key: password      # 它是secret中的key名

```bash
[root@xianchaomaster1  ~]# kubectl apply -f pod-secret.yaml
[root@xianchaomaster1  ~]# kubectl exec -it pod-secret -- /bin/sh
/ # printenv
MYSQL_ROOT_PASSWORD= xianchao pod**lucky66
```

**2、通过volume挂载Secret**

1）创建Secret
手动加密，基于 base64加密

```bash
[root@xianchaomaster1  ~]# echo -n 'admin' | base64
YWRtaW4=
[root@xianchaomaster1  ~]# echo -n 'xianchao 123456f' | base64
eGlhbmNoYW8xMjM0NTZm
```

解码：

```bash
[root@xianchaomaster1  ~]# echo eGlhbmNoYW8xMjM0NTZm   | base64 -d
```

 2）创建yaml文件

```bash
[root@xianchaomaster1  ~]# vim secret.yaml
```

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mysecret
type: Opaque
data:
  username: YWRtaW4=
  password: eGlhbmNoYW8xMjM0NTZm

```

```bash
[root@xianchaomaster1  ~]# kubectl apply -f secret.yaml

[root@xianchaomas ter1]# kubectl describe secret mysecret
Name:         mysecret
Namespace:    default
Labels:       <none>
Annotations:  <none>

```

```yaml
Type:  Opaque

Data
====
password:  15 bytes
username:  5 bytes

```
3）将Secret挂载到Volume中

```bash
[root@xianchaomaster1  ~]# vim pod_secret_volume.yaml
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod -secret-volume
spec:
  containers:
  - name: myapp
    image: registry.cn -beijing.aliyuncs.com/google_registry/myapp:v1
    volumeMounts:
    - name: secret -volume
      mountPat h: /etc/secret
      readOnly: true
  volumes:
  - name: secret -volume

     secret:
      secretName: mysecret

```

```bash
[root@xianchaomaster1  ~]# kubectl apply -f pod_secret_volume.yaml
[root@xianchaomaster1  ~]# kubectl exec -it pod-secret-volume -- /bin/sh
/ # ls /etc/secret
password  username
/ #
/ # cat /etc/secret/username
admin/ #
/ #
/ # cat /etc/secret/password
xianchao 123456f/ #

#由上可见，在 pod中的secret信息实际已经被解密。
```


