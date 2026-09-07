---
name: k8s-knowledge
description: K8S（Kubernetes）运维知识库，涵盖 Docker、Pod、控制器、网络、存储、安全、集群搭建、监控、CI/CD、Istio 等 36 个专题。当用户询问 K8S 相关问题时使用此知识库检索答案。
---

# K8S 运维知识库

韩先超 K8S 课程整理，覆盖 36 个专题。

## 使用方法

1. 用户提出 K8S 相关问题时，先看 `INDEX.md` 快速定位专题
2. 用 `grep` 或 `read` 搜索 `docs/` 目录下的具体文件
3. 根据文档内容回答用户问题，引用具体文件路径

## 目录结构

```
docs/
├── 01-课程笔记总结.md     ← 课程总览
├── 02-学习路线图.md        ← 13 阶段学习路线（索引）
├── 03-思维导图.md          ← 全课程脑图
├── 01-Docker容器基础.md
├── 02-Pod入门与实战.md
├── 03-kubectl命令行工具.md
├── 04-Pod启动探测.md
├── 05-临时容器.md
├── 06-ReplicaSet和Deployment控制器.md
├── 07-StatefulSet控制器.md
├── 08-DaemonSet控制器.md
├── 09-Service负载均衡.md
├── 10-CNI网络插件.md
├── 11-kube-proxy IPVS模式.md
├── 12-IngressController高可用.md
├── 13-Ingress灰度发布.md
├── 14-ConfigMap配置管理.md
├── 15-Secret配置管理.md
├── 16-持久化存储PV-PVC.md
├── 17-Ceph分布式存储.md
├── 18-RBAC安全机制.md
├── 19-kubeadm单master集群搭建.md
├── 20-kubeadm多master高可用集群.md
├── 21-kubeadm快速初始化集群.md
├── 22-kubeadm初始化1.23版-containerd.md
├── 23-kubeadm安装1.24高可用集群.md
├── 24-二进制安装多master集群.md
├── 25-Rancher管理k8s集群.md
├── 26-K3s轻量级k8s.md
├── 27-Helm包管理工具.md
├── 28-HPA-VPA自动扩缩容.md
├── 29-CRD自定义资源.md
├── 30-SpringCloud电商项目实战.md
├── 31-Prometheus+Grafana监控系统.md
├── 32-日志收集平台.md
├── 33-全链路监控.md
├── 34-Jenkins+DevOps容器云平台.md
├── 35-Tekton原生CI-CD.md
└── 36-Istio服务网格.md
```
