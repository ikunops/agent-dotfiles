**1、Kubernetes 的三种探针：**

• livenessProbe ：用于探测容器是否运行 。如果存活探测失败，则  kubelet 会杀死容器，并且容器将受
到其重启策略的影响 决定是否重启 。如果容器不提供存活探针，则默认状态为  Success。

• readinessProbe ：一般用于探测容器内的程序是否健康 ，容器是否准备好服务请求。如果就绪探测失
败，endpoint 将从与 Pod 匹配的所有  Service 的端点中删除该  Pod 的 IP 地址。初始延迟之前的就绪
状态默认为  Failure。如果容器不提供就绪探针，则默认状态为  Success。

• startupProbe: 探测容器中的应用是否已经启动。如果提供了启动探测 (startup probe) ，则禁用所有其
他探测，直到它成功为止。如果启动探测失败， kubelet 将杀死容器，容器服从其重启策略进行重启。
如果容器没有提 供启动探测，则默认状态为成功 Success。

可以自定义在 pod启动时是否执行这些检测，如果不设置，则检测结果均默认为通过，如果设置，
则顺序为 startupProbe>readinessProbe>livenessProbe 。

**2、为什么要用 startupProbe ？**

在k8s中，通过控制器管理 pod，如果更新 pod的时候， 会创建新的 pod，删除老的 pod，但是如果
新的pod创建了， pod里的容器还没完成初始化，老的 pod就被删除了，会导致访问 service 或者
ingress 时候，访问到的 pod是有问题的， 所以k8s就加入了一些存活性探针： livenessProbe 、就绪性
探针readinessProbe 以及这节课要介绍的启动探针 startupProbe 。

startupProbe 是在k8s v1.16 加入了alpha版，官方对其作用的解释是：

Indicates whether the application within the Container i s started. All other probes are
disabled if a startup probe is provided, until it succeeds. If the startup probe fails, the
kubelet kills the Container, and the Container is subjected to its restart policy. If a
Container does not provide a startup probe, the default state is Success

翻译：判断容器内的应用程序是否已启动。如果提供了启动探测，则禁用所有其他探测，直到它成功为
止。如果启动探测失败， kubelet 将杀死容器，容器将服从其重启策略。如果容器没有提供启动探测，则
默认状态为成功。

> **注意：不要将 startupProbe 和readinessProbe 混淆。**
**3、什么时候会用 startupProbe 呢？**
正常情况下，我们会在 pod template 中配置livenessProbe 来探测容器是否正常运行，如果异常则会触发
restartPolicy 重启容器（因为默认情况下 restartPolicy 设置的是 always）。

 如下：
livenessProbe:
  httpGet:
    path: /test
    prot: 80
  failureThreshold: 1
  initialDelay ：10
  periodSeconds: 10

上面配置的意思是容器启动 10s后每10s检查一次，允许失败的次数是 1次。如果失败次数超过 1则会
触发restartPolicy 。

但是有时候会存在特殊情况，比如服务 A启动时间很慢，需要 60s。这个时候如果还是用上面的探针就会
进入死循环，因为上面的探针 10s后就开始探测，这时候我们服务并没有起来，发现探测失败就会触发
restartPolicy 。这时候有的朋友可能会想到把 initialDelay 调成60s不就可以了？但是我们并不能保
证这个服务每次起来都是 60s，假如新的版本起来要 70s，甚至更多的时间，我们就 不好控制了。有的朋
友可能还会想到把失败次数增加，比如下面配置：

livenessProbe:
  httpGet:
    path: /test
    prot: 80
  failureThreshold: 5
  initialDelay ：60
  periodSeconds: 10

这在启动的时候是可以解决我们目前的问题，但是如果这个服务挂了呢？如果 failureThreshold=1 则
10s后就会报警通知服务挂了，如果设置了 failureThreshold=5 ，那么就需要 5*10s=50s 的时间，在现
在大家追求快速发现、快速定位、快速响应的时代是不被允许的。

在这时候我们把 startupProbe 和livenessProbe 结合起来使用就可以很大程度上解决我们的问题。

如下：
livenessProbe:
  httpGet:
    path: /test
    prot: 80
  failureThreshold: 1
  initialDelay ：10
  periodSeconds: 10
startupProbe:
  httpGet:

     path: /test
    prot: 80
  failureThreshold: 10
  initialDelay ：10
  periodSeconds: 10

上面的配置是只有 startupProbe 探测成功后再交给 livenessProbe 。我们startupProbe 配置的是
10*10s，也就是说只要应用在 100s内启动都是 OK的，而且应用挂掉了 10s就会发现问题。

其实这种还是不能确定具体时间，只能给出一个大概的范围。我个人认为对服务启动时间的影响因素太
多了，有可能是应用本身，有可能是外部因素，比如主机性能等等。我们只有在最大程度上追求高效、
稳定，但是我们不能保证 100%稳定，像阿里这样的大企业对外宣称的也是 5个9，6个9的稳定率，如果
出问题了，不好意思你 恰恰不在那几个 9里面，所以我们自己要做好监控有效性，告警的及时性，响应
的快速性，处理的高效性。

**4、K8s的LivenessProbe 和**
ReadinessProbe 的启动顺序问题

LivenessProbe 会导致pod重启，ReadinessProbe 只是不提供服务

我们最初的理解是 LivenessProbe 会在ReadinessProbe 成功后开始检查，但事实并非如此。

kubelet 使用存活探测器来知道什么时候要重启容器。  例如，存活探测器可以捕捉到死锁（应用程序在
运行，但是无法继续执行后面的步骤） 。  这样的情况下重启容器有助于让应用程序在有问题的情况下可
用。

kubelet 使用就绪探测器可以知道容器什么时候准备好了并可以开始接受请求流量，  当一个 Pod 内的
所有容器都准备好了，才能把这个  Pod 看作就绪了。  这种信号的一个用途就是控制哪个  Pod 作为
Service 的后端。  在 Pod 还没有准备好的时候，会从  Service 的负载均衡器中被剔除的。

kubelet 使用启动探测器 (startupProbe) 可以知道应用程序容器什么时候启动了。  如果配置了这类探测
器，就可以控制容器在启动成功后再进行存活性和就绪检查，  确保这些存活、就绪探测器不会影响应用
程序的启动。  这可以用于对慢启动容器进行存活性检测，避免它们在启动运行之前就被杀掉。

真正的启动顺序
https://github.com/kubernetes/kubernetes/issues/60647

 https://github.com/kubernetes/kubernetes/issues/27114

https://kubernetes.io/docs/tasks/configure -pod-container/configure -liveness -readiness -
startup-probes/#define -readiness -probes

官方文档： Caution: Liveness probes do not wait for readiness probes to succeed. If you want
to wait before executing a liv eness probe you should use initialDelaySeconds or a
startupProbe.

也就是 Liveness probes 并不会等到 Readiness probes 成功之后才运行

根据上面的 官方文档 ，Liveness 和 readiness 应该是某种并发的关系


