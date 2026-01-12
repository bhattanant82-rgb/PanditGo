const nodemailer = require("nodemailer");

const transporter = nodemailer.createTransporter({
  service: "gmail",
  auth: {
    user: "bhattanan82@gmail.com",
    pass: "zbfq nnpj uazg pdjt"
  }
});

// Test connection
transporter.verify((error, success) => {
  if (error) {
    console.log("❌ Gmail connection failed:", error);
  } else {
    console.log("✅ Gmail connected successfully");
  }
});

function sendAdminMail(subject, message) {
  const mailOptions = {
    from: "PanditGo System <bhattanan82@gmail.com>",
    to: "bhattanan82@gmail.com",
    subject: subject,
    html: message
  };

  transporter.sendMail(mailOptions, (error, info) => {
    if (error) {
      console.log("❌ Email failed:", error);
    } else {
      console.log("✅ Email sent:", info.messageId);
    }
  });
}

module.exports = sendAdminMail;