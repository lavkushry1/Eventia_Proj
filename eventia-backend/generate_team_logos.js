const fs = require('fs');
const path = require('path');
const https = require('https');

// Create directories if they don't exist
const backendDir = path.join(__dirname, 'app', 'static', 'teams');
const frontendDir = path.join(__dirname, '..', 'eventia-ticketing-flow', 'public', 'assets', 'teams');

// Ensure directories exist
[backendDir, frontendDir].forEach(dir => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
    console.log(`Created directory: ${dir}`);
  }
});

// Team colors (hex without #)
const teamColors = {
  csk: 'FFFF00', // Yellow
  mi: '004BA0',  // Blue
  rcb: 'FF0000', // Red
  kkr: '3A225D', // Purple
  dc: '0078BC',  // Blue
  srh: 'FF822A', // Orange
  rr: 'FF69B4',  // Pink
  pbks: 'ED1C24', // Red
  gt: '1C1C1C',  // Dark Grey
  lsg: 'A7D5ED'  // Light Blue
};

// Function to download an image
function downloadImage(url, filepath) {
  return new Promise((resolve, reject) => {
    https.get(url, (response) => {
      if (response.statusCode !== 200) {
        reject(new Error(`Failed to download image: ${response.statusCode}`));
        return;
      }

      const fileStream = fs.createWriteStream(filepath);
      response.pipe(fileStream);

      fileStream.on('finish', () => {
        fileStream.close();
        resolve();
      });

      fileStream.on('error', (err) => {
        fs.unlink(filepath, () => {});
        reject(err);
      });
    }).on('error', reject);
  });
}

// Generate and download placeholder images for each team
async function generateTeamLogos() {
  for (const [team, color] of Object.entries(teamColors)) {
    const textColor = (team === 'csk' || team === 'lsg') ? '000000' : 'FFFFFF';
    const url = `https://placehold.co/500x500/${color}/${textColor}.png?text=${team.toUpperCase()}`;
    
    const backendPath = path.join(backendDir, `${team}.png`);
    const frontendPath = path.join(frontendDir, `${team}.png`);
    
    try {
      await downloadImage(url, backendPath);
      // Copy to frontend
      fs.copyFileSync(backendPath, frontendPath);
      console.log(`Generated logo for ${team}`);
    } catch (error) {
      console.error(`Error generating logo for ${team}:`, error.message);
    }
  }
  
  console.log('All team logos generated successfully!');
}

generateTeamLogos().catch(console.error);