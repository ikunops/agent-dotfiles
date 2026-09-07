**1、k8s安全管理：认证、授权、准入控制概述**

 k8s对我们整个系统的认证，授权，访问控制做了精密的设置；对于 k8s集群来说， apiserver 是整
个集群访问控制的唯一入口，我们在 k8s集群之上部署应用程序的时候，也可以通过宿主机的
NodePort 暴露的端口访问里面的程序，用户访问 kubernetes 集群需要经历如下认证过程：认证

1.认证(Authenticating) 是对客户端的认证，通俗点就是用户名密码验证
2.授权(Authorization) 是对资源的授权， k8s中的资源无非是容 器，最终其实就是容器的计算，网
络，存储资源，当一个请求经过认证后，需要访问某一个资源（比如创建一个 pod） ，授权检查 会根
据授权规则判定该资源（比如某 namespace 下的 pod）是否是该客户可访问的。

3.准入(Admission Control) 机制：
准入控制器（ Admission Controller ）位于  API Server 中，在对象被持久化之前，准入控制器拦
截对 API Server 的请求，一般用来做身份验证和授权。其中包含两个特殊的控制器：

MutatingAdmissionWebhook  和 ValidatingAdmissionWebhook 。分别作为配置的变异和验
证准入控制  webhook 。
变更（Mutating ）准入控制：修改请求的对象
验证（ Validating ）准入控制：验证请求的对象

准入控制器是在  API Server 的启动参数配置的。一个准入控制器可能属于以上两者中的一种，也
可能两者都属于。当请求到达  API Server 的时候首先执行变更准入控制，然后再执行验证准入控
制。

我们在部署  Kubernetes 集群的时候都会默认开启一系列准入控制器，如果没有设置这些准入控制
器的话可以说你的  Kubernetes 集群就是在裸奔，应该只有集群管理员可以修改集群的准入控制
器。
例如我 会默认开启如下的准入控制器。
--admission -

```bash
control=ServiceAccount,NamespaceLifecycle,NamespaceExists,LimitRanger,ResourceQ
uota,MutatingAdmissionWebhook,ValidatingAdmissionWebhook
```

k8s的整体架构也是一个微服务的架构，所有的请求都是通过一个 GateWay ，也就是 kube -
apiserver 这个组件（对外提供 REST 服务） ， k8s中客户端有两类，一种是普通用户， 一种是集群
内的 Pod，这两种客户端的认证机制略有不同，但无论是哪一种，都需要依次经过认证，授权，准
入这三个机制。

**1.1 认证**
**1、认证支持多种插件**
（1）令牌（ token ）认证：

 双方有一个共享密钥，服务器上先创建一个密 码下来，客户端登陆的时候拿这个密码登陆即可，这个
就是对称密钥认证方式； k8s提供了一个 restful 风格的接口，它的所有服务都是通过 http 协议提
供的，因此认证信息只能经由 http 协议的认证首部进行传递，这种认证首部进行传递通常叫做令
牌；
（2）ssl认证：
对于 k8s访问来讲， ssl认证能让客户端确认服务器的认证身份，我们在跟服务器通信的时候，需要
服务器发过来一个证书，我们需要确认这个证书是不是 ca签署的，如果是我们认可的 ca签署的，
里面的 subj 信息与我们访问的目标主机信息保持一致，没有问题，那么我们就认为服务 器的身份得
到认证了， k8s中最重要的是服务器还需要认证客户端的信息， kubectl 也应该有一个证书，这个证
书也是 server 所认可的 ca签署的证书，双方需要互相认证，实现加密通信，这就是 ssl认证。

客户端对 apiserver 发起请求， apiserver 要识别这个用户是否有请求的权限，要识别用户本身能否
通过 apiserver 执行相应的操作，那么需要哪些信息才能识别用户信息来完成对用户的相关的访问
控制呢？

kubectl explain pods.spec 可以看到有一个字 段serviceAccountName （服务账号名称） ，这个
就是我们 pod 连接 apiserver 时使用的账号 ，因此整个 kubernetes 集群中的账号有两类，
ServiceAccount （服务账号） ， User account （用户账号）

User account ：实实在在现实中的人，人可以登陆的账号，客户端想要对 apiserver 发起请求，
apiserver 要识别这个客户端是否有请求的权限，那么不同的用户就会有不同的权限，靠用户账号表
示，叫做 username

ServiceAccount ：方便 Pod 里面的进程调用 Kubernetes API 或其他外部服务而设计的，是
kubernetes 中的一种资源

user account ：这个是登陆 k8s物理机器的用户

1.ServiceAccount
Servic e account 是为了方便 Pod 里面的进程调用 Kubernetes API 或其他外部服务而设计的。它
与User account 不同，User account 是为人设计的，而 service account 则是为 Pod 中的进程
调用 Kubernetes API 而设计； User account 是跨 namespace 的，而 service account 则是仅
局限它所在的 namespace ；每个 namespace 都会自动创建一个 default service account ；
开启 ServiceAccount Adm ission Controller 后

1）每个 Pod 在创建后都会自动设置 spec.serviceAccount 为default （除非指定了其他
ServiceAccout ）
2）验证 Pod 引用的 service account 已经存在，否则拒绝创建；

 当创建  pod 的时候，如果没有指定一个  serviceaccount ，系统会自动在与该 pod 相同的
namespace 下为其指派一个 default  service account 。这是 pod 和apiserver 之间进行通信的
账号，如下：

kubectl get pods

```bash
[root@xuegod63 ~]# kubectl get pods
NAME                              READY   STATUS      RESTARTS   AGE
mysql -pod-volume                  1/1     Running     0          43m
nfs-provisioner -cd5589cfc -c8vc5    1/1     Running     0          13h
pod-secret                          1/1     Running     0          18m
web-0                               1/1     Running     0          13h
web-1                               1/1     Running     0          13h

[root@xuegod63 ~]# kubectl get pods w eb-0 -o yaml | grep "serviceAccountName"
  serviceAccountName: default
[root@xuegod63 ~]# kubectl describe pods web -0
Volumes:
  www:
```

```yaml
    Type:       PersistentVolumeClaim
    ClaimName:  www -web-0
   default -token -cq5qp:
    Type:        Secret (a volume  populated by a Secret)
    SecretName:  default -token -cq5qp
    Optional:    false

```
从上面可以看到每个 Pod 无论定义与否都会有个存储卷，这个存储卷为 default -token -***。pod
和apiserver 的认证信息 通过 secret 进行定义，由于认证信息属于敏感信息，所以需要保存在
secret 资源当中，并以存储卷的方式挂载到 Pod 当中。从而让 Pod 内运行的应用通过对应的
secret 中的信息来连接 apiserver ，并完 成认证。每个  namespace 中都有一个默认的叫做
default  的 serviceaccount 资源。查看名称空间内的 secret ，也可以看到对应的 default -
token 。让当前名称空间中所有的 pod 在连接 apiserver 时可以使用的预制认证信息，从而保证
pod 之间的通信。

```bash
[root@xuegod63 ~]# kubectl get sa
NAME              SECRETS   AGE
default           1         12d
[root@xuegod63 ~]# kubectl get secret
NAME                          TYPE                                  DATA   AGE
default -token -cq5qp           kubernetes.io/service -account -token   3      12d
```

默认的 service account 仅仅只能获取当前 Pod 自身的相关属性，无法观察到其他名称空间 Pod
的相关属性信息 。如果想要扩展 Pod，假设有一个 Pod 需要用于管理其他 Pod 或者是其他资源对
象，是无法通过自身的名称空间的 serviceaccount 进行获取其他 Pod 的相关属性信息的，此时就

 需要进行手动创建一个 serviceaccount ，并在创建 Pod 时进行定义。那么 serviceaccount 该如
何进行定义呢？实际上， service accout 也属于一个 k8s资源， serviceAccount 也属于标准的
k8s资源，可以创建一个 serviceAccount ，创建之后由我们创建的 pod 使用
serviceAccount Name 去加载自己定义的 serviceAccount 就可以了，如下 ：

（1）创建一个 serviceaccount ：
kubectl create serviceaccount test
kubectl get sa 显示如下：

可以看到已经创建了 test 的serviceacount
kubectl describe sa test 查看 test 这个账号的详细信息

上面可以看到生成了一个 test-token -hnc57 的secret 和test-token -hnc57 的token

kubectl get secret 显示如下：

kubectl describe secret test -token -hnc57 显示如下：

上面可以看到生成了 test-token -hnc57 的token 详细信息，这个 token 就是 sa连接 apiserver
的认证信息 ，这个 token 也是登陆 k8s dashboard 的token ，这些是一个认证信息，能够登陆
k8s，能认证到 k8s，但是不能做别的事情，不代表权限，想要做其他事情，需要授权

**2、kubeconfig 文件**

 在K8S 集群当中，每一个用户对资源的访问都是需要通过 apiserver 进行通信认证才能进行访问
的，那么在此机制当中，对资源的访问可以是 token ，也可以是通过配置文件的方式进行保存和使用
认证信息，可以通过 kubectl config 进行查看配置，如下：
kubectl config view

```yaml
apiVersion: v1
clusters:
- cluster:
    certificate -authority -data: DATA+OMITTED
    server: https://192.168. 40.199:6443    #apiserver 的地址
  name: kubernetes                         # 集群的名字
contexts:
- context:
    cluster: kubernetes
    user: kubernetes -admin
  name: kubernetes -admin@kubernetes     # 上下文的名字
current -context: kubernetes -admin@kubernetes       # 当前上下文的名字
kind: Config
preferences: {}
users:
- name: kubernetes -admin
  user:
    client -certificate -data: REDACTED
    client -key-data: REDACTED

```
在上面的配置文件当中，定义了集群、 上下文以及用户。其中 Config 也是 K8S 的标准资源之一，
在该配置文件当中定义了一个集群列表，指定的集群可以有多个；用户列表也可以有多个，指明集群
中的用户；而在上下文列表当中，是进行定义可以使用哪个用户对哪个集群进行访问，以及当前使用
的上下文是什么。

kubectl get pods --kubeconfig=./config

**1.2 授权**
如果用户通过认证，什么权限都没有，需要一些后续的授权操作，如对资源的增删该查等，
kubernetes1.6 之后开始有 RBAC （基于角色的访问控制机制）授权检查机制 。
 Kubernetes 的授权是基于插件 形成的，其常用的授权插件有以下几种：
1）Node （节点认证）
2）ABAC( 基于属性的访问控制 )
3）RBAC （基于角色的访问控制） ***

 4）Webhook （基于 http 回调机制的访问控制）

什么是 RBAC （基于角色的访问控制）？
 让一个用户（ Users ）扮演一个角色（ Role ） ，角色拥有权限，从而让用户拥有这样的权限，随后在
授权机制当中，只需要将权限授予某个角色，此时用户将获取对应角色的权限，从而实现角色的访问
控制。如图：

在k8s的授权机制当中，采用 RBAC 的方式进行授权，其工作逻辑是，把对对象的操作权限定义到
一个角色当中，再将用户绑定到该角色，从而使用户得到对应角色的权限。如果通过 rolebinding
绑定 role，只能对 rolebingding 所在的名称空间的资源有权限，上图 user1 这个用户绑定到
role1 上，只对 role1这个名称空间的资源有权限，对其他名称空间资源没有权限，属于名称空间级
别的；

另外， k8s为此还有一种集群级别的授权机制，就是定义一个集群角色（ ClusterRole ） ，对集群内
的所有资源都有可操作的权限，从而将 User2 通过 ClusterRoleBinding 到ClusterRole ，从而使
User2 拥有集群的操作权限。

Role 、RoleBinding 、ClusterRole 和ClusterRoleBinding 的关系如下图：

通过上图可以看到，可以通过 rolebinding 绑定 role，rolebinding 绑定 clusterrole ，
clusterrolebinding 绑定 clusterrole 。

 上面我们说了两个角色绑定：
（1）用户通过 rolebinding 绑定 role
（2）用户通过 clusterrolebinding 绑定 clusterrole
还有一种： rolebinding 绑定clusterrole

rolebinding 绑定 clusterrole 的好处：
假如有 6个名称空间，每个名称空间的用户都需要对自己的名称空间有管理员权限，那么需要定义 6
个role 和rolebinding ，然后依次绑定，如果名称空间更多，我们需要定义更多的 role，这个是很
麻烦的，所以我们引入 clusterrole ，定义一个 clusterrole ，对 clusterrole 授予所有权限，然后用
户通过 rolebinding 绑定到 clusterrole ，就会拥有自己名称空间的管理员权限了

> **注：RoleBinding 仅仅对当前名称空间有对应的权限。**

**1.3 准入控制**
一般而言，准入控制只是用来定义我们授权检查完成之后的后续的其他安全检查操作的，进一步补充
了授权机制，由多个插件组合实行，一般而言在创建，删除，修改或者做代理时做补充；

Kubernetes 的Admission Control 实际上是一个准入控制器 (Admission Controller) 插件列
表，发送到 APIServer 的请求都需要经过这个列表中的每个准入控制器插件的检查，如果某一个控
制器插件准入失败，就准入失败。

控制器插件如下：
AlwaysAdmit ：允许所有请求通过
AlwaysPullIma ges：在启动容器之前总是去下载镜像，相当于每当容器启动前做一次用于是否有权
使用该容器镜像的检查
AlwaysDeny ：禁止所有请求通过，用于测试
DenyEscalatingExec ：拒绝 exec 和attach 命令到有升级特权的 Pod 的终端用户访问。如果集中
包含升级特权的容器，而要限制终端用户在这些容器中执行命令的能力，推荐使用此插件
ImagePolicyWebhook
ServiceAccount ：这个插件实现了 serviceAccounts 等等自动化，如果使用 ServiceAccount 对
象，强烈推荐使用这个插件
SecurityContextDeny ：将 Pod 定义中定义了的 SecurityContext 选项全部失效。
SecurityContext 包含在容器中定义了操作系统级别的安全选型如 fsGroup ，selinux 等选项
ResourceQuota ：用于 namespace 上的配额管理，它会观察进入的请求，确保在 namespace 上
的配额不超标。推荐将这个插件放到准入 控制器列表的最后一个。 ResourceQuota 准入控制器既可
以限制某个 namespace 中创建资源的数量，又可以限制某个 namespace 中被 Pod 请求的资源总
量。ResourceQuota 准入控制器和 ResourceQuota 资源对象一起可以实现资源配额管理。
LimitRanger ：用于 Pod 和容器上的配额管理，它会观察进入的请求，确保 Pod 和容器上的配额不
会超标。准入控制器 LimitRanger 和资源对象 LimitRange 一起实现资源限制管理

 NamespaceLifecycle ：当一个请求是在一 个不存在的 namespace 下创建资源对象时，该请求会
被拒绝。当删除一个 namespace 时，将会删除该 namespace 下的所有资源对象
DefaultStorageClass
DefaultTolerationSeconds
PodSecurityPolicy
当Kubernetes 版本>=1.6.0 ，官方建议使用这些插件：
–admission -

```bash
control=NamespaceLifecycle,LimitRanger,ServiceAccount,PersistentVolumeLabel,Def au
ltStorageClass,ResourceQuota,DefaultTolerationSeconds
```
当Kubernetes 版本>=1.4.0 ，官方建议使用这些插件：
–admission -

```bash
control=NamespaceLifecycle,LimitRanger,ServiceAccount,DefaultStorageClass,Resourc
eQuota
```
以上是标准的准入插件，如果是自己定制的话， k8s1.7 版 出了两个 alpha features, Initializers
和 External Admission Webhooks

**2、ServiceAccount 介绍**

kubernetes 中账户区分为： User Accounts （用户账户）  和 Service Accounts （服务账户）
两种：
UserAccount 是给 kubernetes 集群外部用户使用的，例如运维或者集群管理人员， ，kubeadm
安装的 k8s，默认用户账号是 kubernetes -admin ；

  k8s客户端 (一般用 :kubectl) ------ >API Server

  APIServer 需要对客户端做认证，使用 kubeadm 安装的 K8s，会在用户家目录下创建一个认
证配置文件  .kube/config 这里面保存了客户端访问 API Server 的密钥相关信息，这样当用 kubectl
访问 k8s时，它就会自动读取该配置文件，向 API Server 发起认证，然后完成操作请求。

用户名称可以在 kubeconfig 中查看

```bash
[root@ xuegod 63~]# cd ~/.kube/
[root@ xuegod 63 .kube]# ls
cache config http -cach e
[root@xuegod63 .kube]# cat config
...
users:
- name: kubernetes -admin
...
```

ServiceAccount 是Pod使用的账号 ，Pod 容器的进程需要访问 API Server 时用的就是
ServiceAccount 账户； ServiceAccount 仅局限它所在的 namespace ，每个 namespace 创建时都会
自动创建一个 default service account ；创建 Pod 时，如果没有指定 Service Account ，Pod 则会使
用default Service Account 。

**3、RBAC认证授权策略**
RBAC 介绍
在Kubernetes 中，所有资源对象都是通过 API进行操作，他们保存在 etcd 里。而对 etcd 的操作
我们需要通过访问  kube -apiserver 来实现，上面的 Service Account 其实就是 APIServer 的认证过
程，而授权的机制是通过 RBAC ：基于角色的访问控制实现。

RBAC 有四个资源对象，分别是 Role 、ClusterRole 、RoleBinding 、ClusterRoleBinding

**3.1 Role ：角色**
一组权限的集合，在一个命名空间中，可以用其来定义一个角色，只能对命名空间内的资源进行
授权。如果是集群级别的资源，则需要使用 ClusterRole 。例如：定义一个角色用来读取 Pod 的权
限

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: rbac
  name: pod -read
rules:
- apiGroups: [""]
  resources: ["pods"]
  resourceNames: [ ]
verbs: ["get","watch","list"]

```
rules 中的参数说明：
**1、apiGroups ：支持的 API组列表，例如： "apiVersion: batch/v1" 等**
**2、resources ：支持的资源对象列表，例如 pods 、deplayments 、jobs 等**
**3、resourceNames: 指定 resource 的名称**
**4、verbs ：对资源对象的操作方法列表。**

**3.2 ClusterRole ：集群角色**

具有和角色一致的命名空间资源的管理能力，还可用于以下特殊元素的授权
**1、集群范围的资源，例如 Node**
**2、非资源型的路径，例如： /healthz**
**3、包含全部命名空间的资源，例如 Pods**

例如：定义一个集群角色可让用户访问任意 secrets

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: secrets -clusterrole
rules:
- apiGroups: [""]
 resources: ["secrets"]
verbs: ["get","watch","list"]

```
**3.3 RoleBinding ：角色绑定 、ClusterRolebinding ：集群角**
色绑定

角色绑定和集群角色绑定用于把一个角色绑定在一个目标上，可以是 User ，Group ，Service
Account ，使用 RoleBinding 为某个命名空间授权，使用 ClusterRoleBinding 为集群范围内授
权。
例如：将在 rbac 命名空间中把 pod-read 角色授予用户 es

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: pod -read -bind
  namespace: rbac
subjects:
- kind: User
  name: es
  apiGroup: rbac.authorization.k8s.io
roleRef:
- kind: Role
  name: pod -read

   apiGroup: rbac.authorizatioin.k8s.io

```
RoleBinding 也可以引用 ClusterRole ，对属于同一命名空间内的 ClusterRole 定义的资源主体进
行授权，  例如： es能获取到集群中所有的资源信息

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBindi ng
metadata:
  name: es -allresource
  namespace: rbac
subjects:
- kind: User
  name: es
  apiGroup: rbac.authorization.k8s.io
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster -admin

```
集群角色绑定的角色只能是集群角色，用于进行集群级别或对所有命名空间都生效的授权
例如：允许 manager 组的用户读取所有 namaspace 的secrets

```yaml
apiVersion: rabc.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: read -secret -global
subjects:
- kind: Group
  name: manager
  apiGroup: rabc.authorization.k8s. io
ruleRef:
- kind: ClusterRole
  name: secret -read
  apiGroup: rabc.authorization.k8s.io
```
**4、资源的引用方式**
多数资源可以用其名称的字符串表示，也就是 Endpoint 中的 URL 相对路径，例如 pod 中的日志是
GET /api/v1/namaspaces/{namespace}/pods/{podname}/log
如果需要在一个 RBAC 对象中体现上下级资源，就需要使用 “/”分割资源和下级资源。
例如：若想授权让某个主体同 时能够读取 Pod 和Pod log ，则可以配置  resources 为一个数组

```yaml
apiVersion: rabc.authorization.k8s.io/v1
kind: Role
metadata:

   name: logs -reader
  namespace: default
rules:
- apiGroups: [""]
  resources: ["pods","pods/log"]
  verbs: ["get","list"]

```
资源还可以通过名称（ ResourceName ）进行引用，在指定 ResourceName 后，使用 get、
delete 、update 、patch 请求，就会被限制在这个资源实例范围内
例如，下面的声明让一个主体只能对名为 my-configmap 的Configmap 进行 get和update 操
作：

```yaml
apiVersion: rabc.authorization.k8s.io/v1
kind: Role
metadata:
  namaspace: default
  name: configmap -update
rules:
- apiGroups: [""]
  resources: ["configmap"]
  resourceNames: ["my -configmap"]
  verbs: ["get","update"]

```
**5、常见角色示例**
（1）允许读取核心 API组的 Pod 资源
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get","list","watch"]

（2）允许读写 extensions 和apps 两个 API组中的 deploym ent资源
rules:
- apiGroups: ["extensions","apps"]
  resources: ["deployments"]
  verbs: ["get","list","watch","create","update","patch","delete"]

（3）允许读取 Pod 以及读写 job信息
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get","list","watch"] 、

 - apiVersion: ["batch","extensions"]
  resources: ["jobs"]
  verbs: ["get","list","watch","create","update","patch","delete"]

（4）允许读取一个名为 my-config 的ConfigMap （必须绑定到一个 RoleBinding 来限制到一个
Namespace 下的 ConfigMap ）：
rules:
- apiGroups : [""]
  resources: ["configmap"]
  resourceNames: ["my -configmap"]
  verbs: ["get"]

（5）读取核心组的 Node 资源（ Node 属于集群级的资源，所以必须存在于 ClusterRole 中，并使
用ClusterRoleBinding 进行绑定） ：
rules:
- apiGroups: [""]
  resources: ["nodes"]
  verbs: ["get","list","watch"]

（6）允许对非资源端点 “/healthz”及其所有子路径进行 GET 和POST 操作（必须使用
ClusterRole 和ClusterRoleBinding ）：
rules:
- nonResourceURLs: ["/healthz","/healthz/*"]
  verbs: ["get","post"]

**6、常见的角色绑定示例**
（1）用户名 alice
subjects:
- kind: User
  name: alice
  apiGroup: rbac.authorization.k8s.io

（2）组名 alice
subjects:
- kind: Group
  name: alice
  apiGroup: rbac.authorization.k8s.io

（3）kube -system 命名空间中默认 Service Account

 subjects:
- kind: ServiceAccount
  name: default
  namespace: kube -system

（4）qa命名空间中的所有 Service Account ：
subjects:
- kind: Group
  name: system:serviceaccounts:qa
  apiGroup: rbac.authorization.k8s.io

（5）所有 Service Account
subjects:
- kind: Group
  name: system:serviceaccounts
  apiGroup: rbac.authorization.k8s.io

（6）所有认证用户
subjects:
- kind: Group
  name: system:authenticated
  apiGroup: rbac.authorization.k8s.io

（7）所有未认证用户
subjects:
- kind: Group
  name: system:unauthenticated
  apiGroup: rbac.authorization.k8s.io

（8）全部用户
subjects:
- kind: Group
  name: system:authenticated
  apiGroup: rbac.authorization.k8s.io
- kind: Group
  name: system:unauthenticated
  apiGroup: rbac.authorization.k8s.io

**7、对Service Account 的授权管理**
Service Account 也是一种账号，是给运行在 Pod 里的进程提供了必要的身份证明。需要在 Pod
定义中指明引用的 Service Account ，这样就可以对 Pod 的进行赋权操作。例如： pod 内可获取
rbac 命名空间的所有 Pod 资源， pod-reader -sc的Service Account 是绑定了名为 pod-read 的
Role

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
  namespace: rbac
spec:
  serviceAccountName:  pod-reader -sc
  containers:
  - name: nginx
    image: nginx
    imagePullPolicy: IfNotPresent
    ports:
    - containerPort: 80

```
默认的 RBAC 策略为控制平台组件、节点和控制器授予有限范围的权限，但是除 kube -system 外
的Service Account 是没有任何权限的。
（1）为一个应用专属的 Service Account 赋权
此应用需要在 Pod 的spec 中指定一个 serviceAccountName ，用于 API、Application
Manifest 、kubectl create serviceaccount 等创建 Service Account 的命令。

例如为 my-namespace 中的 my-sa Service Account 授予只读权限
kubectl create rolebinding my -sa-view --clusterrole=view --serviceaccount=my -
namespace:my -sa --namespace=my -names pace

（2）为一个命名空间中名为 default 的Service Account 授权
如果一个应用没有指定  serviceAccountName ，则会使用名为 default 的Service Account 。注
意，赋予 Service Account “default ”的权限会让所有没有指定 serviceAccountName 的Pod
都具有这些权限

例如，在 my-namespace 命名空间中为 Service Account “default ”授予只读权限：
kubectl create rolebinding default -view --clusterrole=view --serviceaccount=my -
namespace:default --namespace=my -namespace

 另外，许多系统级 Add-Ons 都需要在 kube -system 命名空间中运行，要让这些 Add-Ons 能够使
用超级用户权限，则可以把 cluster -admin 权限赋予 kube -system 命名空间中名为 default 的
Service Account ，这一操作意味着 kube -system 命名空间包含了 通向 API超级用户的捷径。
kubectl create clusterrolebinding add -ons-add-admin --clusterrole=cluster -admin --

```bash
serviceaccount=kube -system:default
```

（3）为命名空间中所有 Service Account 都授予一个角色
如果希望在一个命名空间中，任何 Service Account 应用都具有一个角色，则可以为这一命名空间
的Service Account 群组进行授权

kubectl create rolebinding serviceaccounts -view --clusterrole=view --

```bash
group=system:serviceaccounts:my -namespace --namespace=my -namespace
```

（4）为集群范围内所有 Service Account 都授予一个低权限角色
如果不想为每个命名空间管理授权，则可以把一个集群级别的角色赋给所有 Service Account 。

kubectl create clusterrolebinding serviceacco unts-view --clusterrole=view --

```bash
group=system:serviceaccounts
```

（5）为所有 Service Account 授予超级用户权限
kubectl create clusterrolebinding serviceaccounts -view --clusterrole=cluster -admin --

```bash
group=system:serviceaccounts
```

**8、使用 kubectl命令行工具创建资源对象**
（1）在命名空间 rbac 中为用户 es授权 admin ClusterRole ：

kubectl create rolebinding bob -admin -binding --clusterrole=admin --user=es --

```bash
namespace=rbac
```

（2）在命名空间 rbac 中为名为 myapp 的Service Account 授予 view ClusterRole ：

kubctl create rolebinding myapp -role-binding --clusterrole=vi ew --

```bash
serviceaccount= rbac:myapp --namespace=rbac
```

（3）在全集群范围内为用户 root 授予 cluster -admin ClusterRole ：

kubectl create clusterrolebinding cluster -binding --clusterrole=cluster -admin --

```bash
user=root
```

（4）在全集群范围内为名为 myapp 的Service Account 授予 view ClusterRole ：

kubect l create clusterrolebinding service -account -binding --clusterrole=view --

```bash
serviceaccount=myapp
```

yaml文件进行 rbac 授权： https://kubernetes.io/zh/docs/reference/access -authn -
authz/rbac/

**9、限制不同的用户操作 k8s集群**
ssl认证
生成一个证书
（1）生成一个私钥
cd /etc/kubernetes/pki/
(umask 077; openssl genrsa -out lucky.key 2048)
（2）生成一个证书请求
openssl req -new -key lucky.key -out lucky.csr -subj "/CN=lucky"
（3）生成一个证书
openssl x509 -req -in lucky.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out lucky.crt
-days 3650
在kubeconfig 下新增加一个 lucky这个用户
（1）把lucky这个用户添加到 kubernetes 集群中，可以用来认证 apiserver 的连接

```bash
[root@xianchaomaster1 pki]# kubectl config set -credentials lucky --client-
certificate=./lucky.crt --client-key=./lucky.key --embed-certs=true
kubectl config set -context lucky@kubernetes --cluster=kubernetes --user=lucky
```
（3）切换账号到 lucky，默认没有任何权限
kubectl config use -context lucky@kubernetes
kubectl config use -context kubernetes -admin@kubernetes 这个是集群用户，有任何权限
把user这个用户通过 rolebinding 绑定到clusterrole 上，授予权限 ,权限只是在 lucky这个名称
空间有效
（1）把lucky这个用户通过 rolebinding 绑定到clusterrole 上
kubectl create ns lucky
kubectl create rolebinding lucky -n lucky --clusterrole=cluster -admin --user=lucky
（2）切换到 lucky这个用户
kubectl config use -context lucky@kubernetes
（3）测试是否有权限
kubectl get pods -n lucky 批注 [韩1]:

 有权限操作这个名称空间
kubectl get pods
没有权限操作其他名称空间

添加一个 lucky的普通用户
useradd lucky
cp -ar /root/.kube/ /home/lucky/
chown -R lucky.lucky  /home/lucky/
su - lucky
kubectl get pods -n lucky


