// frontend/src/Icon.jsx (V5 - 修正样式版)

import React from 'react';

const ICONS = {
  directory: "/icons/folder.png",
  file: "/icons/file.png",
  c: "/icons/c.png",
  python: "/icons/python.png",
  text: "/icons/text.png",
  executable: "/icons/executable.png" 
};

function getIconForFile(name, type, is_executable) {
  if (type === 'directory') {
    return ICONS.directory;
  }
  if (is_executable) {
    return ICONS.executable;
  }
  if (!name.includes('.') || name.startsWith('.')) {
    return ICONS.file;
  }
  const extension = name.split('.').pop().toLowerCase();
  switch (extension) {
    case 'c':
    case 'h':
    case 'cpp':
      return ICONS.c;
    case 'py':
      return ICONS.python;
    case 'txt':
    case 'md':
    case 'doc':
      return ICONS.text;
    // 我们可以为 a.exe 这样的文件也指定图标
    case 'exe':
      return ICONS.executable;
    default:
      return ICONS.file;
  }
}

function Icon({ name, type, is_executable }) {
  // --- 核心改动：移除了内部的flex布局，采用更简单的块级布局 ---
  const style = {
    width: '80px',
    textAlign: 'center', // 让文字居中
    margin: '10px',
    color: 'white',
    textShadow: '1px 1px 2px black',
  };
  
  const imgStyle = {
    width: '50px',
    height: '50px',
  };

  const pStyle = {
    margin: '5px 0',
    wordWrap: 'break-word',
    width: '100%',
  };
  
  const iconUrl = getIconForFile(name, type, is_executable);

  return (
    // 外层div负责双击事件和key
    <div style={style}>
      {/* 内层img和p负责显示 */}
      <img src={iconUrl} alt={name} style={imgStyle} />
      <p style={pStyle}>{name}</p>
    </div>
  );
}

export default Icon;