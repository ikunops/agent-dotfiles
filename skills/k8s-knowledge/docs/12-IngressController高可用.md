
**1、Ingress -controller 高可用**

Ingress Controller 是集群流量的接入层，对它做 高可用 非常重要 ，可以基于 keepalive 实现
nginx -ingress -controller 高可用，具体实现如下：
Ingress -controller 根据 Deployment + nodeSeletor +pod 反亲和性 方式部署在 k8s指定的两个
work 节点， nginx -ingress -controller 这个 pod 共享宿主机 ip，然后通过 keepalive +lvs实现
nginx -ingress -controller 高可用

参考： https://github.com/kubernetes/ingress -nginx

https://github.com/kubernetes/ingress -
nginx/tree/main/deploy/static/provider/baremetal

```bash
 [root@ xianchaomaster1 ]# kubectl label node xianchaonode1
kubernetes.io/ingres s=nginx
[root@ xianchaomaster1 ]# kubectl label node xianchaonode2
kubernetes.io/ingress=nginx
[root@ xianchaonode1  ~]# docker load -i ingress -nginx -controllerv1.1.0.tar.gz
[root@ xianchaonode1  ~]# docker load -i kube -webhook -certgen -v1.1.0.tar.gz

[root@ xianchaonode2  ~]# docker load -i ingress -nginx -controllerv1.1.0.tar.gz
[root@ xianchaonode2  ~]# docker load -i kube -webhook -certgen -v1.1.0.tar.gz

[root@ xianchaomaster1  ingress]# kubectl apply  -f  ingress -deploy.yam l

[root@xianchaomaster1 ~]# kubectl get pods -n ingress -nginx -o wide
NAME                                        READY   STATUS      RESTARTS   AGE
IP               NODE            NOMINATED NODE   READINESS GATES
ingress -nginx -admission -create -k4fmn        0/1     Completed   0          103s
10.244.1.12      xianchaonode1   <none>           <none>
ingress -nginx -admission -patch -x87h8         0/1     Completed   1          103s
10.244.1.11      xianchaonode1   <none>           <none>
ingress -nginx -controller -6c8ffbbfcf -cjj9t   1/1     Running     0          103s
192.168.40.181   xianchaonode1   <none>           <none>
ingress -nginx -controller -6c8ffbbfcf -wpt26   1/1     Running     0          103s
192.168.40.182   xianchaonode2   <n one>           <none>
```

**10.3.1 通过 keepalive +nginx 实现 nginx -ingress -controller 高可用**
**1、安装 nginx 主备：**
在xianchaonode1 和xianchaonode2 上做 nginx 主备安装

```bash
[root@ xianchaonode1  ~]#  yum install nginx keepalived -y
[root@ xianchaonode2  ~]#  yum install nginx keepalived -y
```

**2、修改 nginx 配置文件。主备一样**

```bash
[root@xianchaonode1 ~]# yum install nginx -mod -stream -y
[root@xianchaonode 2~]# yum install nginx -mod -stream -y
[root@ xianchaonode1  ~]# cat /etc/nginx/nginx.conf
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;

include /usr/share/nginx/modules/*.conf;

 events {
    worker_connections 1024;
}

# 四层负载均衡，为两台 Master apiserver 组件提供负载均衡
stream {

    log_format  main  '$remote_addr $upstream_addr - [$time_local] $status
$upstream_bytes_sent';

    access_log  /var/log/nginx/k8s -access.log  main;

    upstream k8s -apiserver {
       server 192.168.40.181 :80;   # Master1 APISERVER IP:PORT
       server 192.168.40.182 :80;   # Master2 APISERVER IP:PORT
    }

    server {
       listen 30080 ;
       proxy_pass k8s -apiserver;
    }
}

http {
    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile            on;
    tcp_nopush          on;
    tcp_nodelay         on;
    keepalive_time out   65;
    types_hash_max_size 2048;

    include             /etc/nginx/mime.types;
    default_type        application/octet -stream;

}

[root@ xianchaonode2  ~]# cat /etc/nginx/nginx.conf
user nginx;

 worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;

include /usr/share/nginx/modules/*.conf;

events {
    worker_connections 1024;
}

# 四层负载均衡，为两台 Master apiserver 组件提供负载均衡
stream {

    log_format  main  '$remote_addr $upstream_addr - [$time_local] $status
$ups tream_bytes_sent';

    access_log  /var/log/nginx/k8s -access.log  main;

    upstream k8s -apiserver {
       server 192.168.40.182 :80;   # Master1 APISERVER IP:PORT
       server 192.168.40.181 :80;   # Master2 APISERVER IP:PORT
    }

    server {
       listen 30080 ;
       proxy_pass k8s -apiserver;
    }
}

http {
    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http _user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile            on;
    tcp_nopush          on;
    tcp_nodelay         on;
    keepalive_timeout   65;
    types_hash_max_size 2048;

    include             /etc/nginx/mime.types;

     default_type        application/octet -stream;

}
```

> **注意： nginx 监听端口变成大于 30000 的端口，比方说 30080, 这样访问域名 :30080 就可以了，必**
须是满足大于 30000 以上，才能代理 ingress -controller

**3、keepalive 配置**
主keepalived

```bash
[root@ xianchaonode1  ~]# cat /etc/keepalived/keepalived.conf
global_defs {
   notification_email {
     acassen@firewall.loc
     failover@firewall.loc
     sysadmin@firewall.loc
   }
   notification_email_from Alexandre.Cassen@firewall.loc
   smtp_server 127.0.0.1
   smtp_connect_timeout 30
   router_id NGINX_MASTER
}

vrrp_script check_nginx {
    script "/etc/keepalived/check_nginx.sh"
}

vrrp_instance VI_1 {
    state MASTER
    interface ens33  # 修改为实际网卡名
    virtual_router_id 51 # VRRP 路由 ID实例，每个实例是唯一的
    priority 100    # 优先级，备服务器设置  90
    advert_int 1    # 指定 VRRP 心跳包通告间隔时间，默认 1秒
    authentication {
        auth_type PASS
        auth_pass 1111
    }
    # 虚拟 IP
    virtual_ipaddress {
        192.168.1.199/24
    }
    track_script {

         check_nginx
    }
}

#vrrp_script ：指定检查 nginx 工作状态脚本（根据 nginx 状态判断是否故障转移）
#virtual_ipaddress ：虚拟 IP（VIP）

[root@ xianchaonode1  ~]# cat /etc/keepalived/check_nginx.sh
#!/bin/bash
#1、判断 Nginx 是否存活
counter=`ps -C nginx --no-header | wc -l`
if [ $counter -eq 0 ]; then
    #2、如果不存活则尝试启动 Nginx
    service nginx start
    sleep 2
    #3、等待 2秒后再次获取一次 Nginx 状态
    counter=`ps -C nginx --no-header | wc -l`
    #4、再次进行判断，如 Nginx 还不存活则停止 Keepalived ，让地址进行漂移
    if [ $counter -eq 0 ]; then
        service  keepalived stop
    fi
fi

[root@ xianchaonode1  ~]# chmod +x  /etc/keepalived/check_nginx.sh
```

备keepalive

```bash
[root@ xianchaonode2  ~]# cat /etc/keepalived/keepalived.conf
global_defs {
   notification_email {
     acassen@firewall.loc
     failover@firewall.loc
     sysadmin@firewall.loc
   }
   notification_email_from Alexandre.Cassen@firewall.loc
   smtp_server 127.0.0.1
   smtp_connect_timeout 30
   router_id NGINX_BACKUP
}

vrrp_script check_nginx {
    script "/etc/keepalived/check_nginx.sh"
}

 vrrp_instance VI_1 {
    state BACKUP
    interface ens33
    virtual_router_id 51 # VRRP 路由 ID实例，每个实例是唯一的
    priority 90
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass 1111
    }
    virtual_ipaddress {
        192.168.1.199/24
    }
    track_script {
        check_nginx
    }
}

[root@ xianchaonode2  ~]# cat /etc/keepalived/check_nginx.sh
#!/bin/bash
#1、判断 Nginx 是否存活
counter=`ps -C nginx --no-header | wc -l`
if [ $counter -eq 0 ]; then
    #2、如果不存活则尝试启动 Nginx
    service nginx start
    sleep 2
    #3、等待 2秒后再次获取一次 Nginx 状态
    counter=`ps -C nginx --no-header | wc -l`
    #4、再次进行判断，如 Nginx 还不存活则停止 Keepalived ，让地址进行漂移
    if [ $ counter -eq 0 ]; then
        service  keepalived stop
    fi
fi

[root@ xianchaonode2  ~]# chmod +x /etc/keepalived/check_nginx.sh
#注：keepalived 根据脚本返回状态码（ 0为工作正常，非 0不正常）判断是否故障转移。
```

**4、启动服务：**

```bash
[root@ xianchaonode1  ~]# systemctl daemon -reload
[root@ xianchaonode1  ~]# systemctl enable nginx keepalived
[root@ xianchaonode1  ~]# systemctl start nginx
```

 报错：
Jul 11 14:33:16 xianchaomaster1  nginx[17367]: nginx: [emerg] unknown directive
"stream" in /etc/ngi...:13
解决办法如下：

```bash
[root@xianchaonode1  ~]# yum install nginx -mod -stream  -y
[root@ xianchaonode1  ~]# systemctl start nginx
[root@ xianchaonode1  ~]# systemctl start  keepalived

[root@ xianchaonode2  ~]# systemctl daemon -reload
[root@ xianchaonode2  ~]# systemctl enable nginx keepalived
[root@ xianchaonode2  ~]# systemctl start nginx
```
报错：
Jul 11 14:33:16 xianchaomaster1  nginx[17367]: nginx: [emerg] unknown directive
"stream" in /etc/ngi...:13
解决办法如下：

```bash
[root@ xianchaonode2  ~]# yum install nginx -mod -stream  -y
[root@ xianchaonode2  ~]# systemctl start nginx
[root@ xianchaonode2  ~]# systemctl start keepalived
```

**5、测试 vip是否绑定成功**

```bash
[root@ xianchaonode1  ~]# ip addr
1: lo: <LOOPBACK,UP ,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group
default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host
       valid_lft forever preferred_lft forever
2: ens33: <BROADCAST,MULTICAST,UP ,LOWER _UP> mtu 1500 qdisc pfifo_fast state UP
group default qlen 1000
    link/ether 00:0c:29:79:9e:36 brd ff:ff:ff:ff:ff:ff
    inet 192.168.40.182 /24 brd 192.168.40.255 scope global noprefixroute ens33
       valid_lft forever preferred_lft forever
    inet 192.168.1.199 /24 scope global secondary ens33
       valid_lft forever preferred_lft forever
    inet6 fe80::b6ef:8646:1cfc:3e0c/64 scope link noprefixroute
       valid_lft forever preferred_lft forever
```

**6、测试 keepalived ：**
停掉 xianchaonode1 上的 keepalived 。Vip会漂移到 xianchaonode2

```bash
[root@ xianchaonode1  ~]# service  keepalived stop
[root@ xianchaonode2  ~]# ip addr

 1: lo: <LOOPBACK,UP ,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group
default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127 .0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host
       valid_lft forever preferred_lft forever
2: ens33: <BROADCAST,MULTICAST,UP ,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP
group default qlen 1000
    link/ether 00:0c:29:83:4d:9e brd ff:ff:ff:ff:ff:ff
    inet 192.168.40.181 /24 brd 192.168.40.255 scope global noprefixroute ens33
       valid_lft forever preferred_lft forever
    inet 192.168.1.199 /24 scope global secondary ens33
       valid_lft for ever preferred_lft forever
    inet6 fe80::a5e0:c74e:d0f3:f5f2/64 scope link tentative noprefixroute dadfailed
       valid_lft forever preferred_lft forever
    inet6 fe80::b6ef:8646:1cfc:3e0c/64 scope link noprefixroute
       valid_lft forever preferr ed_lft forever
    inet6 fe80::91f:d383:3ce5:b3bf/64 scope link tentative noprefixroute dadfailed
       valid_lft forever preferred_lft forever
```

启动 xianchaonode1 上的 keepalived 。Vip又会漂移到 xianchaomaster1

```bash
[root@ xianchaonode1  ~]#  service  keepalived start
[root@ xianchaonode1  ~]# ip addr
1: lo: <LOOPBACK,UP ,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group
default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft foreve r
    inet6 ::1/128 scope host
       valid_lft forever preferred_lft forever
2: ens33: <BROADCAST,MULTICAST,UP ,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP
group default qlen 1000
    link/ether 00:0c:29:79:9e:36 brd ff:ff:ff:ff:ff:ff
    inet 192.168.40 .182/24 brd 192.168.40.255 scope global noprefixroute ens33
       valid_lft forever preferred_lft forever
    inet 192.168.1.199 /24 scope global secondary ens33
       valid_lft forever preferred_lft forever
    inet6 fe80::b6ef:8646:1cfc:3e0c/64 scope link noprefixroute
       valid_lft forever preferred_lft forever
```

**10.3.2 测试 Ingress HTTP 代理 k8s内部站点**

 1.部署后端 tomcat 服务

```bash
[root@ xianchaomaster1  ~]# cat ingress -demo.yaml
```

```yaml
apiVersion: v1
kind: Service
metadata:
  name: tomcat
  namespace: default
spec:
  selector:
    app: tomcat
    release: canary
  ports:
  - name: http
    targetPort: 8080
    port: 8080
  - name: ajp
    targetPort: 8009
    port: 8009
---
apiVersion: apps/v1
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
        app: tomcat
        release: canary
    spec:
      containers:
      - name : tomcat
        image: tomcat:8.5.34 -jre8-alpine
        imagePull Policy: IfNotPresent
        ports:
        - name: http
          containerPort: 8080

           name: ajp
          containerPort: 8009
#更新资源清单 yaml 文件：
```

```bash
[root@ xianchaomaster1  ~]# kubectl apply -f ingress -demo.yaml
service/tomcat created
deployment.apps/tomcat -deploy created
#查看 pod 是否部署成功
[root@ xianchaomaster1  ~]# kubectl get pods -l app=tomcat
NAME                             READY   STATUS    RESTARTS   AGE
tomcat-deploy -66b67fcf7b -9h9qp   1/1     Running   0          32s
tomcat -deploy -66b67fcf7b -hxtkm   1/1     Running   0          32s
```
**2、编写 ingress 规则**

```bash
#编写 ingress 的配置清单
[root@ xianchaomaster1  ~]# cat ingress -myapp.yaml
```

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress -myapp
  namespace: default
  annotations:
    kubernetes.io/ingress.class: "nginx"
spec:
  rules:   #定义后端转发的规则
  - host: tomcat.lucky.com #通过域名进行转发
    http:
      paths:
      - path: /   #配置访问路径，如果通过 url进行转发，需要修改；空默认为访问的路径为 "/"
        pathType:  Prefix
        backend:  #配置后端服务
         service:
           name: tomcat
           port:
            number: 8080

#更新 yaml 文件：
```

```bash
[root@ xianchaomaster1  ~]# kubectl apply -f ingress -myapp.yaml
#查看 ingress -myapp 的详细信息
[root@ xianchaomaster1  ~]# kubectl describe ingress ingress -myapp
Name:             ingress -myapp
Namespace:        default
Address:
Default backend:  default -http-backend:80 (10.244.187.118:8080)
Rules:

   Host              Path  Backends
  ----              ----  --------
  tomcat.lucky.com
                       tomcat:8080 (10.244.209.172:8080,10.244.209.173:8080)
Annotations:        kubernetes.io/ingress.class: nginx
Events:
  Type    Reason  Age   From                      Message
  ----    ------   ----  ----                      -------
  Normal  CREATE  22s   nginx -ingress -controller  Ingress default/ingress -myapp

#修改电脑本地的host 文件， 增加如下一行， 下面的 ip是xianchaonode1 节点 ip
192.168.1. 199  tomcat.lucky.com
```
浏览器访问 tomcat.lucky.com ，出现如下 页面：

总结：
通过 deployment +nodeSelector +pod 反亲和性实现 ingress -controller 在xianchaonode1 和
xianchaonode 2调度

Keeplaive +nginx 实现 ingress -controller 高可用

测试 ingress 七层代理是否正常

**10.3.3 同一个 k8s搭建多套 Ingress -controller**

 ingress 可以简单理解为 service 的service ，他通过独立的 ingress 对象来制定请求转发的规则，
把请求路由到一个或多个 service 中。这样就把服务与请求规则解耦了，可以从业务维度统一考虑业务的
暴露，而不用为每个 service 单独考虑。

在同一个 k8s集群里，部署两个 ingress nginx 。一个 deploy 部署给 A的API网关项目用。另一
个daemonset 部署给其它项目作域名访问用。这两个项目的更新频率和用法不一致，暂时不用合成一
个。

为了满足多租户场景，需要在 k8s集群部署多个 ingress -controller ，给不同用户不同环境使用。

主要参数设置：
containers:
        - name: nginx -ingress -controller
          image: registry.cn -hangzhou.aliyuncs.com/google_containers/nginx -ingress -
controller:v1.1.0
          args:
            - /nginx -ingress -controller
            - --ingress -class=ngx -ds

> **注意： --ingress -class 设置该 Ingress Controller 可监听的目标 Ingress Class 标识；注意：同一**
个集群中不同套 Ingress Controller 监听的 Ingress Class 标识必须唯一，且不能设置为 nginx 关键
字（其是集群默认 Ingress Controller 的监听标识） ；

创建 Ingress 规则：

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress -myapp
  namespace: default
  annotations:
    kubernetes.io/ingress.class: " ngx-ds"
spec:
  rules:
  - host: tomcat.lucky.com
    http:
      paths:
      - path: /
        pathType:  Prefix
        backend:
         service:
           name: tomcat
           port:

             number: 8080

annotations:
    # 注意：这里要设置为 你前面配置的 `controller.ingressClass` 唯一标识
 annotations:
    kubernetes.io/ingress.class: "ngx -ds"
```


