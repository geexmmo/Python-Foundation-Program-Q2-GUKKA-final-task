from os import link
import time
import datetime
from flask import Flask, abort, request, jsonify, g, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
import jwt
import FinalV1
from werkzeug.security import generate_password_hash, check_password_hash

# initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:mysecretpassword@127.0.0.1:5432/web'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

# extensions
db = SQLAlchemy(app)
auth = HTTPBasicAuth()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(128))

    def hash_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expires_in=600):
        return jwt.encode(
            {'id': self.id, 'exp': time.time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')
    
    @staticmethod
    def verify_auth_token(token):
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'],
                              algorithms=['HS256'])
        except:
            return
        return User.query.get(data['id'])


class Chan(db.Model):
    # __tablename__ = 'cache_channels'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(512), nullable=False)
    description = db.Column(db.String(512), nullable=False)
    language = db.Column(db.String(32), nullable=False)
    link = db.Column(db.String(64), nullable=False)
    source = db.Column(db.String(128), nullable=False)
    
    def __repr__(self):
        return f'<Channel {self.title} {self.items}>'

class Items(db.Model):
    # __tablename__ = 'cache_items'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(512), nullable=False)
    link = db.Column(db.String(512), nullable=False)
    description = db.Column(db.String(), nullable=False)
    pubDate = db.Column(db.String(128), nullable=False)
    channel_id = db.Column(db.Integer, db.ForeignKey('chan.id'),
        nullable=False)
    channel = db.relationship('Chan',
        backref=db.backref('items', lazy=True))

    def __repr__(self):
        return f'<Items {self.title} {self.channel_id}>'
        
    def json(self):
        return {'title': self.title, 'link': self.link, 
                'description': self.description, 'pubDate': self.pubDate}


def arg_parser(json):
        return {'source': json.get('source') if json.get('source') else None,
            'limit': int(json.get('limit')) if json.get('limit') else None,
            'json': json.get('json') if json.get('json') else None,
            'date': json.get('date') if json.get('date') else None}

def cache_make(data, source):
    for i in data:
        chaninfo = Chan(title=data[i]['title'],
                description=data[i]['description'],
                language=data[i]['language'],
                link=data[i]['link'],
                source=source)
        for dataitems in data[i]['items']:
            item = Items(title=dataitems['title'],
                    link=dataitems['link'],
                    description=dataitems['description'],
                    pubDate=dataitems['pubDate'],
                    channel=chaninfo)
            #items comes from relation mapping
            chaninfo.items.append(item)
        db.session.add(chaninfo)
        db.session.commit()

def cache_find_by_date(source, unixtime):
    channel = Chan.query.filter_by(source=source).first_or_404()
    items = Items.query.filter_by(channel_id=channel.id).all()
    filtered_items = []
    for item in items:
        topic_time = int(
                datetime.datetime.strptime(item.pubDate, "%a, %d %b \
                %Y %H:%M:%S %z").timestamp())
        if not (topic_time <= unixtime - 86400*2) and \
                   not (topic_time >= unixtime + 86400*2):
            filtered_items.append(item.json())
    return filtered_items


def cache_return_full(source):
    channel = Chan.query.filter_by(source=source).first_or_404()
    items = Items.query.filter_by(channel_id=channel.id).all()
    returndict = {'id': channel.id,
    'title': channel.title,
    'description': channel.description,
    'language': channel.language,
    'link': channel.link,
    'source': channel.source,
    'items': []}
    for item in channel.items:
        returndict['items'].append(item.json())
    # print(channel)
    return returndict


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True

@app.route('/api/cache', methods=['POST'])
@auth.login_required
def cache_test():
    args = arg_parser(request.json)
    if Chan.query.filter_by(source=args['source']).first() is None:
        print('not cached')
        # if not cached
        text = FinalV1.http_get_feed(args['source'])
        if FinalV1.check_if_rss(text):
            data = FinalV1.parse_rss(text)
            cache_make(data, args['source'])
            if args['date']:
                unixtime = FinalV1.validate_date(args['date'])
                if unixtime:
                    return cache_find_by_date(args['source'], unixtime)
            else: 
                return cache_return_full(args['source'])
        else:
            return 'not rss'
    else:
        # cached already
        if args['date']:
                unixtime = FinalV1.validate_date(args['date'])
                if unixtime:
                    return cache_find_by_date(args['source'], unixtime)
        else:
            return cache_return_full(args['source'])

@app.route('/api/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)    # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        abort(400)    # existing user
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return (jsonify({'username': user.username}), 201,
            {'Location': url_for('get_user', id=user.id, _external=True)})


@app.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})


@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token, 'duration': 600})


@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.username})


@app.route('/api/req', methods=['POST'])
@auth.login_required
def req_test():
    args = arg_parser(request.json)
    text = FinalV1.http_get_feed(args['source'])
    if FinalV1.check_if_rss(text):
        data = FinalV1.parse_rss(text, args['limit'])
        if args['json']:
            return(FinalV1.json_presentation(data))
        # elif args.to_html:
        #     FinalV1.convert_to_html(data, args.to_html)
        elif args.to_pdf:
            FinalV1.convert_to_pdf(data, args.to_pdf)
        else:
            return(''.join(FinalV1.user_presentation(data)))


def main():
    db.create_all()
    app.run(debug=True)

if __name__ == '__main__':
    main()