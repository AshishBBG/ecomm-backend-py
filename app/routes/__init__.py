# Dynamic blueprint registration for existing route modules
def register_blueprints(app):
    modules = ['auth_routes','product_routes','category_routes','cart_routes','order_routes','admin_routes', 'payment_routes', 'user_routes']
    for mod in modules:
        try:
            m = __import__(f'app.routes.{mod}', fromlist=['bp','blueprint'])
            # common blueprint names
            for candidate in ('bp','blueprint', f'{mod}_bp', f'{mod.replace("_routes","")}_bp'):
                if hasattr(m, candidate):
                    bp = getattr(m, candidate)
                    prefix = '/api/v1/' + mod.replace('_routes','').replace('routes','').replace('auth','auth')
                    app.register_blueprint(bp, url_prefix=prefix)
                    break
        except Exception:
            continue
