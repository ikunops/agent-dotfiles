参考链接：https://blog.csdn.net/weixin_36171533/article/details/82737172
docker有四种网络模型：
  bridge：桥接网络，自由网络名称空间
  joined：连接式网络，与另外一个容器共享网络名称空间
  opened：开放式网络，容器直接共享使用宿主机的网络
  none：不适用任何的网络空间
跨节点容器之间的通信，需要使用NAT机制实现
pod是一个私有网段地址，任何一个pod想要访问外部网络，需要做源地址转换，拿着物理
机的地址访问；每一个pod要想被别人访问，也需要做nat
第一个node节点上有container1，container1使用自己的网卡eth0生成一个虚拟的网络接
口veth，veph一半在容器上，一半在宿主机上，并关联到docker0桥；
上图可以看到node1上的container1想要出去访问node2上的container2需要在node1上
的eth0上做snat源地址转换，然后访问node2上的eth0，也就是container1先访问node2
的eth0，eth0在通过dnat转换到container2上

kubernetes之上的网络通信模型：
（1）容器间的通信：同一个pod内的多个容器间的通信，lo
（2）pod通信：从一个pod Ip到另一个pod Ip
（3）Pod与service通信：pod ip 到cluster ip
（4）Service与集群外部客户端的通信
要解决上面四种通信的问题，需要靠CNI插件接口：
CNI（容器网络接口）：
  flannel：支持地址分配，不支持网络策略
  calico：部署使用麻烦，支持地址分配，支持网络策略，calico可以实现三层网络路由，性
能比flannel好
  canel：flannel和calico结合
  kube-router：
flannel默认使用vxlan的方式进行后端网络传输机制的，ifconfig可以看到有个flannel.1接
口，这个是封装了网络隧道的接口，还有个cni0接口，这个是在flannel.1隧道上通信的接
口；
flannel：
    支持多种后端：
        VxLAN：
             (1)  vxlan                     叠加网络模式
             (2)  Directrouting
       host-gw: Host Gateway     直接路由模式
       UDP: 一般不使用这种方式
解决方案：
虚拟网桥：bridge
多路复用的方式：MacVLAN
硬件交换：SR-IOV
flannel用法及参数配置：
flannel应该事先存在，是k8s的附件
kubectl get pods -n kube-system -o wide   显示如下：
 kubectl get configmap -n kube-system   显示如下：
这个kube-flannel-cfg用来设置上面看到的三个flannel是怎么运行的

kubectl get configmap kube-flannel-cfg -n kube-system -o yaml  显示如下：

```yaml
apiVersion: v1
data:
  cni-conf.json: |
    {
      "name": "cbr0",
      "plugins": [
        {
          "type": "flannel",
          "delegate": {
            "hairpinMode": true,
            "isDefaultGateway": true
          }
        },
        {
          "type": "portmap",
          "capabilities": {
            "portMappings": true
          }
        }
      ]
    }
  net-conf.json: |
    {
      "Network": "10.244.0.0/16",
      "Backend": {
        "Type": "vxlan"
      }
    }
kind: ConfigMap
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"v1","data":{"cni-conf.json":"{\n  \"name\": \"cbr0\",\n  \"plugins\": [\n    {\n
\"type\": \"flannel\",\n      \"delegate\": {\n        \"hairpinMode\": true,\n
\"isDefaultGateway\": true\n      }\n    },\n    {\n      \"type\": \"portmap\",\n
\"capabilities\": {\n        \"portMappings\": true\n      }\n    }\n  ]\n}\n","net-conf.json":"{\n
\"Network\": \"10.244.0.0/16\",\n  \"Backend\": {\n    \"Type\": \"vxlan\"\n
}\n}\n"},"kind":"ConfigMap","metadata":{"annotations":{},"labels":
{"app":"flannel","tier":"node"},"name":"kube-flannel-cfg","namespace":"kube-system"}}
  creationTimestamp: 2018-12-15T14:13:30Z
  labels:
    app: flannel
    tier: node
  name: kube-flannel-cfg
  namespace: kube-system
  resourceVersion: "7384"
  selfLink: /api/v1/namespaces/kube-system/configmaps/kube-flannel-cfg
  uid: 998ec087-0073-11e9-bd88-000c29f9bea7
```
上面可以看到使用的后端网络模型是vxlan

flannel配置参数：
    network：flannel使用的CIDR格式的网络地址，用于为pod配置网络功能
                      10.244.0.0/16    ->
                       master：10.244.0.0/24
                       node1: 10.244.1.0/16
                       ...
                       node255:10.244.255.0/24
SubnetLen： 把network切分子网供各个节点使用时，使用多长的掩码进行切分，默认是
24位；
SubnetMin：10.244.10.0/24
SubnetMax：10.244.100.0/24
Backend：vxlan，host-gw，udp
         vxlan：叠加方式通信
         host-gw：直接路由通信
1.演示flannel使用直接路由的模式通信：
（1）先看下flannel默认的后端通信方式（vxlan）
kubectl get pods -o wide   显示如下：
分别登陆不同的node节点的pod上，看两个节点跨主机通信是如何实现的
在窗口1执行如下，登录到node01节点的pod上：
kubectl exec -it  myapp-deploy-67f6f6b4dc-4fc76 -- /bin/sh
在打开一个窗口2，在窗口2上登陆到node02节点的pod上：
kubectl exec -it  myapp-deploy-67f6f6b4dc-bd8bp -- /bin/sh
ping  10.244.1.56  发现可以ping通
在node01上抓包
tcpdump -i cni0 -nn icmp
显示如下：
从cni接口进来，到flannel.1被封装成了vxlan的报文
tcpdump -i flannel.1 -nn    显示如下：

可以看到两个node上的pod是接通信的
tcpdump -i ens33 -nn host 192.168.199.188   (node02的ip地址)，显示如
下：
可以看到192.168.188.184和192.168.199.188是通过icmp直接通信的，
overlay表示网络是叠加的网络类型
（2）修改flannel配置文件，更改后端通信方式变成directrouting（直接路由）
回到master节点：
cd /root/manifests/
mkdir  flannel
cd  flannel
用如下方法修改flannel的后端网络模式：
https://kubernetes.io   登陆官网------>点击Documentation，搜索flannel，  显示如
下：
选则第一个链接打开，找到flannel，如下：

文件：
cd /root/manifests
kubectl delete -f deploy-demo.yaml
cd  /root/manifests/flannel
把下面的文件上传到这个目录下：这个文件里再net-conf.json字段新增加
了”Directrouting”: true，原来文件时没有的
kubectl delete -f kube-flannel.yml
kubectl get pods -n kube-system  显示如下：
等到上面关于flannel的pod都删除之后再重新执行如下：
kubectl apply -f kube-flannel.yml
kubectl get pods -n kube-system  显示如下：
说明重新生成了flannel这个pod
cd /root/manifestskube­flannel.yml
10.38KB

kubectl apply -f deploy-demo.yaml
kubectl get pods -o wide  显示如下：
ip route show    显示如下：
上面可以看到10.244.1.0/24 via 192.168.199.184 dev ens33
dev后面是ens33，表示变成了直接路由模式，通过物理网络直接通信了，直接实现了桥接
功能，提高了性能，之前是flannel.1
在master节点登陆到node01上存在的这个pod：
kubectl exec -it myapp-deploy-67f6f6b4dc-llcdl -- /bin/sh
ping 10.244.2.116    这个ip是node02节点上的pod
在node01和node02上抓包
tcpdump -i ens33 -nn icmp   显示如下：
上面可以看到两个节点直接通信是通过ens33，而不是overlay（覆盖网络），这样就提高
了网络传输性能；如果两个节点是跨网段的，那么就会降级到vxlan（叠加网络）模式，否
则就可以用直接路由模式
上面修改flannel的网络模式，一般在刚开始安装flannel的时候修改，不要在线上直接修改
总结：

两台主机上上Pod进行通信，利用flannel
vxlan：扩展的虚拟局域网
    V虚拟的
    X扩展的
    lan局域网
flannel
    支持多种后端
    Vxlan
        1.vxlan
        2.Dirextrouting
    host-gw：Host Gateway  #不推荐，只能在二层网络中，不支持跨网络，如果有成千上
万的Pod，容易产生广播风暴
    UDP：性能差
caclio：有着很强大的控制平面，有自己的面向工具使用，直接在这个层面控制网络参数的
配置和使用，caclio是基于bjp的网络控制协议，通过自动学习来判定和发现有哪些路由条
目需要设置，flannel是自动生成的，caclio是直接学习的
calico：
calico是一个专门的项目：官网地址
https://docs.projectcalico.org/v2.0/getting-started/kubernetes/
calico是一个三层隧道，基于bjp协议，ip-ip隧道
Requirements（要求）
使用calico的时候，需要满足下面几个条件：
1.kube-proxy必须使用iptables，不能使用ipvs
2.部署kubelet时必须使用cni接口，现在新版本都是这个接口了
Calico Hosted Install：
安装
Custom Installation：

自定义安装
Third Party Integrations：
第三方整合方式
Integration Guide：第三方整合安装
我们使用的calico提供网络策略，和flannel（提供网络功能）整合使用，查看v3.1的文档如
下：
https://docs.projectcalico.org/v3.1/getting-started/kubernetes/installation/flannel
canel：
在flannel提供网络功能的基础之上，在额外提供calico提供网络策略，kubernetes如果使
用calico这个网络插件，默认使用的地址是192.168.0.0/16，这里不把calico当成是网络插
件的提供者，而是当成网络策略的提供者，依然使用10.244.0.0/16这个地址；
calico功能很复杂：
对集群节点的分配需要借助etcd，kubernetes有etcd，calico也有etcd，这是两套，如果
两套一起管理，对我们来说比较复杂；新版calico也支持不挂数据直接放在自己的存储中，
而且是通过调用apiserver的功能，把所有的请求发给apiserver，由apiserver在存储在
etcd中，因为整个k8s集群中，任何节点，任何功能，任何组件都不能直接写k8s的etcd，
都必须通过apiserver写，确保数据的一致性的；
因此calico部署方式有两种：
1.使用独立的etcd部署
2.使用k8s的etcd，但是不能直接操作etcd，而是通过apiserver调用
一、开始部署使用：
If your cluster has RBAC enabled, issue the following command to configure the
roles and bindings that Calico requires.（因为我们启用了rbac模式，因此需要用下面这
种方式安装，具体官网有说明）
kubectl apply -f \
https://docs.projectcalico.org/v3.1/getting-
started/kubernetes/installation/hosted/canal/rbac.yaml
cd /root/manifests/flannel/
wget 'https://docs.projectcalico.org/v3.1/getting-
started/kubernetes/installation/hosted/canal/rbac.yaml'
kubectl apply -f rbac.yaml
二、创建两个pod，看它们能否通信，并且控制怎么通信

kubectl explain networkpolicy   查看networkpolicy（网络策略）的用法
kubectl explain networkpolicy.spec     显示如下：

```yaml
KIND:     NetworkPolicy
VERSION:  extensions/v1beta1
RESOURCE: spec <Object>
DESCRIPTION:
     Specification of the desired behavior for this NetworkPolicy.
     DEPRECATED 1.9 - This group version of NetworkPolicySpec is deprecated by
     networking/v1/NetworkPolicySpec.
FIELDS:
   egress <[]Object>
     List of egress rules to be applied to the selected pods. Outgoing traffic
     is allowed if there are no NetworkPolicies selecting the pod (and cluster
     policy otherwise allows the traffic), OR if the traffic matches at least
     one egress rule across all of the NetworkPolicy objects whose podSelector
     matches the pod. If this field is empty then this NetworkPolicy limits all
     outgoing traffic (and serves solely to ensure that the pods it selects are
     isolated by default). This field is beta-level in 1.8
   ingress <[]Object>
     List of ingress rules to be applied to the selected pods. Traffic is
     allowed to a pod if there are no NetworkPolicies selecting the pod OR if
     the traffic source is the pod's local node, OR if the traffic matches at
     least one ingress rule across all of the NetworkPolicy objects whose
     podSelector matches the pod. If this field is empty then this NetworkPolicy
     does not allow any traffic (and serves solely to ensure that the pods it
     selects are isolated by default).
   podSelector <Object> -required-
     Selects the pods to which this NetworkPolicy object applies. The array of
     ingress rules is applied to any pods selected by this field. Multiple
     network policies can select the same set of pods. In this case, the ingress
     rules for each are combined additively. This field is NOT optional and
     follows standard label selector semantics. An empty podSelector matches all
     pods in this namespace.
   policyTypes <[]string>
     List of rule types that the NetworkPolicy relates to. Valid options are
     Ingress, Egress, or Ingress,Egress. If this field is not specified, it will
     default based on the existence of Ingress or Egress rules; policies that
     contain an Egress section are assumed to affect Egress, and all policies
     (whether or not they contain an Ingress section) are assumed to affect
     Ingress. If you want to write an egress-only policy, you must explicitly
     specify policyTypes [ "Egress" ]. Likewise, if you want to write a policy
     that specifies that no egress is allowed, you must specify a policyTypes
     value that include "Egress" (since such a policy would not include an
```

     Egress section and would otherwise default to just [ "Ingress" ]). This
     field is beta-level in 1.8
kubectl explain networkpolicy.spec.egress     显示如下：

```yaml
KIND:     NetworkPolicy
VERSION:  extensions/v1beta1
RESOURCE: egress <[]Object>
DESCRIPTION:
     List of egress rules to be applied to the selected pods. Outgoing traffic
     is allowed if there are no NetworkPolicies selecting the pod (and cluster
     policy otherwise allows the traffic), OR if the traffic matches at least
     one egress rule across all of the NetworkPolicy objects whose podSelector
     matches the pod. If this field is empty then this NetworkPolicy limits all
     outgoing traffic (and serves solely to ensure that the pods it selects are
     isolated by default). This field is beta-level in 1.8
     DEPRECATED 1.9 - This group version of NetworkPolicyEgressRule is
     deprecated by networking/v1/NetworkPolicyEgressRule.
     NetworkPolicyEgressRule describes a particular set of traffic that is
     allowed out of pods matched by a NetworkPolicySpec's podSelector. The
     traffic must match both ports and to. This type is beta-level in 1.8
FIELDS:
   ports <[]Object>
     List of destination ports for outgoing traffic. Each item in this list is
     combined using a logical OR. If this field is empty or missing, this rule
     matches all ports (traffic not restricted by port). If this field is
     present and contains at least one item, then this rule allows traffic only
     if the traffic matches at least one port in the list.
   to <[]Object>
     List of destinations for outgoing traffic of pods selected for this rule.
     Items in this list are combined using a logical OR operation. If this field
     is empty or missing, this rule matches all destinations (traffic not
     restricted by destination). If this field is present and contains at least
     one item, this rule allows traffic only if the traffic matches at least one
     item in the to list.
```
对Egress来说，需要定义目标地址和目标端口
kubectl explain networkpolicy.spec.egress.to     显示如下：

```yaml
KIND:     NetworkPolicy
VERSION:  extensions/v1beta1
RESOURCE: to <[]Object>
DESCRIPTION:
     List of destinations for outgoing traffic of pods selected for this rule.
     Items in this list are combined using a logical OR operation. If this field
     is empty or missing, this rule matches all destinations (traffic not
     restricted by destination). If this field is present and contains at least
```

     one item, this rule allows traffic only if the traffic matches at least one
     item in the to list.
     DEPRECATED 1.9 - This group version of NetworkPolicyPeer is deprecated by
     networking/v1/NetworkPolicyPeer.
FIELDS:
   ipBlock <Object>
     IPBlock defines policy on a particular IPBlock. If this field is set then
     neither of the other fields can be.
#目标地址是一个ip块，是一个地址范围
   namespaceSelector <Object>
     Selects Namespaces using cluster-scoped labels. This field follows standard
     label selector semantics; if present but empty, it selects all namespaces.
     If PodSelector is also set, then the NetworkPolicyPeer as a whole selects
     the Pods matching PodSelector in the Namespaces selected by
     NamespaceSelector. Otherwise it selects all Pods in the Namespaces selected
     by NamespaceSelector.
#目标地址是一个名称空间，控制这个名称空间的所有pod
   podSelector <Object>
     This is a label selector which selects Pods. This field follows standard
     label selector semantics; if present but empty, it selects all pods. If
     NamespaceSelector is also set, then the NetworkPolicyPeer as a whole
     selects the Pods matching PodSelector in the Namespaces selected by
     NamespaceSelector. Otherwise it selects the Pods matching PodSelector in
     the policy's own Namespace.
#目标地址是一个pod
kubectl explain networkpolicy.spec.egress.ports

```yaml
KIND:     NetworkPolicy
VERSION:  extensions/v1beta1
RESOURCE: ports <[]Object>
DESCRIPTION:
     List of destination ports for outgoing traffic. Each item in this list is
     combined using a logical OR. If this field is empty or missing, this rule
     matches all ports (traffic not restricted by port). If this field is
     present and contains at least one item, then this rule allows traffic only
     if the traffic matches at least one port in the list.
     DEPRECATED 1.9 - This group version of NetworkPolicyPort is deprecated by
     networking/v1/NetworkPolicyPort.
FIELDS:
   port  <string>
     If specified, the port on the given protocol. This can either be a
     numerical or named port on a pod. If this field is not provided, this
     matches all port names and numbers. If present, only traffic on the
     specified protocol AND port will be matched.
   protocol  <string>
```

     Optional. The protocol (TCP or UDP) which traffic must match. If not
     specified, this field defaults to TCP.
网路策略：
    名称空间：
          拒绝所有出站，进站
           放行所有出站目标本名称空间内的所有pod


