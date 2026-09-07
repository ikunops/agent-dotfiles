**1、修改 iptables 变成 ipvs 模式**

  ipvs 采用的 hash 表，iptables 采用一条条的规则列表。集群数量越多 iptables 规则就越多，而
iptables 规则是从上到下匹配，所以效率就越是低下。因此当 service 数量达到一定规模时， hash 查表
的速度优势就会显现出来，从而提高 service 的服务性能

**1、使用 ipvs 代替 iptables**

```bash
[root@xianchaomaster1 ~]# yum install -y ipset  ipvsadm
[root@xianchaonode1 ~]# yum install -y ipset  ipvsadm
[root@xianchaonode 2~]# yum install -y ipset ipvsadm
[root@xianchaomaster1 ~]# cat << 'EOF' > /etc/sysconfig/modules/ipvs.modules
#!/bin/bash
ipvs_modules=(ip_vs ip_vs_lc ip_vs_wlc ip_vs_rr ip_vs_wrr ip_vs_lblc ip_vs_lblcr ip_vs_dh
ip_vs_sh ip_vs_fo ip_vs_nq ip_vs_sed ip_vs_ftp nf_conntrack_ipv4)
for kernel_module in ${ipvs_modules[*]}; do
/sbin/modinfo -F filename ${kernel_module} > /dev/null 2>&1
if [ $? -eq 0 ]; then
/sbin/modprobe ${kernel_module}
fi
done
EOF

[root@xianchaomaster1 ~]# chmod +x /etc/sysconfig/modules/ipvs.modules

[root@xianchaomaster1 ~]#  /etc/sysconfig/modules/ipvs.modules

[root@ xianchaonode 1~]#  yum install -y ipset ipvsadm

 [root@ xianchaonode 1~]#cat << 'EOF' > /etc/sysconfig/modules/ipvs.modules
#!/bin/bash
ipvs_mo dules=(ip_vs ip_vs_lc ip_vs_wlc ip_vs_rr ip_vs_wrr ip_vs_lblc ip_vs_lblcr ip_vs_dh
ip_vs_sh ip_vs_fo ip_vs_nq ip_vs_sed ip_vs_ftp nf_conntrack_ipv4)
for kernel_module in ${ipvs_modules[*]}; do
/sbin/modinfo -F filename ${kernel_module} > /dev/null 2>&1
if [ $? -eq 0 ]; then
/sbin/modprobe ${kernel_module}
fi
done
EOF

[root@  xianchaonode 1 ~]# chmod +x /etc/sysconfig/modules/ipvs.modules

[root@  xianchaonode 1~]# /etc/sysconfig/modules/ipvs.modules

[root@ xianchaonode 2~]# yum install -y ipset ipvsadm

[root@ xianchaonode 2~]#cat << 'EOF' > /etc/sysconfig/modules/ipvs.modules
#!/bin/bash
ipvs_modules=(ip_vs ip_vs_lc ip_vs_wlc ip_vs_rr ip_vs_wrr ip_vs_lblc ip_vs_lblcr ip_vs_dh
ip_vs_sh ip_vs_fo ip_vs_nq ip_vs_sed ip_vs_ftp nf_conntrack_ipv4)
for kernel_modu le in ${ipvs_modules[*]}; do
/sbin/modinfo -F filename ${kernel_module} > /dev/null 2>&1
if [ $? -eq 0 ]; then
/sbin/modprobe ${kernel_module}
fi
done
EOF

[root@  xianchaonode 2 ~]# chmod +x /etc/sysconfig/modules/ipvs.modules

[root@  xianchaonode 2~]# /etc/sysconfig/modules/ipvs.modules

[root@xianchaomaster1 ~]#  kubectl -n kube -system edit cm kube -proxy
......
mode: "ipvs"
......

[root@xianchaomaster1 ~]#  kubectl -n kube -system get pod -l k8s -app=kube -proxy |
grep -v 'NAME' | awk '{print $1}' | xargs kubectl -n kube -system delete pod

 [root@xianchaomaster1 ~]#  iptables -t filter -F; iptables -t filter -X; iptables -t nat -F;
iptables -t nat -X;

[root@  xianchaonode 1~]# iptables -t filter -F; iptables -t filter -X; iptables -t nat -F;
iptables -t nat -X;
[root@xianchaonode2 ~]#  iptables -t filter -F; iptables -t filter -X; iptables -t nat -F;
iptables -t nat -X;
```

修改 ipvs 模式之后 过5-10分钟测试在 k8s创建 pod 是否可以正常访问网络

```bash
[root@xianchaomaster1 ~]#  kubectl run busybox --image busybox:1.28 --
restart=Never --rm -it busy box -- sh
/ # ping www.baidu.com
PING www.baidu.com (39.156.66.18): 56 data bytes
64 bytes from 110.242.68.4: seq=0 ttl=127 time=37.319 ms
#通过上面可以看到能访问网络
/# exit
```

测试 dns是否正常

```bash
[root@xianchaomaster1 ~]#  kubectl run busybox --image busybox:1.28 --
restart=Never --rm -it busybox -- sh

/ # nslookup kubernetes.default.svc.cluster.local
Server:    10.96.0.10
Address 1: 10.96.0.10 kube -dns.kube -system.svc.cluster.local

Name:      kubernetes.default.svc.cluster.local
Address 1: 10.96.0.1 kubernetes.default.svc.cluster.local
```

看到上面内容，说明 k8s的dns解析正常


