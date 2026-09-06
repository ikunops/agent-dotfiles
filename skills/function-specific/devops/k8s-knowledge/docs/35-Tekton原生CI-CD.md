目录
kubernetes 原生的 CI-CD工具 Tekton ................................ ................................ ...........................  2
**3.3 什么是 Tekton ？ ................................ ................................ ................................ ...............  2**
**3.4 为什么要用 k8s原生的 CI-CD工具 Tekton ？ ................................ ................................ .. 2**
**3.5 使用 Tekton 自动化发布应用流程  ................................ ................................ .....................  3**
**3.6 安装 Tekton  ................................ ................................ ................................ ......................  3**
**3.7 Tekton 概念 ................................ ................................ ................................ ......................  4**
**3.8 测试 Tekton 构建 CI/CD 流水线  ................................ ................................ .......................  4**
**3.8.1 clone 应用程序代码进行测试，创建一个 task 任务 ................................ ................  4**
**3.8.2 创建 pipelineresource 资源对象  ................................ ................................ ...........  6**
**3.8.3 创建 taskrun 任务................................ ................................ ................................ ... 6**
**3.9 自定义 CRD 资源 ................................ ................................ ................................ ...............  7**
**3.9.1 通过 crd资源创建自定义资源，即自定义一个 Restful API ： ................................ .. 7**
**3.9.2 创建自定义资源的对象  ................................ ................................ ..............................  9**

kubernetes 原生的 CI-CD工具 Tekton

**3.3 什么是 Tekton ？**
Tekton 是一个功能强大且灵活的  Kubernetes 原生开源框架， 是谷歌开源的， 功能强大且灵活，
开源社区也正在快速的迭代和发展壮大 ，主要用于 创建持续集成和交付（ CI/CD ）系统。通过抽象底层实
现细节，用户可以跨多云平台和本地系统进行构建、测试和部署。 另外，基于 kubernetes CRD 定义的
pipeline 流水线也是 Tekton 最重要的特征 。

扩展： CRD 是什么？
知道： 1
不知道： 2

CRD 全称是 CustomResourceDefinition ：
在 Kubernetes 中一切都可视为资源， Kubernetes 1.7 之后增加了对  CRD 自定义资源二次开发
能力来扩展  Kubernetes API ，通过  CRD 我们可以向  Kubernetes API 中增加新资源类型，而不需
要修改  Kubernetes 源码来创建自定义的  API server ，该功能大大提高了  Kubernetes 的扩展能力。
当你创建一个新的 CustomResourceDefinition (CRD) 时，Kubernetes API 服务器将为你指定的每个
版本创建一个新的 RESTful 资源路径，我们可以根据该 api路径来创建一些我们自己定义的类型资源。
CRD 可以是命名空间 的，也可以是集群范围的，由 CRD 的作用域 (scpoe) 字段中所指定的，与现有的内
置对象一样，删除名称空间将删除该名称空间中的所有自定义对象。 customresourcedefinition 本身
没有名称空间，所有名称空间都可以使用。

**3.4 为什么要用 k8s原生的 CI-CD工具 Tekton ？**
持续集成是云原生应用的支柱技术之一，因此在交付基于云原生的一些支撑产品的时候， CICD 是非
常好的方案 。为了满足这种需要，自然而然会想到对 Jenkins(X) 或者 Gitlab 进行集成， 也有创业公司
出来的 一些小工具比如  Argo Rollout 。Tekton 是一款  k8s 原生的应用发布框架，主要用来构建
CI/CD 系统。它原本是  knative 项目里面一个叫做  build -pipeline 的子项目，用来作为  knative -
build 的下一代引擎。然而，随着  k8s 社区里各种各样的需求涌入，这个子项目慢慢成长为一个通用的
框架，能够提供灵活强大的能力去做基于  k8s 的构建发布。 Tekton 其实只提供  Pipeline 这个一个功
能，Pipeline 会被直接映射成  K8s Pod 等 API 资源。 而比如应用发布过程的控制，灰度和上线策
略，都是我们自己编写  K8s Controller 来实现的，也就意味着  Tekton 不会在 K8s 上盖一个 ”大帽子
“，比如我们想看发布状态、日志等是直接通过  K8s 查看这个  Pipeline 对应的  Pod 的状态和日志，
不需要再面对另外一个  API。

Tekton 功能：
1.Kubernetes 原生的Tekton 的所有配置都是使用 CRD 方式进行编写存储的，非常易于检索和使

 用。
2.配置和流程分离 ： Tekton 的Pipeline 和配置可以分开编写，使用名称进行引用。
3.轻量级核心的 Pipeline 非常轻便 ：适合作为组件进行集成，另外也有周边的  Dashboard 、
Trigger 、CLI等工具，能够进一步挖掘其潜力。
4.可复用、组合的  Pipeline 构建方式 ：非常适合在集成过程中对 Pipeline 进行定制。

**3.5 使用 Tekton 自动化发布应用流程**

这里的流程大致是：
**1、用户把需要部署的应用先按照一套标准的应用定义写成  YAML 文件（类似  Helm Chart ）；**
**2、用户把 应用定义  YAML 推送到  Git 仓库里；**
**3、Tekton CD ( 一个 K8s Operator) 会监听到相应的改动，根据不同条件生成不同的  Tekton**
Pipelines ；
Tekton CD 的操作具体分为以下几种情况：
**1、如果 Git 改动里有一个应用  YAML 且该应用不存在，那么将渲染和生成  Tekton Pipelines**
用来创建应用。
**2、如果 Git 改动里有一个应用  YAML 且该应用存在，那么将渲染和生成  Tekton Pipelines 用**
来升级应用。这里我们会根据应用定 义 YAML 里的策略来做升级，比如做金丝雀发布、灰度升级。
**3、如果 Git 改动里有一个应用  YAML 且该应用存在且标记了 “被删除”，那么将渲染和生成**
Tekton Pipelines 用来删除应用。确认应用被删除后，我们才从  Git 里删除这个应用的  YAML 。

**3.6 安装 Tekton**
#把tekton -0-12-0.tar.gz 和busybox -v-1-0.tar.gz 上传到 xianchaonode1 机器上，手动解
压：

```bash
[root@ xianchaonode1 ]# docker load -i tekton -0-12-0.tar.gz
[root@ xianchaonode1 ]# docker load -i busybox -v-1-0.tar.gz
#编写安装 tekton 资源清单文件
[root@ xianchaomaster1  ~]# kubectl apply -f release.yaml
#验证 pod 是否创建成功

 [root@ xianchaomaster1  ~]# kubectl get pods -n tekton -pipelines
NAME                                          READY   STATUS    RESTARTS   AGE
tekton -pipelines -controller -d64889fb9 -9b68f   1/1     Running   0              52s
tekton -pipelines -webhook -7c8664944c -ctsgf     1/1     Running   0            52s

[root@ xianchaomaster1  ~]# kubectl get crd
```
找到下面这些东西，说明创建 crd成功了 ：
pipelineresources.tekton.dev                          2021 -08-21T13:52:16Z
pipelineruns.tekton.dev                               2021 -08-21T13:52:16Z
pipelines.tek ton.dev                                  2021 -08-21T13:52:16Z
taskruns.tekton.dev                                   2021 -08-21T13:52:16Z
tasks.tekton.dev                                      2021 -08-21T13:52:16Z

```bash
[root@ xianchaomaster1  ~]# kubectl api -versi ons
```
看到下面说明 apiversion 创建成功了
tekton.dev/v1alpha1
tekton.dev/v1beta1

**3.7 Tekton 概念**
Tekton  为Kubernetes 提供了多种  CRD 资源对象，可用于定义我们的流水线，主要有以下几个
CRD 资源对象：
1）Task ：表示执行命令的一系列步骤， task 里可以定义一系列的  steps ，例如编译代码、构建镜
像、推送镜像等，每个  step 实际由一个  Pod 里的容器 执行。
2）TaskRun ：task 只是定义了一个模版， taskRun 才真正代表了一次实际的运行，当然你也可以
自己手动创建一个 taskRun ，taskRun 创建出来之后，就会自动触发 task 描述的构建任务。
3）Pipeline ：一组任务，表示一个或多个 task、PipelineResource 以及各种定义参数的集合。
4）PipelineRu n：类似 task 和taskRun 的关系， pipelineRun 也表示某一次实际运行的
pipeline ，下发一个  pipelineRun CRD 实例到  Kubernetes 后，同样也会触发一次  pipeline 的构
建。
5）PipelineResource ：表示 pipeline 输入资源，比如 github 上的源码，或者 pipeline 输出资
源，例如一个容器镜像或者构建生成的 jar包等。

**3.8 测试 Tekton 构建 CI/CD 流水线**
我们测试一个简单的 golang 程序。应用程序代码，测试及 docke rfile 文件可在如下地址获取：

**3.8.1 clone 应用程序代码进行测试，创建一个 task 任务**

```bash
[root@ xianchaomaster1  ~]# cat task -test.yaml
```

```yaml
apiVersion: tekton.dev/v1beta1
kind: Task

 metadata:
  name: test
spec:
  resources:
    inputs:
    - name: repo
      type: git
  steps:
  - name: run -test
    image: golang:1.14 -alpine
    imagePull Policy: IfNotPresent
    workingDir: /workspace/repo
    command: ["go"]
    args: ["test"]
#更新资源清单文件
```

```bash
[root@ xianchaomaster1  ~]# kubectl apply -f task -test.yaml
task.tek ton.dev/test created
#查看 Task 资源
[root@ xianchaomaster1  ~]# kubectl get Task
NAME   AGE
test   23s

 #上面内容解释说明：
```
resources 定义了我们的任务中定义的步骤 中需要 输入的内容，这里我们的步骤需要  Clone 一个
Git 仓库作为  go test  命令的输入。 Tekton 内置了一种  git 资源类型，它会自动将代码仓库  Clone
到 /workspace/$input_name  目录中，由于我们这里 输入被命名成  repo ，所以代码会被  Clone
到 /workspace/repo  目录下面。然后下面的  steps  就是来定义执行运行测试命令的步骤，这里我们直
接在代码的根目录中运行  go test  命令即可，需要注意的是命令和参数需要分别定义。

**3.8.2 创建 pipelineresource 资源对象**
通过上面步骤 我们定义了一个  Task 任务，但是该任务并不会立即执行，我们必须创建一个
TaskRun 引用它并提供所有必需输入的数据才行。这里我们就需要将  git 代码库作为输入，我们必须先
创建一个  PipelineResource 对象来定义输入信息，创建一个名为  pipelineresource.yaml  的资源清
单文件，内容如下所示：

```bash
[root@ xianchaomaster1  ~]# cat pipelineresource.yaml
```

```yaml
apiVersion: tekton.dev/v1alpha1
kind: PipelineResource
metadata:
  name: xuegod -tekton -example
spec:
  type: git
  params:
    - name: url
    - name: revision
      value: master
#更新资源清单文件
```

```bash
[root@ xianchaomaster1  ~]# kubectl apply -f pipelineresource.yaml
```

**3.8.3 创建 taskrun 任务**

```bash
[root@ xianchaomaster1  ~]# cat taskrun.yaml
```

```yaml
apiVersion: tekton.dev/v1beta1
kind: TaskRun
metadata:
  name: testrun
spec:
  taskRef:
    name: test
  resources:
    inputs:
    - name: repo
      resourceRef:
        name: xuegod -tekton -example

#更新资源清单文件
```

```bash
[root@ xianchaomaster1  ~]# kubectl apply -f taskrun.yaml
#上面资源清单文件解释说明
```
这里通过 taskRef 引用上面定义的 Task 和git仓库作为输入， resourceRef 也是引用上面定义的
PipelineResource 资源对象。

```bash
#创建后，我们可以通过查看 TaskRun 资源对象的状态来查看构建状态
[root@ xianchaomaster1  ~]# kubectl get taskrun
NAME      SUCCEEDED   REASON    STARTTIME
testrun      Unknown     Running    6s
[root@ xianchaomaste r1 ~]# kubectl get pods
NAME                READY   STATUS    RESTARTS   AGE
testrun -pod-x9rkn   2/2     Running   0          9s
```
当任务执行完成后，  Pod 就会变成  Completed 状态了：

```bash
[root@ xianchaomaster1  ~]# kubectl get pods
NAME                READY   STATUS      RESTARTS   AGE
testrun -pod-x9rkn   0/2     Completed       0          72s
```

我们可以通过 kubectl  describe 命令来查看任务运行的过程，首先就是通过  initContainer 中的
一个 busybox 镜像将代码  Clone 下来，然后使用任务中定义的镜像来执行命令。当任务执行完成后，
Pod 就会变成  Completed  状态了 ，我们可以查看容器的日志信息来了解任务的执行结果信息 ：

```bash
[root@ xianchaomaster1  ~]# kub ectl logs testrun -pod-x9rkn --all-containers
{"level":"info","ts":1617616592.58145,"caller":"git/git.go:136","msg":"Successfully
c6c2a85091d538a13c44f85bcee9e861c362b0d3 (grafted, HEAD, origin/master) i n path
/workspace/repo"}
{"level":"info","ts":1617616592.6319332,"caller":"git/git.go:177","msg":"Successfully
initialized and updated submodules in path /workspace/repo"}
PASS
ok   _/workspace/repo  0.003s

#通过上面 可以看到我们的测试已经通过了。
```

总结： 我们已经在 Kubernetes 集群上成功安装了  Tekton ，定义了一个  Task ，并通过  YAML 清
单和创建 TaskRun 对其进行了测试。

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

spec 用于指定该  CRD 的 group 、version 。比如在创建  Pod 或者 Deployment 时，它的
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
根据 crd对象资源创建出来的 RESTful API ，来创建 crontab 类型资源对象
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
创建自定 义资源类型

```bash
[root@ xianchaomaster1  ~] kubectl create ns mongodb

[root@ xianchaomaster1  ~]# cd mongodb -kubernetes -operator -0.5.0

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
的；其 operator 只负责创建和监听对应 资源类型的变化，在资源有变化时，实例化为对应资源对
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
[root@ xianchaomaster1  mongodb -kubernetes -operator -0.5.0]# cat
deploy/crds/mongodb.com_v1_mongodbcommunity_cr.yaml

[root@ xianchao master1  mongodb -kubernetes -operator -0.5.0]# kubectl apply -f
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
has unbound  immediate PersistentVolumeClaims.
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
  accessModes: ["Re adWriteOnce","ReadWriteMany","ReadOnlyMany"]
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
  capacity:
    storage: 1Gi
  volumeMode: Filesystem
  accessModes: ["ReadWriteOnce","ReadWriteMany","ReadOnlyMany"]
  persistentVolumeReclaimPolicy: Retain
  mountOptions:
  - hard
  - nfsver s=4.1
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
[root@ xianchaoma ster1  ~]# mkdir /data/p2
[root@ xianchaomaster1  ~]# mkdir /data/p3
[root@ xianchaomaster1  ~]# cat /etc/exports
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


