# K8S 知识库索引

> 使用: 先按分类定位专题文件, 再到 `docs/<文件名>` 查具体内容(每行末尾列出该文档的正文小节)。

## 课程总览

| 文件 | 专题 | 正文小节 |
|------|------|----------|
| `01-课程笔记总结.md` | 课程整体笔记总结 |  |
| `02-学习路线图.md` | 13 阶段学习路线 |  |
| `03-思维导图.md` | 全课程思维导图（XMind 可导入） |  |

## 基础篇

| 文件 | 专题 | 正文小节 |
|------|------|----------|
| `01-Docker容器基础.md` | Docker 概念、架构、安装、镜像、Dockerfile、Volume、网络模式 | 1 docker是什么 ; 2 docker的优点 ; 3 docker缺点 ; 4 安装Docker ; 5 开启包转发功能和修改内核参数 ; 6 配置docker镜像加速器 ; 7 docker的基本用法 ; 7.1 镜像相关操作 ; 7.2 容器相关操作 ; 7.2.1 以交互式方式 启动并进入容器 |
| `02-Pod入门与实战.md` | Pod 定义、生命周期、重启策略、Init 容器、Sidecar | 1.1 Pod是什么 ; 1.1.1 Pod如何管理多个容器 ; 1.1.2 Pod 网络 ; 1.1.3 Pod 存储 ; 1.2 Pod工作方式 ; 1.2.1 自主式Pod ; 1.2.2 控制器管理的 Pod ; 2.1 资源清单YAML文件书写技巧 ; 2.2 通过资源清单文件创建第一个 Pod ; 2.3 通过kubectl run创建Pod |
| `03-kubectl命令行工具.md` | kubectl 语法、常用命令、输出格式 |  |
| `04-Pod启动探测.md` | livenessProbe、readinessProbe、startupProbe | 2 为什么要用 startupProbe ; 3 什么时候会用 startupProbe 呢 |
| `05-临时容器.md` | kubectl debug、临时容器调试 | 1.1 什么是临时容器 ; 1.2 临时容器的用途 ; 1.3 开启特性支持临时容器 ; 2 使用临时容器 ; 3 kubectl raw更新临时容器 |

## 控制器篇

| 文件 | 专题 | 正文小节 |
|------|------|----------|
| `06-ReplicaSet和Deployment控制器.md` | ReplicaSet 副本控制、Deployment 滚动更新/回滚 | 1 Replicaset 控制器：概念、原理解读 ; 1.1 Replicaset 概述 ; 1.2 Replicaset 工作原理：如何管理 Pod ; 2 Replicaset 资源清单文件编写技巧 ; 3 Replicaset 使用案例：部署 Guestbook 留言板 ; 4 Replicaset 管理pod：扩容、缩容、更新 ; 5 Deployment 控制器：概念、原理解读 ; 5.1 Deployment 概述 ; 5.2 Deployment 工作原理：如何管理 rs和Pod ; 1 创建ReplicaSet 和Pod |
| `07-StatefulSet控制器.md` | 有状态服务、稳定网络标识、有序启停 | 1.1 Statefulset 控制器 ：概念、原理解读 ; 1.2 Statefulset 资源清单 文件编写技巧 ; 1.3 Statefulset 使用案例 ：部署 web 站点 ; 1.4 Statefulset 管理 pod：扩容、缩容、更新 |
| `08-DaemonSet控制器.md` | 每个 Node 一个 Pod、日志收集、监控 | 1.1 DaemonSet 概述 ; 1.2 DaemonSet 工作原理 ：如何管理 Pod ; 1.3 Daemonset 典型的应用 场景 ; 1.4 DaemonSet 与 Deployment 的区别 |

## 网络篇

| 文件 | 专题 | 正文小节 |
|------|------|----------|
| `09-Service负载均衡.md` | ClusterIP/NodePort/LB/ExternalName、CoreDNS | 1.1 四层负载均衡 Service：概念、原理解读 ; 1.1.1 为什么要有 Service ; 1.1.2 Service 概述 ; 1.1.3 Service 工作原理 ; 1.1.4 kubernetes 集群中有三类 IP地址 ; 1.2 创建Service 资源 ; 1.2.1 Service 的四种类型 ; 1.2.2 Service 的端口 ; 1.4 创建Service：type类型是ClusterIP ; 1 创建Pod |
| `10-CNI网络插件.md` | Flannel/Calico/Canal 部署与切换 |  |
| `11-kube-proxy IPVS模式.md` | iptables vs ipvs、性能优化 | 1 使用 ipvs 代替 iptables |
| `12-IngressController高可用.md` | Ingress Controller 安装、高可用部署 | 1 Ingress -controller 高可用 ; 3 keepalive 配置 ; 5 测试 vip是否绑定成功 ; 10.3.2 测试 Ingress HTTP 代理 k8s内部站点 ; 2 编写 ingress 规则 ; 10.3.3 同一个 k8s搭建多套 Ingress -controller |
| `13-Ingress灰度发布.md` | header/cookie/weight 灰度策略 | 1.2 通过 Ingress -nginx 实现灰度发布 |

## 配置与存储篇

| 文件 | 专题 | 正文小节 |
|------|------|----------|
| `14-ConfigMap配置管理.md` | ConfigMap 创建、挂载、热更新 | 1.1 Configmap 概述 ; 1.1.1 什么是Configmap ; 1.1.2 Configmap 能解决哪些问题 ; 4 在容器看来，配置文件就像是打包在容器内部特定目录，整个过程对应用没有任何 ; 1.1.3 Configmap 应用场景 ; 2 使用微服务架构的话，存在多个服务共用配置的情况，如果每个服务中单独一份配 ; 1.2 Configmap 创建方法 ; 1.2.1 命令行直接创建 ; 1.2.2 通过文件创建 ; 1.2.3 指定目录创建 configmap |
| `15-Secret配置管理.md` | Secret 类型、创建、挂载 | 1.1 Secret是什么 ; 1.2 使用Secret ; 1 通过环境变量引入 Secret ; 2 通过volume挂载Secret |
| `16-持久化存储PV-PVC.md` | PV/PVC/StorageClass、动态供给 | 1 k8s持久化存储 ：emptyDir ; 2 在容器中要使用 volumemounts 挂载对应的存储 ; 2 k8s持久化存储： hostPath ; 3 k8s持久化存储： nfs ; 1 搭建nfs服务 ; 4 k8s持久化存储：  PVC ; 4.1.1 k8s PV是什么 ; 4.1.2 k8s PVC是什么 ; 4.1.3 k8s PVC和PV工作原理 ; 1 Retain |
| `17-Ceph分布式存储.md` | Ceph 部署、RBD、CephFS | 4 配置互信 ; 5 关闭防火墙 ; 6 关闭 selinux ; 7 配置 Ceph安装源 ; 8 安装 iptables ; 9 配置时间同步 ; 10 安装基础软件包 ; 2 安装ceph集群 ; 2.1 安装 ceph -deploy ; 2.2 创建 monitor 节点 |

## 安全篇

| 文件 | 专题 | 正文小节 |
|------|------|----------|
| `18-RBAC安全机制.md` | Role/ClusterRole/RoleBinding/ServiceAccount | 2 kubeconfig 文件 ; 1.3 准入控制 ; 2 ServiceAccount 介绍 ; 3 RBAC认证授权策略 ; 3.1 Role ：角色 ; 3 resourceNames: 指定 resource 的名称 ; 3.2 ClusterRole ：集群角色 ; 1 集群范围的资源，例如 Node ; 2 非资源型的路径，例如： /healthz ; 3 包含全部命名空间的资源，例如 Pods |

## 集群搭建篇

| 文件 | 专题 | 正文小节 |
|------|------|----------|
| `19-kubeadm单master集群搭建.md` | kubeadm 单节点部署 | 1 初始化安装k8s集群的实验环境 ; 1.1 修改机器 IP，变成静态 IP ; 1.2 配置机器主机名 ; 1.3 配置主机hosts文件，相互之间通过主机名 互相访问 ; 1.4 配置主机之间无密码登录 ; 1.5 关闭交换分区 swap，提升性能 ; 1.6 修改机器内核参数 ; 1.7 关闭firewalld 防火墙 ; 1.7 关闭selinux ; 1.8 配置阿里云 的repo源 |
| `20-kubeadm多master高可用集群.md` | 多 master + keepalived + haproxy | 1 初始化安装k8s集群的实验环境 ; 1.1 修改机器 IP，变成静态 IP ; 1.2 配置机器主机名 ; 1.3 配置主机hosts文件，相互之间通过主机名 互相访问 ; 1.4 配置主机之间无密码登录 ; 1.5 关闭交换分区 swap，提升性能 ; 1.6 修改机器内核参数 ; 1.7 关闭firewalld 防火墙 ; 1.7 关闭selinux ; 1.8 配置阿里云 的repo源 |
| `21-kubeadm快速初始化集群.md` | 快速部署脚本 | 1 kubeadm 和二进制安装 k8s区别 ; 2 初始化安装 k8s的实验环境 ; 3 安装containerd 服务 ; 4 kubeadm 指定containerd 初始化K8s集群 ; 5 配置kube-proxy使用ipvs ; 6 扩容k8s集群-添加work节点 ; 7 安装网络插件 calico ; 8 测试k8s创建pod网络是否正常 ; 9 测试k8s部署tomcat服务 ; 10 测试k8s集群内部 dns解析是否正常 |
| `22-kubeadm初始化1.23版-containerd.md` | containerd 运行时、1.23 版本 | 1 kubeadm 和二进制安装 k8s区别 ; 2 初始化安装 k8s的实验环境 ; 3 安装containerd 服务 ; 4 kubeadm 指定containerd 初始化K8s集群 ; 5 配置kube-proxy使用ipvs ; 6 扩容k8s集群-添加work节点 ; 7 安装网络插件 calico ; 8 测试k8s创建pod网络是否正常 ; 9 测试k8s部署tomcat服务 ; 10 测试k8s集群内部 dns解析是否正常 |
| `23-kubeadm安装1.24高可用集群.md` | 1.24 版本新特性、高可用 | 1 初始化安装k8s集群的实验环境 ; 1.1 修改机器 IP，变成静态 IP ; 1.2 配置机器主机名 ; 1.3 配置主机hosts文件，相互之间通过主机名 互相访问 ; 1.4 配置主机之间无密码登录 ; 1.5 关闭交换分区 swap，提升性能 ; 1.6 修改机器内核参数 ; 1.7 关闭firewalld 防火墙 ; 1.8 关闭selinux ; 1.9 配置阿里云 的repo源 |
| `24-二进制安装多master集群.md` | 二进制手动部署、证书签发 | 1.1 配置静态 IP ; 1.2 配置主机名 ; 1.3 配置hosts文件 ; 1.11 安装iptables ; 1.12 开启ipvs ; 2.1 配置etcd工作目录 ; 2.2 安装签发证书工具 cfssl ; 2.3 配置ca证书 ; 2.4 生成etcd证书 ; 2.5 部署etcd集群 |
| `25-Rancher管理k8s集群.md` | Rancher 部署、集群管理 | 1.1 Rancher 简介 ; 1.2 Rancher和k8s的区别 ; 1.3 Rancher使用案例 ; 1 中保银行 ; 2 蔚来汽车数字运营中国 ; 3 上汽集团 ; 2.1 初始化实验环境 ; 2.2 安装Rancher ; 2.3 登录Rancher 平台 ; 4.1 启用Rancher 集群级别监控 |
| `26-K3s轻量级k8s.md` | K3s 安装、边缘场景 | 1.1 什么是k3s ; 1.1.1 CNCF介绍 ; 2 帮助云原生技术开发人员快速地构建出色的产品 。 ; 1.1.2 什么是发行版 ; 1.1.3 边缘计算介绍 ; 1.1.4 边缘计算应用场景 ; 1.2 为什么叫做 k3s ; 1 边缘计算 -Edge ; 2 物联网-IoT ; 3 CI：持续集成 |

## 运维与扩展篇

| 文件 | 专题 | 正文小节 |
|------|------|----------|
| `27-Helm包管理工具.md` | Helm chart、模板、仓库 | 1 Helm介绍 ; 2 Helm v3版本变化 ; 1 Helm服务端Tiller被删除 ; 2 Release 名称可以在不同命名空间重用 ; 3 支持将 Chart推送至Docker镜像仓库中 ; 4 使用JSONSchema 验证chartvalues ; 3 安装Helm v3 ; 4 配置国内 存放chart仓库的地址 ; 5 Helm基本使用 ; 5.1 搜索和下载 Chart |
| `28-HPA-VPA自动扩缩容.md` | HPA/VPA/metrics-server | 1 自动（弹性） 扩缩容背景分析 ; 2 k8s中自动伸缩的方案 ; 1 根据并发请求数实现自动扩缩容 ; 2 设置扩缩容边界实现自动扩缩容 ; 3 利用 HPA基于 CPU指标实现 pod自动扩缩容 ; 3.1 HPA工作原理 ; 1 Metrics server 是K8S 集群资源使用情况的聚合器 ; 1 创建 HPA 资源，设定目标 CPU 使用率限额，以及最大、最小实例数 ; 3 读取 HPA 中设定的 CPU 使用限额 ; 4 计算：平均值之和 /限额，求出目标调整的实例个数 |
| `29-CRD自定义资源.md` | CRD、Operator、controller-runtime | 3.9 自定义 CRD 资源 ; 3.9.2 创建自定义资源的对象 ; 3 安装 operator |

## 实战与监控篇

| 文件 | 专题 | 正文小节 |
|------|------|----------|
| `30-SpringCloud电商项目实战.md` | SpringCloud 微服务上 K8s | 1.1 配置静态 ip ; 1.1.1 配置静态 ip ; 1.2 修改 yum 源 ; 1.2.1 备份原来的 yum 源 ; 1.2.2 下载阿里的 yum 源 ; 1.2.3 配置安装 k8s需要的 yum 源 ; 1.2.4 清理 yum 缓存 ; 1.2.5 生成新的 yum 缓存 ; 1.2.6 更新 yum 源 ; 1.2.7 安装软件包 |
| `31-Prometheus+Grafana监控系统.md` | Prometheus 部署、Grafana 面板 | 1 Prometheus 介绍 ; 2 Prometheus 特点 ; 3 Prometheus 组件介绍 ; 4 Prometheus 工作流程 ; 4 Prometheus 和zabbix对比分析 ; 5 Prometheus 的几种部署模式 ; 5.1 基本高可用 模式 ; 5.2 基本高可用 +远程存储 ; 5.3 基本HA + 远程存储  + 联邦集群方案 ; 6 Prometheus 的四种数据类型 |
| `32-日志收集平台.md` | EFK/ELK、Filebeat、Logstash | 1 日志对我们来说到底重不重要 ; 2 常见的日志收集方案 ; 2.2 ELK Stack ; 2.3 ELK+filebeat ; 2.4 其他方案 ; 2 elasticsearch 组件介绍 ; 3 filebeat 组件介绍 ; 3.1 filebeat 和beat 关系 ; 1 Packetbeat ：网络数据（收集网络流量数据） ; 3 Filebeat ：日志文件（收集文件数据） |
| `33-全链路监控.md` | Jaeger、SkyWalking、链路追踪 | 4.1 zipkin ; 4.2 skywalking ; 4.3 p inpoint ; 5.1 全面的调用链路数据分析 ; 5.2 Pinpoint 与Zipkin细化比较 ; 5.2.1 pinpoint 与zipkin差异性 ; 5.2.2 pinpoint 与zipkin相似性 ; 1.1 配置静态 ip ; 1.2 修改yum源 ; 1.3 配置防火墙 |
| `34-Jenkins+DevOps容器云平台.md` | Jenkins pipeline、GitOps | 1.1 传统方式部署项目为什么发布慢，效率低 ; 1.2 上线一个功能，有多少时间被浪费了 ; 1.3 如何解决发布慢，效率低的问题呢 ; 1.5 什么是DevOps ; 1.5.1 敏捷开发 ; 1.5.2 持续集成（ CI） ; 1.5.3 持续交付 ; 1.5.4 持续部署 ; 2.2 DevOps在金融行业的应用 -张安全分享 ; 2.3 哪些企业在用 DevOps |
| `35-Tekton原生CI-CD.md` | Tekton pipeline、task、trigger | 3.3 什么是 Tekton ; 3.4 为什么要用 k8s原生的 CI-CD工具 Tekton ; 3.5 使用 Tekton 自动化发布应用流程 ; 3.6 安装 Tekton ; 3.7 Tekton 概念 ; 3.8 测试 Tekton 构建 CI/CD 流水线 ; 3.8.1 clone 应用程序代码进行测试，创建一个 task 任务 ; 3.8.2 创建 pipelineresource 资源对象 ; 3.8.3 创建 taskrun 任务 ; 3.9 自定义 CRD 资源 |
| `36-Istio服务网格.md` | Istio 安装、流量管理、安全、可观测性 | 1.1 Istio是什么 ; 2 安全加固（ Secure） ：自动为服务之间的调用提供认证、授权和加密。 ; 1.1.1 服务注册和发现 ; 1.1.2 负载均衡 ; 1.1.3 故障恢复 ; 1.1.4 服务度量 ; 1.1.5 灰度发布 ; 1.2 Istio核心特性 ; 1 流控(traffic management) ; 2 安全(security) |
