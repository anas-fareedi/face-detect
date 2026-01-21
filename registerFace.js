const video = document.getElementById('video');
const statusDiv = document.getElementById('status');
let labeledFaceDescriptors = [];
let faceMatcher = null;
let isModelLoaded = false;
const API_BASE_URL = 'http://localhost:8000/api/v1';

async function loadModels() {
  try {
    statusDiv.textContent = 'Loading models...';
    console.log('Loading models...');
    
    await Promise.all([
      faceapi.nets.tinyFaceDetector.loadFromUri('./models'),
      faceapi.nets.faceLandmark68Net.loadFromUri('./models'),
      faceapi.nets.faceRecognitionNet.loadFromUri('./models'),
      faceapi.nets.faceExpressionNet.loadFromUri('./models')
    ]);
    
    console.log('Models loaded');
    isModelLoaded = true;
    
    statusDiv.textContent = 'Loading registered faces...';
    await loadRegisteredFaces();
    
    statusDiv.textContent = 'Starting camera...';
    await startVideo();
    
    statusDiv.textContent = '✓ Ready!';
    
  } catch (err) {
    console.error('Error:', err);
    statusDiv.textContent = '✗ Error: ' + err.message;
    statusDiv.style.color = 'red';
  }
}

async function loadRegisteredFaces() {
  try {
    const res = await fetch(`${API_BASE_URL}/face/all`);
    const result = await res.json();
    if (result.success && result.data) {
      labeledFaceDescriptors = result.data.map(f => 
        new faceapi.LabeledFaceDescriptors(
          f.label,
          f.descriptors.map(d => new Float32Array(d))
        )
      );
      document.getElementById('registered-count').textContent = labeledFaceDescriptors.length;
      console.log(`Loaded ${labeledFaceDescriptors.length} faces`);
    }
  } catch (e) {
    console.error('Load faces error:', e);
  }
}

async function startVideo() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: {} });
    video.srcObject = stream;
    await new Promise(resolve => {
      video.onloadedmetadata = () => {
        video.play();
        resolve();
      };
    });
    setTimeout(() => recognizeFaces(), 500);
  } catch (err) {
    console.error('Camera error:', err);
    statusDiv.textContent = '✗ Camera denied';
    statusDiv.style.color = 'red';
  }
}

async function recognizeFaces() {
  if (!isModelLoaded) return;

  const canvas = faceapi.createCanvasFromMedia(video);
  document.querySelector('.video-container').append(canvas);
  const displaySize = { width: video.videoWidth, height: video.videoHeight };
  faceapi.matchDimensions(canvas, displaySize);

  if (labeledFaceDescriptors.length > 0) {
    faceMatcher = new faceapi.FaceMatcher(labeledFaceDescriptors, 0.6);
  }

  setInterval(async () => {
    const detections = await faceapi
      .detectAllFaces(video, new faceapi.TinyFaceDetectorOptions())
      .withFaceLandmarks()
      .withFaceDescriptors()
      .withFaceExpressions();

    const resized = faceapi.resizeResults(detections, displaySize);
    canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);

    faceapi.draw.drawDetections(canvas, resized);
    faceapi.draw.drawFaceLandmarks(canvas, resized);

    document.getElementById('faces-detected').textContent = detections.length;

    if (detections.length > 0) {
      const d = detections[0];
      const expr = Object.entries(d.expressions).reduce((a,b) => a[1]>b[1]?a:b)[0];
      document.getElementById('detection-status').textContent = '✓ Face Detected';
      document.getElementById('confidence').textContent = (d.expressions[expr]*100).toFixed(1)+'%';
      document.getElementById('expression').textContent = expr.toUpperCase();

      if (faceMatcher) {
        const results = resized.map(det => faceMatcher.findBestMatch(det.descriptor));
        results.forEach((r, i) => {
          const box = resized[i].detection.box;
          new faceapi.draw.DrawBox(box, {
            label: r.label === 'unknown' ? 'Unknown' : r.label,
            boxColor: r.label === 'unknown' ? 'red' : 'green'
          }).draw(canvas);
          document.getElementById('recognized').textContent = r.label;
        });
      }
    } else {
      document.getElementById('detection-status').textContent = 'No Face';
      document.getElementById('confidence').textContent = '-';
      document.getElementById('expression').textContent = '-';
      document.getElementById('recognized').textContent = '-';
    }
  }, 100);
}

async function registerPerson() {
  const studentId = document.getElementById('student-id').value.trim();
  if (!studentId) { alert('Enter Student ID'); return; }
  if (!isModelLoaded) { alert('Models loading...'); return; }

  const detection = await faceapi
    .detectSingleFace(video, new faceapi.TinyFaceDetectorOptions())
    .withFaceLandmarks()
    .withFaceDescriptor();

  if (!detection) { alert('No face detected'); return; }

  const canvasSnap = document.createElement('canvas');
  canvasSnap.width = video.videoWidth;
  canvasSnap.height = video.videoHeight;
  canvasSnap.getContext('2d').drawImage(video, 0, 0);
  const imageData = canvasSnap.toDataURL('image/jpeg', 0.8);

  try {
    const resp = await fetch(`${API_BASE_URL}/face/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        data: [{
          label: studentId,
          descriptors: [Array.from(detection.descriptor)],
          image_data: imageData
        }]
      })
    });
    const result = await resp.json();
    if (result.success) {
      alert('✓ Registered!');
      await loadRegisteredFaces();
      document.getElementById('student-id').value = '';
    }
  } catch (e) {
    alert('✗ Backend error');
    console.error(e);
  }
}

window.addEventListener('load', loadModels);