/**
 * Real Estate WhatsApp Marketing Platform • Frontend Application Logic
 * Modular ES6 with Real-Time SSE live synchronization
 */

const state = {
  stats: {},
  leads: [],
  projects: [],
  campaigns: [],
  logs: [],
  activeProjectId: 1,
  selectedMedia: 'IMAGE',
  leadFilter: 'ALL',
  leadSearch: '',
  sseConnected: false,
};

// ---------------- DOM Elements ---------------- //
const el = {
  sseStatusDot: document.getElementById('sseStatusDot'),
  sseStatusText: document.getElementById('sseStatusText'),
  metaStatusPill: document.getElementById('metaStatusPill'),
  metaStatusDot: document.getElementById('metaStatusDot'),
  metaStatusText: document.getElementById('metaStatusText'),

  // KPIs
  kpiTotalLeads: document.getElementById('kpiTotalLeads'),
  kpiEligibleLeads: document.getElementById('kpiEligibleLeads'),
  kpiOptRate: document.getElementById('kpiOptRate'),
  kpiSent: document.getElementById('kpiSent'),
  kpiDelivered: document.getElementById('kpiDelivered'),
  kpiDeliveryRate: document.getElementById('kpiDeliveryRate'),
  kpiRead: document.getElementById('kpiRead'),
  kpiReadRate: document.getElementById('kpiReadRate'),
  kpiReplied: document.getElementById('kpiReplied'),
  kpiInterested: document.getElementById('kpiInterested'),
  kpiBooked: document.getElementById('kpiBooked'),

  // Simulator Elements
  phoneTime: document.getElementById('phoneTime'),
  simProjectName: document.getElementById('simProjectName'),
  simMediaContainer: document.getElementById('simMediaContainer'),
  simBodyText: document.getElementById('simBodyText'),
  simFooterText: document.getElementById('simFooterText'),
  simTimestamp: document.getElementById('simTimestamp'),
  simButtonsStack: document.getElementById('simButtonsStack'),

  // Studio Controls
  projectSelector: document.getElementById('projectSelector'),
  leadNameInput: document.getElementById('leadNameInput'),
  metaJsonPayload: document.getElementById('metaJsonPayload'),
  cliEquivalentCode: document.getElementById('cliEquivalentCode'),

  // Tables
  leadsTableBody: document.getElementById('leadsTableBody'),
  logsTableBody: document.getElementById('logsTableBody'),
  campaignsList: document.getElementById('campaignsList'),

  // Console
  consoleOutput: document.getElementById('consoleOutput'),

  // Modals
  addLeadModal: document.getElementById('addLeadModal'),
  sendTestModal: document.getElementById('sendTestModal'),
  verifyCredsModal: document.getElementById('verifyCredsModal'),
};

// ---------------- Initialization ---------------- //

document.addEventListener('DOMContentLoaded', async () => {
  setupTabs();
  setupPhoneClock();
  initSSE();
  await loadInitialData();
  setupEventListeners();
  checkMetaApiHealth();
});

function setupPhoneClock() {
  const updateClock = () => {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const mins = String(now.getMinutes()).padStart(2, '0');
    if (el.phoneTime) el.phoneTime.textContent = `${hours}:${mins}`;
    if (el.simTimestamp) el.simTimestamp.textContent = `${hours}:${mins}`;
  };
  updateClock();
  setInterval(updateClock, 10000);
}

function setupTabs() {
  const tabBtns = document.querySelectorAll('.tab-btn');
  tabBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      tabBtns.forEach((b) => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach((c) => c.classList.remove('active'));

      btn.classList.add('active');
      const targetId = btn.getAttribute('data-tab');
      const targetEl = document.getElementById(targetId);
      if (targetEl) targetEl.classList.add('active');
    });
  });
}

// ---------------- Real-Time Server-Sent Events (SSE) ---------------- //

function initSSE() {
  const eventSource = new EventSource('/api/events');

  eventSource.onopen = () => {
    state.sseConnected = true;
    if (el.sseStatusDot) {
      el.sseStatusDot.className = 'status-indicator pulse';
      el.sseStatusText.textContent = 'Live Sync Active (SSE)';
    }
  };

  eventSource.onerror = () => {
    state.sseConnected = false;
    if (el.sseStatusDot) {
      el.sseStatusDot.className = 'status-indicator warning';
      el.sseStatusText.textContent = 'Sync Reconnecting...';
    }
  };

  eventSource.addEventListener('ping', () => {});

  eventSource.addEventListener('stats_updated', (e) => {
    const data = JSON.parse(e.data);
    updateStatsUI(data);
  });

  eventSource.addEventListener('lead_updated', async () => {
    await fetchLeads();
    await fetchStats();
  });

  eventSource.addEventListener('message_sent', async (e) => {
    const payload = JSON.parse(e.data);
    showToast(`Message dispatched to ${payload.phone}!`, 'success');
    await fetchLogs();
    await fetchStats();
  });

  eventSource.addEventListener('message_status_updated', async (e) => {
    const payload = JSON.parse(e.data);
    showToast(`Message ${payload.status.toUpperCase()} (${payload.recipient || 'lead'})`, 'info');
    await fetchLogs();
    await fetchStats();
  });

  eventSource.addEventListener('inbound_message', (e) => {
    const payload = JSON.parse(e.data);
    showToast(`Inbound message from ${payload.phone}: "${payload.text}"`, 'info');
    appendSimulatorInbound(payload.text);
  });

  eventSource.addEventListener('campaign_completed', async (e) => {
    const payload = JSON.parse(e.data);
    showToast(`Campaign completed! Sent: ${payload.result?.sent || 0}`, 'success');
    await fetchCampaigns();
    await fetchLogs();
    await fetchStats();
  });

  eventSource.addEventListener('script_executed', (e) => {
    const payload = JSON.parse(e.data);
    showToast(`Script executed: ${payload.command}`, payload.code === 0 ? 'success' : 'error');
  });
}

// ---------------- Data Fetching ---------------- //

async function loadInitialData() {
  await Promise.all([
    fetchStats(),
    fetchProjects(),
    fetchLeads(),
    fetchCampaigns(),
    fetchLogs(),
  ]);
  await updateTemplatePreview();
}

async function fetchStats() {
  try {
    const res = await fetch('/api/stats');
    if (!res.ok) return;
    const data = await res.json();
    state.stats = data;
    updateStatsUI(data);
  } catch (err) {
    console.error('Failed to fetch stats:', err);
  }
}

function updateStatsUI(stats) {
  if (el.kpiTotalLeads) el.kpiTotalLeads.textContent = stats.total_leads || 0;
  if (el.kpiEligibleLeads) el.kpiEligibleLeads.textContent = stats.eligible_leads || 0;
  if (el.kpiOptRate) {
    const optRate = stats.total_leads > 0 ? Math.round((stats.eligible_leads / stats.total_leads) * 100) : 0;
    el.kpiOptRate.textContent = `${optRate}% consent`;
  }
  if (el.kpiSent) el.kpiSent.textContent = stats.sent || 0;
  if (el.kpiDelivered) el.kpiDelivered.textContent = stats.delivered || 0;
  if (el.kpiDeliveryRate) el.kpiDeliveryRate.textContent = `${stats.delivery_rate || 0}%`;
  if (el.kpiRead) el.kpiRead.textContent = stats.read || 0;
  if (el.kpiReadRate) el.kpiReadRate.textContent = `${stats.read_rate || 0}%`;
  if (el.kpiReplied) el.kpiReplied.textContent = stats.replied || 0;
  if (el.kpiInterested) el.kpiInterested.textContent = stats.interested || 0;
  if (el.kpiBooked) el.kpiBooked.textContent = stats.booked || 0;
}

async function fetchProjects() {
  try {
    const res = await fetch('/api/projects');
    if (!res.ok) return;
    state.projects = await res.json();

    if (el.projectSelector) {
      el.projectSelector.innerHTML = state.projects
        .map((p) => `<option value="${p.id}">${p.name} (${p.location})</option>`)
        .join('');
    }

    const campProj = document.getElementById('campaignProject');
    if (campProj) {
      campProj.innerHTML = state.projects
        .map((p) => `<option value="${p.id}">${p.name}</option>`)
        .join('');
    }
  } catch (err) {
    console.error('Failed to fetch projects:', err);
  }
}

async function fetchLeads() {
  try {
    let url = '/api/leads';
    const params = [];
    if (state.leadFilter === 'OPTED_IN') params.push('opt_in=true');
    if (state.leadFilter === 'OPTED_OUT') params.push('opt_in=false');
    if (state.leadSearch) params.push(`search=${encodeURIComponent(state.leadSearch)}`);
    if (params.length) url += '?' + params.join('&');

    const res = await fetch(url);
    if (!res.ok) return;
    state.leads = await res.json();
    renderLeadsTable(state.leads);
  } catch (err) {
    console.error('Failed to fetch leads:', err);
  }
}

function renderLeadsTable(leads) {
  if (!el.leadsTableBody) return;
  if (leads.length === 0) {
    el.leadsTableBody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding: 30px; color: var(--text-dim);">No leads found matching criteria.</td></tr>`;
    return;
  }

  el.leadsTableBody.innerHTML = leads
    .map((lead) => {
      let badgeClass = 'unverified';
      let badgeText = '⚠ UNVERIFIED';

      if (lead.whatsapp_opt_in === 1 && !lead.opt_out_timestamp) {
        badgeClass = 'opted-in';
        badgeText = '✔ OPTED_IN';
      } else if (lead.opt_out_timestamp) {
        badgeClass = 'opted-out';
        badgeText = '✖ OPTED_OUT';
      }

      const isOptedIn = lead.whatsapp_opt_in === 1 && !lead.opt_out_timestamp;

      return `
      <tr>
        <td>
          <div style="font-weight: 700; color: #fff;">${escapeHtml(lead.name)}</div>
          <div style="font-size: 11px; color: var(--text-dim);">${escapeHtml(lead.source || 'Website')}</div>
        </td>
        <td><code style="font-family: var(--font-mono); color: var(--accent-cyan);">+${escapeHtml(lead.phone)}</code></td>
        <td>
          <div>${escapeHtml(lead.city || 'Chennai')}</div>
          <div style="font-size: 11px; color: var(--text-muted);">${escapeHtml(lead.project_interest || 'Green Valley')}</div>
        </td>
        <td>
          <span class="badge-consent ${badgeClass}">${badgeText}</span>
          ${lead.opt_in_timestamp ? `<div style="font-size: 10px; color: var(--text-dim); margin-top: 2px;">${lead.opt_in_timestamp.split('T')[0]}</div>` : ''}
        </td>
        <td>
          <div style="display: flex; gap: 6px;">
            <button class="btn btn-secondary btn-sm" onclick="openSendTestModal('${lead.phone}', '${escapeHtml(lead.name)}')">
              💬 Send Template
            </button>
            <button class="btn ${isOptedIn ? 'btn-danger-outline' : 'btn-outline-emerald'} btn-sm" onclick="toggleLeadOptIn('${lead.phone}', ${!isOptedIn})">
              ${isOptedIn ? 'Revoke Opt-In' : 'Grant Opt-In'}
            </button>
          </div>
        </td>
      </tr>
    `;
    })
    .join('');
}

async function toggleLeadOptIn(phone, targetOptIn) {
  try {
    const res = await fetch('/api/leads/toggle-opt-in', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone, opt_in: targetOptIn }),
    });
    const data = await res.json();
    if (data.success) {
      showToast(`Consent updated for +${phone}`, 'success');
      await fetchLeads();
      await fetchStats();
    }
  } catch (err) {
    showToast('Failed to toggle opt-in', 'error');
  }
}

async function fetchCampaigns() {
  try {
    const res = await fetch('/api/campaigns');
    if (!res.ok) return;
    state.campaigns = await res.json();
    renderCampaigns(state.campaigns);
  } catch (err) {
    console.error('Failed to fetch campaigns:', err);
  }
}

function renderCampaigns(campaigns) {
  if (!el.campaignsList) return;
  if (campaigns.length === 0) {
    el.campaignsList.innerHTML = `<div style="text-align:center; padding: 20px; color: var(--text-dim);">No marketing campaigns executed yet.</div>`;
    return;
  }

  el.campaignsList.innerHTML = campaigns
    .slice(0, 5)
    .map(
      (c) => `
    <div style="background: var(--bg-primary); border: 1px solid var(--border-subtle); border-radius: var(--radius-sm); padding: 12px; margin-bottom: 8px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
        <div style="font-weight: 700; color: #fff;">${escapeHtml(c.name)}</div>
        <span class="status-tag ${c.status === 'COMPLETED' ? 'delivered' : 'sent'}">${c.status}</span>
      </div>
      <div style="display: flex; gap: 14px; font-size: 11px; color: var(--text-muted); font-family: var(--font-mono);">
        <span>Total: <b>${c.total_leads}</b></span>
        <span>Eligible: <b>${c.eligible}</b></span>
        <span>Sent: <b style="color: var(--accent-mint);">${c.sent}</b></span>
        <span>Delivered: <b style="color: var(--accent-emerald);">${c.delivered}</b></span>
        <span>Read: <b style="color: var(--accent-purple);">${c.read}</b></span>
      </div>
    </div>
  `
    )
    .join('');
}

async function fetchLogs() {
  try {
    const res = await fetch('/api/logs?limit=25');
    if (!res.ok) return;
    state.logs = await res.json();
    renderLogsTable(state.logs);
  } catch (err) {
    console.error('Failed to fetch logs:', err);
  }
}

function renderLogsTable(logs) {
  if (!el.logsTableBody) return;
  if (logs.length === 0) {
    el.logsTableBody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding: 30px; color: var(--text-dim);">No message logs recorded yet.</td></tr>`;
    return;
  }

  el.logsTableBody.innerHTML = logs
    .map((log) => {
      const statusLower = (log.status || 'sent').toLowerCase();
      return `
      <tr>
        <td><code style="font-family: var(--font-mono); color: var(--accent-cyan);">+${escapeHtml(log.phone)}</code></td>
        <td>
          <span class="status-tag ${statusLower}">${escapeHtml(log.status)}</span>
          ${log.error_message ? `<div style="font-size: 10px; color: var(--accent-rose); margin-top: 2px;">${escapeHtml(log.error_message)}</div>` : ''}
        </td>
        <td style="font-size: 12px; color: var(--text-muted);">${escapeHtml(log.template_name || 'direct')}</td>
        <td><code style="font-size: 10px; color: var(--text-dim);">${escapeHtml(log.whatsapp_message_id || 'N/A')}</code></td>
        <td style="font-size: 11px; color: var(--text-dim);">${log.sent_at ? log.sent_at.split('.')[0].replace('T', ' ') : ''}</td>
      </tr>
    `;
    })
    .join('');
}

// ---------------- Simulator & Template Studio ---------------- //

async function updateTemplatePreview() {
  const projectId = el.projectSelector ? el.projectSelector.value : 1;
  const leadName = el.leadNameInput ? el.leadNameInput.value.trim() || 'Aravind Kumar' : 'Aravind Kumar';
  const mediaType = state.selectedMedia;

  try {
    const res = await fetch(`/api/templates/preview?project_id=${projectId}&lead_name=${encodeURIComponent(leadName)}&media_type=${mediaType}`);
    if (!res.ok) return;
    const data = await res.json();

    const project = state.projects.find((p) => String(p.id) === String(projectId)) || state.projects[0];
    if (project && el.simProjectName) {
      el.simProjectName.textContent = project.name;
    }

    // Render Media in Simulator
    if (el.simMediaContainer && project) {
      if (mediaType === 'IMAGE') {
        el.simMediaContainer.innerHTML = `
          <div class="wa-media-preview">
            <span class="media-tag-overlay">🖼️ HERO IMAGE</span>
            <img src="${project.hero_image_url}" alt="${project.name}">
          </div>
        `;
      } else if (mediaType === 'VIDEO') {
        el.simMediaContainer.innerHTML = `
          <div class="wa-media-preview">
            <span class="media-tag-overlay">🎬 4K WALKTHROUGH</span>
            <video src="${project.walkthrough_video_url}" autoplay loop muted></video>
          </div>
        `;
      } else {
        el.simMediaContainer.innerHTML = `
          <div class="wa-doc-header">
            <span class="media-tag-overlay">📄 PDF BROCHURE</span>
            <div style="font-size: 32px;">📑</div>
            <div style="font-weight: 700; font-size: 12px;">${project.name} - Layout Map.pdf</div>
            <div style="font-size: 10px; color: var(--text-dim);">DTCP Approved • 2.4 MB</div>
          </div>
        `;
      }
    }

    // Render Text & Formatting
    if (el.simBodyText) {
      el.simBodyText.innerHTML = formatWhatsAppText(data.text_preview);
    }

    // Render Action Buttons
    if (el.simButtonsStack) {
      el.simButtonsStack.innerHTML = `
        <div class="wa-btn-cta" onclick="simulateBuyerClick('VIEW_LAYOUT', '🗺️ View Layout Plan')">
          🗺️ View Layout Plan
        </div>
        <div class="wa-btn-cta" onclick="simulateBuyerClick('BOOK_PLOT', '📍 Book a Plot (Priority Pass)')">
          📍 Book a Plot (Priority Pass)
        </div>
        <div class="wa-btn-cta" onclick="simulateBuyerClick('TALK_SALES', '📞 Talk to Sales Executive')">
          📞 Talk to Sales Executive
        </div>
        <div class="wa-btn-cta" style="color: var(--accent-rose); font-size: 11px;" onclick="simulateBuyerClick('STOP', 'Reply STOP to Unsubscribe')">
          🛑 Unsubscribe (Reply STOP)
        </div>
      `;
    }

    // Render Raw Payload
    if (el.metaJsonPayload) {
      el.metaJsonPayload.textContent = JSON.stringify(data.meta_cloud_api_payload, null, 2);
    }

    // Update CLI Equivalent Code
    if (el.cliEquivalentCode) {
      el.cliEquivalentCode.textContent = `python send_whatsapp.py --preview --project-id ${projectId} --media ${mediaType}`;
    }
  } catch (err) {
    console.error('Failed to update preview:', err);
  }
}

function formatWhatsAppText(text) {
  if (!text) return '';
  return text
    .replace(/\*([^\*]+)\*/g, '<b>$1</b>')
    .replace(/_([^_]+)_/g, '<i>$1</i>')
    .replace(/\n/g, '<br>');
}

function simulateBuyerClick(action, label) {
  showToast(`Simulated customer clicked: ${label}`, 'info');

  let reply = '';
  if (action === 'VIEW_LAYOUT') {
    reply = '🗺️ Here is your high-resolution layout map and brochure PDF: https://realestate-demo.example.com/layout.pdf';
  } else if (action === 'BOOK_PLOT') {
    reply = '📍 Reserve Your Plot: Opening booking reservation form: https://realestate-demo.example.com/book';
  } else if (action === 'TALK_SALES') {
    reply = '📞 Our senior real estate advisor will call you within 15 minutes.';
  } else if (action === 'STOP') {
    reply = '🛑 You have unsubscribed. Reply START anytime to reactivate.';
  }

  appendSimulatorInbound(label);
  setTimeout(() => {
    appendSimulatorAgentReply(reply);
  }, 600);
}

function appendSimulatorInbound(text) {
  const chatArea = document.querySelector('.wa-chat-area');
  if (!chatArea) return;

  const userBubble = document.createElement('div');
  userBubble.style.cssText = `
    align-self: flex-end;
    background: var(--wa-bubble-out);
    color: #fff;
    padding: 8px 12px;
    border-radius: var(--radius-md) 0 var(--radius-md) var(--radius-md);
    font-size: 12px;
    max-width: 80%;
    margin-top: 6px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.3);
  `;
  userBubble.textContent = text;
  chatArea.appendChild(userBubble);
  chatArea.scrollTop = chatArea.scrollHeight;
}

function appendSimulatorAgentReply(text) {
  const chatArea = document.querySelector('.wa-chat-area');
  if (!chatArea) return;

  const replyBubble = document.createElement('div');
  replyBubble.style.cssText = `
    align-self: flex-start;
    background: var(--wa-bubble-in);
    color: var(--text-main);
    padding: 8px 12px;
    border-radius: 0 var(--radius-md) var(--radius-md) var(--radius-md);
    font-size: 12px;
    max-width: 80%;
    margin-top: 6px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    box-shadow: 0 1px 3px rgba(0,0,0,0.3);
  `;
  replyBubble.textContent = text;
  chatArea.appendChild(replyBubble);
  chatArea.scrollTop = chatArea.scrollHeight;
}

// ---------------- Meta API Health & Credential Check ---------------- //

async function checkMetaApiHealth() {
  try {
    const res = await fetch('/api/whatsapp/verify');
    const data = await res.json();

    if (data.success) {
      if (el.metaStatusDot) el.metaStatusDot.className = 'status-indicator';
      if (el.metaStatusText) el.metaStatusText.textContent = `Meta API: Connected (${data.data?.display_phone_number || 'Live'})`;
    } else {
      if (el.metaStatusDot) el.metaStatusDot.className = 'status-indicator danger';
      if (el.metaStatusText) el.metaStatusText.textContent = 'Meta API: Check Config / Token';
    }
  } catch (err) {
    if (el.metaStatusDot) el.metaStatusDot.className = 'status-indicator danger';
    if (el.metaStatusText) el.metaStatusText.textContent = 'Meta API: Offline';
  }
}

async function runMetaCredentialVerification() {
  const outputEl = document.getElementById('verifyModalOutput');
  if (outputEl) {
    outputEl.textContent = 'Contacting Meta Graph API https://graph.facebook.com/v21.0/...';
  }

  try {
    const res = await fetch('/api/whatsapp/verify');
    const data = await res.json();

    if (outputEl) {
      if (data.success) {
        outputEl.innerHTML = `
          <div style="color: var(--accent-mint); font-weight: 700; margin-bottom: 8px;">✅ Connected to Meta WhatsApp Business Cloud API!</div>
          <div>• Display Phone Number: <b>${data.data?.display_phone_number}</b></div>
          <div>• Verified Name: <b>${data.data?.verified_name}</b></div>
          <div>• Status: <b>${data.data?.code_verification_status}</b></div>
          <div>• Quality Rating: <b>${data.data?.quality_rating}</b></div>
          <div>• Phone Number ID: <code>${data.data?.id}</code></div>
        `;
      } else {
        outputEl.innerHTML = `
          <div style="color: var(--accent-rose); font-weight: 700; margin-bottom: 8px;">❌ Credential Verification Failed:</div>
          <div>• Error: ${escapeHtml(data.message)}</div>
          ${data.diagnostic_hint ? `<div style="margin-top: 8px; color: var(--accent-amber);">💡 Tip: ${escapeHtml(data.diagnostic_hint)}</div>` : ''}
        `;
      }
    }
    await checkMetaApiHealth();
  } catch (err) {
    if (outputEl) outputEl.textContent = `Network Error: ${err.message}`;
  }
}

// ---------------- Campaign Launchpad ---------------- //

async function updateAudienceBreakdown() {
  const projId = document.getElementById('campaignProject')?.value || 1;
  const city = document.getElementById('campaignCity')?.value || 'All';

  try {
    const res = await fetch(`/api/campaigns/audience-preview?project_id=${projId}&city=${encodeURIComponent(city)}`);
    if (!res.ok) return;
    const data = await res.json();

    const poolEl = document.getElementById('campTotalPool');
    const eligEl = document.getElementById('campEligibleCount');
    const ineligEl = document.getElementById('campIneligibleCount');

    if (poolEl) poolEl.textContent = data.total_leads;
    if (eligEl) eligEl.textContent = data.eligible_count;
    if (ineligEl) ineligEl.textContent = data.ineligible_count;
  } catch (err) {
    console.error('Failed to preview audience:', err);
  }
}

async function handleLaunchCampaign(e) {
  e.preventDefault();
  const name = document.getElementById('campaignName').value.trim() || 'WhatsApp Launch Campaign';
  const projectId = parseInt(document.getElementById('campaignProject').value, 10);
  const city = document.getElementById('campaignCity').value;
  const mediaType = document.getElementById('campaignMediaType').value;
  const dryRun = document.getElementById('campaignDryRun').checked;
  const throttleSeconds = parseFloat(document.getElementById('campaignThrottle').value);

  const launchBtn = document.getElementById('launchCampaignBtn');
  if (launchBtn) {
    launchBtn.disabled = true;
    launchBtn.textContent = '🚀 Dispatching Campaign...';
  }

  try {
    const res = await fetch('/api/campaigns', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name,
        project_id: projectId,
        audience_city: city,
        media_type: mediaType,
        dry_run: dryRun,
        throttle_seconds: throttleSeconds,
      }),
    });
    const data = await res.json();

    if (data.success) {
      showToast(`Campaign launched! Sent: ${data.result.sent}, Skipped: ${data.result.ineligible_skipped}`, 'success');
      await fetchCampaigns();
      await fetchStats();
      await fetchLogs();
    } else {
      showToast(`Campaign error: ${data.message || 'Unknown error'}`, 'error');
    }
  } catch (err) {
    showToast('Network error launching campaign', 'error');
  } finally {
    if (launchBtn) {
      launchBtn.disabled = false;
      launchBtn.textContent = '🚀 Launch WhatsApp Campaign';
    }
  }
}

// ---------------- CLI Script Console Runner ---------------- //

async function runCliCommand(args) {
  if (el.consoleOutput) {
    el.consoleOutput.textContent += `\n$ python send_whatsapp.py ${args}\nRunning...`;
    el.consoleOutput.scrollTop = el.consoleOutput.scrollHeight;
  }

  try {
    const res = await fetch('/api/whatsapp/run-script', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command_args: args }),
    });
    const data = await res.json();

    if (el.consoleOutput) {
      el.consoleOutput.textContent += `\n${data.output || data.error || 'Command finished.'}\n`;
      el.consoleOutput.scrollTop = el.consoleOutput.scrollHeight;
    }
    showToast(`Finished: python send_whatsapp.py ${args}`, data.success ? 'success' : 'error');
  } catch (err) {
    if (el.consoleOutput) {
      el.consoleOutput.textContent += `\nError executing CLI command: ${err.message}\n`;
    }
  }
}

// ---------------- Event Listeners ---------------- //

function setupEventListeners() {
  // Media Type Toggles
  const mediaBtns = document.querySelectorAll('.media-toggle-btn');
  mediaBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      mediaBtns.forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      state.selectedMedia = btn.getAttribute('data-media');
      updateTemplatePreview();
    });
  });

  // Project selector change
  if (el.projectSelector) {
    el.projectSelector.addEventListener('change', () => {
      state.activeProjectId = parseInt(el.projectSelector.value, 10);
      updateTemplatePreview();
    });
  }

  // Lead name input change
  if (el.leadNameInput) {
    el.leadNameInput.addEventListener('input', () => {
      updateTemplatePreview();
    });
  }

  // Copy JSON Button
  const copyBtn = document.getElementById('copyPayloadBtn');
  if (copyBtn) {
    copyBtn.addEventListener('click', () => {
      if (el.metaJsonPayload) {
        navigator.clipboard.writeText(el.metaJsonPayload.textContent);
        showToast('Meta Cloud API payload copied to clipboard!', 'success');
      }
    });
  }

  // Lead Filter Buttons
  const filterBtns = document.querySelectorAll('.filter-btn');
  filterBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      filterBtns.forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      state.leadFilter = btn.getAttribute('data-filter');
      fetchLeads();
    });
  });

  // Lead Search Input
  const leadSearchInput = document.getElementById('leadSearchInput');
  if (leadSearchInput) {
    let timeout = null;
    leadSearchInput.addEventListener('input', (e) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => {
        state.leadSearch = e.target.value.trim();
        fetchLeads();
      }, 300);
    });
  }

  // Campaign Form Audience Preview Updates
  const campCity = document.getElementById('campaignCity');
  const campProj = document.getElementById('campaignProject');
  if (campCity) campCity.addEventListener('change', updateAudienceBreakdown);
  if (campProj) campProj.addEventListener('change', updateAudienceBreakdown);

  // Campaign Form Submission
  const campForm = document.getElementById('campaignForm');
  if (campForm) {
    campForm.addEventListener('submit', handleLaunchCampaign);
  }

  // Add Lead Form
  const addLeadForm = document.getElementById('addLeadForm');
  if (addLeadForm) {
    addLeadForm.addEventListener('submit', handleAddLead);
  }

  // Send Single Message Form
  const sendTestForm = document.getElementById('sendTestForm');
  if (sendTestForm) {
    sendTestForm.addEventListener('submit', handleSendSingleMessage);
  }

  // Audience preview on load
  updateAudienceBreakdown();
}

// ---------------- Modal Handlers ---------------- //

function openModal(modalId) {
  const m = document.getElementById(modalId);
  if (m) m.classList.add('open');
}

function closeModal(modalId) {
  const m = document.getElementById(modalId);
  if (m) m.classList.remove('open');
}

function openSendTestModal(phone = '', name = '') {
  const phoneInput = document.getElementById('testPhone');
  const nameInput = document.getElementById('testLeadName');
  if (phoneInput && phone) phoneInput.value = phone;
  if (nameInput && name) nameInput.value = name;
  openModal('sendTestModal');
}

async function handleAddLead(e) {
  e.preventDefault();
  const name = document.getElementById('newLeadName').value.trim();
  const phone = document.getElementById('newLeadPhone').value.trim();
  const email = document.getElementById('newLeadEmail').value.trim();
  const city = document.getElementById('newLeadCity').value;
  const project = document.getElementById('newLeadProject').value;
  const optIn = document.getElementById('newLeadOptIn').checked;
  const source = document.getElementById('newLeadSource').value.trim() || 'Admin Dashboard';

  try {
    const res = await fetch('/api/leads', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name,
        phone,
        email,
        city,
        project_interest: project,
        whatsapp_opt_in: optIn,
        source,
      }),
    });
    const data = await res.json();

    if (data.success) {
      showToast(`Lead ${name} successfully added!`, 'success');
      closeModal('addLeadModal');
      document.getElementById('addLeadForm').reset();
      await fetchLeads();
      await fetchStats();
    }
  } catch (err) {
    showToast('Failed to add lead', 'error');
  }
}

async function handleSendSingleMessage(e) {
  e.preventDefault();
  const phone = document.getElementById('testPhone').value.trim();
  const leadName = document.getElementById('testLeadName').value.trim();
  const projectId = parseInt(document.getElementById('testProject').value, 10);
  const mediaType = document.getElementById('testMediaType').value;
  const mode = document.getElementById('testSendMode').value;
  const dryRun = document.getElementById('testDryRun').checked;

  const isDirect = mode === 'DIRECT';
  const customTmpl = mode === 'HELLO_WORLD' ? 'hello_world' : null;

  try {
    const res = await fetch('/api/whatsapp/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        phone,
        lead_name: leadName,
        project_id: projectId,
        media_type: mediaType,
        dry_run: dryRun,
        direct: isDirect,
        template_name: customTmpl,
      }),
    });
    const data = await res.json();

    if (data.success) {
      showToast(`Dispatched to ${phone}!`, 'success');
      closeModal('sendTestModal');
      await fetchLogs();
      await fetchStats();
    } else {
      showToast(`Dispatch failed: ${data.message}`, 'error');
      if (data.diagnostic_hint) {
        showToast(data.diagnostic_hint, 'info');
      }
    }
  } catch (err) {
    showToast('Network error during dispatch', 'error');
  }
}

// ---------------- Toast Notifications ---------------- //

function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <span style="font-size: 16px;">${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</span>
    <span>${escapeHtml(message)}</span>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
