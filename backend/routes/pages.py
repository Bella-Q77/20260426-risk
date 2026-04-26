from flask import Blueprint, render_template, redirect, url_for, current_app

pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/')
def index():
    return render_template('index.html', title='风控策略/建模/算法工程师工作系统')

@pages_bp.route('/dashboard')
def dashboard():
    return redirect(url_for('pages.index'))

@pages_bp.route('/project/<project_id>')
def project_detail(project_id):
    return render_template('project_detail.html', title='项目详情', project_id=project_id)

@pages_bp.route('/create-project')
def create_project():
    return render_template('create_project.html', title='创建新项目')

@pages_bp.route('/projects')
def projects_list():
    return render_template('projects_list.html', title='项目列表')

@pages_bp.route('/docs')
def docs():
    return render_template('documentation.html', title='使用文档')
