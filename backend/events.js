const sendAdminMail = require("./mailer");

function notify(event, data) {
  const timestamp = new Date().toISOString();
  let subject = `🔔 PanditGo Alert: ${event}`;
  let message = `
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
      <h2 style="color: #D4AF37; border-bottom: 2px solid #D4AF37; padding-bottom: 10px;">
        ${event}
      </h2>
      <div style="background: #0B0F14; color: #EAEAEA; padding: 20px; border-radius: 8px; margin: 20px 0;">
        <pre style="font-family: monospace; white-space: pre-wrap; word-wrap: break-word;">
${JSON.stringify(data, null, 2)}
        </pre>
      </div>
      <p style="color: #666; font-size: 12px;">
        Timestamp: ${timestamp}
      </p>
      <p style="color: #666; font-size: 12px;">
        PanditGo Admin System
      </p>
    </div>
  `;

  console.log(`📧 Sending notification: ${event}`);
  sendAdminMail(subject, message);
}

module.exports = notify;