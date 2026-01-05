import logging
from concurrent_log_handler import ConcurrentRotatingFileHandler
import redis.asyncio as redis
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import uuid
import json
from .models import AgentResponse
from .config import Config
from datetime import timedelta



# Author:@南哥AGI研习社 (B站 or YouTube 搜索“南哥AGI研习社”)


# 设置日志基本配置，级别为DEBUG或INFO
logger = logging.getLogger(__name__)
# 设置日志器级别为DEBUG
logger.setLevel(logging.DEBUG)
logger.handlers = []  # 清空默认处理器
# 使用ConcurrentRotatingFileHandler
handler = ConcurrentRotatingFileHandler(
    # 日志文件
    Config.LOG_FILE,
    # 日志文件最大允许大小为5MB，达到上限后触发轮转
    maxBytes=Config.MAX_BYTES,
    # 在轮转时，最多保留3个历史日志文件
    backupCount=Config.BACKUP_COUNT
)
# 设置处理器级别为DEBUG
handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
))
logger.addHandler(handler)


# 实现redis相关方法 支持多用户多会话
# Redis管理
# 实现redis相关方法 支持多用户多会话
class RedisSessionManager:
    # 初始化 RedisSessionManager 实例
    # 配置 Redis 连接参数和默认会话超时时间
    def __init__(self, redis_host: str, redis_port: int, redis_db: int, session_timeout: int):
        # 创建 Redis 客户端连接
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            decode_responses=True
        )
        # 设置默认会话过期时间（秒）
        self.session_timeout = session_timeout

    # 关闭 Redis 连接
    async def close(self):
        # 异步关闭 Redis 客户端连接
        await self.redis_client.close()

    # 创建指定用户的新会话
    async def create_session(self, user_id: str, session_id: Optional[str] = None, status: str = "active",
                            last_query: Optional[str] = None, last_response: Optional['AgentResponse'] = None,
                            last_updated: Optional[float] = None, ttl: Optional[int] = None) -> str:
        # 如果未提供 session_id，生成新的 UUID
        if session_id is None:
            session_id = str(uuid.uuid4())
        # 如果未提供最后更新时间，设置为 0 秒
        if last_updated is None:
            last_updated = str(timedelta(seconds=0))
        # 使用提供的 TTL 或默认的 session_timeout
        effective_ttl = ttl if ttl is not None else self.session_timeout

        # 构造会话数据结构
        session_data = {
            "session_id": session_id,
            "status": status,
            "last_response": last_response.model_dump() if isinstance(last_response, BaseModel) else last_response,
            "last_query": last_query,
            "last_updated": last_updated
        }

        # 将会话数据存储到 Redis，使用 JSON 序列化，并设置过期时间
        await self.redis_client.set(
            f"session:{user_id}:{session_id}",
            json.dumps(session_data, default=lambda o: o.__dict__ if not hasattr(o, 'model_dump') else o.model_dump()),
            ex=effective_ttl
        )
        # 将 session_id 添加到用户的会话列表中
        await self.redis_client.sadd(f"user_sessions:{user_id}", session_id)
        # 返回新创建的 session_id
        return session_id

    # 更新指定用户的特定会话数据
    async def update_session(self, user_id: str, session_id: str, status: Optional[str] = None,
                            last_query: Optional[str] = None, last_response: Optional['AgentResponse'] = None,
                            last_updated: Optional[float] = None, ttl: Optional[int] = None) -> bool:
        # 检查会话是否存在
        if await self.redis_client.exists(f"session:{user_id}:{session_id}"):
            # 获取当前会话数据
            current_data = await self.get_session(user_id, session_id)
            if not current_data:
                return False
            # 更新提供的字段
            if status is not None:
                current_data["status"] = status
            if last_response is not None:
                if isinstance(last_response, BaseModel):
                    current_data["last_response"] = last_response.model_dump()
                else:
                    current_data["last_response"] = last_response
            if last_query is not None:
                current_data["last_query"] = last_query
            if last_updated is not None:
                current_data["last_updated"] = last_updated
            # 使用提供的 TTL 或默认的 session_timeout
            effective_ttl = ttl if ttl is not None else self.session_timeout
            # 将更新后的数据重新存储到 Redis，并设置新的过期时间
            await self.redis_client.set(
                f"session:{user_id}:{session_id}",
                json.dumps(current_data,
                           default=lambda o: o.__dict__ if not hasattr(o, 'model_dump') else o.model_dump()),
                ex=effective_ttl
            )
            # 更新成功返回 True
            return True
        # 会话不存在返回 False
        return False

    # 获取指定用户当前会话ID的状态数据
    async def get_session(self, user_id: str, session_id: str) -> Optional[dict]:
        # 从 Redis 获取会话数据
        session_data = await self.redis_client.get(f"session:{user_id}:{session_id}")
        # 如果会话不存在，返回 None
        if not session_data:
            return None
        # 解析 JSON 数据
        session = json.loads(session_data)
        # 处理 last_response 字段，尝试转换为 AgentResponse 对象
        if session and "last_response" in session:
            if session["last_response"] is not None:
                try:
                    session["last_response"] = AgentResponse(**session["last_response"])
                except Exception as e:
                    # 记录转换失败的错误日志
                    logger.error(f"转换 last_response 失败: {e}")
                    session["last_response"] = None
        # 返回会话数据
        return session

    # 获取指定用户下的当前激活的会话ID
    async def get_user_active_session_id(self, user_id: str) -> str | None:
        # 在查询前清理指定用户的无效会话
        await self.cleanup_user_sessions(user_id)

        # 获取用户的所有 session_id
        session_ids = await self.redis_client.smembers(f"user_sessions:{user_id}")

        # 初始化最新会话信息
        latest_session_id = None
        latest_timestamp = -1  # 使用负值确保任何有效时间戳都更大

        # 遍历每个 session_id，获取会话数据
        for session_id in session_ids:
            session = await self.get_session(user_id, session_id)
            if session:
                last_updated = session.get('last_updated')
                # 过滤掉 last_updated 为 "0:00:00" 的记录
                if isinstance(last_updated, str) and last_updated == "0:00:00":
                    continue
                # 确保 last_updated 是数字（时间戳）
                if isinstance(last_updated, (int, float)) and last_updated > latest_timestamp:
                    latest_timestamp = last_updated
                    latest_session_id = session_id

        # 返回最新会话ID，如果没有有效会话则返回 None
        return latest_session_id

    # 获取指定用户下的所有 session_id
    async def get_all_session_ids(self, user_id: str) -> List[str]:
        # 在查询前清理指定用户的无效会话，确保返回的 session_id 都是有效的
        await self.cleanup_user_sessions(user_id)
        # 从 Redis 获取用户的所有 session_id
        session_ids = await self.redis_client.smembers(f"user_sessions:{user_id}")
        # 将集合转换为列表并返回
        return list(session_ids)

    # 获取系统内所有用户下的所有 session_id
    async def get_all_users_session_ids(self) -> Dict[str, List[str]]:
        # 清理所有用户的无效会话
        await self.cleanup_all_sessions()
        # 初始化结果字典
        result = {}
        # 遍历所有 user_sessions:* 键
        async for key in self.redis_client.scan_iter("user_sessions:*"):
            # 提取用户 ID
            user_id = key.split(":", 1)[1]
            # 获取该用户的所有 session_id
            session_ids = await self.redis_client.smembers(f"user_sessions:{user_id}")
            # 如果集合非空，将用户 ID 和 session_id 列表存入结果字典
            if session_ids:
                result[user_id] = list(session_ids)
        # 返回所有用户及其 session_id
        return result

    # 获取指定用户ID的所有会话状态详情数据
    async def get_all_user_sessions(self, user_id: str) -> List[dict]:
        # 初始化会话列表
        sessions = []
        # 获取用户的所有 session_id
        session_ids = await self.redis_client.smembers(f"user_sessions:{user_id}")
        # 遍历每个 session_id，获取会话数据
        for session_id in session_ids:
            session = await self.get_session(user_id, session_id)
            if session:
                sessions.append(session)
        # 返回所有会话数据
        return sessions

    # 检查指定用户ID是否在 Redis 中
    async def user_id_exists(self, user_id: str) -> bool:
        # 在查询前清理指定用户的无效会话
        await self.cleanup_user_sessions(user_id)
        # 检查是否存在 user_sessions:{user_id} 键
        return (await self.redis_client.exists(f"user_sessions:{user_id}")) > 0

    # 检查指定用户ID的特定 session_id 是否存在
    async def session_id_exists(self, user_id: str, session_id: str) -> bool:
        # 在查询前清理指定用户的无效会话
        await self.cleanup_user_sessions(user_id)
        # 检查指定用户的特定会话是否存在
        return (await self.redis_client.exists(f"session:{user_id}:{session_id}")) > 0

    # 获取所有会话数量
    async def get_session_count(self) -> int:
        # 清理所有用户的无效会话
        await self.cleanup_all_sessions()
        # 初始化计数器
        count = 0
        # 遍历所有 session:* 键
        async for _ in self.redis_client.scan_iter("session:*"):
            count += 1
        # 返回会话总数
        return count

    # 清理指定用户的无效会话
    async def cleanup_user_sessions(self, user_id: str) -> None:
        # 获取用户会话集合中的所有 session_id
        session_ids = await self.redis_client.smembers(f"user_sessions:{user_id}")
        # 遍历每个 session_id，检查对应的会话键是否存在
        for session_id in session_ids:
            if not await self.redis_client.exists(f"session:{user_id}:{session_id}"):
                # 如果会话键已过期或不存在，从集合中移除 session_id
                await self.redis_client.srem(f"user_sessions:{user_id}", session_id)
                logger.info(f"Removed expired session_id {session_id} for user {user_id}")
        # 如果集合为空，删除集合
        if not await self.redis_client.scard(f"user_sessions:{user_id}"):
            await self.redis_client.delete(f"user_sessions:{user_id}")
            logger.info(f"Deleted empty user_sessions collection for user {user_id}")

    # 清理所有用户的无效会话
    async def cleanup_all_sessions(self) -> None:
        # 遍历所有 user_sessions:* 键
        async for key in self.redis_client.scan_iter("user_sessions:*"):
            # 提取用户 ID
            user_id = key.split(":", 1)[1]
            # 获取用户会话集合中的所有 session_id
            session_ids = await self.redis_client.smembers(f"user_sessions:{user_id}")
            # 遍历每个 session_id，检查对应的会话键是否存在
            for session_id in session_ids:
                if not await self.redis_client.exists(f"session:{user_id}:{session_id}"):
                    # 如果会话键已过期或不存在，从集合中移除 session_id
                    await self.redis_client.srem(f"user_sessions:{user_id}", session_id)
                    logger.info(f"Removed expired session_id {session_id} for user {user_id}")
            # 如果集合为空，删除集合
            if not await self.redis_client.scard(f"user_sessions:{user_id}"):
                await self.redis_client.delete(f"user_sessions:{user_id}")
                logger.info(f"Deleted empty user_sessions collection for user {user_id}")

    # 删除指定用户的特定会话
    async def delete_session(self, user_id: str, session_id: str) -> bool:
        # 从用户会话列表中移除 session_id
        await self.redis_client.srem(f"user_sessions:{user_id}", session_id)
        # 删除会话数据并返回是否成功
        return (await self.redis_client.delete(f"session:{user_id}:{session_id}")) > 0


# 实例化redis实例并返回
def get_session_manager():
    # 实例化异步Redis会话管理器 并存储为单实例
    session_manager = RedisSessionManager(
        Config.REDIS_HOST,
        Config.REDIS_PORT,
        Config.REDIS_DB,
        Config.SESSION_TIMEOUT
    )

    logger.info("Redis初始化成功")
    return session_manager


