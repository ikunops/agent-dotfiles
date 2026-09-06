podSubnet （pod网段） 10.244.0.0/16
serviceSubnet （service 网段）: 10.96.0.0/16

实验环境规划：

准备两台虚拟机
操作系统： centos7.6
配置： 4Gib内存/6vCPU/100G硬盘
网络：NAT
机器IP：
K8s控制节点 Ip: 192.168.40.180
K8s工作节点 ip： 192.168.40.181

开启虚拟机的虚拟化：

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

关闭selinux
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
#修改selinux 配置文件之后，重启机器， selinux 配置才能永久生效
getenforce
Disabled
#显示Disabled 说明selinux 已经关闭

**1.2 配置机器主机名**
在192.168.40.180 上执行如下：
hostnamectl set -hostname  xianchaomaster1  && bash
在192.168.40.18 1上执行如下：
hostnamectl set -hostname xianchaonode1  && bash

**1.3 配置主机hosts文件，相互之间通过主机名 互相访问**
修改每台机器的 /etc/hosts 文件，增加如下 两行：
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

[root@xianchaonode1  ~]# modprobe br_netfilter
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
net.bridge.bridge -nf-call-iptables = 1

问题4：为什么要开启 net.ipv4.ip_forward = 1 参数？
kubeadm 初始化k8s如果报错：

就表示没有开启 ip_forward ，需要开启。

net.ipv4.ip_forward 是数据包转发：
出于安全考虑， Linux系统默认是禁止数据包转发的。所谓转发即当主机拥有多于一块的网卡时，
其中一块收到数据包，根据数据包的目的 ip地址将数据包发往本机另一块网卡，该网卡根据路由表继
续发送数据包。这通常是路由器所要 实现的功能。
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
[root@xianchaomaster1 ~]# yum install yum -utils -y
[root@xianchaomaster1 ~]# yum-config-manager --add-repo
http://mirrors.aliyun.com/docker -ce/linux/centos/docker -ce.repo
[root@xianchaonode1 ~]#  yum install yum -utils -y

 [root@xianchaonode1 ~]# yum-config-manager --add-repo http://mirrors.aliyun.com/docker -
ce/linux/centos/docker -ce.repo
```

**1.10 配置安装k8s组件需要的 阿里云的 repo源**

```bash
[root@xianchaomaster1 ~]# cat >  /etc/yum.repos.d/kubernetes.repo  <<EOF
[kubernetes]
name=Kubernetes
baseurl=https://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes -el7-x86_64/
enabled=1
gpgcheck=0
EOF

#将xianchaomaster1 上Kubernetes 的repo源复制给 xianchaonode1 和xianchaonode 2
[root@xianchaomaster1 ~]# scp /etc/yum.repos.d/kubernetes.repo
xianchaonode1 :/etc/yum.repos.d/
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

#把ipvs.modules 拷贝到xianchaonode 1的/etc/sysconfig/modules/ 目录下
[root@xianchaomaster1 ~]# scp /etc/sysconfig/modules/ipvs.modules
xianchao node1:/etc/sysconfig/modules/

[root@xianchaonode1]# chmod 755 /etc/sysconfig/modules/ipvs.modules && bash
/etc/sysconfig/modules/ipvs.modules && lsmod | g rep ip_vs
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
**2、ipvs 支持比 iptables 更复杂的复制均衡算法（最小负载、最少连接、加权等等）**
**3、ipvs 支持服务器健康检查和连接重试等功能**

**1.13 安装基础软件包**

```bash
[root@xianchaomaster1 ~]# yum install -y yum-utils device -mapper-persistent -data lvm2
wget net -tools nfs -utils lrzsz gcc gcc -c++ make cmake libxml2 -devel openssl -devel curl
curl-devel unzip sudo ntp  libaio-devel wget vim ncurses -devel autoconf automake zlib -
devel  python-devel epel -release openssh -server socat   ipvsadm conntrack ntpdate  telnet
ipvsadm

[root@xianchaonode1 ~]# yum install -y yum-utils device -mapper-persistent -data lvm 2
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

接下来安装步骤在 k8s控制节点和工作节点都要操作

在各个服务器节点上安装容器运行时  Containerd 。下载 Containerd 的二进制包 :
wget https://github.com/containerd/containerd/releases/download/v1.6.4/cri -containerd -
cni-1.6.4 -linux -amd64.tar.gz

这个二进制包在课件里也有，大家可以直接从课 件里上传到 k8s所有机器上

cri-containerd -cni-1.6.4 -linux -amd64.tar.gz 压缩包中已经按照官方二进制部署推荐的目录结构布局
好。 里面包含了  systemd 配置文件， containerd 以及 cni 的部署文件。  将解压缩到系统的根目录  /
中:

tar -zxvf cri -containerd -cni-1.6.4-linux-amd64.tar.gz -C /

注意经测试  cri-containerd -cni-1.6.4 -linux -amd64.tar.gz 包中包含的  runc 在 CentOS 7 下的动态链
接有问题，这里从  runc 的 github 上单独下载  runc ，并替换上面安装的  containerd 中的 runc:
wget https://github.com/openco ntainers/runc/releases/download/v1.1.2/runc.amd64

runc.amd64 在课件里也有，大家可以手动上传到 k8s的各个节点上

cp runc.amd64 /usr/local/sbin/runc
chmod +x /usr/local/sbin/runc

接下来生成  containerd 的配置文件 :
mkdir -p /etc/containerd
containerd config default > /etc/containerd/config.toml

根据文档  Container runtimes 中的内容，对于使用  systemd 作为 init system 的 Linux 的发行版，
使用 systemd 作为容器的  cgroup driver 可以确保服务器节点在资源紧张的情况更加稳定，因此这里
配置各个节点上  containerd 的 cgroup driver 为 systemd。修改前面生成的配置文件
/etc/containerd/config.toml ：
[plugins."io.c ontainerd.grpc.v1.cri".containerd.runtimes.runc]
  ...
  [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
SystemdCgroup = true

再修改 /etc/containerd/config.toml 中的
[plugins."io.containerd.grpc.v1.cri"]
  ...
  # sandbox_image = "k8s.gcr.io/pause:3.6"
  sandbox_image = "registry.aliyuncs.com/google_containers/pause:3.7"

配置 containerd 开机启动，并启动  containerd
systemctl enable containerd  --now

启动 containerd
systemctl start containerd

**3、安装初始化 k8s需要的软件包**

```bash
[root@xianchaomaster1  ~]# yum install -y kubelet -1.24.1 kubeadm-1.24.1 kubectl-1.24.1
[root@xianchaomaster1  ~]# systemctl enable kubelet

[root@xianchaonode1  ~]# yum install -y kubelet -1.24.1 kubeadm-1.24.1 kubectl-1.24.1

 [root@xianchaonode1  ~]# systemctl enable kubelet
```

> **注：每个软件包的作用**
Kubeadm:  kubeadm 是一个工具，用来初始化 k8s集群的
kubelet:   安装在集群所有节点上，用于启动 Pod的
kubectl:   通过kubectl 可以部署和管理应用，查看各种资源，创建、删除和更新各种组件

**4、kubeadm初始化k8s集群**

```bash
#设置容器运行时
[root@xianchaonode1 ~]# crictl config runtime -endpoint /run/containerd/containerd.sock

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
  criSocket:  unix:///run/containerd/containerd .sock  #用containerd 作为容器运行时
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
kubernetesVersion: 1.2 4.1 #k8s版本
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
[root@xianchaomaster1 ~]# kubeadm init --config=kubeadm.yaml  --ignore -preflight -
errors=SystemVerification
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
xianchaomaster1   Ready   control -plane,master   2m25s   v1.2 4.1
```

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
[root@xianchaonode1 ~]# kubeadm join 192.168.40.180:6443 --token vulvta.9ns7da3saibv4pg1
--discovery -token-ca-cert-hash
sha256:72a0896e27521244850b8f1c3b6000 87292c2d10f2565adb56381f1f4ba7057a  --ignore -preflight -
errors=SystemVerification

#看到上面说明 xianchaonode1 节点已经加入到集群了 ,充当工作节点

#在xianchaomaster1 上查看集群节点状况 ：
[root@xianchaomaster1 ~]# kubectl get nodes
NAME              STATUS     ROLES                  AGE     VERSION
xianchaomaster1   Ready   control -plane,master   3m11s   v1.2 4.1
xianchaonode1     Ready   <none>                 8s      v1.2 4.1

#可以对xianchaonode 1打个标签，显示 work
[root@xianchaomaster1 ~]# kubectl label nodes xianchaonode1 node-
role.kubernetes.io/work=work

 [root@xianchaomaster1 ~]# kubectl get nodes
NAME              STATUS     ROLES                  AGE     VERSION
xianchaomaster1   NotReady   control -plane,master   27m     v1.2 4.1
xianchaonode1     NotReady   work                   5m47s   v1.2 4.1
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
xianchaomaster1   Ready    control -plane,master   58m     v1.2 4.1
xianchaonode1     Ready    <none>                 5m46s   v1.2 4.1

[root@xianchaomaster1 ~]# kubectl get pods -n kube-system
NAME                                       READY   STATUS    REST ARTS   AGE
calico-kube-controllers -677cd97c8d -fmhct   1/1     Running   0          59s
calico-node-jt475                          1/1     Running   0          59s
calico-node-q4zfw                          1/1     Running   0          59s
coredns-65c54cc98 4-sd68l                   1/1     Running   0          11m
coredns-65c54cc984 -srxfv                   1/1     Running   0          11m
etcd-xianchaomaster1                       1/1     Running   0          11m
kube-apiserver -xianchaomaster1             1/ 1     Running   0          11m
kube-controller -manager-xianchaomaster1    1/1     Running   0          11m
kube-proxy-bhxbh                           1/1     Running   0          11m
kube-proxy-twj5w                           1/1     Running   0          8 m29s
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

Name:      kubernetes.default.svc.clu ster.local
Address 1: 10.96.0.1 kubernetes.default.svc.cluster.local
```

**10.96.0.10 就是我们 coreDNS 的clusterIP ，说明coreDNS 配置好了。**
解析内部 Service 的名称，是通过 coreDNS 去解析的。

#注意：
busybox要用指定的 1.28版本，不能用最新版本，最新版本， nslookup 会解析不到 dns和ip


