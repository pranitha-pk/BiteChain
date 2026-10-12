// static/js/script.js (Version 10.1 - FINAL)
document.addEventListener('DOMContentLoaded', () => {
    if (!localStorage.getItem('bitechain_username')) { window.location.href = 'login.html'; return; }
    const grid = document.getElementById('restaurant-grid'), searchInput = document.getElementById('search-input'), filterButtons = document.querySelectorAll('.filter-btn:not(.near-me-btn)'), adventureBtn = document.getElementById('adventure-btn'), nearMeBtn = document.getElementById('near-me-btn'), themeToggleBtn = document.getElementById('theme-toggle-btn'), body = document.documentElement, keywordMenu = document.getElementById('keyword-menu'), keywordBtn = document.getElementById('keyword-btn');
    const foodKeywords = ['Dosa','Idli','Vada','Biryani','Thali','Parotta','Pizza','Burger','Pasta','Noodles','Ramen','Sushi','Tacos','Shawarma','Kebab','Grilled Chicken','Steak','Seafood','Prawns','Crab','Paneer Tikka','Dal Makhani','Naan','Chole Bhature','Samosa','Jalebi','Cheesecake','Milkshake','Coffee','Tea','Lassi','Mocktails','Soup','Salad','Sandwich','Fries','Momos','Manchurian','Fried Rice','Butter Chicken','Tandoori Chicken', 'Sambar', 'Filter Coffee', 'Rava Idli', 'Mandi Rice', 'Falooda', 'Sizzler'];
    foodKeywords.sort().forEach(keyword => { 
        const li = document.createElement('li'); 
        li.textContent = keyword; 
        li.addEventListener('click', () => { 
            searchInput.value = keyword; 
            currentFilters.search = keyword;
            keywordMenu.style.display = 'none'; 
            fetchRestaurants();
        }); 
        keywordMenu.appendChild(li); 
    });
    let currentFilters = { dietary: null, fitness: null, search: '', adventure: false, near_me: false, location: localStorage.getItem('bitechain_location') || 'Chennai' };
    let debounceTimer;
    const fetchRestaurants = async () => {
        grid.innerHTML = '<div class="loader"></div>'; const params = new URLSearchParams();
        for (const key in currentFilters) { if (currentFilters[key]) params.append(key, currentFilters[key]); }
        try { const response = await fetch(`/api/restaurants?${params.toString()}`); if (!response.ok) throw new Error('Network response was not ok'); const restaurants = await response.json(); renderRestaurants(restaurants); } catch (error) { grid.innerHTML = `<p class="error-message">Could not fetch restaurants.</p>`; console.error('Fetch error:', error); }
    };
    const renderRestaurants = (restaurants) => {
        grid.innerHTML = ''; if (restaurants.length === 0) { grid.innerHTML = `<p class="error-message">No restaurants match your criteria in our current database!</p>`; return; }
        restaurants.forEach(r => { const card = document.createElement('a'); card.className = 'restaurant-card'; card.href = `restaurant.html?id=${r.id}`; card.innerHTML = `<img src="${r.image_url}" alt="${r.name}"><div class="card-content"><h3>${r.name}</h3><p>${r.cuisine} • <span class="cost">${r.cost}</span></p></div>`; grid.appendChild(card); });
    };
    keywordBtn.addEventListener('click', (e) => { e.stopPropagation(); keywordMenu.style.display = keywordMenu.style.display === 'block' ? 'none' : 'block'; });
    document.addEventListener('click', () => { keywordMenu.style.display = 'none'; });
    filterButtons.forEach(button => { button.addEventListener('click', () => { const filterType = button.dataset.filterType, filterValue = button.dataset.filterValue; if (button.classList.contains('active')) { button.classList.remove('active'); currentFilters[filterType] = null; } else { document.querySelectorAll(`[data-filter-type="${filterType}"]`).forEach(btn => btn.classList.remove('active')); button.classList.add('active'); currentFilters[filterType] = filterValue; } fetchRestaurants(); }); });
    nearMeBtn.addEventListener('click', () => { nearMeBtn.classList.toggle('active'); currentFilters.near_me = nearMeBtn.classList.contains('active'); fetchRestaurants(); });
    adventureBtn.addEventListener('click', () => { currentFilters.adventure = true; fetchRestaurants(); currentFilters.adventure = false; });
    searchInput.addEventListener('keyup', () => { clearTimeout(debounceTimer); debounceTimer = setTimeout(() => { currentFilters.search = searchInput.value; fetchRestaurants(); }, 300); });
    themeToggleBtn.addEventListener('click', () => {
        const isDark = body.classList.contains('dark-theme');
        const newTheme = isDark ? 'light-theme' : 'dark-theme';
        body.className = newTheme;
        localStorage.setItem('bitechain_theme', newTheme);
    });
    fetchRestaurants();
});