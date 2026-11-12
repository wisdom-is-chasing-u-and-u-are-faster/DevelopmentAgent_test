/**
 * Enterprise Fitness Challenge Platform Client API Library
 * Wires live interactive DOM views to backend REST endpoints with XSS sanitization.
 */

const API_BASE = '/api/v1';

function escapeHTML(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

const FitnessAPI = {
    // Health probe
    async fetchHealth() {
        const res = await fetch('/health');
        return await res.json();
    },

    // Challenges
    async fetchChallenges(sportType = 'all', status = 'all', page = 1) {
        const params = new URLSearchParams({ sport_type: sportType, status: status, page: page });
        const res = await fetch(`${API_BASE}/challenges?${params.toString()}`);
        return await res.json();
    },

    async fetchChallengeDetails(id) {
        const res = await fetch(`${API_BASE}/challenges/${id}`);
        if (!res.ok) throw new Error(`Challenge ${id} not found`);
        return await res.json();
    },

    async createChallenge(data) {
        const res = await fetch(`${API_BASE}/challenges`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return await res.json();
    },

    async enrollInChallenge(challengeId, userId = 1, teamCode = null) {
        const res = await fetch(`${API_BASE}/challenges/${challengeId}/enroll`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, team_code: teamCode })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Enrollment failed');
        return data;
    },

    // Leaderboard
    async fetchLeaderboard(challengeId = 1, rankingType = 'global', userId = 1) {
        const params = new URLSearchParams({ challenge_id: challengeId, type: rankingType, user_id: userId });
        const res = await fetch(`${API_BASE}/leaderboard?${params.toString()}`);
        return await res.json();
    },

    // Social Feed
    async fetchSocialFeed() {
        const res = await fetch(`${API_BASE}/social/feed`);
        return await res.json();
    },

    async createSocialPost(title, distanceKm, durationMinutes, gpsPoints = []) {
        const res = await fetch(`${API_BASE}/social/posts`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: 1,
                activity_title: title,
                distance_km: distanceKm,
                duration_minutes: durationMinutes,
                gps_points: gpsPoints
            })
        });
        return await res.json();
    },

    // User Profile & Badges
    async fetchUserProfile(userId = 1) {
        const res = await fetch(`${API_BASE}/users/profile?user_id=${userId}`);
        return await res.json();
    },

    async fetchBadges(userId = 1) {
        const res = await fetch(`${API_BASE}/badges?user_id=${userId}`);
        return await res.json();
    },

    // Privacy & Data Rights
    async fetchPrivacySettings(userId = 1) {
        const res = await fetch(`${API_BASE}/privacy/settings?user_id=${userId}`);
        return await res.json();
    },

    async updatePrivacySettings(settings, userId = 1) {
        const payload = Object.assign({ user_id: userId }, settings);
        const res = await fetch(`${API_BASE}/privacy/settings`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        return await res.json();
    },

    async requestAccountDeletion(confirmEmail, reason, userId = 1) {
        const res = await fetch(`${API_BASE}/account/deletion`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, confirm_email: confirmEmail, reason: reason })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Deletion request rejected');
        return data;
    },

    // Connected Apps
    async fetchConnectedApps() {
        const res = await fetch(`${API_BASE}/connected-apps`);
        return await res.json();
    },

    // Telemetry Ingestion
    async ingestTelemetry(provider, activityType, telemetryPoints, userId = '1') {
        const res = await fetch(`${API_BASE}/telemetry/ingest`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                provider: provider,
                user_id: userId,
                activity_type: activityType,
                telemetry_points: telemetryPoints
            })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Telemetry rejected');
        return data;
    },

    // Admin endpoints
    async fetchAdminUsers() {
        const res = await fetch(`${API_BASE}/admin/users`);
        return await res.json();
    },

    async fetchAdminChallenges() {
        const res = await fetch(`${API_BASE}/admin/challenges`);
        return await res.json();
    }
};

// UI DOM Hydration & Event Wiring on DOMContentLoaded
document.addEventListener('DOMContentLoaded', async () => {
    // 1. Leaderboard page wiring
    const leaderboardTable = document.getElementById('leaderboard-tbody');
    const rankingTabs = document.querySelectorAll('[data-ranking-type]');
    if (leaderboardTable) {
        async function loadLeaderboard(type = 'global') {
            try {
                const data = await FitnessAPI.fetchLeaderboard(1, type, 1);
                leaderboardTable.textContent = '';
                (data.rankings || []).forEach(r => {
                    const tr = document.createElement('tr');
                    tr.className = r.user_id === 1 ? 'table-primary font-weight-bold' : '';

                    const tdRank = document.createElement('td');
                    const rankSpan = document.createElement('span');
                    rankSpan.className = 'badge badge-pill badge-primary';
                    rankSpan.textContent = `#${r.rank_position}`;
                    tdRank.appendChild(rankSpan);

                    const tdUser = document.createElement('td');
                    const divUser = document.createElement('div');
                    divUser.className = 'd-flex align-items-center';
                    const img = document.createElement('img');
                    img.src = r.avatar_url || 'https://via.placeholder.com/32';
                    img.className = 'rounded-circle mr-2';
                    img.width = 32;
                    img.height = 32;
                    img.alt = r.screen_name || 'Athlete';
                    const nameSpan = document.createElement('span');
                    nameSpan.textContent = r.screen_name || 'Athlete';
                    divUser.appendChild(img);
                    divUser.appendChild(nameSpan);
                    tdUser.appendChild(divUser);

                    const tdScore = document.createElement('td');
                    tdScore.className = 'text-right font-weight-bold';
                    tdScore.textContent = `${Number(r.score_value).toFixed(1)} ${r.unit || 'km'}`;

                    tr.appendChild(tdRank);
                    tr.appendChild(tdUser);
                    tr.appendChild(tdScore);
                    leaderboardTable.appendChild(tr);
                });
            } catch (err) {
                console.error('Failed to load leaderboard:', err);
            }
        }
        loadLeaderboard('global');

        rankingTabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                rankingTabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                loadLeaderboard(tab.getAttribute('data-ranking-type'));
            });
        });
    }

    // 2. Challenge List page wiring
    const challengeContainer = document.getElementById('challenge-cards-container');
    const sportFilter = document.getElementById('filter-sport');
    if (challengeContainer) {
        async function loadChallenges() {
            try {
                const sport = sportFilter ? sportFilter.value : 'all';
                const data = await FitnessAPI.fetchChallenges(sport, 'all');
                challengeContainer.textContent = '';
                (data.challenges || []).forEach(c => {
                    const col = document.createElement('div');
                    col.className = 'col-md-6 mb-4';
                    
                    const card = document.createElement('div');
                    card.className = 'card h-100 shadow-sm border-0';
                    const cardBody = document.createElement('div');
                    cardBody.className = 'card-body';

                    const headerDiv = document.createElement('div');
                    headerDiv.className = 'd-flex justify-content-between align-items-center mb-2';
                    const badgeSport = document.createElement('span');
                    badgeSport.className = 'badge badge-info';
                    badgeSport.textContent = c.sport_type;
                    const badgeStatus = document.createElement('span');
                    badgeStatus.className = 'badge badge-success';
                    badgeStatus.textContent = c.status;
                    headerDiv.appendChild(badgeSport);
                    headerDiv.appendChild(badgeStatus);

                    const titleEl = document.createElement('h5');
                    titleEl.className = 'card-title font-weight-bold';
                    titleEl.textContent = c.title;

                    const descEl = document.createElement('p');
                    descEl.className = 'card-text text-muted';
                    descEl.textContent = c.description;

                    const footerDiv = document.createElement('div');
                    footerDiv.className = 'd-flex justify-content-between align-items-center mt-3';
                    const countEl = document.createElement('small');
                    countEl.className = 'text-muted';
                    countEl.textContent = `${c.enrolled_count} / ${c.capacity_cap} enrolled`;
                    const viewBtn = document.createElement('a');
                    viewBtn.href = `challenge_details.html?id=${c.id}`;
                    viewBtn.className = 'btn btn-outline-primary btn-sm';
                    viewBtn.textContent = 'View & Enroll';
                    footerDiv.appendChild(countEl);
                    footerDiv.appendChild(viewBtn);

                    cardBody.appendChild(headerDiv);
                    cardBody.appendChild(titleEl);
                    cardBody.appendChild(descEl);
                    cardBody.appendChild(footerDiv);
                    card.appendChild(cardBody);
                    col.appendChild(card);
                    challengeContainer.appendChild(col);
                });
            } catch (err) {
                console.error('Failed to load challenges:', err);
            }
        }
        loadChallenges();
        if (sportFilter) {
            sportFilter.addEventListener('change', loadChallenges);
        }
    }

    // 3. Challenge Details & Enrollment Form
    const enrollBtn = document.getElementById('btn-enroll-challenge');
    if (enrollBtn) {
        enrollBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            const urlParams = new URLSearchParams(window.location.search);
            const challengeId = parseInt(urlParams.get('id') || '1');
            const teamCodeInput = document.getElementById('input-team-code');
            const teamCode = teamCodeInput ? teamCodeInput.value.trim() : null;

            try {
                const res = await FitnessAPI.enrollInChallenge(challengeId, 1, teamCode);
                alert(`Successfully enrolled in challenge #${res.challenge_id}!`);
                enrollBtn.textContent = 'Enrolled ✓';
                enrollBtn.disabled = true;
                enrollBtn.classList.replace('btn-primary', 'btn-success');
            } catch (err) {
                alert(`Enrollment Error: ${err.message}`);
            }
        });
    }

    // 4. Social Feed page wiring
    const socialFeedContainer = document.getElementById('social-feed-container');
    const postForm = document.getElementById('form-post-activity');
    if (socialFeedContainer) {
        async function loadFeed() {
            try {
                const data = await FitnessAPI.fetchSocialFeed();
                socialFeedContainer.textContent = '';
                (data.activities || []).forEach(post => {
                    const card = document.createElement('div');
                    card.className = 'card mb-3 shadow-sm border-0';
                    const cardBody = document.createElement('div');
                    cardBody.className = 'card-body';

                    const userHeader = document.createElement('div');
                    userHeader.className = 'd-flex align-items-center mb-2';
                    const img = document.createElement('img');
                    img.src = post.avatar_url || 'https://via.placeholder.com/40';
                    img.className = 'rounded-circle mr-3';
                    img.width = 40;
                    img.height = 40;
                    img.alt = post.screen_name;
                    const metaDiv = document.createElement('div');
                    const nameH6 = document.createElement('h6');
                    nameH6.className = 'mb-0 font-weight-bold';
                    nameH6.textContent = post.screen_name;
                    const dateSmall = document.createElement('small');
                    dateSmall.className = 'text-muted';
                    dateSmall.textContent = post.created_at;
                    metaDiv.appendChild(nameH6);
                    metaDiv.appendChild(dateSmall);
                    userHeader.appendChild(img);
                    userHeader.appendChild(metaDiv);

                    const titleH5 = document.createElement('h5');
                    titleH5.className = 'card-title text-primary';
                    titleH5.textContent = post.activity_title;

                    const statsDiv = document.createElement('div');
                    statsDiv.className = 'd-flex text-muted mb-2';

                    const spanDist = document.createElement('span');
                    spanDist.className = 'mr-3';
                    spanDist.textContent = `📏 ${Number(post.distance_km).toFixed(2)} km`;

                    const spanDur = document.createElement('span');
                    spanDur.className = 'mr-3';
                    spanDur.textContent = `⏱️ ${Number(post.duration_minutes)} mins`;

                    const spanPriv = document.createElement('span');
                    spanPriv.textContent = '🔒 500m Privacy Protected';

                    statsDiv.appendChild(spanDist);
                    statsDiv.appendChild(spanDur);
                    statsDiv.appendChild(spanPriv);

                    const likeBtn = document.createElement('button');
                    likeBtn.className = 'btn btn-sm btn-outline-danger btn-like';
                    likeBtn.textContent = `❤️ ${post.likes_count} Likes`;

                    cardBody.appendChild(userHeader);
                    cardBody.appendChild(titleH5);
                    cardBody.appendChild(statsDiv);
                    cardBody.appendChild(likeBtn);
                    card.appendChild(cardBody);
                    socialFeedContainer.appendChild(card);
                });
            } catch (err) {
                console.error('Failed to load social feed:', err);
            }
        }
        loadFeed();

        if (postForm) {
            postForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const title = document.getElementById('input-post-title').value;
                const dist = parseFloat(document.getElementById('input-post-distance').value || '5.0');
                const dur = parseInt(document.getElementById('input-post-duration').value || '30');

                try {
                    await FitnessAPI.createSocialPost(title, dist, dur, [
                        { lat: 40.7128, lng: -74.0060 },
                        { lat: 40.7200, lng: -74.0100 }
                    ]);
                    postForm.reset();
                    loadFeed();
                } catch (err) {
                    alert('Failed to publish activity post: ' + err.message);
                }
            });
        }
    }

    // 5. Account Deletion (GDPR/CCPA) Form
    const deleteForm = document.getElementById('form-account-deletion');
    if (deleteForm) {
        deleteForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('input-confirm-email').value;
            const reason = document.getElementById('input-deletion-reason').value;

            if (!confirm('Are you absolutely sure you want to permanently delete your account and all associated telemetry?')) {
                return;
            }

            try {
                const res = await FitnessAPI.requestAccountDeletion(email, reason, 1);
                alert(`Account successfully deleted under GDPR/CCPA. Purged ${res.records_purged} data records.`);
                window.location.href = 'index.html';
            } catch (err) {
                alert(`Deletion Error: ${err.message}`);
            }
        });
    }

    // 6. Privacy Settings Form
    const privacyForm = document.getElementById('form-privacy-settings');
    if (privacyForm) {
        try {
            const currentSettings = await FitnessAPI.fetchPrivacySettings(1);
            const radiusInput = document.getElementById('input-mask-radius');
            if (radiusInput) radiusInput.value = currentSettings.mask_radius_meters || 500;
        } catch (err) {
            console.warn('Could not load privacy settings:', err);
        }

        privacyForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const radius = parseInt(document.getElementById('input-mask-radius').value || '500');
            try {
                await FitnessAPI.updatePrivacySettings({ mask_radius_meters: radius }, 1);
                alert('Privacy zones and masking radius updated successfully.');
            } catch (err) {
                alert('Failed to update privacy settings: ' + err.message);
            }
        });
    }
});

if (typeof module !== 'undefined' && module.exports) {
    module.exports = { FitnessAPI };
}
