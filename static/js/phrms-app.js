/**
 * Personal Health Record Management and Sharing System (PHRMS)
 * Interactive Application Scripts (phrms-app.js)
 */

document.addEventListener('DOMContentLoaded', () => {
  initRecordSelectors();
  initCategoryFilters();
  initDocumentViewer();
  initModalTriggers();
});

/**
 * 1. Timeline Checkbox Counter for Consultation Summary Builder (FR08)
 */
function initRecordSelectors() {
  const checkboxes = document.querySelectorAll('.record-selector');
  const countSpan = document.getElementById('selectedCount');
  const counterBtn = document.getElementById('packetCounterBtn');

  function updateCounter() {
    const checked = document.querySelectorAll('.record-selector:checked');
    if (countSpan) {
      countSpan.textContent = checked.length;
    }
    if (counterBtn) {
      if (checked.length === 0) {
        counterBtn.classList.add('opacity-50');
      } else {
        counterBtn.classList.remove('opacity-50');
      }
    }
  }

  checkboxes.forEach(cb => {
    cb.addEventListener('change', updateCounter);
  });

  updateCounter();
}

/**
 * 2. Category Filtering on Chronological Timeline
 */
function initCategoryFilters() {
  const filterBtns = document.querySelectorAll('.filter-pill-btn');
  const timelineItems = document.querySelectorAll('.timeline-item');

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => {
        b.classList.remove('btn-surgical', 'text-white');
        b.classList.add('btn-outline');
      });
      btn.classList.remove('btn-outline');
      btn.classList.add('btn-surgical');

      const selectedCategory = btn.getAttribute('data-category');

      timelineItems.forEach(item => {
        const itemCat = item.getAttribute('data-category');
        if (selectedCategory === 'ALL' || itemCat === selectedCategory) {
          item.style.display = 'block';
        } else {
          item.style.display = 'none';
        }
      });
    });
  });
}

/**
 * 3. Document Inspection Viewport (Zoom & Rotate)
 */
function initDocumentViewer() {
  let currentZoom = 100;
  let currentRotation = 0;
  const canvas = document.getElementById('document-canvas');
  const zoomDisplay = document.getElementById('zoom-level');

  const zoomInBtn = document.getElementById('zoom-in');
  const zoomOutBtn = document.getElementById('zoom-out');
  const rotateBtn = document.getElementById('rotate-btn');

  function applyTransform() {
    if (canvas) {
      canvas.style.transform = `scale(${currentZoom / 100}) rotate(${currentRotation}deg)`;
    }
    if (zoomDisplay) {
      zoomDisplay.textContent = `${currentZoom}%`;
    }
  }

  if (zoomInBtn) {
    zoomInBtn.addEventListener('click', () => {
      if (currentZoom < 180) {
        currentZoom += 15;
        applyTransform();
      }
    });
  }

  if (zoomOutBtn) {
    zoomOutBtn.addEventListener('click', () => {
      if (currentZoom > 60) {
        currentZoom -= 15;
        applyTransform();
      }
    });
  }

  if (rotateBtn) {
    rotateBtn.addEventListener('click', () => {
      currentRotation = (currentRotation + 90) % 360;
      applyTransform();
    });
  }
}

/**
 * 4. Modal Openers and Closers
 */
function initModalTriggers() {
  // Close any modal on clicking [data-close-modal]
  document.querySelectorAll('[data-close-modal]').forEach(el => {
    el.addEventListener('click', () => {
      const modal = el.closest('.modal-backdrop');
      if (modal) modal.style.display = 'none';
    });
  });

  // Close modal when clicking outside of modal container
  document.querySelectorAll('.modal-backdrop').forEach(modal => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.style.display = 'none';
      }
    });
  });
}

function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.style.display = 'flex';
  }
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.style.display = 'none';
  }
}

/**
 * Open Resubmit Modal populated with record metadata
 */
function openResubmitModal(recordId, title, category, provider, dateStr, notes) {
  const modal = document.getElementById('resubmitRecordModal');
  const form = document.getElementById('resubmitForm');
  if (modal && form) {
    form.action = `/patient/records/${recordId}/resubmit`;
    document.getElementById('resubmit_title').value = title;
    document.getElementById('resubmit_category').value = category;
    document.getElementById('resubmit_provider').value = provider;
    document.getElementById('resubmit_date').value = dateStr;
    document.getElementById('resubmit_notes').value = notes || '';
    modal.style.display = 'flex';
  }
}
