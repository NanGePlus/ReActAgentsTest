# 导入操作系统模块，用于环境变量、路径等系统级操作
import os
# 导入日志模块，用于记录运行过程中的各种日志信息
import logging
# 导入支持多进程/多线程安全写入并按大小轮转的日志处理器
from concurrent_log_handler import ConcurrentRotatingFileHandler
# 从 langchain_openai 包中导入对话模型和向量嵌入模型类
from langchain_openai import ChatOpenAI,OpenAIEmbeddings
# 从当前包中导入配置类 Config，用于统一管理配置
from .config import Config



# Author:@南哥AGI研习社 (B站 or YouTube 搜索“南哥AGI研习社”)


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


# 定义不同 LLM 类型对应的模型与接口配置
MODEL_CONFIGS = {
    # 使用自定义 openai 代理服务的配置
    "openai": {
        # LLM 服务的基础 URL
        "base_url": "https://nangeai.top/v1",
        # 调用该服务所需的 API Key
        "api_key": "sk-k9NrHx3432fgsdKrF1f4R3452248CCLyT1RwRoOkfF10oq",
        # 对话模型名称
        "chat_model": "deepseek-v3.2",
        # 向量嵌入模型名称
        "embedding_model": "text-embedding-3-small"
    },
    # 使用 oneapi 网关服务的配置
    "oneapi": {
        # oneapi 服务的基础 URL
        "base_url": "http://139.224.72.218:3000/v1",
        # oneapi 的访问密钥
        "api_key": "sk-GseYmJ8pX1D0I004W7a435weew2312342r343B724FfD66aD9",
        # 对话模型名称
        "chat_model": "qwen-max",
        # 向量嵌入模型名称
        "embedding_model": "text-embedding-v1"
    },
    # 直连通义千问兼容 OpenAI 协议的配置
    "qwen": {
        # DashScope 兼容模式的基础 URL
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        # DashScope 的 API Key
        "api_key": "sk-f718953873a8445436888345890d8843026e2e5",
        # 对话模型名称
        "chat_model": "qwen-turbo-latest",
        # 向量嵌入模型名称
        "embedding_model": "text-embedding-v1"
    },
    # 本地 ollama 服务的配置
    "ollama": {
        # 本地 ollama HTTP 接口地址
        "base_url": "http://localhost:11434/v1",
        # 兼容 OpenAI 协议时需要传一个伪 API Key，这里固定写死
        "api_key": "ollama",
        # 使用的本地 LLaMA 对话模型
        "chat_model": "llama3.1:8b",
        # 使用的本地嵌入模型名称
        "embedding_model": "nomic-embed-text:latest"
    }
}


# 默认的 LLM 类型，未指定时优先使用该类型
DEFAULT_LLM_TYPE = "openai"
# 默认温度为 0，使模型输出更稳定、更可控
DEFAULT_TEMPERATURE = 0


# 自定义异常类，在 LLM 初始化失败时统一抛出该异常
class LLMInitializationError(Exception):
    """自定义异常类用于LLM初始化错误"""
    pass


# 定义函数用于初始化 LLM 与 Embedding 实例，并返回二者
def initialize_llm(llm_type: str = DEFAULT_LLM_TYPE) -> tuple[ChatOpenAI, OpenAIEmbeddings]:
    """
    初始化LLM实例

    Args:
        llm_type (str): LLM类型，可选值为 'openai', 'oneapi', 'qwen', 'ollama'

    Returns:
        ChatOpenAI: 初始化后的LLM实例

    Raises:
        LLMInitializationError: 当LLM初始化失败时抛出
    """
    try:
        # 检查传入的 llm_type 是否在预定义的配置字典中
        if llm_type not in MODEL_CONFIGS:
            # 如果不支持该类型，则先抛出 ValueError 供下方捕获
            raise ValueError(f"不支持的LLM类型: {llm_type}. 可用的类型: {list(MODEL_CONFIGS.keys())}")

        # 根据指定类型获取对应的配置
        config = MODEL_CONFIGS[llm_type]

        # 对 ollama 类型做特殊处理
        if llm_type == "ollama":
            # 使用兼容 OpenAI 协议的方式时，需要设置 OPENAI_API_KEY 环境变量
            os.environ["OPENAI_API_KEY"] = "NA"

        # 创建对话 LLM 实例
        llm_chat = ChatOpenAI(
            # 指定后端服务地址
            base_url=config["base_url"],
            # 指定访问后端的 API Key
            api_key=config["api_key"],
            # 指定使用的聊天模型名称
            model=config["chat_model"],
            # 控制模型输出的随机性，这里使用统一默认值
            temperature=DEFAULT_TEMPERATURE,
            # 设置单次调用的超时时间（秒），避免长时间阻塞
            timeout=30,
            # 设置失败时的最大重试次数，提高稳定性
            max_retries=2
        )

        # 创建向量嵌入模型实例
        llm_embedding = OpenAIEmbeddings(
            # 嵌入服务的基础 URL，与 chat 使用同一后端
            base_url=config["base_url"],
            # 访问嵌入服务的 API Key
            api_key=config["api_key"],
            # 嵌入模型名称
            model=config["embedding_model"],
            # 部署名称，一般与模型名保持一致
            deployment=config["embedding_model"]
        )

        # 记录成功初始化的日志，包含当前使用的 llm_type
        logger.info(f"成功初始化 {llm_type} LLM")
        # 返回对话模型和嵌入模型两个实例
        return llm_chat, llm_embedding

    # 捕获配置不正确导致的 ValueError
    except ValueError as ve:
        # 记录详细的配置错误日志
        logger.error(f"LLM配置错误: {str(ve)}")
        # 将其包装成自定义异常并抛出，方便统一处理
        raise LLMInitializationError(f"LLM配置错误: {str(ve)}")
    # 捕获其他所有异常
    except Exception as e:
        # 记录通用的初始化失败日志
        logger.error(f"初始化LLM失败: {str(e)}")
        # 抛出自定义异常，供调用方判断与重试
        raise LLMInitializationError(f"初始化LLM失败: {str(e)}")


# 提供对外使用的封装函数，负责获取 LLM 实例并带有容错逻辑
def get_llm(llm_type: str = DEFAULT_LLM_TYPE) -> ChatOpenAI:
    """
    获取LLM实例的封装函数，提供默认值和错误处理

    Args:
        llm_type (str): LLM类型

    Returns:
        ChatOpenAI: LLM实例
    """
    try:
        # 直接调用初始化函数，返回 (chat, embedding) 元组
        return initialize_llm(llm_type)
    # 捕获自定义的初始化异常
    except LLMInitializationError as e:
        # 打印警告日志，说明会尝试使用默认配置重试
        logger.warning(f"使用默认配置重试: {str(e)}")
        # 如果当前类型不是默认类型，则退回到默认 LLM 类型再尝试一次
        if llm_type != DEFAULT_LLM_TYPE:
            return initialize_llm(DEFAULT_LLM_TYPE)
        # 如果已经是默认类型仍然失败，则继续向上抛出异常
        raise



# 仅在当前文件作为脚本直接运行时执行下面的测试代码
if __name__ == "__main__":
    try:
        # 测试使用 openai 配置初始化 LLM 与 Embedding
        llm_openai, llm_embedding = get_llm("openai")

        # 测试传入一个无效的 llm_type，触发错误处理逻辑
        llm_invalid = get_llm("invalid_type")
    # 捕获初始化相关的自定义异常
    except LLMInitializationError as e:
        # 记录致命错误，并终止程序
        logger.error(f"程序终止: {str(e)}")
