/**
 * app/static/js/app.js — Dynamic DOM Wiring & Interactive Application Controller
 * Safe DOM Manipulation & Zero Static Dummy Data: All views query /api/v1 REST endpoints.
 * WCAG 2.1 AA Compliant & Secure (Zero unescaped innerHTML injection sinks).
 */

document.addEventListener('DOMContentLoaded', () => {
  const page = document.body.dataset.page || '';

  // Initialize view specific logic
  if (page === 'dashboard' || document.getElementById('dashboard-view')) {
    initDashboard();
  } else if (page === 'trajectories' || document.getElementById('trajectories-view')) {
    initTrajectories();
  } else if (page === 'datasets' || document.getElementById('datasets-view')) {
    initDatasets();
  } else if (page === 'new-run' || document.getElementById('new-run-view')) {
    initNewRun();
  } else if (page === 'annotations' || document.getElementById('annotations-view')) {
    initAnnotations();
  }

  // Global Health Probe status check
  checkSystemHealth();
});

async function checkSystemHealth() {
  const indicator = document.getElementById('health-indicator');
  if (!indicator) return;
  try {
    const health = await ApiClient.getHealth();
    indicator.textContent = health.status === 'healthy' ? 'System Operational' : 'Degraded';
    indicator.className = health.status === 'healthy' ? 'status-badge status-healthy' : 'status-badge status-warning';
  } catch (e) {
    indicator.textContent = 'Backend Offline';
    indicator.className = 'status-badge status-error';
  }
}

/* -------------------------------------------------------------------------- */
/* Dashboard Page Logic                                                       */
/* -------------------------------------------------------------------------- */
async function initDashboard() {
  const leaderboardBody = document.getElementById('agent-leaderboard-body');
  const runsTableBody = document.getElementById('recent-runs-body');

  try {
    // 1. Load Telemetry Metrics
    const telemetry = await ApiClient.getCollaborationTelemetry();
    updateText('metric-total-cards', telemetry.total_cards);
    updateText('metric-precision-rate', `${telemetry.precision_rate}%`);
    updateText('metric-avg-latency', `${telemetry.avg_latency_ms} ms`);
    updateText('metric-consensus-rate', `${telemetry.consensus_rate}%`);

    // 2. Load Agent Leaderboard
    const agentsData = await ApiClient.getAgents();
    if (leaderboardBody) {
      leaderboardBody.replaceChildren();
      if (agentsData.items.length === 0) {
        const tr = document.createElement('tr');
        const td = document.createElement('td');
        td.colSpan = 6;
        td.className = 'empty-state';
        td.textContent = 'No agents registered yet.';
        tr.appendChild(td);
        leaderboardBody.appendChild(tr);
      } else {
        agentsData.items.forEach(agent => {
          const tr = document.createElement('tr');

          // Name
          const tdName = document.createElement('td');
          const strongName = document.createElement('strong');
          strongName.textContent = agent.name;
          tdName.appendChild(strongName);
          tr.appendChild(tdName);

          // Model
          const tdModel = document.createElement('td');
          const codeModel = document.createElement('code');
          codeModel.textContent = agent.model;
          tdModel.appendChild(codeModel);
          tr.appendChild(tdModel);

          // Pass Rate
          const tdPass = document.createElement('td');
          const badgePass = document.createElement('span');
          badgePass.className = `badge ${agent.pass_rate >= 90 ? 'badge-success' : 'badge-warning'}`;
          badgePass.textContent = `${agent.pass_rate}%`;
          tdPass.appendChild(badgePass);
          tr.appendChild(tdPass);

          // Latency
          const tdLatency = document.createElement('td');
          tdLatency.textContent = `${agent.latency_p95} ms`;
          tr.appendChild(tdLatency);

          // Runs Evaluated
          const tdRuns = document.createElement('td');
          tdRuns.textContent = String(agent.runs_evaluated);
          tr.appendChild(tdRuns);

          // Status
          const tdStatus = document.createElement('td');
          const pillStatus = document.createElement('span');
          pillStatus.className = `status-pill status-${agent.status}`;
          pillStatus.textContent = agent.status;
          tdStatus.appendChild(pillStatus);
          tr.appendChild(tdStatus);

          leaderboardBody.appendChild(tr);
        });
      }
    }

    // 3. Load Recent Runs
    const runsData = await ApiClient.getRuns();
    if (runsTableBody) {
      runsTableBody.replaceChildren();
      if (runsData.items.length === 0) {
        const tr = document.createElement('tr');
        const td = document.createElement('td');
        td.colSpan = 6;
        td.className = 'empty-state';
        td.textContent = 'No evaluation runs recorded.';
        tr.appendChild(td);
        runsTableBody.appendChild(tr);
      } else {
        runsData.items.forEach(run => {
          const tr = document.createElement('tr');

          // Run Name Link
          const tdName = document.createElement('td');
          const link = document.createElement('a');
          link.href = `/trajectories.html?run_id=${encodeURIComponent(run.id)}`;
          const strong = document.createElement('strong');
          strong.textContent = run.name;
          link.appendChild(strong);
          tdName.appendChild(link);
          tr.appendChild(tdName);

          // Mode
          const tdMode = document.createElement('td');
          const tagMode = document.createElement('span');
          tagMode.className = `tag-mode tag-${run.mode}`;
          tagMode.textContent = run.mode;
          tdMode.appendChild(tagMode);
          tr.appendChild(tdMode);

          // Status
          const tdStatus = document.createElement('td');
          const pillStatus = document.createElement('span');
          pillStatus.className = `status-pill status-${run.status}`;
          pillStatus.textContent = run.status;
          tdStatus.appendChild(pillStatus);
          tr.appendChild(tdStatus);

          // Pass Rate
          const tdPass = document.createElement('td');
          tdPass.textContent = `${run.pass_rate}%`;
          tr.appendChild(tdPass);

          // Progress
          const tdProg = document.createElement('td');
          tdProg.textContent = `${run.completed_steps} / ${run.total_steps}`;
          tr.appendChild(tdProg);

          // Date
          const tdDate = document.createElement('td');
          tdDate.textContent = new Date(run.created_at).toLocaleDateString();
          tr.appendChild(tdDate);

          runsTableBody.appendChild(tr);
        });
      }
    }
  } catch (err) {
    console.error('Error populating dashboard:', err);
  }
}

/* -------------------------------------------------------------------------- */
/* Trajectories Page Logic                                                    */
/* -------------------------------------------------------------------------- */
async function initTrajectories() {
  const urlParams = new URLSearchParams(window.location.search);
  const initialRunId = urlParams.get('run_id') || '';
  const trajectoryListContainer = document.getElementById('trajectory-list');
  const traceDetailContainer = document.getElementById('trace-detail-view');
  const searchInput = document.getElementById('filter-search');
  const statusSelect = document.getElementById('filter-status');

  async function loadTrajectories() {
    const filters = {};
    if (initialRunId) filters.run_id = initialRunId;
    if (statusSelect && statusSelect.value) filters.status = statusSelect.value;

    const data = await ApiClient.getTrajectories(filters);
    if (!trajectoryListContainer) return;

    trajectoryListContainer.replaceChildren();
    if (data.items.length === 0) {
      const empty = document.createElement('div');
      empty.className = 'empty-state';
      empty.textContent = 'No trajectories matching filter criteria.';
      trajectoryListContainer.appendChild(empty);
      return;
    }

    data.items.forEach((trj, idx) => {
      const card = document.createElement('div');
      card.className = `trajectory-item ${idx === 0 ? 'active' : ''}`;
      card.dataset.id = trj.id;

      const header = document.createElement('div');
      header.className = 'trj-header';

      const trjIdSpan = document.createElement('span');
      trjIdSpan.className = 'trj-id';
      trjIdSpan.textContent = trj.id;

      const statusSpan = document.createElement('span');
      statusSpan.className = `status-pill status-${trj.status}`;
      statusSpan.textContent = trj.status;

      header.appendChild(trjIdSpan);
      header.appendChild(statusSpan);

      const agentDiv = document.createElement('div');
      agentDiv.className = 'trj-agent';
      agentDiv.textContent = trj.agent_name;

      const metaDiv = document.createElement('div');
      metaDiv.className = 'trj-meta';
      metaDiv.textContent = `Run: ${trj.run_id} • ${trj.turns ? trj.turns.length : 0} turns`;

      card.appendChild(header);
      card.appendChild(agentDiv);
      card.appendChild(metaDiv);

      card.addEventListener('click', () => {
        document.querySelectorAll('.trajectory-item').forEach(c => c.classList.remove('active'));
        card.classList.add('active');
        renderTrajectoryDetail(trj.id);
      });
      trajectoryListContainer.appendChild(card);
    });

    if (data.items.length > 0) {
      renderTrajectoryDetail(data.items[0].id);
    }
  }

  async function renderTrajectoryDetail(id) {
    if (!traceDetailContainer) return;
    try {
      traceDetailContainer.replaceChildren();
      const spinner = document.createElement('div');
      spinner.className = 'loading-spinner';
      spinner.textContent = 'Loading trajectory trace...';
      traceDetailContainer.appendChild(spinner);

      const trj = await ApiClient.getTrajectory(id);
      traceDetailContainer.replaceChildren();

      // Header
      const traceHeader = document.createElement('div');
      traceHeader.className = 'trace-header';
      const h3 = document.createElement('h3');
      h3.textContent = trj.agent_name;
      const idSpan = document.createElement('span');
      idSpan.className = 'text-muted';
      idSpan.textContent = ` (${trj.id})`;
      h3.appendChild(idSpan);

      const topStatus = document.createElement('span');
      topStatus.className = `status-pill status-${trj.status}`;
      topStatus.textContent = trj.status;

      traceHeader.appendChild(h3);
      traceHeader.appendChild(topStatus);
      traceDetailContainer.appendChild(traceHeader);

      // Section: Judge Consensus
      const judgeSec = document.createElement('div');
      judgeSec.className = 'trace-section';
      const judgeH4 = document.createElement('h4');
      judgeH4.textContent = 'LLM Judge Consensus';
      judgeSec.appendChild(judgeH4);

      const judge = trj.judge_evaluation || {};
      const judgeSummary = document.createElement('div');
      judgeSummary.className = 'judge-summary';

      const judgeScore = document.createElement('div');
      judgeScore.className = 'judge-score';
      judgeScore.textContent = 'Verdict: ';
      const strongVerdict = document.createElement('strong');
      strongVerdict.className = `text-${judge.verdict === 'pass' ? 'success' : 'warning'}`;
      strongVerdict.textContent = judge.verdict ? judge.verdict.toUpperCase() : 'PENDING';
      judgeScore.appendChild(strongVerdict);
      judgeScore.appendChild(document.createTextNode(` (Score: ${judge.score || 0})`));

      const judgeReasoning = document.createElement('div');
      judgeReasoning.className = 'judge-reasoning';
      judgeReasoning.textContent = judge.reasoning || 'Evaluation pending.';

      judgeSummary.appendChild(judgeScore);
      judgeSummary.appendChild(judgeReasoning);
      judgeSec.appendChild(judgeSummary);
      traceDetailContainer.appendChild(judgeSec);

      // Section: A2A Cards
      if (trj.a2a_cards && trj.a2a_cards.length > 0) {
        const a2aSec = document.createElement('div');
        a2aSec.className = 'trace-section';
        const a2aH4 = document.createElement('h4');
        a2aH4.textContent = 'Agent-to-Agent (A2A) Delegation Cards';
        a2aSec.appendChild(a2aH4);

        const cardsGrid = document.createElement('div');
        cardsGrid.className = 'a2a-cards-grid';

        trj.a2a_cards.forEach(card => {
          const cardEl = document.createElement('div');
          cardEl.className = 'a2a-card-item';

          const cardHdr = document.createElement('div');
          cardHdr.className = 'a2a-header';
          const intentSpan = document.createElement('span');
          intentSpan.className = 'a2a-intent';
          intentSpan.textContent = card.intent || 'TASK_DELEGATION';
          const stSpan = document.createElement('span');
          stSpan.className = `status-pill status-${card.status}`;
          stSpan.textContent = card.status;
          cardHdr.appendChild(intentSpan);
          cardHdr.appendChild(stSpan);

          const flow = document.createElement('div');
          flow.className = 'a2a-flow';
          flow.textContent = `${card.sender} → ${card.receiver}`;

          const pre = document.createElement('pre');
          pre.className = 'a2a-payload';
          pre.textContent = JSON.stringify(card.payload, null, 2);

          cardEl.appendChild(cardHdr);
          cardEl.appendChild(flow);
          cardEl.appendChild(pre);
          cardsGrid.appendChild(cardEl);
        });

        a2aSec.appendChild(cardsGrid);
        traceDetailContainer.appendChild(a2aSec);
      }

      // Section: Execution Turns
      const turnsSec = document.createElement('div');
      turnsSec.className = 'trace-section';
      const turnsH4 = document.createElement('h4');
      turnsH4.textContent = 'Execution Steps & Multi-Turn Trace';
      turnsSec.appendChild(turnsH4);

      const turnsContainer = document.createElement('div');
      turnsContainer.className = 'turns-container';

      (trj.turns || []).forEach(turn => {
        const turnCard = document.createElement('div');
        turnCard.className = `turn-card turn-${turn.speaker}`;

        const spk = document.createElement('div');
        spk.className = 'turn-speaker';
        spk.textContent = (turn.speaker || 'AGENT').toUpperCase();
        turnCard.appendChild(spk);

        if (turn.thought) {
          const thoughtDiv = document.createElement('div');
          thoughtDiv.className = 'turn-thought';
          const thoughtBold = document.createElement('strong');
          thoughtBold.textContent = 'CoT Thought: ';
          thoughtDiv.appendChild(thoughtBold);
          thoughtDiv.appendChild(document.createTextNode(turn.thought));
          turnCard.appendChild(thoughtDiv);
        }

        if (turn.content) {
          const contentDiv = document.createElement('div');
          contentDiv.className = 'turn-content';
          contentDiv.textContent = turn.content;
          turnCard.appendChild(contentDiv);
        }

        if (turn.tool_calls && turn.tool_calls.length) {
          const toolsDiv = document.createElement('div');
          toolsDiv.className = 'turn-tools';
          turn.tool_calls.forEach(tc => {
            const tcDiv = document.createElement('div');
            tcDiv.className = 'tool-call';
            const tcCode = document.createElement('code');
            tcCode.textContent = tc.tool;
            tcDiv.appendChild(tcCode);
            tcDiv.appendChild(document.createTextNode(`: ${JSON.stringify(tc.args)}`));
            toolsDiv.appendChild(tcDiv);
          });
          turnCard.appendChild(toolsDiv);
        }

        turnsContainer.appendChild(turnCard);
      });

      turnsSec.appendChild(turnsContainer);
      traceDetailContainer.appendChild(turnsSec);

    } catch (e) {
      traceDetailContainer.replaceChildren();
      const alert = document.createElement('div');
      alert.className = 'alert alert-error';
      alert.textContent = `Failed to load trajectory details: ${e.message}`;
      traceDetailContainer.appendChild(alert);
    }
  }

  if (statusSelect) {
    statusSelect.addEventListener('change', loadTrajectories);
  }
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      const q = e.target.value.toLowerCase();
      document.querySelectorAll('.trajectory-item').forEach(item => {
        item.style.display = item.textContent.toLowerCase().includes(q) ? '' : 'none';
      });
    });
  }

  await loadTrajectories();
}

/* -------------------------------------------------------------------------- */
/* Datasets Page Logic                                                        */
/* -------------------------------------------------------------------------- */
async function initDatasets() {
  const listContainer = document.getElementById('datasets-list');
  const form = document.getElementById('create-dataset-form');

  async function loadDatasets() {
    if (!listContainer) return;
    try {
      const data = await ApiClient.getDatasets();
      listContainer.replaceChildren();
      if (data.items.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'empty-state';
        empty.textContent = 'No benchmark datasets imported yet.';
        listContainer.appendChild(empty);
        return;
      }

      data.items.forEach(ds => {
        const card = document.createElement('div');
        card.className = 'card dataset-card';

        const cardHdr = document.createElement('div');
        cardHdr.className = 'card-header';
        const h4 = document.createElement('h4');
        h4.textContent = ds.name;
        const tag = document.createElement('span');
        tag.className = 'tag';
        tag.textContent = ds.domain;
        cardHdr.appendChild(h4);
        cardHdr.appendChild(tag);

        const cardBody = document.createElement('div');
        cardBody.className = 'card-body';
        const pCount = document.createElement('p');
        const countStrong = document.createElement('strong');
        countStrong.textContent = 'Total Test Cases: ';
        pCount.appendChild(countStrong);
        pCount.appendChild(document.createTextNode(String(ds.test_count)));
        cardBody.appendChild(pCount);

        const tcPreview = document.createElement('div');
        tcPreview.className = 'test-cases-preview';
        (ds.test_cases || []).slice(0, 3).forEach(tc => {
          const tcItem = document.createElement('div');
          tcItem.className = 'tc-item';
          const code = document.createElement('code');
          code.textContent = tc.id || 'tc';
          tcItem.appendChild(code);
          tcItem.appendChild(document.createTextNode(`: ${tc.prompt || ''}`));
          tcPreview.appendChild(tcItem);
        });
        cardBody.appendChild(tcPreview);

        card.appendChild(cardHdr);
        card.appendChild(cardBody);
        listContainer.appendChild(card);
      });
    } catch (e) {
      console.error(e);
    }
  }

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const name = document.getElementById('dataset-name').value;
      const domain = document.getElementById('dataset-domain').value;
      const testCasesRaw = document.getElementById('dataset-cases').value;

      let testCases = [];
      try {
        testCases = testCasesRaw ? JSON.parse(testCasesRaw) : [];
      } catch (err) {
        alert('Test cases must be a valid JSON array.');
        return;
      }

      try {
        await ApiClient.createDataset({
          name,
          domain,
          test_count: testCases.length,
          test_cases: testCases
        });
        form.reset();
        await loadDatasets();
        alert('Dataset created successfully!');
      } catch (err) {
        alert(`Error: ${err.message}`);
      }
    });
  }

  await loadDatasets();
}

/* -------------------------------------------------------------------------- */
/* New Run Page Logic                                                         */
/* -------------------------------------------------------------------------- */
async function initNewRun() {
  const agentSelectContainer = document.getElementById('agent-selection-container');
  const datasetSelect = document.getElementById('run-dataset');
  const form = document.getElementById('new-run-form');

  try {
    // Populate Agents
    const agentsData = await ApiClient.getAgents();
    if (agentSelectContainer) {
      agentSelectContainer.replaceChildren();
      agentsData.items.forEach(agent => {
        const label = document.createElement('label');
        label.className = 'checkbox-card';

        const cb = document.createElement('input');
        cb.type = 'checkbox';
        cb.name = 'agents';
        cb.value = agent.id;

        const content = document.createElement('div');
        content.className = 'checkbox-card-content';

        const nameSpan = document.createElement('span');
        nameSpan.className = 'font-bold';
        nameSpan.textContent = agent.name;

        const roleSpan = document.createElement('span');
        roleSpan.className = 'text-subtle text-sm';
        roleSpan.textContent = `${agent.role} (${agent.model})`;

        content.appendChild(nameSpan);
        content.appendChild(roleSpan);

        label.appendChild(cb);
        label.appendChild(content);
        agentSelectContainer.appendChild(label);
      });
    }

    // Populate Datasets
    const datasetsData = await ApiClient.getDatasets();
    if (datasetSelect) {
      datasetSelect.replaceChildren();
      const defaultOpt = document.createElement('option');
      defaultOpt.value = '';
      defaultOpt.textContent = 'Select Golden Benchmark Dataset';
      datasetSelect.appendChild(defaultOpt);

      datasetsData.items.forEach(ds => {
        const opt = document.createElement('option');
        opt.value = ds.id;
        opt.textContent = `${ds.name} (${ds.test_count} tests - ${ds.domain})`;
        datasetSelect.appendChild(opt);
      });
    }
  } catch (err) {
    console.error('Failed to populate form options:', err);
  }

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const name = document.getElementById('run-name').value;
      const mode = document.getElementById('run-mode').value;
      const datasetId = datasetSelect ? datasetSelect.value : '';
      const concurrency = parseInt(document.getElementById('run-concurrency').value || '1', 10);
      const judgeModel = document.getElementById('run-judge').value || 'gpt-4o';

      const selectedAgents = Array.from(
        document.querySelectorAll('input[name="agents"]:checked')
      ).map(cb => cb.value);

      if (!name || !mode || !datasetId || selectedAgents.length === 0) {
        alert('Please fill out all required fields and select at least one agent.');
        return;
      }

      try {
        const run = await ApiClient.createRun({
          name,
          mode,
          agent_ids: selectedAgents,
          dataset_id: datasetId,
          concurrency,
          judge_model: judgeModel
        });
        alert(`Evaluation run '${run.name}' launched successfully!`);
        window.location.href = `/trajectories.html?run_id=${encodeURIComponent(run.id)}`;
      } catch (err) {
        alert(`Error launching run: ${err.message}`);
      }
    });
  }
}

/* -------------------------------------------------------------------------- */
/* Annotations Page Logic                                                     */
/* -------------------------------------------------------------------------- */
async function initAnnotations() {
  const queueContainer = document.getElementById('annotations-queue');
  const trajectorySelect = document.getElementById('ann-trajectory-id');
  const form = document.getElementById('annotation-form');

  async function loadAnnotations() {
    if (!queueContainer) return;
    try {
      const data = await ApiClient.getAnnotations();
      queueContainer.replaceChildren();
      if (data.items.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'empty-state';
        empty.textContent = 'No human review records submitted yet.';
        queueContainer.appendChild(empty);
        return;
      }

      data.items.forEach(ann => {
        const item = document.createElement('div');
        item.className = 'annotation-card';

        const hdr = document.createElement('div');
        hdr.className = 'ann-header';
        const vSpan = document.createElement('span');
        vSpan.className = `ann-verdict verdict-${ann.verdict}`;
        vSpan.textContent = ann.verdict.toUpperCase();
        const tSpan = document.createElement('span');
        tSpan.className = 'ann-taxonomy';
        tSpan.textContent = ann.taxonomy;
        hdr.appendChild(vSpan);
        hdr.appendChild(tSpan);

        const meta = document.createElement('div');
        meta.className = 'ann-meta';
        const strongTrj = document.createElement('strong');
        strongTrj.textContent = 'Trajectory: ';
        const trjLink = document.createElement('a');
        trjLink.href = '/trajectories.html';
        trjLink.textContent = ann.trajectory_id;
        meta.appendChild(strongTrj);
        meta.appendChild(trjLink);
        meta.appendChild(document.createTextNode(` • Evaluator: ${ann.evaluator}`));

        const notes = document.createElement('div');
        notes.className = 'ann-notes';
        notes.textContent = ann.notes || 'No comments provided.';

        item.appendChild(hdr);
        item.appendChild(meta);
        item.appendChild(notes);
        queueContainer.appendChild(item);
      });
    } catch (e) {
      console.error(e);
    }
  }

  // Populate trajectory selector
  try {
    const trjs = await ApiClient.getTrajectories();
    if (trajectorySelect) {
      trajectorySelect.replaceChildren();
      const defaultOpt = document.createElement('option');
      defaultOpt.value = '';
      defaultOpt.textContent = 'Select Trajectory to Annotate';
      trajectorySelect.appendChild(defaultOpt);

      trjs.items.forEach(t => {
        const opt = document.createElement('option');
        opt.value = t.id;
        opt.textContent = `${t.id} - ${t.agent_name} (${t.status})`;
        trajectorySelect.appendChild(opt);
      });
    }
  } catch (e) {
    console.error(e);
  }

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const trajectoryId = trajectorySelect ? trajectorySelect.value : '';
      const verdict = document.getElementById('ann-verdict').value;
      const taxonomy = document.getElementById('ann-taxonomy').value;
      const evaluator = document.getElementById('ann-evaluator').value;
      const notes = document.getElementById('ann-notes').value;

      if (!trajectoryId || !verdict || !taxonomy || !evaluator) {
        alert('Please fill out all required fields.');
        return;
      }

      try {
        await ApiClient.createAnnotation({
          trajectory_id: trajectoryId,
          verdict,
          taxonomy,
          evaluator,
          notes
        });
        form.reset();
        await loadAnnotations();
        alert('Annotation submitted successfully!');
      } catch (err) {
        alert(`Error: ${err.message}`);
      }
    });
  }

  await loadAnnotations();
}

/* -------------------------------------------------------------------------- */
/* Utilities                                                                  */
/* -------------------------------------------------------------------------- */
function updateText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}
