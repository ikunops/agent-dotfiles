 Prometheus+Grafana+alertmanager 构建企业级监控系统

实验环境：
Prometheus +grafana+alertmanager 安装在k8s集群，k8s环境如下：

k8s集群：        k8s的控制节点
ip：192.168.40.180
主机名： xianchaomaster1

 配置：4vCPU/4Gi内存

k8s的工作节点：
ip：192.168.40.181
主机名： xianchaonode1
配置：4vCPU/4Gi内存

课程目标：
介绍k8s集群中部署 prometheus 、grafana、alertmanager ，并且配置 prometheus 的动态、静态服
务发现，实现对容器、物理节点、 service、pod等资源指标监控，并在 Grafana 的web界面展示
警。Promql 语法、prometheus 数据类型。

**1、Prometheus 介绍？**
Prometheus 是一个开源的系统监控和报警系统，现在已经加入到 CNCF基金会，成为继 k8s之后第二
个在CNCF托管的项目，在 kubernetes 容器管理系统中，通常会搭配 prometheus 进行监控，同时也支持
多种exporter 采集数据，还支持 pushgateway 进行数据上报， Prometheus 性能足够支撑上万台规模的集
群。

**2、Prometheus 特点？**
1.多维度数据模型
每一个时间序列数据 都由metric度量指标名称和它的标签 labels键值对集合唯一确定 ：
这个metric度量指标名称指定监控目标系统的测量特征（如： http_requests_total - 接收http请
求的总计数）。 labels开启了Prometheus 的多维数据模型：对于相同的度量名称，通过不同标签列表的
结合, 会形成特定的度量维度实例。 (例如：所有包含度量名称为 /api/tracks 的http请求，打上
method=POST 的标签，则形成了具体的 http请求)。这个查询语言在这些度量和标签列表的基础上进行过
滤和聚合。改变任何度量上的任何标签值，则会形成新的时间序列图。
2.灵活的查询语言（ PromQL）
可以对采集的 metrics 指标进行加法，乘法，连接等操作；
3.可以直接在本地部署，不依赖其他分布式存储；
4.通过基于 HTTP的pull方式采集时序数据；
5.可以通过中间网关 pushgateway 的方式把时间 序列数据推送到 prometheus server 端；
6.可通过服务发现或者静态配置来发现目标服务对象（ targets）。
7.有多种可视化图像界面，如 Grafana 等。
8.高效的存储，每个采样数据占 3.5 bytes 左右，300万的时间序列， 30s间隔，保留 60天，消耗
磁盘大概 200G。
9.做高可用，可以对数据做异地备份，联邦集群，部署多套 prometheus ，pushgateway 上报数据

**2.1 样本**
在时间序列中的每一个点称为一个样本（ sample），样本由以下三部分组成：
**1、指标（metric）：指标名称和描述当前样本特征的  labelsets ；**

**2、时间戳（ timestamp ）：一个精确到毫秒的时间戳；**
**3、样本值（ value）： 一个 folat64 的浮点型数据表示当前样本的值。**

表示方式：
通过如下表达方式表示指定指标名称和指定标签集合的时间序列：
<metric name>{<label name>=<label value>, ...}
例如，指标名称为  api_http_requests_total ，标签为  method="POST"  和 handler="/messages"
的时间序列可以表示为：
api_http_requests_total{method="POST", handler="/messages"}

**3、Prometheus 组件介绍**
1.Prometheus Server: 用于收集和存储时间序列数据。
2.Client Library: 客户端库，检测应用程序代码，当 Prometheus 抓取实例的 HTTP端点时，客户
端库会将所有跟踪的 metrics 指标的当前状态发送到 prometheus server 端。
3.Exporters: prometheus 支持多种 exporter ，通过exporter 可以采集 metrics 数据，然后发送到
prometheus server 端，所有向 promtheus  server提供监控数据的程序都可以被称为 exporter
4.Alertmanager: 从 Prometheus server 端接收到  alerts 后，会进行去重，分组，并路由到相应
5.Grafana ：监控仪表盘，可视化监控数据
6.pushgateway: 各个目标主机可上报数据到 pushgatew ay，然后prometheus server 统一从
pushgateway 拉取数据。

从上图可发现， Prometheus 整个生态圈组成主要包括 prometheus server ，Exporter ，
pushgateway ，alertmanager ，grafana，Web ui界面，Prometheus server由三个部分组成，
Retrieval ，Storage，PromQL
1.Retrieval 负责在活跃的 target主机上抓取监控指标数据
2.Storage 存储主要是把采集到的数据存储到磁盘中

 3.PromQL 是Prometheus 提供的查询语言模块。

**4、Prometheus 工作流程**
1.Prometheus  server可定期从活跃的（ up）目标主机上（ target）拉取监控指标数据，目标主机的
监控数据可通过配置静态 job或者服务发现的方式被 prometheus server 采集到，这种方式 默认的pull
方式拉取指标；也可通过 pushgateway 把采集的数据上报到 prometheus server 中；还可通过一些组件
自带的exporter 采集相应组件的数据；
2.Prometheus server 把采集到的监控指标数据保存到本地磁盘或者数据库；
3.Prometheus 采集的监控指标数据按时间序列存储，通过配置报警规则，把触发的报警发送到
alertmanager
5.Prometheus 自带的web ui界面提供 PromQL查询语言，可查询监控数据
6.Grafana 可接入prometheus 数据源，把监控数据以图形化形式展示出

**4、Prometheus 和zabbix对比分析**

**5、Prometheus 的几种部署模式**

**5.1 基本高可用 模式**

基本的HA模式只能确保 Promthues 服务的可用性问题，但是不解决 Prometheus Server之间的数据
一致性问题以及持久化问题 (数据丢失后无法恢复 )，也无法进行动态的扩展。因此这种部署方式适合监
控规模不大， Promthues Server 也不会频繁发生迁移的情况，并且只需要保存短周期监控数据的场景。

**5.2 基本高可用 +远程存储**

在解决了 Promthues 服务可用性的基础上，同时确保了数据的持久化，当 Promthues Server 发生宕
机或者数据丢失的情况下，可以快速的恢复。  同时Promthues Server可能很好的进行迁移。因此，该
方案适用于用户监控规模不大，但是希望能够将监控数据持久化，同时能够确保 Promthues Server 的可
迁移性的场景。

**5.3 基本HA + 远程存储  + 联邦集群方案**

Promthues 的性能瓶颈主要在于大量的采集任务，因此用户需要利用 Prometheus 联邦集群的特性，
将不同类型的采集任务划分到不同的 Promthues 子服务中，从而实现功能分区。例如一个 Promthues

 Server负责采集基础设施相关的监控指标，另外一个 Prometheus Serv er负责采集应用监控指标。再有
上层Prometheus Server 实现对数据的汇聚。

**6、Prometheus 的四种数据类型**
**6.1 Counter**
Counter 是计数器类型：
**1、Counter 用于累计值，例如记录请求次数、任务完成数、错误发生次数。**
**2、一直增加，不会减少。**
**3、重启进程后，会被重置。**
例如：http_response_total{method="GET",endpoint="/api/tracks"}   100
      http_response_total{method="GET",endpoint="/api/tracks"}   160

Counter 类型数据可以让用户方便的了解事件产生的速率的变化，在 PromQL内置的相关操作函数可
以提供相应的分析，比如以 HTTP应用请求量来进行说明：
**1、通过rate()函数获取 HTTP请求量的增长率**
rate(http_requests_total[5m])
**2、查询当前系统中，访问量前 10的HTTP地址**
topk(10, http_requests_total)

**6.2 Gauge**
Gauge是测量器类型：
**1、Gauge是常规数值，例如温度变化、内存使用变化。**
**2、可变大，可变小。**
**3、重启进程后，会被重置**

例如：
memory_usage_bytes{host="master -01"}   100
memory_usage_bytes{host="master -01"}   30
memory_usage_bytes{host="master -01"}   50
memory_usage_bytes{host="master -01"}   80

对于 Gauge 类型的监控指标，通过  PromQL 内置函数  delta() 可以获取样本在一段时间内的变化
情况，例如，计算  CPU 温度在两小时内的差异：
dalta(cpu_temp_celsius{host="zeus"}[2h])

你还可以通过 PromQL 内置函数  predict_linear()  基于简单线性回归的方式，对样本数据的变化趋
势做出预测。例如，基于  2 小时的样本数据，来预测主机可用磁盘空间在  4 个小时之后的剩余情况：
predict_linear(node_filesystem_free{job="node"}[2h], 4 * 3600)  < 0

**6.3 histogram**
histogram 是柱状图，在 Prometheus 系统的查询语言中，有三种作用：

**1、在一段时间范围内对数据进行采样（通常是请求持续时间或响应大小等），并将其计入可配置的**
存储桶（ bucket）中. 后续可通过指定区间筛选样本，也可以统计样本总数，最后一般将数据展示为直
方图。
**2、对每个采样点值累计和 (sum)**
**3、对采样点的次数累计和 (count)**

度量指标名称 : [basename]_ 上面三类的作用度量指标名称
**1、[basename]_bucket{le=" 上边界"}, 这个值为小于等于上边界的所有采样点数量**
**2、[basename]_sum**
**3、[basename]_count**

小结：如果定义一个度量类型为 Histogram ，则Prometheus 会自动生成三个对应的指标

**6.3.1 为什需要用 histogram 柱状图？**

在大多数情况下人们都倾向于使用某些量化指标的平均值，例如  CPU 的平均使用率、页面的平均响
应时间。这种方式的问题很明显，以系统  API 调用的平均响应时间为例：如果大多数  API 请求都维持
在 100ms 的响应时间范围内，而个别请求的响应时间需要  5s，那么就会导致某些  WEB 页面的响应时间
落到中位数的情况，而这种现象被称为长尾问题。
为了区分是平均的慢还是长尾的慢，最简单的方式就是按照请求延迟的范围进行分组。例如，统计
延迟在 0~10ms 之间的请求数有多少 ，而 10~20ms 之间的请求数又有多少。通过这种方式可以快速分析
系统慢的原因。 Histogram 和 Summary 都是为了能够解决这样问题的存在，通过  Histogram 和
Summary 类型的监控指标，我们可以快速了解监控样本的分布情况。

Histogram 类型的样本会提供三种指标（假设指标名称为  <basename> ）：
样本的值分布在  bucket 中的数量，命名为  <basename>_bucket{le="< 上边界>"}。解释的更通俗易
懂一点，这个值表示指标值小于等于上边界的所有样本数量。

**1、在总共2次请求当中。 http 请求响应时间  <=0.005 秒 的请求次数为 0**
io_namespace_http_requests_latency_seconds_histogram_bucket{path="/",method="GET",code=
"200",le="0.005",} 0.0
**2、在总共2次请求当中。 http 请求响应时间  <=0.01 秒 的请求次数 为0**
io_namespace_http_requests_latency_seconds_histogram_bucket{path="/",method="GET",code="200
",le="0.01",} 0.0
**3、在总共2次请求当中。 http 请求响应时间  <=0.025 秒 的请求次数为 0**
io_namespace_http_requests_latency_seconds_histogram_bucket{path="/",method="GET",code="200
",le="0.025",} 0.0
io_namespace_http_requests_latency_seconds_histogram_bucket{path="/",method="GET",code=
"200",le="0.05",} 0.0
io_namespace_http_requests_latency_se conds_histogram_bucket{path="/",method="GET",code=
"200",le="0.075",} 0.0

 io_namespace_http_requests_latency_seconds_histogram_bucket{path="/",method="GET",code=
"200",le="0.1",} 0.0
io_namespace_http_requests_latency_seconds_histogram_bucket{path="/",method ="GET",code=
"200",le="0.25",} 0.0
io_namespace_http_requests_latency_seconds_histogram_bucket{path="/",method="GET",code=
"200",le="0.5",} 0.0
io_namespace_http_requests_latency_seconds_histogram_bucket{path="/",method="GET",code=
"200",le="0.75",} 0.0
io_namespace_http_requests_latency_seconds_histogram_bucket{path="/",method="GET",code=
"200",le="1.0",} 0.0
io_namespace_http_requests_latency_seconds_histogram_bucket{path="/",method="GET",code=
"200",le="2.5",} 0.0
io_namespace_http_requests_latency_seconds_hi stogram_bucket{path="/",method="GET",code=
"200",le="5.0",} 0.0
io_namespace_http_requests_latency_seconds_histogram_bucket{path="/",method="GET",code=
"200",le="7.5",} 2.0
**4、在总共2次请求当中。 http 请求响应时间  <=10 秒 的请求次数为  2**
io_namespace_http_requests_latency_seconds_hi stogram_bucket{path="/",method="GET",code=
"200",le="10.0",} 2.0
io_namespace_http_requests_latency_seconds_histogram_bucket{path="/",method="GET",code=
"200",le="+Inf",} 2.0

所有样本值的大小总和，命名为  <basename> _sum。
**5、实际含义：  发生的2次 http 请求总的响应时间为  13.107670803000001 秒**
io_namespace_http_requests_latency_seconds_histogram_sum{path="/",method="GET",code="20
0",} 13.107670803000001

样本总数，命名为  <basename> _count。值和 <basename> _bucket{le="+Inf"}  相同。
**6、实际含义：  当前一共发生了  2 次 http 请求**
io_namespace_http_requests_latency_seconds_histogram_count{path="/",method="GET",code="
200",} 2.0

> **注意：**
bucket 可以理解为是对数据指标值域的一个划分，划分的依据应该基于数据值的分布。注意后面的
采样点是包含前面的采样点的，假设  xxx_bucket{...,le="0.01"}  的值为 10，而
xxx_bucket{...,le="0.05"}  的值为 30，那么意味着这  30 个采样点中，有  10 个是小于  0.01s的，其
余 20 个采样点的响应时间是介于 0.01s 和 0.05s之间的。
可以通过  histogram_quantile() 函数来计算 Histogram 类型样本的 分位数。分位数可能不太好理
解，你可以理解为分割数据的点。我举个例子，假设样本的  9 分位数（ quantile=0.9 ）的值为  x，即表
示小于 x 的采样值的数量占总体采样值的  90%。Histogram 还可以用来计算应用性能指标值（ Apdex
score）。

**6.4 summary**
与 Histogram 类型类似，用于表示一段时间内的数据采样结果（通常是请求持续时间或响应大小
等） ，但它直接存储了分位数（ 通过客户端计算，然后展示出来） ，而不是通过区间来计算。 它也有三种
作用：
**1、对于每个采样点进行统计，并形成分位图。 （如：正态分布一样，统计低于 60分不及格的同**
学比例，统计低于 80分的同学比例，统计低于 95分的同学比例）
**2、统计班上所有同学的总成绩 (sum)**
**3、统计班上同学的考试总人数 (count)**

带有度量指标的 [basename] 的summary 在抓取时间序列数据 有如命名。
**1、观察时间的φ -quantiles (0 ≤ φ ≤ 1), 显示为[basename]{ 分位数="[φ]"}**
**2、[basename]_sum ， 是指所有观察值的总和**
**3、[basename]_count, 是指已观察到的事件计数值**

样本值的分位数分布情况，命名为  <basename> {quantile=" <φ>"}。
**1、含义：这  12 次 http 请求中有  50% 的请求响应时间是  3.052404983s**

io_namespace_http_requests_latency_seconds_summary{path="/",method="GET",c ode="200",quantil

```bash
e="0.5",} 3.052404983
```
**2、含义：这  12 次 http 请求中有  90% 的请求响应时间是  8.003261666s**

io_namespace_http_requests_latency_seconds_summary{path="/",method="GET",code="200",quantil

```bash
e="0.9",} 8.003261666
```
所有样本值的大小总和，命名为  <basename> _sum。
**1、含义：这 12次 http 请求的总响应时间为  51.029495508s**

io_namespace_http_requests_latency_seconds_summary_sum{path="/",metho d="GET",code="200",}
51.029495508

样本总数，命名为  <basename> _count。
**1、含义：当前一共发生了  12 次 http 请求**

io_namespace_http_requests_latency_seconds_summary_count{path="/",method="GET",code="200",}
12.0

现在可以总结一下  Histogram 与 Summary 的异同：
它们都包含了  <basename>_sum 和 <basename>_count 指标
Histogram 需要通过  <basename>_bucket 来计算分位数，而  Summary 则直接存储了分位数的
值。

        prometheus_tsdb_wal_fsync_duration_seconds{quantile="0.5"} 0.012352463
prometheus_tsdb_wal_fsync_duration_seconds{quantile="0.9"} 0.014458005

 prometheus_tsdb_wal_fsync_duration_seconds{quantile="0.99"} 0.017316173
prometheus_tsdb_wal_fsync_duration_seconds_sum 2.888716127000002
prometheus_tsdb_wal_fsync_duration_seconds_count 216

从上面的样本中可以得知当前 Promtheus Server 进行wal_fsync 操作的总次数为 216次，耗时
**2.88871612700000 2s。其中中位数（ quantile=0.5 ）的耗时为 0.012352463 ，9分位数（ quantile=0.9 ）**
的耗时为 0.014458005s 。

**7、Prometheus 能监控什么？**
• Databases
• Hardware related
• Messaging systems
• Storage
• HTTP
• APIs
• Logging
•  Other monitoring systems
•  Miscellaneous
•  Software exposing Prometheus metrics

**7.1 DATABASES -数据库**
• Aerospike exporter
• ClickHouse exporter
• Consul exporter (official)
• Couchbase exporter
• CouchDB exporter
• ElasticSearch  exporter
• EventStore exporter
• Memcached  exporter (official)
• MongoDB exporter
• MSSQL server exporter
• MySQL server exporter (official)
• OpenTSDB  Exporter
• Oracle DB Exporter
• PgBouncer exporter
• PostgreSQL  exporter
• ProxySQL exporter
• RavenDB exporter
• Redis exporter
• RethinkDB exporter
• SQL exporter
• Tarantool metric library

 • Twemproxy

**7.2 HARDWARE  RELATED-硬件相关**
• apcupsd exporter
• Collins exporter
• IBM Z HMC exporter
• IoT Edison exporter
• IPMI exporter
• knxd exporter
• Netgear Cable Modem Exporter
• Node/system  metrics exporter (official)
• NVIDIA GPU exporter
• ProSAFE exporter
• Ubiquiti UniFi exporter

**7.3 Messaging systems -消息服务**
• Beanstalkd exporter
• Gearman exporter
• Kafka exporter
• NATS exporter
• NSQ exporter
• Mirth Connect exporter
• MQTT blackbox exporter
• RabbitMQ  exporter
• RabbitMQ Management Plugin exporter

**7.4 Storage-存储**
• Ceph exporter
• Ceph RADOSGW exporter
• Gluster exporter
• Hadoop HDFS  FSImage exporter
• Lustre exporter
• ScaleIO exporter

**7.5 http-网站服务**
• Apache exporter
• HAProxy exporter (official)
• Nginx metric library
• Nginx VTS exporter
• Passenger exporter
• Squid exporter
• Tinyproxy exporter
• Varnish exporter

 • WebDriver exporter

**7.6 API**
• AWS ECS exporter
• AWS Health exporter
• AWS SQS exporter
• Cloudflare exporter
• DigitalOcean exporter
• Docker Cloud  exporter
• Docker Hub  exporter
• GitHub exporter
• InstaClustr exporter
• Mozilla Observatory exporter
• OpenWeatherMap exporter
• Pagespeed exporter
• Rancher exporter
• Speedtest exporter

**7.7 Logging-日志**
• Fluentd exporter
• Google's mtail log data extractor
• Grok exporter

**7.8 Other monitoring systems**
• Akamai Cloudmonitor exporter
• Alibaba Cloudmonitor  exporter
• AWS CloudWatch exporter (official)
• Cloud Foundry  Firehose exporter
• Collectd exporter (official)
• Google Stackdriver exporter
• Graphite exporter (official)
• Heka dashboard exporter
• Heka exporter
• InfluxDB  exporter (official)
• JavaMelody exporter
• JMX exporter (official)
• Munin exporter
• Nagios / Naemon exporter
• New Relic exporter
• NRPE exporter
• Osquery exporter
• OTC CloudEye exporter
• Pingdom exporter

 • scollector exporter
• Sensu exporter
• SNMP exporter (official)
• StatsD exporter (official)

**7.9 Miscellaneous -其他**
• ACT Fibernet Exporter
• Bamboo exporter
• BIG-IP exporter
• BIND exporter
• Bitbucket exporter
• Blackbox  exporter (official)
• BOSH exporter
• cAdvisor
• Cachet exporter
• ccache exporter
• Confluence exporter
• Dovecot exporter
• eBPF exporter
• Ethereum Client e xporter
• Jenkins exporter
• JIRA exporter
• Kannel exporter
• Kemp LoadBalancer exporter
• Kibana Exporter
• Meteor JS web framework exporter
• Minecraft exporter module
• PHP-FPM exporter
• PowerDNS exporter
• Presto exporter
• Process exporter
• rTorrent exporter
• SABnzbd exporter
• Script exporter
• Shield exporter
• SMTP/Maildir MDA blackbox prober
• SoftEther exporter
• Transmission exporter
• Unbound exporter
• Xen exporter
**7.10 Software exposing Prometheus metrics -Prometheus 度量指标**
• App Connect Enterprise
• Ballerina

 • Ceph
• Collectd
• Concourse
• CRG Roller Derby Scoreboard (direct)
• Docker Daemon
• Doorman (direct)
• Etcd (direct)
• Flink
• FreeBSD Kernel
• Grafana
• JavaMelody
• Kubernetes (direct)
• Linkerd

**8、Prometheus 对kubernetes 的监控**
对于Kubernetes 而言，我们可以把当中所有的资源分为几类：
• 基础设施层（ Node） ：集群节点，为整个集群和应用提供运行时资源
• 容器基础设施（ Container ） ：为应用提供运行时环境
• 用户应用（ Pod）：Pod中会包含一组容器，它们一起工作，并且对外提供一个（或者一
组）功能
• 内部服务负载均衡（ Service） ：在集群内，通过 Service 在集群暴露应用功能，集群内
应用和应用之间访问时提供内部的负载均衡
• 外部访问入口（ Ingress） ：通过Ingress 提供集群外的访问入口，从而可以使外部客户
端能够访问到部署在 Kubernetes 集群内的服务

因此，如果要构建一个完整的监控体系，我们应该考虑，以下 5个方面：
• 集群节点状态监控：从集群中各节点的 kubelet 服务获取节点的基本运行状态；
• 集群节点资源用量监控：通过 Daemonset 的形式在集群中各个节点部署 Node Exporte r
采集节点的资源使用情况；
• 节点中运行的容器监控：通过各个节点中 kubelet 内置的cAdvisor 中获取个节点中所有
容器的运行状态和资源使用情况；
• 如果在集群中部署的应用程序本身内置了对 Prometheus 的监控支持，那么我们还应该找
到相应的 Pod实例，并从该 Pod实例中获取其内部运行状态的监控指标。
• 对k8s本身的组件做监控： apiserver 、scheduler 、controller -manager、kubelet、
kube-proxy

**9、node-exporter 组件安装和配置**
机器规划：
我的实验环境使用的 k8s集群是一个 master节点和一个 node节点
master节点的机器 ip是192.168.40.1 80，主机名是 xianchaomaster1
node节点的机器 ip是192.168.40.1 81，主机名是 xianchaonode1

**9.1 node-exporter 介绍？**
node-exporter 可以采集机器（物理机、虚拟机、云主机等）的监控指标数据，能够采集到的指标包
括CPU, 内存，磁盘，网络，文件数等信息。

**9.2 安装node-exporter**

```bash
[root@xianchaomaster1 ~]# kubectl create ns monitor -sa
```
把课件里的 node-exporter .tar.gz 镜像压缩包上传到 k8s的各个节点，手动解压：

```bash
[root@xianchaomaster1 ~]# docker load -i node-exporter.tar.gz
[root@xianchaonode1 ~]# docker load -i node-exporter.tar.gz
```
node-export.yaml文件在课件，可上传到自己 k8s的控制节点xianchaomaster1 ：
cat  node -export.yaml

```yaml
apiVersion: apps/v1
kind: DaemonSet  #可以保证 k8s集群的每个节点都运行完全一样的 pod
metadata:
  name: node -exporter
  namespace: monitor -sa
  labels:
    name: node -exporter
spec:
  selector:
    matchLabels:
     name: node -exporter
  template:
    metadata:
      labels:
        name: node -exporter
    spec:
      hostPID: true
      hostIPC: true
      hostNetwork: true
# hostNetwork 、hostIPC、hostPID 都为True时，表示这个 Pod里的所有容器，会直接使用宿主机的网
```
络，直接与宿主机进行 IPC（进程间通信） 通信，可以看到宿主机里正在运行的所有进程。
加入了hostNetwork:true 会直接将我们的宿主机的 9100端口映射出来，从而不需要创建 service 在我
们的宿主机上就会有一个 9100的端口
      containers:
      - name: node -exporter
        image: prom/node -exporter:v0.16.0
        ports:
        - containerPort: 9100
        resources:
          requests:
            cpu: 0.15   #这个容器运行至少需要 0.15核cpu

         securityContext:
          privileged: true   #开启特权模式
        args:
        - --path.procfs   #配置挂载宿主机（ node节点）的路径
        - /host/proc
        - --path.sysfs   #配置挂载宿主机（ node节点）的路径
        - /host/sys
        - --collector.filesystem.ignored -mount-points
        - '"^/(sys|proc|dev|host|etc)($|/)"'
#通过正则表达式忽略某些文件系统挂载点的信息收集
        volumeMounts:
        - name: dev
          mountPath: /host/dev
        - name: proc
          mountPath: /host/proc
        - name: sys
          mountPath: /host/sys
        - name: rootfs
          mountPath: /rootfs
#将主机/dev、/proc、/sys这些目录挂在到容器中，这 是因为我们采集的很多节点数据都是通过这
些文件来获取系统信息 的。
      tolerations:
      - key: "node -role.kubernetes.io/master"
        operator: "Exists"
        effect: "NoSchedule"
      volumes:
        - name: proc
          hostPath:
            path: /proc
        - name: dev
          hostPath:
            path: /dev
        - name: sys
          hostPath:
            path: /sys
        - name: rootfs
          hostPath:
            path: /

```bash
#通过kubectl apply 更新node-exporter .yaml文件
[root@xianchaomaster1]# kubectl apply -f node-export.yaml
#查看node-exporter 是否部署成功
[root@xianchaomaster1]# kubectl get pods -n monitor -sa
```

 显示如下，看到 pod的状态都是 running，说明部署成功
NAME                  READY   STATUS    RESTARTS   AGE
node-exporter -9qpkd   1/1     Running   0          89s
node-exporter -zqmnk   1/1     Running   0          89s

通过node-exporter 采集数据
curl  http://主机ip:9100/metrics

#node-export默认的监听端口是 9100，可以看到当前主机获取到的所有监控数据

curl http://192.168.40.1 80:9100/metrics | grep node_cpu_seconds
显示192.168.40.1 80主机cpu的使用情况

# HELP node_cpu_seconds_total Seconds the cpus spent in each mode.
# TYPE node_cpu_seconds_total counter
node_cpu_seconds_total{cpu="0",mode="idle"} 72963.37
node_cpu_seconds_total{cpu="0",mode="iowait"} 9.35
node_cpu_seconds_total{cpu="0",mode="irq"} 0
node_cpu_seconds_total{cpu="0",mode="nice"} 0
node_cpu_seconds_total{cpu="0",mode="softirq"} 151.4
node_cpu_seconds_total{cpu="0",mode="steal"} 0
node_cpu_seconds_total{cpu="0",mode="system"} 656.12
node_cpu_secon ds_total{cpu="0",mode="user"} 267.1

#HELP：解释当前指标的含义，上面表示在每种模式下 node节点的cpu花费的时间，以 s为单位
#TYPE：说明当前指标的数据类型，上面是 counter 类型
node_cpu_seconds_total{cpu="0",mode="idle"} ：
cpu0上idle进程占用 CPU的总时间， CPU占用时间是一个只增不减的度量指标，从类型中也可以看
出node_cpu 的数据类型是 counter（计数器）

counter 计数器：只是采集递增的指标

curl http://192.168.40.1 80:9100/metrics | grep node_load
# HELP node_load1 1m load average.
# TYPE node_load1 gauge
node_load1 0.1

node_load1 该指标反映了当前主机在最近 一分钟以内的负载情况，系统的负载情况会随系统资源的
使用而变化，因此 node_load1 反映的是当前状态，数据可能增加也可能减少，从注释中可以看出当前指
标类型为 gauge（标准尺寸）
gauge标准尺寸：统计的指标可增加可减少

**10、Prometheus  server安装和配置**

**10.1 创建sa账号，对sa做rbac授权**

```bash
#创建一个 sa账号monitor
[root@xianchaomaster1 ~]# kubectl create serviceaccount monitor -n monitor-sa
#把sa账号monitor 通过clusterrolebing 绑定到clusterrole 上
[root@xianchaomaster1 ~]# kubectl create clusterrolebinding monitor -clusterrolebinding
-n monitor -sa --clusterrole=cluster -admin  --serviceaccount=monitor -sa:monitor
```

**10.2 创建prometheus 数据存储目录**

```bash
#在k8s集群的xianchaonode 1节点上创建数据存储目录
[root@xianchaonode1 ~]# mkdir /data
[root@xianchaonode1 ~]# chmod 777 /data/
```

**10.3 安装Prometheus  server服务**
**10.3.1 创建一个 configmap 存储卷，用来存放 prometheus 配置信息**
prometheus -cfg.yaml 文件在课件，可 上传到k8s控制节点xianchaomaster 1上:

```bash
#通过kubectl apply更新configmap
[root@xianchaomaster1 prometheus]# kubectl apply  -f  prometheus -cfg.yaml
```
prometheus -cfg.yaml 文件内容如下：
---

```yaml
kind: ConfigMap
apiVersion: v1
metadata:
  labels:
    app: prometheus
  name: prometheus -config
  namespace: monitor -sa
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s  #采集目标主机监控据的时间 间隔
      scrape_timeout: 10s  # 数据采集超时时间 ，默认10s
      evaluation_interval: 1m   #触发告警检测的时间 ，默认是 1m
scrape_configs:
#scrape_configs ：配置数据源，称为 target，每个target用job_name 命名。又分为静态配置和服
```
务发现
    - job_name: 'kubernetes -node'
      kubernetes_sd_configs:
#使用的是 k8s的服务发现
      - role: node
# 使用node角色，它使用默认的 kubelet 提供的http端口来发现集群中每个 node节点。

       relabel_configs:
#重新标记
      - source_labels: [__address__]  #配置的原始标签，匹配地址
        regex: '(.*):10250'   #匹配带有 10250端口的url

        replacement: '${1}:9100'  # 把匹配到的 ip:10250 的ip保留
        target_label: __address__ # 新生成的 url是${1}获取到的 ip:9100
        action: replace
      - action: labelmap
#匹配到下面正则表达式的标签会被保留 ,如果不做 regex正则的话， 默认只是会显示 instance 标签
        regex: __meta_kubernetes_node_label_(.+)

> **注意：Before relabeling 表示匹配到的所有标签**

```bash
instance="xianchaomaster1"
Before relabeling:
__address__="192.168.40.180:10250"
__meta_kubernetes_node_address_Hostname="xianchaomaster1"
__meta_kubernetes_node_address_InternalIP="192.168.40.180"
__meta_kubernetes_node_annotation_kubeadm_alpha_kubernetes_io_cri_socket="/var/run/dockersh
im.sock"
__meta_kubernetes_node_annotation_node_alpha_kubernetes_io_ttl="0"
__meta_kubernetes_node_annotation_projectcalico_org_IPv4Address="192.168.40.180/24"
__meta_kubernetes_node_annotation_projectcalico_org_IPv4IPIPTunnelAddr="10.244.123.64"
__meta_kubernetes_node _annotation_volumes_kubernetes_io_controller_managed_attach_detach="t
rue"
__meta_kubernetes_node_label_beta_kubernetes_io_arch="amd64"
__meta_kubernetes_node_label_beta_kubernetes_io_os="linux"
__meta_kubernetes_node_label_kubernetes_io_arch="amd64"
__meta_kubernetes_node_label_kubernetes_io_hostname="xianchaomaster1"
__meta_kubernetes_node_label_kubernetes_io_os="linux"
__meta_kubernetes_node_label_node_role_kubernetes_io_control_plane=""
__meta_kubernetes_node_label_node_role_kubernetes_io_master=""

 __meta_kubernetes_node_name="xianchaomaster1"
__metrics_path__="/metrics"
__scheme__="http"
instance="xianchaomaster1"
job="kubernetes -node"

- job_name: 'kubernetes -node-cadvisor'
# 抓取cAdvisor 数据，是获取 kubelet 上/metrics/cadvisor 接口数据来获取容器的资源使用情况
      kubernetes_sd_configs:
      - role:  node
      scheme: https
      tls_config:
        ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
      bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
      relabel_configs:
      - action: labelmap   #把匹配到的标签 保留
        regex: __meta_kubernetes_node_label_(.+)
#保留匹配到的具有 __meta_kubernetes_node_label 的标签
      - target_label: __addre ss__
#获取到的地址： __address__="192.168.40.180:10250"
        replacement: kubernetes.default.svc:443
#把获取到的 地址替换成新的地址 kubernetes.default.svc:443
      - source_labels: [__meta_kubernetes_node_name]
        regex: (.+)
#把原始标签中 __meta_kubernetes_node_name 值匹配到
        target_label: __metrics_path__
#获取__metrics_path__ 对应的值
        replacement: /api/v1/nodes/${1}/proxy/metrics/cadvisor
#把metrics 替换成新的 值api/v1/nodes/xianchaomaster1/proxy/metrics/cadvisor
```
${1}是__meta_kubernetes_node_name 获取到的值

新的url就是
https://kubernetes.default.svc:443/api/v1/nodes/xianchaomaster1/proxy/metrics/cadvisor

    - job_name: 'kubernetes -apiserver'
      kubernetes_sd_configs:
      - role: endpoints
#使用k8s中的endpoint 服务发现 ，采集apiserver  6443端口获取到的数据
      scheme: https
      tls_config:
        ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
      bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token

       relabel_configs:
      - source_labels: [__meta_kubernetes_namespace
#endpoint 这个对象的名称空间
,__meta_kubernetes_service_name
#endpoint 对象的服务名
, __meta_kubernetes_endpoint_port_nam e
#exnpoint 的端口名称 ]
        action: keep   #采集满足条件的实例，其他实例不采集
        regex: default;kubernetes;https
#正则匹配到的默认空间下的 service 名字是kubernetes ，协议是 https的endpoint 类型保留下来

    - job_name: 'kubernetes -service-endpoints'
      kubernet es_sd_configs:
      - role: endpoints
      relabel_configs:
      - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_scrape]
        action: keep
        regex: true
# 重新打标仅抓取到的具有  "prometheus.io/scrape: true" 的annotation 的端点，意思是说如果
某个service具有prometheus.io/scrape = true annotation 声明则抓取 ，annotation 本身也是键值结
构，所以这里的源标签设置为键，而 regex设置值true，当值匹配到 regex设定的内容时则执行 keep动
作也就是保留，其余则丢弃 。
      - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_scheme]
        action: replace
        target_l abel: __scheme__
        regex: (https?)
#重新设置 scheme，匹配源标签 __meta_kubernetes_service_annotation_prometheus_io_scheme 也
就是prometheus.io/scheme annotation ，如果源标签的值匹配到 regex，则把值替换为 __scheme__ 对应
的值。
      - source_labels: [__meta_kubernetes_service_annotation_prometh eus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
# 应用中自定义暴露的指标，也许你暴露的 API接口不是 /metrics 这个路径，那么你可以在这个
POD对应的service 中做一个 "prometheus.io/path = /mymetrics" 声明，上面的意思就是把你声明的这
个路径赋值给 __metrics_path__ ，其实就是让 prometheus 来获取自定义应用暴露的 metrices 的具体路
径，不过这里写的要和 service 中做好约定 ，如果service 中这样写  prometheus.io/app -metrics-
path: '/metrics' 那么你这里就要
__meta_kubernetes_service_annotation_prometheus_io_app_metrics_path 这样写。

      - source_labels: [__address__,
__meta_kubernetes_service_annotation_prometheus_io_port]
        action: replace
        target_label: __address__
        regex: ([^:]+)(?:: \d+)?;(\d+)
        replacement: $1:$2
# 暴露自定义的应用的端口，就是把地址和你在 service 中定义的  "prometheus.io/port =
<port>" 声明做一个拼接 ，然后赋值给 __address__ ，这样prometheus 就能获取自定义应用的端口，然
后通过这个端口再结合 __metrics_path__ 来获取指标，如果 __metrics_path__ 值不是默认的 /metrics 那
么就要使用上面的标签替换来获取真正暴露的具体路径 。

      - action: labelmap  # 保留下面匹配到的标签
        regex: __meta_kubernetes_service_label_(.+ )
      - source_labels: [__meta_kubernetes_namespace]
        action: replace   #替换__meta_kubernetes_namespace 变成kubernetes_namespace
        target_label: kubernetes_namespace
      - source_labels: [__meta_kubernetes_service_name]
        action: replace
        target_label: kubernetes_name

```bash
#更新configmap 资源
[root@xianchaomaster1 prometheus]# kubectl apply -f prometheus -cfg.yaml
```

**10.3.2 通过deployment 部署prometheus**
安装prometheus 需要的镜像 prometheus -2-2-1.tar.gz 在课件，上传到 k8s的工作节点
xianchaonode 1上，手动解压：

```bash
[root@xianchaonode1 ~]# docker load -i prometheus -2-2-1.tar.gz
```
prometheus -deploy.yaml 文件在课件 里，上传到自己的 k8s的控制节点xianchaomaster1

```bash
#通过kubectl apply 更新prometheus
[root@xianchaomaster1]# kubectl apply -f prometheus -deploy.yaml
#查看prometheus 是否部署成功
[root@xianchaomaster1]# kubectl get pods -n monitor -sa
```
显示如下，可看到 pod状态是running，说明prometheus 部署成功
NAME                                 READY   STATUS    RESTARTS   AGE
node-exporter -9qpkd                  1/1     Running   0          76m
node-exporter -zqmnk                  1/1     Running   0          76m
prometheus -server-85dbc6c7f7 -nsg94   1/1     Running   0          6m7

> **注意：在上面的 prometheus -deploy.yaml 文件有个 nodeName 字段，这个就是用来指定创建的这个**
prometheus 的pod调度到哪个节点上，我们这里让 nodeName=xianchaonode1 ，也即是让 pod调度到
xianchaonode1 节点上，因为 xianchaonode1 节点我们创建了数据目录 /data，所以大家记住：你在 k8s
集群的哪个节点创建 /data，就让pod调度到哪个节 点，nodeName 根据你们自己环境主机去修改即可。

prometheus -deploy.yaml 文件内容如下：
---

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus -server
  namespace: monitor -sa
  labels:
    app: prometheus
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
      component: server
    #matchExpressions:
    #- {key: app, operator: In, values: [prometheus]}
    #- {key: component, operator: In, values: [server]}
  template:
    metadata:
      labels:
        app: prometheus
        component: server
      annotations:
        prometheus.io/scrape: 'false'
    spec:
      nodeName: xianchao node1
      serviceAccountName: monitor
      containers:
      - name: prometheus
        image: prom/prometheus:v2.2.1
        imagePullPolicy: IfNotPresent
        command:
          - prometheus
          - --config.file=/etc/prometheus/prometheus.yml
          - --storage.tsdb.path=/prometheus   #旧数据存储目录
          - --storage.tsdb.retention=720h     #何时删除旧数据，默认为 15天。
          - --web.enable -lifecycle    #开启热加载
        ports:
        - containerPort: 9090
          protocol: TCP
        volumeMounts:

         - mountPath: /etc/prometheus/prometheus.yml
          name: prometheus -config
          subPath: prometheus.yml
        - mountPath: /prometheus/
          name: prometheus -storage-volume
      volumes:
        - name: prometheus -config
          configMap:
            name: prometheus -config
            items:
              - key: prometheus.yml
                path: prometheus.yml
                mode: 0644
        - name: prometheus -storage-volume
          hostPath:
           path: /data
           type: Directory

```
**10.3.3 给prometheus pod 创建一个 service**

prometheus -svc.yaml 文件在课件，可上传到 k8s的控制节点xianchao master1 上：

```bash
#通过kubectl apply 更新service
[root@xianchaomaster1]# kubectl apply -f prometheus -svc.yaml
```

prometheus -svc.yaml 文件内容如下 ：
---

```yaml
apiVersion: v1
kind: Service
metadata:
  name: prometheus
  namespace: monitor -sa
  labels:
    app: prometheus
spec:
  type: NodePort
  ports:
    - port: 9090
      targetPort: 9090
      protocol: TCP
  selector:
    app: prometheus
    component: serve r

#查看service 在物理机映射的端口
```

```bash
[root@xianchaomaster1]# kubectl get svc -n monitor -sa
```
显示如下：
NAME         TYPE       CLUSTER -IP    EXTERNAL -IP   PORT(S)          AGE
prometheus   NodePort   10.96.45.93   <none>        9090:32732/TCP   50s

通过上面可以看到 service 在宿主机上映射的端口是 32732，这样我们访问 k8s集群的master1 节点
的ip:32732 ，就可以访问到 prometheus 的web ui界面了
#访问prometheus web ui 界面
火狐浏览器输入如下地址：
http://192.168.40.1 80:32732/graph
可看到如下页面：

#点击页面的 Status->Targets ，可看到如下 ,说明我们配置的服务发现可以正常采集数据

**10.3.4 Prometheus 热加载**
#为了每次修改配置文件可以热加载 prometheus ，也就是不停止 prometheus ，就可以使配置生效 ，
想要使配置生效可用如下热加载命令：

```bash
[root@xianchaomaster1 prometheus]# kubectl get pods -n monitor -sa -o wide -l
app=prometheus

#10.244. 121.4是prometheus 的pod的ip地址，如何查看 prometheus 的pod ip
```

想要使配置生效可用如下 命令热加载：

```bash
[root@xianchaomaster1]#  curl -X POST http://10.244.121.4:9090/ -/reload

#热加载速度比较慢，可以暴力重启 prometheus ，如修改上面的 prometheus -cfg.yaml 文件之后，可
```
执行如下强制删除：
kubectl delete -f prometheus -cfg.yaml
kubectl delete -f prometheus -deploy.yaml
然后再通过 apply更新：
kubectl apply -f prometheus -cfg.yaml
kubectl apply -f prometheus -deploy.yaml

> **注意：**
线上最好热加载，暴力删除可能造成监控数据的丢失

**11、可视化 UI界面Grafana 的安装和配置**
**11.1 Grafana 介绍**
Grafana 是一个跨平台的开源的度量分析和可视化工具，可以将采集的数据可视化的展示，并及时通
知给告警接收方 。它主要有以下六大特点：
**1、展示方式：快速灵活的客户端图表，面板插件有许多不同方式的可视化指标和日志，官方库中具**
有丰富的仪表盘插件，比如热图、折线图、图表等多种展示方式；
**2、数据源： Graphite ，InfluxDB ，OpenTSDB ，Prometheus ，Elasticsearch ，CloudWatch 和**
KairosDB 等；
**3、通知提醒：以可视方式定义最重要指标的警报规则， Grafana 将不断计算并发送通知，在数据达**
到阈值时通过 Slack、PagerDuty 等获得通知；
**4、混合展示：在同一图表中混合使用不同的数据源，可以基于每个查询指定数据源，甚至自定义数**
据源；
**5、注释：使用来自不同数据源的丰富事件注释图表，将鼠标悬停在事件上会显示完整的事件元数据**
和标记。

**11.2 安装Grafana**
安装Grafana 需要的镜像 heapster -grafana-amd64_v5_0_4.tar.gz, 把镜像上传到k8s的工作节点
xianchao node1上，手动解压：

```bash
[root@xianchaonod e1 ~]# docker load -i heapster -grafana-amd64_v5_0_4.tar.gz
```
grafana.yaml 文件在课件里，可上传到 k8s的控制节点：

更新yaml文件：

```bash
[root@xianchaomaster1 prometheus]# kubectl apply -f grafana.yaml

#查看grafana 是否创建成功：
[root@xianchaomaster1 prometheus]# kubectl get pods -n kube-system -l task=monitoring
```

显示如下，说明部署成功
NAME                                  READY   STATUS    RESTARTS   AGE
monitoring -grafana-675798bf47 -cw9hr   1/1     Running   0          39s

grafana.yaml 文件内容如下：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: monitoring -grafana
  namespace: kube -system
spec:
  replicas: 1

   selector:
    matchLabels:
      task: monitoring
      k8s-app: grafana
  template:
    metadata:
      labels:
        task: monitoring
        k8s-app: grafana
    spec:
      containers:
      - name: grafana
        image: k8s.gcr.io/heapster -grafana-amd64:v5.0.4
        ports:
        - containerPort: 3000
          protocol: TCP
        volumeMounts:
        - mountPath: /etc/ssl/certs
          name: ca -certificates
          readOnly: true
        - mountPath: /var
          name: grafana -storage
        env:
        - name: INFLUXDB_HOST
          value: monitoring -influxdb
        - name: GF_SERVER _HTTP_PORT
          value: "3000"
          # The following env variables are required to make Grafana accessible via
          # the kubernetes api -server proxy. On production clusters, we recommend
          # removing these env variables, setup auth fo r grafana, and expose the
grafana
          # service using a LoadBalancer or a public IP.
        - name: GF_AUTH_BASIC_ENABLED
          value: "false"
        - name: GF_AUTH_ANONYMOUS_ENABLED
          value: "true"
        - name: GF_AUTH_ANONYMOUS_OR G_ROLE
          value: Admin
        - name: GF_SERVER_ROOT_URL
          # If you're only using the API Server proxy, set this value instead:
          # value: /api/v1/namespaces/kube -system/services/monitoring -grafana/proxy
          value: /
      volumes:

       - name: ca -certificates
        hostPath:
          path: /etc/ssl/certs
      - name: grafana -storage
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  labels:
    # For use as a Cluster add -on
(https://github.com/kubernetes/kubernetes/tree/master/cluster/addons)
    # If you are NOT using this as an addon, you should comment out this line.
    kubernetes.io/cluster -service: 'true'
    kubernetes.io/name: monitoring -grafana
  name: monitoring -grafana
  namespace: kube -system
spec:
  # In a production setup, we recommend accessing Grafana through an external
Loadbalancer
  # or through a public IP.
  # type: LoadBalancer
  # You could also use NodePort to expose the service at a randomly -generated port
  # type: NodePort
  ports:
  - port: 80
    targetPort: 3000
  selector:
    k8s-app: grafana
  type: NodePort

```
**11.3 Grafana 界面接入 Prometheus 数据源**
查看grafana 前端的service

```bash
[root@xianchaomaster1]# kubectl get svc -n kube-system | grep grafana
```
显示如下：
monitoring -grafana     NodePort    10.106.3.47   <none>        80:30858/TCP
1）登陆grafana，在浏览器访问
**192.168.40.1 80:30858**
可看到如下界面：

2）配置grafana 界面：
开始配置 grafana 的web界面：
选择Create your first data source

出现如下

Name: Prometheus

```yaml
Type: Prometheus
```
HTTP 处的URL写 如下：

http://prometheus.monitor -sa.svc:9090
配置好的整体页面如下：

grafana 接入了

导入的监控模板，可在如下链接搜索
https://grafana.com/dashboards?dataSource=prometheus&search=kubernetes
可直接导入 node_exporter.json 监控模板，这个可以把 node节点指标显示出来
node_exporter.json 在课件里
可直接导入 docker_rev1.json ，显示容器资源指标的， docker_rev1.json 在课件里

怎么导入监控模板，按如下步骤 ：
上面Save & Test 测试没问题之后，就可以返回 Grafana 主页面

选择Upload json file ，出现如下

选择一个本地的 json文件，我们选择的是上面让大家下载的 node_exporter.json 这个文件，选择之
后出现如下 ：

> **注：箭头标注的地方 Name后面的名字是 node_exporter.json 定义的**

 Prometheus 后面需要变成 Prometheus ，然后再点击 Import，就可以出现如下界面：

导入docker_rev1.json 监控模板，步骤和上面导入 node_exporter.json 步骤一样，导入之后显示
如下：

扩展：如果Grafana 导入Prometheus z之后，发现仪表盘没有数据，如何排查？
**1、打开grafana 界面，找到仪表盘 对应无数据的图标**

Edit之后出现如下：

node_cpu_seconds_total  就是grafana 上采集的 cpu的时间， 需要到prometheus  ui界面看看采集
的指标是否是 node_cpu_seconds_total

如果在prometheus  ui界面输入 node_cpu_seconds_total 没有数据，那就看看是不是 prometheus
采集的数据是 node_cpu_seconds_total s，怎么看呢？

**12、安装kube-state-metrics 组件**
kube-state-metrics 是什么？
kube-state-metrics 通过监听 API Server生成有关资源对象的状态指标，比如 Deployment 、
Node、Pod，需要注意的是 kube-state-metrics 只是简单的提供一个 metrics 数据，并不会存储这
些指标数据，所以我们可以使用 Prometheus 来抓取这些数据然后存储，主要关注的是业务相关的一
些元数据，比如 Deployment 、Pod、副本状态等；调度了多少个 replicas ？现在可用的有几个？多
少个Pod是running/stopped/terminated 状态？Pod重启了多少次？我有多少 job在运行中。
安装kube-state-metrics 组件
1）创建sa，并对sa授权
在k8s的控制节点生成一个 kube-state-metrics-rbac.yaml 文件，kube-state-metrics-rbac.yaml
文件在课件，大家 上传到k8s的控制节点即可 ：
通过kubectl apply 更新资源清单 yaml文件

```bash
 [root@xianchaomaster1 prometheus]# kubectl apply -f kube-state-metrics-rbac.yaml
```

kube-state-metrics-rbac.yaml 文件内容如下：
---

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: kube -state-metrics
  namespace: kube -system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: kube -state-metrics
rules:
- apiGroups: [""]
  resources: ["nodes", "pods", "services", "resourcequotas", "replicationcontrollers",
"limitranges", "persistentvolumeclaims", "persistentvolumes", "namespaces",
"endpoints"]
  verbs: ["list", "watch"]
- apiGroups: ["extensions"]
  resources: ["daemonsets", "deployments", "replicasets"]
  verbs: ["list", "watch"]
- apiGroups: ["apps"]
  resources: ["statefulsets"]
  verbs: ["list", "watch"]
- apiGroups: ["batch"]
  resources: ["cronjobs", "jobs"]
  verbs: ["list", "watch"]
- apiGroups: ["autoscaling"]
  resources: ["horizontalpodautoscalers"]
  verbs: ["list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: kube -state-metrics
roleRef:
  apiGroup: rba c.authorization.k8s.io
  kind: ClusterRole
  name: kube -state-metrics
subjects:
- kind: ServiceAccount

   name: kube -state-metrics
  namespace: kube -system

```
2)安装kube-state-metrics 组件
安装kube-state-metrics 组件需要的镜像在课件，可上传到 k8s各个工作节点，手动解压：

```bash
[root@xianchaonode1 ~]# docker load -i kube-state-metrics_1_9_0.tar.gz
```
在k8s的控制节点生成一个 kube-state-metrics-deploy.yaml 文件，kube-state-metrics-
deploy.yaml 在课件， 可上传到 xianchaomaster 1节点：

通过kubectl apply 更新yaml文件

```bash
[root@xianchaomaster1 prometheus]# kubectl apply -f kube-state-metrics-deploy.yaml
```

kube-state-metrics-deploy.yaml 文件内容如下：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kube -state-metrics
  namespace: kube -system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kube -state-metrics
  template:
    metadata:
      labels:
        app: kube -state-metrics
    spec:
      serviceAccountName: kube -state-metrics
      containers:
      - name: kube -state-metrics
        image: quay.io/coreos/kube -state-metrics:v1.9.0
        ports:
        - containerPort: 8080

```
查看kube-state-metrics 是否部署成功

```bash
[root@xianchaomaster1]# kubectl get pods -n kube-system -l app=kube -state-metrics
```
显示如下，看到 pod处于running 状态，说明部署成功
kube-state-metrics-79c9686b96 -4njrs   1/1     Running   0          76s

3）创建service
在8s的控制节点生成一个 kube-state-metrics-svc.yaml 文件，kube-state-metrics-svc.yaml 文
件在课件，可上传到 k8s的xianchaomaster 1节点：

通过kubectl apply 更新yaml

```bash
[root@xianchaomaster1]# kubectl apply -f kube-state-metrics-svc.yaml
```

kube-state-metrics-svc.yaml 文件内容如下：

```yaml
apiVersion: v1
kind: Service
metadata:
  annotations:
    prometheus.io/scrape: 'true'
  name: kube -state-metrics
  namespace: kube -system
  labels:
    app: kube -state-metrics
spec:
  ports:
  - name: kube -state-metrics
    port: 8080
    protocol: TCP
  selector:
    app: kube -state-metrics

```
查看service 是否创建成功

```bash
[root@xianchaomaster1]# kubectl get svc -n kube-system | grep kube -state-metrics
```
显示如下，说明创建成功
kube-state-metrics   ClusterIP   10.105.53.102    <none>        8080/TCP

在grafana web 界面导入 Kubernetes Cluster (Prometheus) -1577674936972.json 和Kubernetes
cluster monitoring (via Prometheus) (k8s 1.16) -1577691996738.json ，Kubernetes Cluster
(Prometheus) -1577674936972.json 和Kubernetes cluster monitoring (via Prometheus) (k8s
1.16)-1577691996738.json 文件在课件
导入Kubernetes Cluster (Prometheus) -1577674936972.json 文件

导入之后出现如下页面

在grafana web 界面导入 Kubernetes cluster monitoring (via Prometheus) (k8s 1.16) -
1577691996738.json

导入之后 出现如下页面

**13、配置alertmanager -发送报警到 qq邮箱**

报警：指 prometheus 将监测到的异常事件发送给 alertmanager

    #创建alertmanager 配置文件
在k8s的控制节点创建 alertmanager -cm.yaml 文件，alertmanager -cm.yaml 文件在课件，可 上传到
k8s的xianchaomaster 1节点

通过kubectl apply 更新文件
kubectl apply -f alertmanager -cm.yaml

alertmanager -cm.yaml 文件内容如下：

```yaml
kind: ConfigMap
apiVersion: v1

 metadata:
  name: alertmanager
  namespace: monitor -sa
data:
  alertmanager.yml: | -
    global:
      resolve_timeout: 1m
      smtp_smarthost: 'smtp.163.com:25'
      smtp_from: '1501157 2657@163.com'
      smtp_auth_username: '1501157 2657'
      smtp_auth_password: ' BGWHYUOSOOHWEUJM '
      smtp_require_tls: false
    route:  # 用于配置告警分发策略
      group_by: [alertname] # 采用哪个标签来作为分组依据
      group_wait: 10s       # 组告警等待时间。也就是告警产生后等待 10s，如果有同组告警一
```
起发出
      group_interval: 10s    # 上下两组发送告警的间隔时间
      repeat_interval: 10m    # 重复发送告警的时间，减少相同邮件的发送频率 ，默认是 1h
      receiver: default -receiver  #定义谁来收告警
    receivers:
    - name: 'default -receiver'
      email_configs:
      - to: '1980570 647@qq.com'
        send_resolved: true

alertmanager 配置文件解释说明：
smtp_smarthost: 'smtp.163.com:25'
#163邮箱的SMTP服务器地址 +端口
smtp_from: '1501157 2657@163.com'
#这是指定从哪个邮箱发送报警
smtp_auth_username: '1501157 2657'
#这是发送邮箱的认证用户，不是邮箱名
smtp_auth_password: ' BGWHYUOSOOHWEUJM '
#这是发送邮箱的授权码而不是登录密码 ，你们需要用自己的 ，不要用 我的，用我的你会发不出来报
警

email_configs:
   - to: '1980570 647@qq.com'
#to后面指定发送到哪个邮箱，我发送到我的 qq邮箱，大家需要写自己的邮箱地址，不应该跟
smtp_from 的邮箱名字重复

  route:  # 用于设置告警的分发策略
      group_by: [alertname]

 #alertmanager 会根据group_by 配置将Alert分组
      group_wait: 10s
 # 分组等待时间。也就是告警产生后等待 10s，如果有同组告警一起发出
      group_interval: 10s   # 上下两组发送告警的间隔时间
      repeat_interval: 10m    # 重复发送告警的时间，减少相同邮件的发送频率 ，默认是 1h
      receiver: default -receiver  # 定义谁来收告警

Prometheus 一条告警的触发流程、等待时间
报警处理流程如下：
**1. Prometheus Server 监控目标主机上暴露的 http接口（这里假设接口 A） ，通过Promethes 配置的**
'scrape_interval' 定义的时间间隔，定期采集目标主机上监控数据。
**2. 当接口A不可用的时候， Server端会持续的尝试从接口中取数据，直到 "scrape_timeout" 时间后**
停止尝试。这时候把接口的状态变为 “DOWN” 。
**3. Prometheus 同时根据配置的 "evaluation_interval" 的时间间隔，定期（默认 1min）的对Alert**
Rule进行评估；当到达评 估周期的时候，发现接口 A为DOWN，即UP=0为真，激活 Alert，进入
“PENDING” 状态，并记录当前 active的时间；
**4. 当下一个 alert rule 的评估周期到来的时候，发现 UP=0继续为真，然后判断警报 Active的时间**
是否已经超出 rule里的‘for’ 持续时间，如果未超出，则进入下一个评估周期；如果时间超出，
则alert的状态变为 “FIRING” ；同时调用 Alertmanager 接口，发送相关报警数据。
**5. AlertManager 收到报警数据后，会将警报信息进行分组，然后根据 alertmanager 配置的**
“group_wait” 时间先进行等待。等 wait时间过后再发送报警信息。
**6. 属于同一个 Alert Group 的警报，在等待的过程中可能进入新的 alert，如果之前的报警已经成**
功发出，那么间隔 “group_interval” 的时间间隔后再重新发送报警信息。比如配置的是邮件报警，
那么同属一个 group的报警信息会汇总在一个邮件里进行发送。
**7. 如果Alert Group 里的警报一直没发生变化并且已经成功发送，等待 ‘repeat_interval’ 时间间**
隔之后再重复发送相同的报警邮件 ；如果之前的警报没有成功发送，则相当于触发第 6条条件，则需
要等待group_interval 时间间隔后重复发送。

同时最后至于警报信息具体发给谁，满足什么样的条件下指定警报接收人，设置不同报警发送频率，
这里有alertmanager 的route路由规则进行配置。

#创建prometheus 和告警规则配置文件
在k8s的控制节点生成一个 prometheus -alertmanager -cfg.yaml 文件，prometheus -alertmanager -
cfg.yaml 文件在课件，上传到 k8s的xianchaomaster 1节点

通过kubectl apply 更新资源文件

```bash
[root@xianchaomaster1]# kubectl delete -f prometheus -cfg.yaml
[root@xianchaomaster1]# kubectl apply -f prometheus -alertmanager -cfg.yaml
```

> **注意：prometheus -alertmanager -cfg.yaml 文件大家做实验需要修改，修改内容如下：**
    - job_name: 'kubernetes -schedule'
      scrape_interval: 5s

       static_configs:
      - targets: ['192.168.40.180:10251']   #scheduler 组件所在节点的 ip
    - job_name: 'kubernetes -controller -manager'
      scrape_interval: 5s
      static_configs:
      - targets: ['192.168.40.180:10252']
    - job_name: 'kubernetes -kube-proxy'
      scrape_interval: 5s
      static_configs:
      - targets: ['192.168.40.180:10249','192.168.40.181:10249']
#kube-proxy组件所在节点的 ip
    - job_name: 'kubernetes -etcd'
      scheme: https
      tls_config:
        ca_file: /var/run/secrets/kubernetes.io/k8s -certs/etcd/ca.crt
        cert_file: /var/run/secrets/kubernetes.io/k8s -certs/etcd/server.crt
        key_file: /var/run/secrets/kubernetes.io/k8s -certs/etcd/server.key
      scrape_interval: 5s
      static_configs:
      - targets: ['192.168.40.180:2379']
     #etcd组件所在节点的 ip

#安装prometheus 和alertmanager
需要把alertmanager.tar.gz 镜像包上传的 k8s的各个工作节点 ，手动解压：

```bash
[root@xianchaonode1 ~]# docker load -i alertmanager.tar.gz
```

在k8s的控制节点生成一个 prometheus -alertmanager -deploy.yaml 文件，prometheus -
alertmanager -deploy.yaml 文件在课件，可上传到 k8s的控制节点xianchaomaster 1上：

> **注意：配置文件指定了 nodeName: xianchaonode 1，这个位置要写你自己环境的 k8s的node节点名字**

生成一个 etcd-certs，这个在部署 prometheus 需要

```bash
[root@xianchaomaster1]# kubectl -n monitor -sa create secret generic etcd-certs --from-
file=/etc/kubernetes/pki/etcd/server.key  --from-
file=/etc/kubernetes/pki/etcd/server.crt --from-file=/etc/kubernetes/pki/etcd/ca.crt
```

通过kubectl apply 更新资源清单 yaml文件

```bash
[root@xianchaomaster1# kubectl delete -f prometheus -deploy.yaml
[root@xianc haomaster1]# kubectl apply -f prometheus -alertmanager -deploy.yaml
#查看prometheus 是否部署成功
[root@xianchaomaster1]# kubectl get pods -n monitor -sa | grep prometheus
#显示如下，说明创建成功：

 prometheus -server-6bfc4755f6 -cn487   2/2     Running   0          16s

#部署alertmanager 的service，方便在浏览器访问
```
在k8s的控制节点生成一个 alertmanager -svc.yaml 文件，alertmanager -svc.yaml 文件在课件里，
可上传到 k8s的控制节点xianchaomaster 1：

通过kubectl apply 更新yaml文件

```bash
[root@xianchaomaster 1]# kubectl apply -f alertmanager -svc.yaml
```

alertmanager -svc.yaml 文件内容如下 :
---

```yaml
apiVersion: v1
kind: Service
metadata:
  labels:
    name: prometheus
    kubernetes.io/cluster -service: 'true'
  name: alertmanager
  namespace: monitor -sa
spec:
  ports:
  - name: alertmanager
    nodePort: 30066
    port: 9093
    protocol: TCP
    targetPort: 9093
  selector:
    app: prometheus
  sessionAffinity: None
  type: NodePort

#查看service 在物理机映射的端口
kubectl get svc -n monitor -sa
```
显示如下：
NAME           TYPE       CLUSTER -IP       EXTERNAL -IP   PORT(S)          AGE
alertmanager   NodePort   10.101.253.221   <none>        9093: 30066/TCP   20s
prometheus     NodePort   10.103.243.87    <none>        9090:32732/TCP   96m

> **注意：上面可以看到 prometheus 的service 在物理机映射 的端口是 32732，alertmanager 的**
service 在物理机映射 的端口是 30066
http://192.168.40.180:30066/#/alerts

访问prometheus 的web界面

从上面可以发现 kubernetes -controller -manager和kubernetes -schedule 都显示连接不上对应的端
口
可按如下方法处理 ：
vim /etc/kubernetes/manifests/kube -scheduler.yaml
修改如下内容：
把--bind-address=127.0.0.1 变成--bind-address=192.168.40.1 80
把httpGet: 字段下的 hosts由127.0.0.1 变成192.168.40.1 80
把—port=0删除
#注意：192.168.40.1 80是k8s的控制节点xianchaomaster 1的ip
vim /etc/kubernetes/manifests/kube -controller -manager.yaml

 把--bind-address=127.0.0.1 变成--bind-address=192.168.40.130
把httpGet: 字段下的 hosts由127.0.0.1 变成192.168.40.1 80
把—port=0删除

修改之后在 k8s各个节点执行
systemctl restart kubelet

kubectl get cs
显示如下 :
NAME                 STATUS    MESSAGE             ERROR
controller -manager   Healthy   ok
scheduler            Healthy   ok
etcd-0               Healthy   {"health":"true"}

ss -antulp | grep :10251
ss -antulp | grep :10252
可以看到相应的端口已经被物理机监听了

kubernetes -kube-proxy显示如下：

是因为kube-proxy默认端口 10249是监听在 127.0.0.1 上的，需要改成监听到物理节点上，按如下
方法修改，线上建议在安装 k8s的时候就做修改，这样风险小一些：
kubectl edit configmap kube -proxy -n kube-system
把metricsBindAddress 这段修改成 metricsBindAddress: 0.0.0.0:10249
然后重新启动 kube-proxy这个pod

```bash
[root@xianchaomaster1]# kubectl get pods -n kube-system | grep kube -proxy |awk '{print
$1}' | xargs kubectl delete pods -n kube-system
[root@xianchaomaster1]# ss  -antulp |grep :10249
```
可显示如下
    tcp    LISTEN     0      128    [::]:10249              [::]:*

把controller -manager的cpu使用率大于 90%展开，可看到如下

FIRING表示prometheus 已经将告警发给 alertmanager ，在Alertmanager 中可以看到有一个
alert。
登录到alertmanager web 界面
浏览器输入 192.168.40.1 80:30066，显示如下

这样我在我的 qq邮箱，1980570647@qq.com 就可以收到报警了，如下

扩展：暴力更新配置文件
修改prometheus 任何一个配置文件之后，可 通过kubectl apply 使配置生效 ，执行顺序如下：
kubectl delete -f alertmanager -cm.yaml
kubectl apply -f alertmanager -cm.yaml
kubectl delete -f prometheus -alertmanager -cfg.yaml
kubectl apply   -f prometheus -alertmanager -cfg.yaml
kubectl delete -f  prometheus -alertmanager -deploy.yaml
kubectl apply   -f prometheus -alertmanag er-deploy.yaml

**14、配置alertmanager -发送报警到 钉钉**
打开电脑版钉钉创建机器人
1.创建钉钉机器人
打开电脑版钉钉，创建一个群，创建自定义机器人，按如下步骤创建
https://ding -doc.dingtalk.com/doc#/serverapi2/qf2nxq

https://developers.dingtalk.com/document/app/custom -robot-access

我创建的机器人如下：
群设置-->智能群助手 -->添加机器人 -->自定义-->添加

机器人名称： test
接收群组：钉钉报警测试

 安全设置：
自定义关键词： cluster1

上面配置好之后点击完成即可，这样就会创建一个 test的报警机器人，创建机器人成功之后怎么查
看webhook，按如下：

置界面
出现如下内容：
机器人名称： test
接受群组：钉钉报警测试
消息推送：开启

webhook：
https://oapi.dingtalk.com/robot/send?access_token=8a53475677339a11cec453c608543c3d85ea73
b330ea70c4b2de96a0839cbb90

安全设置：
自定义关键词： cluster1

2.安装钉钉的 webhook 插件，在 k8s的控制节点xianchaomaster 1操作
tar zxvf prometheus -webhook-dingtalk -0.3.0.linux -amd64.tar.gz
prometheus -webhook-dingtalk -0.3.0.linux -amd64.tar.gz 压缩包所在的百度网盘地址如下：
链接：https://pan.baidu.com/s/1_HtVZsItq2KsYvOlkIP9DQ
提取码： d59o

cd prometheus -webhook-dingtalk -0.3.0.linux -amd64
启动钉钉报警插件
nohup ./prometh eus-webhook-dingtalk --web.listen -address="0.0.0.0:8060" --
ding.profile="cluster1= https://oapi.dingtalk.com/robot/send?access _token=8a53475677339a1
1cec453c608543c3d85ea73b330ea70c4b2de96a0839cbb90 " &

对原来的 alertmanager -cm.yaml 文件做备份
cp alertmanager -cm.yaml alertmanager -cm.yaml.bak
重新生成一个新的 alertmanager -cm.yaml 文件

cat >alertmanager -cm.yaml <<EOF

```yaml
kind: ConfigMap
apiVersion: v1
metadata:
  name: alertmanager
  namespace: monitor -sa
data:

   alertmanager.yml: | -
    global:
      resolve_timeout: 1m
      smtp_smarthost: 'smtp.163.com:25'
      smtp_from: '1501157 2657@163.com'
      smtp_auth_username: '1501157****'
      smtp_auth_password: ‘BGWHYUOSOOHWEUJM '
      smtp_require_tls: false
    route:
      group_by: [alertname]
      group_wait: 10s
      group_interval: 10s
      repeat_interval: 10m
      receiver: cluster1
    receivers:
    - name: cluster1
      webhook_configs:
      - url: 'http://192.168.40.1 80:8060/dingtalk/cluster1/send'
        send_resolved: true
EOF

```
修改prometheus 任何一个配置文件之后，可 通过kubectl apply 使配置生效 ，执行顺序如下：
kubectl  delete -f  alertmanager -cm.yaml
kubectl apply  -f alertmanager -cm.yaml
kubectl  delete -f prometheus -alertmanager -cfg.yaml
kubectl  apply  -f prometheus -alertmanager -cfg.yaml
kubectl  delete -f  prometheus -alertmanager -deploy.yaml
kubectl  apply  -f prometheus -alertmanager-deploy.yaml

登陆网址：
https://work.weixin.qq.com/

找到应用管理，创建应用
应用名字 wechat
创建成功之后显示如下：

AgentId：1000003
Secret：Ov5SWq_JqrolsOj6dD4Jg9qaMu1TTaDzVTCrXHcjlFs

2.修改alertmanager -cm.yaml

global:
    smtp_smarthost: 'smtp.163.com:25'
    smtp_from: '1501157 2657@163.com'
    smtp_auth_username: '1501157 2657'
    smtp_auth_password: ' BGWHYUOSOOHWEUJM '
    smtp_require_tls: false
route:
    group_by: [alertname]
    group_wait: 10s
    group_interval: 10s
    repeat_interval: 3m
    receiver: "prometheus"
receivers:
- name: 'prometheus'
  wechat_configs:
  - corp_id: wwa82df90a693abb15
    to_user: '@all '
    agent_id: 1000003
    api_secret: Ov5SWq_JqrolsOj6dD4Jg9qaMu1TTaDzVTCrXHcjlFs

参数说明：

 wechat是本人自创建应用名称
corp_id: 企业信息 ("我的企业 "--->"CorpID"[ 在底部])
wechat是自创建应用名称  #在这创建的应用名字是 wechat，那么在配置 route时，receiver 也应该
是Prometheus
to_user: '@all' : 发送报警到所有人

3.配置自定义告警模板
cat template_wechat.tmpl
{{ define "wechat.default.message" }}
{{ range .Alerts }}
========start==========
告警程序： node_exporter
告警名称： {{ .Labels.alertname }}
故障主机 : {{ .Labels.instance }}
告警主题 : {{ .Annotations.summary }}
告警信息 : {{ .Annotations.description }}
========end==========
{{ end }}
{{ end }}

**16、Prometheus  PromQL语法**
PromQL（Prometheus Query Language ）是 Prometheus 自己开发的表达式语言，语言表现力很丰
富，内置函 数也很多。使用它可以对时序数据进行筛选和聚合。

**16.1 数据类型**
PromQL 表达式计算出来的值有以下几种类型：
瞬时向量  (Instant vector): 一组时序，每个时序只有一个采样值
区间向量  (Range vector): 一组时序，每个时序包含一段时间内的多个采样值
标量数据  (Scalar): 一个浮点数
字符串 (String): 一个字符串，暂时未用

**16.1.1 瞬时向量 选择器**
瞬时向量选择器用来选择一组时序在某个采样点的采样值。
最简单的情况就是指定一个度量指标，选择出所有属于该度量指标的时序的当前采样值。比如下面的表
达式：
apiserver_request_total

 可以通过在后面添加用大括号包围起来的一组标签键值对来对时序进行过滤。比如下面的表达式筛
选出了 job 为 kubernetes -apiserver s，并且 resource 为 pod的时序：
apiserver_request_total{job="kubernetes -apiserver",resource="pods"}

匹配标签值时可以是等于，也可以使用正则表达式。总共有下面几种匹配操作符：
=：完全相等
!=： 不相等
=~： 正则表达式匹配
!~： 正则表达式不匹配

下面的表达式筛选出了 container 是kube-scheduler 或kube-proxy或kube-apiserver 的时序数据
container_processes{container=~"kube -scheduler|kube -proxy|kube -apiserver"}

**16.1.2 区间向量选择器**
区间向量选择器类似于瞬时向量选择器，不同的是它选择的是过去一段时间的采样值。可以通过在
瞬时向量选择器后面添加包含在  [] 里的时长来得到区间向量选择器。比如下面的表达式选出了所有度
量指标为 apiserver_request_total 且resource 是pod的时序在过去 1 分钟的采样值。

apiserver_request_total{job="kubernetes -apiserver",resource="pods"}[ 1m]

这个不支持 Graph，需要选择 Console，才会看到采集的数据

说明：时长的单位可以是下面几种之一：
s：seconds
m：minutes
h：hours
d：days
w：weeks
y：years

**16.1.3 偏移向量选择器**
前面介绍的选择器默认都是以当前时间为基准时间，偏移修饰器用来调整基准时间，使其往前偏移

 一段时间。偏移修饰器紧跟在选择器后面，使用  offset 来指定要偏移的量。比如下面的表达式选择度
量名称为 apiserver_request_total 的所有时序在  5 分钟前的采样值。
apiserver_request_total{job="kubernetes -apiserver",resource="pods"}  offset 5m

下面的表达式选择 apiserver_request_tota l 度量指标在  1 周前的这个时间点过去  5 分钟的采样
值。
apiserver_request_total{job="kubernetes -apiserver",resource="pods"} [5m] offset 1w

**16.1.4 聚合操作符**
PromQL 的聚合操作符用来将向量里的元素聚合得更少。总共有下面这些聚合操作符：
sum：求和
min：最小值
max：最大值
avg：平均值
stddev：标准差
stdvar：方差
count：元素个数
count_values ：等于某值的元素个数
bottomk：最小的  k 个元素
topk：最大的  k 个元素
quantile ：分位数

如：
计算xianchaomaster1 节点所有容器总计内存
sum(container_memory_usage_bytes{instance=~"xianchaomaster1"})/1024/1024/1024

计算xianchaomaster1 节点最近1m所有容器 cpu使用率
sum (rate (container_cpu_usage_seconds_total{instance=~"xianchaomaster1"}[1m])) / sum
(machine_cpu_cores{  instance =~"xianchaomaster1"}) * 100

计算最近 1m所有容器 cpu使用率
sum (rate (container_cpu_usage_seconds_total{id!="/"}[1m])) by (id)
#把id会打印出来
结果如下：

**16.1.5 函数**
Prometheus 内置了一些函数来辅助计算，下面介绍一些典型的。
abs()：绝对值
sqrt()：平方根

 exp()：指数计算
ln()：自然对数
ceil()：向上取整
floor()：向下取整
round()：四舍五入取整
delta()：计算区间向量里每一个时序第一个和最后一个的差值
sort()：排序

**17、Prometheus 监控扩展**

**1、promethues 采集 tomcat 监控数据**
笔记：

https://note.youdao.com/ynoteshare1/index.html?id=0ddfc17eaf7bac94ad4497d7f535
6213&type=note

**2、promethues 采集 redis 监控数据**
笔记：
https://note.youdao.com/ynoteshare1/index.html?id=b9f87092ce8859cd583967677ea
332df&type=note

**3、Prometheus 监控 mysql**

```bash
[root@xianchaomaster1 prometheus]# yum install mysql -y
[root@xianchaomaster1 prometheus]# yum install mariadb  -y

tar -xvf mysqld_exporter -0.10.0.linux -amd64.tar.gz
cd mysqld_exporter -0.10.0.linux -amd64
cp -ar mysqld_exporter /usr/local/bin/
chmod +x /usr/local/bin/mysqld_exporter
```

2.登陆 mysql 为mysql_exporter 创建账号并授权
# 创建数据库用户。
mysql> CREATE USER 'mysql_exporter'@'localhost' IDENTIFIED BY 'Abcdef123!.';

# 对mysql_exporter 用户授权
mysql> GRANT PROCESS, REPLICATION CLIENT, SELECT ON *.* TO
'mysql_exporter'@'localhost';

exit 退出 mysql

3.创建 mysql 配置文件、运行时可免密码连接数据库：
cd mysqld_exporter -0.10.0.linux -amd64

 cat my.cnf
[client]

```bash
user=mysql_exporter
password=Abcdef123!.
```

4.启动 mysql_exporter 客户端
nohup ./mysqld_exporter --config.my -cnf=./my.cnf &

mysqld _exporter 的监听端口是 9104

5.修改 prometheus -alertmanager -cfg.yaml 文件，添加如下
  - job_name: 'mysql'
    static_configs:
    - targets: ['192.168.40.180:9104']

kubectl apply -f prometheus -alertmanager -cfg.yaml
kubectl delete -f prometheus -alertmanager -deploy.yaml
kubectl apply -f prometheus -alertmanager -deploy.yaml

grafana导入mysql监控图表
mysql -overview_rev5.json

**4、Prometheus 监控 Nginx**
笔记：
https://note.youdao.com/ynoteshare1/index.html?id=bea7b4b8f9a78db1679e1ac2ab7
47da5&type=note

**5、prometheus 监控 mongodb**
笔记：
https://note.youdao.com/ynoteshare1/index.html?id=39b54acb1fbc0199f966115ce952
3bb6&type=note

**18、Pushgateway**

 Pushgateway 简介：
Pushgateway 是prometheus 的一个组件， prometheus  server 默认是通过 exporter 主动获取
数据（默认采取 pull 拉取数据） ， pushgateway 则是通过被动方式推送数据到 prometheus  server ，
用户可以写一些自定义的监控脚本把需要监控的数据发送给 pushgateway ， 然后 pushgateway 再把
数据发送给 Prometheus  server

Pushgateway 优点：
Prometheus 默认采用定时 pull 模式拉取 targets 数据，但是如果不在一个子网或者防火墙，

 prometheus 就拉取不到 targets 数据，所以可以采用各个 target 往pushgateway 上push 数据，然
后prometheus 去pushgateway 上定时 pull 数据
在监控业务数据的时候，需要将不同数据汇总 , 汇总之后的数据可以由 pushgateway 统一收集，然
后由 Prometheus 统一拉取。

pushgateway 缺点：
Prometheus 拉取状态只针对  pushgateway, 不能对每个节点都有效；
Pushg ateway 出现问题，整个采集到的数据都会出现问题
监控下线， prometheus 还会拉取到旧的监控数据，需要手动清理  pushgateway 不要的数据。

安装 pushgateway ，在 k8s-node 节点（ 192.168. 40.18 1）操作 ：
在k8s-node 节点操作

```bash
[root@xianchaonode1 ~]# docker load -i pushgateway.tar.gz
[root@xianchaonode1 ~]# docker run -d --name pushgateway -p 9091:9091
prom/pushgateway
```
在浏览器访问 192.168. 40.18 1:9091 出现如下 ui界面

修改 prometheus -alertmanager -cfg.yaml 文件，在 k8s-master 节点操作
添加如下 job
- job_name: 'pushgateway'
      scrape_interval: 5s
      static_configs:
      - targets: ['192.168. 40.181 :9091']
  honor_labels: tru e

kubectl apply -f prometheus -alertmanager -cfg.yaml
kubectl delete -f prometheus -alertmanager -deploy.yaml
kubectl apply -f prometheus -alertmanager -deploy.yaml

在prometheus 的targets 列表可以看到 pushgateway

推送指定的数据格式到 pushgateway

向 {job=" test_job"} 添加单条数据：
echo  " metric 3. 6" | curl --data-binary @ -
http:// 192.168. 40.181:9091/metrics/job/ test_job

> **注：--data-binary 表示发送二进制数据，注意：它是使用 POST 方式发送的！**

添加复杂数据
cat <<EOF | curl --data-binary @ -
http:// 192.168. 40.181 :9091/metrics/job/ test_job/instance/ test_instance
#TYPE node_memory_usage  gauge
node_m emory _usage 36
# TYPE memory _total  gauge
node_m emory _total 36000
EOF

删除某个组下某个实例的所有数据
curl -X DELETE http: //192.168. 40.181 :9091/metrics/job/test_job/instance/test_instance

删除某个组下的所有数据：
curl -X DELETE http: //192.168. 40.181 :9091/metrics/job/test_job

把数据上报到 pushgateway
在被监控服务所在的机器配置数据上报 ,想要把 192.168.40.181 这个机器的内存数据上报到
pushgateway ，下面步骤需要在 192.168.40.181 操作

 cat push.sh

node _memory_usages=$ (free -m | grep Mem | awk '{print $3/$2*100}')

```bash
job_name="memory"
instance_name="192.168. 40.181 "
cat <<EOF | curl --data-binary @ -
http://192.168. 40.181 :9091/metrics/job/$job_ name/instance/$instance_name
#TYPE node_memory_usages   gauge
node_memory_usages $node_memory_usages
EOF

sh push.sh
```

打开 pushgateway  web ui界面，可看到如下：

打开 prometheus  ui界面，可看到如下 node_memory_usages 的metrics 指标

设置计划任务，定时上报数据
chmod  +x push. sh

crontab -e
*/1 * * * * /usr/bin/bash  /root/push.sh

> **注意：从上面配置可以看到，我们上传到 pushgateway 中的数据有 job也有 instance ，而**
prometheus 配置 pushgateway 这个 job_name 中也有 job和instance ，这个 job和instance 是
指pushgateway 实例本身， 添加 honor_labels: true 参数，  可以避免 promethues 的targets 列
表中的 job_name 是pushgateway 的 job 、insta nce 和上报到 pushgateway 数据的 job和
instance 冲突。


