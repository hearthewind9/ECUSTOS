import React, { useEffect, useRef } from 'react';
import Draggable from 'react-draggable';

function Terminal({ ws, log, path, onClose, inputValue, setInputValue }) {
  const logAreaRef = useRef(null);
  const nodeRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (logAreaRef.current) {
      logAreaRef.current.scrollTop = logAreaRef.current.scrollHeight;
    }
  }, [log]);

  useEffect(() => {
    if(inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  const sendMessage = () => {
    if (inputValue.trim() && ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ action: 'runCommand', payload: inputValue }));
      setInputValue('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Tab') {
      e.preventDefault();
      ws.current.send(JSON.stringify({ action: 'autoComplete', payload: inputValue }));
    }
    if (e.key === 'Enter') {
      sendMessage();
    }
  };

  return (
    <Draggable nodeRef={nodeRef} handle=".title-bar" cancel=".terminal-content">
      <div ref={nodeRef} className="terminal-window" onClick={() => inputRef.current?.focus()}>
        <div className="title-bar">
          {path}
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
            <span>$</span>
            <input 
              ref={inputRef}
              type="text" 
              value={inputValue} 
              onChange={e => setInputValue(e.target.value)} 
              onKeyDown={handleKeyDown}
            />
          </div>
        </div>
      </div>
    </Draggable>
  );
}

export default Terminal;