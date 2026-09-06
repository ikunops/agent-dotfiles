实验环境：
Istio安装在已经存在的 k8s集群上即可

k8s集群：        k8s的控制节点
ip：192.168.40.180
主机名： xianchaomaster1
配置：6vCPU/6Gi内存

k8s的工作节点：
ip：192.168.40.181
主机名： xianchaonode1
配置：12vCPU/8Gi内存

1.Istio介绍？

官方文档： https://istio.io/docs/concepts/what -is-istio/
中文官方文档： https://istio.io/zh/docs/concepts/what -is-istio/
Github地址：https://github.com/istio/istio/releases

**1.1 Istio是什么？**

官当解释：
An open platform to connect, secure, control and observe services.

翻译过来，就是 ”连接、安全加固、控制和观察服务的开放平台 “。开放平台就是指它本身是开源
的，服务对应的是微服务，也可以粗略地理解为单个应用。

**1、连接（Connect） ：智能控制服务之间的调用流量，能够实现灰度升级、 AB 测试和蓝绿部署等功**
能
**2、安全加固（ Secure） ：自动为服务之间的调用提供认证、授权和加密。**
**3、控制（Control） ：应用用户定义的  policy，保证资源在消费者中公平分配。**
**4、观察（Observe） ：查看服务运行期间的各种数据，比如日志、监控和  tracing，了解服务的运行**
情况。

Istio是ServiceMesh 的产品化落地， 可以通过在现有 的服务器新增部署边车代理 (sidecar
proxy)，应用程序不用改代码，或者只需要改很少的代码，就能实现 如下基础功能 ：
**1、帮助微服务之间建立连接，帮助研发团队更好的管理与监控微服务，并使得系统架构更加安全 ；**
**2、帮助微服务分层解耦，解耦后的 proxy层能够更加专注于提供基础架构能力，例如：**
（1）服务发现 (discovery);
（2）负载均衡 (load balancing);
（3）故障恢复 (failure recovery);
（4）服务度量 (metrics);
（5）服务监控 (monitoring);
（6）A/B测试(A/B testing);
（7）灰度发布 (canary rollouts);
（8）限流限速 (rate limiting);
（9）访问控制 (access control);
（10）身份认证 (end-to-end authentication) 。

**1.1.1 服务注册和发现**

RPC：RPC（Remote Procedure Call）远程过程调用，简单的理解是一个节点请求另一个节点提供的
服务

**1.1.2 负载均衡？**
把前端的请求分发到后台多个服务器

**1.1.3 故障恢复**
出现故障具备自恢复的能力

**1.1.4 服务度量**
对于 HTTP，HTTP/2 和 GRPC 流量，Istio 生成以下指标：
**1、请求计数（ istio_requests_total ） ：这是一个用于累加每个由  Istio 代理所处理请求的**
COUNTER 指标。
**2、请求持续时间（ istio_request_duration_seconds ） ：这是一个用于测量请求的持续时间的**
DISTRIBUTION 指标。
**3、请求大小（ istio_request_bytes ） ：这是一个用于测量  HTTP 请求 body 大小的 DISTRIBUTION**
指标。
**4、响应大小（ istio_response_bytes ） ：这是一个用于测量  HTTP 响应 body 大小的 DISTRIBUTION**
指标。
对于 TCP 流量，Istio 生成以下指标：
**1、Tcp 发送字节数（ istio_tcp_sent_bytes_total ） ：这是一个用于测量在  TCP 连接下响应期间发**
送的总字节数的  COUNTER 指标。
**2、Tcp 接收字节数（ istio_tcp_received_bytes_total ） ：这是一个用于测量在  TCP 连接下请求期**
间接收的总字节数的 COUNTER 指标。
**3、Tcp 打开连接数（ istio_tcp_connections_opened_total ） ：这是一个用于累加每个打开连接的**
COUNTER 指标。
**4、Tcp 关闭连接数  (istio_tcp_connect ions_closed_total) : 这是一个用于累加每个关闭连接的**
COUNTER 指标。

**1.1.5 灰度发布**
灰度发布也叫金丝雀发布，起源是，矿井工人发现，金丝雀对瓦斯气体很敏感，矿工会在下井之
前，先放一只金丝雀到井中，如果金丝雀不叫了，就代表瓦斯浓度高。

在灰度发布开始后，先启动一个新版本应用，但是并不直接将流量切过来，而是测试人员对新版本
进行线上测试，启动的这个新版本应用，就是我们的金丝雀。如果没有问题，那么可以将少量的用户流
量导入到新版本上，然后再对新版本做运行状态观察，收集各种运行时数据，如果此时对新旧版本做各
种数据对比，就是所谓的 A/B测试。

当确认新版本运行良好后，再逐步将更多的流量导入到新版本上，在此期间，还可以不断地调整新旧两
个版本的运行的服务器副本数量，以使得新版本能够承受越来越大的流量压力。直到将 100%的流量都切
换到新版本上，最后关闭剩 下的老版本服务，完成灰度发布。

如果在灰度发布过程中（灰度期）发现了新版本有问题，就应该立即将流量切回老版本上，这样，就会
将负面影响控制在最小范围内。

**1.2 Istio核心特性**
**1、流控(traffic management)**
断路器(circuit breakers) 、超时、重试、多路由规则、 AB测试、灰度发布、按照百分比分配流量
等。

**2、安全(security)**
加密、身份认证、服务到服务的权限控制、 K8S里容器到容器的权限控制等。

**3、可观察 (observability)**
追踪、监控、数据收集，通过控制后台全面了解上行下行流量，服务链路情况，服务运行情况，系
统性能情况，国内微服务架构体系，这一块做得比较缺乏。

**4、平台无关系 (platform support)**
K8s，物理机，自己的虚机都没问题。

**5、集成与定制 (integration and customization)**
可定制化扩展功能。
**1.2.1 断路器**
互动1：举个生活中的例子 解释断路器
当电路发生故障或异常时，伴随着电流不断升高，并且升高的电流有可能 能损坏电路中的某些重要
器件，也有可能烧毁电路甚至造成火灾。若电路中正确地安置了保险丝，那么保险丝就会在电流异常升
高到一定的高度和热度的时候，自身熔断切断电流，从而起到保护电路安全运行的作用。

很多技术都是来源生活的，随着社会进步，科技发展

断路器也称为服务熔断，在多个服务调用的时候，服务 A依赖服务 B，服务B依赖服务 C，如果服务
C响应时间过长或者不可用，则会让服务 B占用太多系统资源，而服务 A也依赖服 B，同时也在占用大量
的系统资源，造成系统雪 崩的情况出现。  Istio 断路器通过网格中的边车对流量进行拦截判断处理，避
免了在代码中侵入控制逻辑，非常方便的就实服务熔断的能力。

在微服务架构中， 在高并发情况下，如果请求数量达到一定极限（可以自己设置阈值），超出了设
置的阈值， 断路器会自动开启服务保护功能，然后通过服务降级的方式返回一个友好的提示给客户端。
假设当10个请求中，有 10%失败时，熔断器就会打开，此时再调用此服务，将会直接返回失败，不再调
远程服务。直到 10s钟之后，重新检测该触发条件，判断是否把熔断器关闭，或者继续打开。

互动2：服务降级（提高用户体验效果）
比如电商平台，在针对 618、双11的时候会有一些秒杀场景，秒杀的时候请求量大，可能会返回报
错标志“当前请求人数多，请稍后重试”等，如果使用服务降级，无法提供服务的时候，消费者会调用
降级的操作，返回服务不可用等信息，或者返回提前准备好的静态页面写好的信息。

**1.2.2 超时**
什么时候需要用到超时？
在生产环境中经常会碰到由于调用方等待下游的响应过长，堆积大量的请求阻塞了自身服务，造成
雪崩的情况，通过超时处理来避免由于无限期等待造成的故障，进而增强服务的可用性。
通过例子来理解

nginx 服务设置了超时时间为 3秒，如果超出这个时间就不在等待，返回超时错误

 httpd 服务设置了响应时间延迟 5秒，任何请求都需要等待 5秒后才能返回
client 通过访问  nginx 服务去反向代理  httpd 服务，由于  httpd 服务需要 5秒后才能返回，但
nginx 服务只等待 3秒，所以客户端会提示超时错误。

**1.2.3 重试**
istio 重试机制就是如果调用服务失败， Envoy 代理尝试连接服务的最大次数。而默认情况下，
Envoy 代理在失败后并不会尝试重新连接服务 。
举个例子：

客户端调用  nginx，nginx 将请求转发给  tomcat。tomcat 通过故障注入而中止对外服务， nginx
设置如果访问  tomcat 失败则会重试  3 次。

**1.2.4 多路由规则**
**1、HTTP重定向（ HTTPRedirect ）**
**2、HTTP重写（HTTPRewrite ）**
**3、HTTP重试（HTTPRetry ）**
**4、HTTP故障注入（ HTTPFaultInjection ）**
**5、HTTP跨域资源共享（ CorsPolicy ）**

2.Istio架构

istio服务网格从逻辑上分为数据平面和控制平面。

**1、数据平面由 一组以Sidecar 方式部署的 智能代理 (Envoy+Polit -agent)组成。这些代理承载并控**
制微服务之间的所有网络通信 ，管理入口和出口流量，类似于一线员工。  Sidecar 一般和业务容器
绑定在一起（在 Kubernets 中以自动注入 的方式注入到到业务pod中），来劫持业务应用容器的流
量，并接受控制面组件的控制，同时会向控制面输出日志、跟踪及监控数据。

Envoy 和 pilot-agent 打在同一个镜像中，即 sidecar Proxy。

**2、控制平面 负责管理和配置代理来 路由流量。**
istio1.5+中使用了一个全新的部署模式 ，重建了控制平面，将原有的多个组件整合为一个单体结构
istiod，这个组件是控制平面的核心， 管理Istio的所有功能，主要包括 Pilot、Mixer、Citadel
等服务组件。

istiod是新版本中最大的变化，以一个单体组件替代了原有的架构，降低 了复杂度和维护难度 ，但
原有的多组件并不是被完全移除，而是在重构后以模块的形式整合在一起组成 了istiod。

结合下图我们来理解 Istio的各组件的功能及相互之间的协作方式。

**1. 自动注入：在创建应用程序时自动注入  Sidecar 代理Envoy程序。在  Kubernetes 中创建 Pod时，**
Kube-apiserver 调用控制面组件的  Sidecar-Injector 服务，自动修改应用程序的描述信息并注入
Sidecar。在真正创建 Pod时，在创建业务容器的 Pod中同时创建 Sidecar 容器。

**2. 流量拦截：在 Pod初始化时设置 iptables 规则，基于配置的 iptables 规则拦截业务容器的 Inbound**
流量和Outbound 流量到Sidecar 上。而应用程序感知不到 Sidecar的存在，还以原本的方式  进行互相
访问。上图中，流出 frontend 服务的流量会被  frontend 服务侧的  Envoy拦截，而当流量到达 forecast
容器时， Inbound 流量被forecast 服务侧的 Envoy拦截。

**3. 服务发现：服务发起方的  Envoy 调用控制面组件  Pilot 的服务发现接口获取目标服务的实例列表。**
上图中， frontend 服务侧的  Envoy 通过 Pilot 的服务发现接口得到 forecast 服务各个实例的地址。

**4. 负载均衡：服务发起方的 Envoy根据配置的负载均衡策略选择服务实例，并连接对应的实例地址。上**
图中，数据面的各个 Envoy从Pilot中获取forecast 服务的负载均衡配置，并执行负载均衡动作。

**5. 流量治理： Envoy 从 Pilot 中获取配置的流量规则，在拦截到  Inbound 流量和Outbound 流量时执**
行治理逻辑。上图中，  frontend 服务侧的  Envoy 从 Pilot 中获取流量治理规则，并根据该流量治理
规则将不同特征的流量分发到 forecast 服务的v1或v2版本。

**6. 访问安全：在服务间访问时通 过双方的 Envoy进行双向认证和通道加密，并基于服务的身份进行授权**
管理。上图中， Pilot下发安全相关配置，在 frontend 服务和forecast 服务的Envoy上自动加载证书和
密钥来实现双向认证，其中的证书和密钥由另一个管理面组件  Citadel 维护。

**7. 服务监测：在服务间通信时，通信双方的 Envoy都会连接管理面组件 Mixer上报访问数据，并通过**
Mixer将数据转发给对应的监控后端。上图中， frontend 服务对forecast 服务的访问监控指标、日志和
调用链都可以通过这种方式收集到对应的监控 后端。

**8. 策略执行：在进行服务访问时，通过 Mixer连接后端服务来控制服务间的访问，判断对访问是放行还**
是拒绝。上图中， Mixer 后端可以对接一个限流服务对从 frontend 服务到forecast 服务的访问进行速
率控制等操作。

**9. 外部访问：在网格的入口处有一个 Envoy扮演入口网关的角  色。上图中，外部服务通过 Gateway 访**
问入口服务  frontend ，对 frontend 服务的负载均衡和一些流量治理策略都在这个 Gateway 上执行。

问题1：为什么代理会叫 sidecar proxy ？

看了上图就容易懂了， sidecar 和proxy相生相伴，就像摩托车 (motor)与旁边的车厢 (sidecar) 。未来，
sidecar 和proxy就指微服务进程解耦成两个进程之后，提供基础能力的那个代理进程。

3.istio组件详解
Istio服务组件 有很多，从上面的流程中基本能看出每个组件如何协作的，下面具体讲解每个组件的
具体用途和功能。

```bash
[root@xianchaomaster1 ~]# kubectl get svc -n istio-system |awk '{print $1}'
istio-egressgateway

 istio-ingressgateway
istiod

3.1 Pilot
```
Pilot 是 Istio 的主要控制组件，下发指令控制客户端。在整个系统中， Pilot 完成以下任务：
**1、从 Kubernetes 或者其他平台的注册中心获取服务信息，完成服务发现过程。**
**2、读取 Istio 的各项控制配置，在进行转换之后，将其发给数据面进行实施。**

Pilot 将配置内容下发给数据面的  Envoy，Envoy 根据 Pilot 指令，将路由、服务、监听、集群等
定义信息转换为本地配置，完成控制行为的落地。

1）Pilot为Envoy提供服务发现
2）提供流量管理功能（例如， A/B 测试、金丝雀发布等）以及弹性功能（超时、重试、熔断器
等）；
3）生成envoy配置
4）启动envoy
5）监控并管理 envoy的运行状况，比如 envoy出错时pilot-agent负责重启 envoy，或者envoy配
置变更后 reload envoy

**3.2 Envoy**
Envoy是什么？
Envoy是用 C++ 开发的高性能代理，用于协调服务网格中所有服务的入站和出站流量。
Envoy有许多强大的功能 ，例如:
动态服务发现
负载均衡
TLS终端
HTTP/2与gRPC代理
断路器

 健康检查
流量拆分
灰度发布
故障注入

Istio中Envoy与服务什么关系？
为了便于理解 Istio中Envoy与服务的关系，下图为 Envoy的拓扑图，如图所示：

Envoy和Service A 同属于一个 Pod，共享网络和命名空间， Envoy代理进出 Pod A的流量，并将流
量按照外部请求的规则作用于 Service A 中。

Pilot-agent是什么？
Envoy不直接跟 k8s交互，通过  pilot-agent管理的
Pilot-agent进程根据 K8S APIserver中的配置信息生成 Envoy的配置文件，并负责启动 Envoy进
程。
Envoy由Pilot-agent进程启动，启动后， Envoy读取Pilot-agent为它生成的配置文件，然后根据
该文件的配置获取到 Pilot的地址，通过数据面从 pilot拉取动态配置信息，包括路由（ route），
监听器（ listener ），服务集群（ cluster）和服务端点（ endpoint ）。

**3.3 Citadel**
负责处理系统上不同服务之间的 TLS通信。 Citadel 充当证书颁发机构 (CA)，并生成证书以允许在
数据平面中进行安 全的mTLS通信。

Citadel 是 Istio的核心安全组件，提供了自动生  成、分发、轮换与撤销密钥和证书功能。
Citadel 一直监听  Kube- apiserver ，以 Secret的形式为每个服务都生成证书密钥，并在 Pod创建
时挂载到 Pod上，代理容器使用这些文件来做服务身份认证，进而代  理两端服务实现双向 TLS认
证、通道加密、访问授权等安全功能。如图  所示，frontend 服 务对 forecast 服务的访问用到了
HTTP方式，通过配置即可对服务增加认证功能，双方的 Envoy会建立双向认证的 TLS通道，从而在
服务间启用双向认证的 HTTPS。

**3.4 Galley**
Galley是istio的配置验证、提取、处理和分发 的组件。Galley是提供配置管理的服务。实现原理
是通过k8s提供的ValidatingWebhook 对配置进行验证。

Galley使Istio可以与Kubernetes 之外的其他环境一起工作，因为它可以将不同的配置数据转换为
Istio可以理解的通用格式。

**3.5 Ingressgateway**
Ingressgateway 就是入口处的  Gateway，从网格外访问网格内的服务就是通过这个 Gateway 进行
的。istio-ingressgateway 是一个Loadbalancer 类型的Service，不同于其他服务组件只有一两个
端 口，istio-ingressgateway 开放了一组端口，这些就是网格内服务的外部访问端口。如下图所
示，网格入口网关 istio-ingressgateway 的负载和网格内的 Sidecar 是同样的执行流程，也和网格
内的其他  Sidecar 一样从 Pilot处接收流量规则并执行。

**3.6 Sidecar-injector**
Sidecar-injector 是负责自动注入的组件，只要开启了自动注  入，在Pod创建时就会自动调用
istio-sidecar-injector 向Pod中注入Sidecar 容器。
在 Kubernetes 环境下，根据自动注入配置， Kube-apiserver 在拦截到  Pod创建的请求时，会调用
自动注入服务  istio-sidecar-injector 生成 Sidecar 容器的描述并将其插入原  Pod的定义中，这
样，在创建的  Pod 内除了包括业务容器，还包括  Sidecar容器，这个注入过程对用户透明。

**3.7 其他组件**
除了以“istio” 为前缀的 Istio自有组件，在集群中一般还安装 Jaeger-agent、Jaeger-
collector 、Jaeger-query、Kiali、Prometheus 、Grafana、 Tracing、Zipkin等组件，这些组件提
供了Istio的调用链、监控等功能，可以选择安装来完成完整的服务监控管理功能。

4.在k8s平台安装 Istio
**4.1 准备安装 Istio是要的压缩包**
官网下载地址：
https://github.com/istio/istio/
官方访问相对较慢，我在课件提供了压缩包，大家最好用我的压缩包，这样做实验才不会出问题
**1、把压缩包上传到 k8s的控制节点xianchaomaster1 。手动解压：**

```bash
[root@xianchaomaster1 ~]# tar zxvf istio -1.10.1-linux-amd64.tar.gz
```

**2、切换到istio包所在目录下。 tar zxvf istio-1.10.1-linux-amd64.tar.gz 解压的软件包 包**
名是istio-1.10.1，则：
cd istio-1.10.1

 安装目录包含如下内容：
2）samples/ 目录下，有示例应用程序
3）bin/目录下，包含 istioctl 的客户端文件。 istioctl 工具用于手动注入 Envoy sidecar 代理。

**3、将istioctl 客户端路径增加到 path环境变量中， macOS 或 Linux 系统的增加方式如下：**
export PATH=$PWD/bin:$PATH
**4、把istioctl 这个可执行文件拷贝到 /usr/bin/ 目录**
cd /root/ istio-1.10.1/bin/
cp -ar istioctl /usr/bin/

**4.2 安装istio**
1.下载镜像：
安装istio需要的镜像 默认从官网拉取， 但是官网的镜像我们拉取会有问题 ，可以从课件下载镜
像，然后上传到自己 k8s集群的各个节点，通过 docker load -i手动解压 镜像：
docker load -i  examples -bookinfo -details.tar.gz
docker load -i  examples -bookinfo -reviews-v1.tar.gz
docker load -i  examples -bookinfo -productpage.tar.gz
docker load -i  examples -bookinfo -reviews-v2.tar.gz
docker load -i  examples -bookinfo -ratings.tar.gz
docker load -i  examples -bookinfo -reviews-v3.tar.gz
docker load -i  istio-1-10-1.tar.gz
docker load -i  engress-proxyv2-1-10-1.tar.gz
docker load -i  httpbin.tar.gz
2.安装
在k8s的控制节点xianchaomaster1 操作
istioctl install --set profile=demo -y
看到如下，说明 istio初始化完成：
Detected that your cluster does not support third party JWT authentication. Falling
back to less secure first party JWT. See https://istio.io/docs/ops/best -
practices/security/#configure -third-party-service-account-tokens for details.
- Applying manifest for component Base...
✔ Finished applying manifest for component Base.
- Applying manifest for component Pilot...
✔ Finished ap plying manifest for component Pilot.
  Waiting for resources to become ready...
  Waiting for resources to become ready...
- Applying manifest for component EgressGateways...
- Applying manifest for component IngressGateways...
- Applying manifest for comp onent AddonComponents...
✔ Finished applying manifest for component EgressGateways.
✔ Finished applying manifest for component IngressGateways.
✔ Finished applying manifest for component AddonComponents.

 ✔ Installation complete

3.验证istio是否部署成功
kubectl get pods -n istio-system
显示如下，说明部署成功
istio-egressgateway -d84f95b69 -5gtdc     1/1     Running   0          15h
istio-ingressgateway -75f6d79f48 -fhxjj   1/1     Running   0          15h
istiod-c9f6864c4 -nrm82                  1/1     Running   0          15h

4.卸载istio集群，暂时不执行，记住这个命令即可
istioctl  manifest generate --set profile =demo | kubectl delete -f -

**5、通过Istio部署在线书店 bookinfo**
**5.1 在线书店 功能介绍**
在线书店 -bookinfo
该应用由四个单独的微服务构成 ，这个应用模仿在线书店的一个分类，显示一本书的信息 ，页面上
会显示一本书的描述，书籍的细节（ ISBN、页数等），以及关于这本书的一些评论。

Bookinfo 应用分为四个单独的微服务
1）productpage 这个微服务会调用 details 和reviews两个微服务，用来生成页面 ；
2）details 这个微服务中包含了书籍的信息 ；
3）reviews 这个微服务中包含了书籍相关的评论 ，它还会调用 ratings 微服务；
4）ratings 这个微服务中包含了由书籍评价组成的评级信息。

reviews 微服务有3个版本
1）v1版本不会调 用ratings 服务；
2）v2版本会调用 ratings 服务，并使用 1到5个黑色星形图标来显示评分信息 ；
3）v3版本会调用 ratings 服务，并使用 1到5个红色星形图标来显示评分信息。

下图展示了这个应用的端到端架构

Bookinfo 应用中的几个微服务是由不同的语言编写的。这些服务对 istio并无依赖，但是构成了一
个有代表性的服务网格的例子：它由多个服务、多个语言构成，并且 reviews 服务具有多个版本。

**5.2 部署应用**
要在Istio中运行这一应用，无需对应用自身做出任何改变。  只要简单的在  Istio 环境中对服务
进行配置和运行，具体一点说就是把  Envoy sidecar 注入到每个服务之中。  最终的部署结果将如
下图所示：

 所有的微服务都和 Envoy sidecar 集成在一起，被集成服务所有的出入流量都被 envoy sidecar 所
劫持，这样就为外部控制准备了所需的  Hook，然后就可以利用 Istio控制平面为应用提供服务路
由、遥测数据收集以及策略实施等功能。

**5.3 启动应用服务**
1.进入istio安装目录。
2.istio默认自动注入  sidecar，需要为default 命名空间打上标签 istio-injection=enabled
kubectl label namespace default istio -injection =enabled
3.使用kubectl 部署应用
cd istio -1.10.1
kubectl apply -f samples/bookinfo/platform/kube/bookinfo.yaml
上面的命令会启动全部的四个服务，其中也包括了  reviews 服务的三个版本（ v1、v2 以及 v3）。
4.确认所有的服务和  Pod 都已经正确的定义和启动：
kubectl get services
显示如下
NAME                      TYPE        CLUSTER -IP       EXTERNAL -IP   PORT(S)
details                   ClusterIP   10.109.124.202   <none>        9080/TCP
productpage               Cl usterIP   10.102.89.129    <none>        9080/TCP
ratings                   ClusterIP   10.101.97.75     <none>        9080/TCP
reviews                   ClusterIP   10.100.105.33    <none>        9080/TCP
kubectl get pods
显示如下
NAME                              READY   STATUS    RESTARTS   AGE
details-v1-78d78fbddf -qssjb           2/2     Runnin g   0          73m
productpage -v1-85b9bf9cd7 -r699f     2/2     Running   0          73m
ratings-v1-6c9dbf6b45 -77kv7          2/2     Running   0          73m
reviews-v1-564b97f875 -2jtxq           2/2     Running   0          73m
reviews-v2-568c7c9d8f -f5css           2/2     Running   0          73m
reviews-v3-67b4988599 -fxfzx           2/2     Running   0          73m
tomcat-deploy-59664bcb6f -5z4nn      1/1     Running   0          22h
tomcat-deploy-59664bcb6f -cgjbn       1/1     Running   0          22h
tomcat-deploy-59664bcb6f -n4tqq      1/1     Running   0          22h

5.确认 Bookinfo 应用是否正在运行，在某个 Pod中用curl命令对应用发送请求，例如 ratings：
kubectl exec -it $(kubectl get pod -l app=ratings -o

```bash
jsonpath='{.items[0].metadata.name}') -c ratings -- curl productpage:9080/produ ctpage |
grep -o "<title>.*</title>"
```

显示如下：

6.确定Ingress 的IP和端口

 现在Bookinfo 服务已经启动并运行， 你需要使应用程序可以从 Kubernetes 集群外部访问，例如从
浏览器访问 ，那可以用Istio Gateway 来实现这个目标。
1）为应用程序定义 gateway 网关：
kubectl apply -f samples/bookinfo/networking/bookinfo -gateway.yaml
2）确认网关创建完成：
kubectl get gateway
显示如下：
NAME               AGE
bookinfo -gateway   2m18s
3）确定ingress ip和端口
执行如下指令，明确自身  Kubernetes 集群环境支持外部负载均衡：
kubectl get svc istio -ingressgateway -n istio-system

如果EXTERNAL -IP值已设置，说明环境正在使用外部负载均衡，可以用其为 ingress gateway 提供
服务。 如果EXTERNAL -IP值为<none>（或持续显示 <pending> ）， 说明环境没有提供外部负载均
衡，无法使用 ingress gateway 。在这种情况下，你可以使用服务的 NodePort访问网关。

若自身环境未使用外部负载均衡器，需要通过  node port 访问。可以通过以下命令获取 Istio
Gateway 的地址：

export INGRESS_PORT=$(kubectl -n istio-system get service istio -ingressgateway -o

```bash
jsonpath='{.spec.ports[?(@.name=="http2")].nod ePort}')

export SECURE_INGRESS_PORT=$(kubectl -n istio-system get service istio -ingressgateway -
o jsonpath='{.spec.ports[?(@.name=="https")].nodePort}')
```

4）设置GATEWAY_ URL

```bash
INGRESS_HOST=192.168.40.180
#192.168.40.180 是安装istio的机器，即 k8s控制节点 xianchaomaster1 的ip
export GATEWAY_URL =$INGRESS_HOST:$INGRESS_PORT
```
echo $GATEWAY_URL 显示如下：
**192.168.40.180 :30871**

确认可以从集群外部访问应用
可以用curl命令来确认是否能够从集群外部访问  Bookinfo 应用程序：
curl -s http:// ${GATEWAY_URL} /productpage | grep -o "<title>.*</title>"
显示如下：

 还可以用浏览器打开网址 http://$GATEWAY_URL/productpage ，也就是
**192.168.40.180 :30871/productpage 来浏览应用的  Web 页面。如果刷新几次应用的页面，就会看**
到 productpage  页面中会随机展示  reviews 服务的不同版本的效果（红色、黑色的星形或者
没有显示）。

通过istio的ingressgateway 访问，官网：
https://istio.io/docs/examples/bookinfo/#determine -the-ingress-ip-and-port

扩展：添加外部 IP-extertal -IP

```bash
[root@xianchaomaster1 ~]# kubectl edit svc istio-ingressgateway -n istio-system

[root@xianchaomaster1 ~]# kubectl get  service istio -ingressgateway -n istio-system
```

在windows 机器上的 C:\Windows\System32 \drivers\etc\hosts里面最后一行 加上如下域名解析：
**192.168.40.180 productpage.xianchao.cn**
在浏览器访问：
http://productpage.xianchao.cn/productpage

**5.4 卸载bookinfo 服务**
可以使用下面的命令来完成应用的删除和清理了：
1.删除路由规则，并销毁应用的  Pod
sh samples/bookinfo/platform/kube/cleanup.sh
2.确认应用已经关停
kubectl get virtualservices     #-- there should be no virtual services
kubectl get destinationrules   #-- there should be n o destination rules
kubectl get gateway           #-- there should be no gateway
kubectl get pods               #-- the Bookinfo pods should be deleted

**6、通过Istio实现灰度发布**
**6.1 什么是灰度发布？**
灰度发布也叫金丝雀部署  ，是指通过控制流量的比例，实现新老版本的逐步更替。
比如对于服务 A 有 version1 、 version2 两个版本  ， 当前两个版本同时部署，但是 version1 比例
90% ，version2 比例10% ，看运行效果，如果效果好逐步调整流量占比  80～20 ，70～
30 ·····10 ～90 ，0，100 ，最终version1 版本下线。

灰度发布的特点 ：
1）新老板共存
2）可以实时根据反馈动态调整占比
3）理论上不存在服务完全宕机的情况。
4）适合于服务的平滑升级与动态更新。

**6.2 使用istio进行金丝雀发布**

下面实验需要的镜像包在课件，把 canary-v2.tar.gz 和canary-v1.tar.gz 上传到k8s工作节点，手动
解压：

```bash
[root@xianchao node1 ~]# docker load -i canary -v2.tar.gz
[root@xianchao node1 ~]# docker load -i canary-v1.tar.gz
```

创建金丝雀服务
cat deployment.y aml，内容如下：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: appv1
  labels:
    app: v1
spec:
  replicas: 1
  selector:
    matchLabels:
      app: v1
      apply: canary
  template:
    metadata:
      labels:
        app: v1
        apply: canary
    spec:
      containers:
      - name: nginx
        image: xianchao /canary:v1
        ports:
        - containerPort: 80
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: appv2
  labels:
    app: v2
spec:
  replicas: 1
  selector:
    matchLabels:
      app: v2
      apply: canary
  template:
    metadata:
      labels:
        app: v2

         apply: canary
    spec:
      containers:
      - name: nginx
        image: xianchao /canary:v2
        ports:
        - containerPort: 80

```
更新：
kubectl apply -f deployment.y aml

创建service
cat service.yaml 文件，内容如下：

```yaml
apiVersion: v1
kind: Service
metadata:
  name: canary
  labels:
    apply: canary
spec:
  selector:
    apply: canary
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80

```
更新service.yaml文件
kubectl apply -f service.yaml

创建gateway
cat gateway.yaml文件，内容如下：

```yaml
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: canary -gateway
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:

       number: 80
      name: http
      protocol: HTTP
    hosts:
- "*"

```
更新gateway.yaml
kubectl apply -f gateway.yaml
创建virtualservice
cat virtual.yaml ，内容如下：

```yaml
apiVersion: networking.istio.io/v1beta1
kind: Virt ualService
metadata:
  name: canary
spec:
  hosts:
  - "*"
  gateways:
  - canary-gateway
  http:
  - route:
    - destination:
        host: canary.default.svc.cluster.local
        subset: v1
      weight: 90
    - destination:
        host: canary.default.svc.cluster.local
        subset: v2
      weight: 10
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: canary
spec:
  host: canary.default.svc.cluster.local
  subsets:
  - name: v1
    labels:
      app: v1
  - name: v2
    labels:

       app: v2
```
更新virtual.yaml文件
kubectl apply -f virtual.yaml

（5）获取Ingress_ port:
kubectl -n istio-system get service istio -ingressgateway -o

```bash
jsonpath='{.spec.ports[?(@.name=="http2")].nodePort}'
```

显示结果是 30871
验证金丝雀发布效果：
for i in `seq 1 100`; do curl 192.168.40.1 80:30871;done > 1.txt
打开1.txt可以看到结果有 90次出现v1，10次出现canary-v2,符合我们预先设计的流量走向。

**7、istio核心资源解读**
官网：
https://istio.io/latest/docs/concepts/traffic -management/

**7.1 Gateway**
在Kubernetes 环境中， Ingress controller 用于管理进入集群的流量。在 Istio服务网格中  Istio
Ingress Gateway 承担相应的角色，它使用新的配置模型（ Gateway 和 VirtualServices ）完成流量管理
的功能。通过下图做一个总的描述。

**1、用户向某端口发出请求**
**2、负载均衡器监听端口，并将请求转发到集群中的某个节点上。 Istio Ingress Gateway Service**

 会监听集群节点端口的请求
**3、Istio Ingress Gateway Service 将请求交给 Istio Ingress Gateway Pod 处理。**
IngressGateway Pod 通过 Gateway 和 VirtualService 配置规则处理请求。其中， Gateway 用来配置
端口、协议和证书； VirtualService 用来配置一些路由信息（找到请求对应处理的服务 App Service ）
**4、Istio Ingress Gateway Pod 将请求转给 App Service**
**5、最终的请求会交给 App Service 关联的App Deployment 处理**

cat gateway.yaml

```yaml
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: canary -gateway
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
- "*"

```
网关是一个运行在网格边缘的负载均衡器， 用于接收传入或传出的 HTTP/TCP 连接。主要工作是接受
外部请求， 把请求转发到内部服务 。网格边缘的 Ingress 流量，会通过对应的  Istio IngressGateway
Controller 进入到集群内部 。

在上面这个yaml里我们配置了一个监听 80端口的入口网关，它会将 80端口的http流量导入到集
群内对应的 Virtual Service 上。

> **注意：hosts:**
- "*"
*表示通配符， 通过任何域名都可以访问

**7.2 VirtualService**
VirtualService 是Istio流量治理的一个核心配置，可以说是 Istio流量治理中最重要、最复杂
的。VirtualService 在形式上表示一个虚拟服务，将满足条件的流量都转发到对应的服务后端，这个服
务后端可以是一个服务，也可以是在 DestinationRule 中定义的服务的子集。
cat virtual.yaml

```yaml
apiVersion:   networking.istio.io/v1beta1
kind: VirtualService

 metadata:
  name: canary
spec:
  hosts:
  - "*"
  gateways:
  - canary-gateway
  http:
  - route:
    - destination:
        host: canary.default.svc.cluster.local
        subset: v1
      weight: 90
    - destination:
        host: canary.default.svc.cluster.local
        subset: v2
      weight: 10

```
这个虚拟服务会收到上一个 gateway 中所有80端口来的 http流量。

VirtualService 主要由以下部分组成
**1、hosts：虚拟主机名称，如果在  Kubernetes 集群中，则这个主机名可以是 service 服务名。**
hosts字段列出了 virtual service 的虚拟主机。它是客户端向服务发送请求时使用的一个或多个地
址，通过该字段提供的地址访问 virtual service ，进而访问后端服务。在集群内部 (网格内)使用时通常
与kubernetes 的Service 同名；当需要在集群外部 (网格外)访问时，该字段为 gateway 请求的地址，即
与gateway 的hosts字段相同。
hosts:
- reviews
virtual service 的主机名可以是 IP地址、DNS名称，也可以是短名称 (例如Kubernetes 服务短名
称)，该名称会被隐式或显式解析为全限定域名（ FQDN） ，具体取决于 istio依赖的平台。可以使用前缀
通配符（ “*”）为所有匹配的服务创建一组路由规则。 virtual service 的hosts不一定是 Istio服务
注册表的一部分，它们只是虚拟目的地，允许用户为网格无法路由到的虚拟主机建立流量模型。

virtual service 的hosts短域名在解析为完整的域名时，补齐的 namespace 是VirtualService 所
在的命名空间，而非 Service 所在的命名空间。如上例的 hosts会被解析为：
reviews.default.svc.cluster.l ocal。

hosts:
  - "*"
*表示通配符，任何域名都可以
如在虚拟机配置 hosts文件
**192.168.40.180 xianchaomaster1 hello.com.cn**
这样就可以 在虚拟机 通过域名 hello.com.cn 访问istio内部的服务了

扩展：virtualservice 配置路由规则
路由规则的功能是：满足 http.match 条件的流量都被路由到 http.route.destination ，执行重定向
（HTTPRedirect ） 、重写（ HTTPRewrite ） 、重试（ HTTPRetry ） 、故障注入（ HTTPFaultInjection ） 、跨站
（CorsPolicy ）策略等。 HTTPRoute 不仅可以做路由匹配，还可以做一些写操作来修改请求本身。
如下：

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: reviews
spec:
  hosts:
  - reviews
  http:
  - match:
    - headers:
        end-user:
          exact: jason
    route:
    - destination:
        host: reviews
        subset: v2
  - route:
    - destination:
        host: reviews
        subset: v3

```
在 http 字段包含了虚拟服务的路由规则，用来描述匹配条件和路由行为，它们把  HTTP/1.1 、
HTTP2 和 gRPC 等流量发送到  hosts 字段指定的目标 。

示例中的第一个路由规则有一个条件，以  match 字段开始 。此路由接收来自 ”jason“ 用户的所
有请求，把请求发送到 destination 指定的v2子集。

**7.2.1 路由规则优先级**
在上面例子中， 不满足第一个路由规则的流量均流向一个默认的目标，该目标在第二条规则中指
定。因此，第二条规则没有  match 条件，直接将流量导向  v3 子集。

**7.2.2 多路由规则解读**
详细配置可参考：
https://istio.io/latest/zh/docs/reference/con fig/networking/virtual -
service/#HTTPMatchRequest

```yaml
apiVersion: networking.istio.io/v1alpha3

 kind: VirtualService
metadata:
  name: bookinfo
spec:
  hosts:
    - bookinfo.com
  http:
  - match:
    - uri:
        prefix: /reviews
    route:
    - destination:
        host: reviews
  - match:
    - uri:
        prefix: /ratings
    route:
    - destination:
        host: ratings

```
路由规则是将特定流量子集路由到指定目标地址的工具。可以在流量端口、 header 字段、URI 等内
容上设置匹配条件。例如， 上面这个虚拟服务让用户发送请求到两个独立的服务： ratings 和
reviews，相当于访问 http://bookinfo.com/ ratings 和http://bookinfo.com/
reviews，虚拟服务规则根据请求的  URI 把请求路由到特定的目标地址。

**2、Gateway：流量来源网关。**
**3、路由：**
路由的destination 字段指定了匹配条件的流量的实际地址。与 virtual service 的主机不同，该
host必须是存在于 istio的服务注册表 (如kubernetes services ，consul services 等)中的真实目的地
或由ServiceEntries 声明的hosts，否则Envoy不知道应该将流量发送到哪里。它可以是一个带代理的
网格服务或使用 service entry 添加的非网格服务。在 kubernetes 作为平台的情况下， host表示名为
kubernetes 的service 名称：
  - destination:
        host: canary.default.svc.cluster.local
        subset: v1
      weight: 90

**7.3 DestinationRule**
destination rule是istio流量路由功能的重要组成部分。一个 virtual service 可以看作是如何
将流量分发给特定的目的地，然后调用 destination rule 来配置分发到该目的地的流量。 destination
rule在virtual service 的路由规则之后起作用 (即在virtual service 的math->route-destination 之

 后起作用，此时流量已经分发到真实的 service 上)，应用于真实的目的地。
可以使用 destination rule 来指定命名的服务子集，例如根据版本对 服务的实例进行分组，然后通
过virtual service 的路由规则中的服务子集将控制流量分发到不同服务的实例中。

cat DestinationRule. yaml

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: canary
spec:
  host: canary.default.svc.cluster.local
  subsets:
  - name: v1
    labels:
      app: v1
  - name: v2
    labels:
      app: v2

```
在虚拟服务中使用 Hosts配置默认绑定的路由地址，用 http.route 字段，设置 http进入的路由地
址，可以看到， 上面导入到了目标规则为 v1和v2的子集。

v1子集对应的是 具有如下标签的 pod：
selector:
    matchLabels:
      app: v1

流量控制流程：
Gateway->VirtaulService ->TCP/HTTP Router ->DestinationWeight ->Subset:Port

**8、istio核心功能演示**
**8.1 断路器**
官网：
https://istio.io/latest/zh/docs/tasks/traffic -management/circuit -breaking/

断路器是创建弹性微服务应用程序的重要模式。断路器使应用程序可以适应网络故障和延迟等网络
不良影响。

测试断路器：
**1、在k8s集群创建后端服务**

```bash
[root@xianchaomaster1 ~]# cd istio -1.10.1
[root@xianchaomaster1 istio -1.10.1]# cat samples/httpbin/httpbin.yaml

```

```yaml
 apiVersion: v1
kind: ServiceAccount
metadata:
  name: httpbin
---
apiVersion: v1
kind: Service
metadata:
  name: httpbin
  labels:
    app: httpbin
    service: httpbin
spec:
  ports:
  - name: http
    port: 8000
    targetPort: 80
  selector:
    app: httpbin
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: httpbin
spec:
  replicas: 1
  selector:
    matchLabels:
      app: httpbin
      version: v1
  template:
    metadata:
      labels:
        app: httpbin
        version: v1
    spec:
      serviceAccountName: httpbin
      containers:
      - image: docker.io/kennethreitz/httpbin
        imagePullPolicy: IfNotPresent
        name: httpbin
        ports:
        - containerPort: 80

 #把httpbin.tar.gz 上传到xianchaonode1 节点，手动解压：
```

```bash
[root@xianchaonode1 ~]# docker load -i httpbin.tar.gz
[root@xianch aomaster1 istio -1.10.1]# kubectl apply -f samples/httpbin/httpbin.yaml
#该httpbin 应用程序充当后端服务。
```

**2、配置断路器**

```bash
#创建一个 目标规则 ，在调用 httpbin 服务时应用断路器设置：
[root@xianchaomaster1 istio -1.10.1]# vim destination.yaml
```

```yaml
apiVersion:  networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: httpbin
spec:
  host: httpbin
  trafficPolicy:
    connectionPool:
#连接池（ TCP | HTTP ）配置，例如：连接数、并发请求等
      tcp:
        maxConnections: 1
#TCP连接池中的最大连接请求数，当超过这个值，会 返回503代码。如两个请求过来，就会有一个
```
请求返回 503。
      http:
        http1MaxPendingRequests: 1
#连接到目标主机的最大挂起 请求数，也就是待处理请求 数。这里的目标指的是  virtualservice 路
由规则中配置的  destination 。
        maxRequestsPerConnection: 1
#连接池中每个连接最多处理 1个请求后就关闭，并根据需要重新创建连接池中的连接
    outlierDetection:
#异常检测配置，传统意义上的熔断配置，即对规定时间内服务错误数的监测
      consecutiveGatewayErrors: 1
#连续错误数 1，即连续返回 502-504状态码的 Http请求错误数
      interval: 1s
#错误异常的扫描间隔 1s，即在interval （1s）内连续发生 consecutiveGatewayErrors （1）个错
误，则触发服务熔断
      baseEjectionTime: 3m
#基本驱逐时间 3分钟，实际驱逐时间为 baseEjectionTime* 驱逐次数
      maxEjectionPercent: 100
#最大驱逐百分比 100%

```bash
[root@xianchaomaster1 istio -1.10.1]# kubectl apply -f destination.yaml
destinationrule.networking.istio.io/httpbin created
```

**3、添加客户端访问 httpbin 服务**

 创建一个客户端以将流量发送给 httpbin 服务。该客户端是一个简单的负载测试客户端， Fortio可
以控制连接数，并发数和 HTTP调用延迟。使用此客户端来 “跳闸”在DestinationRule 中设置的断路器
策略。

```bash
#通过执行下面的命令部署 fortio客户端：
#把fortio.tar.gz 上传到xianchaonode 1节点，手动解压：
[root@xianchaonode1 ~]# docker load -i fortio.tar.gz
[root@xianchaomaster1 istio -1.10.1]# kubectl apply -f  samples/httpbin/sample -
client/fortio -deploy.yaml

#通过kubectl 执行下面的命令，使用 fortio客户端工具调用 httpbin：
[root@xianchaomaster1 istio -1.10.1]# kubectl get pods
NAME                              READY   STATUS    RE STARTS   AGE
appv1-77b5cbd5cc -bmch2            2/2     Running   0          28m
appv2-f78cb577 -n7rhc              2/2     Running   0          28m
details-v1-847c7999fb -htd2z       2/2     Running   0          28m
fortio-deploy-576dbdfbc4 -z28m7    2/2     Running   0          3m32s
httpbin-74fb669cc6 -hqtzl          2/2     Running   0          15m
productpage -v1-5f7cf79d5d -6d4lx   2/2     Running   0          28m
ratings-v1-7c46bc6f4d -sfqnz       2/2     Running   0          28m
reviews-v1-549967c688 -pr8gh       2/2     Running   0          28m
reviews-v2-cf9c5bfcd -tn5z5        2/2     Running   0          28m
reviews-v3-556dbb4456 -dxt4r       2/2     Running   0          28m

[root@xianchaomaster1 istio -1.10.1]# kubectl exec  fortio -deploy-576dbdfbc4 -z28m7   -c
fortio -- /usr/bin/fortio curl  http://httpbin:8000/get
#显示如下：
HTTP/1.1 200 OK
server: envoy
date: Mon, 03 May 2021 02:28:06 GMT
content-type: application/json
content-length: 622
access-control-allow-origin: *
access-control-allow-credentials: true
x-envoy-upstream -service-time: 2

{
  "args": {},
  "headers": {
    "Content -Length": "0",
    "Host": "httpbin:8000",
    "User-Agent": "fortio.org/fortio -1.11.3",
    "X-B3-Parentspanid": "4631e62a6cd0b167",
    "X-B3-Sampled": "1",

     "X-B3-Spanid": "6d20afff1671aa89",
    "X-B3-Traceid": "6f4ddb61363d04d54631e62a6cd0b167",
    "X-Envoy-Attempt-Count": "1",
    "X-Forwarded -Client-Cert":
"By=spiffe://cluster.local/ns/default /sa/httpbin;Hash=498edf0dcb7f6e74f40735869a9912eca62d6
1fb21dbc190943c1c19dbf01c18;Subject= \"\";URI=spiffe://cluster.local/ns/default/sa/default"
  },
  "origin": "127.0.0.1",
  "url": "http://httpbin:8000/get"
}
```

**4、触发断路器**
在DestinationRule 设置中，指定了 maxConnect ions: 1 和 http1MaxPendingRequests: 1 。这些
规则表明，如果超过一个以上的连接并发请求，则 istio-proxy在为进一步的请求和连接打开路由时，
应该会看到下面的情况  。
以两个并发连接（ -c 2）和发送 20个请求（ -n 20）调用服务：

```bash
[root@xianchaomaster1 istio -1.10.1]# kubectl exec -it fortio -deploy-576dbdfbc4 -z28m7  -
c fortio -- /usr/bin/fortio load  -c 2 -qps 0 -n 20 -loglevel Warning
http://httpbin:8000/get

#显示如下：
02:31:00 I logger.go:127> Log level is now 3 Warning (was 2  Info)
Fortio 1.11.3 running at 0 queries per second, 6 ->6 procs, for 20 calls:
http://httpbin:8000/get
Starting at max qps with 2 thread(s) [gomax 6] for exactly 20 calls (10 per thread + 0)
02:31:00 W http_client.go:693> Parsed non ok code 503 (HTTP/1.1 503)
02:31:00 W http_client.go:693> Parsed non ok code 503 (HTTP/1.1 503)
02:31:00 W http_client.go:693> Parsed non ok code 503 (HTTP/1.1 503)
02:31:00 W http_client.go:693> Parsed non ok code 503 (HTTP/1.1 503)
02:31:00 W http_client.go:693> Parsed non ok  code 503 (HTTP/1.1 503)
02:31:00 W http_client.go:693> Parsed non ok code 503 (HTTP/1.1 503)
02:31:00 W http_client.go:693> Parsed non ok code 503 (HTTP/1.1 503)
02:31:00 W http_client.go:693> Parsed non ok code 503 (HTTP/1.1 503)
02:31:00 W http_client.g o:693> Parsed non ok code 503 (HTTP/1.1 503)
02:31:00 W http_client.go:693> Parsed non ok code 503 (HTTP/1.1 503)
02:31:00 W http_client.go:693> Parsed non ok code 503 (HTTP/1.1 503)
02:31:00 W http_client.go:693> Parsed non ok code 503 (HTTP/1.1 503)
02:31:00 W http_client.go:693> Parsed non ok code 503 (HTTP/1.1 503)
02:31:00 W http_client.go:693> Parsed non ok code 503 (HTTP/1.1 503)
02:31:00 W http_client.go:693> Parsed non ok code 503 (HTTP/1.1 503)
02:31:00 W http_client.go:693> Parsed non ok code 503  (HTTP/1.1 503)
Ended after 69.506935ms : 20 calls. qps=287.74
Aggregated Function Time : count 20 avg 0.0054352091 +/ - 0.01077 min 0.000474314 max

 0.04968864 sum 0.108704183
# range, mid point, percentile, count
>= 0.000474314 <= 0.001 , 0.000737157 , 35. 00, 7
> 0.001 <= 0.002 , 0.0015 , 50.00, 3
> 0.002 <= 0.003 , 0.0025 , 65.00, 3
> 0.004 <= 0.005 , 0.0045 , 75.00, 2
> 0.005 <= 0.006 , 0.0055 , 85.00, 2
> 0.007 <= 0.008 , 0.0075 , 90.00, 1
> 0.016 <= 0.018 , 0.017 , 95.00, 1
> 0.045 <= 0.0496886 , 0.0473443 , 100.00, 1
# target 50% 0.002
# target 75% 0.005
# target 90% 0.008
# target 99% 0.0487509
# target 99.9% 0.0495949
Sockets used: 16 (for perfect keepalive, would be 2)
Jitter: false
Code 200 : 4 (20.0 %)
Code 503 : 16 (80.0 %)
#只有20%成功了，其余的都断开了
Response Header Sizes : count 20 avg 46 +/ - 92 min 0 max 230 sum 920
Response Body/Total Sizes : count 20 avg 292.8 +/ - 279.6 min 153 max 852 sum 5856
All done 20 calls (plus 0 warmup) 5.435 ms avg, 287.7 qps
```

**8.2 超时**

在生产环境中经常会碰到由于调用方等待下游的响应过长， 堆积大量的请求阻塞了自身服务，造成
雪崩的情况，通过通过超时处理来避免由于无限期等待造成的故障，进而增强服务的可用性 ，Istio 使
用虚拟服务来优雅实现超时处理。
下面例子 模拟客户端调用  nginx，nginx 将请求转发给  tomcat。nginx 服务设置了超时时间为 2
秒，如果超出这个时间就不在等待，返回超时错误 。tomcat服务设置了响应时间延迟 10秒，任何请求都
需要等待 10秒后才能返回 。client 通过访问  nginx 服务去反向代理  tomcat服务，由于  tomcat服务
需要10秒后才能返回，但 nginx 服务只等待 2秒，所以客户端会提示超时错误 。

#把busybox.tar.gz 、 nginx.tar.gz 、 tomcat-app.tar.gz 上传到xianchaonode 1节点，手动解
压：

```bash
[root@xianchaonode1 ~]# docker load -i nginx.tar.gz
[root@xianchaonode1 ~]# docker load -i busybox.tar.gz
[root@xianchaonode1 ~]# docker load -i tomcat -app.tar.gz
[root@xianchaomaster1 ~]# mkdir /root/timeout
[root@xianchaomaster1 ~]# cd /root/timeout/
[root@xianchaomaster1 timeout]# cat nginx -deployment.yaml
---

```

```yaml
 apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  labels:
    server: nginx
    app: web
spec:
  replicas: 1
  selector:
    matchLabels:
      server: nginx
      app: web
  template:
    metadata:
      name: nginx
      labels:
        server: nginx
        app: web
    spec:
      containers:
      - name: nginx
        image: nginx:1.14 -alpine
        imagePullPolicy: IfNotPresent
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tomcat
  labels:
    server: tomcat
    app: web
spec:
  replicas: 1
  selector:
    matchLabels:
      server: tomcat
      app: web
  template:
    metadata:
      name: tomcat
      labels:
        server: tomcat

         app: web
    spec:
      containers:
      - name: tomcat
        image: docker.io/kubeguide/tomcat -app:v1
        imagePullPolicy: IfNotPresent

```

```bash
[root@xianchaomaster1 timeout]# cat nginx -tomcat-svc.yaml
---
```

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx -svc
spec:
  selector:
    server: nginx
  ports:
  - name: http
    port: 80
    targetPort: 80
    protocol: TCP
---
apiVersion: v1
kind: Service
metadata:
  name: tomcat -svc
spec:
  selector:
    server: tomcat
  ports:
  - name: http
    port: 8080
    targetPort: 8080
    protocol: TCP

```

```bash
[root@xianchaomaster1 timeout]# cat virtual -tomcat.yaml
---
```

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: nginx -vs
spec:
  hosts:

   - nginx-svc
  http:
  - route:
    - destination:
        host: nginx -svc
    timeout: 2s
---
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: tomcat -vs
spec:
  hosts:
  - tomcat-svc
  http:
  - fault:
      delay:
        percentage:
          value: 100
        fixedDelay: 10s
    route:
    - destination:
        host: tomcat -svc

#virtual-tomcat.yaml资源清单重点知识讲解
```
第一：故障注入：
http:
- fault:
    delay:
      percentage:
      value: 100
   fixedDelay: 10s
该设置说明每次调用  tomcat-svc 的 k8s service ，都会延迟 10s才会调用。
第二：调用超时：
hosts:
- nginx-svc
  http:
  - route:
    - destination:
      host: nginx -svc
    timeout: 2s
该设置说明调用  nginx-svc 的 k8s service ，请求超时时间是  2s。

 #部署tomcat、nginx服务
需要对nginx-deployment.yaml 资源文件进行  Istio 注入，将  nginx、tomcat 都放入到网格中。
可以采用 手工注入  Istio 方式。

```bash
[root@xianchaomaster1 timeout]# kubectl apply -f nginx-deployment.yaml
```
执行成功后，通过  kubectl get pods 查看 Istio 注入情况：

```bash
[root@xianchaomaster1 timeout]# kubectl get pods
NAME                              READY   STATUS             RESTARTS   AGE
nginx-tomcat-7dd6f74846-48g9f      2/2     Running   0          6m36s
tomcat-86ddb8f5c9 -h6jdl            2/2     Running              0           53s

#部署nginx和tomcat的service
[root@xianchaomaster1 timeout]# kubectl apply -f nginx-tomcat-svc.yaml
#部署虚拟服务
[root@xianchaomaster1 timeout]# kubectl apply -f virtual -tomcat.yaml

#设置超时 时间
[root@xianchaomaster1 timeout]# kubectl exec -it nginx-tomcat-7dd6f74846 -48g9f --  sh
# apt-get update
# apt-get install vim -y
/ # vim /etc/nginx/conf.d/default.conf

proxy_pass http://tomcat -svc:8080;
proxy_http_version  1.1;
```
编辑完后，再执行如下语句验证配置和让配置生效：
/ # nginx -t
/ # nginx -s reload

这样，整个样例配置和部署 都完成了 。

#验证超时
登录client，执行如下语句：

```bash
[root@xianchaomaster1 timeout]# kubectl run busybox --image busybox:1.28 --
restart=Never --rm -it busybox -- sh
/ # time wget -q -O - http://nginx -svc
wget: server returned error: HTTP/1.1 408 Request Timeout
Command exited with non -zero status 1
real 0m 2.02s
user 0m 0.00s
sys 0m 0.00s

/ # while true; do wget -q -O - http://nginx -svc; done
wget: server returned error: HTTP/1.1 504 Gateway Timeout
wget: server returned error: HTTP/1.1 504 Gateway Timeout
wget: server returned error: HTTP/1.1 504 Gateway Timeout
wget: server returned error: HTTP/1.1 504 Gateway Timeout
wget: server returned error: HTTP/1.1 408 Request Timeout
```

每隔2秒，由于  nginx 服务的超时时间到了而  tomcat未有响应，则提示返回超时错误。

验证故障注入效果，执行如下语句：
/ # time wget -q -O - http://tomcat -svc
wget: server returned error: HTTP/1.1 503 Service Unavailable
Command exited with non -zero status 1
real 0m 10.02s
user 0m 0.00s
sys 0m 0.01s
执行之后 10s才会有结果

**8.3 故障注入和 重试**
Istio 重试机制就是如果调用服务失败， Envoy 代理尝试连接服务的最大次数。而默认情况下，
Envoy 代理在失败后并不会尝试重新连接服务，除非我们启动  Istio 重试机制。
下面例子 模拟客户端调用  nginx，nginx 将请求转发给  tomcat。tomcat 通过故障注入而中止对外
服务，nginx 设置如果访问  tomcat 失败则会重试  3 次。

```bash
[root@xianchaomaster1 attemp]# cd /root/timeout/
[root@xianchaomaster1 timeout]# kubectl delete -f .
[root@xianchaomaster1 timeout]# kubectl apply -f nginx-deployment.yaml
[root@xianchaomaster1 timeout]# kubectl apply -f nginx-tomcat-svc.yaml
[root@xianchaomaster1 ~]# kubectl get pods
NAME                              READY   STATUS    RESTARTS   AGE
busybox                           2/2     Running   0          55m
nginx-7f6496574c -zbtqj            2/2     Running   0          10m
tomcat-86ddb8f5c9 -dqxcq           2/2     Running   0          35m

[root@xianchaomaster1 timeout]# cat virtual -attempt.yaml
---
```

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: nginx -vs
spec:
  hosts:

   - nginx-svc
  http:
  - route:
    - destination:
        host: nginx -svc
    retries:
      attempts: 3
      perTryTimeout: 2s
---
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: tomcat -vs
spec:
  hosts:
  - tomcat-svc
  http:
  - fault:
      abort:
        percentage:
          value: 100
        httpStatus : 503
    route:
    - destination:
        host: tomcat -svc
```

```bash
[root@xianchaomaster1 timeout]# kubectl apply -f virtual -attempt.yaml
```

虚拟服务 资源清单解读 ：
第一：故障注入。该虚拟服务的作用对象就是  tomcat-svc。使用此故障注入后，在网格中该
tomcat 就是不可用的。
abort:
        percentage:
          value: 100
        httpStatus: 503

abort是模拟tomcat服务始终不可用， 该设置说明每次调用  tomcat-svc 的 k8s service ，100%都
会返回错误状态码 503。

第二：调用超时：
hosts:
- nginx-svc
  http:
  - route:

     - destination:
      host: nginx -svc
    reties:
      attempts: 3
      perTryTimeout: 2s
该设置说明调用  nginx-svc 的 k8s service ，在初始调用失败后最多重试  3 次来连接到服务子
集，每个重试都有  2 秒的超时。

```bash
[root@xianchaomaster1 timeout]# kubectl exec -it nginx -tomcat-7dd6f74846 -rdqqf --
/bin/sh
# apt-get update
# apt-get install vim -y
/ # vi /etc/nginx/conf.d/default.conf

/ # nginx -t
/ # nginx -s reload

#验证重试是否 生效
[root@xianchaomaster1 timeout]#  kubectl run busybox --image busybox:1.28 --
restart=Never --rm -it busybox -- sh

/ # wget -q -O - http://nginx -svc

[root@xianchaomaster1 timeout]# kubectl logs -f nginx-tomcat-7dd6f74846 -rdqqf  -c
istio-proxy
#执行结果如下：
```

由上图可知，重试设置生效。

**9、分布式追踪系统 -jaeger**
1.什么是分布式追踪 ？

 分布式追踪最早由谷歌的 Dapper 普及开来，它本质上 是具有在微服务的整个生命周期中追踪请求
的能力。 分布式追踪（ Distributed Tracing ）主要用于记录整个请求链的信息。

2.为什么要分布式追踪？
当业务微服务化后，一次业务请求，可能会涉及到多个微服务，分布式跟踪可以对跨多个分布式服务
网格的 1个请求进行追踪分析，并通过可视化的方式深入地了解请求的延迟，序列化和并发，充分地了解
服务流量实况， 从而快速地排查和定位问题 。在微服务应用中，一个完整的业务往往需要调用多个服务才
能完成，服务之间就产生了交互。当出现故障时，如何找到问题的根源非常重要。 追踪系统可以清晰地展
示出请求的整个调用链以及每一步的耗时，方便查找问题所在。

3.分布式追踪系统 -jaeger
Jaeger 是一个开源的分布式追踪系统，它可以在复杂的 分布式系统中进行监控和故障排查。 Jaeger
的主要功能包括分布式请求监控、性能调优、故障分析和服务依赖分析等。

Jaeger 组件介绍：
jaeger -agent ：
负责发送的进程，对 spans 进行处理并发送给 collector ，监听 spans 的UDP 发送。这层作为基
础组件部署 在主机上， Agent 将Client Library 和Collector 解耦，为 ClientLibrary 屏蔽了路由和发
现Collector 的细节。

jaeger -collector ：
收集追踪  spans ，并通过管道对追踪数据进行 处理。当前的管道支持追踪的验证、索引、转换，最
后存储数据

jaeger -query ：
从存储中检索追踪信息并通过  UI 展示

data store ：
追踪信息的存储

4.使用 jaeger

kubectl get svc -n istio -system | grep jaeger

显示如下：
jaeger -agent                ClusterIP   None             <none>
5775/UDP ,6831/UDP ,6832/UDP
55d
jaeger -collector            ClusterIP   10.99.194.57     <none>
14267/TCP ,14268/TCP ,14250/TCP
55d
jaeger -collector -headless   ClusterIP   None             <none>

 14250/TCP
55d
jaeger -query                ClusterIP   10.107.192.115   <none>        16686/TCP

修改 jaeger -query 的type 类型为 nodePort
kubectl edit svc jaeger -query -n istio -system

把type: ClusterIP 变成 type: NodePort

kubectl get svc -n istio -system | grep jaeger -query

显示如下：
jaeger -query                NodePort    10.107.192.115   <none>
16686:31450/TCP

在浏览器访问：
**192.168. 40.180:31450**
5.查看追踪数据
在Jaeger 左侧版面的 Service 下拉列表中选择 v1.default ，单击 Find Traces 按钮，会看到如 下
图所示：

单击右侧的 URL 进入详细页，可以看到具体的服务调用情况，并且能够了解每个服务的耗时 。

**6. 追踪上下文传递**
Istio 利用 Envoy 的分布式追踪 功能提供了开箱即用的追踪集成。确切地说， Istio 提供了安装各
种追踪后端服务的选项，并且通过配置代理来自动发送追踪  span 到追踪后端服务。 尽管 Istio 代理能
够自动发送  span ，但是他们需要一些附加线索才能将整个追踪链路关联到一起。所以当代理发送  span
信息的时候，应用需要 附加适当的  HTTP 请求头信息，这样才能够把多个  span 正确的关联到同一个追
踪上。
要做到这一点，应用程序从传入请求到任何传出的请求中需要包含以下请求头参数：
x-request -id
x-b3-traceid
x-b3-spanid
x-b3-parentspanid
x-b3-sampled
x-b3-flags
x-ot-span -context

**10、分布式追踪系统 -kiali**
Kiali 是Istio 服务网格的可视化工具，它主要的功能是用可视化的界面来观察微服务系统以及服务之
间的关系。 Kiali功能如下。
1）服务拓扑图：这是 Kiali 最主要的功能，提供了一个总的服务视图，可以实时地显示命名空间下
服务之间的调用和层级关系，以及负载情况。 ·
2）服务列表视图：展示了系统中所有的服务，以及它们的健康状况和出错率。 · 工作负 载视图：展
示服务的负载情况。
3）Istio 配置视图：展示了所有的 Istio 配置对象。
Kiali 的架构比较简单，如 下图，它分为前端和后端两部分。后端以容器的方式运行 在应用平台，负
责获取和处理数据，并发送给前端；前端是一个典型的 Web 应用，由 React 和TypeScript 实现，负责
展示后端发送过来的数据。对 Kiali 来说 Istio 是必须存在的系统，它类似于 Kiali 的宿主。虽然它们可以
分开部署，但没有了 Istio ，Kiali 是不能工作的。

2.使用：
kubectl get svc -n istio -system | grep kiali

显示如下：
kiali                       ClusterIP   10.106.61.5      <none>        20001/TCP

修改 kiali 的type 类型为 nodePort
kubectl edit svc kiali -n istio -system

把type: ClusterIP 变成 type: NodePort

kubectl get svc -n istio -system | grep kiali

显示如下：
kiali                       NodePort    10.106.61.5      <none>
20001:32514/TCP

在浏览器访问 192.168.40.180:32514

Username ：admin
Password ： admin

输入用户名和密码之后出现如下界面 :

Kiali 是一个非常强大的可视化工具，可以让用户清晰和直观地了解到 Istio 服务网格中的服务以及服
务之间的关系。除了服务拓扑图外，它还提供了健康检查、指标数据显示和配置验证等功能。强烈推荐把
Kiali 作为必选项添加到服务网格中，来帮助监控和观测网格中服务的工作情况。


