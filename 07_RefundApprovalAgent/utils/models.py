from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import time



# Author:@南哥AGI研习社 (B站 or YouTube 搜索“南哥AGI研习社”)


# 定义数据模型 客户端发起的运行智能体的请求数据
class AgentRequest(BaseModel):
    # 用户唯一标识
    user_id: str
    # 会话唯一标识
    session_id: str
    # 用户的问题
    query: str
    # 系统提示词
    system_message: Optional[str] = "你会使用工具来帮助用户。如果工具使用被拒绝，请提示用户。"

# 定义数据模型 客户端发起的写入长期记忆的请求数据
class LongMemRequest(BaseModel):
    # 用户唯一标识
    user_id: str
    # 写入的内容
    memory_info: str

# 定义数据模型 运行智能体后返回的响应数据
class AgentResponse(BaseModel):
    # 会话唯一标识
    session_id: str
    # 三个状态：interrupted, completed, error
    status: str
    # 时间戳
    timestamp: float = Field(default_factory=lambda: time.time())
    # error时的提示消息
    message: Optional[str] = None
    # completed时的结果消息
    result: Optional[Dict[str, Any]] = None
    # interrupted时的中断消息
    interrupt_data: Optional[Dict[str, Any]] = None

# 定义数据模型 客户端发起的恢复智能体运行的中断反馈请求数据
class InterruptResponse(BaseModel):
    # 用户唯一标识
    user_id: str
    # 会话唯一标识
    session_id: str
    # 响应类型：accept(允许调用), edit(调整工具参数，此时args中携带修改后的调用参数), response(直接反馈信息，此时args中携带修改后的调用参数)，reject(不允许调用)
    response_type: str
    # 如果是edit, response类型，可能需要额外的参数
    args: Optional[Dict[str, Any]] = None

# 定义数据模型 系统内的会话状态响应数据
class SystemInfoResponse(BaseModel):
    # 当前系统内会话总数
    sessions_count: int
    # 系统内当前活跃的用户和会话
    active_users: Optional[Dict[str, Any]] = None

# 定义数据模型 所有会话ID响应数据
class SessionInfoResponse(BaseModel):
    # 当前用户的所有session_id
    session_ids: List[str]

# 定义数据模型 当前最近一次更新的会话ID响应
class ActiveSessionInfoResponse(BaseModel):
    # 最近一次更新的会话ID
    active_session_id: str

# 定义数据模型 会话状态详情响应数据
class SessionStatusResponse(BaseModel):
    # 用户唯一标识
    user_id: str
    # 会话唯一标识
    session_id: Optional[str] = None
    # 状态：not_found, idle, running, interrupted, completed, error
    status: str
    # error时的提示消息
    message: Optional[str] = None
    # 上次查询
    last_query: Optional[str] = None
    # 上次更新时间
    last_updated: Optional[float] = None
    # 上次响应
    last_response: Optional[AgentResponse] = None
