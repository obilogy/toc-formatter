import { useState } from 'react';
import Head from 'next/head';

export default function Home() {
  const [file, setFile] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [logs, setLogs] = useState('');

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.name.endsWith('.docx')) {
      setFile(selectedFile);
      setError(null);
      setResult(null);
      setLogs('');
    } else {
      setError('Please select a .docx file');
      setFile(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setProcessing(true);
    setError(null);
    setResult(null);
    setLogs('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const uploadResponse = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!uploadResponse.ok) {
        throw new Error('Upload failed');
      }

      const { filename } = await uploadResponse.json();

      const processResponse = await fetch('/api/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename }),
      });

      if (!processResponse.ok) {
        const errorData = await processResponse.json();
        throw new Error(errorData.error || 'Processing failed');
      }

      const processResult = await processResponse.json();
      setResult(processResult);
      setLogs(processResult.logs || '');
    } catch (err) {
      setError(err.message);
    } finally {
      setProcessing(false);
    }
  };

  const handleDownload = () => {
    if (result?.outputFile) {
      window.open(`/api/download?file=${encodeURIComponent(result.outputFile)}`, '_blank');
    }
  };

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', padding: '40px 20px', fontFamily: 'system-ui' }}>
      <Head>
        <title>TOC Formatter</title>
      </Head>

      <h1 style={{ textAlign: 'center', marginBottom: '40px', color: '#333' }}>
        Table of Contents Formatter
      </h1>

      <div style={{ 
        border: '2px dashed #ccc', 
        borderRadius: '8px', 
        padding: '40px', 
        textAlign: 'center',
        marginBottom: '20px',
        backgroundColor: file ? '#f8f9fa' : '#fff'
      }}>
        <input
          type="file"
          accept=".docx"
          onChange={handleFileChange}
          style={{ marginBottom: '20px' }}
        />
        <p style={{ color: '#666', margin: '10px 0' }}>
          Select a .docx file with messy table of contents
        </p>
        {file && (
          <p style={{ color: '#28a745', fontWeight: 'bold' }}>
            Selected: {file.name}
          </p>
        )}
      </div>

      <div style={{ textAlign: 'center', marginBottom: '30px' }}>
        <button
          onClick={handleUpload}
          disabled={!file || processing}
          style={{
            backgroundColor: processing ? '#ccc' : '#007bff',
            color: 'white',
            border: 'none',
            padding: '12px 24px',
            borderRadius: '4px',
            cursor: processing ? 'not-allowed' : 'pointer',
            fontSize: '16px'
          }}
        >
          {processing ? 'Processing...' : 'Format TOC'}
        </button>
      </div>

      {error && (
        <div style={{
          backgroundColor: '#f8d7da',
          color: '#721c24',
          padding: '15px',
          borderRadius: '4px',
          marginBottom: '20px'
        }}>
          Error: {error}
        </div>
      )}

      {result && (
        <div style={{
          backgroundColor: '#d4edda',
          color: '#155724',
          padding: '15px',
          borderRadius: '4px',
          marginBottom: '20px'
        }}>
          <p style={{ margin: '0 0 10px 0', fontWeight: 'bold' }}>
            ✅ Processing complete!
          </p>
          <button
            onClick={handleDownload}
            style={{
              backgroundColor: '#28a745',
              color: 'white',
              border: 'none',
              padding: '8px 16px',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Download Formatted Document
          </button>
        </div>
      )}

      {logs && (
        <div style={{
          backgroundColor: '#f8f9fa',
          border: '1px solid #dee2e6',
          borderRadius: '4px',
          padding: '15px',
          marginTop: '20px'
        }}>
          <h4 style={{ margin: '0 0 10px 0', color: '#495057' }}>Processing Log:</h4>
          <pre style={{ 
            margin: 0, 
            fontSize: '12px', 
            color: '#495057',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word'
          }}>
            {logs}
          </pre>
        </div>
      )}

      <div style={{ 
        marginTop: '40px', 
        padding: '20px', 
        backgroundColor: '#f8f9fa', 
        borderRadius: '4px' 
      }}>
        <h3 style={{ margin: '0 0 15px 0', color: '#495057' }}>What this tool does:</h3>
        <ul style={{ color: '#6c757d', lineHeight: '1.6' }}>
          <li>Removes messy arrows and dots from table of contents</li>
          <li>Adds professional dot leaders</li>
          <li>Properly aligns page numbers</li>
          <li>Formats abbreviation definitions</li>
          <li>Preserves hierarchy and indentation</li>
          <li>Supports Roman numerals and special characters</li>
        </ul>
      </div>
    </div>
  );
}