async function send(path, data) {
  const response = await fetch(path, {method: 'POST', credentials: 'same-origin',
    headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)});
  const result = await response.json();
  if (!response.ok) throw new Error(result.detail || 'Request failed.');
  return result;
}
for (const name of ['login', 'chat', 'credentials']) {
  document.getElementById(name).addEventListener('submit', async event => {
    event.preventDefault();
    const form = event.currentTarget;
    const data = Object.fromEntries(new FormData(form));
    if (name === 'credentials') data.employee_id = data.employee_id ? Number(data.employee_id) : null;
    // Clear password inputs immediately; never add them to the chat DOM/history.
    for (const input of form.querySelectorAll('input[type=password]')) input.value = '';
    try {
      const result = await send('/api/' + name, data);
      document.getElementById(name === 'chat' ? 'answer' : 'status').textContent =
        result.answer || JSON.stringify(result);
    } catch (error) { document.getElementById('status').textContent = error.message; }
    finally { if ('password' in data) data.password = ''; }
  });
}
document.getElementById('logout').onclick = async () => {
  try { await send('/api/logout', {}); document.getElementById('status').textContent = 'Signed out.';
    document.getElementById('answer').textContent = ''; }
  catch (error) { document.getElementById('status').textContent = error.message; }
};
