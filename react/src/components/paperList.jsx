import { useEffect, useState } from "react";
import { listPapers } from "../api/api";
import { useAuth } from "../AuthContext";

export default function PaperList({ selectedPaper, setSelectedPaper }) {
  const [papers, setPapers] = useState([]);
  const { token } = useAuth();

  const fetchPapers = async () => {
    if (!token) return; // wait until logged in
    try {
      const data = await listPapers(token); // pass JWT token
      setPapers(data.papers);
    } catch (err) {
      alert("Error fetching papers: " + err.message);
    }
  };

  useEffect(() => {
    fetchPapers();
  }, [token]);

  return (
    <div>
      <h3>Uploaded Papers</h3>
      <ul>
        {papers.map((paper) => (
          <li key={paper.id}>
            <button onClick={() => setSelectedPaper(paper.id)}>
              {paper.title}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
