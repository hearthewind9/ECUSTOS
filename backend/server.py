import asyncio
import websockets
import subprocess
import os
import json
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXECUTOR_PATH = os.path.join(SCRIPT_DIR, "executor")
DESKTOP_PATH = os.path.join(SCRIPT_DIR, "desktop")
try:
    os.makedirs(DESKTOP_PATH, exist_ok=True)
    os.chdir(DESKTOP_PATH)
except OSError as e:
    print(f"错误：无法创建或进入桌面目录 {DESKTOP_PATH}: {e}")

COMMAND_HISTORY = []
ALIASES = {}

def parse_ls_output(output):
    items = []
    lines = output.strip().split('\n')
    if not lines or "总计" in lines[0]:
        lines = lines[1:]
    
    for line in lines:
        parts = re.split(r'\s+', line)
        if len(parts) < 9:
            continue
        
        permissions = parts[0]
        item_type = 'directory' if permissions.startswith('d') else 'file'
        is_executable = 'x' in permissions
        file_name = " ".join(parts[8:])
        items.append({'name': file_name, 'type': item_type, 'executable': is_executable})
    return items

def expand_variables(command_str):
    expanded_str = re.sub(r'\$(\w+)', lambda m: os.environ.get(m.group(1), ''), command_str)
    expanded_str = re.sub(r'\$\{(\w+)\}', lambda m: os.environ.get(m.group(1), ''), expanded_str)
    return expanded_str

async def handle_message(data):
    action = data.get("action")
    payload = data.get("payload", "")
    response = {"currentDirectory": os.getcwd()}

    if action == "runCommand":
        command_str = payload.strip()
        response["commandToLog"] = command_str
        
        if not command_str:
            response["commandOutput"] = ""
            return response

        if command_str == '!!':
            if len(COMMAND_HISTORY) > 0:
                command_str = COMMAND_HISTORY[-1]
            else:
                response["commandOutput"] = "history: no events found"
                return response
        elif command_str.startswith('!'):
            try:
                index = int(command_str[1:])
                if 1 <= index <= len(COMMAND_HISTORY):
                    command_str = COMMAND_HISTORY[index - 1]
                else:
                    response["commandOutput"] = f"history: event not found: {index}"
                    return response
            except (ValueError, IndexError):
                pass
        
        if command_str != "history" and (not COMMAND_HISTORY or COMMAND_HISTORY[-1] != command_str):
             COMMAND_HISTORY.append(command_str)

        command_str = expand_variables(command_str)
        
        command_parts_for_alias_check = command_str.strip().split()
        if command_parts_for_alias_check and command_parts_for_alias_check[0] in ALIASES:
            alias_name = command_parts_for_alias_check[0]
            replacement = ALIASES[alias_name]
            remaining_args = " ".join(command_parts_for_alias_check[1:])
            command_str = f"{replacement} {remaining_args}".strip()

        command_parts = command_str.split()
        command = command_parts[0]

        if command == "cd":
            if len(command_parts) < 2:
                response["commandOutput"] = "用法: cd <目录>"
            else:
                try:
                    target_dir = os.path.expanduser(command_parts[1])
                    os.chdir(target_dir)
                    response["event"] = "fileSystemChanged"
                except FileNotFoundError:
                    response["commandOutput"] = f"错误: 目录 '{command_parts[1]}' 不存在"
                except Exception as e:
                    response["commandOutput"] = f"更改目录时发生错误: {e}"
        elif command == "history":
            try:
                num_to_show = len(COMMAND_HISTORY)
                if len(command_parts) > 1:
                    num_to_show = int(command_parts[1])
                
                history_list = COMMAND_HISTORY[-num_to_show:]
                start_index = len(COMMAND_HISTORY) - len(history_list) + 1
                history_str = "\n".join([f"  {i}\t{cmd}" for i, cmd in enumerate(history_list, start=start_index)])
                response["commandOutput"] = history_str
            except ValueError:
                response["commandOutput"] = f"history: 无效的数字: {command_parts[1]}"
        elif command == "alias":
            if len(command_parts) == 1:
                alias_list = [f"alias {name}='{value}'" for name, value in ALIASES.items()]
                response["commandOutput"] = "\n".join(alias_list)
            else:
                alias_def = " ".join(command_parts[1:])
                if '=' in alias_def:
                    name, value = alias_def.split('=', 1)
                    if value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    ALIASES[name] = value
                else:
                     response["commandOutput"] = "alias: 用法: alias name='command'"
        elif command == "unalias":
            if len(command_parts) < 2:
                response["commandOutput"] = "用法: unalias <别名>"
            else:
                alias_name_to_remove = command_parts[1]
                if alias_name_to_remove in ALIASES:
                    del ALIASES[alias_name_to_remove]
                else:
                    response["commandOutput"] = f"unalias: 未找到别名 {alias_name_to_remove}"
        else:
            full_command = [EXECUTOR_PATH] + command_parts
            result = subprocess.run(full_command, capture_output=True, text=True, cwd=os.getcwd())
            response["commandOutput"] = result.stderr or result.stdout
            
            modifying_commands = ['mkdir', 'rm', 'touch', 'mv', 'cp', 'rmdir', 'gcc']
            if command in modifying_commands:
                response["event"] = "fileSystemChanged"
            
            if command == "ls":
                response["directoryListing"] = parse_ls_output(result.stdout)
    
    elif action == "readFile":
        try:
            path = os.path.expanduser(payload["path"])
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            response["fileContent"] = {"path": payload["path"], "content": content}
        except Exception as e:
            response["error"] = f"读取文件 '{payload['path']}' 失败: {e}"

    elif action == "writeFile":
        try:
            path = os.path.expanduser(payload["path"])
            content = payload["content"]
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            response["fileWriteSuccess"] = {"path": payload["path"]}
            response["event"] = "fileSystemChanged"
        except Exception as e:
            response["error"] = f"写入文件 '{payload['path']}' 失败: {e}"
    
    elif action == "autoComplete":
        line = payload
        parts = line.split()
        to_complete = ""
        if not line.endswith(' '):
            to_complete = parts[-1] if parts else ''
        
        path_prefix = line[:-len(to_complete)] if to_complete else line
        
        completions = []
        try:
            for f in os.listdir('.'):
                if f.startswith(to_complete):
                    if os.path.isdir(os.path.join('.', f)):
                        completions.append(f + "/")
                    else:
                        completions.append(f)
        except OSError:
            pass
        
        if len(completions) == 1:
            response['autoCompleted'] = path_prefix + completions[0]
        elif len(completions) > 1:
            response['commandOutput'] = "\n" + "  ".join(completions)

    response["currentDirectory"] = os.getcwd()
    return response

async def handler(websocket):
    print(f"一个客户端已连接: {websocket.remote_address}")
    initial_response = await handle_message({"action": "runCommand", "payload": "ls -l"})
    await websocket.send(json.dumps(initial_response))
    try:
        async for raw_message in websocket:
            try:
                data = json.loads(raw_message)
                response_data = await handle_message(data)
                await websocket.send(json.dumps(response_data))
            except Exception as e:
                print(f"处理消息时发生严重错误: {e}")
                await websocket.send(json.dumps({"error": f"服务器内部错误: {e}"}))
    except websockets.exceptions.ConnectionClosedError:
        print("客户端已断开")

async def main():
    port = 8765
    async with websockets.serve(handler, "localhost", port):
        print(f"功能完整的服务器已启动，正在监听 ws://localhost:{port}")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())