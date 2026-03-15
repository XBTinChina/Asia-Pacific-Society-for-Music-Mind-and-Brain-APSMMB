document.addEventListener('DOMContentLoaded', () => {

  // Mobile navigation toggle
  const hamburger = document.querySelector('.hamburger');
  const navMenu = document.querySelector('nav ul');

  if (hamburger && navMenu) {
    hamburger.addEventListener('click', () => {
      navMenu.classList.toggle('open');
    });
    document.addEventListener('click', (e) => {
      if (!hamburger.contains(e.target) && !navMenu.contains(e.target)) {
        navMenu.classList.remove('open');
      }
    });
  }

  // Active nav link
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('nav ul li a').forEach(link => {
    if (link.getAttribute('href') === currentPage) {
      link.classList.add('active');
    }
  });

  // Accordion
  document.querySelectorAll('.accordion-header').forEach(header => {
    header.addEventListener('click', () => {
      const body = header.nextElementSibling;
      const isOpen = body.classList.contains('open');
      document.querySelectorAll('.accordion-body').forEach(b => b.classList.remove('open'));
      document.querySelectorAll('.accordion-header').forEach(h => h.classList.remove('active'));
      if (!isOpen) {
        body.classList.add('open');
        header.classList.add('active');
      }
    });
  });

  // Contact form validation
  const contactForm = document.getElementById('contact-form');
  if (contactForm) {
    contactForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const name = document.getElementById('name')?.value.trim();
      const email = document.getElementById('email')?.value.trim();
      const message = document.getElementById('message')?.value.trim();
      if (!name || !email || !message) {
        alert('Please fill in all required fields.');
        return;
      }
      const btn = contactForm.querySelector('button[type="submit"]');
      btn.textContent = 'Message Sent';
      btn.disabled = true;
      btn.style.backgroundColor = 'var(--teal)';
    });
  }

  // Membership form validation
  const memberForm = document.getElementById('membership-form');
  if (memberForm) {
    memberForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const agree = document.getElementById('coc-agree')?.checked;
      if (!agree) {
        alert('Please agree to the Code of Conduct to proceed.');
        return;
      }
      const btn = memberForm.querySelector('button[type="submit"]');
      btn.textContent = 'Application Submitted';
      btn.disabled = true;
      btn.style.backgroundColor = 'var(--teal)';
    });
  }

  // Event filter
  const filterBtns = document.querySelectorAll('.filter-btn');
  if (filterBtns.length > 0) {
    filterBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        filterBtns.forEach(b => b.classList.remove('active-filter'));
        btn.classList.add('active-filter');
        const filter = btn.dataset.filter;
        document.querySelectorAll('.event-card').forEach(card => {
          card.style.display = (filter === 'all' || card.dataset.type === filter) ? 'flex' : 'none';
        });
      });
    });
  }

  // Newsletter form
  const newsletterForm = document.getElementById('newsletter-form');
  if (newsletterForm) {
    newsletterForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const email = newsletterForm.querySelector('input[type="email"]')?.value.trim();
      if (!email) { alert('Please enter a valid email.'); return; }
      const btn = newsletterForm.querySelector('button');
      btn.textContent = 'Subscribed!';
      btn.disabled = true;
      btn.style.backgroundColor = 'var(--teal)';
    });
  }

});
