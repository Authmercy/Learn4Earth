import { useNavigate } from "react-router-dom";

export function apiFetch(url, options = {}) {
  const token = localStorage.getItem("access_token");

  return fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: token ? `Bearer ${token}` : "",
      ...(options.headers || {}),
    },
  }).then(async (res) => {
    // Token expiré → déconnexion
    if (res.status === 401 || res.status === 403) {
      localStorage.removeItem("access_token");
      window.location.href = "/login"; // redirection immédiate
      return;
    }

    // Retour normal
    const data = await res.json().catch(() => null);
    return { status: res.status, data };
  });
}
