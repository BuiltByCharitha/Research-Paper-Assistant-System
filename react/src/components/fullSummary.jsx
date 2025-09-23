import { useState } from "react";
import { summarizeFull } from "../api/api";
import { useAuth } from "../AuthContext";

export default function FullSummary({ paperId, model }) {
  const { token } = useAuth(); // get JWT token
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSummarize = async () => {
    if (!paperId) return;
    if (!token) return alert("Not authenticated");

    setLoading(true);
    try {
      const data = await summarizeFull(paperId, model, token); // pass token
      setSummary(data.summary);
    } catch (err) {
      alert("Error summarizing: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={handleSummarize} disabled={loading || !paperId}>
        {loading ? "Summarizing..." : "Summarize Full Paper"}
      </button>
      {summary && (
        <div>
          <h4>Summary:</h4>
          <p>{summary}</p>
        </div>
      )}
    </div>
  );
}
