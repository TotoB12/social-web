from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
import random
import requests
import base64
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def save_users(users):
    with open('users.json', 'w') as file:
        json.dump(users, file)

def load_users():
  if not os.path.exists('users.json'):
      with open('users.json', 'w') as file:
          json.dump({}, file)  # Creates an empty JSON object in the file
  with open('users.json', 'r') as file:
      try:
          return json.load(file)
      except json.JSONDecodeError:
          return {}

@app.route('/')
def home():
    posts = load_posts()
    return render_template('home.html', username=session.get('username'), posts=posts)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        users = load_users()
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return render_template('signup.html', error="Passwords do not match.")

        if username in users:
            return render_template('signup.html', error="Username already exists.")

        users[username] = password
        save_users(users)
        session['username'] = username
        return redirect(url_for('home'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_users()
        username = request.form['username']
        password = request.form['password']

        if username not in users or users[username] != password:
            return render_template('login.html', error="Invalid username or password.")

        session['username'] = username
        return redirect(url_for('home'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))


def save_posts(posts):
  with open('posts.json', 'w') as file:
      json.dump(posts, file)


def load_posts():
  if os.path.exists('posts.json'):
      with open('posts.json', 'r') as file:
          try:
              return json.load(file)
          except json.JSONDecodeError:
              return []
  return []


@app.route('/u/<username>')
def user_profile(username):
    posts = load_posts()
    user_posts = [post for post in posts if post['username'] == username]
    return render_template('user_profile.html', username=username, posts=user_posts)


@app.route('/post', methods=['GET', 'POST'])
def post():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']
        image_url = request.form.get('imgur_url')  # Get the image URL from the hidden form field

        if not title or not text:
            return render_template('post.html', error="Title and text are required.")

        id = random.randint(0, 99999999999999999999)
        posts = load_posts()
        while id in posts:
          id = random.randint(0, 99999999999999999999)

        posts[id] = {'username': session['username'], 'title': title, 'text': text, 'image': image_url, 'upvotes': [], 'downvotes': []}
        save_posts(posts)
        return redirect(url_for('home'))

    return render_template('post.html')

@app.route('/delete_post/<int:post_id>')
def delete_post(post_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    posts = load_posts()
    if posts[post_id]['username'] == session['username']:
      del posts[post_id]
      save_posts(posts)
    return redirect(request.referrer or url_for('home'))

@app.route('/upvote/<int:post_id>', methods=['POST'])
async def upvote(post_id):
  posts = load_posts()
  if posts[post_id] and not session['username'] in posts[post_id]['upvotes']:
      posts[post_id]["upvotes"].append(session['username'])
      save_posts(posts)
      return jsonify(len(posts[post_id]['upvotes']))
  return jsonify(0)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
