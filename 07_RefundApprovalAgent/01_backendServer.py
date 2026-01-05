# 导入日志模块，用于记录应用程序运行时的信息
import logging
# 导入并发日志处理器，支持多进程安全的日志文件轮转
from concurrent_log_handler import ConcurrentRotatingFileHandler
# 导入时间模块，用于处理时间相关操作
import time
# 从FastAPI导入核心类和异常处理
from fastapi import FastAPI, HTTPException
# 导入类型提示相关的类型
from typing import Dict, Any, Optional, List
# 导入UUID模块，用于生成唯一标识符
import uuid
# 从LangGraph导入中断和命令类型
from langgraph.types import Command
# 从LangChain导入创建智能体的函数
from langchain.agents import create_agent
# 导入异步PostgreSQL检查点保存器，用于保存智能体状态
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
# 导入异步PostgreSQL存储器，用于长期记忆存储
from langgraph.store.postgres import AsyncPostgresStore
# 导入Uvicorn服务器
import uvicorn
# 导入异步上下文管理器，用于管理应用生命周期
from contextlib import asynccontextmanager
# 导入异步PostgreSQL连接池
from psycopg_pool import AsyncConnectionPool
# 导入自定义的数据模型
from utils.models import (AgentRequest, AgentResponse, InterruptResponse, SystemInfoResponse, LongMemRequest,
                          SessionInfoResponse, ActiveSessionInfoResponse, SessionStatusResponse)
# 导入Redis会话管理器获取函数
from utils.redis import get_session_manager
# 导入配置类
from utils.config import Config
# 导入大语言模型获取函数
from utils.llms import get_llm
# 导入工具获取函数
from utils.tools import get_tools



# 作者信息注释
# Author:@南哥AGI研习社 (B站 or YouTube 搜索"南哥AGI研习社")


# 获取当前模块的日志记录器实例
logger = logging.getLogger(__name__)
# 将日志记录器的级别设置为DEBUG，记录所有调试信息
logger.setLevel(logging.DEBUG)
# 清空日志记录器的默认处理器列表
logger.handlers = []
# 创建并发安全的日志文件轮转处理器
handler = ConcurrentRotatingFileHandler(
    # 指定日志文件路径
    Config.LOG_FILE,
    # 设置单个日志文件的最大字节数，超过此大小将触发轮转
    maxBytes = Config.MAX_BYTES,
    # 设置保留的历史日志文件数量
    backupCount = Config.BACKUP_COUNT
)
# 设置处理器的日志级别为DEBUG
handler.setLevel(logging.DEBUG)
# 为处理器设置日志格式，包含时间、模块名、级别和消息
handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
))
# 将配置好的处理器添加到日志记录器
logger.addHandler(handler)

# 定义异步函数，用于解析和格式化显示state消息列表
async def parse_messages(messages: List[Any]) -> None:
    """
    解析消息列表，打印 HumanMessage、AIMessage 和 ToolMessage 的详细信息

    Args:
        messages: 包含消息的列表，每个消息是一个对象
    """
    # 打印消息解析结果的分隔标题
    print("=== 消息解析结果 ===")
    # 遍历消息列表，索引从1开始
    for idx, msg in enumerate(messages, 1):
        # 打印当前消息的序号
        print(f"\n消息 {idx}:")
        # 获取消息对象的类名作为消息类型
        # 获取消息类型
        msg_type = msg.__class__.__name__
        # 打印消息类型
        print(f"类型: {msg_type}")
        # 提取消息的内容属性，如果不存在则为空字符串
        # 提取消息内容
        content = getattr(msg, 'content', '')
        # 打印消息内容，如果为空则显示"<空>"
        print(f"内容: {content if content else '<空>'}")
        # 获取消息的附加参数字典
        # 处理附加信息
        additional_kwargs = getattr(msg, 'additional_kwargs', {})
        # 如果存在附加参数
        if additional_kwargs:
            # 打印附加信息标题
            print("附加信息:")
            # 遍历附加参数的键值对
            for key, value in additional_kwargs.items():
                # 如果键是工具调用且值不为空
                if key == 'tool_calls' and value:
                    # 打印工具调用标题
                    print("  工具调用:")
                    # 遍历每个工具调用
                    for tool_call in value:
                        # 打印工具调用的ID
                        print(f"    - ID: {tool_call['id']}")
                        # 打印工具调用的函数名
                        print(f"      函数: {tool_call['function']['name']}")
                        # 打印工具调用的参数
                        print(f"      参数: {tool_call['function']['arguments']}")
                # 对于其他附加参数
                else:
                    # 打印键值对
                    print(f"  {key}: {value}")
        # 如果消息类型是工具消息
        # 处理 ToolMessage 特有字段
        if msg_type == 'ToolMessage':
            # 获取工具名称
            tool_name = getattr(msg, 'name', '')
            # 获取工具调用ID
            tool_call_id = getattr(msg, 'tool_call_id', '')
            # 打印工具名称
            print(f"工具名称: {tool_name}")
            # 打印工具调用ID
            print(f"工具调用 ID: {tool_call_id}")
        # 如果消息类型是AI消息
        # 处理 AIMessage 的工具调用和元数据
        if msg_type == 'AIMessage':
            # 获取工具调用列表
            tool_calls = getattr(msg, 'tool_calls', [])
            # 如果存在工具调用
            if tool_calls:
                # 打印工具调用标题
                print("工具调用:")
                # 遍历每个工具调用
                for tool_call in tool_calls:
                    # 打印工具名称
                    print(f"  - 名称: {tool_call['name']}")
                    # 打印工具参数
                    print(f"    参数: {tool_call['args']}")
                    # 打印工具ID
                    print(f"    ID: {tool_call['id']}")
            # 获取响应元数据
            # 提取元数据
            metadata = getattr(msg, 'response_metadata', {})
            # 如果存在元数据
            if metadata:
                # 打印元数据标题
                print("元数据:")
                # 获取令牌使用情况
                token_usage = metadata.get('token_usage', {})
                # 打印令牌使用情况
                print(f"  令牌使用: {token_usage}")
                # 打印模型名称，如果不存在则显示"未知"
                print(f"  模型名称: {metadata.get('model_name', '未知')}")
                # 打印完成原因，如果不存在则显示"未知"
                print(f"  完成原因: {metadata.get('finish_reason', '未知')}")
        # 获取消息ID
        # 打印消息 ID
        msg_id = getattr(msg, 'id', '未知')
        # 打印消息ID
        print(f"消息 ID: {msg_id}")
        # 打印分隔线
        print("-" * 50)

# 定义异步函数，用于处理智能体执行结果:可能是中断，也可能是最终结果
async def process_agent_result(
        session_id: str,
        result: Dict[str, Any],
        user_id: Optional[str] = None
) -> AgentResponse:
    """
    处理智能体执行结果，统一处理中断和结果

    Args:
        session_id: 会话ID
        result: 智能体执行结果
        user_id: 用户ID，如果提供，将更新会话状态

    Returns:
        AgentResponse: 标准化的响应对象
    """
    # 初始化响应对象为None
    response = None

    # 使用try-except捕获处理过程中的异常
    try:
        # 检查结果中是否包含中断标记
        if "__interrupt__" in result:
            # 提取中断数据的值
            interrupt_data = result["__interrupt__"][0].value
            # 如果中断数据中没有中断类型字段
            if "interrupt_type" not in interrupt_data:
                # 添加默认的未知中断类型
                interrupt_data["interrupt_type"] = "unknown"
            # 构造中断状态的响应对象
            response = AgentResponse(
                session_id=session_id,
                status="interrupted",
                interrupt_data=interrupt_data
            )
            # 记录中断信息到日志
            logger.info(f"当前触发工具调用中断:{response}")
        # 如果没有中断标记
        else:
            # 构造完成状态的响应对象
            response = AgentResponse(
                session_id=session_id,
                status="completed",
                result=result
            )
            # 记录最终结果到日志
            logger.info(f"最终智能体回复结果:{response}")

    # 捕获异常情况
    except Exception as e:
        # 构造错误状态的响应对象
        response = AgentResponse(
            session_id=session_id,
            status="error",
            message=f"处理智能体结果时出错: {str(e)}"
        )
        # 记录错误信息到日志
        logger.error(f"处理智能体结果时出错:{response}")

    # 检查用户会话是否存在
    exists = await app.state.session_manager.session_id_exists(user_id, session_id)
    # 如果会话存在
    if exists:
        # 获取响应状态
        status = response.status
        # 将最后查询设置为None
        last_query = None
        # 将最后响应设置为当前响应
        last_response = response
        # 记录当前时间戳
        last_updated = time.time()
        # 获取会话TTL（生存时间）
        ttl = Config.TTL
        # 更新会话信息到Redis
        await app.state.session_manager.update_session(user_id, session_id, status, last_query, last_response, last_updated, ttl)

    # 返回处理后的响应对象
    return response

async def read_long_term_info(user_id :str):
    """
    读取指定用户长期记忆中的内容

    Args:
        user_id: 用户的唯一标识

    Returns:
        Dict[str, Any]: 包含记忆内容和状态的响应
    """
    # 使用try-except捕获可能的异常
    try:
        # 构造命名空间元组，包含记忆类型和用户ID
        namespace = ("memories", user_id)

        # 在指定命名空间中搜索所有记忆内容
        memories = await app.state.store.asearch(namespace, query="")

        # 检查搜索结果是否有效
        if memories is None:
            # 如果结果为None，抛出HTTP 500错误
            raise HTTPException(
                status_code=500,
                detail="查询返回无效结果，可能是存储系统错误。"
            )

        # 从搜索结果中提取并拼接记忆内容
        long_term_info = " ".join(
            [d.value["data"] for d in memories if isinstance(d.value, dict) and "data" in d.value]
        ) if memories else ""

        # 记录成功获取记忆的日志信息
        logger.info(f"成功获取用户ID: {user_id} 的长期记忆，内容长度: {len(long_term_info)} 字符")

        # 返回包含成功状态和记忆内容的字典
        return {
            "success": True,
            "user_id": user_id,
            "long_term_info": long_term_info,
            "message": "长期记忆获取成功" if long_term_info else "未找到长期记忆内容"
        }

    # 捕获所有异常
    except Exception as e:
        # 记录错误日志
        logger.error(f"获取用户ID: {user_id} 的长期记忆时发生意外错误: {str(e)}")
        # 抛出HTTP 500错误
        raise HTTPException(
            status_code=500,
            detail=f"获取长期记忆失败: {str(e)}"
        )

# 定义异步函数，用于写入指定用户的长期记忆
async def write_long_term_info(user_id :str, memory_info :str):
    """
    指定用户写入长期记忆内容

    Args:
        user_id: 用户的唯一标识
        memory_info: 要保存的记忆内容

    Returns:
        Dict[str, Any]: 包含成功状态和存储记忆ID的结果
    """
    # 使用try-except捕获可能的异常
    try:
        # 构造命名空间元组
        namespace = ("memories", user_id)
        # 生成唯一的记忆ID
        memory_id = str(uuid.uuid4())
        # 将记忆内容存储到指定命名空间
        result = await app.state.store.aput(
            namespace=namespace,
            key=memory_id,
            value={"data": memory_info}
        )
        # 记录存储成功的日志
        logger.info(f"成功为用户ID: {user_id} 存储记忆，记忆ID: {memory_id}")
        # 返回存储成功的响应字典
        return {
            "success": True,
            "memory_id": memory_id,
            "message": "记忆存储成功"
        }

    # 捕获所有异常
    except Exception as e:
        # 记录错误日志
        logger.error(f"存储用户ID: {user_id} 的记忆时发生意外错误: {str(e)}")
        # 抛出HTTP 500错误
        raise HTTPException(
            status_code=500,
            detail=f"存储记忆失败: {str(e)}"
        )

# 定义异步上下文管理器，用于管理应用的生命周期，app应用初始化函数
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 使用try-except-finally确保资源正确清理
    try:
        # 创建并初始化Redis会话管理器实例
        app.state.session_manager = get_session_manager()
        # 记录Redis初始化成功日志
        logger.info("Redis初始化成功")

        # 获取聊天模型和嵌入模型实例
        llm_chat, llm_embedding = get_llm(Config.LLM_TYPE)
        # 记录模型初始化成功日志
        logger.info("Chat模型初始化成功")

        # 创建异步PostgreSQL连接池，动态连接池根据负载调整连接池大小
        async with AsyncConnectionPool(
                # 数据库连接字符串
                conninfo=Config.DB_URI,
                # 连接池最小连接数
                min_size=Config.MIN_SIZE,
                # 连接池最大连接数
                max_size=Config.MAX_SIZE,
                # 连接参数：启用自动提交和禁用预处理语句
                kwargs={"autocommit": True, "prepare_threshold": 0},
                # 延迟打开连接池
                open=False
        ) as pool:
            # 创建短期记忆检查点保存器实例
            app.state.checkpointer = AsyncPostgresSaver(pool)
            # 初始化检查点保存器的数据库表结构
            await app.state.checkpointer.setup()
            # 记录检查点保存器初始化成功日志
            logger.info("短期记忆Checkpointer初始化成功")

            # 创建长期记忆存储器实例
            app.state.store = AsyncPostgresStore(pool)
            # 初始化存储器的数据库表结构
            await app.state.store.setup()
            # 记录存储器初始化成功日志
            logger.info("长期记忆store初始化成功")

            # 获取智能体可用的工具列表
            tools = await get_tools()

            # 创建ReAct智能体实例
            app.state.agent = create_agent(
                # 使用的聊天模型
                model=llm_chat,
                # 可用的工具列表
                tools=tools,
                # 短期记忆检查点保存器
                checkpointer=app.state.checkpointer,
                # 长期记忆存储器
                store=app.state.store
            )
            # 记录智能体初始化成功日志
            logger.info("Agent初始化成功")

            # 记录服务完成初始化日志
            logger.info("服务完成初始化并启动服务")

            # yield将控制权交给应用运行
            yield

    # 捕获初始化过程中的异常
    except Exception as e:
        # 记录初始化失败日志
        logger.error(f"初始化失败: {str(e)}")
        # 抛出运行时错误
        raise RuntimeError(f"服务初始化失败: {str(e)}")

    # 无论是否发生异常都执行清理操作
    # 清理资源
    finally:
        # 关闭Redis连接
        # 关闭Redis连接
        await app.state.session_manager.close()
        # 关闭PostgreSQL连接池
        # 关闭PostgreSQL连接池
        await pool.close()
        # 记录资源清理完成日志
        logger.info("关闭服务并完成资源清理")

# 创建FastAPI应用实例
app = FastAPI(
    # 应用标题
    title="Agent智能体后端API接口服务",
    # 应用描述
    description="基于LangGraph提供AI Agent服务",
    # 指定生命周期管理函数
    lifespan=lifespan
)

# 定义POST接口，用于调用智能体并返回大模型结果或中断数据
@app.post("/agent/invoke", response_model=AgentResponse)
async def invoke_agent(request: AgentRequest):
    # 记录接口调用日志
    logger.info(f"调用/agent/invoke接口，运行智能体并返回大模型结果或中断数据，接受到前端用户请求:{request}")
    # 从请求中提取用户ID
    user_id = request.user_id
    # 从请求中提取会话ID
    session_id = request.session_id

    # 读取用户的长期记忆内容
    result = await read_long_term_info(user_id)
    # 检查是否成功获取长期记忆
    if result.get("success", False):
        # 提取长期记忆内容
        long_term_info = result.get("long_term_info")
        # 如果获取到的记忆内容不为空
        if long_term_info:
            # 将记忆内容拼接到系统提示词中
            system_message = f"{request.system_message}我的附加信息有:{long_term_info}"
            # 记录拼接后的系统提示词日志
            logger.info(f"获取用户偏好配置数据，system_message的信息为:{system_message}")
        # 如果记忆内容为空
        else:
            # 直接使用原始系统提示词
            system_message = request.system_message
            # 记录未获取到记忆的日志
            logger.info(f"未获取到用户偏好配置数据，system_message的信息为:{system_message}")
    # 如果获取记忆失败
    else:
        # 直接使用原始系统提示词
        system_message = request.system_message
        # 记录未获取到记忆的日志
        logger.info(f"未获取到用户偏好配置数据，system_message的信息为:{system_message}")

    # 检查用户会话是否存在
    exists = await app.state.session_manager.session_id_exists(user_id, session_id)

    # 如果会话不存在
    if not exists:
        # 设置会话初始状态为空闲
        status = "idle"
        # 初始化最后查询为None
        last_query = None
        # 初始化最后响应为None
        last_response = None
        # 记录当前时间戳
        last_updated = time.time()
        # 获取会话TTL配置
        ttl = Config.TTL
        # 创建新会话并存储到Redis
        await app.state.session_manager.create_session(user_id, session_id, status, last_query, last_response, last_updated, ttl)

    # 为新请求更新会话信息,设置会话状态为运行中
    status = "running"
    # 记录用户当前查询
    last_query = request.query
    # 清空最后响应
    last_response = None
    # 更新时间戳
    last_updated = time.time()
    # 获取TTL配置
    ttl = Config.TTL
    # 更新会话信息到Redis
    await app.state.session_manager.update_session(user_id, session_id, status, last_query, last_response, last_updated, ttl)

    # 构造智能体的输入消息列表
    messages = [
        # 添加系统消息
        {"role": "system", "content": system_message},
        # 添加用户消息
        {"role": "user", "content": request.query}
    ]

    # 使用try-except处理智能体调用过程中的异常
    try:
        # 调用智能体处理消息
        result = await app.state.agent.ainvoke({"messages": messages}, config={"configurable": {"thread_id": session_id}})
        # 格式化输出返回的消息列表
        await parse_messages(result['messages'])

        # 处理智能体返回结果并更新会话状态
        return await process_agent_result(session_id, result, user_id)

    # 捕获异常情况
    except Exception as e:
        # 构造错误响应对象
        error_response = AgentResponse(
            session_id=session_id,
            status="error",
            message=f"处理请求时出错: {str(e)}"
        )
        # 记录错误日志
        logger.error(f"处理请求时出错: {error_response}")

        # 更新会话状态为错误
        status = "error"
        # 清空最后查询
        last_query = None
        # 记录错误响应
        last_response = error_response
        # 更新时间戳
        last_updated = time.time()
        # 获取TTL配置
        ttl = Config.TTL
        # 更新会话信息到Redis
        await app.state.session_manager.update_session(user_id, session_id, status, last_query, last_response, last_updated, ttl)

        # 返回错误响应
        return error_response

# 定义POST接口，用于恢复被中断的智能体运行并等待运行完成或再次中断
@app.post("/agent/resume", response_model=AgentResponse)
async def resume_agent(response: InterruptResponse):
    # 记录接口调用日志
    logger.info(f"调用/agent/resume接口，恢复被中断的智能体运行并等待运行完成或再次中断，接受到前端用户请求:{response}")
    # 从请求中提取用户ID
    user_id = response.user_id
    # 从请求中提取会话ID
    session_id = response.session_id

    # 检查用户会话是否存在
    exists = await app.state.session_manager.session_id_exists(user_id, session_id)
    # 如果会话不存在
    if not exists:
        # 记录错误日志
        logger.error(f"status_code=404,用户会话 {user_id}:{session_id} 不存在")
        # 抛出404错误
        raise HTTPException(status_code=404, detail=f"用户会话 {user_id}:{session_id} 不存在")

    # 获取会话信息
    session = await app.state.session_manager.get_session(user_id, session_id)
    # 提取会话状态
    status = session.get("status")
    # 如果会话状态不是中断状态
    if status != "interrupted":
        # 记录错误日志
        logger.error(f"status_code=400,会话当前状态为 {status}，无法恢复非中断状态的会话")
        # 抛出400错误
        raise HTTPException(status_code=400, detail=f"会话当前状态为 {status}，无法恢复非中断状态的会话")

    # 更新会话状态为运行中
    status = "running"
    # 清空最后查询
    last_query = None
    # 清空最后响应
    last_response = None
    # 更新时间戳
    last_updated = time.time()
    # 获取TTL配置
    ttl = Config.TTL
    # 更新会话信息到Redis
    await app.state.session_manager.update_session(user_id, session_id, status, last_query, last_response, last_updated, ttl)

    # 构造响应命令数据
    command_data = {
        # 设置响应类型
        "type": response.response_type
    }
    # 如果请求中包含参数
    if response.args:
        # 将参数添加到命令数据中
        command_data["args"] = response.args

    # 使用try-except处理恢复执行过程中的异常
    try:
        # 恢复智能体执行
        result = await app.state.agent.ainvoke(Command(resume=command_data), config={"configurable": {"thread_id": session_id}})
        # 格式化输出返回的消息列表
        await parse_messages(result['messages'])
        # 处理智能体返回结果并更新会话状态
        return await process_agent_result(session_id, result, user_id)

    # 捕获异常情况
    except Exception as e:
        # 构造错误响应对象
        error_response = AgentResponse(
            session_id=session_id,
            status="error",
            message=f"恢复执行时出错: {str(e)}"
        )
        # 记录错误日志
        logger.error(f"处理请求时出错: {error_response}")

        # 更新会话状态为错误
        status = "error"
        # 清空最后查询
        last_query = None
        # 记录错误响应
        last_response = error_response
        # 更新时间戳
        last_updated = time.time()
        # 获取TTL配置
        ttl = Config.TTL
        # 更新会话信息到Redis
        await app.state.session_manager.update_session(user_id, session_id, status, last_query, last_response, last_updated, ttl)

        # 返回错误响应
        return error_response

# 定义GET接口，用于获取指定用户当前会话的状态数据
@app.get("/agent/status/{user_id}/{session_id}", response_model=SessionStatusResponse)
async def get_agent_status(user_id: str, session_id: str):
    # 记录接口调用日志
    logger.info(f"调用/agent/status/接口，获取指定用户当前会话的状态数据，接受到前端用户请求:{user_id}:{session_id}")

    # 检查用户会话是否存在
    exists = await app.state.session_manager.session_id_exists(user_id, session_id)

    # 如果会话不存在
    if not exists:
        # 记录错误日志
        logger.error(f"用户 {user_id}:{session_id} 的会话不存在")
        # 返回会话不存在的响应
        return SessionStatusResponse(
            user_id=user_id,
            session_id=session_id,
            status="not_found",
            message=f"用户 {user_id}:{session_id} 的会话不存在"
        )

    # 如果会话存在，获取会话信息
    session = await app.state.session_manager.get_session(user_id, session_id)
    # 构造会话状态响应对象
    response = SessionStatusResponse(
        user_id=user_id,
        session_id=session_id,
        status=session.get("status"),
        last_query=session.get("last_query"),
        last_updated=session.get("last_updated"),
        last_response=session.get("last_response")
    )
    # 记录返回的会话状态日志
    logger.info(f"返回当前用户的会话状态:{response}")
    # 返回会话状态响应
    return response

# 定义GET接口，用于获取指定用户当前最近一次更新的会话ID
@app.get("/agent/active/sessionid/{user_id}", response_model=ActiveSessionInfoResponse)
async def get_agent_active_sessionid(user_id: str):
    # 记录接口调用日志
    logger.info(f"调用/agent/active/sessionid/接口，获取指定用户当前最近一次更新的会话ID，接受到前端用户请求:{user_id}")

    # 检查用户是否存在
    exists = await app.state.session_manager.user_id_exists(user_id)

    # 如果用户不存在
    if not exists:
        # 记录错误日志
        logger.error(f"用户 {user_id} 的会话不存在")
        # 返回空的活跃会话ID响应
        return ActiveSessionInfoResponse(
            active_session_id=""
        )

    # 如果用户存在，获取活跃会话ID
    response = ActiveSessionInfoResponse(
        # 获取用户的活跃会话ID
        active_session_id=await app.state.session_manager.get_user_active_session_id(user_id)
    )

    # 记录返回的活跃会话ID日志
    logger.info(f"返回当前用户的激活的会话ID:{response}")
    # 返回活跃会话ID响应
    return response

# 定义GET接口，用于获取指定用户的所有会话ID
@app.get("/agent/sessionids/{user_id}", response_model=SessionInfoResponse)
async def get_agent_sessionids(user_id: str):
    # 记录接口调用日志
    logger.info(f"调用/agent/sessionids/接口，获取指定用户的所有会话ID，接受到前端用户请求:{user_id}")

    # 检查用户是否存在
    exists = await app.state.session_manager.user_id_exists(user_id)

    # 如果用户不存在
    if not exists:
        # 记录错误日志
        logger.error(f"用户 {user_id} 的会话不存在")
        # 返回空的会话ID列表响应
        return SessionInfoResponse(
            session_ids=[]
        )

    # 如果用户存在，获取所有会话ID
    response = SessionInfoResponse(
        # 获取用户的所有会话ID列表
        session_ids=await app.state.session_manager.get_all_session_ids(user_id)
    )

    # 记录返回的会话ID列表日志
    logger.info(f"返回当前用户的所有会话ID:{response}")
    # 返回会话ID列表响应
    return response

# 定义GET接口，用于获取当前系统内全部的会话状态信息
@app.get("/system/info", response_model=SystemInfoResponse)
async def get_system_info():
    # 记录接口调用日志
    logger.info(f"调用/system/info接口，获取当前系统内全部的会话状态信息")
    # 构造系统信息响应对象
    response = SystemInfoResponse(
        # 获取系统内会话总数
        sessions_count=await app.state.session_manager.get_session_count(),
        # 获取系统内所有活跃用户及其会话
        active_users=await app.state.session_manager.get_all_users_session_ids()
    )
    # 记录返回的系统状态信息日志
    logger.info(f"返回当前系统状态信息:{response}")
    # 返回系统状态信息响应
    return response

# 定义DELETE接口，用于删除指定用户当前会话
@app.delete("/agent/session/{user_id}/{session_id}")
async def delete_agent_session(user_id: str, session_id: str):
    # 记录接口调用日志
    logger.info(f"调用/agent/session/接口，删除指定用户当前会话，接受到前端用户请求:{user_id}:{session_id}")
    # 检查用户会话是否存在
    exists = await app.state.session_manager.session_id_exists(user_id, session_id)
    # 如果会话不存在
    if not exists:
        # 记录错误日志
        logger.error(f"status_code=404,用户 {user_id}:{session_id} 的会话不存在")
        # 抛出404错误
        raise HTTPException(status_code=404, detail=f"用户会话 {user_id}:{session_id} 不存在")

    # 如果会话存在，删除会话
    await app.state.session_manager.delete_session(user_id, session_id)
    # 构造删除成功的响应字典
    response = {
        "status": "success",
        "message": f"用户 {user_id}:{session_id} 的会话已删除"
    }
    # 记录会话删除成功日志
    logger.info(f"用户会话已经删除:{response}")
    # 返回删除成功响应
    return response

# 定义POST接口，用于写入指定用户的长期记忆
@app.post("/agent/write/longterm")
async def write_long_term(request: LongMemRequest):
    # 记录接口调用日志
    logger.info(f"调用/agent/write/long_term接口，写入指定用户的长期记忆，接受到前端用户请求:{request}")

    # 从请求中提取用户ID
    user_id = request.user_id
    # 从请求中提取记忆内容
    memory_info = request.memory_info

    # 检查用户是否存在
    exists = await app.state.session_manager.user_id_exists(user_id)
    # 如果用户不存在
    if not exists:
        # 记录错误日志
        logger.error(f"status_code=404,用户 {user_id} 不存在")
        # 抛出404错误
        raise HTTPException(status_code=404, detail=f"用户会话 {user_id} 不存在")

    # 调用函数写入长期记忆
    result = await write_long_term_info(user_id, memory_info)

    # 检查写入结果是否成功
    if result.get("success", False):
        # 构造成功响应字典
        return {
            "status": "success",
            "memory_id": result.get("memory_id"),
            "message": result.get("message", "记忆存储成功")
        }
    # 如果写入失败
    else:
        # 抛出500错误
        # 处理非成功返回结果
        raise HTTPException(
            status_code=500,
            detail="记忆存储失败，返回结果未包含成功状态"
        )



# 当脚本作为主程序运行时执行
# 启动服务器
if __name__ == "__main__":
    # 启动Uvicorn服务器，运行FastAPI应用
    uvicorn.run(app, host=Config.HOST, port=Config.PORT)
