document.addEventListener('DOMContentLoaded', () => {
    loadPandits();
    document.getElementById('addPanditForm').addEventListener('submit', addPandit);
});

async function loadPandits() {
    try {
        const response = await fetch('/admin/pandits');
        const pandits = await response.json();
        const tbody = document.querySelector('#panditsTable tbody');
        tbody.innerHTML = '';
        pandits.forEach(pandit => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${pandit.name}</td>
                <td>${pandit.city}</td>
                <td>${pandit.availability}</td>
                <td>${pandit.status}</td>
                <td>
                    <button onclick="editPandit('${pandit._id}')">Edit</button>
                    <button onclick="deletePandit('${pandit._id}')">Delete</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading pandits:', error);
    }
}

async function addPandit(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData);
    data.languages = data.languages ? data.languages.split(',').map(l => l.trim()) : [];
    data.experience = parseInt(data.experience) || 0;
    data.chat_price_per_min = parseFloat(data.chat_price_per_min);
    data.call_price_per_min = parseFloat(data.call_price_per_min);
    try {
        const response = await fetch('/admin/pandits', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (response.ok) {
            alert('Pandit added successfully');
            event.target.reset();
            loadPandits();
        } else {
            alert('Error adding pandit');
        }
    } catch (error) {
        console.error('Error adding pandit:', error);
    }
}

async function deletePandit(id) {
    if (confirm('Are you sure you want to delete this pandit?')) {
        try {
            const response = await fetch(`/admin/pandits/${id}`, {
                method: 'DELETE'
            });
            if (response.ok) {
                loadPandits();
            } else {
                alert('Error deleting pandit');
            }
        } catch (error) {
            console.error('Error deleting pandit:', error);
        }

    }
}

function editPandit(id) {
    // For simplicity, redirect to edit page or show modal
    alert('Edit functionality not implemented yet');
}