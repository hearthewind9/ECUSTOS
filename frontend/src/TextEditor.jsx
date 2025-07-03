// frontend/src/TextEditor.jsx (V2 - 带行号和语法高亮版)
import React, { useState } from 'react';
import Draggable from 'react-draggable';
import Editor from 'react-simple-code-editor'; // 引入新安装的编辑器
import { highlight, languages } from 'prismjs/components/prism-core'; // 引入PrismJS
import 'prismjs/components/prism-clike';
import 'prismjs/components/prism-c'; // 为C语言添加语法高亮
import 'prismjs/themes/prism-tomorrow.css'; // 引入一个好看的深色主题

function TextEditor({ filePath, initialContent, onSave, onClose }) {
  const [content, setContent] = useState(initialContent);
  const nodeRef = React.useRef(null);

  const handleSave = () => {
    onSave(filePath, content);
  };

  const editorStyle = {
    fontFamily: '"Fira code", "Fira Mono", monospace',
    fontSize: 14,
    minHeight: '100%',
    background: '#282a36',
    color: '#f8f8f2',
  };

  return (
    <Draggable nodeRef={nodeRef} handle=".title-bar" cancel=".editor-content, .editor-buttons">
      <div ref={nodeRef} className="terminal-window text-editor">
        <div className="title-bar">
          {filePath}
          {/* 使用图片作为关闭按钮 */}
          <img 
            src="/icons/close.png" 
            alt="Close" 
            onClick={onClose} 
            className="window-close-btn"
          />
        </div>
        {/* 使用新的 Editor 组件替换 textarea */}
        <div className="editor-content">
          <Editor
            value={content}
            onValueChange={code => setContent(code)}
            highlight={code => highlight(code, languages.c, 'c')}
            padding={10}
            style={editorStyle}
          />
        </div>
        <div className="editor-buttons">
          <button onClick={handleSave}>保存</button>
        </div>
      </div>
    </Draggable>
  );
}

export default TextEditor;