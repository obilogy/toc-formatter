import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { filename } = req.body;

  if (!filename) {
    return res.status(400).json({ error: 'Filename is required' });
  }

  const inputPath = path.join(process.cwd(), 'uploads', filename);
  const outputDir = path.join(process.cwd(), 'outputs');
  const outputFilename = `processed_${filename}`;
  const outputPath = path.join(outputDir, outputFilename);

  if (!fs.existsSync(inputPath)) {
    return res.status(404).json({ error: 'File not found' });
  }

  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  return new Promise((resolve) => {
    const pythonScript = path.join(process.cwd(), 'python', 'toc_formatter.py');
    const pythonProcess = spawn('python3', [
      pythonScript,
      inputPath,
      '-o',
      outputPath
    ]);

    let output = '';
    let error = '';

    pythonProcess.stdout.on('data', (data) => {
      output += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      error += data.toString();
    });

    pythonProcess.on('close', (code) => {
      // Clean up input file
      try {
        fs.unlinkSync(inputPath);
      } catch (e) {
        console.error('Failed to delete input file:', e);
      }

      if (code === 0) {
        res.status(200).json({
          success: true,
          outputFile: outputFilename,
          logs: output
        });
      } else {
        console.error('Python process error:', error);
        res.status(500).json({
          error: error || 'Processing failed',
          logs: output
        });
      }
      resolve();
    });

    pythonProcess.on('error', (err) => {
      console.error('Failed to start Python process:', err);
      res.status(500).json({
        error: 'Failed to start processing. Make sure Python is installed.'
      });
      resolve();
    });
  });
}