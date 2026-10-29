(() => {
  const root = document.querySelector('[data-checkout]');
  if (!root) return;
  const error = root.querySelector('[role="alert"]');
  if (error) error.focus();
  const labels = {
    quote: 'Calculando envío…', select: 'Preparando resumen…',
    pay: 'Abriendo pago seguro…', resume: 'Retomando pago…', refresh: 'Verificando pago…',
  };
  root.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', event => {
      if (form.getAttribute('aria-busy') === 'true') {
        event.preventDefault();
        return;
      }
      const button = event.submitter;
      const label = labels[button?.value] || 'Procesando tu solicitud…';
      form.dataset.loadingMessage = label;
      if (button && button.name) {
        const action = document.createElement('input');
        action.type = 'hidden'; action.name = button.name; action.value = button.value;
        action.dataset.submitAction = 'true'; form.append(action);
      }
      form.setAttribute('aria-busy', 'true');
      form.querySelectorAll('button').forEach(control => {
        control.dataset.wasDisabled = String(control.disabled);
        control.disabled = true;
      });
      if (button) {
        button.dataset.idleMarkup = button.innerHTML;
        button.dataset.submitting = 'true';
        button.replaceChildren();
        const spinner = document.createElement('span');
        spinner.className = 'loading-spinner'; spinner.setAttribute('aria-hidden', 'true');
        button.append(spinner, document.createTextNode(label));
      }
      const feedback = root.querySelector('[data-payment-feedback]');
      if (feedback) feedback.textContent = label;
    });
  });
  window.addEventListener('pageshow', () => {
    root.querySelectorAll('form[aria-busy="true"]').forEach(form => {
      form.removeAttribute('aria-busy');
      form.querySelectorAll('button').forEach(button => {
        button.disabled = button.dataset.wasDisabled === 'true';
        delete button.dataset.wasDisabled;
        if (button.dataset.submitting) {
          button.innerHTML = button.dataset.idleMarkup;
          delete button.dataset.submitting; delete button.dataset.idleMarkup;
        }
      });
      delete form.dataset.loadingMessage;
      form.querySelectorAll('[data-submit-action]').forEach(input => input.remove());
    });
    const feedback = root.querySelector('[data-payment-feedback]');
    if (feedback) feedback.textContent = '';
  });
})();
