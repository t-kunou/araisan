import React from "react";

const GOOGLE_LOGOUT_URL = process.env.NEXT_PUBLIC_API_BASE_URL + '/logout';

const GoogleLogoutButton: React.FC = () => (
  <a href={GOOGLE_LOGOUT_URL}>
    <button style={{ padding: "8px 16px", background: "#DB4437", color: "#fff", border: "none", borderRadius: 4 }}>
      Googleからログアウト
    </button>
  </a>
);
export default GoogleLogoutButton;