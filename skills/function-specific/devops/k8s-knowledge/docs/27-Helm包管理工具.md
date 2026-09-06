

**1、Helm介绍**
官网：https://v3.helm.sh/zh/docs/

https://helm.sh/
helm 官方的chart站点：
https://hub.kubeapps.com/

Helm是kubernetes 的包管理工具， 相当于linux环境下的 yum/apg-get命令。

Helm的首要目标一直是让 “从零到Kubernetes” 变得轻松。无论是 运维、开发人员、经验丰富的 DevOps
工程师，还是刚刚入门的学生， Helm的目标是让大家在两分钟内就可以在 Kubernetes 上安装应用程序。

Helm可以解决的问题：运维人员写好资源文件模板
                 交给开发人员填 写参数即可

Helm中的一些概念 ：
（1）helm：命令行客户端工具，主要用于 Kubernetes 应用中的chart的创建、打包、发布和管理。
（2）Chart：helm程序包，一系列用于描述 k8s资源相关文件的集合 ，比方说我们部署 nginx，需要
deployment 的yaml，需要service 的yaml，这两个清单文件就是一个 helm程序包，在 k8s中把这些
yaml清单文件叫做 chart图表。
vlues.yaml 文件为模板中的文件赋值，可以实现我们自定义安装
如果是chart开发者需要自定义模板，如果是 chart使用者只需要修改 values.yaml 即可

repository ：存放chart图表的仓库，提供部署 k8s应用程序需要的那些 yaml清单文件

chart--->通过values.yaml 这个文件赋值 -->生成release 实例
helm也是go语言开发的

（3）Release：基于Chart的部署实体，一个 chart被Helm运行后将会生成对应的一个 release；将在
k8s中创建出真实运行的资源对象。

总结：
helm把kubernetes 资源打包到一个 chart中，制作并完成各个 chart和chart本身依赖关系并利用
chart仓库实现对外分发，而 helm还可通过 values.yaml 文件完成可配置的发布，如果 chart版本更新
了，helm自动支持滚更更新机制，还可以一键回滚，但是不是适合在生产环境使用，除非具有定义自制
chart的能力。

helm属于kubernetes 一个项目：
下载地址：
https://github.com/helm/helm/releases

 找Linux amd64这个checksum 的，下载之后传到机器即可，目前 Helm最新稳定版本是 3.6.3，这个压缩
包我已经下载了，在课件，大家可以直接从课件传到自己机器，解压即可。

**2、Helm v3版本变化**
2019年11月13日，Helm团队发布 Helmv3的第一个稳定版本。

该版本主要变化如下：
架构变化：
**1、Helm服务端Tiller被删除**
**2、Release 名称可以在不同命名空间重用**
**3、支持将 Chart推送至Docker镜像仓库中**
**4、使用JSONSchema 验证chartvalues**

**3、安装Helm v3**
K8s版本支持的各个 helm版本对照表：

https://helm.sh/zh/docs/topics/version_skew/

```bash
[root@xianchaomaster1 ~]# tar zxvf helm -v3.6.3-linux-amd64.tar.gz
[root@xianchaomaster1 ~]# mv linux -amd64/helm /usr/bin/

#查看helm版本：
[root@xianchaomaster1 ~]# helm version
version.BuildInfo{Version:"v3.6.3", GitCommit:"d506314abfb5d21419df8c7e7e68012379db2354",
GitTreeState:"clean", GoVersion:"go1.16.5"}
```

**4、配置国内 存放chart仓库的地址**
阿里云仓库（ https://kubernetes.oss -cn-hangzhou.aliyuncs.com/charts ）
官方仓库（ https://hub.kubeapps.com/charts/incubator ）官方chart仓库，国内 可能无法访问。
微软仓库（ http://mirror.azure.cn/kubernetes/charts/ ）这个仓库推荐，基本上官网有的 chart
这里都有 ，国内可能无法访问。

```bash
#添加阿里云的 chart仓库
[root@xianchaomaster1 ~]# helm repo add aliyun https://kubernetes.oss -cn-
hangzhou.aliyuncs.com/charts
#显示如下：
"aliyun" has been added to your repositories

 #添加bitnami 的chart仓库

 [root@xianchaomaster1 ~]# helm repo add bitnami https://charts.bitnami.com/bitnami

#更新chart仓库
[root@xianchaomaster1 ~]#  helm repo update

#查看配置的 chart仓库有哪些
[root@xianchaomaster1 ~]# helm repo list
NAME    URL
aliyun  https://kubernetes.oss -cn-hangzhou.aliyuncs.com/charts
bitnami https://charts.bitnami.com/bitnami

#删除chart仓库地址
[root@xianchaomaster1 ~]# helm repo remove aliyun
"aliyun" has been removed from your repositories

#重新添加阿里云的 chart仓库
[root@xianchaomaster1 ~]# helm repo add aliyun https://kubernetes.oss -cn-
hangzhou.aliyuncs.com/charts
#更新chart仓库
[root@xianchaomaster1 ~]# helm repo update

#从指定chart仓库地址搜索 chart
[root@xianchaomaster1 ~]# helm search repo aliyun
```

**5、Helm基本使用**
**5.1 搜索和下载 Chart**

```bash
#查看阿里云 chart仓库中的 memcached
[root@xianchaomaster1 ~]# helm search repo aliyun |grep memcached
aliyun/mcrouter                0.1.0         0.36.0        Mcrouter is a
aliyun/memcached               2.0.1                       Free & open

#查看chart信息
[root@xianchaomaster1 ~]# helm show chart  aliyun/memcached
```

```yaml
apiVersion: v1
description: Free & open source, high -performance, distributed memory object caching
  system.
home: http://memcached.org/
icon: https://uploa d.wikimedia.org/wikipedia/en/thumb/2/27/Memcached.svg/1024px -
Memcached.svg.png

 keywords:
- memcached
- cache
maintainers:
- email: gtaylor@gc -taylor.com
  name: Greg Taylor
name: memcached
sources:
- https://github.com/docker -library/memcached
version: 2.0.1

#下载chart包到本地
```

```bash
[root@xianchaomaster1 ~]#  helm pull  aliyun/memcached
[root@xianchaomaster1 ~]# tar zxvf memcached -2.0.1.tgz
[root@xianchaomaster1 ~]# cd memcached
[root@xianchaomaster1 memcached]# ls
Chart.yaml  README.md  templates  values.yaml
```

Chart.yaml: chart 的基本信息，包括版本名字之类
templates: 存放k8s的部署资源模板，通过渲染变量得到部署文件
values.yaml ：存放全局变量， templates 下的文件可以调用

```bash
[root@xianchaomaster1 memcached]# cd templates/
[root@xianchaomaster1 templates]# ls
_helpers.tpl  NOTES.txt  pdb.yaml  statefulset.yaml  svc.yaml
```

_helpers.tpl      存放能够复用的模板
NOTES.txt         为用户提供一个关于 chart部署后使用说明的文件
**5.2 部署chart**
**5.2.1 helm部署memcached 服务**

```bash
#安装memcached 的Chart
[root@xianchaonode1 ~]# docker load -i memcache_1_4_36.tar.gz
#修改statefulset.yaml 文件
[root@xianchaomaster1 ~]# cd memcached
[root@xianchaomaster1 memcached]# cat templates/statefulset.yaml
```

apiVersion 后面的value值变成apps/v1

spec下添加selector 字段
  selector:
    matchLabels:
        app: {{ template "memcached.fullname" . }}
        chart: "{{ .Chart.Name }} -{{ .Chart.Version }}"
        release: "{{ .Release.Name }}"
        heritage: "{{ .Release.Service }}"

#删除affinity 亲和性配置

```bash
[root@xianchaomas ter1 memcached]# helm install memcached ./
NAME: memcached
LAST DEPLOYED: Fri Jul 16 07:58:54 2021
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
Memcached can be accessed via port 11211 on the following DNS name from within your cluster:
memcached -memcached.default.svc.cluster.local

If you'd like to test your instance, forward the port locally:

  export POD_NAME=$(kubectl get pods --namespace default -l "app=memcached -memcached" -o
jsonpath="{.items[0].metadata.name}")
  kubectl port -forward $POD_NAME 11211

In another tab, attempt to set a key:

  $ echo -e 'set mykey 0 60 5 \r\nhello\r' | nc localhost 11211

You should see:

  STORED

#验证memcache 是否部署成功：
[root@xianchaomaster1 memcached]# kubectl get pods
NAME                               READY   STATUS    RESTARTS   AGE
memcached -memcached -0              1/1     Running   0          56s
memcached -memcached -1              1/1     Running   0          50s
memcached -memcached -2              1/1     Running   0          37s

[root@xianchaomaster1 memcached]# yum install nc -y
```
测试memecached 服务是否正常：

```bash
[root@xianchaomaster1 memcached]#  export POD_NAME=$(kubectl get pods --namespace default -l
"app=memcached -memcached" -o jsonpath="{.items[0].metadata.name}")
[root@xianchaomaster1 me mcached]#  kubectl port -forward $POD_NAME 11211

[root@xianchaomaster1 memcached]# echo -e 'set mykey 0 60 5 \r\nhello\r' | nc localhost 11211
```
**5.3 release 相关操作**

```bash
#查看release 发布状态
[root@xianchaomaster1 memcached]# helm list
NAME      NAMESPACE  REVISION  UPDATED                                 STATUS   CHART
 APP VERSION
memcached  default   1        2021-07-16 08:04:44.172578607 +0800 CST  deployed  memcached -
2.0.1

#删除release
[root@xianchaomaster1 memcached]# helm delete memcached
release "mem cached" uninstalled

#删除release 会把release 下对应的资源也删除
[root@xianchaomaster1 memcached]# kubectl get pods
```
memecached 的pod也被删除了

**6、自定义 Chart模板**
**6.1 自定义一个 Chart**
当我们安装好 helm之后我们可以开始自定义 chart，那么我们需要先创建出一个模板如下：

```bash
[root@xianchaomaster1 ~]# helm create myapp
[root@xianchaomaster1 ~]# cd myapp/

 [root@xianchaomaster1 myapp]# yum install tree -y

[root@xianchaomaster1 myapp]# tree ./
./
├── charts   #用于存放所依赖的子 chart
├── Chart.yaml   # 描述这个  Chart 的相关信息、包括名字、描述信息、版本等

├── templates   #模板目录，保留创建 k8s的资源清单文件
│   ├── deployment.yaml   #deployment 资源的go模板文件
│   ├── _helpers.tpl   # # 模板助手文件，定义的值可在模板中使用

│   ├── hpa.yaml  #水平pod自动扩缩容 go模板文件
│   ├── ingress.yaml   #七层代理 go模板文件
│   ├── NOTES.txt
│   ├── serviceaccount.yaml
│   ├── service.yaml   #service的go模板文件
│   └── tests
│       └── test -connection.yaml
└── values.yaml    #模板的值文件，这些值会在安装时应用到  GO 模板生成部署文件
```

**6.2 Chart.yaml编写规则**

```bash
[root@xianchaomaster1 myapp]# cat Chart.yaml
```

```yaml
apiVersion: v 2
name: myapp
description: A Helm chart for Kubernetes
version: 0.0.1
appVersion: " latest"
type: application
maintainer:
- name: xianchao
appVersion: "1.16.0"

```
解释说明： Chart.yaml 文件主要用来描述对应 chart的相关属性信息，其中 apiVersion 字段用于描述对
应chart使用的api版本，默认是 v2版本；name字段用于描述对应 chart的名称； description 字段用
于描述对应 chart的说明简介； type字段用户描述对应 chart是应用程序还是库文件，应用程序类型的
chart，它可以运行为一个 release，但库类型的 chart不能运行为 release，它只能作为依赖被
application 类型的chart所使用； version 字段用于描述对应 chart版本；appVersion 字段用于描述对
应chart内部程序的版本信息；

**6.3 go模板文件渲染**

```bash
[root@xianchaomaster1 myapp]# cat templates/deployment.yaml
```

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "myapp.fullname" . }}
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "myapp.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      {{- with .Values.podAnnotations }}
      annotations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      labels:
        {{- include "myapp.selectorLabels" . | nindent 8 }}
    spec:
      {{- with .Values.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      serviceAccountName: {{ include "myapp.serviceAccountName" . }}
      securityContext:
        {{- toYaml .Values.podSecurityContext | nindent 8 }}
      containers:
        - name: {{ .Chart.Name }}
          securityContext:
            {{- toYaml .Values.securityContext | nindent 12 }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag |
default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: 80
              protocol: TCP

           livenessProbe:
            httpGet:
              path: /
              port: http
          readinessProbe:
            httpGet:
              path: /
              port: http
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
      {{- with .Values.nodeSelector }}
      nodeSelector:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.affinity }}
      affinity:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.tolerations }}
      tolerations:
        {{- toYaml . | nindent 8 }}
      {{- end }}

```
解释·：该部署清单模板文件，主要用 go模板语言来写的，其中 {{ include "myapp.fullname" . }} 就表
示取myapp的全名； {{ .Values.image.repository }} 这段代码表示读取当前目录下的 values文件中的
image.repository 字段的值； {{ .Values.image.tag | default .Chart.AppVersion }} 表示对于 values
文件中image.tag 的值或者读取 default.chart 文件中的 AppVersion 字段的值；简单讲 go模板就是应用
对应go模板语法来定义关属性的的值；一般都是从 values.yaml 文件中加载对应字段的值作为模板文件
相关属性的值 。

nindent 4 ：表示首行缩进 4个字母
TRUNC（NUMBER）表示截断数字
**6.4 values.yaml文件编写**

```bash
[root@xianchaomaster1 myapp]# cat values.yaml
# Default values for myapp.
# This is a YAML -formatted file.
# Declare variables to be passed into your templates.
replicaCount: 2
image:
  repository: nginx
  pullPolicy: IfNotPresent
  # Overrides the image tag whose default is the chart appVersion.

   tag: ""

imagePullSecrets: []
nameOverride: ""
fullnameOverride: ""

serviceAccount:
  # Specifies whether a service account should be creat ed
  create: true
  # Annotations to add to the service account
  annotations: {}
  # The name of the service account to use.
  # If not set and create is true, a name is generated using the fullname template
  name: ""

podAnnotations: {}

podSecurityCont ext: {}
  # fsGroup: 2000

securityContext: {}
  # capabilities:
  #   drop:
  #   - ALL
  # readOnlyRootFilesystem: true
  # runAsNonRoot: true
  # runAsUser: 1000

service:
```

```yaml
  type: ClusterIP
  port: 80

ingress:
  enabled: false
  className: ""
  annotations: {}
    # kubernetes.io/ingress.class: nginx
    # kubernetes.io/tls -acme: "true"
  hosts:
    - host: chart -example.local
      paths:
        - path: /
          pathType: ImplementationSpecific

   tls: []
  #  - secretName: chart-example-tls
  #    hosts:
  #      - chart-example.local

resources: {}
  # We usually recommend not to specify default resources and to leave this as a conscious
  # choice for the user. This also increases chances charts run on environments with little
  # resources, such as Minikube. If you do want to specify resources, unc omment the
following
  # lines, adjust them as necessary, and remove the curly braces after 'resources:'.
  # limits:
  #   cpu: 100m
  #   memory: 128Mi
  # requests:
  #   cpu: 100m
  #   memory: 128Mi

autoscaling:
  enabled: false
  minReplicas: 1
  maxReplicas: 100
  targetCPUUtilizationPercentage: 80
  # targetMemoryUtilizationPercentage: 80

nodeSelector: {}

tolerations: []

affinity: {}

```
解释：比如我们要引用 values.yaml 文件中的 image字段下的 tag字段的值，我们可以在模板文件中写成
{{ .Values.image.tag }}；如果在命令行使用 --set选项来应用我们可以写成  image.tag ；修改对应的
值可以直接编辑对应 values.yaml 文件中对应字段的值，也可以直接使用 --set 指定对应字段的对应值即
可；默认情况在命令行使用 --set选项给出的值，都会直接被替换，没有给定的值，默认还是使用
values.yaml 文件中给定的默认值；

6.5部署release

```bash
[root@xianchaomaster1 myapp]# helm install  myapp .
NAME: myapp
LAST DEPLOYED: Fri Jul 16 12:35:10 2021
NAMESPACE: default

 STATUS: deployed
REVISION: 1
NOTES:
1. Get the application URL by running these commands:
  export POD_NAME=$(kubectl get pods --namespace default -l
"app.kubernetes.io/name=myapp,app.kubernetes.io/inst ance=myapp" -o
jsonpath="{.items[0].metadata.name}")
  export CONTAINER_PORT=$(kubectl get pod --namespace default $POD_NAME -o
jsonpath="{.spec.containers[0].ports[0].containerPort}")
  echo "Visit http://127.0.0.1:8080 to use your application"
  kubectl --namespace default port -forward $POD_NAME 8080:$CONTAINER_PORT

[root@xianchaomaster1 myapp]# kubectl get pods
NAME                               READY   STATUS    RESTARTS   AGE
myapp-86bdd79db4 -cn6kj             1/1     Running   0          28s
myapp-86bdd79db4 -lwshh             1/1     Running   0          28s
```

**7. Helm常用命令演示**
**7.1 检查values语法格式**

```bash
[root@xianchaomaster1 myapp]# helm lint /root/myapp/
==> Linting /root/myapp/
[INFO] Chart.yaml: icon is recommended

1 chart(s) linted, 0 chart(s) failed

#通过上面可看到语法正确
```
**7.2 upgrade 升级release**

```bash
[root@xianchaomaster1 myapp]# kubectl get svc
NAME                  TYPE        CLUSTER -IP      EXTERNAL -IP   PORT(S)     AGE
myapp                 ClusterIP   10.106.231.94   <none>        80/TCP

[root@xianchaomaster1 myapp]# helm upgrade --set service.type="NodePort" myapp .
Release "myapp" has been upgraded. Happy Helming!
NAME: myapp
LAST DEPLOYED: Fri Jul 16 13:12:11 2021
NAMESPACE: default
STATUS: deployed
REVISION: 2
NOTES:
1. Get the application URL by running these commands:

   export NODE_PORT=$(kubectl get --namespace default -o jsonpath="{.spec.ports[0].nodePort}"
services myapp)
  export NODE_IP=$(kubectl get no des --namespace default -o
jsonpath="{.items[0].status.addresses[0].address}")
  echo http://$NODE_IP:$NODE_PORT

[root@xianchaomaster1 myapp]# kubectl get svc
NAME                  TYPE        CLUSTER -IP      EXT ERNAL-IP   PORT(S)        AGE
myapp                 NodePort    10.106.231.94   <none>        80:30334/TCP   5m2s

#通过上面可以看到 Service的type类型已经变成了 nodePort
```

**7.3 回滚release**

```bash
#查看历史版本
[root@xianchaomaster1 myapp]# helm history myapp
REVISION  UPDATED                  STATUS     CHART       APP VERSION  DESCRIPTION
1        Fri Jul 16 13:07:32 2021  superseded  myapp-0.0.1 latest      Install
complete
2        Fri Jul 16 13:12:11 2021  deployed   myapp-0.0.1 latest      Upgrade
complete

#把myapp回滚到版本 1
[root@xianchaomaster1 myapp]# helm rollback myapp 1
[root@xianchaomaster1 myapp]# kubectl get svc
NAME                  TYPE        CLUSTER -IP      EXTERNAL -IP   PORT(S)     AGE
myapp                 ClusterIP   10.106.231.94   <none>        80/TCP

#可以看到 service 已经完成回滚了
```

**7.4 打包Chart**

```bash
[root@xianchaomaster1 myapp]# helm package /root/myapp/
Successfully packaged chart and saved it to: /root/myapp/myapp -0.0.1.tgz
```

**7.5 操作release 命令**
升级release 版本
helm upgrade

回滚release 版本
helm rollback

 创建一个 release 实例
helm install

卸载release
helm uninstall

查看历史 版本
helm history

**7.6 操作Chart命令**

#检查Chat的语法
helm lint

chart相关的
查看chart的详细信息
helm inspect

把chart下载下来
helm pull

把chart打包
helm package


