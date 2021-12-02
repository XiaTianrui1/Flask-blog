from flask import Blueprint, render_template, request, redirect, url_for, jsonify, g, flash

# 实例化蓝图对象
from app.articles.model import Article, Comment, Save
from app.user.model import User
from ext import db
import logging

article_bp = Blueprint('articles', __name__)


# article_bp蓝图下的视图函数


# 跳转到home页面展示
@article_bp.route('/home')
def home():
    uid = request.cookies.get('uid', None)
    user = User.query.get(uid)
    # 接受页码数
    page = int(request.args.get('page', 1))
    # 展示所有文章
    pagination = Article.query.order_by(-Article.time).paginate(page=page, per_page=5)
    # 查询每种分类的文章数量
    num1 = Article.query.filter(Article.type == 'CS learning experience').count()
    num2 = Article.query.filter(Article.type == 'Reading notes').count()
    num3 = Article.query.filter(Article.type == 'Hobbies').count()
    num4 = Article.query.filter(Article.type == 'Daily life').count()
    if user:
        # 有用户登录
        logging.info(f'User "{user.username}" browsed the home page.')
        return render_template('home.html', user=user, pagination=pagination, num1=num1, num2=num2, num3=num3,
                               num4=num4)
    else:
        # 没有用户登录
        logging.info('Anonymous User browsed the home page.')
        return render_template('home.html', pagination=pagination, num1=num1, num2=num2, num3=num3,
                               num4=num4)


# 发布博客
@article_bp.route('/publish', methods=['GET', 'POST'])
def publish():
    if request.method == 'POST':
        title = request.form.get('title')
        atype = request.form.get('type')
        content = request.form.get('article')
        try:
            article = Article()
            article.title = title
            article.type = atype
            article.content = content
            db.session.add(article)
            db.session.commit()
        # 提交失败，数据库回滚
        except Exception as e:
            logging.error(e)
            db.session.rollback()
        logging.info(f'Successfully publish a blog whose title is "{article.title}"')
        flash("Successfully published a blog!")
        return redirect(url_for('articles.home'))


# 删除博客
@article_bp.route('/delete')
def delete():
    aid = request.args.get('aid')
    article_delete = Article.query.get(aid)
    if article_delete:
        # 删除收藏夹中的这篇博客
        saves = Save.query.filter(Save.article_id == aid).all()
        for ssave in saves:
            db.session.delete(ssave)
        try:
            db.session.delete(article_delete)
            db.session.commit()
        except Exception as e:
            logging.error(e)
            # 如果删除失败，则回滚
            db.session.rollback()
        logging.info(f'Successfully delete a blog whose title is "{article_delete.title}"')
        flash('Successfully delete the blog!')
    else:
        logging.error(f"Error: Couldn't find the blog named '{article_delete.title}' which the admin wants to delete.")
    return redirect(url_for('user.center'))


# 从收藏夹中移除
@article_bp.route('/delete_save')
def delete_save():
    aid = request.args.get('aid')
    uid = request.args.get('uid')
    user = User.query.filter(User.user_id == uid).first()
    article_delete = Article.query.get(aid)
    if article_delete:
        # 删除当前用户收藏夹中的这篇博客
        saves = Save.query.filter(Save.article_id == aid, Save.user_id == uid).all()
        for ssave in saves:
            db.session.delete(ssave)
        try:
            db.session.commit()
        except Exception as e:
            logging.error(e)
            # 如果删除失败，则回滚
            db.session.rollback()
        logging.info(f' User "{user.username}" has Successfully removed a blog from his/her favorites.')
        flash('Successfully removed the blog from my favorites!')
    else:
        logging.error(f"Error: Couldn't find the blog which user '{user.username}' wants to remove.")
    return redirect(url_for('user.center'))


# 展示文章详情
@article_bp.route('/detail')
def detail():
    # 获得文章id
    a = 1
    article_id = request.args.get('aid')
    article = Article.query.get(article_id)
    # 获得登录用户
    user_id = request.cookies.get('uid')
    if user_id:
        if article.saves:
            for save1 in article.saves:
                print(save1.user_id)
                print(user_id)
                if save1.user_id == int(user_id):
                    flag = 1
                    a = a + 1
                else:
                    flag = 0
            if a != 1:
                flag = 1
        else:
            flag = 0
    else:
        flag = 0
    # 接受页码数
    page = int(request.args.get('page', 1))
    # 展示所有文章
    pagination = Comment.query.filter(Comment.article_id == article_id).order_by(-Comment.comment_time).paginate(
        page=page, per_page=5)
    if user_id:
        user = User.query.get(user_id)
        logging.info(f'User "{user.username}" browsed the detail page of the blog "{article.title}".')
        return render_template('detail.html', article=article, user=user, pagination=pagination, flag=flag)
    else:
        logging.info(f'Anonymous user browsed the detail page of the blog "{article.title}".')
        return render_template('detail.html', article=article, pagination=pagination, flag=flag)


# 文章点赞
@article_bp.route('/like')
def like():
    uid = request.cookies.get('uid', None)
    article_id = request.args.get('article_id')
    flag = request.args.get('flag')
    article = Article.query.get(article_id)
    if flag == '1':
        if uid:
            user = User.query.get(uid)
            article.like -= 1
            logging.info(f'User "{user.username}" canceled the like of the blog "{article.title}".')
        else:
            article.like -= 1
            logging.info(f'Anonymous user canceled the like of the blog "{article.title}".')
    else:
        if uid:
            user = User.query.get(uid)
            article.like += 1
            logging.info(f'User "{user.username}" liked the blog "{article.title}".')
        else:
            article.like += 1
            logging.info(f'Anonymous user liked the blog "{article.title}".')
    try:
        db.session.commit()
    except Exception as e:
        logging.error(e)
        # 如果提交数据库失败，则回滚
        db.session.rollback()
    return jsonify(like=article.like)


# 文章点击量
@article_bp.route('/click')
def click():
    article_id = request.args.get('article_id')
    article = Article.query.get(article_id)
    article.click += 1
    try:
        db.session.commit()
    except Exception as e:
        logging.error(e)
        # 如果提交数据库失败，则回滚
        db.session.rollback()
    return jsonify(uclick=article.click)


# 发表评论
@article_bp.route('/add_comment', methods=['GET', 'POST'])
def add_comment():
    if request.method == 'POST':
        comment = request.form.get('comment')
        user_id = g.user.user_id
        article_id = request.form.get('aid')
        article = Article.query.filter(Article.article_id == article_id).first()
        # 数据库验证，判断提交内容是否为空
        if len(comment) == 0:
            flash("The submitted comment can not be empty!")
            logging.warning(f'User "{g.user.username}" published an empty comment on the blog "{article.title}".')
        else:
            try:
                ncomment = Comment()
                ncomment.comment = comment
                ncomment.user_id = user_id
                ncomment.article_id = article_id
                db.session.add(ncomment)
                db.session.commit()
            except Exception as e:
                logging.error(e)
                # 如果提交数据库失败，则回滚
                db.session.rollback()
            logging.info(f'User "{g.user.username}" commented on the blog "{article.title}".')
            flash('Successfully released your comment!')
        return redirect(url_for('articles.detail') + "?aid=" + article_id)
    return redirect(url_for('articles.home'))


# 关键字搜索
@article_bp.route('/search/<int:number>', methods=['GET', 'POST'])
def search(number):
    uid = request.cookies.get('uid', None)
    # 接受页码数
    page = int(request.args.get('page', 1))
    if request.method == 'POST':
        # 在所有文章中搜索
        if number == 1:
            key = request.form.get('keyboard')
            pagination = Article.query.filter(Article.content.contains(key) | Article.title.contains(key)).order_by(
                -Article.time).paginate(
                page=page, per_page=5)
            if not pagination.items:
                flash("Sorry, there is no search results found matching the keyword.")
                logging.warning(f'User searched for a keyword "{key}" with empty results.')
            else:
                logging.info(f'User searched for a keyword "{key}" with expected results.')

        # 在cs分类下搜索
        if number == 2:
            key = request.form.get('keyboard')
            pagination = Article.query.filter((Article.content.contains(key) | Article.title.contains(key)),
                                              Article.type == 'CS learning experience').order_by(
                -Article.time).paginate(
                page=page, per_page=5)
            if not pagination.items:
                flash("Sorry, there is no search results found matching the keyword.")
                logging.warning(f'User searched for a keyword "{key}" with empty results.')
            else:
                logging.info(f'User searched for a keyword "{key}" with expected results.')
        if number == 3:
            key = request.form.get('keyboard')
            pagination = Article.query.filter((Article.content.contains(key) | Article.title.contains(key)),
                                              Article.type == 'Reading notes').order_by(-Article.time).paginate(
                page=page, per_page=5)
            if not pagination.items:
                flash("Sorry, there is no search results found matching the keyword.")
                logging.warning(f'User searched for a keyword "{key}" with empty results.')
            else:
                logging.info(f'User searched for a keyword "{key}" with expected results.')
        if number == 4:
            key = request.form.get('keyboard')
            pagination = Article.query.filter((Article.content.contains(key) | Article.title.contains(key)),
                                              Article.type == 'Hobbies').order_by(-Article.time).paginate(
                page=page, per_page=5)
            if not pagination.items:
                flash("Sorry, there is no search results found matching the keyword.")
                logging.warning(f'User searched for a keyword "{key}" with empty results.')
            else:
                logging.info(f'User searched for a keyword "{key}" with expected results.')
        if number == 5:
            key = request.form.get('keyboard')
            pagination = Article.query.filter((Article.content.contains(key) | Article.title.contains(key)),
                                              Article.type == 'Daily life').order_by(-Article.time).paginate(
                page=page, per_page=5)
            if not pagination.items:
                flash("Sorry, there is no search results found matching the keyword.")
                logging.warning(f'User searched for a keyword "{key}" with empty results.')
            else:
                logging.info(f'User searched for a keyword "{key}" with expected results.')
        if uid:
            # 有用户登录
            user = User.query.get(uid)
            return render_template('home.html', user=user, pagination=pagination)
        else:
            # 没有用户登录
            return render_template('home.html', pagination=pagination)


# 添加到收藏夹
@article_bp.route('/save')
def save():
    aid = request.args.get('article_id')
    flag = request.args.get('flag')
    article = Article.query.get(aid)
    print(flag)
    if flag == '1':
        save1 = Save.query.filter(Save.user_id == g.user.user_id, Save.article_id == aid).first()
        if save1:
            db.session.delete(save1)
        article.save -= 1
    else:
        # 把新的收藏记录添加到数据库中
        save_article = Save()
        save_article.article_id = aid
        save_article.user_id = g.user.user_id
        db.session.add(save_article)
        article.save += 1
    db.session.commit()
    return jsonify(saves=article.save)


# 分类展示
@article_bp.route('/cs')
def cs():
    uid = request.cookies.get('uid', None)
    # 接受页码数
    page = int(request.args.get('page', 1))
    # 展示所有文章
    pagination = Article.query.filter(Article.type == 'CS learning experience').order_by(-Article.time).paginate(
        page=page, per_page=5)
    # 查询每种分类的文章数
    num1 = Article.query.filter(Article.type == 'CS learning experience').count()
    num2 = Article.query.filter(Article.type == 'Reading notes').count()
    num3 = Article.query.filter(Article.type == 'Hobbies').count()
    num4 = Article.query.filter(Article.type == 'Daily life').count()
    if uid:
        # 有用户登录
        user = User.query.get(uid)
        logging.info(f'User "{user.username}" browsed the blog under the "CS learning experience" category')
        return render_template('classification.html', user=user, pagination=pagination, num=2, num1=num1, num2=num2,
                               num3=num3,
                               num4=num4, name='CS learning experience')
    else:
        # 没有用户登录
        logging.info(f'Anonymous user browsed the blog under the "CS learning experience" category')
        return render_template('classification.html', pagination=pagination, num=2, num1=num1, num2=num2, num3=num3,
                               num4=num4, name='CS learning experience')


@article_bp.route('/rn')
def rn():
    uid = request.cookies.get('uid', None)
    # 接受页码数
    page = int(request.args.get('page', 1))
    # 展示所有文章
    pagination = Article.query.filter(Article.type == 'Reading notes').order_by(-Article.time).paginate(
        page=page, per_page=5)
    # 查询每种分类的文章数
    num1 = Article.query.filter(Article.type == 'CS learning experience').count()
    num2 = Article.query.filter(Article.type == 'Reading notes').count()
    num3 = Article.query.filter(Article.type == 'Hobbies').count()
    num4 = Article.query.filter(Article.type == 'Daily life').count()
    if uid:
        # 有用户登录
        user = User.query.get(uid)
        logging.info(f'User "{user.username}" browsed the blog under the "Reading notes" category')
        return render_template('classification.html', user=user, pagination=pagination, num=3, num1=num1, num2=num2,
                               num3=num3,
                               num4=num4, name='Reading notes')
    else:
        # 没有用户登录
        logging.info(f'Anonymous user browsed the blog under the "Reading notes" category')
        return render_template('classification.html', pagination=pagination, num=3, num1=num1, num2=num2, num3=num3,
                               num4=num4, name='Reading notes')


@article_bp.route('/ho')
def ho():
    uid = request.cookies.get('uid', None)
    # 接受页码数
    page = int(request.args.get('page', 1))
    # 展示所有文章
    pagination = Article.query.filter(Article.type == 'Hobbies').order_by(-Article.time).paginate(
        page=page, per_page=5)
    # 查询每种分类的文章数
    num1 = Article.query.filter(Article.type == 'CS learning experience').count()
    num2 = Article.query.filter(Article.type == 'Reading notes').count()
    num3 = Article.query.filter(Article.type == 'Hobbies').count()
    num4 = Article.query.filter(Article.type == 'Daily life').count()
    if uid:
        # 有用户登录
        user = User.query.get(uid)
        logging.info(f'User "{user.username}" browsed the blog under the "Hobbies" category')
        return render_template('classification.html', user=user, pagination=pagination, num=4, num1=num1, num2=num2,
                               num3=num3,
                               num4=num4, name='Hobbies')
    else:
        # 没有用户登录
        logging.info(f'Anonymous user browsed the blog under the "Hobbies" category')
        return render_template('classification.html', pagination=pagination, num=4, num1=num1, num2=num2,
                               num3=num3,
                               num4=num4, name='Hobbies')


@article_bp.route('/dl')
def dl():
    uid = request.cookies.get('uid', None)
    # 接受页码数
    page = int(request.args.get('page', 1))
    # 展示所有文章
    pagination = Article.query.filter(Article.type == 'Daily life').order_by(-Article.time).paginate(
        page=page, per_page=5)
    # 查询每种分类的文章数
    num1 = Article.query.filter(Article.type == 'CS learning experience').count()
    num2 = Article.query.filter(Article.type == 'Reading notes').count()
    num3 = Article.query.filter(Article.type == 'Hobbies').count()
    num4 = Article.query.filter(Article.type == 'Daily life').count()
    if uid:
        # 有用户登录
        user = User.query.get(uid)
        logging.info(f'User "{user.username}" browsed the blog under the "Daily life" category')
        return render_template('classification.html', user=user, pagination=pagination, num=5, num1=num1, num2=num2,
                               num3=num3,
                               num4=num4, name='Daily life')
    else:
        # 没有用户登录
        logging.info(f'Anonymous user browsed the blog under the "Daily life" category')
        return render_template('classification.html', pagination=pagination, num=5, num1=num1, num2=num2,
                               num3=num3,
                               num4=num4, name='Daily life')
