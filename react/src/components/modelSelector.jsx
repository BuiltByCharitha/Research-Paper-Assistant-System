import { useEffect, useState } from "react";
import { getModels } from "../api/api";
import { useAuth } from "../AuthContext";

export default function ModelSelector({ selectedModel, setSelectedModel }) {
  const [models, setModels] = useState([]);
  const { token } = useAuth();

  useEffect(() => {
    async function fetchModels() {
      if (!token) return; // wait until logged in
      try {
        const data = await getModels(token); // pass token
        setModels(data.supported_models);
      } catch (err) {
        alert("Error fetching models: " + err.message);
      }
    }
    fetchModels();
  }, [token]);

  return (
    <select value={selectedModel} onChange={(e) => setSelectedModel(e.target.value)}>
      {models.map((model) => (
        <option key={model} value={model}>
          {model}
        </option>
      ))}
    </select>
  );
}
