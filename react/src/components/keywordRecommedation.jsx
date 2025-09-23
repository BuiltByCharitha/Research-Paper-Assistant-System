import { useState } from "react";
import { recommendPapers } from "../api/api";
import { useAuth } from "../AuthContext";

export default function KeywordRecommendation({ onSelectPaper }) {
  const { token } = useAuth();
  const [keyword, setKeyword] = useState("");
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async () => {
    if (!keyword.trim()) return;
    if (!token) return alert("Please login to search papers");

    setLoading(true);
    setError(null);
    try {
      const data = await recommendPapers(keyword, token); // pass token
      setRecommendations(data.recommended_papers || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ marginTop: "20px" }}>
      <h2>Keyword-Based Paper Recommendations</h2>
      <input
        type="text"
        value={keyword}
        onChange={(e) => setKeyword(e.target.value)}
        placeholder="Enter a keyword"
      />
      <button onClick={handleSearch} disabled={loading}>
        {loading ? "Searching..." : "Search"}
      </button>
      {error && <p style={{ color: "red" }}>{error}</p>}
      {recommendations.length > 0 && (
        <ul>
          {recommendations.map((paper) => (
            <li
              key={paper.id}
              style={{ cursor: "pointer" }}
              onClick={() => onSelectPaper && onSelectPaper(paper.id)}
            >
              {paper.title} ({paper.id})
            </li>
          ))}
        </ul>
      )}
      {recommendations.length === 0 && !loading && <p>No recommendations yet.</p>}
    </div>
  );
}
