# 1、项目介绍                  
## 1.1、主要内容
本期视频为大家分享如何在LangGraph提供的ReAct架构的Agent中使用Human in the loop(HIL 人工审查)           
在工具被调用时，系统会暂停执行，等待用户的反馈（接受、编辑或直接提供响应），然后根据用户的反馈决定如何继续执行工具             
这个功能在需要人工干预的工作流中非常有用                  
(1)验证工具输入:确保工具接收到的输入参数是正确的                        
(2)调整工具行为:允许用户在工具执行前修改参数                     
(3)直接提供结果:在某些情况下，用户可能希望跳过工具的执行，直接返回自定义结果                   
本期视频提供的3个demo用例分别为大家介绍自定义工具、MCP Server提供的工具以及两者的混合工具，如何进行人工审查                          
 
## 1.2 LangGraph介绍 
LangGraph 是由 LangChain 团队开发的一个开源框架，旨在帮助开发者构建基于大型语言模型（LLM）的复杂、有状态、多主体的应用            
官方文档:https://langchain-ai.github.io/langgraph/            
关于LangGraph大家可以参考如下项目，里面有详细的源码资料和视频分享:               
https://github.com/NanGePlus/LangGraphChatBot                

## 1.2 MCP介绍              
MCP官方简介:https://www.anthropic.com/news/model-context-protocol                                                                                        
MCP文档手册:https://modelcontextprotocol.io/introduction                                                    
MCP官方服务器列表:https://github.com/modelcontextprotocol/servers                              
PythonSDK的github地址:https://github.com/modelcontextprotocol/python-sdk                                      
关于MCP大家可以参考如下项目，里面有详细的源码资料和视频分享:                       
https://github.com/NanGePlus/MCPServerTest                          
关于高德地图MCP Server的分享，已经为大家分享过两期视频(在上述项目内)如下:                                            
【大模型应用开发-MCP系列】高德地图MCP Server STDIO传输模式全流程实操演示 已覆盖12大核心服务接口，提供全场景覆盖的地图服务                                   
https://youtu.be/yXFb8Cg9l7g               
【大模型应用开发-MCP系列】高德地图MCP Server SSE+HTTP连接模式全流程实操演示 已覆盖12大核心服务接口，提供全场景覆盖的地图服务                             
https://youtu.be/OLVHObhEP0U                     

## 1.3 自定义工具
使用python实现的一个模拟酒店预订的工具book_hotel                                    
其需传入的参数为:{hotel_name}                        

## 1.4 高德地图MCP Server 
为实现 LBS 服务与 LLM 更好的交互，高德地图 MCP Server 现已覆盖12大核心服务接口，提供全场景覆盖的地图服务                
包括地理编码、逆地理编码、IP 定位、天气查询、骑行路径规划、步行路径规划、驾车路径规划、公交路径规划、距离测量、关键词搜索、周边搜索、详情搜索等                 
链接地址:https://lbs.amap.com/api/mcp-server/summary              
具体提供的接口详情介绍:                  
**(1)地理编码**                
name='maps_regeocode'               
description='将一个高德经纬度坐标转换为行政区划地址信息'                       
inputSchema={'type': 'object', 'properties': {'location': {'type': 'string', 'description': '经纬度'}}, 'required': ['location']}                   
**(2)逆地理编码**               
name='maps_geo'              
description='将详细的结构化地址转换为经纬度坐标。支持对地标性名胜景区、建筑物名称解析为经纬度坐标'               
inputSchema={'type': 'object', 'properties': {'address': {'type': 'string', 'description': '待解析的结构化地址信息'}, 'city': {'type': 'string', 'description': '指定查询的城市'}}, 'required': ['address']}                  
**(3)IP 定位**               
name='maps_ip_location'         
description='IP 定位根据用户输入的 IP 地址，定位 IP 的所在位置'            
inputSchema={'type': 'object', 'properties': {'ip': {'type': 'string', 'description': 'IP地址'}}, 'required': ['ip']}                
**(4)天气查询**               
name='maps_weather'               
description='根据城市名称或者标准adcode查询指定城市的天气'                 
inputSchema={'type': 'object', 'properties': {'city': {'type': 'string', 'description': '城市名称或者adcode'}}, 'required': ['city']}             
**(5)骑行路径规划**               
name='maps_bicycling'     
description='骑行路径规划用于规划骑行通勤方案，规划时会考虑天桥、单行线、封路等情况。最大支持 500km 的骑行路线规划'     
inputSchema={'type': 'object', 'properties': {'origin': {'type': 'string', 'description': '出发点经纬度，坐标格式为：经度，纬度'}, 'destination': {'type': 'string', 'description': '目的地经纬度，坐标格式为：经度，纬度'}}, 'required': ['origin', 'destination']}      
**(6)步行路径规划**               
name='maps_direction_walking'      
description='步行路径规划 API 可以根据输入起点终点经纬度坐标规划100km 以内的步行通勤方案，并且返回通勤方案的数据'       
inputSchema={'type': 'object', 'properties': {'origin': {'type': 'string', 'description': '出发点经度，纬度，坐标格式为：经度，纬度'}, 'destination': {'type': 'string', 'description': '目的地经度，纬度，坐标格式为：经度，纬度'}}, 'required': ['origin', 'destination']}        
**(7)驾车路径规划**                
name='maps_direction_driving'          
description='驾车路径规划 API 可以根据用户起终点经纬度坐标规划以小客车、轿车通勤出行的方案，并且返回通勤方案的数据。'            
inputSchema={'type': 'object', 'properties': {'origin': {'type': 'string', 'description': '出发点经度，纬度，坐标格式为：经度，纬度'}, 'destination': {'type': 'string', 'description': '目的地经度，纬度，坐标格式为：经度，纬度'}}, 'required': ['origin', 'destination']}            
**(8)公交路径规划**              
name='maps_direction_transit_integrated'           
description='公交路径规划 API 可以根据用户起终点经纬度坐标规划综合各类公共（火车、公交、地铁）交通方式的通勤方案，并且返回通勤方案的数据，跨城场景下必须传起点城市与终点城市'           
inputSchema={'type': 'object', 'properties': {'origin': {'type': 'string', 'description': '出发点经度，纬度，坐标格式为：经度，纬度'}, 'destination': {'type': 'string', 'description': '目的地经度，纬度，坐标格式为：经度，纬度'}, 'city': {'type': 'string', 'description': '公共交通规划起点城市'}, 'cityd': {'type': 'string', 'description': '公共交通规划终点城市'}}, 'required': ['origin', 'destination', 'city', 'cityd']}         
**(9)距离测量**              
name='maps_distance'            
description='距离测量 API 可以测量两个经纬度坐标之间的距离,支持驾车、步行以及球面距离测量'      
inputSchema={'type': 'object', 'properties': {'origins': {'type': 'string', 'description': '起点经度，纬度，可以传多个坐标，使用分号隔离，比如120,30;120,31，坐标格式为：经度，纬度'}, 'destination': {'type': 'string', 'description': '终点经度，纬度，坐标格式为：经度，纬度'}, 'type': {'type': 'string', 'description': '距离测量类型,1代表驾车距离测量，0代表直线距离测量，3步行距离测量'}}, 'required': ['origins', 'destination']}        
**(10)关键词搜索**         
name='maps_text_search'           
description='关键词搜，根据用户传入关键词，搜索出相关的POI'           
inputSchema={'type': 'object', 'properties': {'keywords': {'type': 'string', 'description': '搜索关键词'}, 'city': {'type': 'string', 'description': '查询城市'}, 'types': {'type': 'string', 'description': 'POI类型，比如加油站'}}, 'required': ['keywords']}              
**(11)周边搜索**            
name='maps_search_detail'            
description='查询关键词搜或者周边搜获取到的POI ID的详细信息'              
inputSchema={'type': 'object', 'properties': {'id': {'type': 'string', 'description': '关键词搜或者周边搜获取到的POI ID'}}, 'required': ['id']}              
**(12)详情搜索**                 
name='maps_around_search'            
description='周边搜，根据用户传入关键词以及坐标location，搜索出radius半径范围的POI'              
inputSchema={'type': 'object', 'properties': {'keywords': {'type': 'string', 'description': '搜索关键词'}, 'location': {'type': 'string', 'description': '中心点经度纬度'}, 'radius': {'type': 'string', 'description': '搜索半径'}}, 'required': ['location']})]               


# 2、前期准备工作
## 2.1 集成开发环境搭建  
anaconda提供python虚拟环境,pycharm提供集成开发环境                                              
**具体参考如下视频:**                        
【大模型应用开发-入门系列】03 集成开发环境搭建-开发前准备工作                         
https://youtu.be/KyfGduq5d7w                     

## 2.2 大模型LLM服务接口调用方案
(1)gpt大模型等国外大模型使用方案                  
国内无法直接访问，可以使用代理的方式，具体代理方案自己选择                        
这里推荐大家使用:https://nangeai.top/register?aff=Vxlp                        
(2)非gpt大模型方案 OneAPI方式或大模型厂商原生接口                                              
(3)本地开源大模型方案(Ollama方式)                                              
**具体参考如下视频:**                                           
【大模型应用开发-入门系列】04 大模型LLM服务接口调用方案                    
https://youtu.be/mTrgVllUl7Y                           


# 3、项目初始化
## 3.1 下载源码
GitHub或Gitee中下载工程文件到本地，下载地址如下：                
https://github.com/NanGePlus/ReActAgentsTest                                                                                 
https://gitee.com/NanGePlus/ReActAgentsTest                                                                                     

## 3.2 构建项目 
使用pycharm构建一个项目，为项目配置虚拟python环境                          
项目名称：ReActAgentsTest                                                         
虚拟环境名称保持与项目名称一致                             

## 3.3 将相关代码拷贝到项目工程中           
将下载的代码文件夹中的文件全部拷贝到新建的项目根目录下                             

## 3.4 安装项目依赖                            
新建命令行终端，在终端中运行如下指令进行安装             
pip install langgraph==0.4.5                     
pip install langchain==0.3.25                             
pip install langchain-openai==0.3.17                                                       
pip install langchain-mcp-adapters==0.1.0                  
**注意:** 建议先使用要求的对应版本进行本项目测试，避免因版本升级造成的代码不兼容。测试通过后，可进行升级测试                               


# 4、功能测试 
进入到02_ReActAgentHILTest中运行01_reviewCustomToolCalls.py脚本进行测试                                    
进入到02_ReActAgentHILTest中运行02_reviewMCPToolCalls.py脚本进行测试                                     
进入到02_ReActAgentHILTest中运行03_reviewMixToolCalls.py脚本进行测试                                    

         
 