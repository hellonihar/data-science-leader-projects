import { useState, useEffect, useRef } from 'react';
import { api } from '../services/api';
import { Upload, FileText, Trash2 } from 'lucide-react';

interface DocFile {
  filename: string;
  metadata: Record<string, unknown>;
}

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setDocuments(await api.listDocuments());
    } catch {}
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setMessage('');
    try {
      const result = await api.uploadDocument(file);
      setMessage(result.message);
      loadDocuments();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : 'Upload failed');
    }
    setUploading(false);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Document Management</h1>

      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-6 text-center">
        <Upload className="mx-auto mb-3 text-gray-500" size={32} />
        <p className="text-sm text-gray-400 mb-3">Upload clinical guidelines, treatment protocols, or other documents for RAG indexing</p>
        <input
          ref={fileInputRef}
          type="file"
          accept=".txt,.pdf,.md,.docx"
          onChange={handleUpload}
          className="hidden"
          id="file-upload"
        />
        <label
          htmlFor="file-upload"
          className="inline-block bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded cursor-pointer text-sm"
        >
          {uploading ? 'Uploading...' : 'Choose File'}
        </label>
        {message && <p className="text-sm text-gray-400 mt-3">{message}</p>}
      </div>

      <div className="space-y-2">
        {documents.length === 0 && (
          <p className="text-gray-500 text-center py-8">No documents uploaded yet.</p>
        )}
        {documents.map(doc => (
          <div key={doc.filename} className="bg-gray-800 rounded-lg p-4 border border-gray-700 flex items-center gap-3">
            <FileText className="text-gray-500" size={20} />
            <div className="flex-1">
              <p className="text-sm font-medium">{doc.filename}</p>
              <p className="text-xs text-gray-500">Uploaded for RAG indexing</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
