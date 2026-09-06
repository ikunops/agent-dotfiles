1 Rancher 介绍

**1.1 Rancher 简介**
Rancher 是一个开源的企业级多集群 Kubernetes 管理平台，实现了 Kubernetes 集群在混合云 +本地
数据中心的集中部署与管理，以确保集群的安全性，加速企业数字化转型。

超过40,000家企业每天使用 Rancher 快速创新

Rancher官方文档：
https://docs.rancher.cn/

**1.2 Rancher和k8s的区别**
Rancher 和k8s都是用来作为容器的调度与编排系统。但是 rancher 不仅能够管理应用容器，更重要
的一点是能够管理 k8s集群。Rancher2.x 底层基于 k8s调度引擎，通过 Rancher 的封装，用户可以在不
熟悉k8s概念的情况下轻松的通过 Rancher 来部署容器到 k8s集群当中 。

**1.3 Rancher使用案例**

**1、中保银行**
在使用Rancher 平台之前，中银保险也尝试过使用原生的一些 Kubernetes 平台，但是这些平台学习
使用成本高昂、运行维护特别复杂。尤其是当我公司使用多种混合云环境的时候， 一个个Kubernetes 集
群就变成了一个个技术孤岛，反而加重了公司信息化转型的压力。 Rancher 平台的采用有效地解决了之前
平台使用中所存在的问题，提升我公司测试业务平台的运行维护效率。
—— 付春涛 中银保险有限公司  信息科技部  技术负责人

**2、蔚来汽车数字运营中国**
Rancher 友好的图形化管理界面和资源创建的易用性、多集群管理能力、 AD认证和权限管理集成、应
用商店功能等各种能力，帮助我们简化了容器化应用的部署，得以方便地进行多云 Kubernetes 管理和权
限控制，提高了应用交付的效率。感谢 Rancher 团队，期待 Rancher 中国团队进一步优化功能，推进
Rancher 在国内的大量落地。
—— 赵鹏飞 蔚来汽车数字运营中国  运维开发工程师

**3、上汽集团**
Rancher 2.x 是数据中心级别的管理平台，拥有多云管理的能力，符合未来企业上云的架构规划演
进；Rancher 的开源产品模式降低了技术人员的使用成本，在兼顾原生 Kubernetes 的同时，为开发人员
提供了丰富的 API与系统功能，提高了开发生产效率。同时， Rancher 专业的容器产品团队，架起了开源
产品与生产业务的桥梁，在微服务、应用容器化、 DevOps、业务上云等技术领域为上汽集团提供了可靠的
支持。
—— 龚瀚申 上汽集团  PaaS平台总监

2安装rancher
**2.1 初始化实验环境**
安装rancher 需要的实验环境如下：
环境说明（ centos7. 6）：
IP                 主机名                 内存    cpu
**192.168.40.138 xianchaorancher        6G    6vCPU**

 已经存在的 K8s实验环境：
角色            ip                     主机名
控制节点        192.168.40.180         xianchaomaster 1
工作节点        192.168.40.181         xianchaonode 1

配置主机名：
在192.168.40.138 上执行如下：
hostnamectl set -hostname xianchaorancher

配置hosts文件：
#在xianchaomaster 1、xianchaonode 1、xianchaorancher 上操作：
**1. 192.168.40.180   xianchaomaster1**
**2. 192.168.40.181   xianchaonode1**
**3. 192.168.40.138   xianchaorancher**

配置rancher 到k8s主机互信
生成ssh 密钥对

```bash
[root@xianchaorancher  ~]# ssh-keygen  # 一路回车，不输入密码
```
把本地的 ssh公钥文件安装到远程主机对应的账户

```bash
[root@xianchaorancher  ~]# ssh-copy-id xianchaomaster1
[root@xianchaorancher  ~]# ssh-copy-id xianchaorancher
[root@xianchaorancher  ~]# ssh-copy-id xianchaonode1
```

关闭防火墙

```bash
[root@xianchaor ancher ~]# systemctl stop firewalld ; systemctl disable firewalld
```

关闭selinux

```bash
[root@xianchaorancher  ~]# setenforce 0
[root@xianchaorancher  ~]# sed -i 's/SELINUX=enforcing/SELINUX=disabled/g'
/etc/selinux/config
```

> **注意：修改 selinux 配置文件之后，重启机器， selinux 才能永久生效**

关闭swap分区。

```bash
[root@xianchaorancher  ~]# swapoff -a
[root@xianchaorancher  ~]# free -m  #可以看到 swap分区的大小，已经变为 0

              total        used        free      shared  buff/cache   available
Mem:           4876         501         516          20        3858        4068
Swap:             0           0           0 ‘
```

永久关闭：注释 swap挂载

> **注：如果是克隆主机请删除网卡中的 UUID并重启网络服务。**

内核参数修改： br_netfilter 模块用于将桥接流量转发至 iptables 链，br_netfilter 内核参数需要
开启转发。

```bash
[root@xianchaorancher  ~]# modprobe br_netfilter
[root@xianchaorancher  ~]# echo "modprobe br_netfilter" >> /etc/profile
[root@xianchaorancher  ~]# cat > /etc/sysctl.d/k8s.conf <<EOF
net.bridge.bridge -nf-call-ip6tables = 1
net.bridge.bridge -nf-call-iptables = 1
net.ipv4.ip_forward = 1
EOF
[root@xianchaorancher  ~]# sysctl -p /etc/sysctl.d/k8s.conf
```

在xianchaorancher 上配置阿里云镜像源：

```bash
[root@xianchaorancher ~]# mv /etc/yum.repos.d/CentOS -Base.repo  /etc/yum.repos.d/CentOS -
Base.repo.backup
[root@xianchaorancher ~]# wget -O /etc/yum.repos.d/CentOS -Base.repo
http://mirrors.aliyun.com/repo/Centos -7.repo

#配置国内阿里云 docker的repo源
[root@xianchaorancher  ~]# yum-config-manager --add-repo
http://mirrors.aliyun.com/docker -ce/linux/centos/docker -ce.repo
```

在xianchaorancher 上安装docker-ce。我们已经配置了 docker本地源，直接安装 docker-ce服
务。

```bash
[root@xianchaorancher  ~]# yum install -y yum-utils device -mapper-persistent -data lvm2
wget net -tools nfs -utils lrzsz gcc gcc -c++ make cmake libxml2 -devel openssl -devel curl curl -
devel unzip sudo ntp  libaio-devel wget vim ncurses -devel autoconf automake zlib-
devel  python-devel epel -release openssh -server socat   ipvsadm conntrack ntpdate
```

安装docker-ce

```bash
[root@xianchaorancher  ~]# yum install docker -ce docker -ce-cli containerd.io -y
[root@xianchaomaster1  ~]# systemctl start docker && systemctl enable docker.s ervice
```

修改docker配置文件，配置镜像加速器

```bash
[root@xianchaorancher  ~]# tee /etc/docker/daemon.json <<  'EOF'
{
"registry -mirrors":["https://rsbud4vc.mirror.aliyuncs.com","https://registry.docker -
cn.com","https://docker.mirrors.ustc.edu.cn","https://dockerhub.azk8s.cn","ht tp://hub -
mirror.c.163.com"," http://qtid6917.mirror.aliyuncs.com ",
"https://rncxm540.mirror.aliyuncs.com"],
"exec-opts": ["native.cgroupdriver=systemd"]
}
EOF
[root@xianchaorancher  ~]# systemctl daemon -reload
[root@xianchaorancher  ~]# systemctl restart docker
[root@xianchaorancher  ~]# systemctl status docker
```

显示如下，说明 docker安装成功了
● docker.service - Docker Application Container Engine
   Loaded: loaded (/usr/lib/systemd/system/docker.s ervice; enabled; vendor preset:
disabled)
   Active: active ( running) since Wed 2021 -03-17 12:39:06 CST

**2.2 安装Rancher**

Rancher2.5.7支持导入已经存在的 k8s1.20.6集群，所以我们安装 rancher2.5.7版本，

> **注：rancher-2-5-7.tar.gz 压缩包在课件**
在xianchaorancher 上操作如下命令：

```bash
[root@xianchaonode1  ~]# ntpdate cn.pool.ntp.org
[root@xianchaorancher  ~]# docker  load -i rancher -2-5-7.tar.gz
[root@xianchaorancher  ~]# docker run -d --restart=unless -stopped -p 80:80 -p 443:443 --
privileged rancher/rancher:v2.5.7
```

> **注：unless-stopped，在容器退出时总是重启容器，但是不考虑在 Docker守护进程启动时就已经停**
止了的容器

验证rancher 是否启动：

```bash
[root@xianchaorancher  ~]# docker ps | grep rancher
```

显示如下，说明启动成功：
f9321083e186   rancher/rancher:v2.5.7   "entrypoint.sh"   About a minute ago   Up About
a minute   0.0.0.0:80 ->80/tcp, 0.0.0.0:443 ->443/tcp   loving_johnson

**2.3 登录Rancher 平台**
在浏览器访问 xianchaorancher 的ip地址：

选择高级
‘接受风险并继续

如果大家用英文不方面，可以把页面字体变成中文，方法如下：

变成如下中文界面：

 3  通过Rancher 管理已存在的 k8s集群

选择添加集群，出现如下：

选择导入，出现如下 :

在k8s控制节点 xianchaomaster1 上执行上面箭头所指的命令

```bash
[root@xianchaomaster1 ~]#  curl --insecure -sfL
https://192.168.40.138/v3/import/r8hkzptfbvw4cbcx69bp25p8dcgs4cfdhmlrwxf8d5znrvsmt7tw6h_c -
5xw59.yaml | kubectl apply -f -

#出现如下：

#再执行一次：
[root@xianchaomaster1 ~]#  curl --insecure -sfL
https://192.168.40.138/v3/import/r8hkzptfbvw4cbcx69bp25p8dcgs4cfdhmlrwxf8d5znrvsmt7tw6h_c -
5xw59.yaml | kubectl apply -f –
```

执行完上面命令后，再点击上面的完成，出现如下：

显示pending 状态

在k8s的控制节点和工作节点执行如下 :

docker load -i rancher-agent-2-5-7.tar.gz

在回到主页面可以看到 rancher 已经成功导入 k8s1.20.6版本了

一会状态就变成 running 了

4  通过Rancher 部署监控系统
**4.1 启用Rancher 集群级别监控**

```bash
#把prometheus -grafana.tar.gz 镜像压缩包上传到 xianchaonode 1机器上，手动解压
[root@xianchaonode 1~]# docker load -i prometheus -grafana.tar.gz
#在开启监控的时候默认会拉取一些镜像，速度较慢，所以大家先把安装监控需要的镜像解压
```
启动监控时间可能比较长，需要等 10-20分钟
在rancher 主页面，点击集群名称 xianchao -test

启动监控并查看实时监控指标

#监控组件版本选择 0.2.1

其他的默认就可以了，点最后：启用监控

点：集群

显示监控API未就绪，需要等待 10-20分钟，才能就绪

在这个里可以查看 监控的安装过程：

具体事件 信息如下：

过10-20分钟后，监控 API已经就绪了，那就 刷新当前页面，监控部署完成后就可以看到我们的监控信息
了。

点开集群监控 -选择Grafana

#出现如下：

**4.2 查看Grafana 监控**
在https://192.168.40.138/c/c -5xw59/monitoring 页面可以看到所有监控项：

我们可以点击每个项目上的 Grafana 图标即可跳转到 Grafana监控页面 。
选择集群监控→点击右侧 Grafana图标

跳转到如下：

Kubernetes 组件监控 —点击右侧 Grafana

跳转到如下：

跳转到如下界面：

5 通过Rncher仪表盘管理 k8s集群：部署tomcat服务

```bash
#把tomcat.tar.gz 镜像压缩包上传到 xianchaonode 1节点，手动解压 :
[root@xianchaonode1 ~]# docker load -i tomcat.tar.gz
```
**1、创建名称空间 namespace**
打开rancher 主页面，点击仪表盘

#出现如下：

把Namespace 名称写上，其他默认即可，点击创建

**2、创建Deployment 资源**

添加标签

容器配置
#指定镜像

#給pod打上标签

容器配置完成，点击创建

查看资源是否创建成功：

查看tomcat详细信息

**3、创建Service 资源，把 k8s集群内部的 tomcat暴露出来**

选择节点端口
#定义服务端口

#定义选择器

创建
查看service 是否创建成功

通过上面可以看到已经创建了 tomat-service



