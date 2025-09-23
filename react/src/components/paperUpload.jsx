import { useState } from "react";
import { uploadPaper } from "../api/api";
import { useAuth } from "../AuthContext";

export default function PaperUpload({ onUpload }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const { token } = useAuth();

  const handleUpload = async () => {
    if (!file || !token) return;
    setLoading(true);
    try {
      const result = await uploadPaper(file, token); // pass JWT token
      alert(result.message);
      onUpload(); // refresh paper list
    } catch (err) {
      alert("Error uploading paper: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input type="file" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={handleUpload} disabled={loading || !token}>
        {loading ? "Uploading..." : "Upload Paper"}
      </button>
    </div>
  );
}
