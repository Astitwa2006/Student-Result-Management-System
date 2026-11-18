/**
 * Student Result Management System - Frontend Controller
 * Connects frontend dashboard with Python computational backend.
 * Supports cross-origin deployment: Vercel (frontend) + Render (backend).
 */

// --- Backend API base URL ---
// Set via window.__API_BASE__ in index.html BEFORE this script loads.
// For local development (single server), leave as empty string.
const API_BASE = (window.__API_BASE__ && window.__API_BASE__ !== 'PLACEHOLDER_RENDER_URL')
  ? window.__API_BASE__.replace(/\/$/, '') // strip trailing slash
  : '';

// State
let allStudents = [];
let filteredStudents = [];
let metadata = null;
let currentSortColumn = "rank";
let currentSortAsc = true;
let activeReportStudent = null;
let activeReportAscii = "";

// Subject list constant (mirrors backend)
const SUBJECT_KEYS = [
  "Python Programming",
  "Mathematics",
  "Digital Electronics",
  "Physics",
  "Professional Communication"
];

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
  if (!API_BASE) {
    console.error("Student Result System: Backend URL not configured. Set window.__API_BASE__ in public/index.html.");
  }
  fetchMetadata();
  loadData();
});

// Toast notification helper
function showToast(message, type = "success") {
  const container = document.getElementById("toastContainer");
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<span>${type === "success" ? "✓" : "⚠️"}</span> ${message}`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// Fetch system metadata
async function fetchMetadata() {
  try {
    const res = await fetch(`${API_BASE}/api/meta`);
    if (res.ok) {
      metadata = await res.json();
    }
  } catch (err) {
    console.warn("Could not load metadata:", err);
  }
}

// Fetch all students and analytics
async function loadData() {
  try {
    const [studentsRes, analyticsRes] = await Promise.all([
      fetch(`${API_BASE}/api/students`),
      fetch(`${API_BASE}/api/analytics`)
    ]);

    if (studentsRes.ok) {
      const data = await studentsRes.json();
      allStudents = data.students || [];
      filteredStudents = [...allStudents];
      renderStudentsTable();
      updateDiagnosticsTab();
    }

    if (analyticsRes.ok) {
      const analytics = await analyticsRes.json();
      updateKPICards(analytics);
      renderSubjectStats(analytics.subject_stats);
      refreshChartImages();
    }
  } catch (err) {
    console.error("Error loading data:", err);
    showToast("Failed to load student data. Please try refreshing the page.", "error");
  }
}

// Update KPI metric cards
function updateKPICards(stats) {
  document.getElementById("kpiTotalStudents").textContent = stats.total_students;
  document.getElementById("kpiClassAverage").textContent = `${stats.class_average.toFixed(1)}%`;
  document.getElementById("kpiMedian").textContent = `Median: ${stats.median_percentage.toFixed(1)}% | StdDev: ${stats.std_deviation.toFixed(1)}%`;

  if (stats.topper) {
    document.getElementById("kpiTopperName").textContent = stats.topper.name;
    document.getElementById("kpiTopperScore").textContent = `${stats.topper.percentage.toFixed(1)}% (Rank #1)`;
  } else {
    document.getElementById("kpiTopperName").textContent = "N/A";
    document.getElementById("kpiTopperScore").textContent = "--";
  }

  document.getElementById("kpiPassRate").textContent = `${stats.pass_rate.toFixed(1)}%`;
  document.getElementById("kpiPassCount").textContent = `${stats.passed_count} passed, ${stats.failed_count} need help`;
}

// Render Students Table
function renderStudentsTable() {
  const tbody = document.getElementById("studentsTableBody");

  if (!filteredStudents || filteredStudents.length === 0) {
    tbody.innerHTML = `<tr><td colspan="9" style="text-align:center; padding: 2.5rem; color: #64748b;">No student records found matching your filters.</td></tr>`;
    return;
  }

  tbody.innerHTML = filteredStudents.map(s => {
    const rankClass = s.rank === 1 ? "badge-rank-1" : "";
    const gradeClass = `grade-${s.grade.replace("+", "plus")}`;
    const statusClass = s.status === "PASS" ? "badge-pass" : "badge-fail";

    // Summary pills for 5 subjects
    const marksPills = SUBJECT_KEYS.map(sub => {
      const score = s.marks[sub] !== undefined ? s.marks[sub] : "-";
      const isFail = typeof score === "number" && score < 40;
      const failClass = isFail ? "fail-mark" : "";
      const abbr = sub.split(" ")[0].slice(0, 4);
      return `<span class="mark-pill ${failClass}" title="${sub}: ${score}">${abbr}: ${score}</span>`;
    }).join("");

    return `
      <tr>
        <td><span class="badge badge-rank ${rankClass}">#${s.rank || "-"}</span></td>
        <td><span class="badge badge-roll">${escapeHtml(s.roll_no)}</span></td>
        <td><strong>${escapeHtml(s.name)}</strong></td>
        <td><div class="marks-summary">${marksPills}</div></td>
        <td><strong>${s.total.toFixed(1)}</strong></td>
        <td>
          <div style="display:flex; align-items:center; gap:0.5rem;">
            <span>${s.percentage.toFixed(1)}%</span>
            <div style="background:#e2e8f0; width:50px; height:6px; border-radius:3px; overflow:hidden;">
              <div style="background:#2563eb; width:${Math.min(s.percentage, 100)}%; height:100%;"></div>
            </div>
          </div>
        </td>
        <td><span class="badge badge-grade ${gradeClass}">${s.grade}</span></td>
        <td><span class="badge ${statusClass}">${s.status}</span></td>
        <td>
          <div style="display:flex; gap:0.35rem;">
            <button class="btn btn-sm btn-outline" onclick="viewReportCard('${s.roll_no}')" title="View Report Card">📄 Marksheet</button>
            <button class="btn btn-sm btn-ghost" style="color:#dc2626;" onclick="deleteStudent('${s.roll_no}')" title="Delete Student">&times;</button>
          </div>
        </td>
      </tr>
    `;
  }).join("");
}

// Render Subject Stats Table in Analytics Tab
function renderSubjectStats(subjStats) {
  const tbody = document.getElementById("subjectStatsBody");
  if (!tbody || !subjStats) return;

  tbody.innerHTML = Object.keys(subjStats).map(sub => {
    const info = subjStats[sub];
    return `
      <tr>
        <td><strong>${escapeHtml(sub)}</strong></td>
        <td><span style="font-weight:700; color:#2563eb;">${info.average.toFixed(1)} / 100</span></td>
        <td><span style="color:#16a34a; font-weight:600;">${info.highest.toFixed(1)}</span></td>
        <td><span style="color:#dc2626; font-weight:600;">${info.lowest.toFixed(1)}</span></td>
        <td>${info.pass_rate.toFixed(1)}%</td>
        <td>&plusmn; ${info.std_dev.toFixed(1)}</td>
      </tr>
    `;
  }).join("");
}

// Update Rule-Based Diagnostics Tab
function updateDiagnosticsTab() {
  const remedialList = document.getElementById("remedialList");
  const meritList = document.getElementById("meritList");

  if (!remedialList || !meritList) return;

  const failedStudents = allStudents.filter(s => s.status === "FAIL");
  const meritStudents = allStudents.filter(s => s.percentage >= 85.0);

  if (failedStudents.length === 0) {
    remedialList.innerHTML = `<p style="padding:1rem; color:#16a34a;">🎉 Excellent! All students are currently passing all subjects.</p>`;
  } else {
    remedialList.innerHTML = failedStudents.map(s => `
      <div class="diag-item">
        <div class="diag-item-header">
          <span class="diag-item-name">${escapeHtml(s.name)} (${s.roll_no})</span>
          <span class="badge badge-fail">Rank #${s.rank} &bull; ${s.percentage}%</span>
        </div>
        <p>⚠️ Needs attention in: <strong>${(s.failed_subjects || []).join(", ") || "Subject marks < 40"}</strong>. Recommended 4 hours/week remedial lab practice.</p>
      </div>
    `).join("");
  }

  if (meritStudents.length === 0) {
    meritList.innerHTML = `<p style="padding:1rem; color:#64748b;">No students currently have overall scores &ge; 85%.</p>`;
  } else {
    meritList.innerHTML = meritStudents.map(s => `
      <div class="diag-item">
        <div class="diag-item-header">
          <span class="diag-item-name">🌟 ${escapeHtml(s.name)} (${s.roll_no})</span>
          <span class="badge badge-rank-1">Rank #${s.rank} &bull; ${s.percentage}% [${s.grade}]</span>
        </div>
        <p>Outstanding academic standing. Recommended for honours projects, hackathons, and teaching assistant mentorship.</p>
      </div>
    `).join("");
  }
}

// Real-time search handler
function handleSearch() {
  applyFilters();
}

// Filter and search logic
function applyFilters() {
  const query = document.getElementById("searchInput").value.trim().toLowerCase();
  const selectedGrade = document.getElementById("gradeFilter").value;
  const selectedStatus = document.getElementById("statusFilter").value;

  filteredStudents = allStudents.filter(s => {
    const matchesQuery = !query ||
      s.roll_no.toLowerCase().includes(query) ||
      s.name.toLowerCase().includes(query);

    const matchesGrade = selectedGrade === "ALL" || s.grade === selectedGrade;
    const matchesStatus = selectedStatus === "ALL" || s.status === selectedStatus;

    return matchesQuery && matchesGrade && matchesStatus;
  });

  sortArray(filteredStudents, currentSortColumn, currentSortAsc);
  renderStudentsTable();
}

function resetFilters() {
  document.getElementById("searchInput").value = "";
  document.getElementById("gradeFilter").value = "ALL";
  document.getElementById("statusFilter").value = "ALL";
  filteredStudents = [...allStudents];
  sortArray(filteredStudents, "rank", true);
  renderStudentsTable();
}

// Table Sorting
function sortTable(column) {
  if (currentSortColumn === column) {
    currentSortAsc = !currentSortAsc;
  } else {
    currentSortColumn = column;
    currentSortAsc = true;
  }
  sortArray(filteredStudents, currentSortColumn, currentSortAsc);
  renderStudentsTable();
}

function sortArray(arr, column, asc) {
  arr.sort((a, b) => {
    let valA = a[column];
    let valB = b[column];

    if (typeof valA === "string") valA = valA.toLowerCase();
    if (typeof valB === "string") valB = valB.toLowerCase();

    if (valA < valB) return asc ? -1 : 1;
    if (valA > valB) return asc ? 1 : -1;
    return 0;
  });
}

// Tab Switching
function switchTab(tabId) {
  document.querySelectorAll(".tab-pane").forEach(pane => pane.classList.remove("active"));
  document.querySelectorAll(".tab-btn").forEach(btn => btn.classList.remove("active"));

  const targetPane = document.getElementById(tabId);
  if (targetPane) targetPane.classList.add("active");

  const matchingBtn = Array.from(document.querySelectorAll(".tab-btn")).find(
    btn => btn.getAttribute("onclick") && btn.getAttribute("onclick").includes(tabId)
  );
  if (matchingBtn) matchingBtn.classList.add("active");
}

// Refresh chart images from backend (busts cache)
function refreshChartImages() {
  const timestamp = new Date().getTime();
  const img1 = document.getElementById("imgSubjectAverages");
  const img2 = document.getElementById("imgGradeDist");
  const img3 = document.getElementById("imgScoreDist");
  if (img1) img1.src = `${API_BASE}/charts/subject_averages.png?t=${timestamp}`;
  if (img2) img2.src = `${API_BASE}/charts/grade_distribution.png?t=${timestamp}`;
  if (img3) img3.src = `${API_BASE}/charts/score_distribution.png?t=${timestamp}`;
}

// Refresh Analytics & Charts
async function refreshAnalytics() {
  showToast("Recomputing analytics and generating updated charts...", "success");
  try {
    const res = await fetch(`${API_BASE}/api/analytics`);
    if (res.ok) {
      const stats = await res.json();
      updateKPICards(stats);
      renderSubjectStats(stats.subject_stats);
      refreshChartImages();
      showToast("Visualizations and statistics updated successfully!", "success");
    }
  } catch (err) {
    showToast("Failed to refresh analytics.", "error");
  }
}

// Export CSV
function exportCsv() {
  window.location.href = `${API_BASE}/api/export/csv`;
}

// Live calculation inside Add Student Modal
function calculateLiveTotal() {
  const p  = parseFloat(document.getElementById("markPython").value)      || 0;
  const m  = parseFloat(document.getElementById("markMaths").value)       || 0;
  const e  = parseFloat(document.getElementById("markElectronics").value) || 0;
  const ph = parseFloat(document.getElementById("markPhysics").value)     || 0;
  const eng = parseFloat(document.getElementById("markEnglish").value)    || 0;

  const total = p + m + e + ph + eng;
  const percentage = (total / 500) * 100;

  document.getElementById("liveTotal").textContent = total.toFixed(1);
  document.getElementById("livePercentage").textContent = `${percentage.toFixed(2)}%`;

  let grade = "F";
  if (percentage >= 90) grade = "A+";
  else if (percentage >= 80) grade = "A";
  else if (percentage >= 70) grade = "B+";
  else if (percentage >= 60) grade = "B";
  else if (percentage >= 50) grade = "C";
  else if (percentage >= 40) grade = "D";

  document.getElementById("liveGrade").textContent = grade;
}

// Add Student Modal Controls
function openAddStudentModal() {
  document.getElementById("formAddStudent").reset();
  document.getElementById("addErrorMsg").style.display = "none";
  calculateLiveTotal();
  document.getElementById("modalAddStudent").classList.add("active");
}

function closeAddStudentModal() {
  document.getElementById("modalAddStudent").classList.remove("active");
}

async function submitNewStudent(event) {
  event.preventDefault();
  const errorBox = document.getElementById("addErrorMsg");
  errorBox.style.display = "none";

  const roll = document.getElementById("newRoll").value.trim().toUpperCase();
  const name = document.getElementById("newName").value.trim();

  const marks = {
    "Python Programming":      parseFloat(document.getElementById("markPython").value),
    "Mathematics":             parseFloat(document.getElementById("markMaths").value),
    "Digital Electronics":     parseFloat(document.getElementById("markElectronics").value),
    "Physics":                 parseFloat(document.getElementById("markPhysics").value),
    "Professional Communication": parseFloat(document.getElementById("markEnglish").value),
  };

  try {
    const res = await fetch(`${API_BASE}/api/students`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ roll_no: roll, name: name, marks: marks }),
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || "Failed to create student record.");
    }

    closeAddStudentModal();
    showToast(`✓ Registered ${name} (${roll}) with rank #${data.student.rank}!`, "success");
    await loadData();
  } catch (err) {
    errorBox.textContent = err.message;
    errorBox.style.display = "block";
  }
}

// Delete Student
async function deleteStudent(rollNo) {
  if (!confirm(`Are you sure you want to delete student '${rollNo}'?`)) {
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/api/students/${encodeURIComponent(rollNo)}`, {
      method: "DELETE",
    });

    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.detail || "Failed to delete student.");
    }

    showToast(`Student ${rollNo} deleted. Ranks recalculated.`, "success");
    await loadData();
  } catch (err) {
    showToast(err.message, "error");
  }
}

// View Detailed Report Card Modal
async function viewReportCard(rollNo) {
  try {
    const res = await fetch(`${API_BASE}/api/students/${encodeURIComponent(rollNo)}/report`);
    if (!res.ok) throw new Error("Could not fetch student report.");

    const data = await res.json();
    activeReportStudent = data.student;
    activeReportAscii = data.ascii_report;

    const s = data.student;
    const recs = data.recommendations || [];

    const rows = SUBJECT_KEYS.map(sub => {
      const mark = s.marks[sub];
      const isPass = mark >= 40;
      const statusBadge = isPass
        ? '<span class="badge badge-pass">PASS</span>'
        : '<span class="badge badge-fail">FAIL</span>';

      return `
        <tr>
          <td><strong>${escapeHtml(sub)}</strong></td>
          <td>100</td>
          <td><strong>${mark.toFixed(1)}</strong></td>
          <td>${statusBadge}</td>
        </tr>
      `;
    }).join("");

    const recsHtml = recs.map(r => `
      <div class="rec-item rec-${r.type}">
        <strong>[${r.category.toUpperCase()}] ${escapeHtml(r.subject)}:</strong> ${escapeHtml(r.message)}
      </div>
    `).join("");

    const html = `
      <div class="marksheet-wrapper">
        <div class="marksheet-top">
          <h3>ACADEMIC PERFORMANCE MARKSHEET</h3>
          <p>Course: Computational Thinking and Programming (2026CSAE100)</p>
        </div>

        <div class="marksheet-student-meta">
          <div><strong>Student Name:</strong> ${escapeHtml(s.name)}</div>
          <div><strong>Roll Number:</strong> <span class="badge badge-roll">${escapeHtml(s.roll_no)}</span></div>
          <div><strong>Class Rank:</strong> <span class="badge badge-rank badge-rank-1">#${s.rank}</span> (${s.percentile}% percentile)</div>
          <div><strong>Final Status:</strong> <span class="badge ${s.status === 'PASS' ? 'badge-pass' : 'badge-fail'}">${s.status}</span></div>
          <div><strong>Overall Grade:</strong> <span class="badge badge-grade grade-${s.grade.replace('+', 'plus')}">${s.grade}</span> (${s.grade_desc})</div>
          <div><strong>Grade Point (GPA):</strong> ${s.gpa.toFixed(1)} / 10.0</div>
        </div>

        <table class="data-table mini-table" style="margin-bottom:1rem;">
          <thead>
            <tr>
              <th>Subject</th>
              <th>Max Marks</th>
              <th>Marks Obtained</th>
              <th>Result</th>
            </tr>
          </thead>
          <tbody>
            ${rows}
          </tbody>
          <tfoot>
            <tr style="background:#f8fafc; font-weight:700;">
              <td>TOTAL AGGREGATE</td>
              <td>${s.max_total}</td>
              <td>${s.total.toFixed(1)}</td>
              <td>${s.percentage.toFixed(2)}%</td>
            </tr>
          </tfoot>
        </table>

        <div class="recommendations-box">
          <h5>💡 Prescriptive Academic Diagnostics &amp; Remedial Recommendations:</h5>
          ${recsHtml || '<p style="color:#64748b;">No remedial flags detected.</p>'}
        </div>
      </div>
    `;

    document.getElementById("reportCardContent").innerHTML = html;
    document.getElementById("modalReportCard").classList.add("active");
  } catch (err) {
    showToast(err.message, "error");
  }
}

function closeReportCardModal() {
  document.getElementById("modalReportCard").classList.remove("active");
}

function downloadReportCardTxt() {
  if (!activeReportAscii || !activeReportStudent) return;
  const blob = new Blob([activeReportAscii], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `Report_Card_${activeReportStudent.roll_no}.txt`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast(`Report card downloaded for ${activeReportStudent.roll_no}`);
}

// Team Modal
function openTeamModal() {
  document.getElementById("modalTeam").classList.add("active");
}

function closeTeamModal() {
  document.getElementById("modalTeam").classList.remove("active");
}

// Utility: escape HTML to prevent XSS
function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// Auto-triggers for tab auto-open via URL params
window.addEventListener('load', () => {
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get('tab') === 'analytics') {
    setTimeout(() => switchTab('tab-analytics'), 800);
  } else if (urlParams.get('tab') === 'diagnostics') {
    setTimeout(() => switchTab('tab-diagnostics'), 800);
  } else if (urlParams.get('report')) {
    setTimeout(() => viewReportCard(urlParams.get('report')), 800);
  }
});
