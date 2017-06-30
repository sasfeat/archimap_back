from flask import Flask, jsonify
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

import settings

from flask_cors import CORS, cross_origin



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

build_to_styles = db.Table('build_to_styles',
                        db.Column('build_id', db.Integer, db.ForeignKey('build_meta.id')),
                        db.Column('style_id', db.Integer, db.ForeignKey('styles.id'))
                        )

build_to_archi = db.Table('build_to_archi',
                        db.Column('build_id', db.Integer, db.ForeignKey('build_meta.id')),
                        db.Column('archi_id', db.Integer, db.ForeignKey('archi.id'))
                        )


class Styles(db.Model):
    __tablename__ = 'styles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    def __init__(self, name):
        self.name = name


class BuildMeta(db.Model):
    __tablename__ = 'build_meta'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    name_add = db.Column(db.Text)
    notes = db.Column(db.Text)
    link = db.Column(db.Text)
    lat = db.Column(db.REAL)
    lon = db.Column(db.REAL)
    photo = db.Column(db.Text)
    year_from = db.Column(db.Integer)
    year_to = db.Column(db.Integer)
    year_from_acc = db.Column(db.Integer, default=0)
    year_to_acc = db.Column(db.Integer, default=0)
    build_styles = db.relationship('Styles',
                                   secondary = build_to_styles,
                                   # backref=db.backref('builds'),
                                   lazy='dynamic')
    build_archi = db.relationship('Archi',
                                     secondary=build_to_archi,
                                     # backref=db.backref('builds'),
                                     lazy='dynamic')

    build_history = db.relationship('BuildHistory', lazy='dynamic')

    def __init__(self, name, name_add, notes, link, lat, lon,
                 photo, year_from, year_to, year_from_acc, year_to_acc):
        self.name = name
        self.name_add = name_add
        self.notes = notes
        self.link = link
        self.lat = lat
        self.lon = lon
        self.photo = photo
        self.year_from = year_from
        self.year_to = year_to
        self.year_from_acc = year_from_acc
        self.year_to_acc = year_to_acc


class Archi(db.Model):
    __tablename__ = 'archi'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Text)
    second_name = db.Column(db.Text)
    link = db.Column(db.Text)

    def __init__(self, first_name, second_name, link):
        self.first_name = first_name
        self.second_name = second_name
        self.link = link


class BuildHistory(db.Model):
    __tablename__ = 'build_history'
    id = db.Column(db.Integer, primary_key=True)
    build_id = db.Column(db.Integer, db.ForeignKey('build_meta.id'))
    notes = db.Column(db.Text)
    event = db.Column(db.Text)
    year = db.Column(db.Integer)
    year_acc = db.Column(db.Integer, default=0)

    def __init__(self, notes, event, year, year_acc):
        self.notes = notes
        self.event = event
        self.year = year
        self.year_acc = year_acc


class StylesSerializer(ma.ModelSchema):
    class Meta:
        model = Styles


class ArchiSerializer(ma.ModelSchema):
    class Meta:
        model = Archi


class BuildHistorySerializer(ma.ModelSchema):
    class Meta:
        model = BuildHistory


class BuildMetaSerializer(ma.ModelSchema):
    build_styles = ma.Nested(StylesSerializer, many=True)
    build_archi = ma.Nested(ArchiSerializer, many=True)
    build_history = ma.Nested(BuildHistorySerializer, many=True)
    class Meta:
        model = BuildMeta


class StylesView(Resource):
    @cross_origin()
    def get(self):
        rows = db.session.query(Styles).all()
        serializer = StylesSerializer(many=True)
        return jsonify(serializer.dump(rows).data)


class BuildMetaView(Resource):
    @cross_origin()
    def get(self):
        rows = db.session.query(BuildMeta).all()
        serializer = BuildMetaSerializer(many=True)
        return jsonify(serializer.dump(rows).data)


class ArchiView(Resource):
    @cross_origin()
    def get(self):
        rows = db.session.query(Archi).all()
        serializer = ArchiSerializer(many=True)
        return jsonify(serializer.dump(rows).data)


api.add_resource(StylesView, '/api/styles')
api.add_resource(BuildMetaView, '/api/build_meta')
api.add_resource(ArchiView, '/api/archi')

if __name__ == '__main__':
    app.run(host=settings.webserver_host, port=settings.webserver_port)