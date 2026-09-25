import re
from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, or_
import os
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
# Import your forms from the forms.py
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm, CATEGORIES

POSTS_PER_PAGE = 6

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("FLASK_KEY", "dev-only-change-this-secret-key")
ckeditor = CKEditor(app)
Bootstrap5(app)

gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False, base_url=None)
#  Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", 'sqlite:///posts.db')
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLES
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="Technology")
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    views: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    comments = relationship("Comment", back_populates="parent_post", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")

    @property
    def reading_time(self):
        """Rough reading-time estimate (minutes) based on word count of the post body."""
        plain_text = re.sub(r"<[^>]+>", " ", self.body or "")
        word_count = len(plain_text.split())
        return max(1, round(word_count / 200))

    @property
    def like_count(self):
        return len(self.likes)

    def is_liked_by(self, user):
        if not user or not getattr(user, "is_authenticated", False):
            return False
        return any(like.user_id == user.id for like in self.likes)


class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")
    post_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("blog_posts.id"))
    parent_post = relationship("BlogPost", back_populates="comments")


class Like(db.Model):
    __tablename__ = "likes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    post_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("blog_posts.id"))
    user = relationship("User", back_populates="likes")
    post = relationship("BlogPost", back_populates="likes")


with app.app_context():
    db.create_all()


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function


@app.context_processor
def inject_globals():
    return dict(all_categories=CATEGORIES, current_year=date.today().year)


# Use Werkzeug to hash the user's password when creating a new user.
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = db.session.execute(db.select(User).where(User.email == form.email.data)).scalar()
        if user:
            flash("You've already signed up with this email, login instead")
            return redirect(url_for('login'))
        hash_password = generate_password_hash(password=form.password.data, method='pbkdf2:sha256', salt_length=8)
        new_user = User(email=form.email.data,
                         password=hash_password,
                         name=form.name.data)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('get_all_posts'))
    return render_template("register.html", form=form, current_user=current_user)


#  Retrieve a user from the database based on their email.
@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('get_all_posts'))
            else:
                flash("Password incorrect, please try again!")
                return redirect(url_for('login'))
        else:
            flash("The email doesn't exist, please try again!")
            return redirect(url_for('login'))
    return render_template("login.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    page = request.args.get('page', 1, type=int)
    stmt = db.select(BlogPost).order_by(BlogPost.id.desc())
    pagination = db.paginate(stmt, page=page, per_page=POSTS_PER_PAGE, error_out=False)
    return render_template(
        "index.html",
        all_posts=pagination.items,
        pagination=pagination,
        pagination_endpoint="get_all_posts",
        pagination_kwargs={},
    )


@app.route('/category/<string:category_name>')
def category_posts(category_name):
    page = request.args.get('page', 1, type=int)
    stmt = db.select(BlogPost).where(BlogPost.category == category_name).order_by(BlogPost.id.desc())
    pagination = db.paginate(stmt, page=page, per_page=POSTS_PER_PAGE, error_out=False)
    return render_template(
        "index.html",
        all_posts=pagination.items,
        pagination=pagination,
        pagination_endpoint="category_posts",
        pagination_kwargs={"category_name": category_name},
        active_category=category_name,
    )


@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    if query:
        pattern = f"%{query}%"
        stmt = db.select(BlogPost).where(
            or_(BlogPost.title.ilike(pattern), BlogPost.subtitle.ilike(pattern), BlogPost.body.ilike(pattern))
        ).order_by(BlogPost.id.desc())
    else:
        stmt = db.select(BlogPost).order_by(BlogPost.id.desc())
    pagination = db.paginate(stmt, page=page, per_page=POSTS_PER_PAGE, error_out=False)
    return render_template(
        "index.html",
        all_posts=pagination.items,
        pagination=pagination,
        pagination_endpoint="search",
        pagination_kwargs={"q": query},
        search_query=query,
    )


@app.route('/author/<int:user_id>')
def author_profile(user_id):
    author = db.get_or_404(User, user_id)
    posts = db.session.execute(
        db.select(BlogPost).where(BlogPost.author_id == user_id).order_by(BlogPost.id.desc())
    ).scalars().all()
    return render_template("author.html", author=author, posts=posts)


#  Allow logged-in users to comment on posts
@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    comment_form = CommentForm()
    requested_post = db.get_or_404(BlogPost, post_id)

    if request.method == "GET":
        requested_post.views += 1
        db.session.commit()

    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('Please log in to leave a comment')
            return redirect(url_for('login'))
        new_comment = Comment(
            text=comment_form.comment.data,
            comment_author=current_user,
            author_id=current_user.id,
            post_id=requested_post.id,
            parent_post=requested_post
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('show_post', post_id=post_id))

    return render_template("post.html", post=requested_post, comment_form=comment_form)


@app.route('/like/<int:post_id>', methods=["POST"])
@login_required
def like_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    existing = db.session.execute(
        db.select(Like).where(Like.user_id == current_user.id, Like.post_id == post.id)
    ).scalar()
    if existing:
        db.session.delete(existing)
    else:
        db.session.add(Like(user_id=current_user.id, post_id=post.id))
    db.session.commit()
    return redirect(url_for('show_post', post_id=post_id))


@app.route('/delete-comment/<int:comment_id>')
@login_required
def delete_comment(comment_id):
    comment = db.get_or_404(Comment, comment_id)
    if current_user.id != comment.author_id and current_user.id != 1:
        return abort(403)
    post_id = comment.post_id
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('show_post', post_id=post_id))


#  Use a decorator so only an admin user can create a new post
@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            category=form.category.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form, current_user=current_user)


#  Use a decorator so only an admin user can edit a post
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    author = db.get_or_404(User, post.author_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        category=post.category,
        img_url=post.img_url,
        author=author.name,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.category = edit_form.category.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True, current_user=current_user)


#  Use a decorator so only an admin user can delete a post
@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=False, port=5001)
