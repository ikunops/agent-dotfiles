一、Ceph简介

官方：
https://ceph.com/en/

https://docs.ceph.com/en/latest/start/intro/

ceph是一种开源的分布式的存储系统
包含以下几种存储类型：
块存储（ rbd） ，对象存储 (RADOS Fateway) ，文件系统（ cephfs）
1.块存储（ rbd）：
块是一个字节序列（例如， 512字节的数据块） 。  基于块的存储接口是使用旋转介质（如硬
盘，CD，软盘甚至传统的 9轨磁带）存储数据的最常用方法 ;Ceph块设备是精简配置，可调
整大小并存储在 Ceph集群中多个 OSD条带化的数据。  Ceph块设备利用 RADOS功能，如快
照，复制和一致性。  Ceph的RADOS块设备（ RBD）使用内核模块或 librbd库与OSD进行交
互;Ceph的块设备为内核模块或 QVM等KVM以及依赖 libvirt和QEMU与Ceph块设备集成的
OpenStack 和CloudStack 等基于云的计算系统提供高性能和无限可扩展性。  可以使用同一
个集群同时运行 Ceph RADOS Gateway ，CephFS文件系统和 Ceph块设备。
linux系统中， ls /dev/ 下有很多块设备文件，这些文件就是我们添加硬盘时识别出来的；
rbd就是由Ceph集群提供出来的块设备。可以这样理解， sda是通过数据线连接到了真实的
硬盘， 而 rbd是通过网络连接到了 Ceph集群中的一块存储区域， 往 rbd设备文件写入数据，
最终会被存储到 Ceph集群的这块区域中；
总结：块设备可理解成一块硬盘，用户可以直接使用不含文件系统的块设备，也可以将其格
式化成特定的文件系统，由文件系 统来组织管理存储空间，从而为用户提供丰富而友好的数
据操作支持。
2.文件系统 cephfs
Ceph文件系统（ CephFS）是一个符合 POSIX标准的文件系统，它使用 Ceph存储集群来存储
其数据。  Ceph文件系统使用与 Ceph块设备相同的 Ceph存储集群系统。

 用户可以在块设备上创建 xfs文件系统，也可以创建 ext4等其他文件系统， Ceph集群实现
了自己的文件系统来组织管理集群的存储空间，用户可以直接将 Ceph集群的文件系统挂载
到用户机上使用， Ceph有了块设备接口， 在块设备上完全可以构建一个文件系统， 那么 Ceph
为什么还需要文件系统接口呢？
主要是因为应用场景的不同， Ceph的块设备具有优异的读写性能，但不能多处挂载同时读
写，目前主要用在 OpenStack 上作为虚拟磁盘，而 Ceph的文件系统接口读写性能较块设备
接口差，但具有优异的共享性。
3.对象存储
Ceph对象存储使用 Ceph对象网关守护进程（ radosgw） ，它是一个用于与 Ceph存储集群交
互的HTTP服务器。由于它提供与 OpenStack Swift 和Amazon S3 兼容的接口，因此 Ceph对
象网关具有自己的用户管理。  Ceph对象网关可以将数据 存储在用于存储来自 Ceph文件系
统客户端或 Ceph块设备客户端的数据的相同 Ceph存储集群中
使用方式就是通过 http协议上传下载删除对象（文件即对象） 。
老问题来了，有了块设备接口存储和文件系统接口存储，为什么还整个对象存储呢 ?
Ceph的块设备存储具有优异的存储性能但不具有共享性，而 Ceph的文件系统具有共享性然
而性能较块设备存储差，为什么不权衡一下存储性能和共享性，整个具有共享性而存储性能
好于文件系统存储的存储呢，对象存储就这样出现了。

分布式存储的优点：
高可靠： 既满足存储读取不丢失，还要保证数 据长期存储。  在保证部分硬件损坏后依然可
以保证数据安全
高性能： 读写速度快
可扩展：分布式存储的优势就是 “分布式”，所谓的 “分布式”就是能够将多个物理节点整
合在一起形成共享的存储池，节点可以线性扩充，这样可以源源不断的通过扩充节点提升性
能和扩大容量，这是传统存储阵列无法做到的

二、Ceph核心组件介绍
在ceph集群中，不管你是想要提供对象存储，块设备存储，还是文件系统存储，所有 Ceph
存储集群部署都是从设置每个 Ceph节点，网络和 Ceph存储开始  的。 Ceph存储集群至少
需要一个 Ceph Monit or，Ceph Manager 和Ceph OSD （对象存储守护进程） 。  运行Ceph
Filesystem 客户端时也需要 Ceph元数据服务器。

Monitors ：Ceph监视器（ ceph-mon）维护集群状态的映射，包括监视器映射，管理器映射，
OSD映射和CRUSH映射。这些映射是 Ceph守护进程相互协调所需的关键集群状态。监视器
还负责管理守护进程和客户端之间的身份验证。冗余和高可用性通常至少需要三个监视器。

Managers ：Ceph Manager守护程序（ ceph-mgr）负责跟踪运行时指标和 Ceph集群的当前状
态， 包括存储利用率， 当前性能指标和系统负载。  Ceph Manager 守护进程还托管基于 python
的模块来管理和公开 Ceph集群信息，包括基于 Web的Ceph Dashboard 和REST API 。高可
用性通常至少需要两名 Managers 。

 Ceph OSD ：Ceph OSD （对象存储守护进程， ceph-osd）存储数据，处理数据复制，恢复，重
新平衡，并通过检查其他 Ceph OSD 守护进程来获取心跳，为 Ceph监视器和管理 器提供一些
监视信息。冗余和高可用性通常至少需要 3个Ceph OSD 。

MDS：Ceph元数据服务器（ MDS，ceph-mds）代表Ceph文件系统存储元数据（即， Ceph块设
备和Ceph对象存储不使用 MDS）。 Ceph元数据服务器允许 POSIX文件系统用户执行基本命
令（如ls，find等） ，而不会给 Ceph存储集群带来巨大负担。

三、安装 Ceph集群
1初始化实验环境
机器配置：
Centos 7.6
网络模式： NAT
准备三台机器，每台机器需要三个硬盘，配置 4GiB/6vCPU/60G
master1 -admin是管理节点  ：192.168.40.200

node1 -monitor是监控节点： 192.168.40.201

node2 -osd是对象存储节点： 192.168.40.202

**1、配置静态 IP：**
把虚拟机或者物理机配置成静态 ip地址， 这样机器重新启动后 ip地址也不会发生改变。
以master1 -admin主机为例，修改静态 IP:
修改/etc/sysconfig/network -scripts/ifc fg-ens33文件，变成如下：

```bash
TYPE=Ethernet
PROXY_METHOD=none

 BROWSER_ONLY=no
BOOTPROTO=static
IPADDR=192.168.40. 200
NETMASK=255.255.255.0
GATEWAY=192.168.40.2
DNS1=192.168.40.2
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
DEVICE=ens33    #网卡设备名，大家 ip addr可看到自己的这个网卡设备名，每个人的
```
机器可能这个名字不一样，需要写自己的

```bash
BOOTPROTO=static   #static表示静态 ip地址
ONBOOT=yes    #开机自启动网络，必须是 yes
IPADDR=192.168.40. 200   #ip地址，需要跟自己电脑所在网段一致
NETMASK=255.255.255.0  #子网掩码，需要跟自己电脑所在网段一致
GATEWAY=192.168.40.2    #网关，在自己电脑打开 cmd，输入 ipconfig /all 可看到
DNS1=192.168.40.2     #DNS，在自己电脑打开 cmd，输入 ipconfig /all 可看到
```

**2、配置主机名：**
在192.168.40.200 上执行如下：
hostnamectl set -hostname master1 -admin  && bash
在192.168.40.201 上执行如下：
hostnamectl set -hostname node1 -monitor  && bash
在192.168.40.202 上执行如下：
hostnamectl set -hostname node2 -osd && bash

**3、配置 hosts文件：**
修改 master 1-admin、node 1-monitor、node 2-osd机器的 /etc/hosts 文件，增加如下三
行：
**192.168.40.200 master1 -admin**
**192.168.40.201 node1 -monitor**
**192.168.40.202 node2 -osd**

**4、配置互信**
生成 ssh 密钥对

```bash
[root@master1 -admin ~]# ssh -keygen -t rsa  #一路回车，不输入密码
```
把本地的 ssh公钥文件安装到远程主机对应的账户

```bash
[root@master1 -admin ~]# ssh -copy -id node1 -monitor

[root@master1 -admin ~]# ssh -copy -id node 2-osd
[root@master1 -admin ~]# ssh -copy -id master1 -admin

[root@node1 -monitor ~]#  ssh-keygen  # 一路回车，不输入密码
```
把本地的 ssh公钥文件安装到远程主机对应的账户

```bash
[root@node1 -monitor ~]# ssh -copy -id  master1 -admin
[root@node1 -monitor ~]# ssh -copy -id  node1 -monitor
[root@node1 -monitor ~]# ssh -copy -id node2 -osd

[root@node2 -osd ~]# ssh -keygen   #一路回车，不输入密码
```
把本地的 ssh公钥文件安装到远程主机对应的账户

```bash
[root@node2 -osd ~]# ssh -copy -id master1 -admin
[root@node2 -osd ~]# ssh -copy -id node1 -monitor
[root@node2 -osd ~]# ssh -copy -id node2 -osd
```

**5、关闭防火墙**

```bash
[root@master1 -admin ~]# systemctl stop fir ewalld ; systemctl disable firewalld
[root@node1 -monitor ~]# systemctl stop firewalld ; systemctl disable firewalld

 [root@node2 -osd ~]# systemctl stop firewalld ; systemctl disable firewalld
```

**6、关闭 selinux**
所有 ceph节点的 selinux都关闭

#临时关闭
setenforce 0
#永久关闭
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
#注意：修改 selinux配置文件之后，重启机器， selinux才能永久生效

**7、配置 Ceph安装源**
#配置阿里云 的repo源，master 1-admin、node 1-monitor、node 2-osd上操作：
mkdir /root/yum.bak
cd /etc/yum.repos.d/
mv * /root/yum.bak/
把课件里 yum源目录下的内容上传到 /etc/yum.repos.d/ 目录下

#配置 ceph的repo源，master 1-admin、node 1-monitor、node 2-osd上操作：
yum install -y yum -utils && sudo yum -config -manager --add-repo
https://dl.fedoraproject.org/pub/epel/7/x86_64/ && sudo yum install --nogpgcheck -y
epel-release  && sudo rpm --import /etc/pki/rpm -gpg/RPM -GPG-KEY-EPEL-7 &&
sudo rm /etc/yum.repos.d/dl.fedoraproject.org*

#把ceph. repo上传到 master 1-admin、node 1-monitor、node 2-osd上
cat  /etc/yum.repos.d/ceph.repo
[Ceph]

```bash
name=Ceph packages for $basearch
baseurl=http://mirrors .aliyun.com/ceph/rpm -jewel/el7/x86_64/
enabled=1
gpgcheck=0
type=rpm -md
gpgkey=https://mirrors.aliyun.com/ceph/keys/release.asc
priority=1

 [Ceph -noarch]
name=Ceph noarch packages
baseurl=http://mirrors.aliyun.com/ceph/rpm -jewel/el7/noarch/
enabled= 1
gpgcheck=0
type=rpm -md
gpgkey=https://mirrors.aliyun.com/ceph/keys/release.asc
priority=1
[ceph -source]
name=Ceph source packages
baseurl=http://mirrors.aliyun.com/ceph/rpm -jewel/el7/SRPMS/
enabled=1
gpgcheck=0
type=rpm -md
gpgkey=https://mirrors.aliyun.com/ceph/keys/release.asc
priority=1
```

master 1-admin、node 1-monitor、node 2-osd上操作如下步骤：
清空缓存
yum clean all
生成新的缓存
yum makecache fa st
升级 yum源
yum -y update

**8、安装 iptables**
#如果你用 firewalld 不是很习惯，可以安装 iptables ，在 ceph的每台机器上操作

yum install iptables -services -y
#禁用 iptables
service iptables stop   && systemctl disable iptables

**9、配置时间同步**
配置机器时间跟网络时间同步，在 ceph的每台机器上操作
service ntpd stop

 ntpdate cn.pool.ntp.org
crontab -e
* */1 * * * /usr/sbin/ntpdate   cn.pool.ntp.org

service crond restart

**10、安装基础软件包**
#安装基础软件包 ，在 ceph的每台机器上操作
yum install -y yum -utils device -mapper -persistent -data lvm2 wget net -tools nfs -utils
lrzsz gcc gcc -c++ make cmake libxml2 -devel openssl -devel curl curl -devel unzip sudo
ntp libaio -devel wget vim ncurses -devel autoconf automake zlib -devel   python -devel
epel-release openssh -server socat   ipvsadm conntrack ntpdate  telnet  deltarpm

**2、安装ceph集群**
**2.1 安装 ceph -deploy**

```bash
#在master 1-admin节点安装 ceph -deploy
[root@master1 -admin ~]# yum install python -setuptools   ceph -deploy -y
#在master 1-admin、node 1-monitor和node 2-osd节点安装 ceph
[root@master1 -admin]#  yum install ceph ceph -radosgw   -y
[root@node1 -monitor ~]# yum install ceph ceph -radosgw   -y
[root@node2 -osd ~]# yum install ceph ceph -radosgw   -y

[root@master1 -admin ~]# ceph --version
ceph version 10.2.11 (e4b061b47f07f583c92a050d9e84b1813a35671e)
```

**2.2 创建 monitor 节点**

```bash
#创建一个目录，用于保存  ceph -deploy 生成的配置文件信息的
[root@master1 -admin ceph  ~]# cd /etc/ceph
[root@master1 -admin  ceph ]# ceph -deploy new master1 -admin node1 -monitor node2 -
osd
[root@master1 -admin  ceph ]# ls

 #生成了如下配置文件
ceph.conf  ceph -deploy -ceph.log  ceph.mon.keyring
```

Ceph配置文件、一个 monitor密钥环和一个日志文件

**2.3 安装 ceph -monitor**
**1、修改 ceph配置文件**
#把ceph .conf配置文件里的默认副本数从 3改成 1 。把 osd_pool_default _size = 2
加入[global]段，这样只有 2个osd也能达到 active+clean 状态：

```bash
[root@master1 -admin]# vim /etc/ceph/ceph.conf
[global]
fsid = af5cd413 -1c53-4035 -90c6-95368eef5c78
mon_initial_members = node1 -monitor
mon_host = 192.168.40.201
auth_cluster_required = cephx
auth_service_required = cephx
auth_client_required = cephx
filestore_xattr_use_omap = true
osd_pool_default _size = 2
mon clock drift allowed = 0.500
mon clock  drift warn backoff = 10

mon clock drift allowed  #监视器间允许的时钟漂移量 默认值 0.05
mon clock drift warn backoff  #时钟偏移警告的退避指数。 默认值 5
```
ceph对每个 mon之间的时间同步延时默认要求在 0.05s之间，这个时间有的时候太短
了。所以如果 ceph集群如果出现 clock问题就检查 ntp时间同步或者适当放宽这个误差时
间。
cephx是认证机制是 整个 Ceph 系统的用户名 /密码

**2、配置初始 monitor、收集所有的密钥**

```bash
[root@master1 -admin]#  cd /etc/ceph
[root@master1 -admin]# ceph -deploy mon create -initial
[root@master1 -admin]#  ls *.keyring
ceph.bootstrap -mds.keyring  ceph.bootstrap -mgr.keyring  ceph.bootstrap -
osd.keyring  ceph.bootstrap -rgw.keyring  ceph.client.admin.keyring
ceph.mon.keyring
```

**2.4 部署 osd服务**

```bash
#准备 osd
[root@  master1 -admin  ceph]#  cd /etc/ceph/
[root@master1 -admin ceph]# ceph -deploy osd prepare master1 -admin:/dev/sdb
[root@master1 -admin ceph]# ceph -deploy osd prepare node1 -monitor:/dev/sdb
[root@master1 -admin ceph]# ceph -deploy osd prepare node2 -osd:/dev/sdb

#激活 osd
[root@master1 -admin ceph]# ce ph-deploy osd activate master1 -admin:/dev/sdb1
[root@master1 -admin ceph]# ceph -deploy osd activate node1 -monitor:/dev/sdb1
[root@master1 -admin ceph]# ceph -deploy osd activate node2 -osd:/dev/sdb1
```

查看状态 ：

```bash
[root@  master1 -admin  ceph]#  ceph -deploy osd list mast er1-admin  node1 -monitor
node2 -osd
```

要使用 Ceph文件系统，你的 Ceph的存储集群里至少需要存在一个 Ceph的元数据服
务器(mds)。
**2.5 创建 ceph文件系统**
创建 mds

```bash
[root@  master1 -admin  ceph]# ceph -deploy mds create master1 -admin  node1 -monitor
node2 -osd
```

查看 ceph当前文件系统

```bash
[root@  master1 -admin  ceph]#  ceph fs ls

No filesystems enabled
```

一个 cephfs至少要求两个 librados存储池，一个为 data，一个为 metadata 。当配置这
两个存储池时，注意：
**1. 为metadata pool 设置较高级别的副本级别，因为 metadata 的损坏可能导致整个文**
件系统不用
**2. 建议， metadata pool 使用低延时存储，比如 SSD，因为 metadata 会直接影响客户端**
的响应速度。

创建存储池

```bash
 [root@  master1 -admin  ceph]# ceph osd pool create cephfs_data 128
pool 'cephfs_data' created
[root@  master1 -admin  ceph]# ceph osd pool create cephfs_metadata 128
pool 'cephfs_metadata' created
```

关于创建存储池
确定 pg_num 取值是强制性的，因为不能自动计算。下面是几个常用的值：
*少于 5 个 OSD 时可把  pg_num 设置为  128
*OSD 数量在  5 到 10 个时，可把  pg_num 设置为  512
*OSD 数量在  10 到 50 个时，可把  pg_num 设置为  4096
*OSD 数量大于  50 时，你得理解权衡方法、以及如何自己计算  pg_num 取值
*自己计算  pg_num 取值时可借助  pgcalc 工具
随着 OSD 数量的增加， 正确的  pg_num 取值变得更加重要， 因为它显著地影响着集群
的行为、以及出错时的数据持久性（即灾难性事件导致数据丢失的概率） 。

创建文件系统
创建好存储池后，你就可以用  fs new 命令创建文件系统了

```bash
[root@  master1 -admin  ceph]# ceph fs new xianchao  cephfs_metadata cephfs_data
new fs with metadata pool 2 and data pool 1
```
其中： new后的 fsname  可自定义

```bash
[root@  master1 -admin  ceph]#  ceph fs ls              #查看创建后的 cephfs
[root@  master1 -admin  ceph]#  ceph mds stat           #查看 mds节点状态

xianchao :1 {0=master1 -admin=up:active} 2 up:standby
```
active是活跃的， 另1个是处于热备份的状态

```bash
[root@master1 -admin ceph]# ceph -s
    cluster cd296ab9 -1f61-4b9f-8cc3-0a57dfab00eb
     health HEALTH_OK
     monmap e1: 3 mons at {master1 -admin=192.168.40.200:6789/0,node1 -
monitor=192.168.40.201:6789/0,node2 -osd=192.168.40.202:6789/0}
            election epoch 4, quorum 0,1,2 master1 -admin,node1 -monitor,node2 -osd
      fsmap e7: 1/1/1 up {0=node2 -osd=up:active}, 2 up:standby
     osdmap e20: 3 osds: 3 up, 3 in
            flags sortbitwise,require_jewel_osds
      pgmap v51: 116 pgs, 3 pools, 2068 bytes data, 20 objects
            323 M B used, 164 GB / 164 GB avail
                 116 active+clean
```

HEALTH_OK 表示 ceph集群正常

**2.6 测试 k8s挂载 ceph rbd**
需要有一套 k8s环境

```bash
[root@xianchaomaster1 ~]# kubectl get nodes
NAME              STATUS   ROLES                  AGE   VERSION
xianchaomaster1   Ready    control -plane,master   24d   v1.20.6
xianchaonode1     Ready    worker                 24d   v1.20.6
```

xianchaomaster1 节点 ip：192.168.40.1 80
xianchaonode1 节点 ip：192.168.40.1 81

# kubernetes 要想使用 ceph， 需要在 k8s的每个 node节点安装 ceph -common ，把ceph
节点上的 ceph.repo 文件拷贝到 k8s各个节点 /etc/yum.repos.d/ 目录下，然后在k8s的各个
节点 yum install ceph -common -y

```bash
#将ceph配置文件拷贝到 k8s的控制节点和工作节点
[root@master1 -admin ~]# scp /etc/ceph/* 192.168.40. 180:/etc/ceph/
[root@master1 -admin ~]# s cp /etc/ceph/* 192.168.40. 181:/etc/ceph/

#创建 ceph  rbd
[root@master1 -admin ~]# ceph osd pool create k8srbd1 56
pool 'k8srbd' created
[root@master1 -admin ~]# rbd create rbda -s 1024 -p k8srbd1
[root@master1 -admin ~]# rbd feature disable  k8srbd 1/rbda object -map fast -diff
deep -flatten

#创建 pod，挂载 ceph  rbd
#把nginx .tar.gz 上传到 xianchaonode1 上，手动解压
[root@ xianchaonode1  ~]# docker load -i nginx.tar.gz
[root@ xianchaomaster1  ~]# vim pod.yaml
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: testrbd
spec:
  containers:
    - image: nginx
      name: nginx
      imagePullPolicy: IfNotPresent
      volumeMounts:
      - name: testrbd
        mountPath: /mnt

   volumes:
    - name: testrbd
      rbd:
        monitors:
        - '192.168.40.201:6789'
        - '192.168.40.200:6789'
        - '192.168.40.202:6789'
        pool: k8srbd1
        image: rbda
        fsType: xfs
        readOnly: false
        user: admin
        keyring: /etc/ceph/ceph.client.admin.keyring

#更新资源清单文件
```

```bash
[root@ xianchaomaster1  ~]# kubectl apply -f pod.yaml
#查看 pod是否创建成功
[root@ xianchaomaster1  ~]# kubectl get pods -o wide
```

> **注意：  k8srbd1下的 rbda被pod挂载了，那其他 pod就不能占用这个 k8srbd1下的**
rbda了
例：创建一个 pod-1.yaml

```bash
[root@ xianchaomaster1  ~]# cat pod -1.yaml
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: testr bd1
spec:
  containers:
    - image: nginx
      name: nginx
      imagePullPolicy: IfNotPresent
      volumeMounts:
      - name: testrbd
        mountPath: /mnt
  volumes:
    - name: testrbd
      rbd:
        monitors:
        - '192.168.40.201:6789'
        - '192.168.40.200:6789'
        - '192.168.40.202:6789'

         pool: k8srbd1
        image: rbda
        fsType: xfs
        readOnly: false
        user: admin
        keyring: /etc/ceph/ceph.client.admin.keyring

```

```bash
[root@ xianchaomaster1  ~]# kubectl apply -f pod -1.yaml
pod/testrbd1 created
[root@ xianchaomaster1  ~]# kubectl get pods
NAME       READY   STATUS    RESTARTS   AGE
testrbd    1/1     Running   0          51s
testrbd1   0/1     Pending   0          15s
#查看 testrbd 1详细信息
[root@ xianchaomaster1  ~]# kubectl describe pods testrbd1
Warning  FailedScheduling  48s (x2 over 48s)  default -scheduler  0/2 nodes are
available: 1 node(s) had no available disk, 1 node(s) had taint {node -
role.kubernetes.io/master: }, that  the pod didn't tolerate.
```
上面一直 pending 状态，通过 warnning 可以发现是因为我的 pool: k8srbd1
        image: rbda
已经被其他 pod占用了。

**2.7 基于 ceph rbd生成 pv**
**1、创建 ceph -secret这个 k8s secret 对象，这个 secret对象用于 k8s volume 插件访问**
ceph集群，获取 client.admin 的keyring值，并用 base64编码，在 master1 -admin（ceph
管理节点）操作

```bash
[root@master1 -admin ~]# ceph auth get -key client.admin | base64
QVFBWk0zeGdZdDlhQXhBQVZsS0poYzlQUlBianBGSWJVbDNBenc9PQ==
```

2.创建 ceph的secret，在 k8s的控制节点操作：

```bash
[root@ xianchaomaster1  ~]# cat ceph -secret.yaml
```

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: ceph -secret
data:
  key: QVFBWk0zeGdZdDlhQXhBQVZsS0poYzlQUlBianBGSWJVbDNBenc9PQ==
```

```bash
[root@ xianchaomaster1  ~]# kubectl apply -f ceph -secret.yaml
```

3.回到 ceph 管理节点创建 pool池

```bash
[root@master1 -admin ~]# ceph osd pool create k8stest 56
pool 'k8stest' created
[root@master1 -admin ~]# rbd create rbda -s 1024 -p k8stest
[root@master1 -admin ~]# rbd feature disable  k8stest/rbda object -map fast -diff deep -
flatten
```

**4、创建 pv**

```bash
[root@ xianchaomaster1  ~]# cat pv.yaml
```

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name:  ceph -pv
spec:
   capacity:
     storage: 1Gi
   accessModes:
   - ReadWriteOnce
   rbd:
         monitors:
         - '192.168.40.201:6789'
         - '192.168.40.200:6789'
         - '192.168.40.202:6789'
         pool: k8stest
         image: rbda
         user: admin
         secretRef:
             name: ceph -secret
         fsType: xfs
         readOnly: false
   persistentVolumeReclaimPolicy: Recycle

```

```bash
[root@ xianchaomaster1  ~]# kubectl apply -f pv.yaml
persistentvolume/ceph -pv created
[root@ xianchaomaster1  ~]# kubectl get pv
```

**5、创建 pvc**

```bash
[root@ xianchaomaster1  ~]# cat pvc.yaml
```

```yaml
kind: PersistentVolumeClaim
apiVersion: v1

 metadata:
  name: ceph -pvc
spec:
  accessModes:
  - ReadWriteOnce
  resources:
   requests:
    storage: 1Gi
```

```bash
[root@ xianchaomaster1  ~]# kubectl apply -f pvc.yaml

[root@xianchaomaster1 ceph]# kubectl get pvc
NAME          STATUS   VOLUME
CAPACITY   ACCESS MODES   STORAGECLASS   AGE
ceph -pvc      Bound    ceph -pv                                    1Gi
RWO
```

**6、测试挂载 pvc**

```bash
[root@ xianchaomaster1  ~]# cat pod -2.yaml
```

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx -deployment
spec:
  selector:
    matchLabels:
     app: nginx
  replicas: 2 # tells deployment to run 2 pods matching the template
  template: # create pods us ing pod definition in this template
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 80
        volumeMounts:
          - mountPath: "/ceph -data"
            name: ceph -data

       volumes:
      - name: ceph -data
        persistentVolumeClaim:
            claimName: ceph -pvc

```

```bash
[root@ xianchaomaster1  ~]# kubectl apply -f pod -2.yaml
[root@ xianchaomaster1  ~]# kubectl get pods -l app=nginx
NAME                                 READY   STATUS    RESTARTS   AGE
nginx -deployment -fc894c564 -8tfhn    1/1      Running   0             78s
nginx -deployment -fc894c564 -l74km    1/1     Running   0             78s

[root@xianchaomaster1  ~]# cat pod -3.yaml
```

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx -1-deployment
spec:
  selector:
    matchLabels:
     appv1: nginxv1
  replicas: 2 # tells deployment to run 2 pods matching the template
  template: # create  pods using pod definition in this template
    metadata:
      labels:
        appv1: nginxv1
    spec:
      containers:
      - name: nginx
        image: nginx
imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 80
        volumeMounts:
          - mountPath: "/ceph -data"
            name: ceph -data
      volumes:
      - name: ceph -data
        persistentVolumeClaim:
            claimName: ceph -pvc

```

```bash
[root@ xianchaomaster1  ~]# kubectl apply  -f pod -3.yaml
[root@ xianchaomaster1  ~]# kubectl get pods -l appv1=nginxv1

 NAME                                 READY   STATUS    RESTARTS   AGE
nginx -1-deployment -cd74b5dd4 -jqvxj   1/1     Running   0          56s
nginx -1-deployment -cd74b5dd4 -lrddc   1/1     Running   0          56s
```

通过上面实验可以发现 pod是可以以ReadWriteOnce 共享挂载 相同的 pvc的

> **注意： ceph  rbd块存储的特点**
ceph rbd 块存储能在同一个 node上跨 pod以ReadWriteOnce 共享挂载
ceph rbd 块存储能在同一个 node上同一个 pod多个容器中以 ReadWriteOnce 共享挂
载
ceph rbd 块存储不能跨 node以ReadWriteOnce 共享挂载
如果一个使用 ceph rdb 的pod所在的 node挂掉， 这个 pod虽然会被调度到其它 node，
但是由于 rbd不能跨 node多次挂载和挂掉的 pod不能自动解绑 pv的问题，这个新
pod不会正常运行

Deployment 更新特性：
deployment 触发更新的时候，它确保至少所需  Pods 75% 处于运行状态（最大不可用
比例为  25%） 。故像一个 pod的情况，肯定是新创建一个新的 pod，新 pod运行正常之
后，再关闭老的 pod。
默认情况下，它可确保启动的  Pod 个数比期望个数最多多出  25%

问题：
结合 ceph rb d共享挂载的特性和 deployment 更新的特性，我们发现原因如下：
由于 deployment 触发更新，为了保证服务的可用性， deployment 要先创建一个 pod
并运行正常之后，再去删除老 pod。而如果新创建的 pod和老 pod不在一个 node，就
会导致此故障。

解决办法：
1，使用能支持跨 node和pod之间挂载的共享存储，例如 cephfs，GlusterFS 等
2，给node添加 label， 只允许 deployment 所管理的 pod调度到一个固定的 node上。
（不建议，这个 node挂掉的话，服务就故障了）

**2.8 基于 storageclass 动态生成 pv**
**1、创建 rbd的供应商 provisioner**

```bash
#把rbd-provisioner.tar.gz 上传到 xianchaonode1 上，手动解压
[root@ xianchaonode1  ~]# docker load -i rbd-provisioner.tar.gz
[root@ xianchaomaster1  ~]# cat rbd -provisioner.yaml
```

```yaml
kind: ClusterRole
apiVersion: rbac.authorizat ion.k8s.io/v1
metadata:

   name: rbd -provisioner
rules:
  - apiGroups: [""]
    resources: ["persistentvolumes"]
    verbs: ["get", "list", "watch", "create", "delete"]
  - apiGroups: [""]
    resources: ["persistentvolumeclaims"]
    verbs: ["get", "list", "watch", "update"]
  - apiGroups: ["storage.k8s.io"]
    resources: ["storageclasses"]
    verbs: ["get", "list", "watch"]
  - apiGroups: [""]
    resources: ["events"]
    verbs: ["creat e", "update", "patch"]
  - apiGroups: [""]
    resources: ["services"]
    resourceNames: ["kube -dns","coredns"]
    verbs: ["list", "get"]
---
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: rbd -provisioner
subjects:
  - kind: ServiceAccount
    name: rbd -provisioner
    namespace: default
roleRef:
  kind: ClusterRole
  name: rbd -provisioner
  apiGroup: rbac.authorization.k8s.io
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: rbd -provisioner
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get"]
- apiGroups: [""]
  resources: ["endpoints"]
  verbs: ["get", "list", "watch", "create", "update", "patch"]
```

 ---

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBi nding
metadata:
  name: rbd -provisioner
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: rbd -provisioner
subjects:
- kind: ServiceAccount
  name: rbd -provisioner
  namespace: default
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rbd -provisioner
spec:
  selector:
    matchLabels:
      app: rbd -provisioner
  replicas: 1
  strategy:
    type: Recreate
  template:
    metadata:
      labels:
        app: rbd -provisioner
    spec:
      containers:
      - name: rbd -provisioner
        image: quay.io/xianchao/external_storage/rbd -provisioner:v1
        imagePullPolicy: IfNotPresent
        env:
        - name: PROVISIONER_NAME
          value: ceph.com/rbd
      serviceAccount: rbd -provisioner
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: rbd -provisioner

```

```bash
[root@ xianchaomaster1  ~]# kubectl apply -f rbd-provisioner.yaml
[root@ xianchaomaster1  ~]# kubectl get pods -l app=rbd -provisioner
NAME                               READY   STATUS    REST ARTS   AGE
rbd-provisioner -685746688f -8mbz5   1/1     Running   0          111s
```

**2、创建 ceph -secret**

```bash
#创建 pool池
[root@master1 -admin ~]# ceph osd pool create k8stest1 56
[root@ xianchaomaster1  ~]# cat ceph -secret -1.yaml
```

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: ceph -secret -1
type: "ceph.com/rbd"
data:
  key: QVFBWk0zeGdZdDlhQXhBQVZsS0poYzlQUlBianBGSWJVbDNBenc9PQ==

```

```bash
[root@ xianchaomaster1  ~]# kubectl apply -f ceph -secret -1.yaml
```

**3、创建 storageclass**

```bash
[root@ xianchaomaster1  ~]# cat storageclass.yaml
```

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: k8s -rbd
provisioner: ceph.com/rbd
parameters:
  monitors: 192.168.40.201:6789
  adminId: admin
  adminSecretName: ceph -secret -1
  pool: k8stest1
  userId: admin
  userSecretName: ceph -secret -1
  fsType: xfs
  imageFormat: "2"
  imageFeatures: "layering"

```

```bash
[root@ xianchaomaster1  ~]# kubectl apply -f storageclass.yaml
```

> **注意:**
k8s1.2 0版本通过 rbd  provisioner 动态生成 pv会报错 :

```bash
[root@ xianchaomaster1  ~]# kubectl logs rbd -provisioner -685746688f -8mbz

 E0418 15:50:09.610071       1 controller.go:1004] provision "default/rbd -pvc" class
"k8s-rbd": unexpected error getting claim reference: selfLink was empty, can't make
```
reference ，报错原因是 1.20版本仅用了 selfLink，解决方法如 下；
编辑/etc/kubernetes/manifests/kube -apiserver.yaml
在这里：

```yaml
spec:
  containers:
  - command:
    - kube -apiserver
```
添加这一行：
- --feature -gates=RemoveSelfLink=false
；：
然后应用它，即可 ：
kubectl apply -f /etc/kubernetes/manifests/kube -apiserver.yaml

```bash
[root@ xianchaomaster1  ~]# kubectl get pods -n kube -system
NAME                                       READY   STATUS
RESTARTS   AGE
kube -apiserver                               0/1     CrashLoopBackOff    1
kube -apiserver -xianchaomaster1                     1/1     Running
0
```
kube -apiserver 状态是 crashloopbackoff ，这个 pod可以删除，因为 kube -apiserver -
xianchaomaster1 是提供服 务的 pod

**4、创建 pvc**

```bash
[root@ xianchaomaster1  ~]# cat rbd -pvc.yaml
```

```yaml
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: rbd -pvc
spec:
  accessModes:
    - ReadWriteOnce
  volumeMode: Filesystem
  resources:
    requests:
      storage: 1Gi
  storageClassNa me: k8s -rbd
```

```bash
[root@ xianchaomaster1  ~]# kubectl apply -f rbd-pvc.yaml
[root@ xianchaomaster1  ~]# kubectl get pvc
```

创建 pod，挂载 pvc

```bash
[root@ xianchaomaster1  ~]# cat pod -sto.yaml
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  labels:
    test: rbd -pod
  name: ceph -rbd-pod
spec:
  containers:
  - name: ceph -rbd-nginx
    image: nginx
    imagePullPolicy: IfNotPresent
    volumeMounts:
    - name: ceph -rbd
      mountPath: /mnt
      readOnly: false
  volumes:
  - name: ceph -rbd
    persistentVolumeClaim:
      claimName: rbd -pvc
```

```bash
[root@ xianchaomaster1  ~]# kubectl apply -f pod -sto.yaml
[root@ xianchaomaster1  ~]# kubectl get pods -l test=rbd -pod
NAME           READY   STATUS    RESTARTS   AGE
ceph -rbd-pod   1/1     Running   0          50s
```

**2.9 k8s挂载 cephfs**

```bash
[root@master1 -admin ~]# ceph fs ls
name: xianchao, metadata pool: cephfs_metadata, data pools: [cephfs_data ]
```

**1、创建ceph子目录**

为了别的地方能挂载 cephfs，先创建一个 secretfile

```bash
[root@master1 -admin ~]# cat /etc/ceph/ceph.client.admin.keyring |grep key|awk -
F" " '{print $3}' > /etc/ceph/admin.secret
```

 挂载 cephfs的根目录到集群的 mon节点下的一个目录， 比如 xianchao_data ， 因为挂载后，
我们就可以直接在 xianchao_data 下面用 Linux命令创建子目录了。

```bash
[root@master1 -admin ~]# mkdir xianchao_data
[root@master1 -admin ~]# mount -t ceph 192.168.40.201:6789:/ /root/xianchao_data
-o name=admin,secretfile=/etc/ceph/admin.secret

[root@master1 -admin ~]# df -h
192.168.40.201:6789:/    165G  106M  165G   1% /root/xianchao_data
```

在cephfs的根目录里面创建了一个子目录 lucky，k8s以后就可以挂载这个目录

```bash
[root@master1 -admin ~]# cd /root/xianchao_data/
[root@master1 -admin xianchao_data]# mkdir lucky
[root@master1 -admin xianchao_data]# chmod 0777 lucky/
```

**2、测试k8s的pod挂载cephfs**
1)创建k8s连接ceph使用的secret
   将/etc/ceph/ceph.client.admin.keyring 里面的key的值转换为
base64，否则会有问题

```bash
[root@master1 -admin xianchao_data]# echo
"AQBvBdZgsDSZKxAAan+5rnsjr2ziA/atqFnQOA==" | base64
QVFCdkJkWmdzRFNaS3hBQWFuKzVybnNqcjJ6aUEvYXRxRm5RT0E9PQo=

[root@xianchaomaster1 ceph]# cat cephfs -secret.yaml
```

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: cephfs -secret
data:
  key: QVFCdkJkWmdzRFNaS3hBQWFuKzVybnNqcjJ6aUEvYXRxRm5RT0E9PQo=

```

```bash
[root@xianchaomaster1 ceph]# kubectl apply -f cephfs -secret.yaml
[root@xianchaomaster1 ceph]# cat cephfs -pv.yaml
```

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: cephfs -pv
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteMany
  cephfs:
    monitors:
      - 192.168.40.201:6789
    path: /lucky
    user: admin
    readOnly: false
    secretRef:
        name: cephfs -secret
  persistentVolumeReclaimPolicy: Recycle
```

```bash
[root@xianchaomaster1 ceph]# kubectl apply -f cephfs -pv.yaml

[root@xianchaomaster1 ceph]# cat cephfs -pvc.yaml

```

```yaml
 kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: cephfs -pvc
spec:
  accessModes:
    - ReadWriteMany
  volumeName: cephfs -pv
  resources:
    requests:
      storage: 1Gi

```

```bash
[root@xianchaomaster1 ceph]# kubectl apply -f cephfs -pvc.yaml

[root@xianchaomaster1 ceph]# kubectl get pvc
NAME          STATUS   VOLUME                             CAPACITY

cephfs-pvc    Bound    cephfs -pv                        1Gi        RWX
```

创建第一个 pod，挂载 cephfs -pvc

```bash
[root@xianchaomaster1 ceph]# cat cephfs -pod-1.yaml
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: cephfs -pod-1
spec:
  containers:
    - image: nginx
      name: nginx
      imagePullPolicy: IfNotPresent
      volumeMounts:
      - name: test -v1
        mountPath: /mnt
  volumes:
  - name: test -v1
    persistentVolumeClaim:
      claimName: cephfs -pvc

```

```bash
[root@xianchaomaster1 ceph]# kubectl apply -f cephfs -pod-1.yaml
```

创建第二个pod，挂载 cephfs -pvc

```bash
[root@xianchaomaster1 ceph]# cat cephfs -pod-2.yaml

```

```yaml
 apiVersion: v1
kind: Pod
metadata:
  name: cephfs -pod-2
spec:
  containers:
    - image: nginx
      name: nginx
      imagePullPolicy: IfNotPresent
      volumeMounts:
      - name: test -v1
        mountPath: /mnt
  volumes:
  - name: test -v1
    persistentVolumeClaim:
      claimName: cephfs -pvc

```

```bash
[root@xianchaomaster1 ceph]# kubectl apply -f cephfs -pod-2.yaml

[root@xianchaomaster1 ceph]# kubectl exec -it cephfs -pod-1 -- /bin/sh
# cd /mnt
# touch hello

[root@xianchaomaster1 ceph]# kubectl exec -it cephfs -pod-2 -- /bin/sh
# cd /mnt
# touch welcome
```

回到 master 1-admin上，可以看到在 cephfs文件目录下已经存在内容了

```bash
[root@master 1-admin lucky]# pwd
/root/xianchao_data/lucky
[root@master1 -admin lucky]# ls
hello  welcome
```


