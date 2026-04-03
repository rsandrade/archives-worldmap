from flask_mail import Mail

# Instantiated here so every module can import without triggering circular imports.
# Bound to the app in create_app() via mail.init_app(app).
mail = Mail()
