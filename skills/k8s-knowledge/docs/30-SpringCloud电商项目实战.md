
安装 k8s-初始化实验环境
准备两台 centos7. 6或者更高版本的虚拟机，用来安装 k8s集群，下面是两台虚拟机的配置情况
master 节点：
主机名           ip                    配置                              网络
master1       192.168.40.130          4vCPU/6G 内存/60G 硬盘         桥接或 NAT 均可
工作节点：
主机名           ip                    配置
node1         192.168.40.131          4vCPU/ 4G内存/60G 硬盘         桥接或 NAT 均可
**1.1 配置静态 ip**
**1.1.1 配置静态 ip**
把虚拟机或者物理机配置成静态 ip地址，这样机器重新启动后 ip地址也不会发生改变。
在master1 节点配置网络
修改/etc/sysconfig/network -scripts/ifcfg -ens33 文件，变成如下：

```bash
TYPE=Ethernet
PROXY_METHOD=none
BROWSER_ONLY=no
```

责。

```bash
 BOOTPROTO=static
IPADDR= 192.168.40.130
NETMASK=255.255.255.0
GATEWAY=192.168.42.2
DNS1=192.168.42.2
DEFROUTE=yes
IPV4_FAILURE_FATAL=no
IPV6INIT=yes
IPV6_AUTOCONF=yes
IPV6_DEFROUTE=yes
IPV6_FAILURE_FATAL=no
IPV6_ADDR_GEN_MODE=stable -privacy
NAME=ens33
DEVICE=ens33
ONBOOT=yes
```
修改配置文件之后需要重启网络服务才能使配置生效，重启网络服务命令如下：
service network restart

> **注：ifcfg-ens33 文件配置解释：**

```bash
IPADDR= 192.168.40.130
#ip地址，需要跟自己电脑所在网段一致
NETMASK=255.255.255.0
#子网掩码，需要跟自己电脑所在网段一致
GATEWAY=192.168.42.2
#网关，在自己电脑打开 cmd，输入 ipconfig /all 可看到
DNS1=192.168.42.2
#DNS ，在自己电脑打开 cmd，输入 ipconfig /all 可看到
```

在node1 节点配置网络

责。
 修改/etc/sysconfig/network -scripts/ifcfg -ens33 文件，变成如下：

```bash
TYPE=Ethernet
PROXY_METHOD=none
BROWSER_ONLY=no
BOOTPROTO=static
IPADDR= 192.168.40.131
NETMASK=255.255.255.0
GATEWAY=192.168.42.2
DNS1=192.168.42.2
DEFROUTE=yes
IPV4_FAILURE_FATAL=no
IPV6INIT=yes
IPV6_AUTOCONF=yes
IPV6_DEFROUTE=yes
IPV6_FAILURE_FATAL=no
IPV6_ADDR_GEN_MODE=stable -privacy
NAME=ens33
DEVICE=ens33
ONBOOT=yes
```

修改配置文件之后需要重启网络服务才能使配置生效，重启网络服务命令如下：
 service network restart
**1.2 修改 yum 源**
下面的步骤在 k8s的各个节点操作
**1.2.1 备份原来的 yum 源**
mv /etc/yum.repos.d/CentOS -Base.repo   /etc/yum.repos.d/CentOS -Base.repo.backup

责。
**1.2.2 下载阿里的 yum 源**
wget -O /etc/yum.repos.d/CentOS -Base.repo http://mirrors.aliyun.com/repo/C entos -7.repo
**1.2.3 配置安装 k8s需要的 yum 源**
cat <<EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]

```bash
name=Kubernetes
baseurl=https://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes -el7-x86_64
enabled=1
gpgcheck=0
EOF
```

**1.2.4 清理 yum 缓存**
yum clean all
**1.2.5 生成新的 yum 缓存**
yum makecache fast
**1.2.6 更新 yum 源**
yum -y update
**1.2.7 安装软件包**
yum -y install wget net -tools nfs -utils lrzsz gcc gcc -c++ make cmake libxml2 -devel openssl -
devel curl curl -devel unzip sudo ntp  libaio -devel wget vim ncurses -devel autoconf automake
zlib-devel   python -devel epel -release openssh -server socat   ipvsadm conntrack ntpdate  yum-
utils device -mapper -persistent -data  lvm2

责。
**1.2.8 添加新的软件源**
yum-config -manager --add-repo http://mirrors.aliyun.com/docker -ce/linux/centos/docker -
ce.repo
**1.2.9 清理 yum 缓存**
yum clean all
**1.2.10 生成新的 yum 缓存**
yum makecache fast
**1.3 配置防火墙**
关闭 firewalld 防火墙， 在k8s各个节点 都要关闭 ，centos7 系统默认使用的是 firewalld 防火墙，停止
firewalld 防火墙，并禁用这个服务 。
在k8s的各个节点操作 如下命令。

 systemctl stop  firewalld   && systemctl   disable  firewalld
**1.4 时间同步**
在k8s的各个节点操作 如下命令。

ntpdate cn.pool.ntp.org
编辑计划任务，每小时做一次同步
1）crontab -e
* */1 * * * /usr/sbin/ntpdate    cn.pool.ntp.org
2）重启 crond 服务：
service crond restart
1.5关闭 selinux
k8s的各个节点 都要关闭 selinux 。

责。
 关闭 selinux ，设置永久关闭，这样重启机器 selinux 也处于关闭状态
可用下面方式修改：
sed -i  's/SELINUX=enforcing/SELINUX=disabled/'  /etc/sysconfig/selinux
sed -i  's/SELINUX=enforcing/SELINUX=disabled/g'  /etc/selinux/config
上面文件修改之后，需要重启虚拟机， 如果测试环境可以用如下命令 强制重启：
reboot -f
> **注：生产环境不要 reboot  -f，要正常关机重启**

查看 selinux 是否修改 成功
重启之后登录到机器上用如下命令：
getenforce
显示 Disabled 说明 selinux 已经处于关闭状态
**1.6 关闭交换分区**
在k8s的各个节点操作 如下命令。

swapoff  -a
#临时禁用
sed -i 's/.*swap.*/#&/' /etc/fstab
#永久禁用，打开 /etc/fstab 注释掉 swap 那一行。

**1.7 修改内核参数**
在k8s的各个节点操作 如步骤。

cat <<EOF >  /etc/sysctl.d/k8s.conf
net.bridge.bridge -nf-call-ip6tables = 1
net.bridge.bridge -nf-call-iptables = 1
EOF

责。

sysctl --system

> **注：sysctl  --system  这个会加载所有的 sysctl 配置**
**1.8 修改主机名**
在192.168.40.130 上：
hostnamectl set -hostname master1
在192.168.40.131 上：
hostnamectl set -hostname node1
**1.9 配置 hosts 文件**
K8s各个节点 hosts 文件保持一致即可，可按如下方法修改：
在/etc/hosts 文件增加如下几行：
**192.168.40.130 master1**
**192.168.40.131 node1**
**1.10 配置主机之间 无密码登陆**
配置 master1 到node1 无密码登陆
在master1 上操作
ssh-keygen -t rsa
#一直回车就可以
cd /root && ssh -copy -id -i .ssh/id_rsa.pub root@node1
#上面需要输入 yes之后，输入密码，输入 node1 物理机密码即可
安装 k8s-安装 docker
在k8s的各个节点 都需要安装 docker ，安装方法按如下操作即可：

责。
**1.1 查看 docker 版本**
yum list docker -ce --showduplicates |sort -r
**1.2 安装 docker**
yum install  -y docker -ce-19.03.7 -3.el7
systemctl enable docker && systemctl start docker
#查看 docker 状态，如果状态是 active （running ），说明 docker 是正常运行状态
systemctl status docker
**1.3 修改 docker 配置文件**
cat > /etc/docker/daemon.json <<EOF
{
"registry -mirrors":["https://rsbud4vc.mirror.aliyuncs.com","https://registry.docker -
cn.com","https://docker.mirrors.ustc.edu.cn" ,"https://dockerhub.azk8s.cn","http://hub -
mirror.c.163.com","http://qtid6917.mirror.aliyuncs.com"],
"exec -opts":["native.cgroupdriver=systemd"],
 "log-driver":"json -file",
 "log-opts": {
  "max -size": "100m"
  },
 "storage -driver":"overlay2",
 "storage -opts": [
  "overlay2.override_kernel_check=true"
  ]
}
EOF

> **注：**

责。
 "registry -mirrors":["https://rsbud4vc.mirror.aliyuncs.com","https://registry.docker -
cn.com","https://docker.mirrors.ustc.edu.cn","https://dockerhub.azk8s.cn","http://hub -
mirror.c.163.com","http://qtid6917.mirror.aliyuncs.com"]
上面配置的是镜像加速器
cat > /etc/docker /daemon.json <<EOF
{
"insecure -registries":["192.168.0. 56"],
"registry -mirrors":["https://rsbud4vc.mirror.aliyuncs.com","https://registry.docker -
cn.com","https://docker.mirrors.ustc.edu.cn","https://dockerhub.azk8s.cn","http://hub -
mirror.c.163.com","http:/ /qtid6917.mirror.aliyuncs.com"],
"exec -opts":["native.cgroupdriver=systemd"],
 "log-driver":"json -file",
 "log-opts": {
  "max -size": "100m"
  },
 "storage -driver":"overlay2",
 "storage -opts": [
  "overlay2.override_kernel_check=true"
  ]
}
EOF

"insecure -registries":["192.168.0. 56"]  #配置的是 harbor私有镜像仓库地址

**1.4 重启 docker 使配置生效**
systemctl daemon -reload && systemctl restart  docker  && systemctl  status docker

责。
**1.5 开启机器的bridge 模式**
以下步骤在 k8s各个节点都需要操作

#临时生效
echo 1 > /proc/sys/net/bridge/bridge -nf-call-iptables
echo 1 >/proc/sys/net/bridge/bridge -nf-call-ip6tables
#永久生效
echo """
vm.swappiness = 0
net.bridge.bridge -nf-call-iptables = 1
net.ipv4.ip_forward = 1
net.bridge.bridge -nf-call-ip6tables = 1
""" > /etc/sysctl.conf
sysctl -p
**1.6 开启 ipvs**
不开启 ipvs将会使用 iptables，但是效率低，所以官网推荐需要开通 ipvs内核，在 k8s的各
个节点都需要开启

cat > /etc/sysconfig/modules/ipvs.modules <<EOF
#!/bin/bash

```bash
ipvs_modules="ip_vs ip_vs_lc ip_vs_wlc ip_vs_rr ip_vs_wrr ip_vs_lblc ip_vs_lblcr ip_vs_dh ip_vs_sh
ip_vs_nq ip_vs_sed ip_vs_ftp nf_conntrack"
for kernel_module in \${ipvs_modules}; do
 /sbin/modinfo -F filename \${kernel_module} > /dev/null 2>&1
 if [ $? -eq 0 ]; then
 /sbin/modprobe \${kernel_ module}
 fi
done
EOF
```

责。

chmod 755 /etc/sysconfig/modules/ipvs.modules && bash
/etc/sysconfig/modules/ipvs.modules && lsmod | grep ip_vs

显示如下，说明 ipvs开启成功了：
ip_vs_ftp              13079  0
ip_vs_sed              12519  0
ip_vs_nq               12516  0
ip_vs_sh               12688  0
ip_vs_dh               12688  0
ip_vs_lblcr            12922  0
ip_vs_lblc             12819  0
ip_vs_wrr              12697  0
ip_vs_rr               12600  0
ip_vs_wlc              12519  0
ip_vs_lc               12516  0
ip_vs                 145497  22
ip_vs_dh,ip_vs_lc,ip_vs_nq,ip_vs_rr,ip_vs_sh,ip_vs_ftp,ip_vs_sed,ip_vs_wlc,ip_vs_wrr,ip_vs_lblcr,ip_vs
_lblc
nf_nat                 26787  3 ip_vs_ftp,nf_nat_ipv4,nf_nat_masquerade_ipv4
nf_conntrack          133095  7
ip_vs,nf_nat,nf_nat_ipv4,xt_conntrack,nf_nat_masquerade_ipv4,nf_conntrack_netlink,nf_conntrack
_ipv4
libcrc32c              12644  4 xfs,ip_vs,nf_nat,nf_conntrack

责。
 安装 kubernetes 高可用集群
**1.1 在master1 和node1 上安装 kubeadm 和kubelet**
yum install  kubeadm -1.19. 6  kubelet -1.19. 6  kubectl -1.19.6   -y
systemctl enable kubelet
**1.2 初始化 k8s集群，在 k8s的master 1节点操作**
kubeadm   init  --kubernetes -version=v1.1 9.6  --pod-network -cidr=10.244.0.0/16 --apiserver -
advertise -address= 192.168.40.130  --image -repository registry.aliyuncs.com/google_containers

> **注：**
1）
--image -repository registry.aliyuncs.com/google_containers 是指定阿里云的镜像源， 国内的镜像源
访问速度会比较快，  --kubernetes -version=v1.1 9.6是指定 k8s版本，基于这个我们可以安装任何版本
的k8s。
2）
如果大家机器访问网络比较慢，可以在执行 kubeadm   init  --kubernetes -version=v1.1 9.6  --pod-
network -cidr=10.244.0.0/16 --apiserver -advertise -address= 192.168.40.130  --image -repository
registry.aliyuncs.com/google_containers   这串命令之前把 aliyun -kubernetes -master -1-19-
6.tar.gz 上传到 k8s的master1 节点，通过 docker load -i aliyun -kubernetes -master -1-19-6.tar.gz
手动解压，把 aliyun -kubernetes -slave -1-19-6.tar.gz 上传到 k8s的node1 节点，通过 docker load -i
aliyun -kubernetes -slave -1-19-6.tar.gz 手动解压。

初始化命令执行成功之后显示如下内容，说明初始化成功了

Your Kubernetes control -plane has initialized successfully!

To start using your cluster, you need to run the following as a regular user:

责。
   mkdir -p $HOME/.kube
  sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
  sudo chown $(id -u):$(id -g) $HOME/.kube/config

You should now deploy a pod network to the cluster.
Run "kubectl apply -f [podnetwork].yaml" with one of the options listed at:
  https://kubernet es.io/docs/concepts/cluster -administration/addons/

Then you can join any number of worker nodes by running the following on each as root:

kubeadm join 192.168.40.130 :6443 --token arebzi.av5ngsdukew8f0b9 \
    --discovery -token -ca-cert-hash
sha256:b8ebb39 10a90584f9806f0220637fc8050d9fb06f8e66c0e92f56ef1e8db52f8

> **注：kubeadm join ... 这条命令需要记住，我们把 k8s的node1 节点加入到集群需要在这些节点节点输**
入这条命令，每次执行这个结果都是不一样的，大家记住自己执行的结果，在下面会用到
**1.3 在master1 节点授权，这样才能有权限操作 k8s资源**
mkdir  -p $HOME/.kube
sudo  cp -ifr  /etc/kubernetes/admin.conf  $HOME/.kube/config
sudo  chown  $(id -u):$(id  -g)  $HOME/.kube/config

> **注： 我们下面执行 kubectl 的命令都是在 k8s的master1 节点操作**

在master1 节点执行
kubectl get nodes
显示如下， master1 节点是 NotReady
NAME      STATUS     ROLES    AGE    VERSION
master1   NotReady   master   103s   v1.19.6

责。
 kubectl get pods -n kube -system
显示如下，可看到 cordns 是处于 pending 状态
NAME                              READY   STATUS    RESTARTS   AGE
coredns -6d56c8448f -ccb8n          0/1     Pending   0          100s
coredns -6d56c8448f -dpklb          0/1     Pending   0          100s

> **注意： 上面可以看到 STATUS 状态是 NotReady ，cordns 是pending ，是因为没有安装网络插件，需要**
安装 calico 或者 flannel ，接下来我们安装 calico ，在 master1 节点安装 calico 网络插件：

安装 calico 需要的镜像是 quay.io/calico/cni:v3.5.3 和quay.io/calico/node:v3.5.3 ，镜像在课件，手动
上传上面两个镜像的压缩包到 master1 和node1节点， 在master1 和node1 上通过 docker load -i解
压
docker load -i   cni.tar.gz
docker load -i   calico -node.tar.gz
**1.4 在master1 节点安装 calico 网络插件**
> **注意： calico .yaml 里需要修改如下内容：**
找到 IP_AUTODETECTION_METHOD 对应的 value 值：
- name: IP_AUTODETECTION_METHOD
  value: "can -reach=192.168.40.131"
#这个 ip写你自己环境的 node 1节点的 ip，假如 node 节点有多个，那么只写一个 node 节点 ip即可，
所以大家只需要写 node 1的ip即可

更新 yaml 文件：
kubectl apply -f calico.yaml
calico.yaml 文件在课件，可自行下载
**1.5 查看 node 节点和 pod 状态，在 master1 节点执行**
kubectl get nodes

责。
 显示如下，看到 STATUS 是Ready
NAME      STATUS   ROLES    AGE     VERSION
master1   Ready    master   8m19s   v1.19.6
kubectl get pods -n kube -system

看到 cordns 也是 running 状态，说明 master1 节点的 calico 安装完成
NAME                              READY   STATUS    RESTARTS   AGE
calico -node -mc66q                 1/1     Running   0          69s
coredns -6d56c8448f -ccb8n          1/1     Running   0          8m50s
coredns -6d56c8448f -dpklb          1/1     Running   0          8m50s
etcd-master1                      1/1     Running   0          9m5s
kube -apiserver -master1            1/1     Running   0          9m5s
kube -controller -manager -master1   1/1     Running   0          9m5s
kube -proxy -6l4g9                  1/1     Running   0          8m50s
kube -scheduler -master1            1/1     Running   0          9m5s

**1.6 把node1 节点加入到 k8s集群，在 node1 节点操作**
> **注：下面的这个 是把 node1 节点加入到 k8s的一串命令 ，下面的这串命令 就是在 8.2节初始化的时候生**
成的，每个人的都不一样，大家用自己的就可以。

kubeadm join 192.168.40.130 :6443 --token arebzi.av5ngsdukew8f0b9 \
--discovery -token -ca-cert-hash
sha256:b8ebb3910a90584f9806f0220637fc8050d9fb06f8e66c0e92f56ef1e8db52f8

上面命令执行之后，出现如下，说明 node1 节点已经加入到 k8s集群：
This node has joined the cluster:
* Certificate signing request was sent to apiserver and a response was received.
* The Kubelet was informed of the new secure connection details.

责。
 Run 'kubectl get nodes' on the control -plane to see this node join the cluster.
**1.7 在master1 节点查看集群节点状态**
kubectl get nodes
显示如下：
NAME        STATUS      ROLES     AGE   VERSION
master1     Ready    master    3m36s    v1.19.6
node1       Ready    <none>    3m36s   v1.19.6

看到上面 STATUS 状态是 Ready ，说明 node1 节点也加入到 k8s集群了，通过以上就完成了 k8s单
master 节点高可用集群的搭建

kubectl  get cs
显示如下 :
Warning: v1 ComponentStatus is deprecated in v1.19+
NAME                 STAT US      MESSAGE
ERROR
controller -manager   Unhealthy   Get "http://127.0.0.1:10252/healthz": dial tcp
127.0.0.1:10252: connect: connection refused
scheduler            Unhealthy   Get "http://127.0.0.1:10251/healthz": dial tcp
127.0.0.1:10251: connect: connection refused
etcd-0               Healthy     {"health":"true"}

看到 cotroller -manager 和scheduler 是Unhealthy ，按如下方面解决：
vim /etc/kubernetes/manifests/kube -scheduler.yaml
修改如下内容：
把--bind-address=127.0.0.1 变成--bind-address= 192.168.40.130
把httpGet: 字段下的 hosts 由127.0.0.1 变成 192.168.40.130
把—port=0删除
#注意： 192.168.40.130 是k8s的master 1节点 ip
vim /etc/kubernetes/manifests/kube -controller -manager.yaml

责。
 把--bind-address=127.0.0.1 变成--bind-address= 192.168. 40.130
把httpGet: 字段下的 hosts 由127.0.0.1 变成 192.168.40.130
把—port=0删除

修改之后在 k8s各个节点执行
systemctl restart kubelet

kubectl  get cs
显示如下 :
NAME                 STATUS    MESSAGE             ERROR
controller -manager   Healthy   ok
scheduler            Healthy   ok
etcd-0               Healthy   {"health":"true"}

ss -antulp | grep :10251
ss -antulp | grep :1025 2
可以看到相应的端口已经被物理机监听了
Ingress 和 Ingress  Controller 概述
**1. 回顾下 service 四层代理**
互动：  回顾下 四层负载均衡器 service
**1、Pod 漂移问题**
Kubernetes 具有强大的副本控制能力，能保证在任意副本（ Pod）挂掉时自动从其他机器启动一个新
的，还可以动态扩容等，通俗地说，这个 Pod可能在任何时刻出现在任何节点上，也可能在任何时刻死
在任何节点上；那么自然随着 Pod的创建和销毁， Pod IP 肯定会动态变化；那么如何把这个动态的 Pod
IP暴露出去？这里借助于 Kubernetes 的 Service 机制， Service 可以以标签的形式选定一组带有指定标
签的 Pod，并监控和自动负载他们的 Pod IP ，那么我们向外暴露只暴露 Service IP 就行了； 这就是
NodePort 模式：即在每个节点上开起一个端口，然后转发到内部 Pod IP 上，如下图所示：

责。
 此时的访问方式： http://nodeip:nodeport/  ，即数据包流向如下：
客户端 请求-->node 节点的 ip:端口--->service 的ip:端口--->pod 的ip:端口

**2、端口管理问题**
采用 NodePort 方式暴露服务面临的问题是，服务一旦多起来， NodePort 在每个节点上开启的端口会及
其庞大，而且难以维护；这时，我们能否使用一个 Nginx 直接对内进行转发呢？众所周知的是， Pod与
Pod之间是可以互相通信的，而 Pod是可以共享宿主机的网络名称空间的，也就是说当在共享网络名称
空间时， Pod上所监听的就是 Node 上的端口。那么这又该如何实现呢？简单的实现就是使用
DaemonSet 在每个 Node 上监听  80，然后写好规则，因为 Nginx 外面绑定了宿主机 80端口（就像
NodePort ），本身 又在集群内，那么向后直接转发到相应  Service IP 就行了，如下图所示：

**3、域名分配及动态更新问题**

责。
 从上面的方法，采用 Nginx -Pod似乎已经解决了问题，但是其实这里面有一个很大缺陷：当每次有新服
务加入又该如何修改 Nginx 配置呢？我们知道使用 Nginx 可以通过虚拟主机域名进行区分不同的服务，
而每个服务通过 upstream 进行定义不同的负载均衡池，再加上 location 进行负载均衡的反向代理，在
日常使用中只需要修改 nginx.conf 即可实现，那在 K8S中又该如何实现这种方式的调度呢？假设后端 的
服务初始服务只有 ecshop ，后面增加了 bbs和member 服务，那么又该如何将这 2个服务加入到
Nginx -Pod进行调度呢？总不能每次手动改或者 Rolling Update 前端 Nginx Pod 吧！此时 Ingress 出
现了，如果不算上面的 Nginx ，Ingress 包含两大组件： Ingress Controller 和 Ingress 。

**2. Ingress 介绍**
Ingress 官网定义： Ingress 可以把进入到集群内部的请求转发到集群中的一些服务上，从而可以把服务
映射到集群外部。 Ingress 能把集群内 Service 配置成外网能够访问的  URL，流量负载均衡，提供基于
域名访问的虚拟主机等 。
Ingress 简单的理解就是你原来需要改 Nginx 配置，然后配置各种域名对应哪个  Service ，现在把这个动
作抽象出来，变成一个  Ingress 对象，你可以用  yaml 创建，每次不要去改 Nginx 了，直接改 yaml 然
后创建 /更新就行了；那么问题来了： ”Nginx 该怎么处理？ ”
Ingres s Controller 这东西就是解决  “Nginx 的处理方式 ” 的；Ingress Control ler 通过与
Kubernetes API 交互，动态的去感知集群中 Ingress 规则变化，然后读取他，按照他自己模板生成一段
Nginx 配置，再写到  Nginx Pod 里，最后  reload 一下，工作流程如下图：

实际上 Ingress 也是 Kubernetes API的标准资源类型之一，它其实就是一组基于 DNS 名称（ host）或
URL路径把请求转发到指定的 Service 资源的规则。用于将集群外部的请求流量转发到集群内部完成的服
务发布。我们需要明白的是， Ingress 资源自身不能进行 “流量穿透 ”，仅仅是一组规则的集合，这些集
合规则还需要其他功能的辅助，比如监听某套接字，然后根据这些规则的匹配进行路由转发，这些能够为
Ingress 资源监听套接字并将流量转发的组件就是 Ingress Controller 。

责。
> **注：Ingress 控制器不同于 Deployment 控制器的是， Ingress 控制器不直接运行为 kube -controller -**
manager 的一部分，它仅仅是 Kubernetes 集群的一个附件，类似于 CoreDNS ，需要在集群上单独部
署。
3.Ingress Controller 介绍
Ingress Controller 是一个七层负载均衡调度器，客户端的请求先到达这个七层负载均衡调度器，由七层
负载均衡器在反向代理到后端 pod，常见的七层负载均衡器有 nginx 、traefik ，以我们熟悉的 nginx 为
例，假如请求到达 nginx ，会通过 upstream 反向代理到后端 pod应用，但是后端 pod的ip地址是一
直在变化的，因此在后端 pod前需要加一个 service ，这个 service 只是起到分组的作用，那么我们
upstream 只需要填写 service 地址即可

4.Ingress 和Ingress Controller 总结
Ingress Controller
Ingress Controller 可以理解为控制器，它通过不断的跟  Kubernetes API 交互，实时获取后端
Service、Pod的变化，比如新增、删除等，结合 Ingress 定义的规则生成配置，然后动态更新上边的
Nginx 或者 trafik 负载均衡器，并刷新使配置生效，来达到服务自动发现的作用。
Ingress 则是定义规则，通过它定义某个域名的请求过来之后转发到集群中指定的  Service 。它可以通过
Yaml 文件定义，可以给一个或多个  Service 定义一个或多个  Ingress 规则。
**5. 使用 Ingress Controller 代理 k8s内部应用 的流程**
（1）部署 Ingress controller ，我们 ingress controller 使用的是 nginx

责。
 （2）创建 Service ，用来分组 pod
（3）创建 Pod应用，可以通过控制器创建 pod
（4）创建 Ingress http ，测试通过 http 访问应用
（5）创建 Ingress https ，测试通过 https 访问应用
客户端通过七层调度器访问后端 pod 的方式
使用七层负载均衡调度器 ingress controller 时，当客户端访问 kubernetes 集群内部的应用时，数据包
走向如下 图流程所示：

**6. 安装 Nginx  Ingress Controller**
安装需要的yaml文件和镜像 在课件，可自行下载
把yaml 文件上传到对应的 K8s的master 1节点上 ，把defaultbackend.tar.gz 和nginx -ingress -
controller.tar.gz 镜像上传到 k8s的node 1节点，手动解压 镜像：
docker load -i defaultbackend.tar.gz
docker load -i nginx -ingress -controller.tar.gz
更新 yaml 文件：
kubectl apply -f nginx -ingress -controller -rbac.yml

责。
 kubectl apply -f default -backend.yaml
kubectl app ly  -f nginx -ingress -controller.yaml
kubectl get pods -n kube -system
显示如下，说明部署成功 了：
nginx -ingress -controller -74cf657846 -qrvdm   1/1     Running   0          30s
> **注意：**
default -backend.yaml 和nginx -ingress -controller.yaml 文件指定了 nodeName ：node1 ，表示
default 和nginx -ingress -controller 部署在 node1 节点，大家的 node 节点如果主机名不是 node1 ，
需要自行修改成自己的主机名，这样才会调度成功，一定要让 default -http-backend 和nginx -ingress -
controller 这两个 pod在一个节点上。

7.测试 Ingress HTTP 代理 tomcat
1.部署后端 tomcat 服务
cat  deploy -demo.yaml

```yaml
apiVersion: v1
kind: Service
metadata:
  name: tomcat
  namespace: default
spec:
  selector:
    app: tomcat
```

责。
     release: canary
  ports:
  - name: http
    targetPort: 8080
    port: 8080
  - name: ajp
    targetPort: 8009
    port: 8009
---

```yaml
apiVersion: a pps/v1
kind: Deployment
metadata:
  name: tomcat -deploy
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: tomcat
      release: canary
  template:
    metadata:
      labels:
```

责。
         app: tomcat
        release: canary

```yaml
    spec:
      containers:
      - name: tomcat
        image: tomcat:8.5.34 -jre8-alpine
        ports:
        - name: http
          containerPort: 8080
          name: ajp
          containerPort: 8009
```
更新 yaml 文件：
kubectl apply -f deploy -demo.yaml
查看 pod 是否部署成功：
kubectl get pods
显示如下，说明 pod 创建成功：
tomcat-deploy-66b67fcf7b -h582w       1/1     Running   0          50s
tomcat-deploy-66b67fcf7b -rm82h       1/1     Running   0          50s
部署 ingress
（1）编写 ingress 的配置清单
cat  ingress -myapp.yaml

```yaml
apiVersion: extensions/v1beta1          #api 版本
kind: Ingress           # 清单类型
```

责。

```yaml
 metadata:                       # 元数据
  name: ingress -myapp    #ingress 的名称
  namespace: default     # 所属名称空间
  annotations:           # 注解信息
    kubernetes.io/ingress.class: "nginx"
spec:      # 规格
  rules:   # 定义后端转发的规则
  - host: tomcat.lucky.com    # 通过域名进行转发
    http:
      paths:
      - path:       # 配置访问路径，如果通过 url进行转发，需要修改；空默认为访问的路径为 "/"
        backend:    # 配置后端服务
          serviceName: tomcat
          servicePort: 80 80
```
更新yaml文件：
kubectl apply -f ingress -myapp.yaml
查看ingress-myapp的详细信息
kubectl describe ingress ingress -myapp
显示如下：
Name:             ingress -myapp
Namespace:        default
Address:
Default backend:  default -http-backend:80 (10.244.1.40:8080)

责。
 Rules:
  Host              Path  Backends
  ----              ----  --------
  tomcat.lucky.com
                       myapp:80 (10.244.1.41:80,10.244.1.42:80)
Annotations:        kubernetes.io/ingress.class: nginx
Events:
  Type    Reason  Age   From                      Message
  ----    ------   ----  ----                      -------
  Normal  CREATE  104s  nginx -ingress -controller  Ingress default/ingress -myapp
  Normal  U PDATE  50s   nginx -ingress -controller  Ingress default/ingress -myapp

修改电脑本地的host 文件， 增加如下一行， 下面的 ip是k8s的node1 节点 ip
**192.168.40.131 tomcat.lucky.com**
浏览器访问 tomcat.lucky.com ，出现如下：

责。

**8. 测试 Ingress  HTTPS 代理 tomcat**
**8.1 构建 TLS站点**
（1）准备证书，在 k8s的master 1节点操作
openssl genrsa -out tls.key 2048
openssl req -new -x509 -key tls.key -out tls.crt -subj
/C=CN/ST=Beijing/L=Beijing/O=DevOps/CN=tomcat.lucky.com
（2）生成 secret ，在 k8s的master 1节点操作
kubectl create secret tls tomcat -ingress -secret --cert=tls.crt --key=tls.key
（3）查看 secret
kubectl get secret
显示如下：

责。
 tomcat -ingress -secret   kubernetes.io/tls                     2      56s
（4）查看 tomcat -ingress -secret 详细信息
kubectl describe secret tomcat -ingress -secret
显示如下：
Name:         tomcat -ingress -secret
Namespace:    default
Labels:       <none>
Annotations:  <none>

```yaml
Type:  kubernetes.io/tls
Data
====
tls.crt:  1294 bytes
tls.key:  1679 bytes
```
**8.2 创建 Ingress**
cat ingress -tomcat -tls.yaml

```yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: ingress -tomcat -tls
  namespace: default
  annotations:
    kubernetes.io/ingress.class: "nginx"
```

责。

```yaml
 spec:
  tls:
  - hosts:
    - tomcat.lucky.com
    secretName: tomcat -ingress -secret
  rules:
  - host: tomcat.lucky.com
    http:
      paths:
      - path:
        backend:
          serviceName: tomcat
          servicePort: 8080
```
更新 yaml 文件
kubectl apply -f ingress -tomcat -tls.yaml
浏览器访问 https://tomcat.lucky.com
选择接受风险并继续即可，出现如下：

责。

私有镜像仓库 Harbor 安装和配置
新创建一台虚拟机 安装harbor，配置如下：
主机名           ip                    配置                              网络
harbor     192.168.40.132          4vCPU/ 4G内存/60G 硬盘         桥接或 NAT 均可

> **注： 新机器的初始化只需要按照上面课程步骤进行初始化即可**

1.harbor 简介
harbor 是私有镜像仓库，用来存储和分发镜像的
docker 还有一个官方的镜像仓库 docker  hub，免费用户只能简单的使用， 创建一个私有镜像仓库，存储
镜像， 付费用户才可以拥有更多权限， 默认 docker  pull拉取镜像就是从 docker  hub上拉取， 速度极慢，
不利于生产环境使用。
harbor 私有镜像仓库拉取镜像速度极快，属于内网传输，功能也很强大：

互动： 有什么功能 ？

1.基于角色访问控制 ：用户与 Docker 镜像仓库通过 “项目”进行组织管理，一个用户可以对多个镜像仓
库在同一命名空间（ project ）里有不同的权限。
2.镜像复制 ：镜像可以在多个 Registry 实例中复制（同步） 。尤其适合于负载均衡，高可用，混合云和多云
的场景。

责。
 3.图形化界面 ：用户可以通过浏览器来浏览，检索当前 Docker 镜像仓库，管理项目和命名空间。
4.部署简单 ：提供在线和离线两种安装工具
5.LDAP ：Harbor 可以集成企业内部已有的 AD/LDAP ，用于鉴权认证管理

2.初始化和 安装 docker
按照上面安装 k8s的时候讲的初始化和安装 docker 步骤进行安装即可

初始化：
**1.1 配置静态 ip**
**1.1.1 配置静态 ip**
把虚拟机或者物理机配置成静态 ip地址，这样机器重新启动后 ip地址也不会发生改变。
在harbor 节点配置网络
修改/etc/sysconfig/network -scripts/ifcfg -ens33 文件，变成如下：

```bash
TYPE=Ethernet
PROXY_METHOD=none
BROWSER_ONLY=no
BOOTPROTO=static
IPADDR= 192.168.40.132
NETMASK=255.255.255.0
GATEWAY=192.168.42.2
DNS1=192.168.42.2
DEFROUTE=yes
IPV4_FAILURE_FATAL=no
IPV6INIT=yes
IPV6_AUTOCONF=yes
IPV6_DEFROUTE=yes
```

责。

```bash
 IPV6_FAILURE_FATAL=no
IPV6_ADDR_GEN_MODE=stable -privacy
NAME=ens33
DEVICE=ens33
ONBOOT=yes
```
修改配置文件之后需要重启网络服务才能使配置生效，重启网络服务命令如下：
service network restart

**1.2 修改 yum 源**
下面的步骤在 harbor 节点操作
**1.2.1 备份原来的 yum 源**
mv /etc/yum.repos.d/CentOS -Base.repo   /etc/yum.repos.d/CentOS -Base.repo.backup
**1.2.2 下载阿里的 yum 源**
wget -O /etc/yum.repos.d/CentOS -Base.repo http://mirrors.aliyun.com/repo/Centos -7.repo
**1.2.3 配置安装 k8s需要的 yum 源**
cat <<EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]

```bash
name=Kubernetes
baseurl=https://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes -el7-x86_64
enabled=1
gpgcheck=0
EOF
```

责。
**1.2.4 清理 yum 缓存**
yum clean all
**1.2.5 生成新的 yum 缓存**
yum makecache fast
**1.2.6 更新 yum 源**
yum -y update
**1.2.7 安装软件包**
yum -y install wget net -tools nfs -utils lrzsz gcc gcc -c++ make cmake libxml2 -devel openssl -
devel curl curl -devel unzip sudo ntp  libaio -devel wget vim ncurses -devel autoconf automake
zlib-devel   python -devel epel -release openssh -server socat   ipvsadm conntrack ntpdate  yum-
utils device -mapper -persistent -data  lvm2
**1.2.8 添加新的软件源**
yum-config -manager --add-repo http://mirrors.aliyun.com/docker -ce/linux/centos/docker -
ce.repo
**1.2.9 清理 yum 缓存**
yum clean all
**1.2.10 生成新的 yum 缓存**
yum makecache fast
**1.3 配置防火墙**
关闭 firewalld 防火墙， 在k8s各个节点 都要关闭 ，centos7 系统默认使用的是 firewalld 防火墙，停止
firewalld 防火墙，并禁用这个服务 。
在k8s的各个节点操作 如下命令。

 systemctl stop  firewalld   && systemctl   disable  firewalld

责。
**1.4 时间同步**
在k8s的各个节点操作 如下命令。

ntpdate cn.pool.ntp.org
编辑计划任务，每小时做一次同步
1）crontab -e
* */1 * * * /usr/sbin/ntpdate    cn.pool.ntp.org
2）重启 crond 服务：
service crond restart
1.5关闭 selinux
关闭 selinux ，设置永久关闭，这样重启机器 selinux 也处于关闭状态
可用下面方式修改：
sed -i  's/SELINUX=enforcing/SELINUX=disabled/'  /etc/sysconfig/selinux
sed -i  's/SELINUX=enforcing/SELINUX=disabled/g'  /etc/selinux/config
上面文件修改之后，需要重启虚拟机， 如果测试环境可以用如下命令 强制重启：
reboot -f
> **注：生产环境不要 reboot  -f，要正常关机重启**

查看 selinux 是否修改 成功
重启之后登录到机器上用如下命令：
getenforce
显示 Disabled 说明 selinux 已经处于关闭状态
**1.6 修改内核参数**
cat <<EOF >  /etc/sysctl.d/k8s.conf
net.bridge.bridge -nf-call-ip6tables = 1
net.bridge.bridge -nf-call-iptables = 1
EOF

责。

sysctl --system

> **注：sysctl  --system  这个会加载所有的 sysctl 配置**
**1.7 修改主机名**
在192.168.40.13 2上：
hostnamectl set -hostname harbor
**1.8 配置 hosts 文件**
各个节点 hosts 文件保持一致即可，可按如下方法修改：
在/etc/hosts 文件增加如下几行：
**192.168.40.130 master1**
**192.168.40.131 node1**
**192.168 .40.132 harbor**
**1.9 配置主机之间 无密码登陆**
配置 master1 到harbor 无密码登陆
在master1 上操作
cd /root && ssh-copy -id -i .ssh/id_rsa.pub root@ harbor
#上面需要输入 yes之后，输入密码，输入 harbor 物理机密码即可

安装 docker ：
安装方法按如下操作即可：
**1.10 查看 docker 版本**
yum list docker -ce --showduplicates |sort -r

责。
**1.11 安装 docker**
yum install  -y docker -ce-19.03.7 -3.el7
systemctl enable docker && systemctl start docker
#查看 docker 状态，如果状态是 active （running ），说明 docker 是正常运行状态
systemctl status docker
**1.12 修改 docker 配置文件**
cat > /etc/docker/daemon.json <<EOF
{
"registry -mirrors":["https://rsbud4vc.mirror.aliyuncs.com","https://registry.docker -
cn.com","https://doc ker.mirrors.ustc.edu.cn","https://dockerhub.azk8s.cn","http://hub -
mirror.c.163.com","http://qtid6917.mirror.aliyuncs.com"],
"exec -opts":["native.cgroupdriver=systemd"],
 "log-driver":"json -file",
 "log-opts": {
  "max -size": "100m"
  },
 "storage -driver": "overlay2",
 "storage -opts": [
  "overlay2.override_kernel_check=true"
  ]
}
EOF

> **注：**
"registry -mirrors":["https://rsbud4vc.mirror.aliyuncs.com","https://registry.docker -
cn.com","https://docker.mirrors.ustc.edu.cn","https://dockerhub.azk8s.cn","http://hub -
mirror.c.163.com","http://qtid6917.mirror.aliyuncs.com"]

责。
 上面配置的是镜像加速器
cat > /etc/docker /daemon.json <<EOF
{
"insecure -registries":["192.168.0. 56"],
"registry -mirrors":["https://rsbud4vc.mirror.aliyuncs.com","https://registry.docker -
cn.com","https://docker.mirrors.ustc.edu.cn","https://dockerhub.azk8s.cn","http://hub -
mirror.c.163.com","http:/ /qtid6917.mirror.aliyuncs.com"],
"exec -opts":["native.cgroupdriver=systemd"],
 "log-driver":"json -file",
 "log-opts": {
  "max -size": "100m"
  },
 "storage -driver":"overlay2",
 "storage -opts": [
  "overlay2.override_kernel_check=true"
  ]
}
EOF

"insecure -registries":["192.168.40.132"]  # 配置的是 harbor私有镜像仓库地址

**1.13 重启 docker 使配置生效**
systemctl daemon -reload && systemctl restart  docker  && systemctl  status docker
**1.14 开启机器的bridge 模式**
以下步骤在 k8s各个节点都需要操作

#临时生效
echo 1 > /proc/sys/net/bridge/bridge -nf-call-iptables

责。
 echo 1 >/proc/sys/net/bridge/bridge -nf-call-ip6tables
#永久生效
echo """
vm.swappiness = 0
net.bridge.bridge -nf-call-iptables = 1
net.ipv4.ip_forward = 1
net.bridge.bridge -nf-call-ip6tables = 1
""" > /etc/sysctl.conf
sysctl -p

责。

3.为harbor 签发证书
mkdir /data/ssl -p
cd /data/ssl/

生成 ca证书：
openssl genrsa -out ca.key 3072
#生成一个 3072 位的 key，也就是私钥
openssl req -new -x509 -days 3650  -key ca.key -out ca.pem
#生成一个数字证书 ca.pem ，3650 表示证书的有效时间是 3年，按箭头提示填写即可，没有箭头标注的
为空：

生成域名的证书：
openssl genrsa -out harbor.key  3072
#生成一个 3072 位的 key，也就是私钥
openssl req -new -key harbor .key -out harbor .csr
#生成一个证书请求，一会签发证书时需要的 ，标箭头的按提示填写， 没有箭头标注的为空：

责。

签发证书：
openssl x509 -req -in harbor .csr -CA ca.pem -CAkey ca.key -CAcreateserial -out harbor .pem -
days 3650
显示如下，说明证书签发好了：

查看证书是否有效：
openssl x509 -noout -text -in harbor .pem

显示如下，说明有效：
Certificate:

```yaml
    Data:
        Version: 1 (0x0)
        Serial Number:
            cd:21:3c:44:64:17:65:40
    Signature Algorithm: sha256WithRSAEncryption
        Issuer: C=CH, ST=BJ, L=BJ, O=Default Company Ltd
        Validity
            Not Before: Dec 26 09:29:19 2020 GMT
```

责。
             Not After : D ec 24 09:29:19 2030 GMT
        Subject: C=CH, ST=BJ, L=BJ, O=Default Company Ltd, CN=harbor
        Subject Public Key Info:
            Public Key Algorithm: rsaEncryption
                Public -Key: (3072 bit)
                Modulus:
                    00:b0:60:c3:e6:35:70:11:c8:73:83:38:9a:7e:b8:
                    4b:f6:b7:53:ae:ab:30:00:48:da:4b:43:15:8b:41:
                    e5:c4:ba:4b:50:c1:89:9e:71:cc:1b:1b:bb:6c:ed:
                    ec:6c:22:19:96:9b:b8:be:60:5a:ff:50:13:0a:bd:
                    8c:4a:63:b9:c5:d5:24:f5:21:72:68:9f:39:d9:38:
                    18:c7:dc:a7:83:ea:67:81:b8:92:d3:fd:31:99:bb:
                    a6:0f:47:74:68:ff:90:a0:4c:56:85:32:95:5b:c9:
                    e6:53:3d:46:c9:2a:7f:fb:1d:a6:b6:b3:cc:ad:3b:
                    4b:bc:42:3a:13:7d:a8:5e:c8:ab:96:fd:06:50:4d:
                    26:2b:b2:6b:34:b5:f4:d1:9b:49:36:c7:6d:0f:fd:
                    a4:17:92:4d:96:80:f8:2f:b5:60:fd:2b:01:27:54:
                    80:60:09:40:bf:c0:56:a6:d1:2e:09:23:4c:8 4:0e:
                    d9:bb:f4:39:5f:5d:e7:ce:b3:22:51:f8:53:ad:95:
                    fe:52:8c:b8:87:e3:67:be:02:3c:18:73:80:23:7e:
                    37:2a:2c:de:9d:1c:b4:ab:b4:79:90:09:d9:3f:f5:
                    ac:b2:08:39:28:56:1e:20:96:e5:35:34:b3:c9:ae:

责。
                     ef:eb:d4:68:14:7d:ac:cb:ec:a6:61:7c:27:fb:87:
                    fa:4f:a8:e1:c9:b0:22:b3:7a:c5:f3:ec:58 :97:61:
                    de:b5:fb:b5:89:a5:91:76:04:eb:c7:ee:db:62:97:
                    14:50:04:0d:6d:6c:fb:1b:52:b5:0b:04:bb:e8:4c:
                    d8:c5:19:c9:f1:3f:5e:bf:b0:3b:33:28:72:47:35:
                    c3:56:98:32:4f:0b:e3:0c:4e:d5: 31:cb:e4:1a:37:
                    a5:ec:ef:97:a5:da:cc:72:3c:0a:e2:0d:a8:e7:b1:
                    fa:aa:d9:cb:54:b6:d2:85:09:85:a2:1b:93:73:27:
                    86:41:76:e2:cf:d3:77:91:d9:b2:19:08:53:f8:0c:
                    dd:51:b1:cf:2a:64:02:3 5:c6:11
                Exponent: 65537 (0x10001)
    Signature Algorithm: sha256WithRSAEncryption
         e6:3d:15:29:a8:a4:bf:79:c7:bd:65:82:49:99:d0:71:5f:60:
         0f:e0:2d:4f:f1:1c:22:73:4f:29:b6:cb:7e:29:e2:6c:bc:b3:
         9e:e4:b0:20:52:24:c5 :e5:33:9f:dc:38:29:55:91:3d:84:d5:
         80:f3:7a:78:86:ce:80:5d:8b:70:ac:d6:84:18:3a:ad:b0:06:
         c3:49:ba:24:13:75:cd:37:91:81:6d:80:b0:20:91:f6:a8:0c:
         d1:77:3d:8f:2e:e8:66:ba:29:1d:d7:6e:ec:81:15:75:70:dd:
         7b:9e:55:85:6e:d9:89 :04:c8:5e:db:bf:e2:f7:ec:93:03:8a:
         73:34:5a:fb:23:03:1d:d3:26:aa:80:1a:a9:65:21:61:f6:16:
         38:14:fe:3a:43:a2:46:60:be:32:b7:b1:aa:47:44:40:01:ca:
         b9:13:10:03:fe:c1:95:6d:aa:71:57:73:ba:76:30:f0:b2:53:

责。
          0f:7e:db:6b:ed:03:d9:8f:64:07:5e:e9:3a:b1:6f:46:d3:67:
         2c:ea:c7:aa:02:de:48:b8:e3:d3:88:ad:52:24:d5:c2:e4:c0:
         c5:0a:fe:eb:ea:8e:a4:8b:f8:d7:36:15:ff:0b:c7:41:79:7c:
         7e:16:75:61:52:fa:b4:29:fb:6b:07:c2:1d:cd:4d:4e:6c:29:
         b4:ef:9a:ed:86:c6:14:75:a6:41:fa:bb:11:d4:d7:00:82:46:
         58:8b:15:54:76:63:84:94:ef:9f:41:a7:c9:4f:63:00:3a:36:
         f0:27:14:4c:16:1b:22:6e:1e:db:bc:83:bb:e5:ab:1d:5c:88:
         9e:b6:4d:f0:b3:10:73:84:c9:6a:eb:4d:f3:f0:cc:a5:80:3f:
         e5:b4:ba:91:ef:c8:8f:be:45:eb:d8:ad:3f:18:8e:dd:f7:c0:
         d0:92:80:21:83:c6:86:e6:c0:af:42:09:49:f4:ce:7b:a2:35:
         5e:3e:a4:5b:e4:9c:49:52:9a:ee:b5:fb:fb:b6:d5:e3:c7:0c:
         50:a6:65:54:28:92

4安装 harbor
创建安装目录
mkdir /data/install -p
cd /data/install/

安装 harbor
/data/ssl 目录下有如下文件：
ca.key  ca.pem  ca.srl  harbor.csr  harbor.key  harbor.pem

cd /data/install/
#把harbor 的离线包 harbor -offline -installer -v1.4.0.tgz 上传到这个目录，离线包在课件里提供了，可
自行下载：
解压：
tar zxvf harbor -offline -installer -v1.4.0.tgz
cd harbor

责。
 #common 目录：存放模板配置
#ha目录：做 harbor 高可用的
修改配置文件：
vim harbor.cfg

hostname = harbor
#修改hostname ，跟上面签发的证书域名保持一致
ui_url_protocol = https
#协议用https
ssl_cert = /data/ssl/ harbor.pem
ssl_cert_key = /data/ssl/ harbor.key
邮件和ldap不需要配置，在 harbor的web界面可以配置
其他配置采用默认即可
harbor默认的账号密码： admin/Harbor12345

安装 docker -compose

yum install docker -compose -y

./install.sh --with-notary --with-clair
#clair 开启镜像的漏洞扫描

安装过程会出现上面的界面，说明安装正常， docker ps 显示如下，说明容器启动正常

责。

在自己电脑修改 hosts文件，添加如下一行， 然后保存即可
**192.168.40.13 2  harbor**

> **注意：**

如何停掉 harbor：
docker -compose stop
如何启动 harbor：
docker -compose st art

**5. harbor  图像化 界面使用说明**
在浏览器输入：
https://harbor/
出现如下界面，说明登陆正常

责。

账号： admin
密码： Harbor12345
输入账号密码出现如下：

所有基础镜像都会放在 library 里面，这是一个公开的镜像仓库

新建项目 ->起个项目名字 test（把访问级别 公开那个选中，让项目 才可以被公开使用）

在harbor机器上修改 docker配置，修改之后的配置 如下
cat  /etc/docker/daemon.json

{
"registry -mirrors":["https://rsbud4vc.mirror.aliyuncs.com","https://registry.docker -
cn.com","https://docker.mirrors.ustc.edu.cn","https://dockerhub.azk8s.cn","http://hub -
mirror.c.163.com","http://qtid6917.mirror.aliyuncs.com"],
"insecure -registries":["192. 168.40.132"],

责。
 "exec -opts":["native.cgroupdriver=systemd"],
 "log-driver":"json -file",
 "log-opts": {
  "max -size": "100m"
  },
 "storage -driver":"overlay2",
 "storage -opts": [
  "overlay2.override_kernel_check=true"
  ]
}

修改配置之后使配置生效：
systemctl daemon -reload && systemctl restart docker

> **注意：**
配置新增加了一行内容如下：
"insecure -registries":["192.168.40.132"],
上面增加的内容表示我们内网访问 harbor的时候走的是 http，192.168.40.132 是安装 harbor
机器的 ip

登录 harbor ：
docker login 192.168.40.132

Username ：admin
Password :  Harbor 12345

输入账号密码之后看到如下，说明登录成功了：
Login Succeeded

6.上传镜像到 harbor 仓库
在harbor 机器上操作：
拉取 tomcat 镜像到本机
docker pull tomcat
docker tag tomcat :latest  192.168.40.132 /test/ tomcat:v1

责。
 docker push 192.168.40.132 /test/ tomcat:v1
执行上面命令就会把 192.168.40.132 /test/ tomcat:v1 上传到 harbor 里的 test项目下

7.从harbor 仓库下载镜像
在harbor 机器上删除镜像
docker rmi -f 192.168.40.132/test/tomcat:v1
拉取镜像
docker pull 192.168.40.132/test/tomcat:v1

微服务介绍
1.什么是微服务 ？
微服务是用于构建应用程序的架构风格，一个大的系统可由一个或者多个微服务组成，微服务架构可将应
用拆分成多个核心功能，每个功能都被称为一项服务，可以单独构建和部署，这意味着各项服务在工作和
出现故障的时候不会相互影响 。

责。
**2. 大型电商平台的 微服务功能图**

总结：   微服务架构是把一个大的系统按照不同的业务单元分解成多个职责单一的小系统，并利用简单 的
方法使多个小系统相互协作，组合成一个大系统，各个小的系统是独立部署的，它们之间是松耦合的。

3.为什么要用微服务？
**1、单体架构扩展性差、维护成本高、不可靠**

互动： 什么是单体架构 ？

在单体架构下 修改代码 ，需要把整个代码重新编译，重新部署， 这个时间周期会很长 ；
单体架构下的所有代码模块都耦合在一起，代码量大，维护困难 ，想要更新 一个模块的 代码，也可能会影

责。
 响其他模块，不能 很好的 定制化代码 。
所有模块都用同一个数据库，存储方式比较单一。
**2、微服务中可以有 java编写、有 Python 编写的，他们都是靠 restful 架构风格统一成一个系统的，所**
以微服务本身与具体技术无关、扩展性强
4.微服务特性
1）灵活部署、独立扩展
传统的单体架构是以整个系统为单位进行部署，而微服务则是以每一个独立组件（例如 订单服务，商品服
务）为单位进行部署。

2）资源的有效隔离
每一个微服务拥有独立的数据源，假如微服务 A想要读写微服务 B的数据库，只能调用微服务 B对外暴
露的接口来完成。这样有效避免了服务之间争用数据库和缓存资源所带来的问题。 另外微服务各模块部署
在k8s中，可以进行 CPU、内存等资源的限制和隔离。

3）高度可扩展性
随着某些服务 模块的不断扩展，可以跨多个服务器和基础架构进行部署，充分满足 业务需求。

4）易于部署
相对于传统的单体式应用，基于微服务的应用更加模块化且小巧 ，且易于部署。

5）服务组件化
在微服务架构中，需要我们对服务进行组件化分解，服务是一种进程外的组件，它通过 HTTP 等通信协议
进行协作，而不是像传统组件那样镶入式的方式协同工作，每一个服务都独立开发、部署、可以有效避免
一个服务的修改引起整个系统的重新部署。

6）去中心化治理
在整个微服务架构，通过采用轻量级的契约定义接口，使得我们 对服务本身的具体技术平台不再那么敏
感，这样整个微服务架构系统中的各个组件就能针对不同的业务特点选择不同的技术平台 。

7）容错设计
在微服务架构中，快速检测出故障源并尽可能地自动恢复服务是必须被设计考虑的，通常 我们都希望在每
个服务中实现监控和日志记录。比如 对服务状态、断路器状态、吞吐量、网络延迟等关键数据 进行可视化
展示。

8）技术栈不受限
在微服务架构中，可以结合项目业务及团队的特点，合理地选择技术栈。

9）局部修改容易部署
单体应用只要有修改，就得重新部署整个应用，微服务解决了这样的问题。

责。

10）易于开发和维护
一个微服务只会关注一个特定的业务功能，所以它业务清晰，代码量较少。

5.什么样的项目适合 使用微服务 ？
在复杂度 比较低的项目中 ，单体架构就可以满足需求，而且部署效率也会比较高 ，在复杂度比较高的项目
中，单体架构就不能满足 了，需要进行微服务化 。
微服务可以按照业务功能本身的独立性来划分，如果系统提供的业务是非常底层的，如：操作系统内核、
存储系统、网络系统、数据库系统等，这类系统都偏底层，功能和功能之间有着紧密的配合关系，如果强
制拆分为较小的服务单元，会让集成工作量急剧上升，并且这种人为的切割无法带来业务上的真正的隔
离，所以无法做到独立部署和运行，也就不适合做成微服务了。
那到底什么样的项目适合微服务呢 ？
**1. 业务并发 量大，项目复杂 ，访问流量高，为了将来更好的扩展， 随时对代码更新维护， 可以使用微服**
务
**2. 代码依赖程度高，想要解耦合， 交给多个开发团队维护**
**3. 业务初期，服务器数量少，可以使用微服务，能 有效节省资源。**
**4. 从思想上 ： 对未来有清晰的认识， 对技术更新 要保持着一种自信 ，超前思维 ，知道这个东西在将来肯**
定会发展起来。
这就告诉了我们一个道理，在学习技术的时候，适合 自己的 才是最好的， 比方说很多人说我们公司单体架
构用的也挺好的啊，为什么还要用微服务，其实他们再用单体可能适合他们业务需求，但是我们公司可能
业务规模大，项目复杂，我就想要用微服务，或者我们在未来上有更大的远见，那我也会选择用微服务，
不要说看别人用，我也用，而是我用是符合我们实际需求的， 一切脱离实际业务的微服务都是耍流氓。
**6. 使用微服务需要考虑的问题**
6.1统一的配置 管理中心
服务拆分以后，服务的数量非常多，如果所有的配置都以配置文件的方式放在应用本地的话，非常难以管
理，可以想象当有几百上千个进程中有一个配置出现了问题，是很难将它找出来的，因而需要有统一的配
置中心，来管理所有的配置，进行统一的配置下发。
在微服务中，配置往往分为几类，一类是几乎不变的配置，这种配置可以直接打在容器镜像里面，第二类
是启动时就会确定的配置，这种配置往往通过环境变量，在容器启动的时候传进去，第三类就是统一的配
置，需要通过配置中心进行下发，例如在大促的情况下，有些功能需要降级，哪些功能可以降级，哪些功

责。
 能不能降级，都可以在配置文件中统一配置。
**6.2 全链路监控**
1）系统和 应用的监控

监控系统和服务的健康状态和性能瓶颈， 当系统出现异常的时候，监控系统可以配合告警系统，及时地发
现，通知，干预，从而保障系统的顺利运行。

2）调用关系的监控
对代码调用关系 进行监控
**6.3 日志收集**
业务层面、代码层面 、系统层面
**7. 常见的微服务框架**
第一代微服务框架
SpringCloud
SpringCloud 为开发者提供了快速构建分布式系统的通用模型的工具（包括配置管理、服务发现 注册、
熔断器、 断路器、 智能路由、微代理、控制总线、一次性令牌、全局锁、领导选举、分布式会话、集群状
态、负载均衡、数据监控 等）

第二代微服务框架
dubbo
dubbo 是一个阿里巴巴开源出来的一个分布式服务框架，致力于提供高性能和透明化的 RPC远程服务调
用方案，以及 SOA 服务治理方案

第三代微服务框架
1.ServiceMesh （服务网格） 、k8s
istio 是开源的 ServiceMesh （服务网格） ， ServiceMesh 翻译成中文就是服务网格

责。
**8. 对不同的 微服务框架 进行对比分析**
**8.1 框架背景对比**
**8.1.1 SpringCloud**
来源于SpringSource ，具有 Spring 社区的强大 背景支持 ，还有  Netflix 强大的后盾与技术输出。
Netflix 作为一家成功实践微服务架构的互联网公司，在几年前就把几乎整个微服务框架开源贡献给了社
区，这些框架开源的整套微服务架构套件是 SpringCloud 的核心。

Eureka: 服务注册发现框架；
Zuul: 服务网关；
Karyon: 服务端框架；
Ribbon: 客户端框架；
Hystrix: 服务容错组件；
Archaius: 服务配置组件；
Servo: Metrics 组件；
Blitz4j: 日志组件。
Pinpoint ：全链路监控组件
**8.1.2 Dubbo**
是一个分布式服务框架，是国内互联网公司开源做的比较不错的阿里开放的微服务化治理框架，致力于提
供高性能和透明化的 RPC远程服务调用方案，以及 SOA 服务治理方案。  其核心部分包含（官网） :
远程通讯 : 提供对多种基于长连接的 NIO框架抽象封装，包括多种线程模型，序列化，以及 “请求-响
应”模式的信息交换方式；
集群容错 : 提供基于接口方法的透明远程过程调用，包括多协议支持，以及软负载均衡，失败容错，地
址路由，动态配置等集群支持；
自动发现 : 基于注册中 心目录服务，使服务消费方能动态的查找服务提供方，使地址透明，使服务提供
方可以平滑增加或减少机器。

Dubbo 也是采用全 Spring 配置方式，透明化接入应用，对应用没有任何 API侵入，只需用  Spring 加载
Dubbo 的配置即可， Dubbo 基于 Spring 的Schema 扩展进行加载。当然也支持官方不推荐的  API 调
用方式。

**8.1.3 k8s、 Istio**
作为用于微服务服务聚合层管理的新锐项目，是  Google 、IBM、Lyft（海外共享出行公司、 Uber 劲
敌） 首个共同联合开源的项目，提供了统一的连接，安全，管理和监控微服务的方案。

责。
 目前是针对  Kubernetes 环境的，社区宣称在未来几个月内会为虚拟机和  Cloud Foundry 等其他环境
增加支持。  Istio 将流量管理添加到微服务中，并为增值功能（如安全性，监控，路由，连接管理和策
略）创造了基础。
HTTP 、gRPC 和 TCP 网络流量的自动负载均衡；
提供了丰富的路由规则，实现细粒度的网络流量行为控制；
流量加密、服务间认证，以 及强身份声明；
全范围（ Fleet -wide ）的策略执行；
深度遥测和报告。
**8.2 开源社区活跃度对比**
开源社区情况：现如今企业在采用云计算首选开源，而选择一个开源框架，社区的活跃度将作为重要参考
选项。
查看下在 Github 上的更新时间
SpringCloud ：Spring Cloud · GitHub → 所有项目均更新于『 1 小时』内。
Dubbo ：Dubbo · GitHub → 核心项目最近更新于『一个月乃至数月』前。
istio：istio · GitHub → 所有项目均更新于『 30 分钟』内。

可见，项目在社区活跃度上， Istio > SpringCloud > Dubbo ，结合稳定性来看，对于使用  Java 开发业
务较多的企业， SpringCloud 是相对更优的选择，对于更多企业来说，与语言几乎无绑定的 Istio 也是可
以好好期待一下其在社区的发展。

总结：结合项目背景、提供功能、社区更新活跃度， SpringCloud 是目前阶段 发展最早的 微服务框架方
案，Istio 作为 Kubernetes 的优先支持来讲，也是一个值得关注的方案 ，而且发展潜力巨大，相信不久
的将来 90%+ 的k8s用户都会使用 istio。目前对比来看， dubbo 则显得稍逊下来。

责。
 SpringCloud 概述

1.SpringCloud 是什么？
官方解释 ：

官网：  https://spring.io/projects/spring -cloud/

SpringCloud 是一系列框架的 有序集合 。它利用 SpringBoot 的开发便利性巧妙地简化了分布式系统基础
设施的开发，如服务发现注册、配置中心、消息总线、负载均衡、断路器、数据监控等，都可以用
SpringBoot 的开发风格做到一键启动和部署。 SpringCloud 并没有重复制造轮子，它只是将各家公司开
发的比较成熟、经得起实际考验的服务框架组合起 来，通过 SpringBoot 风格进行再封装屏蔽掉了复杂的
配置和实现原理，最终给开发者留出了一套简单易懂、易部署和易维护的分布式系统开发工具包。

责。
 2.SpringCloud 和SpringBoot 什么关系？
SpringBoot 专注于快速方便的开发单个个体微服务。
SpringCloud 是关注全局的微服务协调整理治理框架，它将 SpringBoot 开发的一个个单体微服务整合并
管理起来， SpringBoot 可以离开 SpringCloud 独立开发项目，但是 SpringCloud 离不开
SpringBoot ，属于依赖关系。

3.SpringCloud 优缺点
1）SpringCloud 来源于 Spring ，质量、稳定性、持续性都可以得到保证。
SpirngCloud 以SpringBoot 为基础开发框架 ，可以给开发者大量的微服务开发经验 ，例如，只要极少量
的标签，你就可以创建一个配置服务器，再加一些标签，你就可以得到一个客户端库来配置你的服务 ，更
加便于业务落地。
2）SpringCloud 是Java领域最适合做微服务的框架 ，对Java 开发者来说就很容易开发。
3）耦合度低，不影响其他模块
4）多个开发团队可以并行开发项目，提高开发效率
5）直接写自己的代码即可，然后暴露接口，通过组件进行服务通信。

缺点：
只能针对 Java 开发
部署麻烦、组件多
每个微服务都可以用一个数据库，导致数据管理复杂
一套完整的微服务 包括自动化部署，调度，资源管理，进程隔离，自愈，构建流水线等功能 ，单靠
SpringCloud 是无法实现的 ，所以 SpringCloud+ k8s才是最好的方案
4.为何要将 SpringCloud 项目部署到 k8s平台？

Spring Cloud 只能用在  Spring Boot的java环境中，而 kubernetes 可以适用于任何 开发语言 ，只要能
被放进docker 的应用，都可以在 kubernetes 上运行，而且更轻量，更简单 。

责。

每个微服务可以部署多个，没有多少依赖，并且有负载均衡能力，比如一个服务部署一个副本或 5个副
本，通过 k8s可以更好的去扩展我们的应用 。

Spring 提供应用的打包， Docker 和Kubernetes 提供部署和调度。 Spring 通过 Hystrix 线程池提供应用
内的隔离，而 Kubernetes 通过资源，进程和命名空间来提供隔离。 Spring 为每个微服务提供健康终
端，而 Kubernetes 执行健康检查，且把流量导到健康服务。 Spring 外部化配置并更新它们，而
Kubernetes 分发配置到每个微服务。

SpringCloud 很多功能都跟 kubernetes 重合， 比如服务发现，负载均衡，配置管理 ，所以如果把
SpringCloud 部署到 k8s，那么很多功能可以直接使用 k8s原生的 ，减少复杂度 。

SpringCloud 容易上手， 是对开发者 比较友好的平台 ；Kubernetes 是可以实现 DevOps 流程的 ，
SpringCloud 和kubernetes 各有优点，只有结合起来，才能发挥更大的作用，达到最佳的效果 。

5.SpringC loud 项目部署到 k8s的流程
制作镜像 --->控制管理 pod--->暴露应用 --->对外发布应用 --->数据持久化 ---→日志/监控
1.制作镜像 ： 应用程序 、运行环境 、文件系统
2.控制器 管理 pod：deployment 无状态部署 、statefulset 有状态部署 、Daemonset 守护进程部署 、
job & cronjob 批处理
3.暴露应用 ：服务发现、负载均衡
4.对外发布应用 ：service 、Ingress  HTTP/HTTPS 访问
5.pod数据持久化 ：分布式存储 -ceph 和gluster
6.日志/监控：efk、prometheus 、pinpoint 等
SpringCloud 组件介绍
**1. 服务发现与注册组件 Eureka**
Eureka 是Netflix 开发的服务发现框架，  SpringCloud 将它集成在 自己的 子项目 spring -cloud -netflix
中，以实现 SpringCloud 中服务发现 和注册 功能。 Eureka 包含两个组件： Eureka Server 和Eureka

责。
 Client 。

互动： Netflix 是什么？
Netflix 在SpringCloud 项目中占着重要的作用， Netflix 公司提供了包括 Eureka 、Hystrix 、Zuul、
Archaius 等在内的很多组件，在微服务架构中至关重要 。

互动：  举个例子 服务发现与注册

我们在买车的时候，需要找中介，如果不找中介，我们自己去找厂商或者个人车主，这是很麻烦的，也很
浪费时间， 所以为了方便，我们一般去找中介公司，把我们的需求说出来，他们就会按需给我们推荐车
型，我们相当于微服务架构中的消费者 Consumer ，中介相当于微服务架构中的提供者 Provider ，
Consumer 需要调用 Provider 提供的一些服务，就像是我们要买的车一样。

**1.1 Eureka 组件**

Eureka Server
Eureka Server 提供服务注册 中心，各个节点启动后，会 将自己的 IP和端口等网络信息注册到 Eureka
Server 中，这样 Eureka Server 服务注册表中将会存储所有可用服务节点的信息， 在Eureka 的图形化界
面可以看到所有注册的节点信息 。

Eureka Client
Eureka Client 是一个 java客户端 ，在应用启动后， Eureka 客户端将会 向Eureka Server 端发送心跳，
默认周期是 30s，如果 Eureka Server 在多个心跳周期内没有接收到某个节点的心跳， Eureka Server 将
会从服务注册表中把这个 服务节点移除 (默认 90秒)。

Eureka Client 分为两个角色 ，分别是 Application Service 和Application Client
Application Service 是服务提供方，是注册到 Eureka Server 中的服务。
Application Client 是服务消费方，通过 Eureka Server 发现其他服务并消费。

责。
**1.2 Eureka 架构原理**

Register( 服务注册 )：当Eureka 客户端向 Eureka  Server 注册时，会 把自己的 IP、端口、运行状况等信
息注册给 Eureka  Server 。
Renew( 服务续约 )：Eureka 客户端会每隔 30s发送一次心跳来续约，通过续约来告诉 Eureka  Server 自
己正常，没有出现问题 。正常情况下，如果  Eureka Server 在90秒没有收到  Eureka 客户的续约，它
会将实例从其注册表中删除。
Cancel( 服务下线 )：Eureka 客户端在程序关闭时向 Eureka 服务器发送取消请求。  发送请求后，该客户
端实例信息将从服务器的实例注册表中删除 ，防止 consumer 调用到不存在的服务。 该下线请求不会自
动完成 ，它需要调用以下内容： DiscoveryManager.getInstance().shutdownComponent();
Get Registry( 获取服务注册列表 )：获取其他服务列表。
Replicate( 集群中数据同步 )：eureka 集群中的数据复制与同步。
Make Remote Call( 远程调用 )：完成服务的远程调用。

**2. 客户端负载均衡之 Ribbon**
**2.1 Ribbon 简介**
Ribbon 是一个基于 HTTP 和TCP的客户端负载均衡器 ，主要提供客户侧的软件负载均衡算法 ，运行在消
费者端 。客户端负载均衡是当浏览器向后台发出请求的时候，客户端会向 Eureka Server 读取注册到 服务
器的可用服务信息列表，然后根据设定的负载均衡策略 ，抉择出向哪台服务器发送请求。在客户端就进行
负载均衡算法分配。 Ribbon 客户端组件提供一系列完善的配置选项，比如连接超时、重试、重试算法
等。下面 是用到的
一些负载均衡策略：

责。
 随机策略 ---随机选择 server
轮询策略 ---轮询选择，  轮询 index ，选择 index 对应位置的 Server
重试策略 --在一个配置时间段内当选择 Server 不成功，则一直尝试使用 subRule 的方式选择一个可用的
server
最低并发策略 --逐个考察 server ，如果 server 断路器打开，则忽略，再选择其中并发链接最低的 server
可用过滤策略 --过滤掉一直失败并被标记为 circuit tripped 的server ，过滤掉那些高并发链接的 server
（active connections 超过配置的阈值）或者使用一个 AvailabilityPredicate 来包含过滤 server 的逻
辑，其实就就是检查 status 里记录的各个 Server 的运行状态；
响应时间加权重策略 --根据 server 的响应时间分配权重，响应时间越长，权重越低，被选择到的概率也
就越低。响应时间越短，权重越高，被选中的概率越高，这个策略很贴切，综合了各种因素，比如：网
络，磁盘， io等，都直接影响响应时间 ；
区域权重策略 --综合判断 server 所在区域的性能，和 server 的可用性，轮询选择 server 并且判断一个
AWS Zone 的运行性能是否可用，剔除不可用的 Zone 中的所有 server 。

互动：  举个列子 说明 ribbon

比如我们设计了一个秒杀系统，但是为了整个系统的  高可用  ，我们需要将这个系统做一个集群，而这个
时候我们消费者就可以拥有多个秒杀系统的调用途径了，如下图。

如果这个时候我们没有进行一些  均衡操作  ，如果我们对  秒杀系统 1 进行大量的调用，而另外两个基本不
请求，就会导致  秒杀系统 1 崩溃，而另外两个就变成了傀儡，那么我们为什么还要做集群，我们高可用
体现的意义又在哪呢？
所以 Ribbon  出现了，注意我们上面加粗的几个字 —— 运行在消费者端  。指的是， Ribbon  是运行在消
费者端的负载均衡器，如下图。

责。

其工作原理就是  Consumer  端获取到了所有的服务列表之后，在其 内部 使用负载均衡算
法 ，进行对多个系统的调用。
**2.2 Ribbon 的功能**
易于与服务发现组件（比如 Eureka ）集成
使用 Archaius 完成运行时配置
使用 JMX 暴露运维指标，使用 Servo 发布
多种可插拔的序列化选择
异步和批处理操作
自动 SLA框架
系统管理 /指标控制台
**2.3 Ribbon 和nginx 对比分析**
区别：
Ribbon 实现的是客户端负载均衡，它可以在客户端经过一系列算法来均衡调用服务。 Ribbon 工作时分
两步：
第一步： 从Eureka Server 中获取服务注册信息列表 ，它优先选择在同一个  Zone 且负载较少的
Server 。
第二步：根据用户指定的策略，在从 Server 取到的服务注册列表中选择一个地址，其中 Ribbon 提供了
多种策略，例如轮询、随机等。

责。

Nginx 是服务器端负载均衡 ，所有请求统一交给 nginx ，由 nginx 实现负载均衡请求转发，属于服务器端
负载均衡。

**3. 服务网关 Zuul**
Zuul 是SpringCloud 中的微服务网关，首先是一个微服务。也是会在 Eureka 注册中心中进行服务的注
册和发现。也是一个网关，请求应该通过 Zuul 来进行路由。 Zuul 网关不是必要的 ，是推荐使用的。

互动： 网关是什么？

是一个网络整体系统中的前置门户入口。 请求首先通过网关， 进行路径的路由， 定位到具体的服务节点上。

Zuul 网关的作用 ：

统一入口：为服务提供一个唯一的入口，网关起到外部和内部隔离的作用，保障了后台服务的安全性。

责。
 鉴权校验：识别每个请求的权限，拒绝不符合要求的请求。
动态路由：动态的将请求路由到不同的后端集群中。
减少客户端与服务端的耦合：服务可以独立发展，通过网关层来做映射。

**4. 熔断器 Hystrix**
Hystrix 的中文名字是 “豪猪”，豪猪 是满身长满了刺， 能够保护自己不受天敌的伤害，代表了一种防御机
制，Hystrix 在SpringCloud 中负责服务熔断 和服务降级的作用。

什么是 服务熔断？（熔断可 以保护服务） ：

在讲熔断之前先看个概念：  服务雪崩

假设有 A、B、C三个服务，服务 A调用服务 B和C，链路关系如下：

假设服务 C因为请求量大， 扛不住请求， 变得不可用， 这样就是积累大量的请求， 服务 B的请求也会阻塞，
会逐渐耗尽线程资源，使得服务 B变得不可用，那么服务 A在调用服务 B就会出现问题，导致服务 A也
不可用，那么整条链路的服务 调用都失败了，我们称之为雪崩。

接下来看下服务熔断：

互动： 举个生活中的例子
当电路发生故障或异常时，伴随着电流不断升高，并且升高的电流有可 能能损坏电路中的某些重要器件，
也有可能烧毁电路甚至造成火灾。若电路中正确地安置了保险丝，那么保险丝就会在电流异常升高到一定
的高度和热度的时候，自身熔断切断电流，从而起到保护电路安全运行的作用。

责。

在微服务架构中， 在高并发情况下，如果请求数量达到一定极限（可以自己设置阈值），超出了设置的阈
值，Hystrix 会自动开启服务保护功能， 然后通过服务降级的方式返回一个友好的提示给客户端。 假设当10
个请求中，有 10%失败时，熔断器就会打开，此时再调用此服务，将会直接返回失败，不再调远程服务。
直到 10s钟之后，重新检测该触发条件，判断是否把熔断器关闭，或者继续打开。

服务降级（提高用户体验效果） ：
在高并发 的场景下， 当服务器 的压力剧增 时，根据当前业务 以及流量 的情况，对一些服务和页面进行策略
控制， 对这些请求做简单的处理或者不处理 ，来释放服务器资源用以保证核心业务不受影响， 确保业务 可
以正常对外提供服务 ，比如电商平台，在针对 618、双 11的时候会有一些秒杀场景，秒杀的时候请求量
大，可能会返回报错标志“当前请求人数多，请稍后重试” 等，如果使用服务降级，无法提供服务的时
候，消费者会调用降级的操作，返回服务不可用等信息，或者返回提前准备好的静态页面 写好的信息。

**5. API网关 Springcloud  Gateway**
互动：  为什么 学习了 网关 Zuul，又要讲 Spring Cloud Gateway 呢？
原因很简单 ，就是 Spring Cloud 已经放弃 Zuul 了。现在 Spring Cloud 中引用的还是 Zuul 1.x 版本，而
这个版本是基于过滤器的，是阻塞 IO，不支持长连接 ，spring 官网上也已经没有 zuul 的组件了 ，所以给
大家讲下 SpringCloud 原生的网关产品 Gateway 。

Spring Cloud Gateway 是Spring Clou d新推出的网关框架，之前是  Netflix Zuul ，由spring 官方基于
Spring5.0,Spring Boot2.0,Project Reactor 等技术开发的网关 ，该项目提供了一个构建在 Spring
Ecosystem 之上的 API网关，旨在提供一种简单而有效的途径来发送 API，并向他们提供交叉关注点，例
如：安全性，监控 /指标和弹性 .

SpringCloud Gateway 特征：
SpringCloud 官方对 SpringCloud Gateway 特征介绍如下：
（1）集成  Hystrix 断路器
（2）集成  Spring Cloud Discov eryClient
（3）Predicates 和 Filters 作用于特定路由，易于编写的  Predicates 和 Filters
（4）具备一些网关的高级功能：动态路由、限流、路径重写
从以上的特征来说，和 Zuul 的特征差别不大。 SpringCloud Gateway 和Zuul 主要的区别，还是在底层
的通信框架上。

简单说明一下上文中的三个术语：
1）Filter （过滤器）：

责。
 和Zuul 的过滤器在概念上类似，可以使用它拦截和修改请求，并且对上游的响应，进行二次处理。过滤器
为org.springframework.cloud.gateway.filter.GatewayFilter 类的实例。
2）Route （路由）：
网关配置的基本组成模块，和 Zuul 的路由配置模块类似。一个 Route 模块由一个  ID，一个目标  URI，一
组断言和一组过滤器定义。如果断言为真，则路由匹配，目标 URI会被访问。
3）Predicate （断言）：
这是一个 Java8 的Predicate ，可以使用它来匹配 来自 HTTP 请求的任何内容，例如 headers 或参数。断
言的输入类型是一个 ServerWebExchange 。

**6. 配置中心 SpringCloud  Config**
SpringCloud Confi g是一个解决分布式系统的配置管理方案，它包含了 server 和client 两个部
分。 server 用来获取远程的配置信息（默认为  Git 仓库），并且以接口的形式提供出去 ，client 根据
server 提供的接口读取配置文件，以便于初始化自己的应用。如果配置中心出现了问题，将导致灾难性
的后果，因此在生产环境下配置中心都会做集群，来保证高可用。此处配置高可用实际就是把多个配置中
心（指定同一个  Git 远程仓库）注册到注册中心。
将SpringCloud 项目部署到 K8S平台的注意事项
1.如何进行服务发现？
2.如何进行配置管理？
3.如何进行负载均衡？
4.如何访问 k8s中的服务？
5.如何通过 k8s进行服务编排？
6.k8s部署 Spring  Cloud 项目的整体发布流程

1.如何进行服务发现 ？
可以通过 springcloud 的Eureka ，也可以通过 k8s自身的 coredns 。如果是把 Springcloud 项目迁移到
k8s，可以使用原来 的Eureka ，这样可以避免开发 人员对原来的代码进行大量的修改。 通常情况下，我们
的线上的服务在迁移到 k8s环境下的时候，都是采用平滑迁移的方案。服务治理与注册中心等都是采用原
先的组件。比如 springcloud 应用，在 k8s环境下还是用原来的一套注册中心（如 eureka ），服务治理
（hystrix ，ribbon ）等

使用 Kubernetes service 发现 pod：
Kubernetes 中的 pod是有生命周期的，可以被创建、也可以被销毁， k8s中的 pod可以有多组，每组
pod可以称为一个微服务，那么怎么能让这些微服务相互访问呢？需要在每组 pod前端有一个固定的接
入层，叫做 service ，service 解决了对后端 pod进行负载均衡和自动发现的能力，但是我们怎么还需要

责。
 知道 service 的ip，这样才能被其他服务访问，那么怎么解决这一问题呢？
使用 coredns发现 service （服务）：
coredns可以解决 Service 的发现问题， k8s将Service 的名称当做域名注册到 coredns中，通过
Service 的名称就可以访问其提供的服务。 Coredns 支持的域名格式：
<service_name>.<namespace>.svc.<cluster_domain> 。
默认的域名是 <service_name>.<namespace>.svc. cluster .local

2.如何进行配置管理？
通过在 k8s中部署 SpringCloud Config ，也可以通过 k8s自带的的 configmap 。还可以使用 spring -
cloud -kubernetes 进行配置管理。

如果微服务架构中没有使用统一配置中心时，所存在的问题：
配置文件分散在各个项目里，不方便维护
配置内容安全与权限，实际开发中，开发人员是不知道线上环境的配置的
更新配置后，项目需要重启

k8s中自带的 configmap 怎么存配置？
ConfigMap 用于保存配置数据的键值对，可以用来保存单个属性，也可以用来保存配置文件。
ConfigMap 跟secret 很类似，但它可以更方便地处理不包含敏感信息的字符串。
怎么通过 ConfigMap 达到配置中心 的作用 ？
创建一个 configmap 资源，对应着一份配置文件，可以将该资源通过数据卷的形式映射到 Pod上，这样
Pod就能用上这个配置文件了  ，以管理 mysql 配置文件为例用下图演示：

责。
 spring -cloud -starter -kubernetes -config
spring -cloud -starter -kubernetes -config 是spring -cloud -starter -kubernetes 框架下的一个库，作用
是将 kubernetes 的configmap 与SpringCloud Config 结合起来，通过 spring -cloud -starter -
kubernetes -config ，我们的应用就像在通过 SpringCloud Config 取得配置信息，只不过这里的配置信
息来自 kubernetes 的configmap ，而不是 SpringCloud Config  server ，SpringCloud Config 来配置
的应用几乎不用修改代码，仅仅调整了配置和依赖，就能顺利迁移到 kubernetes 之上，直接使用原生的
配置服务，并且 SpringCloud Config Server 也可以不用在 kubernetes 上部署了 。

3.如何进行负载均衡？
通过 springcloud 的Ribbon ，也可通过 k8s的service 、Ingress  Controller
4.如何对外发布应用？
通过 Ingress

如何通过 k8s进行服务编排？

通过编写 yaml 文件，对每个微服务进行发布

责。
 5.k8s部署 Spring  Cloud 项目的整体发布流程

开发代码 ->提交代码到代码仓库 ->Jenkins 调k8s API ->动态生成 Jenkins  Slave  Pod->Slave Pod 拉取
git上的代码 ->编译代码 ->打包镜像 ->推送镜像到镜像仓库 harbor 或者 docker  hub->Slave Pod 工作
完成之后自动删除 ->通过 k8s编排服务发布到测试、生产平台 ->通过 Ingress 发布服务

6.如何通过 k8s进行服务编排？
事先写好资源清单文件，然后放到 gitlab ，我们在调用 jenkins 的时候，通过 pipeline 里写上 kubectl
apply  更新 yaml 文件，就可以实现自动编排了。

安装和配置数据存储仓库 MySQL
1.MySQL 简介
2.MySQL 特点
3.安装和配置 MySQL
4.在MySQL 数据库导入数据
5.对MySQL 数据库 进行授权

责。
 1.My SQL 简介
MySQL 是一款安全、跨平台、高效的，并与 PHP、Java 等主流编程语言紧密结合的数据库系统。该数据
库系统是由瑞典的 MySQL AB 公司开发、发布并支持，由  MySQL 的初始开发人员  David Axmark 和
Michael Monty Widenius 于 1995 年建立的。 MySQL 的象征符号是一只名为  Sakila 的海豚，代表着
MySQL 数据库的速度、能力、精确和优秀本质。

MySQL logo:

目前 MySQL 被广泛地应用在  Internet 上的中小型网站中。由于其体积小、速度快、总体拥有成本低，
尤其是开放源码这一特点，使得很多公司都采用  MySQL 数据库以降低成本。

MySQL 数据库可以称得上是目前运行速度最快的 SQL语言数据库之一。 除了具有许多其他数据库所不具
备的功能外， MySQL 数据库还是一种完全免费的产品，用户可以直接通过网络下载  MySQL 数据库，而
不必支付任何费用。

2.MySQL 特点
1) 功能强大
MySQL 中提供了多种数据库存储引擎，各引擎各有所长，适用于不同的应用场合，用户可以选择最合适
的引擎以得到最高性能， 可以处理每天访问量超过数亿的高强度的搜索  Web 站点。 MySQL5 支持事务、
视图、存储过程、触发器等。
2) 支持跨平台
MySQL 支持至少  20 种以上的开发平台， 包括  Linux 、Windows 、FreeBSD 、IBMAIX 、AIX、FreeBSD
等。这使得在任何平台下编写的程序都可以进行移植，而不需要对程序做任何的修改。
3) 运行速度快
高速是  MySQL 的显著特性。在  MySQL 中，使用了极快的  B 树磁盘表（ MyISAM ）和索引压缩；通过
使用优化的单扫描多连接，能够极快地实现连接； SQL 函数使用高度优化的类库实现，运行速度极快。
4) 支持面向对象
PHP 支持混合编程方式。编程方式可分为纯粹面向对象、纯粹面向过程、面句对象与面向过程混合  3 种
方式。

责。
 5) 安全性高
灵活和安全的权限与密码系统， 允许基本主机的验证。 连接到服务器时， 所有的密码传输均采用加密形式，
从而保证了密码的安全。
6) 成本低
MySQL 数据库是一种完全免费的产品，用户可以直接通过网络下载。
7) 支持各 种开发语言
MySQL 为各种流行的程序设计语言提供支持，为它们提供了很多的  API 函数，包括  PHP、ASP .NET 、
Java、Eiffel 、Python 、Ruby 、Tcl、C、C++、Perl 语言等。
8) 数据库存储容量大
MySQL 数据库的最大有效表尺寸通常是由操作系统对文件大小的限制决定的， 而不是由  MySQL 内部限
制决定的。 InnoDB 存储引擎将  InnoDB 表保存在一个表空间内，该表空间可由数个文件创建，表空间的
最大容量为  64TB ，可以轻松处理拥有上千万条记录的大型数据库。
9) 支持强大的内置函数
PHP 中提供了大量内置函数， 几乎涵盖了  Web 应用开发中的所有功能。 它内置了数据库连接、 文件上传
等功能， MySQL 支持大量的扩展库，如  MySQLi 等，可以为快速开发  Web 应用提供便利。

3.安装 MySQL
在192.168.40.130 上操作：

wget http://repo.mysql.com/mysql -community -release -el7-5.noarch.rpm
rpm -ivh mysql -community -release -el7-5.noarch.rpm
yum install mysql -server -y

权限设置
chown mysql:mysql -R /var/lib/mysql

初始化 MySQL
mysqld --initialize

启动 MySQL
systemctl start mysqld

查看 MySQL 运行状态
systemctl status mysqld

mysql 安装成功后，默认的 root 用户密码为空，你可以使用以下命令来创建 root 用户的密码 ，密码设置
成111111

mysqladmin -u root password " 111111 "

责。
 登陆数据库
mysql  -uroot  -p111111

创建数据库tb_order 、tb_product 、tb_stock
create database tb_product;
create database tb_stock;
create database tb_order ;

4.在Mysql 数据库导入数据
把相应的 sql语句上传到 mysql 机器的 root 目录下， sql文件分别是 order.sql 、product.sql 、stock.sql ，
这些文件在课件里大家可以搜索，会搜索到，按如下方法导入：

use tb_order
source /root/order.sql

use tb_stock
source /root/stock.sql

use tb_product
source /root/product.sql

5.对MySQL 数据库授权
grant all on *.* to 'root'@'10.244.%.%' identified by '111111';
grant all on *.* to 'root'@'192.168.%.%' identified by '111111';
flush  privileges;

grant all on *.* to 'root'@'%' identified by '111111' ;
flush  privileges;

将SpringCloud 微服务项目部署至 K8S平台
以下步骤均在 k8s的master1 节点操作

责。
 1.SpringCloud 的微服务电商框架

2.安装 openjdk 和maven
在k8s的master1 节点操作 :

yum install  java-1.8.0-openjdk   maven -3.0.5* -y

3.上传微服务源码包 到k8s的master 1节点
unzip microservic -test.zip
cd microservic -test

4.修改源代码，更改数据库连接地址
在k8s的master1 节点操作

1）修改库存数据库
cat  /root/microservic -test/stock -service/stock -service -biz/src/main/resources / application -
fat.yml

责。
 jdbc:mysql:// 192.168.40.130 :3306/tb_stock?characterEncoding=utf -8
#变成自己的数据库地址

2）修改产品数据库
cat /root/microservic -test/product -service/product -service -biz/src/ma in/resources /application -
fat.yml

jdbc:mysql:// 192.168.40.130 :3306/tb_product?characterEncoding=utf -8
#变成自己的数据库地址

3）修改订单数据库
cat /root/microservic -test/order -service/order -service -biz/src/main/resources/ application -
fat.yml

url: jdbc:mysql:// 192.168.40.1 30:3306/tb_order?characterEncoding=utf -8
#变成自己的数据库地址

5.通过 Maven 编译、构建、打包源代码
在k8s的master1 节点操作

修改源代码之后回到 /root/microservic -test目录下执行如下命令：
mvn clean package -D maven.test.skip=true

看到如下说明编译打包已经成功了：
[INFO] simple -microservice ............................... SUCCESS [52.385s]
[INFO] basic -common ...................................... SUCCESS [0.001s]
[INFO] basic -common -core ................................. SUCCESS [6:11.156s]
[INFO] gateway -service ............................ ....... SUCCESS [3:33.707s]
[INFO] eureka -service .................................... SUCCESS [12.075s]
[INFO] product -service ................................... SUCCESS [0.001s]
[INFO] product -service -api ............................... SUCCESS [0.271s]
[INFO] stock -service ..................................... SUCCESS [0.002s]
[INFO] stock -service -api ................................. SUCCESS [0.233s]
[INFO] product -service -biz ............................... SUCCESS [3.776s]
[INFO] stock -service -biz ................................. SUCCESS [0.332s]
[INFO] order -service ..................................... SUCCESS [0.000s]
[INFO] order -service -api ................................. SUCCESS [0.270s]
[INFO] order -service -biz .............................. ... SUCCESS [0.364s]
[INFO] basic -common -bom .................................. SUCCESS [0.000s]

责。
 [INFO] portal -service .................................... SUCCESS [0.738s]
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time: 11:13.305s
[INFO] Finished at: Wed Jan 20 15:53:22 CST 2021
[INFO] Final Memory: 92M/710M
[INFO] ------------------------------------------ ------------------------------
6.在k8s中部署 Eureka 组件
修改 k8s的master 1和node 1节点的 docker 的配置文件：

cat > /etc/docker/daemon.json <<EOF
{
"registry -mirrors":["https://rsbud4vc.mirror.aliyuncs.com","https://registry.docker -
cn.com","https://docker.mirrors.ustc.edu.cn","https://dockerhub.azk8s.cn","http://hub -
mirror.c.163.com","http://qtid6917.mirror.aliyuncs.com"],
"insecure -registries":["192. 168.40.132","harbor"],
"exec -opts":["native.cgroupdriver=systemd"],
 "log-driver":"json -file",
 "log-opts": {
  "max -size": "100m"
  },
 "storage -driver":"overlay2",
 "storage -opts": [
  "overlay2.override_kernel_check=true"
  ]
}
EOF

> **注意：**

责。
 daemon .json 中新增加了如下一行内容：
"insecure -registries":["192.168.40.132","harbor"],
这样才可以使用 harbor 私有镜像仓库

重启 docker 使配置生效
systemctl daemon -reload && systemctl restart  docker  && systemctl  status docker

在k8s的master1 节点操作

创建拉取私有镜像仓库需要的 secret

kubectl create ns ms && kubectl create secret docker -registry registry -pull-secret --docker -

```bash
server=192.168.40.132 --docker -username=admin --docker -password=Harbor12345  -n ms
```

在harbor 上创建一个项目 microservice

1）构建镜像
cd /root/microservic -test/eureka -service
docker build -t  192.168.40.132 /microservice/eureka:v1 .
docker  login  192.168.40.132
账号密码：  admin/Harbor12345
docker push 192.168.40.132 /microservice/eureka:v1

2）部署服务
cd /root/microservic -test/k8s
修改 eureka .yaml 文件，把镜像变 成image: 192.168.40.132 /microservice/eureka:v1

责。

3）更新 yaml 文件
kubectl apply -f eureka.yaml

4）查看 pod 状态
kubectl get pods -n ms

看到如下 running 说明 pod运行正常：
NAME       READY   STATUS    RESTARTS   AGE
eureka -0   1/1     Running   0          7m4s
eureka -1   1/1     Running   0          5m39s
eureka -2   1/1     Running   1          6m7s

上面运行没问题之后， 找到自己电脑的 hosts 文件， eureka.ctnrs.com

在浏览器访问 eureka. ctnrs .com 即可，可看到如下，说明 eureka 部署成功了：

> **注意：**
要想访问域名 eureka. ctnrs .com ，
这个需要在自己电脑的 hosts 文件新增加如下内容， 192.168.40.131 是default -http 和ingress -nginx -
controller 所在 node 节点的 ip地址。
**192.168.40.131 eureka. ctnrs .com**

7.在k8s中部署 网关 Gateway 服务
1）构建镜像

责。
 cd  microservic -test/gateway -service/
docker build -t  192.168.40.132 /microservice/ gateway :v1 .
docker push 192.168.40.132 /microservice/ gateway :v1

2）部署服务

cd /root/microservic -test/k8s
修改 gateway .yaml 文件，把镜像变成 image: 192.168.40.132 /microservice/ gateway :v1

3）更新 yaml 文件
kubectl apply -f gateway.yaml

4）查看 pod 状态
kubectl get pods -n ms  | grep gateway

5）看到如下 running 说明 pod 运行正常
gateway -c94f4d95c -2dqvw   1/1     Running   0          31s
gateway -c94f4d95c -l4jmq    1/1     Running   0          31s

6）配置 hosts 文件
gateway 的域名是 gateway. ctnrs .com ，需要在电脑找到 hosts 文件，再增加一行如下：
**192.168.40.131 gateway. ctnrs .com**

在浏览器访问 eureka. ctnrs .com 可看到 GATEWAY -SERVICE 已经注册到 eureka 了：

8.在k8s中部署 前端 portal 服务
1）构建镜像
cd  /root/microservic -test/portal -service
docker build -t  192.168.40.132 /microservice/ portal :v1 .
docker push   192.168.40.132 /microservice/portal:v1

责。
 2）部署服务
cd /root/microservic -test/k8s
修改 portal.yaml 文件，把镜像变成 image: 192.168.40.132 /microservice/portal:v1

3）更新 yaml 文件
kubectl apply -f portal.yaml
4）查看 pod 状态
kubectl get pods -n ms  | grep portal

看到如下 running 说明 pod运行正常：
portal -5f59cb767c -fv67r   1/1     Running   1          5m26s

5）配置 hosts 文件

要在自己电脑找到 hosts 文件，再增加一行如下内容：
**192.168.40.131 portal. ctnrs .com**

6）查看 portal 是否注册到 eureka 中
在浏览器访问 eureka. ctnrs .com 可看到 portal 服务已经注册到 eureka 了

7）访问前端页面
在浏览器访问 portal. ctnrs .com

可看到如下页面：

责。

9.在k8s中部署 订单 order 服务
1）构建镜像
cd  /root/microservic -test/order -service/order -service -biz
docker build -t  192.168.40.132 /microservice/ order :v1 .
docker push   192.168.40.132 /microservice/ order :v1

2）部署服务
cd /root/microservic -test/k8s
修改 order .yaml 文件，把镜像变成 image: 192.168.40.132 /microservice/ order :v1

3）更新 yaml 文件
kubectl apply -f order .yaml

4）查看 pod 状态
kubectl get pods -n ms  | grep order

看到如下 running 说明 pod运行正常：
order -75d9c4bbd7 -f6lhx    1/1     Running       0          3m10s

10.在k8s中部署产品 product 服务
1）构建镜像
cd  /root/microservic -test/product -service/product -service -biz
docker build -t  192.168.40.132 /microservice/ product :v1 .
docker push   192.168.40.132 /microservice/ product :v1

2）部署服务
cd /root/microservic -test/k8s
修改 product .yaml 文件，把镜像变成 image: 192.168.40.132 /micr oservice/ product :v1

3）更新 yaml 文件
kubectl apply -f product .yaml

4）查看 pod 状态
kubectl get pods -n ms  | grep product

责。
 看到如下 running 说明 pod运行正常：
product -775f5f74d9 -4nssp   1/1     Running   0          18s

11.在k8s中部署库存 stock 服务
1）构建镜像
cd  /root/microservic -test/stock -service/stock -service -biz
docker build -t  192.168.40.132 /microservice/ stock :v1 .
docker push   192.168.40.132 /microservice/ stock :v1

2）部署服务
cd /root/microservic -test/k8s
修改 stock .yaml 文件，把镜像变成 image: 192.168.40.132 /microservice/ stock :v1

3）更新 yaml 文件
kubectl apply -f stock.yaml

4）查看 pod 状态
kubectl get pods -n ms  | grep stock

看到如下 running 说明 pod运行正常：
stock -984756d8d -ss8tq      1/1     Running   0          26s

上面都部署成功之后，在浏览器访问 eureka. ctnrs .com 可看到 gateway 、portal 、product 、order 、
stock 等服务都已经注册到 eureka 了，在浏览器访问 portal. ctnrs .com 登陆前端页面，可看到如下内
容：

责。

选择手机，点击购买，然后再点击查询订单服务，出现如下：

责。
 微服务的扩容和缩容
1.扩容
修改 yaml 文件里的 replicas 数量， 如原来是 2，可以修改成 3，然后通过 kubectl  apply  重新更新 yaml
即可

2.缩容
修改 yaml 文件里的 replicas 数量， 如原来是 3，可以修改成 2，然后通过 kubectl  apply  重新更新 yaml
即可

3.发布流程
开发提交代码到 gitlab ->触发自动构建（通过 mvn 打包代码） ->把代码打包成镜像 ->把镜像上传到私有
镜像仓库 >把新的镜像更新到对应服务的 yaml文件里 ->然后 kubectl  apply 更新 yaml 文件->发布服务


