import formidable from 'formidable';
import fs from 'fs';
import path from 'path';

export const config = {
  api: {
    bodyParser: false,
  },
};

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const uploadDir = path.join(process.cwd(), 'uploads');
  
  if (!fs.existsSync(uploadDir)) {
    fs.mkdirSync(uploadDir, { recursive: true });
  }

  const form = formidable({
    uploadDir,
    keepExtensions: true,
    maxFileSize: 10 * 1024 * 1024, // 10MB limit
  });

  try {
    const [fields, files] = await form.parse(req);
    const file = Array.isArray(files.file) ? files.file[0] : files.file;

    if (!file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    if (!file.originalFilename?.endsWith('.docx')) {
      fs.unlinkSync(file.filepath);
      return res.status(400).json({ error: 'Only .docx files are allowed' });
    }

    const timestamp = Date.now();
    const filename = `${timestamp}_${file.originalFilename}`;
    const newPath = path.join(uploadDir, filename);

    fs.renameSync(file.filepath, newPath);

    res.status(200).json({ 
      success: true, 
      filename,
      originalName: file.originalFilename 
    });
  } catch (error) {
    console.error('Upload error:', error);
    res.status(500).json({ error: 'Upload failed' });
  }
}