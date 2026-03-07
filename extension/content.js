/**
 * ============================================================
 *  AI Phishing Detector - Content Script
 *  Capstone Project | BCA Final Year
 *  File: content.js
 * ============================================================
 *
 *  This script runs on every webpage and:
 *  1. Listens for messages from the popup
 *  2. Extracts visible page text when requested
 *  3. Highlights suspicious links on the page
 */

const PHISHING_API = 'http://127.0.0.1:5000/predict';

// Suspicious TLD patterns
const SUSPICIOUS_TLDS = /\.(xyz|tk|ml|ga|cf|gq|pw|top|click|link|info|biz|work|zip|review|country|kim|science|party|trade|date)\b/i;

// ─────────────────────────────────────────────────────────────
// LISTEN FOR MESSAGES FROM POPUP
// ─────────────────────────────────────────────────────────────

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getPageText') {
    const text = extractPageText();
    sendResponse({ text });
  }
  if (request.action === 'highlightLinks') {
    highlightSuspiciousLinks();
    sendResponse({ done: true });
  }
  return true; // Keep message channel open for async
});


// ─────────────────────────────────────────────────────────────
// EXTRACT PAGE TEXT
// ─────────────────────────────────────────────────────────────

function extractPageText() {
  // Get all visible text, prioritizing email content areas
  const selectors = [
    'article', 'main', '.email-body', '.message-body',
    '[role="main"]', '.content', 'body'
  ];

  for (const selector of selectors) {
    const el = document.querySelector(selector);
    if (el && el.innerText.trim().length > 50) {
      return el.innerText.trim().substring(0, 3000);
    }
  }
  return document.body.innerText.trim().substring(0, 3000);
}


// ─────────────────────────────────────────────────────────────
// HIGHLIGHT SUSPICIOUS LINKS
// ─────────────────────────────────────────────────────────────

function highlightSuspiciousLinks() {
  const links = document.querySelectorAll('a[href]');
  let count   = 0;

  links.forEach(link => {
    const href = link.href || '';

    const isSuspicious = (
      SUSPICIOUS_TLDS.test(href) ||
      /https?:\/\/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/.test(href) || // IP-based URL
      (href.includes('redirect') && !href.includes(window.location.hostname))
    );

    if (isSuspicious) {
      link.style.outline      = '2px solid #fc8181';
      link.style.outlineOffset = '2px';
      link.title              = '⚠️ AI Phishing Detector: This link looks suspicious!';
      count++;
    }
  });

  return count;
}


// ─────────────────────────────────────────────────────────────
// AUTO-SCAN ON PAGE LOAD (optional, lightweight check)
// ─────────────────────────────────────────────────────────────

function autoScanPage() {
  // Only scan if page has email-like patterns
  const pageText  = document.body.innerText || '';
  const hasEmailPatterns = (
    /\b(urgent|verify|suspended|click here|confirm account)\b/i.test(pageText) &&
    /http[s]?:\/\//i.test(pageText)
  );

  if (hasEmailPatterns) {
    // Highlight suspicious links silently
    const count = highlightSuspiciousLinks();
    if (count > 0) {
      console.log(`[AI Phishing Detector] ⚠️ Found ${count} suspicious link(s) on this page.`);
    }
  }
}

// Run auto-scan when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', autoScanPage);
} else {
  autoScanPage();
}
