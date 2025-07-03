# backend/server.py (V6 - 支持文件读写与多窗口版)

import asyncio
import websockets
import subprocess
import os
import json
import re

# --- 1. 路径设定与初始化 ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXECUTOR_PATH = os.path.join(SCRIPT_DIR, "executor")
DESKTOP_PATH = os.path.join(SCRIPT_DIR, "desktop")

try:
    print(f"设定工作目录为: {DESKTOP_PATH}")
    os.makedirs(DESKTOP_PATH, exist_ok=True)
    os.chdir(DESKTOP_PATH)
    print(f"工作目录已成功设置为: {os.getcwd()}")
except OSError as e:
    print(f"错误：无法创建或进入桌面目录 {DESKTOP_PATH}: {e}")
    pass

# --- 2. 初始化全局状态 ---
COMMAND_HISTORY = []

# --- 3. 辅助函数 ---
def parse_ls_output(output):
    """解析ls -l的输出，提取文件名和类型"""
    items = []
    lines = output.strip().split('\n')
    if not lines or "总计" in lines[0]:
        lines = lines[1:]
    
    for line in lines:
        parts = re.split(r'\s+', line)
        if len(parts) < 9:
            continue
        
        item_type = 'directory' if parts[0].startswith('d') else 'file'
        
        # 处理文件名中可能包含空格的情况
        file_name_start_index = 8
        file_name = " ".join(parts[file_name_start_index:])

        items.append({'name': file_name, 'type': item_type})
    return items

# --- 4. 核心消息处理器 ---
async def handle_message(data):
    """根据action分发任务"""
    action = data.get("action")
    payload = data.get("payload")
    response = {"currentDirectory": os.getcwd()}

    if action == "runCommand":
        command_str = payload
        command_parts = command_str.split()
        
        if not command_parts:
            response["commandOutput"] = ""
        else:
            command = command_parts[0]
            # 内建命令处理
            if command == "cd":
                if len(command_parts) < 2:
                    response["commandOutput"] = "用法: cd <目录>"
                else:
                    try:
                        os.chdir(command_parts[1])
                        response["event"] = "fileSystemChanged"
                    except FileNotFoundError:
                        response["commandOutput"] = f"错误: 目录 '{command_parts[1]}' 不存在"
                    except Exception as e:
                        response["commandOutput"] = f"更改目录时发生错误: {e}"
            elif command == "history":
                history_str = "命令历史:\n"
                for i, cmd in enumerate(COMMAND_HISTORY, 1):
                    history_str += f"  {i}\t{cmd}\n"
                response["commandOutput"] = history_str.strip()
            # 外部命令处理
            else:
                full_command = [EXECUTOR_PATH] + command_parts
                result = subprocess.run(full_command, capture_output=True, text=True, cwd=os.getcwd())
                
                if result.stderr:
                    response["commandOutput"] = result.stderr
                else:
                    response["commandOutput"] = result.stdout
                
                modifying_commands = ['mkdir', 'rm', 'touch', 'mv', 'cp', 'rmdir', 'gcc']
                if command in modifying_commands:
                    response["event"] = "fileSystemChanged"
                
                if command == "ls":
                    response["directoryListing"] = parse_ls_output(result.stdout)
    
    elif action == "readFile":
        try:
            path = payload["path"]
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            response["fileContent"] = {"path": path, "content": content}
        except Exception as e:
            response["error"] = f"读取文件 '{path}' 失败: {e}"

    elif action == "writeFile":
        try:
            path = payload["path"]
            content = payload["content"]
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            response["fileWriteSuccess"] = {"path": path}
            response["event"] = "fileSystemChanged"
        except Exception as e:
            response["error"] = f"写入文件 '{path}' 失败: {e}"

    return response

# --- 5. WebSocket主处理器 ---
async def handler(websocket):
    print(f"一个客户端已连接: {websocket.remote_address}")
    # 连接时立即发送一次当前"桌面"的文件列表
    initial_response = await handle_message({"action": "runCommand", "payload": "ls -l"})
    await websocket.send(json.dumps(initial_response))

    try:
        async for raw_message in websocket:
            print(f"收到原始消息: {raw_message}")
            try:
                data = json.loads(raw_message)
                
                # 记录命令历史
                if data.get("action") == "runCommand" and data.get("payload", "").strip():
                    COMMAND_HISTORY.append(data.get("payload"))

                response_data = await handle_message(data)
                await websocket.send(json.dumps(response_data))
            except json.JSONDecodeError:
                await websocket.send(json.dumps({"error": "无效的JSON格式"}))
            except Exception as e:
                await websocket.send(json.dumps({"error": f"处理请求时发生错误: {e}"}))

    except websockets.exceptions.ConnectionClosedError:
        print("客户端已断开")

# --- 6. 服务器启动入口 ---
async def main():
    port = 8765
    async with websockets.serve(handler, "localhost", port):
        print(f"多功能服务器已启动，正在监听 ws://localhost:{port}")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())