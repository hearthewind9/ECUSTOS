
# ECUST OS Shell - 现代化Web图形化Shell界面

这是一个基于Web技术的、高度仿真的图形化操作系统Shell界面。本项目旨在作为一份操作系统课程设计，它创造性地将经典的命令行Shell功能与现代化的Web用户界面相结合。

用户可以在一个仿真的桌面环境中，通过可拖拽的窗口来使用终端和文本编辑器，执行真实的Linux命令，甚至完成C语言代码的在线编译与运行，这一切都运行在浏览器中。

## ✨ 主要功能

  * **图形化桌面**: 实现了包含动态图标和自定义背景的桌面环境。
  * **多窗口系统**: 支持可随意拖拽的终端和文本编辑器窗口，并且可以同时打开多个。
  * **功能完备的终端**:
      * 通过C语言核心执行器，支持所有标准的Linux外部命令（如 `ls`, `pwd`, `grep`, `gcc` 等）。
      * 实现了由父进程处理的内建命令，如 `cd` 和 `history`。
      * 支持**管道 (`|`)** 和**输出重定向 (`>`)** 等高级Shell功能。
  * **实时文件系统同步**: 在终端中创建、删除或修改文件/目录（如`mkdir`, `touch`, `rm`），桌面图标会立刻自动刷新。
  * **交互式文件操作**:
      * 支持**双击**桌面图标打开文件或目录。
      * 双击文本文件（`.c`, `.py`, `.txt`等）会启动一个带**行号**和**C语言语法高亮**的文本编辑器。
      * 支持在编辑器中修改内容并**保存**回文件系统。
  * **桌面右键菜单**: 支持右键点击桌面空白处，快捷执行“打开终端”等操作。

## 🛠️ 技术栈

  * **前端 (表示层)**: React, Vite, WebSocket API, `@uiw/react-textarea-code-editor`
  * **后端 (编排层)**: Python 3, `websockets` 库
  * **执行器 (核心层)**: C 语言 (使用 `fork`, `execvp`, `pipe`, `dup2` 等POSIX API)
  * **构建工具**: `npm`, `gcc`

## 🚀 在新设备上运行项目

本项目支持跨平台运行。以下是在一个全新的、未配置过环境的设备上运行本项目的步骤。

### (一) 环境预设

在开始之前，请根据您的操作系统，安装以下必需的软件。

#### **通用**

  * **Git**: 用于从GitHub克隆本项目。 [Git官网](https://git-scm.com/downloads)

#### **Windows系统**

1.  **Node.js (含 npm)**: 从 [Node.js官网](https://nodejs.org/) 下载并安装LTS版本。
2.  **Python**: 从 [Python官网](https://www.python.org/downloads/) 下载并安装最新版的Python 3。**重要**：在安装时，请务必勾选 `Add Python to PATH` 选项。
3.  **C语言编译器 (GCC)**:
      * **强烈推荐**: 安装 **WSL (Windows Subsystem for Linux)**。这会为您提供一个完整的Linux环境，使得编译和运行体验与Linux/macOS完全一致。请参考 [微软官方WSL安装指南](https://learn.microsoft.com/zh-cn/windows/wsl/install)。
      * **备选方案**: 安装 [MinGW-w64](https://www.mingw-w64.org/) 来获取`gcc`编译器。

#### **macOS系统**

1.  **Node.js (含 npm)**: 从 [Node.js官网](https://nodejs.org/) 下载并安装LTS版本，或使用 [Homebrew](https://brew.sh) (`brew install node`) 安装。
2.  **Python**: macOS通常自带Python 3。
3.  **C语言编译器 (GCC/Clang)**: 打开终端，运行 `xcode-select --install` 来安装苹果的命令行开发者工具，其中已包含`clang`编译器（可作为`gcc`使用）。

#### **Linux系统 (Debian/Ubuntu)**

1.  **Node.js (含 npm)**: 推荐使用`nvm`进行安装，请参考我们之前的对话记录。
2.  **Python 和 C编译器**: 打开终端，运行以下命令安装所有必需品。
    ```bash
    sudo apt update
    sudo apt install python3 python3-pip python3-venv git build-essential
    ```

### (二) 安装与启动

当以上预设环境准备好后，请按照以下步骤启动项目。

**1. 克隆项目**

```bash
git clone https://github.com/hearthewind9/ECUSTOS.git
cd ECUSTOS
```

*(请将上面的URL替换为您自己仓库的地址)*

**2. 配置并启动后端**

```bash
# 进入后端目录
cd backend

# 创建Python虚拟环境
python3 -m venv venv

# 激活虚拟环境
# (在 Linux/macOS 上)
source venv/bin/activate
# (在 Windows 的 CMD 中，使用 venv\Scripts\activate)

# 安装Python依赖库
pip install websockets

# 编译C语言执行器
gcc -o executor executor.c

# 启动后端服务器
python3 server.py
```

*此时，您的后端已经成功运行。请不要关闭这个终端窗口。*

**3. 配置并启动前端**
*打开**第二个新终端**，执行以下命令：*

```bash
# 进入前端目录
cd frontend

# 安装Node.js依赖
npm install

# 启动前端开发服务器
npm run dev
```

**4. 访问项目**

前端服务器启动后，会显示一个本地网址（通常是 `http://localhost:5173`）。在您的浏览器中打开这个地址，即可开始使用您的可视化操作系统！
