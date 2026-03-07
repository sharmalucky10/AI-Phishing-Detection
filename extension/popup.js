const API_URL = 'http://127.0.0.1:5000';

document.addEventListener('DOMContentLoaded', function() {

  document.getElementById('analyzeBtn').addEventListener('click', analyzeText);
  document.getElementById('clearBtn').addEventListener('click', clearInput);
  document.getElementById('clearHistoryBtn').addEventListener('click', clearHistory);
  document.getElementById('scanPageBtn').addEventListener('click', scanPage);

  document.querySelectorAll('.tab').forEach(function(tab) {
    tab.addEventListener('click', function() {
      document.querySelectorAll('.tab').forEach(function(t) { t.classList.remove('active'); });
      document.querySelectorAll('.tab-panel').forEach(function(p) { p.classList.remove('active'); });
      tab.classList.add('active');
      document.getElementById('tab-' + tab.getAttribute('data-tab')).classList.add('active');
      if (tab.getAttribute('data-tab') === 'history') loadHistory();
    });
  });

  checkAPIStatus();
  loadHistory();
  loadPageURL();
});

function checkAPIStatus() {
  var dot = document.getElementById('statusDot');
  fetch(API_URL + '/')
    .then(function(r) {
      dot.style.background = '#48bb78';
      dot.style.boxShadow = '0 0 6px #48bb78';
    })
    .catch(function() {
      dot.style.background = '#fc8181';
      dot.style.boxShadow = '0 0 6px #fc8181';
    });
}

function analyzeText() {
  var text = document.getElementById('emailText').value.trim();
  document.getElementById('errorMsg').classList.remove('show');
  document.getElementById('resultCard').classList.remove('show');

  if (!text) {
    document.getElementById('errorMsg').textContent = 'Please paste some text first!';
    document.getElementById('errorMsg').classList.add('show');
    return;
  }

  document.getElementById('loader').classList.add('show');
  document.getElementById('analyzeBtn').disabled = true;
  document.getElementById('analyzeBtn').textContent = 'Analyzing...';

  fetch(API_URL + '/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: text })
  })
  .then(function(response) { return response.json(); })
  .then(function(data) {
    document.getElementById('loader').classList.remove('show');
    document.getElementById('analyzeBtn').disabled = false;
    document.getElementById('analyzeBtn').textContent = 'Analyze with AI';
    showResult(data);
    saveHistory(text, data);
  })
  .catch(function(error) {
    document.getElementById('loader').classList.remove('show');
    document.getElementById('analyzeBtn').disabled = false;
    document.getElementById('analyzeBtn').textContent = 'Analyze with AI';
    document.getElementById('errorMsg').textContent = 'ERROR: Make sure Flask server is running! Run: python app.py';
    document.getElementById('errorMsg').classList.add('show');
  });
}

function showResult(data) {
  var isPhishing = data.prediction === 'phishing';
  document.getElementById('resultCard').classList.add('show');
  document.getElementById('resultHeader').className = 'result-header ' + data.prediction;
  document.getElementById('resultIcon').textContent = isPhishing ? 'PHISHING DETECTED' : 'SAFE MESSAGE';
  document.getElementById('resultTitle').textContent = isPhishing ? 'Phishing Detected!' : 'Safe Message';
  document.getElementById('resultSubtitle').textContent = isPhishing ? 'Do NOT click any links!' : 'This message looks legitimate';
  document.getElementById('confidenceValue').textContent = data.confidence + '%';
  var badge = document.getElementById('riskBadge');
  badge.textContent = 'Risk: ' + data.risk_level;
  badge.className = 'risk-badge risk-' + data.risk_level;
  var factorsDiv = document.getElementById('riskFactors');
  factorsDiv.innerHTML = '';
  if (data.risk_factors && data.risk_factors.length > 0) {
    data.risk_factors.forEach(function(factor) {
      var div = document.createElement('div');
      div.className = 'risk-factor';
      div.textContent = factor;
      factorsDiv.appendChild(div);
    });
  } else {
    var div = document.createElement('div');
    div.className = 'risk-factor';
    div.textContent = isPhishing ? 'Suspicious content detected' : 'No suspicious patterns found';
    factorsDiv.appendChild(div);
  }
}

function clearInput() {
  document.getElementById('emailText').value = '';
  document.getElementById('resultCard').classList.remove('show');
  document.getElementById('errorMsg').classList.remove('show');
}

function scanPage() {
  document.getElementById('resultCardPage').classList.remove('show');
  document.getElementById('loaderPage').classList.add('show');
  chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
    chrome.scripting.executeScript({
      target: { tabId: tabs[0].id },
      func: function() { return document.body.innerText.substring(0, 3000); }
    }, function(results) {
      var pageText = results && results[0] ? results[0].result : '';
      document.getElementById('loaderPage').classList.remove('show');
      if (!pageText || pageText.length < 10) return;
      fetch(API_URL + '/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: pageText })
      })
      .then(function(r) { return r.json(); })
      .then(function(data) {
        var isPhishing = data.prediction === 'phishing';
        document.getElementById('resultCardPage').classList.add('show');
        document.getElementById('resultHeaderPage').className = 'result-header ' + data.prediction;
        document.getElementById('resultIconPage').textContent = isPhishing ? 'PHISHING!' : 'SAFE';
        document.getElementById('resultTitlePage').textContent = isPhishing ? 'Phishing Detected!' : 'Safe Page';
        document.getElementById('resultSubtitlePage').textContent = isPhishing ? 'Suspicious page!' : 'Page appears safe';
        document.getElementById('confidenceValuePage').textContent = data.confidence + '%';
        var badge = document.getElementById('riskBadgePage');
        badge.textContent = 'Risk: ' + data.risk_level;
        badge.className = 'risk-badge risk-' + data.risk_level;
      }).catch(function() {});
    });
  });
}

function loadPageURL() {
  try {
    chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
      if (tabs && tabs[0] && tabs[0].url) {
        document.getElementById('pageUrl').textContent = 'Page: ' + tabs[0].url.substring(0, 55);
      }
    });
  } catch(e) {}
}

function saveHistory(text, data) {
  try {
    var history = JSON.parse(localStorage.getItem('ph_history') || '[]');
    history.unshift({ text: text.substring(0, 55), prediction: data.prediction, confidence: data.confidence, time: new Date().toLocaleTimeString() });
    if (history.length > 10) history.pop();
    localStorage.setItem('ph_history', JSON.stringify(history));
  } catch(e) {}
}

function loadHistory() {
  try {
    var history = JSON.parse(localStorage.getItem('ph_history') || '[]');
    var div = document.getElementById('historyList');
    div.innerHTML = '';
    if (history.length === 0) {
      div.innerHTML = '<div class="empty-state"><div class="empty-icon">📭</div><div>No scans yet!</div></div>';
      return;
    }
    history.forEach(function(item) {
      var el = document.createElement('div');
      el.className = 'history-item';
      el.innerHTML = '<div class="history-dot ' + item.prediction + '"></div><div class="history-text">' + item.text + '</div><div><div class="history-label ' + item.prediction + '">' + item.prediction.toUpperCase() + '</div><div style="font-size:9px;color:#4a5568;">' + item.time + '</div></div>';
      div.appendChild(el);
    });
  } catch(e) {}
}

function clearHistory() {
  localStorage.removeItem('ph_history');
  loadHistory();
}
