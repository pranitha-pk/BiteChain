// static/js/detail.js (Version 10.0 - FINAL)
document.addEventListener('DOMContentLoaded', () => {
    const detailsContainer = document.getElementById('details-container');
    const params = new URLSearchParams(window.location.search);
    const restaurantId = params.get('id');
    const loggedInUsername = localStorage.getItem('bitechain_username');
    if (!loggedInUsername) { window.location.href = 'login.html'; return; }

    const addFormFunctionality = () => {
        const reviewForm = document.getElementById('review-form'); if (!reviewForm) return;
        const starInputs = reviewForm.querySelectorAll('.star-input .fa-star'), ratingInput = document.getElementById('rating-value'), messageEl = document.getElementById('form-message');
        starInputs.forEach((star, index) => { star.addEventListener('click', () => { const r = index + 1; ratingInput.value = r; starInputs.forEach((s, i) => s.classList.toggle('filled', i < r)); }); });
        reviewForm.addEventListener('submit', async (e) => {
            e.preventDefault(); const rating = ratingInput.value; if (rating === '0') { messageEl.textContent = 'Please select a star rating.'; messageEl.style.color = 'var(--primary-color)'; return; }
            messageEl.textContent = 'Submitting...'; messageEl.style.color = 'var(--text-muted)';
            try {
                const response = await fetch('/api/submit-review', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ restaurant_id: restaurantId, rating, feedback: document.getElementById('feedback-text').value, username: loggedInUsername }) });
                const result = await response.json(); if (!response.ok) throw new Error(result.error || 'Server error.');
                messageEl.textContent = "✅ " + result.message; messageEl.style.color = 'green'; reviewForm.reset(); starInputs.forEach(s => s.classList.remove('filled')); ratingInput.value = '0';
                setTimeout(fetchDetails, 2000);
            } catch (error) { messageEl.textContent = `Error: ${error.message}`; messageEl.style.color = 'var(--primary-color)'; }
        });
    };
    const addVerificationFunctionality = () => {
        document.querySelectorAll('.verify-btn').forEach(button => { button.addEventListener('click', async () => { const reviewId = button.dataset.reviewId; button.disabled = true; button.innerHTML = '<i class="fas fa-check-circle"></i> Verifying...'; try { const response = await fetch('/api/verify-review', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ review_id: reviewId }) }); const result = await response.json(); if (!response.ok) throw new Error(result.error); button.nextElementSibling.textContent = `${result.new_count} Verifications`; button.innerHTML = '<i class="fas fa-check-circle"></i> Verified!'; } catch (error) { console.error('Verification failed:', error); button.innerHTML = 'Error!'; } }); });
    };
    const addTagVotingFunctionality = () => {
        document.querySelectorAll('.vote-tag-btn').forEach(button => { button.addEventListener('click', async () => { const tagId = button.dataset.tagId; document.querySelectorAll('.vote-tag-btn').forEach(btn => btn.disabled = true); try { const response = await fetch('/api/vote-tag', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ tag_id: tagId }) }); const result = await response.json(); if (!response.ok) throw new Error(result.error); fetchDetails(); } catch (error) { console.error('Tag vote failed:', error); button.textContent = 'Error!'; document.querySelectorAll('.vote-tag-btn').forEach(btn => btn.disabled = false); } }); });
    };
    const renderDetails = ({ restaurant, reviews, tags }) => {
        document.title = `${restaurant.name} - BiteChain`;
        const createStars = (r) => Array.from({ length: 5 }, (_, i) => `<i class="fa-solid fa-star ${i < r ? 'filled' : ''}"></i>`).join('');
        const reviewsHTML = reviews.length > 0 ? reviews.map(r => `<div class="review-card"><div class="review-header"><span class="review-author">@${r.username}</span><div class="star-rating">${createStars(r.rating)}</div></div><p class="review-text">"${r.feedback_text}"</p><div class="review-actions"><button class="verify-btn" data-review-id="${r.id}"><i class="fas fa-check-circle"></i> Verify</button><span class="verify-count">${r.verifications} Verifications</span></div></div>`).join('') : '<p>Be the first to leave a review!</p>';
        const totalVotes = tags.reduce((sum, tag) => sum + tag.votes, 0);
        const pollHTML = tags.length > 0 ? tags.map(tag => { const percentage = totalVotes > 0 ? (tag.votes / totalVotes) * 100 : 0; return `<div class="poll-item"><span class="poll-tag-name">${tag.tag_name}</span><div class="poll-bar"><div class="poll-progress" style="width: ${percentage}%"></div></div><span class="poll-votes">${tag.votes} votes</span><button class="vote-tag-btn" data-tag-id="${tag.id}">Vote</button></div>`; }).join('') : '<p>No community tags yet.</p>';
        detailsContainer.innerHTML = `<div class="detail-header"><img src="${restaurant.image_url}" alt="${restaurant.name}" class="detail-img"><div class="detail-info glass-card"><h1>${restaurant.name}</h1><p class="detail-subheading">${restaurant.cuisine} • ${restaurant.vibe}</p><div class="detail-meta"><span><i class="fas fa-money-bill-wave"></i> Cost: ${restaurant.cost}</span><span><i class="fas fa-map-marker-alt"></i> Location: ${restaurant.location}</span></div></div></div><section class="community-poll-section"><h2>Community Poll</h2><div class="poll-list">${pollHTML}</div></section><section class="feedback-section"><h2>Community Votes & Reviews</h2><div class="review-list">${reviewsHTML}</div><form id="review-form" class="glass-card review-form"><h3>Cast Your Vote</h3><p>Your vote is permanent and secured on the BiteChain!</p><div class="star-input"><span>Rate: </span>${createStars(0)}</div><input type="hidden" id="rating-value" value="0"><textarea id="feedback-text" placeholder="Tell us about your experience..." required></textarea><button type="submit">Submit Review</button><p id="form-message"></p></form></section>`;
        addFormFunctionality(); addVerificationFunctionality(); addTagVotingFunctionality();
    };
    const fetchDetails = async () => {
        if (!restaurantId) { detailsContainer.innerHTML = '<p class="error-message">Restaurant not found.</p>'; return; }
        try { const response = await fetch(`/api/restaurant-details?id=${restaurantId}`); if (!response.ok) throw new Error('Failed to fetch details.'); const data = await response.json(); renderDetails(data); } catch (error) { console.error('Fetch error:', error); detailsContainer.innerHTML = `<p class="error-message">Could not load restaurant details.</p>`; }
    };
    fetchDetails();
});