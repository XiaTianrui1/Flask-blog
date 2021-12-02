import hashlib
import logging
import re

from flask import Blueprint, render_template, request, redirect, jsonify, flash, session, g, url_for

# 实例化蓝图对象
from werkzeug.security import generate_password_hash

from app.articles.model import Article, Save, Comment
from app.user.model import User, Message
from ext import db

user_bp = Blueprint('user', __name__)

before_request_list = ['/center', '/add_comment', '/save', '/change', '/check_oldpsw', '/checknewem']


# 钩子函数
@user_bp.before_app_request
def before_request():
    if request.path in before_request_list:
        user_id = request.cookies.get('uid')
        if not user_id:
            return render_template('login.html')
        else:
            user = User.query.get(user_id)
            g.user = user
            if request.path == '/center':
                if user.username == 'administrator':
                    # 接受页码数
                    page = int(request.args.get('page', 1))
                    # 展示所有文章
                    pagination = Article.query.order_by(-Article.time).paginate(page=page, per_page=5)
                    logging.info(f'Administrator visited the admin center.')
                    return render_template('admin.html', pagination=pagination)
                else:
                    page = int(request.args.get('page', 1))
                    pagination = Save.query.filter(Save.user_id == g.user.user_id).paginate(
                        page=page, per_page=5)
                    logging.info(f'User {user.username} visited the user center.')
                    return render_template('user.html', pagination=pagination)


# user_bp蓝图下的视图函数

@user_bp.app_template_filter('decodee')
def content_decode(content):
    content = str(content).decode('utf-8')
    print(content)
    return content


# 用户注册
@user_bp.route('/rl', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = request.form.get('email')
        gender = request.form.get('gender')
        user1 = User.query.filter(User.username == username).first()
        user2 = User.query.filter(User.email == email).first()
        # 数据库验证，验证是否用户名已存在
        if user1:
            flash("This username is already been used!")
            logging.warning('Someone registered with an existing username!')
        # 验证用户名是否以字母开头
        elif ('a' <= username[0] <= 'z') == 0 and ('A' <= username[0] <= 'Z') == 0:
            flash("The username should be started with a letter!")
            logging.warning('Someone registered with a wrong format of username!')
        # 验证用户名长度是否在6到15之间
        elif len(username) < 6 or len(username) > 15:
            flash("The length of the username must be 6-15!")
            logging.warning('Someone registered with a wrong format of username!')
        # 验证密码长度是否大于8
        elif len(password) < 8:
            flash("The length of the password must be larger than 7!")
            logging.warning('Someone registered with a wrong format of password!')
        # 验证确认密码是否和密码一致
        elif password != confirm_password:
            flash("Two password entries are inconsistent!")
            logging.warning('The password entered by someone is different from the confirmed password')
        # 数据库验证，验证是否邮箱已存在
        elif user2:
            flash("This email is already been used!")
            logging.warning('Someone registered with an existing email!')
        else:
            user = User()
            user.username = username
            # 密码加密
            user.password = hashlib.sha256(password.encode('utf-8')).hexdigest()
            user.email = email
            if gender == 'Male':
                user.gender = True
            else:
                user.gender = False
            try:
                db.session.add(user)
                db.session.commit()
                flash("Successful register!")
            except Exception as e:
                logging.error(e)
                # 如果提交数据库失败，则回滚
                db.session.rollback()
            logging.info(f'User "{username}" has registered successfully!')
    return render_template('rl.html')


# 用户登录
@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        hash_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        # 验证用户名是否存在
        user = User.query.filter(User.username == username).first()
        # 用户名存在
        if user:
            if user.password == hash_password:
                flash('Successfully logged in!')
                response = redirect('home')
                # 设置cookie
                response.set_cookie('uid', str(user.user_id), max_age=6000)
                logging.info(f'User "{user.username}" has successfully logged in!')
                return response
            # 密码输入不正确
            else:
                flash("The password is incorrect!")
                logging.info(f'User "{user.username}" typed in the wrong password.')
                return render_template('login.html')
        # 用户名不存在
        else:
            flash("This username doesn't exit!")
            logging.info(f"Someone entered a username which doesn't exist when logging in.")
    return render_template('login.html')


# 用户退出
@user_bp.route('/logout')
def logout():
    user_id = request.cookies.get('uid')
    user = User.query.get(user_id)
    response = redirect('home')
    # 删除cookie
    response.delete_cookie('uid')
    flash("Successfully logged out!")
    logging.info(f"User '{user.username}' logged out.")
    return response


# ajax验证用户名唯一
@user_bp.route('/checkun', methods=['GET', 'POST'])
def check_username():
    username = request.args.get('username')
    user = User.query.filter(User.username == username).all()
    if user:
        return jsonify(code=100, msg='This username has already been registered!')
    else:
        return jsonify(code=200, msg='This username can be used!')


# ajax验证邮箱唯一
@user_bp.route('/checkem', methods=['GET', 'POST'])
def check_email():
    email = request.args.get('email')
    user = User.query.filter(User.email == email).all()
    if user:
        return jsonify(code=100, msg='This email has already been registered!')
    else:
        return jsonify(code=200, msg='This email can be used!')


# 跳转到用户中心页面
@user_bp.route('/center', methods=['GET', 'POST'])
def center():
    return render_template('user.html')


# 修改密码
@user_bp.route('/change', methods=['GET', 'POST'])
def change():
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        new_email = request.form.get('new_email')
        user = User.query.filter(User.email == new_email, User.username != g.user.username).all()
        # 数据库验证 验证旧密码是否输入正确
        if old_password != g.user.password:
            flash("The old password is wrong!")
            logging.info(f'User "{g.user.username}" entered the wrong old password.')
            return render_template('change.html')
        # 验证新密码长度是否大于8
        elif len(new_password) < 8:
            flash("New password length should be greater than 7!")
            logging.info(f'User "{g.user.username}" entered the new password with a wrong format.')
            return render_template('change.html')
        # 验证新邮箱是否已存在
        elif user:
            flash("This email is already been registered!")
            logging.info(f'User "{g.user.username}" entered an existing eamil as the new email.')
            return render_template('change.html')
        else:
            g.user.password = new_password
            g.user.email = new_email
            try:
                db.session.commit()
            except Exception as e:
                logging.error(e)
                # 如果提交数据库失败，则回滚
                db.session.rollback()
            flash("Successful modification!")
            logging.info(f'User "{g.user.username}" has successfully changed his/her personal information!')
            return render_template('change.html')
            # return redirect(url_for('user.center'))
    if request.method == 'GET':
        logging.info(f'User "{g.user.username}" entered the personal information modification page.')
        return render_template('change.html')


# ajax验证原密码输入是否正确
@user_bp.route('/check_oldpsw')
def check_oldpsw():
    correct_psw = g.user.password
    old_password = request.args.get('old_password')
    if correct_psw == old_password:
        return jsonify(code=200, msg='The old password is correct!')
    else:
        return jsonify(code=100, msg='The old password is wrong!')


# ajax验证邮箱唯一
@user_bp.route('/checknewem', methods=['GET', 'POST'])
def check_newemail():
    email = request.args.get('email')
    user = User.query.filter(User.email == email, User.username != g.user.username).all()
    if user:
        return jsonify(code=100, msg='This email has already been registered!')
    else:
        return jsonify(code=200, msg='This email can be used!')


@user_bp.route('/aboutme')
def aboutme():
    user_id = request.cookies.get('uid')
    user = User.query.get(user_id)
    if user:
        logging.info(f'User "{user.username}" browsed the about me page.')
    else:
        logging.info('Anonymous user browsed the about me page.')
    return render_template('about_me.html')


# 添加留言
@user_bp.route('/message', methods=['GET', 'POST'])
def message():
    user_id = request.cookies.get('uid')
    user = User.query.get(user_id)
    if request.method == 'POST':
        content = request.form.get('message')
        # 验证提交内容是否为空
        if len(content) == 0:
            flash("The submitted message can not be empty!")
            if user:
                logging.warning(f'User "{user.username}" published an empty message.')
            else:
                logging.warning(f'Anonymous user published an empty message.')
            # 接受页码数
            page = int(request.args.get('page', 1))
            # 展示所有文章
            pagination = Message.query.order_by(-Message.time).paginate(page=page, per_page=5)
            return render_template('message.html', user=user, pagination=pagination)
        else:
            if user:
                message1 = Message()
                message1.content = content
                message1.user_id = user.user_id
                try:
                    db.session.add(message1)
                    db.session.commit()
                except Exception as e:
                    logging.error(e)
                    # 如果提交数据库失败，则回滚
                    db.session.rollback()
                logging.info(f'User {user.username} successfully released a message!')
                flash("Successfully released your message!")
            else:
                # 匿名用户提交
                message1 = Message()
                message1.content = content
                try:
                    db.session.add(message1)
                    db.session.commit()
                except Exception as e:
                    logging.error(e)
                    # 如果提交数据库失败，则回滚
                    db.session.rollback()
                logging.info(f'Anonymous user successfully released a message!')
            # 接受页码数
            page = int(request.args.get('page', 1))
            # 展示所有文章
            pagination = Message.query.order_by(-Message.time).paginate(page=page, per_page=5)
            return render_template('message.html', pagination=pagination, user=user)
    else:
        if user:
            logging.info(f'User "{user.username}" browsed the message board!')
        else:
            logging.info(f'Anonymous user browsed the message board!')
        # 接受页码数
        page = int(request.args.get('page', 1))
        # 展示所有文章
        pagination = Message.query.order_by(-Message.time).paginate(page=page, per_page=5)
        return render_template('message.html', pagination=pagination, user=user)


# 管理员或用户本人删除留言
@user_bp.route('/delete_message')
def delete_message():
    uname = request.args.get('uname')
    mid = request.args.get('mid')
    message1 = Message.query.filter(Message.message_id == mid).first()
    user = User.query.filter(User.user_id == message1.user_id).first()
    try:
        db.session.delete(message1)
        db.session.commit()
    except Exception as e:
        logging.error(e)
        # 如果提交数据库失败，则回滚
        db.session.rollback()
    if uname == 'administrator':
        logging.info(f'The administrator deleted a message released by user "{user.username}". ')
    else:
        logging.info(f'User "{user.username}" deleted his/her own message. ')
    flash('Successfully delete the message!')
    return redirect(url_for('user.message'))


# 管理员或用户本人删除评论
@user_bp.route('/delete_comment')
def delete_comment():
    aid = request.args.get('aid')
    cid = request.args.get('cid')
    uname = request.args.get('uname')
    comment1 = Comment.query.filter(Comment.comment_id == cid).first()
    user = User.query.filter(User.user_id == comment1.user_id).first()
    try:
        db.session.delete(comment1)
        db.session.commit()
    except Exception as e:
        logging.error(e)
        # 如果提交数据库失败，则回滚
        db.session.rollback()
    if uname == 'administrator':
        logging.info(f'The administrator deleted a comment released by user "{user.username}". ')
    else:
        logging.info(f'User "{user.username}" deleted his/her own comment. ')
    flash('Successfully delete the comment!')
    return redirect(url_for('articles.detail', aid=aid))
