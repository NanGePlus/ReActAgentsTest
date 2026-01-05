# 导入 uuid 模块，用于生成唯一标识符
import uuid
# 导入 requests 库，用于发送 HTTP 请求
import requests
# 导入 json 模块，用于处理 JSON 数据
import json
# 导入 traceback 模块，用于打印详细的错误堆栈信息
import traceback
# 导入类型提示相关的类型
from typing import Dict, Any, Optional
# 导入 time 模块，用于时间相关操作
import time
# 从 rich.console 导入 Console，用于在终端中显示美化的输出
from rich.console import Console
# 从 rich.prompt 导入 Prompt，用于获取用户输入
from rich.prompt import Prompt
# 从 rich.panel 导入 Panel，用于创建带边框的面板显示
from rich.panel import Panel
# 从 rich.markdown 导入 Markdown，用于渲染 Markdown 格式文本
from rich.markdown import Markdown
# 从 rich.theme 导入 Theme，用于定义自定义主题样式
from rich.theme import Theme
# 从 rich.progress 导入 Progress，用于显示进度条
from rich.progress import Progress



# 作者信息注释
# Author:@南哥AGI研习社 (B站 or YouTube 搜索"南哥AGI研习社")


# 创建自定义的 Rich 主题，定义各种样式的颜色和格式
custom_theme = Theme({
    # 信息样式：青色加粗
    "info": "cyan bold",
    # 警告样式：黄色加粗
    "warning": "yellow bold",
    # 成功样式：绿色加粗
    "success": "green bold",
    # 错误样式：红色加粗
    "error": "red bold",
    # 标题样式：洋红色加粗带下划线
    "heading": "magenta bold underline",
    # 高亮样式：蓝色加粗
    "highlight": "blue bold",
})

# 使用自定义主题初始化 Rich 控制台实例
console = Console(theme=custom_theme)

# 定义后端 API 服务的基础地址
API_BASE_URL = "http://localhost:8001"


# 调用后端 API 接口，运行智能体并返回结果或中断数据
def invoke_agent(user_id: str, session_id: str, query: str,
                 system_message: str = "你会使用工具来帮助用户。如果工具使用被拒绝，请提示用户。"):
    """
    调用智能体处理查询，并等待完成或中断

    Args:
        user_id: 用户唯一标识
        session_id: 会话唯一标识
        query: 用户待查询的问题
        system_message: 系统提示词

    Returns:
        服务端返回的结果
    """
    # 构造请求的 JSON 数据
    # 发送请求到后端API
    payload = {
        "user_id": user_id,
        "session_id": session_id,
        "query": query,
        "system_message": system_message
    }

    # 显示请求发送提示
    console.print("[info]正在发送请求到智能体，请稍候...[/info]")

    # 使用进度条显示请求处理过程
    with Progress() as progress:
        # 添加一个不确定进度的任务
        task = progress.add_task("[cyan]处理中...", total=None)
        # 发送 POST 请求到后端 API
        response = requests.post(f"{API_BASE_URL}/agent/invoke", json=payload)
        # 标记任务完成
        progress.update(task, completed=100)

    # 检查响应状态码
    if response.status_code == 200:
        # 请求成功，返回 JSON 响应数据
        return response.json()
    else:
        # 请求失败，抛出异常并包含状态码和响应内容
        raise Exception(f"API调用失败: {response.status_code} - {response.text}")


# 调用后端 API 接口，恢复被中断的智能体执行并等待运行完成或再次中断
def resume_agent(user_id: str, session_id: str, response_type: str, args: Optional[Dict[str, Any]] = None):
    """
    发送响应以恢复智能体执行

    Args:
        user_id: 用户唯一标识
        session_id: 用户的会话唯一标识
        response_type: 响应类型：accept(允许调用), edit(调整工具参数，此时args中携带修改后的调用参数), response(直接反馈信息，此时args中携带修改后的调用参数)，reject(不允许调用)
        args: 如果是edit, response类型，可能需要额外的参数

    Returns:
        服务端返回的结果
    """
    # 构造恢复请求的 JSON 数据
    payload = {
        "user_id": user_id,
        "session_id": session_id,
        "response_type": response_type,
        "args": args
    }

    # 显示恢复执行的提示
    console.print("[info]正在恢复智能体执行，请稍候...[/info]")

    # 使用进度条显示恢复执行过程
    with Progress() as progress:
        # 添加恢复执行任务
        task = progress.add_task("[cyan]恢复执行中...", total=None)
        # 发送 POST 请求恢复智能体执行
        response = requests.post(f"{API_BASE_URL}/agent/resume", json=payload)
        # 标记任务完成
        progress.update(task, completed=100)

    # 检查响应状态码
    if response.status_code == 200:
        # 恢复成功，返回 JSON 响应数据
        return response.json()
    else:
        # 恢复失败，抛出异常
        raise Exception(f"恢复智能体执行失败: {response.status_code} - {response.text}")


# 调用后端 API 接口，写入指定用户的长期记忆内容
def write_long_term(user_id: str, memory_info: str):
    """
    写入指定用户长期记忆内容

    Args:
        user_id: 用户唯一标识
        memory_info: 写入的内容

    Returns:
        服务端返回的结果
    """
    # 构造写入长期记忆的请求数据
    # 发送请求到后端API
    payload = {
        "user_id": user_id,
        "memory_info": memory_info
    }

    # 显示写入长期记忆的提示
    console.print("[info]正在发送请求写入指定用户长期记忆内容，请稍候...[/info]")

    # 使用进度条显示写入过程
    with Progress() as progress:
        # 添加写入任务
        task = progress.add_task("[cyan]写入长期记忆处理中...", total=None)
        # 发送 POST 请求写入长期记忆
        response = requests.post(f"{API_BASE_URL}/agent/write/longterm", json=payload)
        # 标记任务完成
        progress.update(task, completed=100)

    # 检查响应状态码
    if response.status_code == 200:
        # 写入成功，返回 JSON 响应数据
        return response.json()
    else:
        # 写入失败，抛出异常
        raise Exception(f"API调用失败: {response.status_code} - {response.text}")


# 调用后端 API 接口，获取指定用户当前会话的状态数据
def get_agent_status(user_id: str, session_id: str):
    """
    获取智能体状态

    Args:
        user_id: 用户唯一标识
        session_id：会话唯一标识

    Returns:
        服务端返回的结果
    """
    # 发送 GET 请求获取会话状态
    response = requests.get(f"{API_BASE_URL}/agent/status/{user_id}/{session_id}")

    # 检查响应状态码
    if response.status_code == 200:
        # 获取成功，返回 JSON 响应数据
        return response.json()
    else:
        # 获取失败，抛出异常
        raise Exception(f"获取智能体状态失败: {response.status_code} - {response.text}")


# 调用后端 API 接口，获取指定用户当前最近一次更新的会话 ID
def get_user_active_sessionid(user_id: str):
    """
    获取系统信息

    Args:
        user_id: 用户唯一标识

    Returns:
        服务端返回的结果
    """
    # 发送 GET 请求获取用户的活跃会话 ID
    response = requests.get(f"{API_BASE_URL}/agent/active/sessionid/{user_id}")

    # 检查响应状态码
    if response.status_code == 200:
        # 获取成功，返回 JSON 响应数据
        return response.json()
    else:
        # 获取失败，抛出异常
        raise Exception(f"获取系统信息失败: {response.status_code} - {response.text}")


# 调用后端 API 接口，获取指定用户的所有会话 ID
def get_user_sessionids(user_id: str):
    """
    获取系统信息

    Args:
        user_id: 用户唯一标识

    Returns:
        服务端返回的结果
    """
    # 发送 GET 请求获取用户的所有会话 ID
    response = requests.get(f"{API_BASE_URL}/agent/sessionids/{user_id}")

    # 检查响应状态码
    if response.status_code == 200:
        # 获取成功，返回 JSON 响应数据
        return response.json()
    else:
        # 获取失败，抛出异常
        raise Exception(f"获取系统信息失败: {response.status_code} - {response.text}")


# 调用后端 API 接口，获取系统内所有的会话状态信息
def get_system_info():
    """
    获取系统信息

    Args:

    Returns:
        服务端返回的结果
    """
    # 发送 GET 请求获取系统信息
    response = requests.get(f"{API_BASE_URL}/system/info")

    # 检查响应状态码
    if response.status_code == 200:
        # 获取成功，返回 JSON 响应数据
        return response.json()
    else:
        # 获取失败，抛出异常
        raise Exception(f"获取系统信息失败: {response.status_code} - {response.text}")


# 调用后端 API 接口，删除指定用户的特定会话
def delete_agent_session(user_id: str, session_id: str):
    """
    删除用户会话

    Args:
        user_id: 用户唯一标识

    Returns:
        服务端返回的结果
    """
    # 发送 DELETE 请求删除指定会话
    response = requests.delete(f"{API_BASE_URL}/agent/session/{user_id}/{session_id}")

    # 检查响应状态码
    if response.status_code == 200:
        # 删除成功，返回 JSON 响应数据
        return response.json()
    elif response.status_code == 404:
        # 会话不存在，也视为成功（幂等性）
        return {"status": "success", "message": f"用户 {user_id}:{session_id} 的会话不存在"}
    else:
        # 删除失败，抛出异常
        raise Exception(f"删除会话失败: {response.status_code} - {response.text}")


# 在终端中显示会话的详细信息
def display_session_info(status_response):
    """
    显示会话的详细信息，包括会话状态、上次查询、响应数据等

    参数:
        status_response: 会话状态响应数据
    """
    # 从响应中提取基本会话信息
    # 基本会话信息面板
    user_id = status_response["user_id"]
    session_id = status_response.get("session_id", "未知")
    status = status_response["status"]
    last_query = status_response.get("last_query", "无")
    last_updated = status_response.get("last_updated")

    # 构建面板要显示的内容列表
    panel_content = [
        f"用户ID: {user_id}",
        f"会话ID: {session_id}",
        f"状态: [bold]{status}[/bold]",
        f"上次查询: {last_query}"
    ]

    # 如果有最后更新时间，格式化并添加到内容中
    if last_updated:
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last_updated))
        panel_content.append(f"上次更新: {time_str}")

    # 根据会话状态设置不同的显示样式
    if status == "interrupted":
        # 中断状态：黄色边框
        border_style = "yellow"
        title = "[warning]中断会话[/warning]"
    elif status == "completed":
        # 完成状态：绿色边框
        border_style = "green"
        title = "[success]完成会话[/success]"
    elif status == "error":
        # 错误状态：红色边框
        border_style = "red"
        title = "[error]错误会话[/error]"
    elif status == "running":
        # 运行中状态：蓝色边框
        border_style = "blue"
        title = "[info]运行中会话[/info]"
    elif status == "idle":
        # 空闲状态：青色边框
        border_style = "cyan"
        title = "[info]空闲会话[/info]"
    else:
        # 未知状态：白色边框
        border_style = "white"
        title = "[info]未知状态会话[/info]"

    # 使用 Panel 组件显示基本会话信息
    console.print(Panel(
        "\n".join(panel_content),
        title=title,
        border_style=border_style
    ))

    # 根据会话状态显示额外的响应数据
    if status_response.get("last_response"):
        last_response = status_response["last_response"]

        # 如果是完成状态且有结果数据
        if status == "completed" and last_response.get("result"):
            result = last_response["result"]
            # 如果结果中包含消息列表
            if "messages" in result:
                # 获取最后一条消息（通常是 AI 的回复）
                final_message = result["messages"][-1]
                # 使用 Markdown 格式显示消息内容
                console.print(Panel(
                    Markdown(final_message["content"]),
                    title="[success]上次智能体回答[/success]",
                    border_style="green"
                ))

        # 如果是中断状态且有中断数据
        elif status == "interrupted" and last_response.get("interrupt_data"):
            interrupt_data = last_response["interrupt_data"]
            # 获取中断描述信息
            message = interrupt_data.get("description", "需要您的输入")
            # 显示中断消息
            console.print(Panel(
                message,
                title=f"[warning]中断消息[/warning]",
                border_style="yellow"
            ))

        # 如果是错误状态
        elif status == "error":
            # 获取错误消息
            error_msg = last_response.get("message", "未知错误")
            # 显示错误信息
            console.print(Panel(
                error_msg,
                title="[error]错误信息[/error]",
                border_style="red"
            ))


# 检查用户会话状态并尝试自动恢复
def check_and_restore_session(user_id: str, session_id: str):
    """
    检查用户会话状态并尝试恢复

    参数:
        user_id: 用户ID
        session_id: 会话ID

    返回:
        tuple: (是否有活跃会话, 会话状态响应)
    """
    try:
        # 调用 API 获取指定会话的状态
        status_response = get_agent_status(user_id, session_id)

        # 如果会话不存在
        if status_response["status"] == "not_found":
            console.print("[info]没有找到现有会话状态数据，基于当前会话开始继续查询…[/info]")
            # 返回无活跃会话
            return False, None

        # 显示找到的会话的基本信息
        console.print(Panel(
            f"用户ID: {user_id}\n"
            f"会话ID: {status_response.get('session_id', '未知')}\n"
            f"状态: [bold]{status_response['status']}[/bold]\n"
            f"上次查询: {status_response.get('last_query', '无')}\n"
            f"上次更新: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(status_response['last_updated'])) if status_response.get('last_updated') else '未知'}\n",
            title="[info]发现现有会话[/info]",
            border_style="cyan"
        ))

        # 调用函数显示会话详细信息
        display_session_info(status_response)

        # 根据会话的不同状态进行相应处理
        if status_response["status"] == "interrupted":
            # 中断状态：需要用户决策
            console.print(Panel(
                "会话处于中断状态，需要您的响应才能继续。\n"
                "系统将自动恢复上次的中断点，您需要提供决策。",
                title="[warning]会话已中断[/warning]",
                border_style="yellow"
            ))

            # 检查是否有中断数据
            if (status_response.get("last_response") and
                    status_response["last_response"].get("interrupt_data")):

                # 提取并显示中断相关信息
                interrupt_data = status_response["last_response"]["interrupt_data"]

                # 获取动作请求信息
                action_request = interrupt_data.get("action_request", "未知中断")
                tool = action_request.get("action", "未知工具")
                args = action_request.get("args", "未知参数")
                # 显示相关工具名称
                console.print(f"[info]相关工具: {tool}[/info]")
                # 显示工具参数
                console.print(f"[info]工具参数: {args}[/info]")

                # 提示将自动恢复中断处理
                console.print("[info]自动恢复中断处理...[/info]")
                # 返回有活跃会话，需要处理中断
                return True, status_response
            else:
                # 中断数据不完整，无法恢复
                console.print("[warning]中断状态会话缺少必要的中断数据，无法恢复[/warning]")
                console.print("[info]将创建新会话[/info]")
                return False, None

        elif status_response["status"] == "completed":
            # 完成状态：显示上次结果并准备开始新会话
            console.print(Panel(
                "会话已完成，上次响应结果可用。\n"
                "系统将显示上次结果并自动开启新会话。",
                title="[success]会话已完成[/success]",
                border_style="green"
            ))

            # 如果有上次的结果数据
            if (status_response.get("last_response") and
                    status_response["last_response"].get("result")):

                # 提取结果数据
                last_result = status_response["last_response"]["result"]
                # 如果结果中包含消息列表
                if "messages" in last_result:
                    # 获取最后一条消息
                    final_message = last_result["messages"][-1]

                    # 使用 Markdown 格式显示智能体的回答
                    console.print(Panel(
                        Markdown(final_message["content"]),
                        title="[success]上次智能体回答[/success]",
                        border_style="green"
                    ))

            # 提示将基于当前会话继续
            console.print("[info]基于当前会话开始继续...[/info]")
            return False, None

        elif status_response["status"] == "error":
            # 错误状态：显示错误信息并开始新会话
            error_msg = "未知错误"
            if status_response.get("last_response"):
                error_msg = status_response["last_response"].get("message", "未知错误")

            # 显示错误信息面板
            console.print(Panel(
                f"上次会话发生错误: {error_msg}\n"
                "系统将自动开始新会话。",
                title="[error]会话错误[/error]",
                border_style="red"
            ))

            # 提示将开始新会话
            console.print("[info]自动开始新会话...[/info]")
            return False, None

        elif status_response["status"] == "running":
            # 运行中状态：等待会话完成或超时
            console.print(Panel(
                "会话正在运行中，这可能是因为:\n"
                "1. 另一个客户端正在使用此会话\n"
                "2. 上一次会话异常终止，状态未更新\n"
                "系统将自动等待会话状态变化。",
                title="[warning]会话运行中[/warning]",
                border_style="yellow"
            ))

            # 提示将等待会话状态变化
            console.print("[info]自动等待会话状态变化...[/info]")
            # 使用进度条显示等待过程
            with Progress() as progress:
                # 添加等待任务
                task = progress.add_task("[cyan]等待会话完成...", total=None)
                # 设置最大等待时间（30 秒）
                max_attempts = 30  # 最多等待30秒
                attempt_count = 0

                # 循环检查会话状态
                for i in range(max_attempts):
                    attempt_count = i
                    # 获取当前会话状态
                    # 检查状态
                    current_status = get_agent_status(user_id, session_id)
                    # 如果状态不再是运行中
                    if current_status["status"] != "running":
                        # 标记任务完成
                        progress.update(task, completed=100)
                        # 显示状态更新提示
                        console.print(f"[success]会话状态已更新为: {current_status['status']}[/success]")
                        break
                    # 等待 1 秒后再次检查
                    time.sleep(1)

                # 如果超过最大等待时间
                if attempt_count >= max_attempts - 1:
                    console.print("[warning]等待超时，会话可能仍在运行[/warning]")
                    console.print("[info]为避免冲突，将创建新会话[/info]")
                    return False, None

                # 递归调用以获取最新状态
                return check_and_restore_session(user_id, session_id)

        elif status_response["status"] == "idle":
            # 空闲状态：可以直接使用现有会话
            console.print(Panel(
                "会话处于空闲状态，准备接收新查询。\n"
                "系统将自动使用现有会话。",
                title="[info]会话空闲[/info]",
                border_style="blue"
            ))

            # 提示将使用现有会话
            console.print("[info]自动使用现有会话[/info]")
            return True, status_response

        else:
            # 未知状态：为安全起见，创建新会话
            console.print(Panel(
                f"会话处于未知状态: {status_response['status']}\n"
                "系统将自动创建新会话以避免潜在问题。",
                title="[warning]未知状态[/warning]",
                border_style="yellow"
            ))

            # 提示将创建新会话
            console.print("[info]自动创建新会话...[/info]")
            return False, None

    except Exception as e:
        # 捕获异常并显示错误信息
        console.print(f"[error]检查会话状态时出错: {str(e)}[/error]")
        # 打印详细的错误堆栈信息
        console.print(traceback.format_exc())
        # 提示将创建新会话
        console.print("[info]将创建新会话[/info]")
        return False, None


# 处理工具调用审批类型的人工中断
def handle_tool_interrupt(interrupt_data, user_id, session_id):
    """
    处理工具使用审批类型的中断

    参数:
        interrupt_data: 中断数据
        user_id: 用户ID
        session_id: 会话ID

    返回:
        处理后的响应
    """
    # 获取中断描述信息
    message = interrupt_data.get("description", "需要您的输入")

    # 在面板中显示工具审批提示
    console.print(Panel(
        f"{message}",
        title=f"[warning]智能体需要您的决定[/warning]",
        border_style="yellow"
    ))

    # 获取用户的决策输入
    user_input = Prompt.ask("[highlight]您的选择[/highlight]")

    # 处理用户的决策
    try:
        # 循环直到获取有效输入
        while True:
            if user_input.lower() == "yes":
                # 用户同意，发送接受响应
                response = resume_agent(user_id, session_id, "accept")
                break
            elif user_input.lower() == "no":
                # 用户拒绝，发送拒绝响应
                response = resume_agent(user_id, session_id, "reject")
                break
            elif user_input.lower() == "edit":
                # 用户选择编辑参数
                new_query = Prompt.ask("[highlight]请调整新的参数[/highlight]")
                # 发送编辑响应，包含新参数
                response = resume_agent(user_id, session_id, "edit", args={"args": json.loads(new_query)})
                break
            elif user_input.lower() == "response":
                # 用户选择直接反馈
                new_query = Prompt.ask("[highlight]不调用工具直接反馈信息[/highlight]")
                # 发送响应类型，包含反馈内容
                response = resume_agent(user_id, session_id, "response", args={"args": new_query})
                break
            else:
                # 无效输入，提示重新输入
                console.print("[error]无效输入，请输入 'yes'、'no' 、'edit' 或 'response'[/error]")
                user_input = Prompt.ask("[highlight]您的选择[/highlight]")

        # 递归处理智能体的响应（可能再次中断）
        return process_agent_response(response, user_id)

    except Exception as e:
        # 处理过程中出错
        console.print(f"[error]处理响应时出错: {str(e)}[/error]")
        return None


# 处理智能体返回的各种响应状态，包括处理中断和显示结果
def process_agent_response(response, user_id):
    # 检查响应是否为空，防止空指针错误
    if not response:
        console.print("[error]收到空响应，无法处理[/error]")
        return None

    try:
        # 从响应中提取关键字段
        session_id = response["session_id"]
        status = response["status"]
        timestamp = response.get("timestamp", time.time())

        # 格式化并显示响应时间和会话 ID
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
        console.print(f"[info]响应时间: {time_str} | 会话ID: {session_id}[/info]")

        # 根据不同的状态进行相应处理
        if status == "interrupted":
            # 中断状态：需要人工干预
            interrupt_data = response.get("interrupt_data", {})

            try:
                # 调用中断处理函数
                return handle_tool_interrupt(interrupt_data, user_id, session_id)

            except Exception as e:
                # 中断处理失败
                console.print(f"[error]处理中断响应时出错: {str(e)}[/error]")
                console.print(f"[info]中断状态已保存，您可以稍后恢复会话[/info]")
                # 打印详细错误信息
                console.print(traceback.format_exc())
                return None

        elif status == "completed":
            # 完成状态：显示最终结果
            result = response.get("result", {})
            # 检查结果中是否有消息列表
            if result and "messages" in result:
                # 获取最后一条消息（通常是 AI 的最终回答）
                final_message = result["messages"][-1]
                # 使用 Markdown 格式显示回答内容
                console.print(Panel(
                    Markdown(final_message["content"]),
                    title="[success]智能体回答[/success]",
                    border_style="green"
                ))
            else:
                # 结果格式异常
                console.print("[warning]智能体没有返回有效的消息[/warning]")
                # 如果结果是字典，显示原始数据
                if isinstance(result, dict):
                    console.print("[info]原始结果数据结构:[/info]")
                    console.print(result)

            return result

        elif status == "error":
            # 错误状态：显示错误信息
            error_msg = response.get("message", "未知错误")
            console.print(Panel(
                f"{error_msg}",
                title="[error]处理过程中出错[/error]",
                border_style="red"
            ))
            return None

        elif status == "running":
            # 运行中状态：提示正在处理
            console.print("[info]智能体正在处理您的请求，请稍候...[/info]")
            return response

        elif status == "idle":
            # 空闲状态：提示准备接收新请求
            console.print("[info]智能体处于空闲状态，准备接收新的请求[/info]")
            return response

        else:
            # 未知状态
            console.print(f"[warning]智能体处于未知状态: {status} - {response.get('message', '无消息')}[/warning]")
            return response

    except KeyError as e:
        # 响应格式错误，缺少必要字段
        console.print(f"[error]响应格式错误，缺少关键字段 {e}[/error]")
        return None
    except Exception as e:
        # 其他未预期的错误
        console.print(f"[error]处理智能体响应时出现未预期错误: {str(e)}[/error]")
        # 打印详细错误堆栈
        console.print(traceback.format_exc())
        return None


# 客户端主函数，运行交互式对话循环
def main():
    # 显示欢迎面板
    console.print(Panel(
        "前端客户端模拟服务(@南哥AGI研习社)",
        title="[heading]ReAct Agent 智能体交互演示系统[/heading]",
        border_style="magenta"
    ))

    try:
        # 获取并显示系统信息
        system_info = get_system_info()
        console.print(f"[info]当前系统内全部会话总计: {system_info['sessions_count']}[/info]")
        # 如果有活跃用户，显示用户及会话信息
        if system_info['active_users']:
            console.print(f"[info]系统内全部用户及用户会话: {system_info['active_users']}[/info]")
    except Exception:
        # 获取系统信息失败，但不影响使用
        console.print("[warning]无法获取当前系统内会话状态信息，但这不影响使用[/warning]")

    # 获取用户 ID（可以输入已有 ID 或创建新 ID）
    default_user_id = f"user_{int(time.time())}"
    user_id = Prompt.ask("[info]请输入用户ID[/info] (新ID将创建新用户，已有ID将恢复使用该用户)", default=default_user_id)

    try:
        # 尝试获取该用户最近活跃的会话 ID
        active_session_id = get_user_active_sessionid(user_id)
        # 如果存在活跃会话，直接使用
        if active_session_id["active_session_id"]:
            session_id = active_session_id["active_session_id"]
        # 否则创建新会话
        else:
            # 生成新的 UUID 作为会话 ID
            session_id = str(uuid.uuid4())
            console.print(f"[info]将为你开启一个新会话，会话ID为 {session_id} [/info]")
    except Exception:
        # 获取活跃会话失败，但不影响使用
        console.print("[warning]无法获取指定用户当前最近一次更新的会话ID，但这不影响使用[/warning]")

    # 检查并尝试恢复现有会话
    has_active_session, session_status = check_and_restore_session(user_id, session_id)

    # 进入主交互循环
    while True:
        try:
            # 如果有活跃会话需要处理
            if has_active_session and session_status:
                # 如果是中断状态，自动处理
                if session_status["status"] == "interrupted":
                    console.print("[info]自动处理中断的会话...[/info]")
                    # 检查是否有上次的响应数据
                    if "last_response" in session_status and session_status["last_response"]:
                        # 调用响应处理函数处理之前的中断
                        result = process_agent_response(session_status["last_response"], user_id)
                        # 重新获取当前会话状态
                        current_status = get_agent_status(user_id, session_id)
                        # 如果处理中断后会话已完成
                        if current_status["status"] == "completed":
                            # 显示完成提示
                            console.print("[success]本次查询已完成[/success]")
                            # 提示将开始新查询
                            console.print("[info]自动开始新的查询...[/info]")
                            # 重置会话状态标志
                            has_active_session = False
                            session_status = None
                        else:
                            # 会话仍在活跃状态
                            has_active_session = True
                            session_status = current_status

            # 获取用户输入的查询或命令
            query = Prompt.ask(
                "\n[info]请输入您的问题[/info] (输入 'exit' 退出，输入 'status' 查询状态，输入 'new' 开始新会话，输入 'history' 恢复历史会话，输入 'setting' 偏好设置)",
                default="你好")

            # 处理退出命令
            if query.lower() == 'exit':
                console.print("[info]感谢使用，再见！[/info]")
                break

            # 处理状态查询命令
            elif query.lower() == 'status':
                # 调用 API 获取会话状态
                status_response = get_agent_status(user_id, session_id)
                # 显示状态信息面板
                console.print(Panel(
                    f"用户ID: {status_response['user_id']}\n"
                    f"会话ID: {status_response.get('session_id', '未知')}\n"
                    f"会话状态: {status_response['status']}\n"
                    f"上次查询: {status_response['last_query'] or '无'}\n"
                    f"上次更新: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(status_response['last_updated'])) if status_response.get('last_updated') else '未知'}\n",
                    title="[info]当前会话状态[/info]",
                    border_style="cyan"
                ))
                continue

            # 处理创建新会话命令
            elif query.lower() == 'new':
                # 生成新的会话 ID
                session_id = str(uuid.uuid4())
                # 重置会话状态
                has_active_session = False
                session_status = None
                console.print(f"[info]将为你开启一个新会话，会话ID为 {session_id}[/info]")
                continue

            # 处理恢复历史会话命令
            elif query.lower() == 'history':
                try:
                    # 获取用户的所有会话 ID
                    session_ids = get_user_sessionids(user_id)
                    # 如果存在历史会话
                    if session_ids['session_ids']:
                        # 显示所有历史会话 ID
                        console.print(f"[info]当前用户{user_id}的历史会话: {session_ids['session_ids']}[/info]")
                        # 提示用户输入要恢复的会话 ID
                        session_id = Prompt.ask("[info]请输入历史会话ID[/info] (这里演示请输入历史会话ID自动恢复会话)")
                        # 重置会话状态
                        has_active_session = False
                        session_status = None
                        console.print(f"[info]将为你恢复选择的历史会话，会话ID为 {session_id}[/info]")
                        continue
                    # 如果没有历史会话，创建新会话
                    else:
                        session_id = str(uuid.uuid4())
                        has_active_session = False
                        session_status = None
                        console.print(f"[info]将为你开启一个新会话，会话ID为 {session_id}[/info]")
                        continue

                except Exception:
                    # 获取历史会话失败
                    console.print("[warning]无法获取指定用户的所有会话ID，但这不影响使用[/warning]")
                    has_active_session = False
                    session_status = None
                    continue

            # 处理偏好设置命令
            elif query.lower() == 'setting':
                try:
                    # 提示用户输入偏好设置内容
                    memory_info = Prompt.ask("[info]请输入需要存储到长期记忆中的偏好设置内容[/info]")
                    # 调用 API 写入长期记忆
                    response = write_long_term(user_id, memory_info)
                    # 写入完成后继续
                    console.print(f"[info]用户 {user_id} 写入数据完成，继续查询…[/info]")
                    has_active_session = False
                    session_status = None
                    continue
                except Exception:
                    # 写入长期记忆失败
                    console.print("[warning]无法写入长期记忆，但这不影响使用[/warning]")
                    has_active_session = False
                    session_status = None
                    continue

            # 处理正常的用户查询
            console.print("[info]正在提交查询，请求运行智能体...[/info]")
            # 调用 API 运行智能体
            response = invoke_agent(user_id, session_id, query)

            # 处理智能体的响应
            result = process_agent_response(response, user_id)

            # 重新获取会话的最新状态
            latest_status = get_agent_status(user_id, session_id)

            # 根据最新状态决定下一步操作
            if latest_status["status"] == "completed":
                # 已完成：准备接收新查询
                console.print("[info]本次查询已完成，准备接收新的查询[/info]")
                has_active_session = False
                session_status = None
            elif latest_status["status"] == "error":
                # 出错：开始新查询
                console.print("[info]查询发生错误，将开始新的查询[/info]")
                has_active_session = False
                session_status = None
            else:
                # 其他状态（idle、interrupted）：保持会话活跃
                has_active_session = True
                session_status = latest_status

        except KeyboardInterrupt:
            # 用户按 Ctrl+C 中断
            console.print("\n[warning]用户中断，正在退出...[/warning]")
            console.print("[info]会话状态已保存，可以在下次使用相同用户ID恢复[/info]")
            break
        except Exception as e:
            # 捕获运行过程中的其他异常
            console.print(f"[error]运行过程中出错: {str(e)}[/error]")
            # 打印详细错误堆栈
            console.print(traceback.format_exc())
            # 尝试恢复或创建新会话
            has_active_session, session_status = check_and_restore_session(user_id, session_id)
            continue


# 当脚本作为主程序运行时执行 main 函数
if __name__ == "__main__":
    main()
