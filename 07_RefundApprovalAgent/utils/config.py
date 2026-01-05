import os


# Author:@南哥AGI研习社 (B站 or YouTube 搜索“南哥AGI研习社”)


class Config:
    """统一的配置类，集中管理所有常量"""
    # 日志持久化存储
    LOG_FILE = "logfile/app.log"
    if not os.path.exists(os.path.dirname(LOG_FILE)):
        os.makedirs(os.path.dirname(LOG_FILE))
    MAX_BYTES = 5*1024*1024,
    BACKUP_COUNT = 3

    # PostgreSQL数据库配置参数
    DB_URI = os.getenv("DB_URI", "postgresql://postgres:postgres@localhost:5432/postgres?sslmode=disable")
    MIN_SIZE = 5
    MAX_SIZE = 10

    # Redis数据库配置参数
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_DB = 0
    SESSION_TIMEOUT = 300
    TTL = 3600

    # openai:调用gpt模型,qwen:调用阿里通义千问大模型,oneapi:调用oneapi方案支持的模型,ollama:调用本地开源大模型
    LLM_TYPE = "openai"

    # API服务地址和端口
    HOST = "0.0.0.0"
    PORT = 8001