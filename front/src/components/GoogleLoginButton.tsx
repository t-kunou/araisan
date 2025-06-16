import React from "react";

const GOOGLE_LOGIN_URL = process.env.NEXT_PUBLIC_API_BASE_URL + '/login'

const GoogleLoginButton: React.FC = () => {
 
  const handleLogin = async () => {
    const res = await fetch(GOOGLE_LOGIN_URL)
    const data = await res.json();
    const authorization_url = data.authorization_url;

    console.log("autorization_url:", authorization_url);

    window.location.href = authorization_url;
  }

  return (
    <button onClick={handleLogin} style={{ padding: "8px 16px", background: "#4285F4", color: "#fff", border: "none", borderRadius: 4 }}>
      Googleでログイン
    </button>
  )};

export default GoogleLoginButton;