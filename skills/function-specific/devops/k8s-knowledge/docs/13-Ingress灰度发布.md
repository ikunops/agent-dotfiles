目录
**1.1 Ingress 和Ingress Controller 深度解读  ................................ ........ 错误!未定义书签。**
**1.1.1 Ingress介绍 ................................ ................................ .........................  错误!未定义书签。**
**1.1.2 Ing ress Controller 介绍 ................................ ................................ .... 错误!未定义书签。**
**1.1.3 Ingress和Ingress Controller 总结 ................................ ...............  错误!未定义书签。**
**1.1.4 使用 Ingress Controller 代理 k8s内部应用的流程  ...................  错误!未定义书签。**
**1.1.5 安装 Nginx Ingress Controller  ................................ .......................  错误!未定义书签。**
**1.1.6 测试 Ingress HTTP 代理 tomcat  ................................ ....................  错误!未定义书签。**
**1.2 通过 Ingress -nginx实现灰度发布  ................................ ................................ ..................... 2**

**1.2 通过 Ingress -nginx 实现灰度发布**

场景一 : 将新版本灰度给部分用户
假设线上运行了一套对外提供  7 层服务的  Service A 服务，后来开发了个新版本  Service A’ 想
要上线，但又不想直接替换掉原来的  Service A，希望先灰度一小部分用户，等运行一段时间足够稳定
了再逐渐全量上线新版本，最后平滑下线旧版本。这个时候就可以利用  Nginx Ingress 基于 Header
或 Cookie 进行流量切分的策略来发布，业务使用  Header 或 Cookie 来标识不同类型的用户，我们
通过配置  Ingress 来实现让带有指定  Header 或 Cookie 的请求被转发到新版本，其它的仍然转发到
旧版本，从而实现将新版本灰度给部分用户 :

场景二 : 切一定比例的流量给新版本
假设线上运行了一套对外提供  7 层服务的  Service B 服务，后来修复了一些问题，需要灰度上线
一个新版本  Service B’ ，但又不想直接替换掉原来的  Service B ，而是让先切  10% 的流量到新版
本，等观察一段时间稳定后再逐渐加大新版本的流量比例直至完全替换旧版本，最后再滑下线旧版本，从
而实现切一定比例的流量给新版本 :

Ingress -Nginx 是一个 K8S ingress 工具，支持配置 Ingress Annotations 来实现不同场景下的
灰度发布和测试。  Nginx Annota tions  支持以下几种 Canary 规则：

假设我们现在部署了两个版本的服务，老版本和 canary 版本

nginx.ingress.kubernetes.io/canary -by-header ：基于 Request Header 的流量切分，适用于
灰度发布以及  A/B 测试。当 Request Header 设置为  always 时，请求将会被一直发送到  Canary 版
本；当  Request Header 设置为  never 时，请求不会被发送到  Canary 入口。

nginx.ingress.kubern etes.io/canary -by-header -value ：要匹配的  Request Header 的值，
用于通知  Ingress 将请求路由到  Canary Ingress 中指定的服务。当  Request Header 设置为此值
时，它将被路由到  Canary 入口。

nginx.ingress.kubernetes.io/canary -weight ：基于服务权重的流量切分，适用于蓝绿部署，权
重范围  0 - 100 按百分比将请求路由到  Canary Ingress 中指定的服务。权重为  0 意味着 该金丝雀规
则不会向  Canary 入口的服务发送任何请求。权重为 60意味着 60%流量转到 canary 。权重为  100 意
味着所有请求都将被发送到  Canary 入口。

nginx.ingress.kubernetes.io/canary -by-cookie ：基于  Cookie 的流量切分，适用于灰度发布
与 A/B 测试。用于通知  Ingress 将请求路由到  Canary Ingress 中指定的服务的 cookie 。当

 cookie 值设置为  always 时，它将被路由到  Canary 入口；当  cook ie 值设置为  never 时，请求不会
被发送到  Canary 入口。

部署两个版本的服务
这里以简单的  nginx 为例，先部署一个  v1 版本:

```bash
[root@ xianchaonode1  ~]# docker load -i openresty.tar.gz
[root@ xianchaonode2  ~]# docker load -i openresty.tar.gz

[root@ xianchaomaster1  v1-v2]# vim v1.yaml
```

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx -v1
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
      version: v1
  template:
    metadata:
      labels:
        app: nginx
        version: v1
    spec:
      containers:
      - name: nginx
        image: "openresty/openresty:centos"
        imagePull Policy: IfNotPresent
        ports:
        - name: http
          protocol: TCP
          containerPort: 80
        volumeMounts:
        - mountPath: /usr/ local/openresty/nginx/conf/nginx.conf
          name: config
          subPath: nginx.conf
      volumes:
      - name: config
        configMap:
          name: nginx -v1
---

 apiVersion: v1
kind: ConfigMap
metadata:
  labels:
    app: nginx
    version: v1
  name: nginx -v1
data:
  nginx.conf: | -
    worker_processes  1;
    events {
        accept_mutex on;
        multi_accept on;
        use epoll;
        worker_connections  1024;
    }
    http {
        ignore_invalid_headers off;
        server {
            listen 80;
            location / {
                access_by_lua '
                    local header_str = ngx.say("nginx -v1")
                ';
            }
        }
    }
---
apiVersion: v1
kind: Service
metadata:
  name: nginx -v1
spec:
  type: ClusterIP
  ports:
  - port: 80
    protocol: TCP
    name: http
  selector:
    app: nginx
    version: v1

```

```bash
[root@ xianchaomaster1  v1-v2]# kubectl apply -f v1.yaml
```

再部署一个  v2 版本:

```bash
[root@ xianchaomaster1  v1-v2]# vim v2.yaml
apiVe rsion: apps/v1
```

```yaml
kind: Deployment
metadata:
  name: nginx -v2
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
      version: v2
  template:
    metadata:
      labels:
        app: nginx
        version: v2
    spec:
      containers:
      - name: nginx
        image: "openresty/openresty:centos"
        imagePull Policy: IfNotPresent
        ports:
        - name: http
          protocol: TCP
          containerPort: 80
        volumeMounts:
        - mountPath: /usr/ local/openresty/nginx/conf/nginx.conf
          name: config
          subPath: nginx.conf
      volumes:
      - name: config
        configMap:
          name: nginx -v2
---
apiVersion: v1
kind: ConfigMap
metadata:
  labels:
    app: nginx
    version: v2
  name: nginx -v2

 data:
  nginx.conf: | -
    worker_processes  1;
    events {
        accept_mutex on;
        multi_accept on;
        use epoll;
        worker_connections  1024;
    }
    http {
        ignore_invalid_headers off;
        server {
            listen 80;
            location / {
                access_by_lua '
                    local header_str = ngx.say("nginx -v2")
                ';
            }
        }
    }
---
apiVersion: v1
kind: Service
metadata:
  name: nginx -v2
spec:
  type: ClusterIP
  ports:
  - port: 80
    protocol: TCP
    name: http
  selector:
    app: nginx
    version: v2

```

```bash
[root@ xianchaomaster1  v1-v2]# kubectl apply -f v2.yaml
```

再创建一个  Ingress ，对外暴露服务，指向  v1 版本的服务 :

```bash
[root@ xianchaomaster1  v1-v2]# vim v1 -ingress.yaml
```

```yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: nginx

   annotations:
    kubernetes.io/ingress.class: nginx
spec:
  rules:
  - host: canary.example.com
    http:
      paths:
      - backend:
          serviceName: ng inx-v1
          servicePort: 80
        path: /

```

```bash
[root@ xianchaomaster1  v1-v2]# kubectl apply -f v1-ingress.yaml
```

访问验证一下 :
$ curl -H "Host: canary.example.com" http://EXTERNAL -IP # EXTERNAL -IP 替换为
Nginx Ingress 自身对外暴露的  IP

```bash
[root@ xianchaomaster1  v1-v2]# curl -H "Host: canary.example.com"
http:// 192.168.40.181
```
返回结果如下：
nginx -v1

基于 Header 的流量切分：
创建 Canary Ingress ，指定  v2 版本的后端服务，且加上一些  annotation ，实现仅将带有名为
Region 且值为  cd 或 sz 的请求头的请求转发给当前  Canary Ingress ，模拟灰度新版本给成都和深
圳地域的用户 :

```bash
[root@ xianchaomaster1  v1-v2]# vim v2 -ingress.yaml
```

```yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/canary: "true"
    nginx.ingress.kubernetes .io/canary -by-header: "Region"
    nginx.ingress.kubernetes.io/canary -by-header -pattern: "cd|sz"
  name: nginx -canary
spec:
  rules:
  - host: canary.example.com
    http:
      paths:
      - backend:

           serviceName: nginx -v2
          servicePort: 80
        path: /
```

```bash
[root@ xianchaomaster1  v1-v2]# kubectl apply -f v2-ingress.yaml
```

测试访问 :
$ curl -H "Host: canary.example.com" -H "Region: cd" http://EXTERNAL -IP #
EXTERNAL -IP 替换为  Nginx Ingress 自身对外暴露的  IP

```bash
[root@ xianchaomaster1  ingress]# curl -H "Host: canary.example.com" -H "Region: cd"
http:// 192.168.40.181
```
返回结果如下：
nginx -v2
$ curl -H "Host: canary.example.com" -H "Region: bj" http://EXTERNAL -IP

```bash
[root@ xianchaomaster1  v1-v2]# curl -H "Host: canary.example.com" -H "Region: bj"
http:// 192.168.40.181
```
返回结果如下：
nginx -v1
$ curl -H "Host: canary.example.com" -H "Region: cd" http://EXTERNAL -IP

```bash
[root@ xianchaomaster1  v1-v2]# curl -H "Host: canary.example.com" -H "Region: cd"
http:// 192.168.40.181
```
返回结果如下：
nginx -v2

$ curl -H "Host: canary.example.com" http://EXTERNAL -IP
$ curl -H "Host: canary.examp le.com" http:// 192.168.40.181
返回结果如下：
nginx -v1

可以看到，只有  header Region 为 cd 或 sz 的请求才由  v2 版本服务响应。

基于 Cookie 的流量切分：
与前面  Header 类似，不过使用  Cookie 就无法自定义  value 了，这里以模拟灰度成都地域用户
为例，仅将带有名为  user_from_cd 的 cookie 的请求转发给当前  Canary Ingress 。先删除前面基
于 Header 的流量切分的  Canary Ingress ，然后创建下面新的  Canary Ingress:

```bash
[root@ xianchaomaster1  v1-v2]# kubectl delete -f v2-ingress.yaml
[root@ xianchaomaster1  v1-v2]# vim v1 -cookie.yaml
```

```yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  annotat ions:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/canary: "true"
```

     nginx.ingress.kubernetes.io/canary -by-cookie: "user_from_cd"
  name: nginx -canary

```yaml
spec:
  rules:
  - host: canary.example.com
    http:
      paths:
      - backend:
          serviceName: nginx -v2
          servicePort: 80
        path: /

```

```bash
[root@ xianchaomaster1  v1-v2]# kubectl apply -f v1-cookie.yaml
```
测试访问 :
$ curl -s -H "Host: canary.example.com" --cookie "user_from_cd=always"
http://EXTERNAL -IP # EXTERNAL -IP 替换为  Nginx Ingress 自身对外暴露的  IP

```bash
[root@ xianchaomaster1  v1-v2]#  curl -s -H "Host: canary.example.com" --cookie
"user_from_cd=always" http:// 192.168.40.181
```
返回的结果：
nginx -v2

$ curl -s -H "Host: canary.example.com" --cookie "user_from_bj=always"
http://EXTERNAL -IP

```bash
[root@ xianchaomaster1  v1-v2]# curl -s -H "Host: canary.example.com" --cookie
"user_from_bj=always" http:// 192.168.40.181
```

返回的结果：
nginx -v1

$ curl -s -H "Host: canary.example.com" http://EXTERNAL -IP

```bash
[root@ xianchaomaster1  v1-v2]# curl -s -H "Host: canary.example.com"
http:// 192.168.40.181
```
返回的结果：
nginx -v1

可以看到，只有  cookie user_from_cd 为 always 的请求才由  v2 版本的服务响应。

基于服务权重的流量切分
基于服务权重的  Canary Ingress 就简单了，直接定义需要导入的流量比例，这里以导入  10% 流
量到 v2 版本为例  (如果有，先删除之前的  Canary Ingress):

```bash
[root@ xianchaomaster1  v1-v2]# kubectl delete -f v1-cookie.yaml

 [root@ xianchaomaster1  v1-v2]# vi m v1 -weight.yaml
```

```yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/canary: "true"
    nginx.ingress.kubernetes.io/canary -weight: "10"
  name: nginx -canary
spec:
  rules:
  - host: canary.example.com
    http:
      paths:
      - backend:
          serviceName: nginx -v2
          servicePort: 80
        path: /

```

```bash
[root@ xianchaomaster1  v1-v2]# kubectl apply -f v1-weight.yaml
```
测试访问 :
$ for i in {1..10}; do curl -H "Host: canary.example.com" http://EXTERNAL -IP; done;

```bash
[root@ xianchaomaster1  v1-v2]#  for i in {1..10}; do curl -H "Host:
canary.example.com" http:// 192.168.40.181 ; done;
```
返回如下结果：
nginx -v1
nginx -v1
nginx -v1
nginx -v1
nginx -v1
nginx -v1
nginx-v2
nginx -v1
nginx -v1
nginx -v1
可以看到，大概只有十分之一的几率由  v2 版本的服务响应，符合  10% 服务权重的设置


