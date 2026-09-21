class SearchBox {
  constructor(inputId) {
    this.input = document.getElementById(inputId);
    if (!this.input) return;
    
    this.dropdown = document.createElement('div');
    this.dropdown.className = 'search-dropdown';
    this.dropdown.style.cssText = 'position: absolute; top: 100%; left: 0; right: 0; background: var(--color-card); border: 1px solid var(--color-border); border-radius: 4px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); z-index: 1000; display: none; max-height: 300px; overflow-y: auto;';
    
    this.input.parentNode.style.position = 'relative';
    this.input.parentNode.appendChild(this.dropdown);
    
    this.timeout = null;
    this.input.addEventListener('input', (e) => this.onInput(e));
    document.addEventListener('click', (e) => {
      if (!this.input.contains(e.target) && !this.dropdown.contains(e.target)) {
        this.hideSuggestions();
      }
    });
  }
  
  onInput(e) {
    clearTimeout(this.timeout);
    const query = e.target.value.trim();
    if (query.length < 2) {
      this.hideSuggestions();
      return;
    }
    
    this.timeout = setTimeout(() => this.fetchSuggestions(query), 300);
  }
  
  async fetchSuggestions(query) {
    // Simulated fetch
    const results = [
      { title: `Search for "${query}" in Gurus`, type: 'Guru', url: `/guru?q=${query}` },
      { title: `Search for "${query}" in Granthalaya`, type: 'Book', url: `/granthalaya?q=${query}` }
    ];
    this.renderSuggestions(results);
  }
  
  renderSuggestions(results) {
    this.dropdown.innerHTML = '';
    if (results.length === 0) {
      this.dropdown.innerHTML = '<div style="padding: 10px; color: var(--color-text-muted);">No results found</div>';
    } else {
      results.forEach(res => {
        const item = document.createElement('a');
        item.href = res.url;
        item.style.cssText = 'display: block; padding: 10px; border-bottom: 1px solid var(--color-border); color: var(--color-text); text-decoration: none;';
        item.innerHTML = `<strong>${res.title}</strong> <span style="font-size: 0.8rem; background: var(--color-gold); color: white; padding: 2px 6px; border-radius: 8px; margin-left: 10px;">${res.type}</span>`;
        item.addEventListener('mouseenter', () => item.style.background = 'var(--color-card-hover)');
        item.addEventListener('mouseleave', () => item.style.background = 'transparent');
        this.dropdown.appendChild(item);
      });
    }
    this.dropdown.style.display = 'block';
  }
  
  hideSuggestions() {
    this.dropdown.style.display = 'none';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  new SearchBox('main-search');
});
