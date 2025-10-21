document.addEventListener('DOMContentLoaded', function () {
  var pills = Array.prototype.slice.call(document.querySelectorAll('.type-pill'));
  var cards = Array.prototype.slice.call(document.querySelectorAll('.region-card'));
  var ctas = Array.prototype.slice.call(document.querySelectorAll('.region-cta'));
  var themeToggle = document.getElementById('themeToggle');
  var themeIcon = themeToggle.querySelector('.theme-icon');
  var regionLinks = Array.prototype.slice.call(document.querySelectorAll('a[data-slug]'));
  var categoryItems = Array.prototype.slice.call(document.querySelectorAll('.category-item'));

  function setActive(type) {
    pills.forEach(function (p) {
      var isActive = p.getAttribute('data-type') === type;
      p.classList.toggle('is-active', isActive);
      p.setAttribute('aria-selected', String(isActive));
    });

    cards.forEach(function (c) {
      var allowed = (c.getAttribute('data-type') || '').split(/\s+/);
      var visible = allowed.indexOf(type) !== -1;
      c.style.display = visible ? '' : 'none';
    });

    ctas.forEach(function (a) {
      var isMatch = a.getAttribute('data-cta-type') === type;
      a.style.display = isMatch ? 'inline-block' : 'none';
    });
  }

  pills.forEach(function (p) {
    p.addEventListener('click', function () {
      setActive(p.getAttribute('data-type'));
    });
  });

  // Theme toggle functionality
  function toggleTheme() {
    var html = document.documentElement;
    var isDark = html.getAttribute('data-theme') === 'dark';
    
    if (isDark) {
      html.removeAttribute('data-theme');
      themeIcon.textContent = '🌙';
      localStorage.setItem('theme', 'light');
    } else {
      html.setAttribute('data-theme', 'dark');
      themeIcon.textContent = '☀️';
      localStorage.setItem('theme', 'dark');
    }
  }

  // Initialize theme from localStorage or system preference
  function initTheme() {
    var savedTheme = localStorage.getItem('theme');
    var prefersDark = false; //window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
      document.documentElement.setAttribute('data-theme', 'dark');
      themeIcon.textContent = '☀️';
    } else {
      themeIcon.textContent = '🌙';
    }
  }

  // Map interaction functionality
  function handleRegionClick(region) {
    // Find the corresponding region card
    var regionCard = document.querySelector('[data-type*="' + region + '"]');
    if (regionCard) {
      // Scroll to the region cards section
      regionCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
      
      // Highlight the clicked region card temporarily
      regionCard.style.transform = 'scale(1.02)';
      regionCard.style.boxShadow = '0 8px 25px rgba(0,0,0,0.15)';
      
      setTimeout(function() {
        regionCard.style.transform = '';
        regionCard.style.boxShadow = '';
      }, 1000);
    }
  }

  // Event listeners
  themeToggle.addEventListener('click', toggleTheme);
  
  // Map region click handlers
  regionLinks.forEach(function(link) {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      var slug = this.getAttribute('data-slug');
      
      // Map slug to region name for card matching
      var slugToRegion = {
        'bozen': 'bolzano',
        'burggrafenamt': 'merano',
        'eisacktal': 'bressanone',
        'pustertal': 'val-pusteria',
        'wipptal': 'val-venosta',
        'unterland': 'val-venosta',
        'saltenschlern': 'alpe-di-siusi',
        'vinschgau': 'val-venosta'
      };
      
      var region = slugToRegion[slug] || slug;
      handleRegionClick(region);
    });
  });

  // Category click handlers
  categoryItems.forEach(function(item) {
    item.addEventListener('click', function() {
      var categoryName = this.querySelector('.category-name').textContent.toLowerCase();
      
      // Map category names to property types
      var typeMapping = {
        'residential': 'residential',
        'commercial': 'commercial',
        'hospitality': 'commercial',
        'mountain properties': 'investment',
        'agricultural': 'investment',
        'development': 'investment',
        'investment': 'investment',
        'historic properties': 'residential'
      };
      
      var targetType = typeMapping[categoryName] || 'residential';
      
      // Set the active type pill
      setActive(targetType);
      
      // Scroll to the type selector
      document.getElementById('types').scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
  });

  // initialize current year, default filter, and theme
  var yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());
  setActive('residential');
  initTheme();
});

