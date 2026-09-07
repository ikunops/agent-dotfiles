本章所讲内容：
kubeadm 初始化k8s1.23高可用集群-使用Containerd 作为容器运行时

具体内容：

**1、kubeadm 和二进制安装 k8s区别**
**2、初始化安装 k8s的实验环境**
**3、安装containerd 服务**
**4、kubeadm 指定containerd 初始化K8s集群**
**5、配置kube-proxy使用ipvs**
**6、扩容k8s集群-添加work节点**
**7、安装网络插件 calico**
**8、测试k8s创建pod网络是否正常**
**9、测试k8s部署tomcat服务**
**10、测试k8s集群内部 dns解析是否正常**
**11、安装使用 k8s可视化ui界面dashboard**
**12、安装和配置 metrics-server**
**13、测试kubectl top获取pod和node节点资源指标**

podSubnet （pod网段） 10.244.0.0/16
serviceSubnet （service 网段）: 10.96.0.0/16

实验环境规划：
操作系统： centos7.6
配置： 4Gib内存/6vCPU/100G硬盘
网络：NAT
开启虚拟机的虚拟化：

准备两台虚拟机

kubeadm 和二进制安装 k8s适用场景分析
kubeadm 是官方提供的开源工具，是一个开源项目，用于快速搭建 kubernetes 集群，目前是比较
方便和推荐使用的。 kubeadm init 以及 kubeadm join 这两个命令可以快速创建  kubernetes 集群。
Kubeadm 初始化k8s，所有的组件都是以 pod形式运行的，具备故障自恢复能力。

Kubeadm安装的k8s默认etcd是没有高可用， kubeadm 安装一个两个 master一个node高可用集
群，etcd是跑在master节点，但是 etcd虽然在每个 master节点都有，没有做高可用，需要我们自己手

 动更改etcd配置文件，对 etcd做成高可用
证书默认有效期是 1年，需要自己手动把证书延长

kubeadm 是工具，可以快速搭建集群，也就是相当于用程序脚本帮我们装好了集群，属于自动部
署，简化部署操作， 证书、组件资源清单文件都是自动创建的， 自动部署屏蔽了很多细节，使得对各个模
块感知很少，如果对 k8s架构组件理解不深的话 ，遇到问题比较难排查。
kubeadm 适合需要经常部署 k8s，或者对自动化要求比较高的场景下使用。

二进制：在官网下载相关组件的二进制包，如果手动安装，对 kubernetes 理解也会更全面。
Kubeadm 和二进制都适合生产环境，在生产环境运行都很稳定，具体如何选择，可以根据实际项目
进行评估。

**1、初始化安装k8s集群的实验环境**
**1.1 修改机器 IP，变成静态 IP**
vim /etc/sysconfig/network -scripts/ifcfg -ens33文件

```bash
TYPE=Ethernet
PROXY_METHOD=none
BROWSER_ONLY=no
BOOTPROTO=static
IPADDR=192.168.40.180
NETMASK=255.255.255.0
GATEWAY=192.168. 40.2
DNS1=192.168. 40.2
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

#修改配置文件之后需要重启网络服务才能使配置生效，重启网络服务命令如下：
service network restart
```

> **注：/etc/sysconfig/network -scripts/ifcfg -ens33文件里的配置说明：**

```bash
NAME=ens33    #网卡名字，跟 DEVICE名字保持一致即可
DEVICE=ens33   #网卡设备名，大家 ip addr可看到自己的这个网卡设备名，每个人的机器可能这个名
```
字不一样，需要写自己的

```bash
BOOTPROTO=static   #static 表示静态 ip地址

 ONBOOT=yes    #开机自启动网络，必须是 yes
IPADDR=192.168.40.180    #ip地址，需要跟自己电脑所在网段一致
NETMASK=255.255.255.0  #子网掩码，需要跟自己电脑所在网段一致
GATEWAY=192.168. 40.2   #网关，在自己电脑打开 cmd，输入ipconfig /all 可看到
DNS1=192.168. 40.2    #DNS，在自己电脑打开 cmd，输入ipconfig /all 可看到
```

**1.2 配置机器主机名**
在192.168.40.180 上执行如下：
hostnamectl set -hostname  xianchaomaster1  && bash
在192.168.40.18 1上执行如下：
hostnamectl set -hostname xianchaonode1  && bash

**1.3 配置主机hosts文件，相互之间通过主机名 互相访问**
修改每台机器的 /etc/hosts 文件，增加如下 三行：
**192.168.40.180 xianchaomaster1**
**192.168.40.181 xianchaonode1**

**1.4 配置主机之间无密码登录**

```bash
[root@xianchaomaster1  ~]# ssh-keygen  # 一路回车，不输入密码
```
把本地生成的密钥文件和私钥文件拷贝到远程主机

```bash
[root@xianchaomaster1  ~]# ssh-copy-id xianchaomaster1

[root@xianchaomaster1  ~]# ssh-copy-id xianchaonode1
[root@ xianchaonode1 ~]# ssh -keygen  # 一路回车，不输入密码
```
把本地生成的密钥文件和私钥文件拷贝到远程主机

```bash
[root@ xianchaonode1  ~]# ssh-copy-id xianchaomaster1

[root@xianchaonode1  ~]# ssh-copy-id xianchaonode1
```

**1.5 关闭交换分区 swap，提升性能**

```bash
#临时关闭
[root@xianchaomaster1 ~]# swapoff -a
[root@xianchaonode1  ~]#  swapoff -a
#永久关闭：注释 swap挂载，给 swap这行开头加一下注释
[root@xianchaomaster1 ~]# vim /etc/fstab
#/dev/mapper/centos -swap swap      swap    defaults        0 0
[root@ xianchaonode1 ~]# vim /etc/fstab
#/dev/mapper/centos -swap swap      swap    defaults        0 0
```

问题1：为什么要关闭 swap交换分区？

 Swap是交换分区，如果机器内存不够，会使用 swap分区，但是 swap分区的性能较低， k8s设计的
时候为了能提升性能，默认是不允许使用 交换分区的。 Kubeadm初始化的时候会检测 swap是否关
闭，如果没关闭，那就初始化失败。 如果不想要关闭交换分区，安装 k8s的时候可以指定 --ignore-
preflight -errors=Swap 来解决。

**1.6 修改机器内核参数**

```bash
[root@xianchaomaster1 ~]# modprobe br_netfilter
[root@xianchaomaster1 ~]# cat > /etc/sysctl.d/k8s.conf <<EOF
net.bridge.bridge -nf-call-ip6tables = 1
net.bridge.bridge -nf-call-iptables = 1
net.ipv4.ip_forward = 1
EOF
[root@xianchaomaster1  ~]# sysctl -p /etc/sysctl.d/k8s.conf

[root@xianchaonode1  ~]# modp robe br_netfilter
[root@xianchaonode1  ~]# cat > /etc/sysctl.d/k8s.conf <<EOF
net.bridge.bridge -nf-call-ip6tables = 1
net.bridge.bridge -nf-call-iptables = 1
net.ipv4.ip_forward = 1
EOF
[root@xianchaonode1 ~]# sysctl -p /etc/sysctl.d/k8s.conf
```

问题1：sysctl是做什么的？
在运行时配置内核参数
  -p   从指定的文件加载系统参数，如不指定即从 /etc/sysctl.conf 中加载

问题2：为什么要执行 modprobe br_netfilter ？
修改/etc/sysctl.d/k8s.conf 文件，增加如下三行参数：
net.bridge.bridge -nf-call-ip6tables = 1
net.bridge.bridge -nf-call-iptables = 1
net.ipv4.ip_forward = 1

sysctl -p /etc/sysctl.d/k8s.conf 出现报错：

sysctl: cannot stat /proc/sys/net/bridge/bridge -nf-call-ip6tables: No such file or
directory
sysctl: cannot stat /proc/sys/net/bridge/bridge -nf-call-iptables: No such file or
directory

解决方法：
modprobe br_netfilter

 问题3：为什么开启 net.bridge.bridge -nf-call-iptables 内核参数？
在centos下安装docker，执行docker info 出现如下警告 ：
WARNING: bridge -nf-call-iptables is disabled
WARNING: bridge -nf-call-ip6tables is disabled

解决办法：
vim  /etc/sysctl.d/k8s.conf
net.bridge.bridge -nf-call-ip6tables = 1
net.bridge.brid ge-nf-call-iptables = 1

问题4：为什么要开启 net.ipv4.ip_forward = 1 参数？
kubeadm 初始化k8s如果报错：

就表示没有开启 ip_forward ，需要开启。

net.ipv4.ip_forward 是数据包转发：
出于安全考虑， Linux系统默认是禁止数据包转发的。所谓转发即当主机拥有多于一块的网卡时，
其中一块收到数据包，根据数据包的目的 ip地址将数据包发往本机另一块网卡，该网卡根据路由表继
续发送数据包。这通常是路由器所要实现的功能。
要让Linux系统具有路由转发功能，需要配置一个 Linux的内核参数 net.ipv4.ip_forward 。这个
参数指定了 Linux系统当前对路由转发功能的支持情况；其值为 0时表示禁止进行 IP转发；如果是 1,
则说明IP转发功能已经打开。

**1.7 关闭firewalld 防火墙**

```bash
[root@xianchaomaster1  ~]# systemctl stop firewalld ; systemctl disable firewalld
[root@xianchaonode1  ~]# systemctl stop firewalld ; systemctl disable firewalld
```

**1.8 关闭selinux**

```bash
[root@xianchaomaster1  ~]# sed -i 's/SELINUX=enforcing/SELINUX=disabled/g'
/etc/selinux/config
#修改selinux 配置文件之后，重启机器， selinux 配置才能永久生效
[root@xianchao node1 ~]# sed -i 's/SELINUX=enforcing/SELINUX=disabled/g'
/etc/selinux/config
#修改selinux 配置文件之后，重启机器， selinux 配置才能永久生效
[root@xianchaomaster1  ~]#getenforce
Disabled
#显示Disabled 说明selinux 已经关闭
[root@xianchao node1 ~]#getenforce
Disabled
#显示Disabled 说明selinux 已经关闭
```

**1.9 配置阿里云 的repo源**

```bash
#配置国内 安装docker和containerd 的阿里云的 repo源
[root@xianchaomaster1 ~]# yum-config-manager --add-repo
http://mirrors.aliyun.com/docker -ce/linux/centos/docker -ce.repo
[root@xianchaonode1 ~]# yum-config-manager --add-repo http://mirrors.aliyun.com/docker -
ce/linux/centos/docker -ce.repo
```

**1.10 配置安装k8s组件需要的 阿里云的 repo源**

```bash
[root@xianchaomaster1 ~]# vim  /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes -el7-x86_64/
enabled=1
gpgcheck=0

#将xianchaomaster1 上Kubernetes 的repo源复制给 xianchaonode1 和xianchaonode 2
[root@xianchaomaster1 ~]# scp /etc/yum.repos.d/kubernetes.repo
xianchaonode1 :/etc/yum.repo s.d/
```

**1.11 配置时间同步**
在xianchaomaster 1上执行如下：

```bash
#安装ntpdate 命令
[root@xianchaomaster1 ~]#  yum install ntpdate -y
#跟网络时间做同步
[root@xianchaomaster1 ~]# ntpdate cn.pool.ntp.org
#把时间同步做成计划任务
[root@xianchaomaster1 ~]# crontab -e
* */1 * * * /usr/sbin/ntpdate   cn.pool.ntp.org
#重启crond服务
[root@xianchaomaster1 ~]# service crond restart
```

在xianchao node1上执行如下：

```bash
#安装ntpdate 命令
[root@ xianchaonode1  ~]# yum install ntpdate -y
#跟网络时间做同步
[root@ xianchaonode1  ~]#ntpdate cn.pool.ntp.org
#把时间同步做成计划任务
[root@ xianchaonode1  ~]#crontab -e
* */1 * * * /usr/sbin/ntpdate   cn.pool.ntp.o rg
#重启crond服务
[root@ xianchaonode1  ~]#service crond restart
```

**1.12 开启ipvs**

安装 k8s: 没有在内核加载 ipvs 模块，会自动适用 iptables 做代理，如果开启了 ipvs，那会使用
ipvs 做规则

```bash
#把ipvs.modules 上传到xianchaomaster1 机器的/etc/sysconfig/modules/ 目录下
[root@xianchaomaster1]# chmod 755 /etc/sysconfig/modules/ipvs.modules && bash
/etc/sysconfig/modules/ipvs.modules && lsmod | grep ip_vs
ip_vs_ftp              13079  0
nf_nat                 26583  1 ip_vs_ftp
ip_vs_sed              12519  0
ip_vs_nq               12516  0
ip_vs_sh               12688  0
ip_vs_dh               12688  0

#把ipvs.modules 拷贝到xianchaonode 1的/etc/sysconfig/module s/目录下
[root@xianchaomaster1 ~]# scp /etc/sysconfig/modules/ipvs.modules
xianchao node1:/etc/sysconfig/modules/

[root@xianchaonode1]# chmod 755 /etc/sysconfig/modules/ipvs.modules && bash
/etc/sysconfig/modules/ipvs.modules && lsmod | grep ip_vs
ip_vs_ftp              13079  0
nf_nat                 26583  1 ip_vs_ftp
ip_vs_sed              12519  0
ip_vs_nq               12516  0
ip_vs_sh               12688  0
ip_vs_dh               12688  0
```

问题1：ipvs是什么？
ipvs (IP Virtual Server) 实现了传输层负载均衡，也就是我们常说的 4层LAN交换，作为  Linux
内核的一部分。 ipvs运行在主机上，在真实服务器集群前充当负载均衡器。 ipvs可以将基于 TCP和UDP
的服务请求转发到真实服务器上，并使真实服务器的服务在单个  IP 地址上显示为虚拟服务。

问题2：ipvs和iptable 对比分析
kube-proxy支持 iptables 和 ipvs 两种模式，  在kubernetes v1.8 中引入了  ipvs 模式，在
v1.9 中处于 beta 阶段，在  v1.11 中已经正式可用了。 iptables 模式在 v1.1 中就添加支持了，从
v1.2 版本开始  iptables 就是 kube-proxy 默认的操作模式， ipvs 和 iptables 都是基于 netfilter
的，但是 ipvs采用的是hash表，因此当 service 数量达到一定规模时， hash查表的速度优势就会显现
出来，从而提高 service 的服务性能。那么  ipvs 模式和 iptables 模式之间有哪些差异呢？

**1、ipvs 为大型集群提供了更好的可扩展性和性能**
**2、ipvs 支持比 iptables 更复杂的复制均衡 算法（最小负载、最少连接、加权等等）**
**3、ipvs 支持服务器健康检查和连接重试等功能**

**1.13 安装基础软件包**

```bash
[root@xianchaomaster1 ~]# yum install -y yum-utils device -mapper-persistent -data lvm2
wget net -tools nfs -utils lrzsz gcc gcc -c++ make cmake libxml2 -devel openssl -devel curl
curl-devel unzip sudo ntp  libaio-devel wget vim ncurses -devel autoconf automake zlib -
devel  python-devel epel -release openssh -server socat   ipvsadm conntrack ntpdate  telnet
ipvsadm

[root@xianchaonode1 ~]# yum install -y yum-utils device -mapper-persistent -data lvm2
wget net -tools nfs -utils lrzsz gcc gcc -c++ make cmake libxml2 -devel openssl -devel curl
curl-devel unzip sudo ntp  libaio-devel wget vim ncurses -devel autoconf automake zlib -
devel  python-devel epel -release openssh -server socat   ipvsadm conntrack ntpdate  telnet
ipvsadm
```

总结：
改了ip地址
Selinux
配置主机名
配置hosts文件
配置主机之间无密码登录
Swap交换分区
Firewalld
安装containerd 的yum源
安装k8s命令行工具 yum源
时间同步
开启ipvs
安装基础包

**2、安装containerd 服务**
**2.1 安装 containerd**

```bash
[root@xianchaomaster1]# yum install containerd -y
[root@xianchaomaster1]# systemctl start containerd && systemctl enable containerd

[root@xianchaonode1 ~]#  yum install containerd -y
[root@xianchaomaster1 modules]# systemctl start containerd && systemctl enable
containerd
```

**2.2 创建Containerd 配置文件**

```bash
[root@xianchaomaster1]#   mkdir -p /etc/containerd

 [root@xianchaomaster1]#  containerd config default > /etc/containerd/config.toml
#替换配置文件
[root@xianchaomaster1]#  sed -i "s#k8s.gcr.io#registry. cn-
hangzhou.aliyuncs.com/google_containers#g"  /etc/containerd/config.toml
[root@xianchaomaster1]#  sed -i '/containerd.runtimes.runc.options/a \ \ \ \ \ \ \ \ \ \ \ \
SystemdCgroup = true' /etc/containerd/config.toml
[root@xianchaomaster1]#  sed -i "s#https: //registry -1.docker.io#https://registry.cn -
hangzhou.aliyuncs.com#g"  /etc/containerd/config.toml
[root@xianchaomaster1 ~]# systemctl restart containerd

[root@xianchao node1]#  mkdir -p /etc/containerd
[root@xianchao node1]# containerd config default > /etc/containerd/config.toml
# 替换配置文件
[root@xianchao node1]# sed -i "s#k8s.gcr.io#registry.cn -
hangzhou.aliyuncs.com/google_containers#g"  /etc/containerd/config.toml
[root@xianchao node1]# sed -i '/containerd.runtimes.runc.options/a \ \ \ \ \ \ \ \ \ \ \ \
SystemdCgroup = true' /etc/containerd/config.toml
[root@xianchao node1]# sed -i "s#https://registry -1.docker.io#https://registry.cn -
hangzhou.aliyuncs.com#g"  /etc/containerd/config.toml
[root@xianchaonode1  ~]# systemctl restart containerd
```

**3、安装初始化 k8s需要的软件包**

```bash
[root@xianchaomaster1  ~]# yum install -y kubelet -1.23.3 kubeadm-1.23.3 kubectl-1.23.3
[root@xianchaomaster1  ~]# systemctl enable kubelet
[root@xianchaomaster1]# systemctl status kubelet

#上面可以看到 kubelet 状态不是 running 状态，这个是正常的，不用管，等 k8s组件起来这个
```
kubelet 就正常了。

```bash
[root@xianchaonode1  ~]# yum install -y kubelet -1.23.3 kubeadm-1.23.3 kubectl-1.23.3
[root@xianchaonode1  ~]# systemctl enable kubelet
```

> **注：每个软件包的作用**
Kubeadm:  kubeadm 是一个工具，用来初始化 k8s集群的
kubelet:   安装在集群所有节点上，用于启动 Pod的
kubectl:   通过kubectl 可以部署和管理应用，查看各种资源，创建、删除和更新各种组件

**5、kubeadm初始化k8s集群**

```bash
#设置容器运行时
[root@xianchaomaster1 ~]#  crictl config runtime -endpoint
/run/containerd/containerd.sock
[root@xianchaonode1 ~]# crictl config runtime-endpoint /run/containerd/containerd.sock

#使用kubeadm 初始化k8s集群
[root@xianchaomaster1 ~]#  kubeadm config print init -defaults > kubeadm.yaml
```

根据我们自己的需求修改配置，比如修改  imageRepository 的值，kube-proxy 的模式为  ipvs，需
要注意的是由于我们使用的 containerd 作为运行时，所以在初始化节点的时候需要指定 cgroupDriver
为systemd

kubeadm.yaml 配置如下：

```yaml
apiVersion: kubeadm.k8s.io/v1beta3
bootstrapTokens:
- groups:
  - system:bootstrappers:kubeadm:default -node-token
  token: abcdef.0123456789abcdef
  ttl: 24h0m0s
  usages:
  - signing
  - authentication
kind: InitConfiguration
localAPIEndpoint:
  advertiseAddress: 192.168.40.180  #控制节点的 ip
  bindPort: 6443
nodeRegistration:
  criSocket: /run/containerd/containerd.sock   #用containerd 作为容器运行时
  imagePullPolicy: IfNotPresent
  name: xianchaomaster1   #控制节点主机名
  taints: null
---
apiServer:
  timeoutForControlPlane: 4m0s
apiVersion: kubeadm.k8s.io/v1beta3
certificatesDir: /etc/kubernetes/pki
clusterName: kubernetes
controllerManager: {}
dns: {}
etcd:

   local:
    dataDir: /var/lib/etcd
imageRepository: registry.cn -hangzhou.aliyuncs.com/google_containers
# 指定阿里云镜像仓库地址
kind: ClusterConfiguration
kubernetesVersion: 1.23.3  #k8s版本
networking:
  dnsDomain: cluster.local
  podSubnet: 10.244.0.0/16  #指定pod网段
  serviceSubnet: 10.96.0.0/1 6 #指定Service 网段
scheduler: {}
---
apiVersion: kubeproxy.config.k8s.io/v1alpha1
kind: KubeProxyConfiguration
mode: ipvs
---
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
cgroupDriver: systemd

#基于kubeadm.yaml初始化k8s集群
```

```bash
[root@xianchaomaster1 ~]# kubeadm init --config=kubeadm.yaml
```

显示如下，说明安装完成 ：

#配置kubectl 的配置文件 config，相当于对 kubectl 进行授权， 这样kubectl 命令可以使用这个证
书对k8s集群进行管理

```bash
[root@xianchaomaster1  ~]# mkdir -p $HOME/.kube
[root@xianchaomaster1  ~]# sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
[root@xianchaomaster1  ~]# sudo chown $(id -u):$(id -g) $HOME/.kube/config

[root@xianchaomaster1 ~]# kubectl get nodes

 NAME              STATUS     ROLES                  AGE     VERSION
xianchaomaster1   NotReady   control -plane,master   2m25s   v1.23.3
```

此时集群状态还是 NotReady 状态，因为 没有安装网络 插件。
**6、扩容k8s集群-添加第一个工作 节点**
在xianchaomaster1 上查看加入节点的命令：

```bash
[root@xianchaomaster1 ~]# kubeadm token create --print-join-command
```

显示如下：
kubeadm join 192.168.40.180:6443 --token vulvta.9ns7da3saibv4pg1     --discovery -token-
ca-cert-hash sha256:72a0896e27521244850b8f1c3b600087292c2d10f2565adb56381f1f4ba7057a

把xianchaonode1 加入k8s集群：

```bash
[root@xianchaonode1 ~]# kubeadm join 192.168.40.180:6443 --token vulvta.9n s7da3saibv4pg1
--discovery -token-ca-cert-hash
sha256:72a0896e27521244850b8f1c3b600087292c2d10f2565adb56381f1f4ba7057a

#看到上面说明 xianchaonode1 节点已经加入到集群了 ,充当工作节点

#在xianchaomaster1 上查看集群节点状况 ：
[root@xianchaomaster1 ~]# kubectl get nodes
NAME              STATUS     ROLES                  AGE     VERSION
xianchaomaster1   NotReady   control -plane,master   3m11s   v1.23.3
xianchaonode1     NotReady   <none>                 8s      v1.23.3

#可以对xianchaonode 1打个标签，显示 work
[root@xianchaomaster1 ~]# kubectl label nodes xianchaonode1 node -
role.kubernetes.io/work=work

[root@xianchaomaster1 ~]# kubectl get nodes
NAME              STATUS     ROLES                  AGE     VERSION
xianchaomaster1   NotReady   control -plane,master    27m     v1.23.3
xianchaonode1     NotReady   work                   5m47s   v1.23.3
```

**8、安装kubernetes 网络组件 -Calico**
把安装calico需要的镜像 calico.tar.gz 传到xianchao master1 和xianchao node1节点，手动解
压：

```bash
 [root@xianchaonode1 ~]# ctr images import calico.tar.gz
[root@xianchao master1 ~]# ctr images import calico.tar.gz
```
上传calico.yaml 到xianchaomaster1 上，使用yaml文件安装 calico 网络插件  。

```bash
[root@xianchaomaster1  ~]# kubectl apply -f  calico.yaml
```

> **注：在线下载配置文件地址是：  https://docs.projectcalico.org/manifests/calico.yaml**
。

```bash
[root@xianchaomaster1 ~]# kubectl get pod -n kube-system
```

再次查看集群状态。

```bash
[root@xianchaomaster1 ~]# kubectl get nodes
NAME              STATUS   ROLES                  AGE     VERSION
xianchaomaster1   Re ady    control -plane,master   58m     v1.2 3.3
xianchaonode1     Ready    <none>                 5m46s   v1.2 3.3

[root@xianchaomaster1 ~]# kubectl get pods -n kube-system
NAME                                       READY   STATUS    RESTARTS   AGE
calico-kube-controllers -677cd97c8d -fmhct   1/1     Running   0          59s
calico-node-jt475                          1/1     Running   0          59s
calico-node-q4zfw                          1/1     Running   0          59s
coredns-65c54cc984 -sd68l                   1/1     Running   0          11m
coredns-65c54cc984 -srxfv                   1/1     Running   0          11m
etcd-xianchaomaster1                       1/1     Running   0          11m
kube-apiserver -xianchaomaster1             1/1     Runni ng   0          11m
kube-controller -manager-xianchaomaster1    1/1     Running   0          11m
kube-proxy-bhxbh                           1/1     Running   0          11m
kube-proxy-twj5w                           1/1     Running   0          8m29s
kube-scheduler -xianchaomaster1             1/1     Running   0          11m

#calico的STATUS状态是Ready，说明k8s集群正常运行了
```

**9、测试在k8s创建pod是否可以正常访问网络**

```bash
#把busybox-1-28.tar.gz 上传到xianchaonode1 节点，手动解压
[root@xianchaonode1  ~]# ctr images import  busybox-1-28.tar.gz
[root@xianchaomaster1  ~]# kubectl run busybox --image busybox:1.28 --restart=Never --rm
-it busybox -- sh
/ # ping www.baidu.com
PING www.baidu.com (39.156.66.18): 56 data bytes
64 bytes from 39.156.66.18: seq=0 ttl=127 time=39.3 ms
#通过上面可以看到能访问网络 ，说明calico网络插件已经被正常安装了
/ # exit   # 退出Pod
```

**10、测试coredns 是否正常**

```bash
[root@xianchaomaster1  ~]# kubectl run busybox --image busybox:1.28 --restart=Never --rm
-it busybox -- sh
/ # nslookup kubernetes.default.svc.cluster.local
Server:    10.96.0.10
Address 1: 10.96.0.10 kube -dns.kube -system.svc.cluster.local

Name:      kubernetes.default.svc.cluster.local
Address 1: 10.96.0.1 kubernetes.default.svc.cluster.local
```

**10.96.0.10 就是我们 coreDNS 的clusterIP ，说明coreDNS 配置好了。**
解析内部 Service 的名称，是通过 coreDNS 去解析的。

#注意：
busybox要用指定的 1.28版本，不能用最新版本，最新版本， nslookup 会解析不到 dns和ip

**11、测试k8s集群中部署 tomcat服务**

```bash
#把tomcat.tar.gz 上传到xianchaonode1 ，手动解压
[root@xianchaonode1 ~]# ctr images import tomcat.tar.gz
[root@xianchaomaster1 ~]# kubectl apply -f tomcat.yaml
[root@xianchaomaster1 ~]#  kubectl get pods
NAME       READY   STATUS    RESTARTS   AGE
demo-pod   1/1     Running   0          10s

[root@xianchaomaster1 ~]# kubectl apply -f tomcat -service.yaml
[root@xianchaomaster1 ~]# kubectl get svc
NAME         TYPE        CLUSTER -IP       EXTERNAL -IP   PORT(S )          AGE
kubernetes   ClusterIP   10.255.0.1       <none>        443/TCP          158m
tomcat       NodePort    10.255.227.179   <none>        8080:30080/TCP   19m
```

在浏览器访问 xianchaonode1 节点的ip:30080 即可请求到浏览器

**12、安装k8s可视化UI界面dashboard**

**12.1 安装dasboard**
把安装kubernetes -dashboard 需要的镜像上传到工作节点 xianchaonode1 和xianchaonode2 ，手动
解压：

```bash
[root@xianchaonode1  ~]# ctr images import  dashboard_2_0_0.tar.gz
[root@xianchaonode1  ~]# ctr images import   metrics-scrapter -1-0-1.tar.gz

#安装dashboard 组件
```
在xianchao master1节点操作如下命令 :

```bash
[root@xianchao master1 ~]# kubectl apply -f kubernetes -dashboard.yaml

#查看dashboard 的状态
[root@xianchao master1 ~]# kubectl get pods -n kubernetes -dashboard
```
显示如下，说明 dashboard 安装成功了
NAME                                         READY   STATUS    RESTARTS   AGE
dashboard -metrics-scraper-7445d59dfd -n5krt   1/1     Running   0          66s
kubernetes -dashboard -54f5b6dc4b -mhd2c        1/1     Running   0          66s

```bash
#查看dashboard 前端的service
[root@xianchaomaster1 ~]#  kubectl get svc -n kubernetes-dashboard
```
显示如下：

 NAME                        TYPE        CLUSTER -IP     EXTERNAL -IP   PORT(S)    AGE
dashboard -metrics-scraper   ClusterIP   10.98.221.57   <none>        8000/TCP
kubernetes -dashboard        ClusterIP   10.97.37.171   <none>        443/TCP

```bash
#修改service type 类型变成 NodePort
[root@xianchaomaster1 ~]# kubectl edit svc kubernetes -dashboard -n kubernetes -dashboard
```
把type: ClusterIP 变成 type: NodePort ，保存退出即可。

```bash
[root@xianchaomaster1 ~]# kubectl get svc -n kubernetes -dashboard
NAME                        TYPE        CLUSTER -IP     EXTERNAL -IP   PORT(S)
AGE
dashboard -metrics-scraper   ClusterIP   10.98.221.57   <none>        8000/TCP
kubernetes -dashboard        NodePort    10.97.37.171   <none >        443:32728/TCP
2m50s
```

上面可看到 service 类型是NodePort ，访问任何一个 工作节点 ip: 32728端口即可访问 kubernetes
dashboard ，在浏览器 (使用火狐浏览器 )访问如下地址 :
https://192.168. 40.180:32728/

可看到出现了 dashboard 界面

**12.2 通过token令牌访问dashboard**
#通过Token登陆dashboard
创建管理员 token，具有查看任何空间的权限，可以管理所有资源对象

```bash
[root@xianchaomaster1 ~]#  kubectl create clusterrolebinding dashboard -cluster-admin --
clusterrole=cluster -admin --serviceaccount=kubernetes -dashboard:kubernetes -dashboard
```
查看kubernetes -dashboard 名称空间下的 secret

```bash
[root@xianchaomaster1 ~]# kubectl get secret -n kubernetes -dashboard
NAME                               TYPE                                  DATA   AGE
default-token-n2x5n                kubernetes.io/service -account-token   3
kubernetes -dashboard -certs         Opaque                                0
kubernetes -dashboard -csrf          Opaque                                1
kubernetes -dashboard -key-holder    Opaque                                2
kubernetes -dashboard -token-ppc8c   kubernetes.io/service -account-token   3
```

找到对应的带有 token的kubernetes -dashboard -token-ppc8c

```bash
[root@xianchaomaster1 ~]# kubectl  describe  secret kubernetes -dashboard -token-ppc8c -n
kubernetes -dashboard

#显示如下：
---
token:
eyJhbGciOiJSUzI1NiIsImtpZCI6IlVNalJOeHBacEYxZ0tieTJKR2ZVY1hvTHZvcVVBU3FPaTU4TGhreDd5VzQifQ.
eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1
lc3BhY2UiOiJrdWJlcm5ldGVzLWRhc2hib2FyZCIsImt1YmVybmV0ZXMuaW8vc2Vydm ljZWFjY291bnQvc2VjcmV0Lm
5hbWUiOiJrdWJlcm5ldGVzLWRhc2hib2FyZC10b2tlbi1wcGM4YyIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291b
nQvc2VydmljZS1hY2NvdW50Lm5hbWUiOiJrdWJlcm5ldGVzLWRhc2hib2FyZCIsImt1YmVybmV0ZXMuaW8vc2Vydmlj
ZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImU0NTZlNT gzLWE1MDItNDViNy04YTEwLTE0MThhZmJiZmRlZCI
sInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDprdWJlcm5ldGVzLWRhc2hib2FyZDprdWJlcm5ldGVzLWRhc2hib2
FyZCJ9.CKSwwXQfwF -HA_giAC1jzTmEnMjA73FtNpMjhI_coLOakc -MBX8f74K4k -

 TGMfBVFwqcvzBnCBOQJ2OJCgZX -
YI109d4PDE9rGO3SK0OGIaLVDafB_9ao MeuMyrsut0PwgZoynUwA_DrwhOFkneNsA93rCIQck1WWOvxbrUtttmhvMDz
YSZu6-TcGx6pxEiHwOEQ5dx92Tv6nSIBS_tjHU -CElQMhcHcHsD6AF -
WdhSF2QtnvcCGasCcBPXzKF8cqd_QdvZvMgcUuwhUBVRRCEc_MCHDqGQBXZ6EzRE0PoXW_S6Rd1zvzT5SVFrgL3xGik
PHTxWP2DurNZuCHmFnMw
```

记住token后面的值，把下面的 token值复制到浏览器 token登陆处即可登陆：
eyJhbGciOiJSUzI1NiIsImtpZCI6IlVNalJOeHBacEYxZ0tieTJKR2ZVY1hvTHZvcVVBU3FPaTU4TGhreDd5VzQ
ifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9
uYW1lc3BhY2UiOiJrdWJlcm5ldGVzLWRhc2hib2FyZCIsImt1YmVybmV0ZXMuaW8v c2VydmljZWFjY291bnQvc2Vjcm
V0Lm5hbWUiOiJrdWJlcm5ldGVzLWRhc2hib2FyZC10b2tlbi1wcGM4YyIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY
291bnQvc2VydmljZS1hY2NvdW50Lm5hbWUiOiJrdWJlcm5ldGVzLWRhc2hib2FyZCIsImt1YmVybmV0ZXMuaW8vc2Vy
dmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImU0 NTZlNTgzLWE1MDItNDViNy04YTEwLTE0MThhZmJiZmR
lZCIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDprdWJlcm5ldGVzLWRhc2hib2FyZDprdWJlcm5ldGVzLWRhc2
hib2FyZCJ9.CKSwwXQfwF -HA_giAC1jzTmEnMjA73FtNpMjhI_coLOakc -MBX8f74K4k -
TGMfBVFwqcvzBnCBOQJ2OJCgZX -
YI109d4PDE9rGO3SK0OGIaLVDa fB_9aoMeuMyrsut0PwgZoynUwA_DrwhOFkneNsA93rCIQck1WWOvxbrUtttmhvMDz
YSZu6-TcGx6pxEiHwOEQ5dx92Tv6nSIBS_tjHU -CElQMhcHcHsD6AF -
WdhSF2QtnvcCGasCcBPXzKF8cqd_QdvZvMgcUuwhUBVRRCEc_MCHDqGQBXZ6EzRE0PoXW_S6Rd1zvzT5SVFrgL3xGik
PHTxWP2DurNZuCHmFnMw

**12.3 通过kubeconfig 文件访问 dashboard**

```bash
[root@xianchaomaster1 ~]# cd /etc/kubernetes/pki
```
**1、创建cluster 集群**

```bash
[root@xianchaomaster1 pki]# kubectl config set -cluster kubernetes --certificate -
authority=./ca.crt --server="https://192.168.40.180:6443" --embed-certs=true --

 kubeconfig=/root/dashboard -admin.conf
[root@xianchaomaster1 pki]# cat /root/dashboard -admin.conf
```

```yaml
apiVersion: v1
clusters:
- cluster:
    certificate -authority -data:
LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUM1ekNDQWMrZ0F3SUJBZ0lCQURBTkJna3Foa2lHOXcwQkFRc0Z
BREFWTVJNd0VRWURWUVFERXdwcmRXSmwKY201bGRHVnpNQjRYRFRJeE1EVXdNVEEzTURRd01sb1hEVE14TURReU9UQT
NNRFF3TWxvd0ZURVRNQkVHQTFVRQpBeE1LYTNWaVpYSnVaWFJsY3pDQ0FTSXdEUVlKS29aS Wh2Y05BUUVCQlFBRGdnR
VBBRENDQVFvQ2dnRUJBTXRUCktUYUF0RENySXB3VUtPUnhlbTRUYk9WS0JTM3NZaHBOTjE0TjAyUzI4Tnh5Y2oyUjVh
VlF2cTF6aGJZYmVnZloKNm81UHAzMk4ydGEzQW5WMmpmT3h2OTFPR2FYL3NIT2hOZG5GQVpiZXdmZmJWVFhrbURMSnB
IRmtYeUVubnltbQpRaDY2Rkl6S1IxSWZaLzFLaXRjM1dSQlpZSjlMR U53UjBWaFcyeUNRbmdwMEhtQ1hBcllZYTFFNz
dnOHI5Vk5ZCjdrRm9ma2dla1BZWEhFeGxVS3dQVVcxSDd1ejRkVXlGZEorR1VjTE9WOXJhdWszaWMwazg4dG9ZdlNIe
lhjR3AKR0ZNS2FrMkhLYTF5RUkveGZqUFJPMDlRRmdvSTdTTFh4RG0yNHNuNUhFWHhzaTgrNFR2a2ZRVHRnZGNtRDNV
RApWTzJrNHVFV1I0V1Axb0lYQnlzQ0F3RUFBY U5DTUVBd0RnWURWUjBQQVFIL0JBUURBZ0trTUE4R0ExVWRFd0VCCi9
3UUZNQU1CQWY4d0hRWURWUjBPQkJZRUZKTUJTREpZdXpIR1JmVWZQMWxBM0dpbGk5ZXlNQTBHQ1NxR1NJYjMKRFFFQk
N3VUFBNElCQVFBK2REQnZpTk0rcXFnaFJtZUxNQUw2QUdBM1ZZWlByUkZaajI2RUI0R2FvMU01b1JtTgpLcmZQKzhQN
zJtRmkycDRCR2xWTUN2T jhUSy8xZW1DWVc0MkZYS0YzOE5zVUhqVFVmZUlxaHJBSW9WWWVvRDlsCjFOeU42QkVkdWJS
WHhjejByV3pMVkZMYUROMzhCcERzUGJMSk5qOGZmWUd0SzJnQlBNRDdRWWxabHpldnNRYzkKclczVGFHUGk2OVNJc0R
GbGZvbnV1aEFqTzNqZVJ6VURzQmIxblIzRGpRQUFBMnRITDJOQVFXaW8zWlNBd3Q4Rwo4UFRYL20waWdaWjNiaHA3Uj
V5cEFNbWR3ODVEak1BMkhxQ0hFRjlvc1MxUnowQWdaK2VXWkNBZUtmclhKWW1kCkZuUjBYNU9TSlUybjhCRkVUbE8wa
3N4QTVWVjJyUDNJb1NmNAotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg==
    server: https://192.168.40.180:6443
  name: kubernetes
contexts: null
current-context: ""
kind: Config
preferences: {}
users: null

```
**2、创建credentials**
创建credentials 需要使用上面 的kubernetes -dashboard -token-ppc8c对应的token信息

```bash
[root@xianchaomaster1 pki]# DEF_NS_ADMIN_TOKEN=$(kubectl get secret kubernetes -
dashboard -token-ppc8c -n kubernetes -dashboard  -o jsonpath={.data.token}|base64 -d)

[root@xianchaomaster1 pki]# kubectl config set -credentials dashboard -admin --
token=$DEF_NS_ADMIN_TOKEN --kubeconfig=/root/dashboard -admin.conf

[root@xianchaomaster1 pki]# cat /root/dashboard -admin.conf
```

```yaml
apiVersion: v1
clusters:
- cluster:
    certificate -authority -data:
```

 LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUM1ekNDQWMrZ0F3SUJBZ0lCQURBTkJna3Foa2lHOXcwQkFRc0Z
BREFWTVJNd0VRWURWUVFERXdwcmRXSmwKY201bGRHVnpNQjRYRFRJeE1EVXdNVEEzTURRd01sb1hEVE14TURReU9U QT
NNRFF3TWxvd0ZURVRNQkVHQTFVRQpBeE1LYTNWaVpYSnVaWFJsY3pDQ0FTSXdEUVlKS29aSWh2Y05BUUVCQlFBRGdnR
VBBRENDQVFvQ2dnRUJBTXRUCktUYUF0RENySXB3VUtPUnhlbTRUYk9WS0JTM3NZaHBOTjE0TjAyUzI4Tnh5Y2oyUjVh
VlF2cTF6aGJZYmVnZloKNm81UHAzMk4ydGEzQW5WMmpmT3h2OTFPR2FYL3NIT2hOZG5GQVpi ZXdmZmJWVFhrbURMSnB
IRmtYeUVubnltbQpRaDY2Rkl6S1IxSWZaLzFLaXRjM1dSQlpZSjlMRU53UjBWaFcyeUNRbmdwMEhtQ1hBcllZYTFFNz
dnOHI5Vk5ZCjdrRm9ma2dla1BZWEhFeGxVS3dQVVcxSDd1ejRkVXlGZEorR1VjTE9WOXJhdWszaWMwazg4dG9ZdlNIe
lhjR3AKR0ZNS2FrMkhLYTF5RUkveGZqUFJPMDlRRmdvSTdTTFh4RG0y NHNuNUhFWHhzaTgrNFR2a2ZRVHRnZGNtRDNV
RApWTzJrNHVFV1I0V1Axb0lYQnlzQ0F3RUFBYU5DTUVBd0RnWURWUjBQQVFIL0JBUURBZ0trTUE4R0ExVWRFd0VCCi9
3UUZNQU1CQWY4d0hRWURWUjBPQkJZRUZKTUJTREpZdXpIR1JmVWZQMWxBM0dpbGk5ZXlNQTBHQ1NxR1NJYjMKRFFFQk
N3VUFBNElCQVFBK2REQnZpTk0rcXFnaFJtZUxN QUw2QUdBM1ZZWlByUkZaajI2RUI0R2FvMU01b1JtTgpLcmZQKzhQN
zJtRmkycDRCR2xWTUN2TjhUSy8xZW1DWVc0MkZYS0YzOE5zVUhqVFVmZUlxaHJBSW9WWWVvRDlsCjFOeU42QkVkdWJS
WHhjejByV3pMVkZMYUROMzhCcERzUGJMSk5qOGZmWUd0SzJnQlBNRDdRWWxabHpldnNRYzkKclczVGFHUGk2OVNJc0R
GbGZvbnV1aEFqTzNqZVJ6 VURzQmIxblIzRGpRQUFBMnRITDJOQVFXaW8zWlNBd3Q4Rwo4UFRYL20waWdaWjNiaHA3Uj
V5cEFNbWR3ODVEak1BMkhxQ0hFRjlvc1MxUnowQWdaK2VXWkNBZUtmclhKWW1kCkZuUjBYNU9TSlUybjhCRkVUbE8wa
3N4QTVWVjJyUDNJb1NmNAotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg==
    server: https://192.168.40.180: 6443
  name: kubernetes
contexts: null
current-context: ""

```yaml
kind: Config
preferences: {}
users:
- name: dashboard -admin
  user:
    token:
eyJhbGciOiJSUzI1NiIsImtpZCI6IlVNalJOeHBacEYxZ0tieTJKR2ZVY1hvTHZvcVVBU3FPaTU4TGhreDd5VzQifQ.
eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1
lc3BhY2UiOiJrdWJlcm5ldGVzLWRhc2hib2FyZCIsImt1YmVybmV0ZXMuaW8vc2 VydmljZWFjY291bnQvc2VjcmV0Lm
5hbWUiOiJrdWJlcm5ldGVzLWRhc2hib2FyZC10b2tlbi1wcGM4YyIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291b
nQvc2VydmljZS1hY2NvdW50Lm5hbWUiOiJrdWJlcm5ldGVzLWRhc2hib2FyZCIsImt1YmVybmV0ZXMuaW8vc2Vydmlj
ZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImU0NT ZlNTgzLWE1MDItNDViNy04YTEwLTE0MThhZmJiZmRlZCI
sInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDprdWJlcm5ldGVzLWRhc2hib2FyZDprdWJlcm5ldGVzLWRhc2hib2
FyZCJ9.CKSwwXQfwF -HA_giAC1jzTmEnMjA73FtNpMjhI_coLOakc -MBX8f74K4k -
TGMfBVFwqcvzBnCBOQJ2OJCgZX -
YI109d4PDE9rGO3SK0OGIaLVDafB _9aoMeuMyrsut0PwgZoynUwA_DrwhOFkneNsA93rCIQck1WWOvxbrUtttmhvMDz
YSZu6-TcGx6pxEiHwOEQ5dx92Tv6nSIBS_tjHU -CElQMhcHcHsD6AF -
WdhSF2QtnvcCGasCcBPXzKF8cqd_QdvZvMgcUuwhUBVRRCEc_MCHDqGQBXZ6EzRE0PoXW_S6Rd1zvzT5SVFrgL3xGik
PHTxWP2DurNZuCHmFnMw

```
**3、创建context**

```bash
[root@xianchaomaster1 pki]# kubectl config set -context dashboard -admin@kubernetes --
cluster=kubernetes --user=dashboard -admin --kubeconfig=/root/dashboard -admin.conf

[root@xianchaomaster1 pki]# cat /root/dashboard -admin.conf
```

```yaml
apiVersion: v1
clusters:
- cluster:
    certificate -authority -data:
LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUM1ekNDQWMrZ0F3SUJBZ0lCQURBTkJna3Foa2lHOXcwQkFRc0Z
BREFWTVJNd0VRWURWUVFERXdwcmRXSmwKY201bGRHVnpNQjRYRFRJeE1EVXdNVEEzTURRd01sb1hEVE14TURReU9UQT
NNRFF3TWxvd0ZURVRNQkVHQTFVRQpBeE1LY TNWaVpYSnVaWFJsY3pDQ0FTSXdEUVlKS29aSWh2Y05BUUVCQlFBRGdnR
VBBRENDQVFvQ2dnRUJBTXRUCktUYUF0RENySXB3VUtPUnhlbTRUYk9WS0JTM3NZaHBOTjE0TjAyUzI4Tnh5Y2oyUjVh
VlF2cTF6aGJZYmVnZloKNm81UHAzMk4ydGEzQW5WMmpmT3h2OTFPR2FYL3NIT2hOZG5GQVpiZXdmZmJWVFhrbURMSnB
IRmtYeUVubnltbQpRa DY2Rkl6S1IxSWZaLzFLaXRjM1dSQlpZSjlMRU53UjBWaFcyeUNRbmdwMEhtQ1hBcllZYTFFNz
dnOHI5Vk5ZCjdrRm9ma2dla1BZWEhFeGxVS3dQVVcxSDd1ejRkVXlGZEorR1VjTE9WOXJhdWszaWMwazg4dG9ZdlNIe
lhjR3AKR0ZNS2FrMkhLYTF5RUkveGZqUFJPMDlRRmdvSTdTTFh4RG0yNHNuNUhFWHhzaTgrNFR2a2ZRVHRnZGNtRDNV
RApWTzJrNHVFV1I0V1Axb0lYQnlzQ0F3RUFBYU5DTUVBd0RnWURWUjBQQVFIL0JBUURBZ0trTUE4R0ExVWRFd0VCCi9
3UUZNQU1CQWY4d0hRWURWUjBPQkJZRUZKTUJTREpZdXpIR1JmVWZQMWxBM0dpbGk5ZXlNQTBHQ1NxR1NJYjMKRFFFQk
N3VUFBNElCQVFBK2REQnZpTk0rcXFnaFJtZUxNQUw2QUdBM1ZZWlByUkZaajI2RUI0R2FvMU01b 1JtTgpLcmZQKzhQN
zJtRmkycDRCR2xWTUN2TjhUSy8xZW1DWVc0MkZYS0YzOE5zVUhqVFVmZUlxaHJBSW9WWWVvRDlsCjFOeU42QkVkdWJS
WHhjejByV3pMVkZMYUROMzhCcERzUGJMSk5qOGZmWUd0SzJnQlBNRDdRWWxabHpldnNRYzkKclczVGFHUGk2OVNJc0R
GbGZvbnV1aEFqTzNqZVJ6VURzQmIxblIzRGpRQUFBMnRITDJOQVFXaW8zW lNBd3Q4Rwo4UFRYL20waWdaWjNiaHA3Uj
V5cEFNbWR3ODVEak1BMkhxQ0hFRjlvc1MxUnowQWdaK2VXWkNBZUtmclhKWW1kCkZuUjBYNU9TSlUybjhCRkVUbE8wa
3N4QTVWVjJyUDNJb1NmNAotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg==
    server: https://192.168.40.180:6443
  name: kubernetes
contexts:
- context:
    cluster: kubernetes
    user: dashboard -admin
  name: dashboard -admin@kubernetes
current-context: ""
kind: Config
preferences: {}
users:
- name: dashboard -admin
  user:
    token:
eyJhbGciOiJSUzI1NiIsImtpZCI6IlVNalJOeHBacEYxZ0tieTJKR2ZVY1hvTHZv cVVBU3FPaTU4TGhreDd5VzQifQ.
eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1
lc3BhY2UiOiJrdWJlcm5ldGVzLWRhc2hib2FyZCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm
5hbWUiOiJrdWJlcm5ldGVzLWRhc2hib2FyZC10b2tlbi1wc GM4YyIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291b
nQvc2VydmljZS1hY2NvdW50Lm5hbWUiOiJrdWJlcm5ldGVzLWRhc2hib2FyZCIsImt1YmVybmV0ZXMuaW8vc2Vydmlj
ZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImU0NTZlNTgzLWE1MDItNDViNy04YTEwLTE0MThhZmJiZmRlZCI
sInN1YiI6InN5c3RlbTpzZXJ2aWNlY WNjb3VudDprdWJlcm5ldGVzLWRhc2hib2FyZDprdWJlcm5ldGVzLWRhc2hib2
```

 FyZCJ9.CKSwwXQfwF -HA_giAC1jzTmEnMjA73FtNpMjhI_coLOakc -MBX8f74K4k -
TGMfBVFwqcvzBnCBOQJ2OJCgZX -
YI109d4PDE9rGO3SK0OGIaLVDafB_9aoMeuMyrsut0PwgZoynUwA_DrwhOFkneNsA93rCIQck1WWOvxbrUtttmhvMDz
YSZu6-TcGx6pxEiHwOEQ5dx92Tv6nSIBS_tjHU -CElQMhcHcHsD6AF -
WdhSF2QtnvcCGasCcBPXzKF8cqd_QdvZvMgcUuwhUBVRRCEc_MCHDqGQBXZ6EzRE0PoXW_S6Rd1zvzT5SVFrgL3xGik
PHTxWP2DurNZuCHmFnMw

**4、切换context 的current-context 是dashboard -admin@kubernetes**

```bash
[root@xianchaomaster1 pki]# kubectl config use -context dashboard -admin@kubernetes --
kubeconfig=/root/dashboard -admin.conf

[root@xianchaomaster1 pki]# cat /root/dashboard -admin.conf
```

```yaml
apiVersion: v1
clusters:
- cluster:
    certificate -authority -data:
LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUM1ekNDQWMrZ0F3SUJBZ0lCQURBTkJna3Foa2lHOXcwQkFRc0Z
BREFWTVJNd0VRWURWUVFERXdwcmRXSmwKY201bGRHVnpNQjRYRFRJeE1EVXdNVEEzTURRd01sb1hEVE14TURReU9UQT
NNRFF3TWxvd0ZURVRNQkVHQTFVRQpBeE1LYTNWaVpY SnVaWFJsY3pDQ0FTSXdEUVlKS29aSWh2Y05BUUVCQlFBRGdnR
VBBRENDQVFvQ2dnRUJBTXRUCktUYUF0RENySXB3VUtPUnhlbTRUYk9WS0JTM3NZaHBOTjE0TjAyUzI4Tnh5Y2oyUjVh
VlF2cTF6aGJZYmVnZloKNm81UHAzMk4ydGEzQW5WMmpmT3h2OTFPR2FYL3NIT2hOZG5GQVpiZXdmZmJWVFhrbURMSnB
IRmtYeUVubnltbQpRaDY2Rkl6 S1IxSWZaLzFLaXRjM1dSQlpZSjlMRU53UjBWaFcyeUNRbmdwMEhtQ1hBcllZYTFFNz
dnOHI5Vk5ZCjdrRm9ma2dla1BZWEhFeGxVS3dQVVcxSDd1ejRkVXlGZEorR1VjTE9WOXJhdWszaWMwazg4dG9ZdlNIe
lhjR3AKR0ZNS2FrMkhLYTF5RUkveGZqUFJPMDlRRmdvSTdTTFh4RG0yNHNuNUhFWHhzaTgrNFR2a2ZRVHRnZGNtRDNV
RApWTzJr NHVFV1I0V1Axb0lYQnlzQ0F3RUFBYU5DTUVBd0RnWURWUjBQQVFIL0JBUURBZ0trTUE4R0ExVWRFd0VCCi9
3UUZNQU1CQWY4d0hRWURWUjBPQkJZRUZKTUJTREpZdXpIR1JmVWZQMWxBM0dpbGk5ZXlNQTBHQ1NxR1NJYjMKRFFFQk
N3VUFBNElCQVFBK2REQnZpTk0rcXFnaFJtZUxNQUw2QUdBM1ZZWlByUkZaajI2RUI0R2FvMU01b1JtTgpL cmZQKzhQN
zJtRmkycDRCR2xWTUN2TjhUSy8xZW1DWVc0MkZYS0YzOE5zVUhqVFVmZUlxaHJBSW9WWWVvRDlsCjFOeU42QkVkdWJS
WHhjejByV3pMVkZMYUROMzhCcERzUGJMSk5qOGZmWUd0SzJnQlBNRDdRWWxabHpldnNRYzkKclczVGFHUGk2OVNJc0R
GbGZvbnV1aEFqTzNqZVJ6VURzQmIxblIzRGpRQUFBMnRITDJOQVFXaW8zWlNBd3Q4 Rwo4UFRYL20waWdaWjNiaHA3Uj
V5cEFNbWR3ODVEak1BMkhxQ0hFRjlvc1MxUnowQWdaK2VXWkNBZUtmclhKWW1kCkZuUjBYNU9TSlUybjhCRkVUbE8wa
3N4QTVWVjJyUDNJb1NmNAotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg==
    server: https://192.168.40.180:6443
  name: kubernetes
contexts:
- context:
    cluster: kubernetes
    user: dashboard -admin
  name: dashboard -admin@kubernetes
current-context: dashboard -admin@kubernetes
kind: Config
preferences: {}
users:

 - name: dashboard -admin
  user:
    token:
eyJhbGciOiJSUzI1NiIsImtpZCI6IlVNalJOeHBacEYxZ0t ieTJKR2ZVY1hvTHZvcVVBU3FPaTU4TGhreDd5VzQifQ.
eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1
lc3BhY2UiOiJrdWJlcm5ldGVzLWRhc2hib2FyZCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm
5hbWUiOiJrdWJlcm5ldGVzLWRhc2hi b2FyZC10b2tlbi1wcGM4YyIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291b
nQvc2VydmljZS1hY2NvdW50Lm5hbWUiOiJrdWJlcm5ldGVzLWRhc2hib2FyZCIsImt1YmVybmV0ZXMuaW8vc2Vydmlj
ZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImU0NTZlNTgzLWE1MDItNDViNy04YTEwLTE0MThhZmJiZmRlZCI
sInN1YiI6InN5 c3RlbTpzZXJ2aWNlYWNjb3VudDprdWJlcm5ldGVzLWRhc2hib2FyZDprdWJlcm5ldGVzLWRhc2hib2
FyZCJ9.CKSwwXQfwF -HA_giAC1jzTmEnMjA73FtNpMjhI_coLOakc -MBX8f74K4k -
TGMfBVFwqcvzBnCBOQJ2OJCgZX -
YI109d4PDE9rGO3SK0OGIaLVDafB_9aoMeuMyrsut0PwgZoynUwA_DrwhOFkneNsA93rCIQck1WWOvxbrUtttm hvMDz
YSZu6-TcGx6pxEiHwOEQ5dx92Tv6nSIBS_tjHU -CElQMhcHcHsD6AF -
WdhSF2QtnvcCGasCcBPXzKF8cqd_QdvZvMgcUuwhUBVRRCEc_MCHDqGQBXZ6EzRE0PoXW_S6Rd1zvzT5SVFrgL3xGik
PHTxWP2DurNZuCHmFnMw

```
**5、把刚才的 kubeconfig 文件dashboard -admin.conf 复制到桌面**
浏览器访问时使用 kubeconfig 认证，把刚才的 dashboard -admin.conf导入到web界面，那么就可
以登陆了

把dashboard -admin.conf 文件导入

**12.4 通过kubernetes -dashboard 创建容器**
把nginx.tar.gz 镜像压缩包上传到 xianchaonode 1和xianchaonode2 上，手动解压：
docker load -i nginx.tar.gz

打开kubernetes 的dashboard 界面（https://192.168.40.1 80:32728/
） ，点开右上角红色箭头标注的  “+” ，如下图所示：

选择Create  from form

上面箭头标注的地方填写之后点击 Deploy即可完成 Pod的创建，如下：

在dashboard 的左侧选择 Services

上图可看到刚才创建的 nginx的service 在宿主机映射的端口是 31135，在浏览器访问：
**192.168.40.1 80:31135**

看到如下界面，说明 nginx部署成功了：

> **注：**

 应用名称： nginx
容器镜像： nginx
pod数量：2
service： external  外部网络
port：8-
targetport ：80

> **注：表单中创建 pod时没有创建 nodeport 的选项，会自动创建在 30000+以上的端口。**

关于port、targetport 、nodeport 的说明：
nodeport 是集群外流量访问集群内服务的端口，比如客户访问 nginx，apache，
port是集群内的 pod互相通信用的端口类型，比如 nginx访问mysql，而mysql是不需要让客户访
问到的， port是service 的的端口
targetport 目标端口，也就是最终端口，也就是 pod的端口。

**13、安装metrics-server组件**
metrics-server是一个集群范围内的资源数据集和工具，同样的， metrics-server也只是显示数
据，并不提供数据存储服务，主要关注的是资源度量 API的实现，比如 CPU、文件描述符、内存、请求延
时等指标， metric-server收集数据给 k8s集群内使用，如 kubectl,hpa,scheduler 等
**1、部署metrics-server组件**

```bash
#把离线镜像压缩包上传到k8s的各个节点，按如下方法手动解压：
[root@xianchaomaster1 ~]# ctr images import   aliyun-metrics-server-amd64-0-3-6.tar.gz
[root@xianchaomaster1 ~]# ctr images import  aliyun-addon.tar.gz

[root@xianchaonode1  ~]# ctr images import  aliyun-metrics-server-amd64-0-3-6.tar.gz
[root@xianchaonode1  ~]# ctr images import  aliyun-addon.tar.gz

#部署metrics-server服务
#在/etc/kubernetes/manifests 里面改一下 apiserver 的配置
```
> **注意：这个是 k8s在1.17的新特性，如果是 1.16版本的可以不用添加， 1.17以后要添加。这个参**
数的作用是 Aggregation 允许在不修改 Kubernetes 核心代码的同时扩展 Kubernetes API 。

```bash
[root@xianchaomaster1 ~]# vim /etc/kubernetes/manifests/kube -apiserver.y aml
```
增加如下内容：
- --enable-aggregator -routing=true

 重新更新 apiserver 配置：

```bash
[root@xianchaomaster1  ~]# systemctl restart kubelet
[root@xianchaomaster1 ~]# kubectl get pods -n kube-system
NAME                                       READY   STATUS    RESTARTS      AGE
calico-kube-controllers -677cd97c8d -fmhct   1/1     Running   0             11m
calico-node-jt475                          1/1     Running   0             11m
calico-node-q4zfw                          1/1     Running   0             11m
coredns-65c54cc984 -sd68l                   1/1     Running   0             21m
coredns-65c54cc984 -srxfv                   1/1     Running   0             21m
etcd-xianchaomaster1                       1/1     Running   0             21m
kube-apiserver -xianchaomaster1             1/1     Running   0             29s
kube-controller -manager-xianchaomaster1    1/1     Running   1 (31s ago)   21m
kube-proxy-bhxbh                           1/1     Running   0             21m
kube-proxy-twj5w                           1/1     Running   0             19m
kube-scheduler -xianchaomaster1             1/1     Running   1 (31s ago)   21m
[root@xianchaomaster1 ~]#  kubectl apply -f metrics.yaml
[root@xianchaomaster1 ~]#  kubectl get pods -n kube-system | grep metrics
metrics-server-6595f875d6 -r94sx            2/2     Running   0          16s
```

**13.1 测试kubectl top命令**

```bash
[root@xianchaomaster1 ~]# kubectl top pods -n kube-system
NAME                                       CPU(cores)   MEMORY(bytes)
calico-kube-controllers -677cd97c8d -fmhct   1m           27Mi
calico-node-jt475                          40m          65Mi
calico-node-q4zfw                          36m          95Mi
coredns-65c54cc984 -sd68l                   2m           24Mi
coredns-65c54cc984 -srxfv                   2m           16Mi
etcd-xianchaomaster1                       14m          69Mi
kube-apiserver -xianchaomaster1             47m          301Mi
kube-controller -manager-xianchaomaster1    23m          67Mi
kube-proxy-bhxbh                           4m           34Mi
kube-proxy-twj5w                           6m           25Mi
kube-scheduler -xianchaomaster1             6m           25Mi
metrics-server-97689b7bb -hxq7j             2m           17Mi

[root@xianch aomaster1 ~]# kubectl top nodes
NAME              CPU(cores)   CPU%   MEMORY(bytes)   MEMORY%
xianchaomaster1   361m         6%     2265Mi          61%
xianchaonode1     166m         2%     1642Mi          66%
```


