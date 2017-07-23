from flask import Flask, jsonify, request
from flask_restful import Resource, Api, abort, reqparse
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import column_property
import settings

from flask_cors import CORS, cross_origin



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# parser = reqparse.RequestParser()
# parser.add_argument('')

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
        # self.id = id
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

    def __init__(self,
                 # id,
                 name, name_add, notes, link, lat, lon,
                 photo, year_from, year_to, year_from_acc, year_to_acc,
                 ):
        # self.id = id
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

    def __init__(self,
                 # id,
                 first_name, second_name, link):
        # self.id = id
        self.first_name = first_name
        self.second_name = second_name
        self.link = link


class BuildHistory(db.Model):
    __tablename__ = 'build_history'
    id = db.Column(db.Integer, primary_key=True)
    build_id = db.Column(db.Integer, db.ForeignKey('build_meta.id'))
    event = db.Column(db.Text)
    year = db.Column(db.Integer)
    year_acc = db.Column(db.Integer, default=0)

    def __init__(self, event, year, year_acc, build_id):

        self.event = event
        self.year = year
        self.year_acc = year_acc
        self.build_id = build_id


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
    def get(self):
        rows = db.session.query(Styles).all()
        serializer = StylesSerializer(many=True)
        return jsonify(serializer.dump(rows).data)


class BuildMetaView(Resource):
    def get(self):
        rows = db.session.query(BuildMeta).all()
        serializer = BuildMetaSerializer(many=True)
        return jsonify(serializer.dump(rows).data)

    def post(self):
        data = request.get_json(force=True)

        photos = ','.join(data['photos'])
        build_meta = BuildMeta(name=data['name'],
                               name_add=data['nameAdd'],
                               link=data['link'],
                               notes=data['notes'],
                               lat=data['lat'],
                               lon=data['lon'],
                               photo=photos,
                               year_from=data['history']['yearFrom'],
                               year_to=data['history']['yearTo'],
                               year_from_acc=data['history']['yearFromAcc'],
                               year_to_acc=data['history']['yearToAcc'])
        # db.session.add(build_meta)
        # db.session.flush()
        # db.session.refresh(build_meta)

        if data['newArchis']:
            # add new archi
            for archi_data in data['newArchis']:
                archi = Archi(first_name=archi_data['firstName'],
                              second_name=archi_data['secondName'],
                              link=archi_data['link'])

                build_meta.build_archi.append(archi)

                # db.session.add(archi)
                # db.session.flush()

                # db.session.refresh(archi)
                # _build_to_archi = build_to_archi.insert(build_id=build_meta.id,
                #                                         archi_id=archi.id)
                # db.session.add(_build_to_archi)
                # db.session.flush()

        if data['newStyles']:
            # add new style
            for style_name in data['newStyles']:
                style = Styles(name=style_name)
                db.session.add(style)
                build_meta.build_styles.append(style)
        db.session.add(build_meta)
        db.session.flush()
                # db.session.add(style)
                # db.session.flush()
                # db.session.refresh(style)
                # _build_to_style = build_to_styles(build_id=build_meta.id,
                #                                   style_id=style.id)
                # db.session.add(_build_to_style)
                # db.session.flush()

        if data['styles']:
            for style_id in data['styles']:
                style = db.session.query(Styles).get(style_id)
                build_meta.build_styles.append(style)
            db.session.flush()


                # _build_to_style = build_to_styles(build_id=build_meta.id,
                #                                   style_id=style.id)
                # db.session.add(_build_to_style)
                # db.session.flush()

        if data['archis']:
            for archi_id in data['archis']:
                archi = db.session.query(Archi).get(archi_id)
                build_meta.build_archi.append(archi)
            db.session.flush()

        if data['history']['events']:
            for event in data['history']['events']:
                build_history = BuildHistory(event=event['name'],
                                             year=event['year'],
                                             year_acc=event['yearAcc'],
                                             build_id=build_meta.id)
                db.session.add(build_history)
                build_meta.build_history.append(build_history)
            db.session.flush()

        db.session.commit()

        return build_meta.id, 201


class BuildMetaItemView(Resource):
    def get(self, build_id):
        row = db.session.query(BuildMeta).filter_by(id=build_id).first()
        if row is None:
            abort(404, message="Building with id {} doesn't exist".format(build_id))
        serializer = BuildMetaSerializer()
        return jsonify(serializer.dump(row).data)


class ArchiView(Resource):
    def get(self):
        rows = db.session.query(Archi).all()
        serializer = ArchiSerializer(many=True)
        return jsonify(serializer.dump(rows).data)


api.add_resource(StylesView, '/api/styles')
api.add_resource(BuildMetaView, '/api/build_meta')
api.add_resource(BuildMetaItemView, '/api/build_meta/<build_id>')
api.add_resource(ArchiView, '/api/archi')

if __name__ == '__main__':
    app.run(host=settings.webserver_host, port=settings.webserver_port)