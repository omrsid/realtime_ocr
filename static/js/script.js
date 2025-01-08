const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');

// Set canvas dimensions
canvas.width = canvas.offsetWidth;
canvas.height = canvas.offsetHeight;

let drawing = false;

canvas.addEventListener('mousedown', () => drawing = true);
canvas.addEventListener('mouseup', () => drawing = false);
canvas.addEventListener('mousemove', draw);

function draw(e) {
  if (!drawing) return;
  ctx.lineWidth = 3;
  ctx.lineCap = 'round';
  ctx.strokeStyle = 'black';
  ctx.lineTo(e.offsetX, e.offsetY);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(e.offsetX, e.offsetY);
}

// Send the drawing to the backend
async function saveDrawing() {
  const image = canvas.toDataURL('image/png');
  const response = await fetch('/process-drawing', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image })
  });
  const result = await response.json();
  document.getElementById('output-text').innerText = result.result;
}
