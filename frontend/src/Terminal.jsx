import React, { useState, useEffect, useRef } from 'react';
import Draggable from 'react-draggable';

function Terminal({ ws, log, path, onClose }) {
  const [inputValue, setInputValue] = useState('');
  const logAreaRef = useRef(null);
  const nodeRef = useRef(null);

  // 自动滚动到日志底部
  useEffect(() => {
    if (logAreaRef.current) {
      logAreaRef.current.scrollTop = logAreaRef.current.scrollHeight;
    }
  }, [log]);

  // 发送命令
  const sendMessage = () => {
    if (inputValue && ws.current?.readyState === WebSocket.OPEN) {
      // 发送JSON格式的消息
      ws.current.send(JSON.stringify({ action: 'runCommand', payload: inputValue }));
      setInputValue('');
    }
  };

  return (
    <Draggable nodeRef={nodeRef} handle=".title-bar" cancel=".terminal-content">
      <div ref={nodeRef} className="terminal-window">
        <div className="title-bar">
          {path}
          {/* 这里是修改过的地方，确保它使用的是img标签 */}
          <img 
            src="/icons/close.png" 
            alt="Close" 
            onClick={onClose} 
            className="window-close-btn"
          />
        </div>
        <div className="terminal-content">
          <pre className="terminal-log-area" ref={logAreaRef}>{log.join('\n')}</pre>
          <div className="terminal-input-area">
            <input type="text" value={inputValue} onChange={e => setInputValue(e.target.value)} onKeyPress={e => e.key === 'Enter' && sendMessage()} placeholder="$" />
            <button onClick={sendMessage}>执行</button>
          </div>
        </div>
      </div>
    </Draggable>
  );
}

export default Terminal;
