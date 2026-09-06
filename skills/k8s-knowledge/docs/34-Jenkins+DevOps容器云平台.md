k8s集群：        k8s的控制节点
ip：192.168.40.180
主机名： xianchaomaster1
配置：6vCPU/6Gi内存

k8s的工作节点：

 ip：192.168.40.181
主机名： xianchaonode1
配置：6vCPU/8Gi内存

1.k8s助力DevOps在企业落地实践

**1.1 传统方式部署项目为什么发布慢，效率低？**

**1.2 上线一个功能，有多少时间被浪费了？**

**1.3 如何解决发布慢，效率低的问题呢？**

**1.5 什么是DevOps？**

**1.5.1 敏捷开发**
提高开发效率，及时跟进用户需求，缩短开发周期。

敏捷开发包括编写代码和构建代码两个阶段，可以使用 git或者svn来管理代码，用 maven对代码
进行构建

**1.5.2 持续集成（ CI）**
持续集成强调开发人员提交了新代码之后，立刻自动的进行构建、 （单元）测试。根据测试结果，我
们可以确定新代码和原有代码能否正确地集成在一起。持续集成过程中很重视自动化测试验证结果，对
可能出现的一些问题进行预警，以保障最终合并的代码没有问题。
常见的持续集成工具：
**1. Jenkins**
Jenkins 是用Java语言编写的，是目前使用最多和最受欢迎的持续集成工具， 使用Jenkins，可以
自动监测到 git或者svn存储库代码的更新，基于最新的代码进行构建 ，把构建好的源码或者镜像发布
到生产环境。 Jenkins 还有个非常好的功能 ：它可以在多台机器上进行分布式地构建和负载测试
**2. TeamCity**
**3. Travis CI**
**4. Go CD**
**5. Bamboo**
**6. GitLab CI**
**7. Codeship**

它的好处主要有 以下几点：
1）较早的发现错误： 每次集成都通过自动化的构建（包括编译，发布，自动化测试）来验证，哪个
环节出现问题都可以较早的发现
2）快速的发现错误 ：每完成一部分代码的 更新，就 会把代码 集成到主干 中，这样就可以快速 的发现
错误，比较容易的定位错误
3）提升团队绩效： 持续集成中代码更新速度快，能及时发现小问题并进行修改，使团队能创造出更
好的产品
4）防止分支 过多的偏离主干 ：经常持续集成，会使分支代码经常向主干更新， 当单元测试失败或者
出现bug，如果开发者需要在没有调试的情况下恢复仓库的代码到没有 bug的状态，只有很小部分的代码
会丢失
持续集成的目的 是提高代码质量，让产品快速的更新迭代 。它的核心措施是，代码集成到主干之
前，必须通过自动化测试。只要有一个测试用例失败，就不能集成。
Martin Fowler 说过，"持续集成并不能消除 Bug，而是让它们非常容易发现和改正。 "
互动：Martin Fowler 是谁？
马丁·福勒

马丁·福勒是一个软件开发方面的著作者和国际知名演说家，专注于面向对象分析与设计，统一建
模语言，领域建模，以及敏捷软件开发方法，包括极限编程。
与持续集成相关的 还有持续交付和持续部署。
**1.5.3 持续交付**
持续交付在持续集成的基础上，将集成后的代码部署到更贴近真实运行环境的「类生产环境」
（production -like environments ）中。交付给质量团队或者用户，以供评审 。如果评审通过，代码就
进入生产阶段。
如果所有的代码完成之后一起交付，会导致很多问题爆发出来，解决起来很麻烦，所以持续集成，
也就是没更新一次代码，都向下交付一次，这样可以及时发现问题，及时解决，防止问题大量堆积。
**1.5.4 持续部署**
持续部署是指当交付的代码通过评审之后，自动部署到生产环境中。持续部署是持续交付的最高阶
段。
Puppet，SaltStack 和Ansible 是这个阶段使用的流行工具。容器化工具在部署阶段也发挥着重要作
用。 Docker和k8s是流行的工具，有助于在开发，测试和生产环境中实现一致性。  除此之外， k8s还
可以实现自动扩容缩容等功能。

互动：举个例子，形象说明持续集成、 持续交付、持续部署之间的关系

2.为什么大厂都在用 DevOps？
**2.1 神州泰岳 DevOps生态体系建设与实践 -神州泰岳云资源运营事业部经理张凯分享**
传统软件服务企业的痛点 ?

解决之道： DevOps

本图摘自：张乐 -《DevOps道法术器》

**2.2 DevOps在金融行业的应用 -张安全分享**
标准的敏捷开发流程：

**2.3 哪些企业在用 DevOps？**

**2.4 DevOps在5G领域的的展望**

3.K8S在DevOps中的核心作用
Docker和K8S的出现使 DevOps变得更加普及，更加容易实现。在传统运维中我们服务时需要针对不
同的环境去安装不同的版本，部署方式也杂、多。那么有了 docker之后，一次构建、到处运行，我们只
需要要构建一次镜像，那么只要有 docker的主机，就可以基于镜像把应用跑起来。

互动：docker可以实现 DevOps的这个思想，但是存在一个问题，什么问题呢？

在众多微服务中，我们每天可能需要去处理各种服务的崩溃，而服务间的依赖调用关系也及其复
杂，这对我们解决问题带来了很大的复杂度。要很好的解决这个问题。我们就需要用到容器编排工具。

Kubernetes 的出现主宰了容器编排的市场，也进化了过去的运维方式，将开发与运维 联系的更加紧
密。而且让 DevOps 这一角色变得更加清晰 ，它是目前可用的很流行的容器解决方案之一。
**3.1 自动化**
敏捷开发 ->持续集成 ->持续交付 ->持续部署
**3.2 多集群管理**
可以根据客户需求对开发，测试，生产环境部署多套 kubernetes 集群，每个环境使用独立的物理资
源，相互之间避免影响

**3.3 多环境一致性**
Kubernetes 是基于docker的容器编排工具， 因为容器的镜像是不可变的，所以镜像把  OS、业务代
码、运行环境、程序库、目录结构都包含在内，镜像 保存在我们的私有仓库 ，只要用户从我们提供的私
有仓库拉取镜像，就 能保证环境的一 致性。
**3.4 实时反馈和智能化报表**
每次集成或交付，都会第一时间 将结果通过多途径的方式反馈给你，也可以定制适合企业专用的报
表平台。

4.基于Jenkins+K 8S+harbor+git等技术链助力 DevOps在企业落地
实践

开发代码 ->提交代码到代码仓库 ->Jenkins 调k8s API->动态生成 Jenkins Slave Pod ->Slave Pod 拉
取git上的代码 ->编译代码 ->打包镜像 ->推送镜像到镜像仓库 harbor或者docker hub ->通过k8s编排服
务发布到测试、生产平台 -> Slave Pod 工作完成之后自动删除 >通过Ingress 发布服务

**4.2 百度：基于 k8s构建亿级 PV流量的DevOps平台**
功能图：

架构图：

**4.3 发布应用到测试环境**

**4.4 发布应用到生产环境**

**4.5 整个DevOps流程图**

5.基于Jenkins+k8s+Git +DockerHub 等技术链 构建企业级 DevOps容器云平台

**5.1 安装Jenkins**
在k8s集群安装 jenkins
Jenkins版本是2.297
Kubernetes 集群版本是 1.20.6

**5.1.1 安装nfs服务，可以选择自己的任意一台机器，我选择 的是k8s的控制节点xianchaomaster 1**
（1）在xianchaomaster1 和xianchaonode 1上安装nfs服务
> **注意： 如果已经安装过 nfs，这个步骤可以忽略**

```bash
[root@xianchaomaster1 ~]# yum install nfs -utils -y
[root@xianchaomaster1 ~]# systemctl start nfs

 [root@xianchaomaster1 ~]# systemctl enable nfs
[root@xianchao node1 ~]# yum install nfs -utils -y
[root@xianchao node1 ~]# systemctl start nfs
[root@xianchao node1 ~]# systemctl enable nfs
```
（2）在xianchaomaster1 上创建一个 nfs共享目录

```bash
[root@xianchaomaster1 ~]# mkdir /data/v2  -p
[root@xianchaomaster1 ~]# vim /etc/export
/data/v1 192.168.40.0/24(rw,no_root_squash)
/data/v2 192.168.40.0/24(rw,no_root_squash)
#新增加一行 /data/v2 192.168.40.0/24
#使配置文件生效
[root@xianchaomaster1 ~]# exportfs -arv
[root@xianchaomaster1 ~]# systemctl restart nfs
```
**5.1.2 在kubernetes 中部署jenkins**
（1）创建名称空间

```bash
[root@xianchaomaster1 ~]# kubectl create namespace jenkins -k8s
```
（2）创建pv

```bash
#更新资源清单文件
[root@xianchaomaster1]# kubectl apply -f pv.yaml
#查看pv是否创建成功
[root@xianchaomaster1]# kubectl get pv
```

  pv.yaml 文件内容如下：

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: jenkins -k8s-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
  - ReadWriteMany
  nfs:
    server: 192.168.40.1 80
path: /data/v 2

```
（3）创建pvc

```bash
#更新资源清单文件
[root@xianchaomaster1]# kubectl apply -f pvc.yaml
#查看pvc是否创建成功
[root@xianchaomaster1]# kubectl get pvc -n jenkins -k8s
```

 pvc.yaml 文件内容如下：

```yaml
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: jenkins -k8s-pvc
  namespace: jenkins -k8s
spec:
  resources:
    requests:
      storage: 10Gi
  accessModes:
  - ReadWriteMany

```

```bash
[root@xianchaomaster1]# kubectl create sa jenkins -k8s-sa -n jenkins -k8s
```
（5）把上面的 sa账号做rbac授权

```bash
[root@xianchaomaster1]# kubectl create clusterrolebinding jenkins -k8s-sa-cluster -n
jenkins-k8s  --clusterrole=cluster -admin --serviceaccount=jenkins -k8s:jenkins -k8s-sa
```
（6）通过deployment 部署jenkins
> **注：下面 jenkins-deployment .yaml文件里的镜像 xianchao /jenkins:v1 ，我已经打包成**
jenkins.tar.gz ，可以把 jenkins.tar.gz 上传到k8s各node节点，，我的工作节点只有一个
xianchao node，所以我上传到 xianchaonode 1节点，用如下方法手动解压：

```bash
[root@xianchaonode1 ~]# docker load -i jenkins.tar.gz
#更新资源清单文件
[root@xianchaomaster1]# kubectl apply -f jenkins -deployment.yaml
#查看jenkins 是否创建成功
[root@xianchaomaster1 jenkins]# kubectl get pods -n jenkins -k8s
NAME                       READY   STATUS            RESTARTS   AGE
jenkins-74b4c59549 -g5j9t   0/1     CrashLoopBackOff   3          67s
#看到jenkins-74b4c59549 -g5j9t是CrashLoopBackOff 状态，查看日志：
[root@xianchaomaster1]# kubectl logs jenkins -74b4c59549 -g5j9t  -n jenkins -k8s
```

日志信息显示：
touch: cannot touch '/var/jenkins_home/copy_reference_file.log': Permission denied
Can not write to /var/jenkins_home/copy_reference_file.log. Wrong volume permissions?

```bash
#报错显示没有权限操作 /var/jenkins_home/copy_reference_file.log 文件，解决办法如下：
[root@xianchaomaster1]# kubectl delete -f jenkins -deployment.yaml
[root@xianchaomaster1]# chown -R 1000.1000 /data/v 2
[root@xianchaomaster1]# kubectl apply -f jenkins -deployment.yaml

#查看pod是否创建成功 :
[root@xianchaomaster1]# kubectl get pods -n jenkins -k8s
```
显示如下，说明部署成功了：

 NAME                       READY   STATUS    RESTARTS   AGE
jenkins-74b4c59549 -6xpnk   1/1     Running   0          66
jenkins-deployment.yaml 文件内容如下 ：

```yaml
kind: Deployment
apiVersion: apps/v1
metadata:
  name: jenkins
  namespace: jenkins -k8s
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jenkins
  template:
    metadata:
      labels:
        app: jenkins
    spec:
      serviceAccount: jenkins -k8s-sa
      containers:
      - name: jenkins
        image:  xianchao /jenkins:v1
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8080
          name: web
          protocol: TCP
        - containerPort: 50000
          name: agent
          protocol : TCP
        resources:
          limits:
            cpu: 1000m
            memory: 1Gi
          requests:
            cpu: 500m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /login
            port: 8080
          initialDelaySeconds: 60
          timeoutSeconds: 5

           failureThreshold: 12
        readinessProbe:
          httpGet:
            path: /login
            port: 8080
          initialDelaySeconds: 60
          timeoutSeconds: 5
          failureThreshold: 12
        volumeMounts:
        - name: jenkins -volume
          subPath: jenkins -home
          mountPath: /var/jenkins_home
      volumes:
      - name: jenkins -volume
        persistentVolumeClaim :
          claimName: jenkins -k8s-pvc

```
（7）把jenkins 前端加上 service，提供外部网络访问

```bash
#更新资源清单文件
[root@xianchaomaster1]# kubectl apply -f jenkins -service.yaml
#查看service 是否创建成功
[root@xianchaomaster1]# kubectl get svc -n jenkins -k8s

#通过上面可以看到 service 的8080端口在物理机映射的端口是 30002
```
 jenkins-service.yaml 文件内容如下：

```yaml
apiVersion: v1
kind: Service
metadata:
  name: jenkins -service
  namespace: jenkins -k8s
  labels:
    app: jenkins
spec:
  selector:
    app: jenkins
  type: NodePort
  ports:
  - name: web
    port: 8080
    targetPort: web
    nodePort: 30002

   - name: agent
    port: 50000
    targetPort: agent

```
**5.2 配置Jenkins**
在浏览器访问 jenkins 的web界面：
http://192.168. 40.180:30002/login?from=%2F

**5.2.1 获取管理员密码**
在nfs服务端，也就是我们的 master1节点获取密码：

```bash
[root@xianchaomaster1 ~]# cat  /data/v2/jenkins -home/secrets/initialAdminPassword
```

把上面获取到的密码拷贝到上面管理员密码下的方框里

**5.2.2 安装插件**
安装推荐的插件

插件安装好之后显示如下

**5.2.3 创建第一个管理员用户**

用户名和密码都设置成 admin，线上环境需要设置成复杂的密码
修改好之后点击保存并完成，出现如下界面

**5.3 测试jenkins 的CI/CD**
**5.3.1 在Jenkins 中安装kubernetes 插件**
（1）在jenkins 中安装k8s插件
Manage Jnekins ------>插件管理 ------>可选插件 ------>搜索kubernetes ------>出现如下

选中kubernetes 之后------>点击下面的直接安装 ------>安装之后选择重新启动 jenkins--->
http://192.168.40. 180:30002/restart -->重启之后登陆 jenkins，插件即可生效

（2）安装blueocean 插件
Manage Jnekins ------>插件管理 ------>可选插件 ------>搜索blueocean ------>出现如下

选中BlueOcean 之后------>点击下面的直接安装 ------>安装之后选择重新启动 jenkins--->
http://192.168.40. 180:30002/restart -->重启之后登陆 jenkins，插件即可生效

**5.3.2 配置jenkins 连接到我们存在的 k8s集群**
（1）访问http://192.168.40.180:30002/configureClouds/

 新增一个云 ,在下拉菜单中选择 kubernets 并添加

（2）填写云 kubernetes 配置内容

kubernetes
https://192.168.40.1 80:6443
（3）测试jenkins 和k8s是否可以通信

Connected to Kubernetes v1.20.6 ，说明测试成功， Jenkins 可以和k8s进行通信

http://jenkins -service.jenkins -k8s.svc.cluster.local:8080
配置k8s集群的时候 jenkins 地址需要写 上面域名的形式，配置之后执行如下：
应用------>保存
**5.3.3 配置pod-template**
（1）配置pod template
访问http://192.168.40.180:30002/configureClouds/

按如下配置

（2）在上面的 pod template 下添加容器
添加容器 ------>Container Template ------>按如下配置 ------>

Docker镜像：使用 jenkins-jnlp.tar.gz 解压出来的镜像 xianchao /jenkins -jnlp:v1，把这个镜像
压缩包上传到k8s的各工作节点，我的工作节点只有一个 xianchaonode 1，我直接把 jenkins-
jnlp.tar.gz 上传到xianchaonode 1，手动解压：

```bash
[root@xianchaonode1 ~]# docker load -i jenkins -jnlp.tar.gz
```
解压出来的镜像是 xianchao /jenkins -jnlp:v1
在每一个 pod template 右下脚都有一个 高级，点击高级

出现如下 :

在Service Account 处输入jenkins-k8s-sa，这个sa就是我们最开始安装 jenkins 时的sa
（3）给上面的 pod template 添加卷
添加卷------>选择Host Path  Volume

/var/run/docker.sock
/var/run/docker.sock

/root/.kube
/home/jenkins/.kube

上面配置好之后， Apply(应用)------>Save(保存)

**5.3.4 添加自己的 dockerhub 凭据**
首页------>系统管理 →Manage Credentials （管理凭据）------>点击Stores scoped to Jenkins
下的第一行 jenkins 后的全局 ，显示如下

username ：xianchao
password ：1989*****
ID：dockerhub
描述：随意 写一段描述即可
上面改好之后选择确定即可

**5.3.5 测试通过 Jenkins 部署应用发布到 k8s开发环境、测试环境、生产环境**

开发提交代码到代码仓库 gitlab -→jenkins 检测到代码更新 -→调用 k8s api在k8s中创建 jenkins
slave  pod：
Jenkins  slave  pod 拉取代码 ---→通过 maven 把拉取的代码进行 构建成war包或者 jar包--->上
传代码到 Sonarqube ，进行 静态代码扫描 - -->基于 war包构建 docker image -->把镜像上传到
harbor 镜像仓库 -->基于镜像 部署应用到开发环境 -->部署应用到测试环境 --->部署应用到生产环
境。

#下面在Pipeline Script输入的脚本内容在课件里面，大家可以找到
jenkins-pipeline -script.txt文件，复制里面内容到 Pipeline Script
在k8s的控制节点创建名称空间：

```bash
[root@xianchaomaster1 ~]# kubectl create ns de vlopment
[root@xianchaomaster1 ~]# kubectl create ns production
[root@xianchaomaster1 ~]# kubectl create ns qatest
```
回到首页：
开始创建一个 新任务------>

输入一个任务名称 ：jenkins-variable -test-deploy------>

流水线------>

确定------>
在Pipeline script 处输入如下内容
node('testhan') {
    stage('Clone') {
        echo "1.Clone Stage"
        script {
            build_tag = sh(returnStdout: true, script: 'git rev -parse --short
HEAD').trim()
        }
    }
    stage('Test') {
      echo "2.Test Stage"

    }
    stage('Build') {
        echo "3.Build Docker Image Stage"

         sh "docker build -t xianchao/jenkins -demo:${build_tag} ."
    }
    stage('Push') {
        echo "4.Push Docker Image Stage"
        withCredentials([usernamePassword(credentialsId: 'dockerhub', passwordVariable:
'dockerHubPassword', usernameVariable: 'dockerHubUser')]) {
            sh "docker login -u ${dockerHubUser} -p ${dockerHubPassword}"
            sh "docker push xianch ao/jenkins -demo:${build_tag}"
        }
    }
    stage('Deploy to dev') {
        echo "5. Deploy DEV"
  sh "sed -i 's/<BUILD_TAG>/${build_tag}/' k8s -dev.yaml"
        sh "sed -i 's/<BRANCH_NAME>/${env.BRANCH_NAME}/' k8s -dev.yaml"
//        sh "bash runni ng-devlopment.sh"
        sh "kubectl apply -f k8s-dev.yaml  --validate=false"
 }
 stage('Promote to qa') {
  def userInput = input(
            id: 'userInput',

            message: 'Promote to qa?',
            parameters: [
                [
                    $class: 'ChoiceParameterDefinition',
                    choices: "YES \nNO",
                    name: 'Env'
                ]
            ]
        )
        echo "This is a deploy step to ${userInput}"
        if (userInput == "YES") {
            sh "sed -i 's/<BUILD_TAG>/${build_tag}/' k8s -qa.yaml"
            sh "sed -i 's/<BRANCH_NAME>/${env.BRANCH_NAME}/' k8s -qa.yaml"
//            sh "bash running -qa.sh"
            sh "kubectl apply -f k8s-qa.yaml --validate=false"
            sh "sleep 6"
            sh "kubectl get pods -n qatest"
        } else {
            //exit
        }
    }
 stage('Promote to pro') {

   def userInput = input(

            id: 'userInput',
            message: 'Promote to pro?',
            parameters: [
                [
                    $class: 'ChoiceParameterDefinition',
                    choices: "YES \nNO",
                    name: 'Env'
                ]
            ]
        )
        echo "This is a deploy step to ${userInput}"
        if (userInput == "YES") {
            sh "sed -i 's/<BUILD_TAG>/${build_tag}/' k8s -prod.yaml"
            sh "sed -i 's/<BRANCH_NAME>/${env.BRANCH_NAME}/' k8s -prod.yaml"
//            s h "bash running -production.sh"
            sh "cat k8s -prod.yaml"
            sh "kubectl apply -f k8s-prod.yaml --record --validate=false"
        }
    }
}
应用------>保存------>立即构建 ,在#1的Console Output可看到构建过程：

#在Console Output如果看到如下：

#上面可以看到已经把应用部署到 dev环境了
#点击Input requested

#通过上面可以看到把应用部署到了 pro环境了

```bash
#验证是否在 devlopment 和production 名称空间下有应用
[root@xianchaomaster1 ~]# kubectl get pods -n production
NAME                            READY   STATUS    RESTARTS   AGE
jenkins-demo-784885d9c9 -w6zlt   1/1     Running   0          60s

[root@xianchaomaster1 ~]# kubectl get pods -n devlopment
NAME                            READY   STATUS    RESTARTS   AGE
jenkins-demo-784885d9c9 -9wkcx   1/1     Running   0          5m38s

[root@xianchaomaster1 ~]# kubectl get pods -n qatest
NAME                            READY   STATUS    RESTARTS   AGE
jenkins-demo-784885d9c9 -wshpj   1/1     Running   0          3m56s
#通过上面可以看到 jenkins 对接k8s，可以把应用发布到 k8s集群的开发、测试、生产环境了。
```

**6. 基于Jenkins+k8s+Git+harbor构建DevOps容器云平台**

需要有一台 harbor服务，我的 harbor安装在了 192.168.40.182 机器上

1.添加凭据
首页------>系统管理 →管理凭据------>点击Stores scoped to Jenkins 下的第一行 jenkins，显
示如下

username ：admin
password ：Harbor12345
ID：dockerharbor
描述：随意
上面改好之后选择确定即可
2.编写jenkins pipeline
因为镜像要上传到 harbor私有镜像仓库，所以需要在 harbor上创建一个项目，项目名称是
jenkins-demo，如下所示：

上面项目创建成功之后，执行如下步骤：

#下面在Pipeline  Script输入的脚本内容在课件里面，大家可以找到
jenkins-pipeline -harbor-script.txt 文件，复制里面内容到 Pipeline Script

新建一个任务 ------>输入一个任务名称处输入 jenkins-harbor------>流水线------>确定------>
在Pipeline script 处输入如下内容
node('testhan') {
    stage('Clone') {
        echo "1.Clone Stage"
        script {
            build_tag = sh(returnStdout: true, script: 'git rev -parse --short
HEAD').trim()
        }
    }

     stage('Test') {
      echo "2.Test Stage"

    }
    stage('Build') {
        echo "3.Build Docker Image Stage"
        sh "docker build -t 192.168. 40.182/jenkins -demo/jenkins -demo:${build_tag} ."
    }
    stage('Push') {
        echo "4.Push Docker Image Stage"
        withCredentials([usernamePassword(credentialsId: 'dockerharbor',
passwordVariable: 'dockerHubPassword', usernameVariable: 'dockerHubUser')]) {
            sh "docker login 192.168. 40.182 -u ${dockerHubUser} -p
${dockerHubPassword}"
            sh "docker p ush 192.168. 40.182/jenkins -demo/jenkins -demo:${build_tag}"
        }
    }
    stage('Deploy to dev') {
        echo "5. Deploy DEV"
  sh "sed -i 's/<BUILD_TAG>/${build_tag}/' k8s -dev-harbor.yaml"
        sh "sed -i 's/<BRANCH_NAME>/${env.BRANCH_NAME}/' k8 s-dev-harbor.yaml"
//        sh "bash running -devlopment.sh"
        sh "kubectl apply -f k8s-dev-harbor.yaml  --validate=false"
 }
 stage('Promote to qa') {
  def userInput = input(
            id: 'userInput',

            message: 'Promote to qa?',
            parameters: [
                [
                    $class: 'ChoiceParameterDefinition',
                    choices: "YES \nNO",
                    name: 'Env'
                ]
            ]
        )
        echo "This is a deploy step to ${userInput}"
        if (userInput == "YES") {
            sh "sed -i 's/<BUILD_TAG>/${build_tag}/' k8s -qa-harbor.yaml"
            sh "sed -i 's/<BRANCH_NAME>/${env.BRANCH_NAME}/' k8s -qa-harbor.yaml"
//            sh "bash running -qa.sh"
            sh "kubectl apply -f k8s-qa-harbor.yaml --validate=false"

             sh "sleep 6"
            sh "kubectl get pods -n qatest"
        } else {
            //exit
        }
    }
 stage('Promote to pro') {
  def userInput = input(

            id: 'userInput',
            message: 'Promote to pro?',
            parameters: [
                [
                    $class: 'ChoiceParameterDefinition',
                    choices: "YES \nNO",
                    name: 'Env'
                ]
            ]
        )
        echo "This is a deploy step to ${userInput}"
        if (userInput == "YES") {
            sh "sed -i 's/<BUILD_TAG>/${build_tag}/' k8 s-prod-harbor.yaml"
            sh "sed -i 's/<BRANCH_NAME>/${env.BRANCH_NAME}/' k8s -prod-harbor.yaml"
//            sh "bash running -production.sh"
            sh "cat k8s -prod-harbor.yaml"
            sh "kubectl apply -f k8s-prod-harbor.yaml --record --validate=false"
        }
    }
}

应用------>保存------>立即构建即可 ,打开blue ocean 会看到如下流程，可以手动点击确认

Jenkins 实现k8s应用按照指定版本回滚
回到首页：
新建一个任务 ------ >输入一个任务名称处输入 jenkins -variable -test-deploy -rollout ------ >流水
线------ >确定------ >在Pipeline script 处输入如下内容

node('testhan') {
  stage('git clone') {
    sh "ls -al"
    sh "pwd"
}
  stage('select env') {
    def envInput = input(
      id: 'envInpu t',
      message: 'Choose a deploy environment',
      parameters: [
         [
             $class: 'ChoiceParameterDefinition',
             choices: "dev lopment \nqatest\npro duction ",
             name: 'Env'
         ]
     ]
)
echo "This is a deploy step to ${envInput}"
sh "sed -i 's/<namespace>/${envInput}/' getVersion.sh"
sh "sed -i 's/<namespace>/${envInput}/' rollout.sh"
sh "bash getVersion.sh"
// env.WORKSPACE = pwd()
// def version = readFile "${env.WORKSPACE}/version.csv"
// println vers ion
}
  stage('select version') {
     env.WORKSPACE = pwd()
  def version = readFile "${env.WORKSPACE}/version.csv"
  println version
      def userInput = input(id: 'userInput',
                                        message: ' 选择回滚版本 ',
                                        parameters: [
            [
                 $class: 'ChoiceParameterDefinition',
                 choices: "$version \n",
                 name: 'Version'
       ]
      ]
)
       sh "sed -i 's/<version>/${userInput}/' rollout.sh"

 }
  stage('rollout deploy') {
      sh "bash rollout.sh"
}
}

**7. Jenkins Pipeline 语法介绍**

**7.1 Jenkins Pipeline 介绍**
Jenkins  pipeline （流水线） 是一套运行于 jenkins 上的工作流框架，将原本独立运行于单个或者
多个节点的任务连接起来，实现单个任务难以完成的复杂流程编排与可视化。 它把持续提交流水线
（Continuous Delivery Pipeline ）的任务 集成到 Jenkins 中。
pipeline 是jenkins2.X 最核心的特性，  帮助 jenkins 实现从 CI到CD与DevOps 的转变 。

持续提交流水线（ Continuous Delivery Pipeline ）会经历一个复杂的过程：  从版本控制、向用户
和客户提交软件，软件的每次变更（提交代码到仓库）到软件发布（ Release ） 。这个过程包括以一种可
靠并可重复的方式构建软件，以及通过多个测试和部署阶段来开发构建好的软件（称为 Build ）。

总结：
1.Jenkins Pipeline 是一组插件，让 Jenkins 可以实现持续交付管道的落地和实施。
2.持续交付管道 (CD Pipeline) 是将软件从版本控制阶段到交付给用户或客户的完
整过程的自动化表现。

 3.软件的每一次更改（提交到源代码管理系统）都要经过一个复杂的过程才能被发布。

**7.2 为什么用 Jenkins Pipeline ？**
本质上， Jenkins 是一个自动化引擎，它支持许多自动模式。  Pipeline 向Jenkins 中添加了一组
强大的工具 , 支持简单的 CI到全面的 CD pipeline 。通过对一系列的相关任务进行建模 , 用户可以利用
pipeline 的很多特性 :
**1、代码： Pipeline 以代码的形式实现，使团队能够编辑，审查和迭代其 CD流程。**
**2、可持续性： Jenkins 重启或者中断后都不会影响 Pipeline Job 。**
**3、停顿： Pipeline 可以选择停止并等待人工输入或批准，然后再继续 Pipeline 运行。**
**4、多功能： Pipeline 支持现实复杂 的CD要求，包括循环和并行执行工作的能力。**
**5、可扩展： Pipeline 插件支持其 DSL 的自定义扩展以及与其他插件集成的多个选项。**

DSL 是什么？
DSL 其实是  Domain Specific Language 的缩写，中文翻译为 领域特定语言 （下简称  DSL） ；而
与 DSL相对的就是 GPL，这里的 GPL 并不是我们知道的开源许可证，而是  General Purpose
Language 的简称，即 通用编程语言 ，也就是我们非常熟悉的  Objective -C、Java 、Python 以及
C 语言等等。
**7.3 Jenkins pipeline 入门**
pipeline 脚本是 由groovy 语言实现的
但无需专门学习  groovy

pipeline 支持两种语法 ：
 -Declarative ：声明式
 -Scripted pipeline  ：脚本式

声明式 pipeline 语法：
官网：
https://www.jenkins.io/doc/book/pipeline/syntax/

声明式 语法包括以下核心流程：
1.pipeline :  声明其内容为一个声明式的 pipeline 脚本
2.agent:   执行节点（ job运行的 slave 或者 master 节点）
3.stages:  阶段集合，包裹所有的阶段（例如：打包，部署等各个阶段）
4.stage:   阶段，被 stages 包裹，一个 stages 可以有多个 stage
5.steps:   步骤,为每个阶段的最小执行单元 ,被stage 包裹
6.post:    执行构建后的操作，根据构建结果来执行对应的操作

根据上面 流程创建一个简单的 pipeline
pipeline {
    agent any
    stages{
        stage(" This is first stage "){

             steps(" This is first step"){
                echo " I am xianchao "
            }
        }
    }
    post{
        always{
            echo " The process  is ending "
        }
    }
}

Pipeline ：
作用域：应用于全局最外层，表明该脚本为声明式 pipeline
是否必须：必须
agent ：
作用域：可用在全局与 stage 内
agent 表明此 pipeline 在哪个节点上执行
是否必须：是
参数： any,none, label, node,docker,dockerfile

agent any
#运行在任意的可用节点上

agent none
#全局不指定运行节点，由各自 stage 来决定

agent { label 'master' }
#运行在指定标签的机器上 ,具体标签名称由 agent 配置决定

agent {
     node {
         label  'my-defined -label '
         customWorkspace ' xxxxxxx '
    }
}
#node{ label 'master' } 和agent { label 'master' } 一样，但是 node 可以扩展节点信息 ，允许
额外的选项  (比如 customWorkspace  )。

agent { docker 'python'  }
#使用指定 的容器运行流水线
如：

 agent {
    docker {
        image 'maven:3 -alpine'
        label 'my -defined -label'
        args  ' -v /tmp:/tmp'
    }
}
#定义此参数时，执行 Pipeline 或stage 时会动态 的在具有 label 'my -defined -label' 标签的
node 提供 docker 节点去 执行 Pipelines 。 docker 还可以接受一个 args ，直接传递给 docker run 调
用。

agent {
    // Equivalent to "docker build -f Dockerfile.build --build -arg version=1.0.2 ./build/
    dockerfile {
        filename 'Dockerfile.build'
        dir 'build'
        label 'my -defined -label'
        additionalBuildArgs  ' --build -arg version=1.0.2'
    }
}

**7.4 Pipeline  声明式语法 Declarative**

**7.4.1 environment**
environment 指令指定一系列键值对，这些键值对将被定义为所有 step 或stage -specific step
的环境变量，具体取决于 environment 指令在 Pipeline 中的位置。该指令支持一种特殊的方法
credentials() ，可以通过其在 Jenkins 环境中的标识符来访问预定义的凭据。对于类型为 “Secret Text ”
的凭据，该  credentials() 方法将确保指定的环境变 量包含 Secret Text 内容；对于 “标准用户名和密码 ”
类型的凭证，指定的环境变量将被设置为 username:password 并且将自动定义两个附加的环境变量：
MYVARNAME_USR 和MYVARNAME_PSW 。

pipeline {
    agent any
    environment {

         CC = 'clang'
    }
    stages {
        stage('Example') {
            steps {
                sh 'printenv'
            }
        }
    }
}

**7.4.2 options**
options 指令允许在 Pipeline 本身内配置 Pipeline 专用选项。 Pipeline 本身提供了许多选项，例
如buildDiscarder ，但它们也可能由插件提供，例如  timestamps 。

可用选项
buildDiscarder ：  pipeline 保持构建的最大个数。 用于保存 Pipeline 最近几 次运行的数据 ，例

 如：options { buildDiscarder(logRotator(numToKeepStr: '1')) }
  disableConcurrentBuilds ： 不允许并行执行 Pipeline, 可用于防止同时访问共享资源等。例如：
options { disableConcurrentBuilds() }
  skipDefaultCheckout ：跳过默认设置的代码 check out 。例如： options
{ skipDefaultCheckout() }
  skipStage sAfterUnstable ： 一旦构建状态进入了 “Unstable ”状态，就跳过此 stage 。例如：
options { skipStagesAfterUnstable() }
  timeout ： 设置 Pipeline 运行的超时时间 ，超过超时时间， job会自动被终止 ，例如： options
{ timeout(time: 1, unit: 'HOURS') }
  retry ：  失败后，重试整个 Pipeline 的次数。例如： options { retry(3) }
  timestamps ： 预定义由 Pipeline 生成的所有控制台输出时间。例如： options { timestamps() }

pipeline {
    agent any
    options {
        timeout(time: 1, unit: 'HOURS')
    }
    stages {
        stage('Example') {
            steps {
                echo 'Hello World'
            }
        }
    }
}

**7.4.3 parameters**
parameters 指令提供用户在触发 Pipeline 时的参数列表。这些参数值通过该 params 对象可用于
Pipeline  stage 中，具体用法如下 ：

作用域：被最外层 pipeline 所包裹，并且只能出现一次，参数可被全局使用
好处：使用 parameters 好处是能够使参数也变成 code, 达到 pipeline as code ，pipeline 中设置
的参数会自动在 job构建的时候生成，形成参数化构建

可用参数
  string
    A parameter of a string type, for example: parameters { string(name:

 'DEPLOY_ENV', defaultValue: 'staging', description: '') }
  booleanParam
    A boolean parameter, for example: parameters { booleanParam(name:
'DEBUG_BUILD', defaultVa lue: true, description: '') }
  目前只支持 [booleanParam, choice, credentials, file, text, password, run, string] 这几种参数
类型，其他高级参数化类型还需等待社区支持。

pipeline{
    agent any
    parameters {
        string(name: 'xianchao', defaultValue: 'my name is xianchao', description: 'My
name is xiancaho')
my wechat')
    }
    stages{
        stage("stage1"){
            steps{
                echo "$xianchao"
            }
        }
    }
}

开始构建

控制台输出观察构建结果：

**7.4.4 triggers**
triggers 指令定义了 Pipeline 自动化触发的方式。目前有 三个可用的触发器： cron 和pollSCM 和
upstream 。

 用域：被 pipeline 包裹，在符合条件下自动触发 pipeline

cron
  接受一个 cron 风格的字符串来定义 Pipeline 触发的 时间间隔，例如：
triggers { cron('H 4/* 0 0 1 -5') }
pollSCM

  接受一个 cron 风格的字符串来定义 Jenkins 检查 SCM 源更改的常规间隔。如果存在新的更改，则
Pipeline 将被重新触发。例如： triggers { pollSCM('H 4/* 0 0 1 -5') }

pipeline {
    agent any
    triggers {
        cron('H 4/* 0 0 1 -5')
    }
    stages {
        stage('Example') {
            steps {
                echo 'Hello World'
            }
        }
    }
}

**7.4.5 tools**

 通过 tools 可自动安装工具，并放置环境变量到 PATH 。如果 agent none ，这将被忽略。

Supported Tools( Global Tool Configuration )
  maven
  jdk
  gradle

pipeline {
    agent any
    tools {
       #工具名称必须在 Jenkins 管理 Jenkins → 全局工具配置中预配置。
        maven 'apache -maven -3.0.1'

     }
    stages {
        stage('Example') {
            steps {
                sh 'mvn --version'
            }
        }
    }
}

# The tool name must be pre-configured in Jenkins under  Manage Jenkins  → Global Tool
Configuration

**7.4.6 input**
stage 的 input 指令允许你使用  input step 提示输入。  在应用了  options 后，进入  stage 的
agent 或评估  when 条件前， stage 将暂停。  如果 input 被批准 , stage 将会继续。  作为 input
提交的一部分的任何参数都将在环境中用于其他  stage

配置项

message
必需的。  这将在用户提交  input 时呈现给用户。

id
input 的可选标识符，  默认为  stage 名称。

ok
`input` 表单上的 "ok" 按钮的可选文本。

submitter
可选的以逗号分隔的用户列表或允许提交  input 的外部组名。默认允许任何用户。

submitterParameter
环境变量的可选名称。如果存在，用  submitter 名称设置。

parameters
提示提交者提供的一个可选的参数列表。

pipeline {
    agent any
    stages {
        stage('Example') {
            input {

                 message "Should we continue?"
                ok "Yes, we should."
                submitter " xianchao ,lucky "
                parameters {
                    string( name: 'PERSON', defaultValue: ' xianchao ', description: 'Who
should I say hello to?')
                }
            }
            steps {
                echo "Hello, ${PERSON}, nice to meet you."
            }
        }
    }
}

**7.4.7 when**
 when 指令允许 Pipeline 根据给定的条件确定是否执行该阶段。该 when 指令必须至少包含一个
条件。如果 when 指令包含多个条件，则所有子条件必须为 stage 执行返回 true。这与子条件嵌套在一
个allOf 条件中相同（见下面的例子） 。
更复杂的条件结构可使用嵌套条件建： not，allOf 或anyOf 。嵌套条件可以嵌套到任意深度。

内置条件
branch
    当正在构建的分支与给出的分支模式匹配时执行，例如： when { branch 'master' } 。请注
意，这仅适用于多分支 Pipelin e。
  environment

     当指定的环境变量设置为给定值时执行，例如：  when { environment name: 'DEPLOY_TO',
value: 'production' }
  expression
    当指定的 Groovy 表达式求值为 true 时执行，例如：  when { expression { return
params.DEBUG_BUILD } }
  not
    当嵌套条件为 false 时执行。必须包含一个条件。例如： when { not { branch ' master' } }
  allOf
    当所有嵌套条件都为真时执行。必须至少包含一个条件。例如： when { allOf { branch
'master'; environment name: 'DEPLOY_TO', value: 'production' } }
  anyOf
    当至少一个嵌套条件为真时执行。必须至少包含一个条件。例如： when { anyOf { branch
'master'; branch 'staging' } }

pipeline {
    agent a ny
    stages {
        stage('Example Build') {
            steps {
                echo 'Hello World'
            }
        }
        stage('Example Deploy') {
            when {
                allOf {
                    branch 'production'
                    environment name: 'DEPLOY_TO', value: 'production'
                }
            }
            steps {
                echo 'Deploying'
            }
        }
    }
}

**7.4.8 Parallel**
Declarative Pipeline 近期新增了对并行嵌套 stage 的支持，对耗时长，相互不存在依赖 的stage
可以使用此方式提升运行效率。除了 parallel stage ，单个 parallel 里的多个 step 也可以使用并行的方
式运行。
pipeline {
    agent any

     stages {
        stage('Non -Parallel Stage') {
            steps {
                echo 'This stage will be executed first.'
            }
        }
        stage('Parallel Stage') {
            when {
                branch 'master'
            }
            parallel {
                stage('Branch A') {
                    agent {
                        label "for -branch -a"
                    }
                    steps {
                        echo "On Branch A"
                    }
                }
                stage('Branch B') {
                    agent {
                        label "for -branch -b"
                    }
                    steps {
                        echo "On Branch B"
                    }
                }
            }
        }
    }
}

**7.5 Pipeline  Scripted 语法**
Groovy 脚本不一定适合所有使用者，因此 jenkins 创建了 Declarative pipeline ，为编写
Jenkins 管道提供了一种更简单、更有主见的语法。但是由于脚本化的 pipeline 是基于 groovy 的一种
DSL 语言，所以与 Declarative pipeline 相比为 jenkins 用户提供了更巨大的灵活性和可扩展性。

1.流程控制
 pipeline 脚本同其它脚本语言一样，从上至下顺序执行，它的流程控制取决于 Groovy 表达式，
如if/else 条件语句，举例如下：
node {
    stage('Example') {

         if (env.BRANCH_NAM E == 'master') {
            echo 'I only execute on the master branch'
        } else {
            echo 'I execute elsewhere'
        }
    }
}

2.Declarative pipeline 和Scripted pipeline 的比较
共同点：
  两者都是 pipeline 代码的持久实现，都能够使用 pipeline 内置的插件或者插件提供的 stage ，两者
都可以利 用共享库扩展。
    区别：
  两者不同之处在于语法和灵活性。 Declarative pipeline 对用户来说，语法更严格，有固定的组织
结构，更容易生成代码段，使其成为用户更理想的选择。但是 Scripted pipeline 更加灵活，因为
Groovy 本身只能对结构和语法进行限制，对于更复杂的 pipeline 来说，用户可以根据自己的业务进行
灵活的实现和扩展。

**8、jenkins+ k8s+harbor实现DevOps**
1.添加凭据
首页------ >系统管理 →管理凭据------ >点击 Stores scoped to Jenkins 下的第一行 jenkins ，显
示如下

username ：admin
password ：Harbor 12345
ID：docker harbor
描述：随意
上面改好之后选择确定即可
2.编写 jenkins  pipeline
因为镜像要上传到 harbor 私有镜像仓库，所以需要在 harbor 上创建一个项目，项目名称是
jenkins -demo ，如下所示：

上面项目创建成功之后，执行如下步骤：

新建一个任务 ------ >输入一个任务名称处输入 jenkins -harbor ------ >流水线 ------ >确定------ >
在Pipeline script 处输入如下内容
node('testhan') {
    stage('Clone') {
        echo "1.Clone Stage"

         script {
            build_tag = sh(returnStdout: true, script: 'git rev -parse --short
HEAD').trim()
        }
    }
    stage('Test') {
      echo "2.Test Stage"

    }
    stage('Build') {
        echo "3.Build Docker Image Stage"
        sh "docker build -t 192.168.40.132/jenkins -demo/jenkins -demo:${build_tag} ."
    }
    stage('Push') {
        echo "4.Push Docker Image Stage"
        withCredentials([usernamePassword(creden tialsId: 'dockerharbor',
passwordVariable: 'dockerHubPassword', usernameVariable: 'dockerHubUser')]) {
            sh "docker login 192.168.40.132 -u ${dockerHubUser} -p
${dockerHubPassword}"
            sh "docker push 192.168.40.132/jenkins -demo/jenkins -demo:${build_tag}"
        }
    }
    stage('Deploy to dev') {
        echo "5. Deploy DEV"
  sh "sed -i 's/<BUILD_TAG>/${build_tag}/' k8s -dev-harbor.yaml"
        sh "sed -i 's/<BRANCH_NAME>/${env.BRANCH_NAME}/' k8s -dev-harbor.yaml"
//        sh "bash running -devlopment.sh"
        sh "kubectl apply -f k8s -dev-harbor.yaml  --validate=false"
 }
 stage('Promote to qa') {
  def userInput = input(
            id: 'userInput',

            message: 'Promote to qa?',
            parameters: [
                [
                    $class: 'ChoiceParameterDefinition',
                    choices: "YES \nNO",
                    name: 'Env'
                ]
            ]
        )
        echo "This is a deploy step to ${userInput}"

         if (userInput == "YES") {
            sh "sed -i 's/<BUILD_TAG>/${build_tag}/' k8s -qa-harbor.yaml"
            sh "sed -i 's/<BRANCH_NAME>/${env.BRANCH_NAME}/' k8s -qa-
harbor.yaml"
//            sh "bash running -qa.sh"
            sh "kubectl apply -f k8s -qa-harbor.yaml --validate=false"
            sh "sleep 6"
            sh "kubectl get pods -n qatest"
        } else {
            //exit
        }
    }
 stage('Promote to pro') {
  def userInput = input(

            id: 'userInput',
            message: 'Promote to pro?',
            parameters: [
                [
                    $class: 'ChoiceParameterDefinition',
                    choices: "YES \nNO",
                    name: 'Env'
                ]
            ]
        )
        echo "This is a deploy step to ${userInput}"
        if (userInput == "YES") {
            sh "sed -i 's/<BUILD_TAG>/${build_tag}/' k8s -prod -harbor.yaml"
            sh "sed -i 's/<BRANCH_NAME>/${env.BRANCH_NAME}/' k8s -prod -
harbor.yaml"
//            sh "bash running -production.sh"
            sh "cat k8s -prod -harbor.yaml"
            sh "kubectl apply -f k8s -prod -harbor.yaml --record --validate=false"
        }
    }
}

应用------ >保存------ >立即构建即可 ,打开 blue ocean 会看到如下流程，可以手动点击确认

**9、Jenkins接入Sonarqube**

1.在192.168.40.1 80上安装 sonarqube ：

docker run   -d   --name postgres10   -p 5432:5432   -e POSTGRES_USER=sonar   -
e POSTGRES_PASSWORD=123456   postgres

docker run   -d   --name sonarqube7.9   -p 9000:9000   --link postgres10   -e

```bash
SONARQUBE_JDBC_URL=jdbc:postgresql://postgres10:5432/sonar   -e
SONARQUBE_JDBC_USERNAME=sonar   -e SONARQUBE_JDBC_PASSWORD=123456   -v
sonar qube_conf:/opt/sonarqube/conf   -v
sonarqube_extensions:/opt/sonarqube/extensions   -v
sonarqube_logs:/opt/sonarqube/logs   -v sonarqube_data:/opt/sonarqube/data
sonarqube
```

在jenkins 中安装 sonarqube 插件：
系统管理 ->插件管理 ->可选插件：搜索 sonar ，找到 Sonarqube  Scanner

选择 Sonarqube  Scanner 直接安装，安装之后重启 jenkins 即可

在sonarqube 的web 界面创建一个 token ：

选择 Generate 出现如下：

把copy 后面的一串 token 记录下来：

2b91be9d40a28385d8b2f61b0fc0a52efd5abf97

回到 k8s的master 1节点：

cd /root/microservic -test

mvn sonar:sonar   -Dsonar.host.url=http://192.168.40.1 81:9000 -
Dsonar.login= 2b91be9d40a28385d8b2f61b0fc0a52efd5abf97

这样就可以把代码上传到 sonarqube 了


