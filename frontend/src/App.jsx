import React, { useState, useEffect, useRef } from 'react';
import './Desktop.css';
import Icon from './Icon.jsx';
import Terminal from './Terminal.jsx';
import TextEditor from './TextEditor.jsx';

function App() {
  const [windows, setWindows] = useState([]);
  const [desktopItems, setDesktopItems] = useState([]);
  const [currentPath, setCurrentPath] = useState('~');
  const [contextMenu, setContextMenu] = useState({ visible: false, x: 0, y: 0 });
  const [terminalInputValue, setTerminalInputValue] = useState(""); // 提升的状态
  const ws = useRef(null);
  const windowCounter = useRef(0);

  useEffect(() => {
    ws.current = new WebSocket('ws://localhost:8765');
    ws.current.onopen = () => openNewTerminal();
    ws.current.onclose = () => {
        setWindows(prev => prev.map(w => w.type === 'terminal' ? { ...w, log: [...w.log, '// WebSocket 连接断开.'] } : w));
    };
    
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log("收到数据:", data);

      if (data.currentDirectory) setCurrentPath(data.currentDirectory);
      
      if (data.commandOutput !== undefined) {
          const newLogEntry = data.commandOutput || '';
          // 在发送命令之前，先把命令本身加入日志
          const lastCommand = data.commandToLog || '';
          const fullLog = (lastCommand ? [`$ ${lastCommand}`, newLogEntry] : [newLogEntry]).filter(Boolean);
          setWindows(prev => prev.map(w => w.type === 'terminal' ? { ...w, log: [...w.log, ...fullLog] } : w));
      }
      
      if (data.autoCompleted) {
          setTerminalInputValue(data.autoCompleted);
      }
      
      if (data.fileContent) {
          const newEditor = { id: `editor-${windowCounter.current++}`, type: 'editor', filePath: data.fileContent.path, initialContent: data.fileContent.content };
          setWindows(prev => [...prev, newEditor]);
      }

      if(data.fileWriteSuccess) {
          alert(`文件 ${data.fileWriteSuccess.path} 已成功保存!`);
      }

      if (data.directoryListing) setDesktopItems(data.directoryListing);
      
      if (data.event === 'fileSystemChanged') {
        ws.current.send(JSON.stringify({ action: 'runCommand', payload: 'ls -l' }));
      }
    };

    return () => ws.current?.close();
  }, []);
  
  const handleIconDoubleClick = (item) => {
    if (item.type === 'directory') {
      ws.current.send(JSON.stringify({ action: 'runCommand', payload: `cd ${item.name}` }));
    } else {
      ws.current.send(JSON.stringify({ action: 'readFile', payload: { path: item.name } }));
    }
  };

  const handleSaveFile = (path, content) => {
    ws.current.send(JSON.stringify({ action: 'writeFile', payload: { path, content } }));
  };

  const closeWindow = (id) => {
    setWindows(prev => prev.filter(w => w.id !== id));
  };

  const handleContextMenu = (e) => {
    if (e.target.classList.contains('desktop')) {
      e.preventDefault();
      setContextMenu({ visible: true, x: e.pageX, y: e.pageY });
    } else {
      closeContextMenu();
    }
  };

  const closeContextMenu = () => {
    if (contextMenu.visible) setContextMenu({ ...contextMenu, visible: false });
  };
  
  const openNewTerminal = () => {
    if (windows.some(w => w.type === 'terminal')) return; // 简单处理，只允许一个终端
    const newTerminal = { id: `terminal-${windowCounter.current++}`, type: 'terminal', log: ['// WebSocket 连接成功!'], path: currentPath };
    setWindows(prev => [...prev, newTerminal]);
    closeContextMenu();
  };

  return (
    <div className="desktop" onContextMenu={handleContextMenu} onClick={closeContextMenu}>
      <div style={{ display: 'flex', flexWrap: 'wrap', padding: '10px' }}>
        {desktopItems.map(item => (
          <div key={item.name} onDoubleClick={() => handleIconDoubleClick(item)}>
            <Icon name={item.name} type={item.type} is_executable={item.executable} />
          </div>
        ))}
      </div>

      {windows.map(win => {
        if (win.type === 'terminal') {
          return <Terminal key={win.id} ws={ws} log={win.log} path={currentPath} onClose={() => closeWindow(win.id)} inputValue={terminalInputValue} setInputValue={setTerminalInputValue} />;
        }
        if (win.type === 'editor') {
          return <TextEditor key={win.id} filePath={win.filePath} initialContent={win.initialContent} onSave={handleSaveFile} onClose={() => closeWindow(win.id)} />;
        }
        return null;
      })}

      {contextMenu.visible && (
        <div className="context-menu" style={{ top: contextMenu.y, left: contextMenu.x }}>
          <ul>
            <li onClick={openNewTerminal}>打开终端</li>
            <li className="separator"></li>
            <li className="disabled">新建文件夹 (待实现)</li>
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;