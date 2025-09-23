import React, { useState } from "react";
import { askGlobalQuery } from "../api/api";

const GlobalQuery = ({ model, token }) => {
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    if (!token) return alert("Please login to ask queries");

    setLoading(true);
    try {
      const response = await askGlobalQuery(query, model, token);
      setAnswer(response.answer);
    } catch (error) {
      console.error("Error fetching global query answer:", error);
      setAnswer("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-6 bg-white rounded-2xl shadow">
      <h2 className="text-xl font-semibold mb-4">Ask a Global Query</h2>
      <form onSubmit={handleSubmit} className="flex gap-2 mb-4">
        <input
          type="text"
          placeholder="Ask a question..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="flex-1 p-2 border rounded-lg focus:outline-none focus:ring"
        />
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
        >
          {loading ? "Thinking..." : "Ask"}
        </button>
      </form>
      {answer && (
        <div className="p-4 bg-gray-100 rounded-lg">
          <h3 className="font-medium">Answer:</h3>
          <p className="mt-2">{answer}</p>
        </div>
      )}
    </div>
  );
};

export default GlobalQuery;
