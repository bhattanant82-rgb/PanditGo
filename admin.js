fetch('http://localhost:5000/admin/pandits')
.then(res => res.json())
.then(data => {
  let html = '';
  data.forEach(p => {
    html += `
      <div>
        <b>${p.name}</b> (${p.city})
        <button onclick="approve(${p.id})">Approve</button>
      </div>
    `;
  });
  document.getElementById('list').innerHTML = html;
});

function approve(id) {
  fetch(`http://localhost:5000/admin/approve-pandit/${id}`, {
    method: 'POST'
  }).then(() => location.reload());
}
