import fs from 'fs';
import path from 'path';

export default function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { file } = req.query;

  if (!file) {
    return res.status(400).json({ error: 'File parameter is required' });
  }

  const filePath = path.join(process.cwd(), 'outputs', file);

  if (!fs.existsSync(filePath)) {
    return res.status(404).json({ error: 'File not found' });
  }

  try {
    const fileBuffer = fs.readFileSync(filePath);
    const originalName = file.replace('processed_', '').replace(/^\d+_/, '');

    res.setHeader('Content-Disposition', `attachment; filename="${originalName}"`);
    res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document');
    res.setHeader('Content-Length', fileBuffer.length);

    res.send(fileBuffer);

    // Clean up the file after download
    setTimeout(() => {
      try {
        fs.unlinkSync(filePath);
      } catch (e) {
        console.error('Failed to delete output file:', e);
      }
    }, 1000);

  } catch (error) {
    console.error('Download error:', error);
    res.status(500).json({ error: 'Failed to download file' });
  }
}