<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PanditGo – Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    <style>
        body { 
            background: linear-gradient(135deg, #fffaf0, #ffe4d9); 
            min-height: 100vh; 
            display: flex; 
            align-items: center; 
        }
        .login-card { 
            max-width: 420px; 
            margin: auto; 
            border-radius: 20px; 
            overflow: hidden; 
            box-shadow: 0 15px 40px rgba(255,153,51,0.2); 
        }
        .card-header { 
            background: linear-gradient(90deg, #FF9933, #FF4500); 
            color: white; 
            text-align: center; 
            padding: 50px 20px; 
        }
        .card-header h2 { 
            font-family: 'Playfair Display', serif; 
            font-size: 3rem; 
            margin: 0; 
        }
        .btn-login { 
            background: #FF9933; 
            border: none; 
            font-weight: bold; 
            padding: 12px; 
            width: 100%; 
        }
        .btn-login:hover { background: #e67e22; }
        .error-msg { color: #dc3545; text-align: center; margin-top: 1rem; }
    </style>
</head>
<body>

<div class="container">
    <div class="login-card card">
        <div class="card-header">
            <h2>Namaste 🙏</h2>
        </div>
        <div class="card-body p-4">
            <form method="POST" action="login_process.php">
                <div class="mb-3">
                    <label for="email" class="form-label">Email Address</label>
                    <input type="email" class="form-control" id="email" name="email" required>
                </div>
                <div class="mb-3">
                    <label for="password" class="form-label">Password</label>
                    <input type="password" class="form-control" id="password" name="password" required>
                </div>
                <button type="submit" class="btn btn-login">Login</button>
            </form>
            <div class="text-center mt-3">
                <a href="signup.html" class="text-decoration-none">Don't have an account? Sign Up</a>
            </div>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>