# 电商退款审核Agent演示系统                

## 1、用例说明

本期视频为大家分享的是一个基于LangChain&LangGraph(截止到2026.01.04的最新版本)和FastAPI等框架构建的 Agent 智能体服务——**电商退款审核Agent演示系统**          
这里想分享给大家的是一个可复制到其他场景进行二次开发的整套闭环解决方案               

本期视频涉及到的全部源码、操作说明文档、Docker文件、前后端代码逻辑流程说明文档等全部资料都是开源分享给大家的，大家可以下载自行进行项目部署实践                               
大家可以在下方、视频简介或本期视频置顶评论中获取项目链接地址，进入项目进行下载即可           
https://github.com/NanGePlus/ReActAgentsTest                                                                                          
https://gitee.com/NanGePlus/ReActAgentsTest             
其中，前后端代码逻辑流程说明文档我以网盘链接的形式单独给到大家，大家可以在下方或本期视频置顶评论中获取网盘链接                                           
链接：https://pan.quark.cn/s/ffaf3125e6d9?pwd=m59M                           
提取码：m59M      

同时，我也会再提供一份详细的视频，为有需要的朋友提供从项目的前期准备工作、项目初始化、功能测试、根据前后端代码逻辑流程来读源代码等，如果有需要希望大家可以支持一下                     

主要核心功能包含：            

- 基于 FastAPI 框架构建 Agent 智能体 API 后端服务
- 集成 LangChain 预置的 ReAct 架构实现智能代理
- 支持短期记忆功能，通过 PostgreSQL 实现持久化存储
- 支持长期记忆功能，读写操作（如用户偏好设置等）
- 支持 Function Calling，整合自定义工具与 MCP Server 工具
- 支持人工介入审查（HIL）机制，提供四种工具调用审查模式
- 兼容多厂商大模型接口：OpenAI、阿里通义千问、Ollama 本地开源模型等
- 基于 Redis 存储用户会话状态，支持客户端与服务端故障恢复
- 支持会话过期时间动态调整
- 用户登录后自动恢复最近会话，无历史会话则自动创建新会话
- 提供历史会话管理与恢复功能
- 使用 Rich 库构建功能完善的前端演示，实现前后端联调

主要场景包含:                     

- 小额退款(≤100元):自动批准退款                 
- 中额退款(101-500元):需要客服审核                      
- 大额退款(>500元):需要主管审核

前后端代码逻辑流程说明:      

- 后端业务流程查看**01_后端业务核心流程.pdf**和**02_API接口和数据模型描述.pdf**                 
- 前端业务流程查看**03_前端业务核心流程.pdf**                
 
文档可通过在下方或本期视频置顶评论中获取网盘链接                                           
链接：https://pan.quark.cn/s/ffaf3125e6d9?pwd=m59M                           
提取码：m59M                     

核心框架:       

- LangChain 是一个帮你把大模型、工具、数据和记忆“拼装”成完整智能应用的工程化框架                    
- LangGraph 是 LangChain 生态里的一个图式编排框架，用“有状态的有向图”来组织、控制和持久化复杂 Agent 工作流 
- 官方文档:https://docs.langchain.com/                                           

## 2、准备工作

### 2.1 集成开发环境搭建  

anaconda提供python虚拟环境,pycharm提供集成开发环境          

具体参考如下视频:                         
【大模型应用开发-入门系列】03 集成开发环境搭建-开发前准备工作                          
https://youtu.be/KyfGduq5d7w                      

### 2.2 大模型LLM服务接口调用方案

(1)gpt大模型等国外大模型使用方案                   
国内无法直接访问，可以使用代理的方式，具体代理方案自己选择                         
这里推荐大家使用:https://nangeai.top/register?aff=Vxlp        

(2)非gpt大模型方案 OneAPI方式或大模型厂商原生接口          

(3)本地开源大模型方案(Ollama方式)            

具体参考如下视频:                                                      
【大模型应用开发-入门系列】04 大模型LLM服务接口调用方案                    
https://youtu.be/mTrgVllUl7Y                           

## 3、项目初始化

### 3.1 下载源码

GitHub或Gitee中下载工程文件到本地，下载地址如下：                    

https://github.com/NanGePlus/ReActAgentsTest                                                                                        
https://gitee.com/NanGePlus/ReActAgentsTest               

### 3.2 构建项目 

使用pycharm构建一个项目，为项目配置虚拟python环境                                       
项目名称：ReActAgentsApplication                                                                   
虚拟环境名称保持与项目名称一致                                                   
 
### 3.3 将相关代码拷贝到项目工程中         

将下载的代码文件夹中的文件全部拷贝到新建的项目根目录下                           

### 3.4 安装项目依赖                

新建命令行终端，在终端中运行如下指令进行安装               

```bash
pip install langgraph==1.0.5                   
pip install langchain==1.2.0                        
pip install langchain-openai==1.1.6              
pip install langgraph-checkpoint-postgres==3.0.2               
pip install rich==14.2.0               
pip install fastapi==0.128.0                 
pip install redis==7.1.0                   
pip install concurrent-log-handler==0.9.28                 
pip install uvicorn==0.40.0            
```

**注意:** 建议先使用这里列出的对应版本进行本项目测试，避免因版本升级造成的代码不兼容。测试通过后，可进行升级测试                                   

## 4、功能测试

### 4.1 使用Docker方式运行PostgreSQL数据库和Redis数据库      

进入官网 https://www.docker.com/ 下载安装Docker Desktop软件并安装，安装完成后打开软件                      

打开命令行终端，`cd 01_RefundApprovalAgent/docker` 文件夹下                     
- 进入到 postgresql 下执行 `docker-compose up -d` 运行 PostgreSQL 服务                                           
- 进入到 redis 下执行 `docker-compose up -d` 运行 Redis 服务                  

运行成功后可在Docker Desktop软件中进行管理操作或使用命令行操作或使用指令                       

使用数据库客户端软件远程登陆进行可视化操作，这里推荐使用免费的DBeaver客户端软件和Redis-Insight客户端软件        

- DBeaver 客户端软件下载链接: https://dbeaver.io/download/          
- Redis-Insight 客户端软件下载链接: https://redis.io/downloads/#Redis_Insight           

### 4.2 运行脚本启动前后端服务
                                            
- 运行后端服务 `python 01_backendServer.py`                                 
- 再运行前端服务 `python 02_frontendServer.py`             

### 4.3 业务功能测试       

**(1)测试流程1:从查询到小额退款**                

用户: "你好，我想退款"                
Agent: "好的，请提供订单号，或者我可以帮您查询订单信息"              

用户: "先查询订单ORD20260103003"               
Agent: [调用query_order_info工具，显示订单信息]                 

用户: "帮我退这个订单，金额89元，尺寸不合适"                   
Agent: [自动调用process_small_refund，直接批准，无需人工审核]                

**(2)测试流程2：中额退款需要审核**

用户: "我要退款订单ORD20260104004"              
Agent: "好的，请告诉我退款金额和原因"               

用户: "全额退款158元，商品质量问题"                 
Agent: [调用process_medium_refund，触发人工中断]             
    【显示审核界面】            
    是否批准退款?             
    订单号: ORD20260104004            
    用户: 陈小芳             
    商品: 电脑背包              
    退款金额: ¥158              
    
审核人: yes            

Agent: [执行退款，显示成功信息]                 


**(3)测试流程3：大额退款修改金额**          
用户: "退款订单ORD20260104005，金额899元，不想要了"     
Agent: [调用process_large_refund，触发高级别审核]        

审核人: edit          
系统: 请输入修改后的参数            
审核人: {"order_id":"ORD20260104005","refund_amount": 700, "refund_reason": "部分退款"}        

Agent: [按新参数执行退款]             

