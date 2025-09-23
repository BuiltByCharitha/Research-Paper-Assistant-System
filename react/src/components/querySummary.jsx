import { useState } from "react";
import { summarizeQuery } from "../api/api";
import { useAuth } from "../AuthContext";

export default function QuerySummary({ paperId, model }) {
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const { token } = useAuth();

  const handleQuery = async () => {
    if (!paperId || !query || !token) return;
    setLoading(true);
    try {
      const data = await summarizeQuery(paperId, query, 3, model, token); // pass token
      setAnswer(data.answer);
    } catch (err) {
      alert("Error querying: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input
        type="text"
        placeholder="Enter your query"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <button onClick={handleQuery} disabled={loading || !query || !token}>
        {loading ? "Fetching Answer..." : "Query Paper"}
      </button>
      {answer && (
        <div>
          <h4>Answer:</h4>
          <p>{answer}</p>
        </div>
      )}
    </div>
  );
}
