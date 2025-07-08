import React, { useState } from 'react';

function Login({ onLogin, error }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (username && password) {
      onLogin(username, password);
    }
  };

  const loginContainerStyle = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100vh',
    backgroundImage: `url('/desktop-bg.jpg')`,
    backgroundSize: 'cover',
  };

  const formStyle = {
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
    padding: '40px',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    borderRadius: '12px',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    backdropFilter: 'blur(10px)',
    width: '320px',
  };

  const inputStyle = {
    padding: '12px',
    border: '1px solid #666',
    borderRadius: '4px',
    background: '#333',
    color: 'white',
    fontSize: '16px'
  };
  
  const buttonStyle = {
    padding: '12px',
    background: '#007aff',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    fontSize: '16px',
    cursor: 'pointer'
  }

  return (
    <div style={loginContainerStyle}>
      <form onSubmit={handleSubmit} style={formStyle}>
        <h2 style={{ color: 'white', textAlign: 'center', margin: 0, marginBottom: '10px' }}>Visual OS Login</h2>
        <input 
          type="text" 
          placeholder="用户名 (maruiyang 或 guest)"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          style={inputStyle}
        />
        <input 
          type="password"
          placeholder="密码 (123456 或 guest)"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={inputStyle}
        />
        <button type="submit" style={buttonStyle}>
          登 录
        </button>
        {error && <p style={{ color: '#ff5555', textAlign: 'center', margin: 0 }}>{error}</p>}
      </form>
    </div>
  );
}

export default Login;