import { useState, useEffect } from "react";
import { useAuth } from "./AuthContext";
import Login from "./components/logIn";
import Signup from "./components/signUp";
import PaperUpload from "./components/paperUpload";
import PaperList from "./components/paperList";
import ModelSelector from "./components/modelSelector";
import FullSummary from "./components/fullSummary";
import QuerySummary from "./components/querySummary";
import GlobalQuery from "./components/globalQuery";
import KeywordRecommendation from "./components/keywordRecommedation";
import { listPapers } from "./api/api.js";  // use listPapers

export default function App() {
  const { token, logout } = useAuth();
  const [selectedPaper, setSelectedPaper] = useState(null);
  const [selectedModel, setSelectedModel] = useState("phi3:mini");
  const [showSignup, setShowSignup] = useState(false);
  const [papers, setPapers] = useState([]); 

  // Fetch papers initially
  useEffect(() => {
    if (token) {
      listPapers(token).then(setPapers).catch(console.error);
    }
  }, [token]);

  // Handle new paper upload
  const handlePaperUpload = async () => {
    const updatedPapers = await listPapers(token);
    setPapers(updatedPapers);
  };

  if (!token) {
    return (
      <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
        <h1>Welcome to Research Paper Assistant</h1>
        {showSignup ? <Signup /> : <Login />}
        <p>
          {showSignup ? "Already have an account?" : "Don't have an account?"}{" "}
          <button onClick={() => setShowSignup(!showSignup)} style={{ marginLeft: "5px" }}>
            {showSignup ? "Login" : "Signup"}
          </button>
        </p>
      </div>
    );
  }

  return (
    <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
      <h1>📑 Research Paper Assistant</h1>
      <button onClick={logout}>Logout</button>

      {/* Model Selection */}
      <ModelSelector selectedModel={selectedModel} setSelectedModel={setSelectedModel} />

      {/* Global Query */}
      <section style={{ marginTop: "20px" }}>
        <h2>🌍 Global Query (All Papers)</h2>
        <GlobalQuery token={token} model={selectedModel} />
      </section>

      {/* Keyword-based Recommendations */}
      <section style={{ marginTop: "20px" }}>
        <h2>🔑 Keyword-based Recommendations</h2>
        <KeywordRecommendation token={token} onSelectPaper={setSelectedPaper} />
      </section>

      {/* Upload & List Papers */}
      <section style={{ marginTop: "20px" }}>
        <h2>📂 Your Papers</h2>
        <PaperUpload token={token} onUpload={handlePaperUpload} />
        <PaperList
          token={token}
          papers={papers}
          selectedPaper={selectedPaper}
          setSelectedPaper={setSelectedPaper}
        />
      </section>

      {/* Summaries */}
      {selectedPaper && (
        <section style={{ marginTop: "20px" }}>
          <h2>📄 Paper Summaries</h2>
          <FullSummary paperId={selectedPaper} model={selectedModel} token={token} />
          <QuerySummary paperId={selectedPaper} model={selectedModel} token={token} />
        </section>
      )}
    </div>
  );
}
