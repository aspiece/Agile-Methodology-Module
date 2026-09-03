document.querySelector('.menu-button')?.addEventListener('click', event => {
  const nav = document.querySelector('#course-nav');
  const open = nav.classList.toggle('open');
  event.currentTarget.setAttribute('aria-expanded', String(open));
});

document.querySelectorAll('.question').forEach(question => {
  const button = question.querySelector('.check-answer');
  const feedback = question.querySelector('.feedback');
  if (!button || !feedback) return;
  button.addEventListener('click', () => {
    const correct = JSON.parse(question.dataset.correct || '[]');
    const selected = [...question.querySelectorAll('input:checked')].map(input => input.value);
    if (!selected.length) {
      feedback.textContent = 'Choose an answer first.';
      feedback.classList.add('incorrect');
      feedback.hidden = false;
      return;
    }
    const isCorrect = selected.length === correct.length && selected.every(value => correct.includes(value));
    feedback.textContent = isCorrect
      ? question.dataset.feedbackCorrect || 'Correct.'
      : question.dataset.feedbackIncorrect || 'Review the idea above and try again.';
    feedback.classList.toggle('incorrect', !isCorrect);
    feedback.hidden = false;
  });
});

document.querySelectorAll('textarea').forEach((field, index) => {
  const key = `course-template-${document.body.dataset.lesson || 'home'}-${index}`;
  field.value = localStorage.getItem(key) || '';
  field.addEventListener('input', () => localStorage.setItem(key, field.value));
});

const stepper = document.querySelector('.stepper');
if (stepper) {
  const steps = [...stepper.querySelectorAll('.lesson-step')];
  const previous = document.querySelector('#previous-step');
  const next = document.querySelector('#next-step');
  const progress = document.querySelector('[role="progressbar"]');
  const fill = progress.querySelector('span');
  const status = document.querySelector('#step-status');
  const count = document.querySelector('#step-count');
  const announcement = document.querySelector('#step-announcement');
  const key = `course-template-lesson-${document.body.dataset.lesson}-step`;
  const requested = Number(new URLSearchParams(location.search).get('step')) - 1;
  let current = Number.isInteger(requested) && requested >= 0 ? requested : Number(localStorage.getItem(key) || 0);

  function show(index, moveFocus = false) {
    current = Math.min(Math.max(index, 0), steps.length - 1);
    steps.forEach((step, stepIndex) => { step.hidden = stepIndex !== current; });
    const label = steps[current].dataset.stepLabel;
    const percent = ((current + 1) / steps.length) * 100;
    status.textContent = `Step ${label}`;
    count.textContent = `${current + 1} of ${steps.length}`;
    progress.setAttribute('aria-valuenow', String(current + 1));
    progress.setAttribute('aria-valuemax', String(steps.length));
    progress.setAttribute('aria-valuetext', `Step ${current + 1} of ${steps.length}`);
    fill.style.width = `${percent}%`;
    previous.disabled = current === 0;
    next.disabled = false;
    next.textContent = current === steps.length - 1 ? 'Finish lesson ✓' : 'Next step →';
    localStorage.setItem(key, String(current));
    history.replaceState(null, '', `${location.pathname}?step=${current + 1}`);
    announcement.textContent = `Now showing step ${label}, ${current + 1} of ${steps.length}.`;
    if (moveFocus) {
      const heading = steps[current].querySelector('h2');
      if (heading) { heading.tabIndex = -1; heading.focus(); }
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  previous.addEventListener('click', () => show(current - 1, true));
  next.addEventListener('click', () => {
    if (current === steps.length - 1) {
      next.textContent = 'Lesson complete ✓';
      next.disabled = true;
      announcement.textContent = 'Lesson complete. Return to your course for any required submission.';
      return;
    }
    show(current + 1, true);
  });
  show(current);
}

document.querySelectorAll('a[href^="http"]').forEach(link => {
  link.target = '_blank';
  link.rel = 'noopener noreferrer';
  if (!link.querySelector('.external-link-label')) {
    const note = document.createElement('span');
    note.className = 'sr-only external-link-label';
    note.textContent = ' (opens in a new tab)';
    link.append(note);
  }
});

const vocabularyLinks = [...document.querySelectorAll('.vocab-link')];
if (vocabularyLinks.length) {
  const dialog = document.createElement('dialog');
  dialog.className = 'vocabulary-dialog';
  dialog.setAttribute('aria-labelledby', 'vocabulary-dialog-term');
  dialog.innerHTML = '<button class="vocabulary-dialog-close" type="button" aria-label="Close definition">Close</button><h2 id="vocabulary-dialog-term"></h2><p></p>';
  document.body.append(dialog);
  const term = dialog.querySelector('h2');
  const definition = dialog.querySelector('p');
  const close = dialog.querySelector('.vocabulary-dialog-close');
  let returnFocus;
  vocabularyLinks.forEach(link => link.addEventListener('click', () => {
    term.textContent = link.dataset.term;
    definition.textContent = link.dataset.definition;
    returnFocus = link;
    dialog.showModal();
    close.focus();
  }));
  close.addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => returnFocus?.focus());
}

const zoomButtons = [...document.querySelectorAll('.image-zoom')];
if (zoomButtons.length) {
  const dialog = document.createElement('dialog');
  dialog.className = 'image-dialog';
  dialog.setAttribute('aria-label', 'Enlarged lesson image');
  dialog.innerHTML = '<button class="image-dialog-close" type="button">Close</button><img alt="">';
  document.body.append(dialog);
  const image = dialog.querySelector('img');
  const close = dialog.querySelector('.image-dialog-close');
  let returnFocus;
  zoomButtons.forEach(button => button.addEventListener('click', () => {
    const source = button.querySelector('img');
    image.src = source.currentSrc || source.src;
    image.alt = source.alt;
    returnFocus = button;
    dialog.showModal();
    close.focus();
  }));
  close.addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => returnFocus?.focus());
}

document.querySelectorAll('.program-application').forEach(activity => {
  const select = activity.querySelector('select');
  const start = activity.querySelector('.program-start');
  const cards = [...activity.querySelectorAll('[data-program]')];
  if (!select || !start) return;
  start.addEventListener('click', () => {
    if (!select.value) {
      select.focus();
      return;
    }
    cards.forEach(card => { card.hidden = card.dataset.program !== select.value; });
    const active = cards.find(card => !card.hidden);
    active?.querySelector('textarea, button')?.focus();
  });
  cards.forEach(card => {
    const button = card.querySelector('.scenario-exemplar');
    const feedback = card.querySelector('.exemplar-feedback');
    button?.addEventListener('click', () => {
      const fields = [...card.querySelectorAll('textarea')];
      if (fields.some(field => !field.value.trim())) {
        feedback.textContent = 'Complete each response before comparing your thinking with the exemplar.';
        feedback.classList.add('incorrect');
      } else {
        feedback.textContent = feedback.dataset.exemplar || feedback.textContent;
        feedback.classList.remove('incorrect');
        select.disabled = false;
      }
      feedback.hidden = false;
    });
    if (feedback) feedback.dataset.exemplar = feedback.textContent;
  });
});
