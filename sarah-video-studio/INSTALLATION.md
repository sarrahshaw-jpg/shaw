# Installation & Local Usage

## Prerequisites
- **Node.js:** v18+
- **FFmpeg:** Must be installed and accessible in your system's PATH.

## Setup
1. Clone the repository and navigate to `sarah-video-studio`.
2. Install dependencies:
   \`\`\`bash
   npm install
   \`\`\`
3. Set up environment variables:
   \`\`\`bash
   cp .env.example .env
   \`\`\`
   *(Note: The app will run in Demo Mode if API keys are omitted.)*

## Running the App
Start the Next.js frontend & agent backend:
\`\`\`bash
npm run dev
\`\`\`
Open [http://localhost:3000](http://localhost:3000) in your browser.

## Using the Editor
1. Click **Upload New Video** on the dashboard.
2. Select your raw MP4/MOV file.
3. Wait for the **AI Agent** to process the file and generate an EDL.
4. Review the timeline and preview.
5. Use the **Natural Language Command Bar** to tweak the edit (e.g., "Add more b-roll").
6. Click **Approve & Export** to generate the final renders for TikTok, Reels, Shorts, and LinkedIn.
