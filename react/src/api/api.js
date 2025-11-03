// api.js
const BASE_URL = "http://127.0.0.1:8000";

// ---- Public endpoints ----
export async function signup(username, password) {
  const res = await fetch(`${BASE_URL}/signup/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) throw new Error((await res.json()).detail || "Signup failed");
  return await res.json();
}

export async function login(username, password) {
  const formData = new URLSearchParams();
  formData.append("username", username);
  formData.append("password", password);

  const res = await fetch(`${BASE_URL}/token/`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: formData,
  });
  if (!res.ok) throw new Error((await res.json()).detail || "Login failed");
  return await res.json(); // { access_token, token_type }
}

// ---- Protected endpoints ----
export async function askGlobalQuery(query, model, token) {
  const res = await fetch(`${BASE_URL}/global-query/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ query, model }),  // include model
  });

  if (!res.ok) throw new Error(await res.text());
  return await res.json();
}


// ---- Centralized protected fetch ----
const fetchWithAuth = async (url, token, options = {}) => {
  options.headers = {
    ...(options.headers || {}),
    Authorization: `Bearer ${token}`,
  };

  const res = await fetch(`${BASE_URL}${url}`, options);

  if (!res.ok) {
    if (res.status === 401) handleUnauthorized();
    throw new Error(await res.text());
  }
  return await res.json();
};

// ---- Helper: handle unauthorized, expired token ----
function handleUnauthorized() {
  
  localStorage.removeItem("token");
  window.location.href = "/";
}

// Upload a paper
export async function uploadPaper(file, token) {
  const formData = new FormData();
  formData.append("file", file);
  return await fetchWithAuth("/upload-paper/", token, { method: "POST", body: formData });
}

// List user's papers
export async function listPapers(token) {
  return await fetchWithAuth("/list-papers/", token);
}

// Recommend papers based on keyword
export async function recommendPapers(keyword, token) {
  return await fetchWithAuth(`/recommend-papers/?keyword=${encodeURIComponent(keyword)}`, token);
}

// Summarize full paper
export async function summarizeFull(paper_id, model, token) {
  return await fetchWithAuth("/summarize-full/", token, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ paper_id, model }),
  });
}

// Summarize paper by query
export async function summarizeQuery(paper_id, query, top_k, model, token) {
  return await fetchWithAuth("/summarize-query/", token, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ paper_id, query, top_k, model }),
  });
}

// Get available models
export async function getModels(token) {
  return await fetchWithAuth("/models/", token);
}
