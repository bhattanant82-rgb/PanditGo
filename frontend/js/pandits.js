// Load pandits from API
async function loadPandits() {
    try {
        const response = await fetch('/api/pandits');
        const pandits = await response.json();
        
        const container = document.getElementById('panditsList');
        container.innerHTML = '';

        pandits.forEach(p => {
            container.innerHTML += `
                <div class="col-lg-4 col-md-6">
                    <div class="pandit-card">
                        <img src="${p.photo}" class="pandit-image" alt="${p.name}">
                        <div class="card-content">
                            <h3 class="pandit-name">${p.name}</h3>
                            <div class="pandit-meta">
                                <div class="meta-item">
                                    <span>${p.city}</span>
                                </div>
                                <div class="meta-item">
                                    <span>${p.experience} Years</span>
                                </div>
                            </div>
                            <p class="specialization">${p.languages ? p.languages.join(', ') : 'General'}</p>
                            <div class="pricing-info">
                                <div class="price-item">
                                    <span class="price-label">Call</span>
                                    <span class="price-value">₹${p.call_price_per_min}/min</span>
                                </div>
                                <div class="price-item">
                                    <span class="price-label">Chat</span>
                                    <span class="price-value">₹${p.chat_price_per_min}/min</span>
                                </div>
                            </div>
                            <div class="action-buttons">
                                <button class="btn-action btn-chat" onclick="startChat('${p.name}', ${p.chat_price_per_min}, '${p._id}', '${p.phone}')">
                                    Chat ₹${p.chat_price_per_min}/min
                                </button>
                                <button class="btn-action btn-call" onclick="startCall('${p.name}', ${p.call_price_per_min}, '${p._id}', '${p.phone}')">
                                    Call ₹${p.call_price_per_min}/min
                                </button>
                            </div>
                            <a href="book-pandit.html?pandit=${encodeURIComponent(p.name)}&id=${p._id}" class="btn-book">
                                Book Pandit
                            </a>
                        </div>
                    </div>
                </div>
            `;
        });
    } catch (error) {
        console.error('Error loading pandits:', error);
    }
}

window.onload = loadPandits;

// Additional functions for chat/call
function startChat(name, pricePerMin, panditId, phone) {
    let minutes = prompt(`How many minutes chat with Pandit ${name}? (₹${pricePerMin}/min)`, "5");
    if (!minutes || minutes < 1) return alert("Minimum 1 minute");
    
    const amount = pricePerMin * minutes * 100;
    const bookingId = Date.now();
    
    const options = {
        "key": "rzp_live_RwBuGYKySb2uQY",
        "amount": amount,
        "currency": "INR",
        "name": "BookMyPandit",
        "description": `Chat with ${name} - ${minutes} min`,
        "handler": function (response){
            // Create booking object
            const booking = {
                booking_id: bookingId,
                pandit_id: panditId,
                user_name: "Guest User", // In real app, get from session
                type: "chat",
                minutes: parseInt(minutes),
                amount: amount / 100,
                status: "paid",
                created_at: new Date().toISOString(),
                payment_id: response.razorpay_payment_id
            };
            
            // Save booking (in real app, this would be API call)
            saveBooking(booking);
            
            // Notify pandit via WhatsApp
            const whatsappMessage = `New Chat Booking Received!\n\nBooking ID: ${bookingId}\nCustomer: Guest User\nDuration: ${minutes} minutes\nAmount: ₹${amount/100}\n\nClick here to connect: ${window.location.origin}/pandit/connect.html?booking_id=${bookingId}`;
            const whatsappUrl = `https://wa.me/${phone}?text=${encodeURIComponent(whatsappMessage)}`;
            
            alert('Payment Success! Pandit has been notified. Please wait for connection.');
            
            // Open WhatsApp for pandit notification (in real app, this would be automatic)
            // window.open(whatsappUrl, '_blank');
        },
        "theme": {"color": "#25D366"}
    };
    const rzp = new Razorpay(options);
    rzp.open();
}

function startCall(name, pricePerMin, panditId, phone) {
    let minutes = prompt(`How many minutes call with Pandit ${name}? (₹${pricePerMin}/min)`, "5");
    if (!minutes || minutes < 1) return alert("Minimum 1 minute");
    
    const amount = pricePerMin * minutes * 100;
    const bookingId = Date.now();
    
    const options = {
        "key": "rzp_live_RwBuGYKySb2uQY",
        "amount": amount,
        "currency": "INR",
        "name": "BookMyPandit",
        "description": `Call with ${name} - ${minutes} min`,
        "handler": function (response){
            // Create booking object
            const booking = {
                booking_id: bookingId,
                pandit_id: panditId,
                user_name: "Guest User", // In real app, get from session
                type: "call",
                minutes: parseInt(minutes),
                amount: amount / 100,
                status: "paid",
                created_at: new Date().toISOString(),
                payment_id: response.razorpay_payment_id
            };
            
            // Save booking (in real app, this would be API call)
            saveBooking(booking);
            
            // Notify pandit via WhatsApp
            const whatsappMessage = `New Call Booking Received!\n\nBooking ID: ${bookingId}\nCustomer: Guest User\nDuration: ${minutes} minutes\nAmount: ₹${amount/100}\n\nClick here to connect: ${window.location.origin}/pandit/connect.html?booking_id=${bookingId}`;
            const whatsappUrl = `https://wa.me/${phone}?text=${encodeURIComponent(whatsappMessage)}`;
            
            alert('Payment Success! Pandit has been notified. Please wait for call connection.');
            
            // Open WhatsApp for pandit notification (in real app, this would be automatic)
            // window.open(whatsappUrl, '_blank');
        },
        "theme": {"color": "#007bff"}
    };
    const rzp = new Razorpay(options);
    rzp.open();
}

// Function to save booking (MVP - in real app this would be API call)
function saveBooking(booking) {
    try {
        // In a real application, this would be an API call to the backend
        // For now, we'll just log it
        console.log('New booking created:', booking);
        
        // You could also store in localStorage for demo purposes
        const existingBookings = JSON.parse(localStorage.getItem('pendingBookings') || '[]');
        existingBookings.push(booking);
        localStorage.setItem('pendingBookings', JSON.stringify(existingBookings));
        
    } catch (error) {
        console.error('Error saving booking:', error);
    }
}