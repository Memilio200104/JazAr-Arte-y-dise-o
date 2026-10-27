(() => {
  const root = document.querySelector('[data-checkout]');
  if (!root) return;
  const error = root.querySelector('[role="alert"]');
  if (error) error.focus();
  root.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', event => {
      if (form.getAttribute('aria-busy') === 'true') {
        event.preventDefault();
        return;
      }
      const button = event.submitter;
      if (button && button.name) {
        const action = document.createElement('input');
        action.type = 'hidden'; action.name = button.name; action.value = button.value;
        action.dataset.submitAction = 'true'; form.append(action);
      }
      form.setAttribute('aria-busy', 'true');
      form.querySelectorAll('button').forEach(control => { control.disabled = true; });
      const feedback = root.querySelector('[data-payment-feedback]');
      if (feedback) feedback.textContent = 'Procesando tu solicitud\u2026';
    });
  });
  window.addEventListener('pageshow', () => {
    root.querySelectorAll('form[aria-busy="true"]').forEach(form => {
      form.removeAttribute('aria-busy');
      form.querySelectorAll('button').forEach(button => { button.disabled = false; });
      form.querySelectorAll('[data-submit-action]').forEach(input => input.remove());
    });
    const feedback = root.querySelector('[data-payment-feedback]');
    if (feedback) feedback.textContent = '';
  });
})();
