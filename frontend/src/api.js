// frontend/api.js  ← This file is in frontend/, NOT in src/

const API_URL = "http://localhost:5000";  // Flask server

export const askQuestion = async (question) => {
  const res = await fetch(`${API_URL}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) throw new Error("Failed to reach backend");
  return res.json();
};

export const getHistory = async () => {
  const res = await fetch(`${API_URL}/history`);
  if (!res.ok) throw new Error("Failed to load history");
  return res.json();
};

export const sendFeedback = async (id, feedback) => {
  await fetch(`${API_URL}/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ qa_id: id, feedback }),
  });
};