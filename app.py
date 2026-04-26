import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
import config

app = Flask(
    __name__,
    static_folder=config.STATIC_DIR,
    template_folder=config.TEMPLATES_DIR
)
app.config.from_object(config)
CORS(app)

from backend.routes.api import api_bp
from backend.routes.pages import pages_bp

app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(pages_bp)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(config.STATIC_DIR, filename)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, message='页面不存在'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error_code=500, message='服务器内部错误'), 500

if __name__ == '__main__':
    print("=" * 60)
    print("  风控策略/建模/算法工程师工作系统")
    print("  Risk Control Workbench")
    print("=" * 60)
    print(f"  服务地址: http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
