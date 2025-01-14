const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const clearBtn = document.getElementById('clear-btn');
const outputText = document.getElementById('output-text');

// Set canvas dimensions
canvas.width = canvas.offsetWidth;
canvas.height = canvas.offsetHeight;

let drawing = false;
let saveTimeout = null;

// Start drwing
canvas.addEventListener('mousedown', (e) => {
  drawing = true;
  ctx.beginPath();
  ctx.moveTo(e.offsetX, e.offsetY)
});

// Stop drawing
canvas.addEventListener('mouseup', (e) => {
  drawing = false;
  ctx.beginPath();

  // Start a timeout to save the canvas as PNG
  saveTimeout = setTimeout(() => {
    saveDrawing();
  }, 3000);
});

// Draw on the canvas
canvas.addEventListener('mousemove', (e) => {
  if (!drawing) return;
  ctx.lineWidth = 4;
  ctx.lineCap = 'round';
  ctx.strokeStyle = 'black';
  ctx.lineTo(e.offsetX, e.offsetY);
  ctx.stroke();
});

// Clear the canvas
clearBtn.addEventListener('click', () => {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  outputText.innerText = "Your output  will appear here."
  clearTimeout(saveTimeout);
});

// Send the drawing to the backend
async function saveDrawing() {
  const image = canvas.toDataURL('image/png');
  const response = await fetch('/process-drawing', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image })
  });
  const result = await response.json();

  // Update the output  area with the extracted text from the response
  if (result.extracted_text) {
    outputText.innerText = result.extracted_text;
  } else {
    outputText.innerText = "No text exctraced"
  }
}
