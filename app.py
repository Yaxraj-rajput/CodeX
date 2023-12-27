
try:
    from flask import Flask, flash, jsonify, render_template, request, redirect, session, url_for
    from flask_sqlalchemy import SQLAlchemy
    from datetime import datetime
    from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
    from werkzeug.security import generate_password_hash
    from werkzeug.security import check_password_hash
    import os
    from werkzeug.utils import secure_filename
    from flask_dance.contrib.github import make_github_blueprint, github
except Exception as e:
    print("Some modules are missing {}".format(e))


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///codex.db'

github_blueprint = make_github_blueprint(client_id='071296f9dfa9072bd5c0', client_secret='57e38b5e49b6026641b07d34142a1bc0f064495d')
app.register_blueprint(github_blueprint, url_prefix='/github_login')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
secret_key = os.urandom(24)
app.secret_key = secret_key

@app.route('/github')
def github_login():
    if not github.authorized:
        return redirect(url_for('github.login'))
    else:
        account_info = github.get('/user')
        if account_info.ok:
            account_info_json = account_info.json()
            username = account_info_json['login']

            user = User.query.filter_by(username=username).first()
            if user is None:
                # User doesn't exist, create a new one
                user = User(username=username, email=account_info_json['email'], password=generate_password_hash('12345678'))
                db.session.add(user)
                db.session.commit()

            # Log in the user
            login_user(user)

            return redirect(url_for('home'))
    return '<h1>Request failed!</h1>'



login_manager = LoginManager()
login_manager.init_app(app)


with app.app_context():
    db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    dob = db.Column(db.Integer)
    tech_stack = db.Column(db.String(80))
    bio = db.Column(db.Text(500))
    occupation = db.Column(db.String(80))
    location = db.Column(db.String(80))
    profile_pic = db.Column(db.String(80), default='default.png')
    github = db.Column(db.String(80))
    linkedin = db.Column(db.String(80))
    twitter = db.Column(db.String(80))
    facebook = db.Column(db.String(80))
    instagram = db.Column(db.String(80))
    website = db.Column(db.String(80))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(80), default='active')    




class Articles(db.Model):
    article_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    code_snippet = db.Column(db.Text, nullable=True)
    post_by = db.Column(db.String(200), nullable=False)
    date_time = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)
    genre = db.Column(db.String(200), nullable=True)
    tags = db.Column(db.String(200), nullable=True)
    views = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    status = db.Column(db.String(200), nullable=False, default='draft')

    def __repr__(self):
        return f"{self.article_id} - {self.title}"


@app.route("/")
def home():

    return render_template("index.html", user=current_user)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))





@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        return redirect(('/login'))
    else:
        return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            session['username'] = user.username
            session['email'] = user.email
            return redirect('/')
        else:
            return 'Invalid username or password'
    else:
        return render_template('login.html')
    

    

@app.route('/logout')
def logout():
    logout_user()
    return redirect(('/login'))


@app.route("/new_article", methods=['GET', 'POST'])
def new_article():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        code_snippet = request.form['code_snippet']
        post_by = request.form['post_by']
        genre = request.form['genre']
        tags = request.form['tags']
        views = int(request.form['views'])  # Convert views to integer
        status = request.form['status']

        # Create new article
        article = Articles(
            title=title,
            description=description,
            code_snippet=code_snippet,
            post_by=post_by,
            genre=genre,
            tags=tags,
            views=views,
            status=status
        )

        # Add new article to the session and commit
        db.session.add(article)
        db.session.commit()

    AllArticles = Articles.query.all()
    return render_template("new_article.html", allArticles=AllArticles)


@app.route("/articles", methods=['GET', 'POST'])
def articles():
    AllArticles = Articles.query.all()
    return render_template("articles.html", allArticles=AllArticles)



@app.route('/article/<int:article_id>', methods=['GET'])
def article(article_id):
    article = Articles.query.get(article_id)
    if article:
        if 'views' in article.__dict__:
            article.views += 1
        else:
            article.views = 1
        db.session.commit()
        return render_template('view_article.html', article=article)
    else:
        return "Article not found", 404
    

@app.route('/profile', methods=['POST', 'GET'])
@login_required
def show_profile():
    # Get user id from form or session
    user_id = current_user.id

    user = User.query.get(user_id)

    if user:
        return render_template('profile.html', user=user)
    else:
        return "User not found", 404

@app.route('/update_profile', methods=['POST', "GET"])
@login_required
def update_profile():
    user_id = current_user.id
    user = User.query.get(user_id)

    if user:
        user.username = request.form['username']
        user.dob = request.form['dob']
        user.tech_stack = request.form['tech_stack']
        user.bio = request.form['bio']
        user.occupation = request.form['occupation']
        user.location = request.form['location']

        # Corrected line
        profile_pic = request.files['profile_pic']
        if profile_pic:
            filename = secure_filename(profile_pic.filename)
            filename = f"{user_id}_{filename}"
            profile_pic.save(os.path.join('./static/profile_pic', filename))
            user.profile_pic = filename

        user.github = request.form['github']
        user.linkedin = request.form['linkedin']
        user.twitter = request.form['twitter']
        user.facebook = request.form['facebook']
        user.instagram = request.form['instagram']
        user.website = request.form['website']
        user.status = request.form['status']

        db.session.commit()

        return redirect(url_for('show_profile', user_id=user_id))
    else:
        return "User not found", 404
    # @app.route("/delete/<int:sno>")
# def delete(sno):
#     todo = Todo.query.filter_by(sno=sno).first()
#     db.session.delete(todo)
#     db.session.commit()
#     return redirect("/")


# @app.route("/edit/<int:sno>", methods=['GET', 'POST'])
# def edit(sno):
#     if request.method == 'POST':
#         title = request.form['title']
#         description = request.form['description']
#         todo = Todo.query.filter_by(sno=sno).first()
#         todo.title = title
#         todo.description = description
#         db.session.add(todo)
#         db.session.commit()
       
    # todo = Todo.query.filter_by(sno=sno).first()

    # return render_template("update.html", todo=todo)

if __name__ == '__main__':
    app.run(debug=True, port=8000,  host='0.0.0.0')