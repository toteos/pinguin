# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------
# AppConfig configuration made easy. Look inside private/appconfig.ini
# Auth is for authenticaiton and access control
# -------------------------------------------------------------------------
from gluon.contrib.appconfig import AppConfig
from gluon.tools import Auth

# -------------------------------------------------------------------------
# This scaffolding model makes your app work on Google App Engine too
# File is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

if request.global_settings.web2py_version < "2.15.5":
    raise HTTP(500, "Requires web2py 2.15.5 or newer")

# -------------------------------------------------------------------------
# if SSL/HTTPS is properly configured and you want all HTTP requests to
# be redirected to HTTPS, uncomment the line below:
# -------------------------------------------------------------------------
# request.requires_https()

# -------------------------------------------------------------------------
# once in production, remove reload=True to gain full speed
# -------------------------------------------------------------------------
configuration = AppConfig(reload=True)

if not request.env.web2py_runtime_gae:
    # ---------------------------------------------------------------------
    # if NOT running on Google App Engine use SQLite or other DB
    # ---------------------------------------------------------------------
    db = DAL(configuration.get('db.uri'),
             pool_size=configuration.get('db.pool_size'),
             migrate_enabled=configuration.get('db.migrate'),
             check_reserved=['all'])
else:
    # ---------------------------------------------------------------------
    # connect to Google BigTable (optional 'google:datastore://namespace')
    # ---------------------------------------------------------------------
    db = DAL('google:datastore+ndb')
    # ---------------------------------------------------------------------
    # store sessions and tickets there
    # ---------------------------------------------------------------------
    session.connect(request, response, db=db)
    # ---------------------------------------------------------------------
    # or store session in Memcache, Redis, etc.
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
    # ---------------------------------------------------------------------

# -------------------------------------------------------------------------
# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
# -------------------------------------------------------------------------
response.generic_patterns = [] 
if request.is_local and not configuration.get('app.production'):
    response.generic_patterns.append('*')

# -------------------------------------------------------------------------
# choose a style for forms
# -------------------------------------------------------------------------
response.formstyle = 'bootstrap4_inline'
response.form_label_separator = ''

# -------------------------------------------------------------------------
# (optional) optimize handling of static files
# -------------------------------------------------------------------------
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

# -------------------------------------------------------------------------
# (optional) static assets folder versioning
# -------------------------------------------------------------------------
# response.static_version = '0.0.0'

# -------------------------------------------------------------------------
# Here is sample code if you need for
# - email capabilities
# - authentication (registration, login, logout, ... )
# - authorization (role based authorization)
# - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
# - old style crud actions
# (more options discussed in gluon/tools.py)
# -------------------------------------------------------------------------

# host names must be a list of allowed host names (glob syntax allowed)
auth = Auth(db, host_names=configuration.get('host.names'))
auth.settings.username_case_sensitive = False
auth.settings.email_case_sensitive = False


# -------------------------------------------------------------------------
# create all tables needed by auth, maybe add a list of extra fields
# -------------------------------------------------------------------------
auth.settings.extra_fields['auth_user'] = []

#auth.settings.extra_fields['auth_user']= [
#	Field('phone'),
#]

auth.define_tables(username=True, signature=False)

# https://groups.google.com/forum/#!topic/web2py/-d0vafeh4Co
custom_auth_table = db[auth.settings.table_user_name] # get the custom_auth_table
custom_auth_table.first_name.notnull = False
custom_auth_table.last_name.notnull = False
custom_auth_table.first_name.requires = False
custom_auth_table.last_name.requires = False
auth.settings.table_user = custom_auth_table




# -------------------------------------------------------------------------
# configure email
# -------------------------------------------------------------------------
#mail = auth.settings.mailer
#mail.settings.server = 'logging' if request.is_local else configuration.get('smtp.server')
#mail.settings.sender = configuration.get('smtp.sender')
#mail.settings.login = configuration.get('smtp.login')
#mail.settings.tls = configuration.get('smtp.tls') or False
#mail.settings.ssl = configuration.get('smtp.ssl') or False

mail = auth.settings.mailer
mail.settings.server = 'localhost:25'
#mail.settings.server = 'logging'
mail.settings.sender = 'no-reply@pinguin.fish'
#mail.settings.login = 'username:password'
mail.settings.login = None

# -------------------------------------------------------------------------
# configure auth policy
# -------------------------------------------------------------------------
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True
#auth.settings.auth_manager_role = 'some_admin_role'

# -------------------------------------------------------------------------  
# read more at http://dev.w3.org/html5/markup/meta.name.html               
# -------------------------------------------------------------------------
response.meta.author = configuration.get('app.author')
response.meta.description = configuration.get('app.description')
response.meta.keywords = configuration.get('app.keywords')
response.meta.generator = configuration.get('app.generator')

# -------------------------------------------------------------------------
# your http://google.com/analytics id                                      
# -------------------------------------------------------------------------
response.google_analytics_id = configuration.get('google.analytics_id')

# -------------------------------------------------------------------------
# maybe use the scheduler
# -------------------------------------------------------------------------
if configuration.get('scheduler.enabled'):
    from gluon.scheduler import Scheduler
    scheduler = Scheduler(db, heartbeat=configure.get('heartbeat'))

# -------------------------------------------------------------------------
# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.
#
# More API examples for controllers:
#
# >>> db.mytable.insert(myfield='value')
# >>> rows = db(db.mytable.myfield == 'value').select(db.mytable.ALL)
# >>> for row in rows: print row.id, row.myfield
# -------------------------------------------------------------------------
db.define_table(
	'citizen',
	Field(
		'user_id', db.auth_user,
		represent=lambda cid, row: A(row.user_id.username, _href=URL("default", "citizen", vars={"c_id": cid}), _class="citizen-name", **{"_data-cid": cid})
	),
	Field(
		'rating', 'double', default=0,
		represent=lambda value, row: 0.00 if not value else "{:.6f}".format(value),
	),
)

db.define_table(
	'quantum',
	Field(
		'holder', db.auth_user,
		represent=lambda cid, row: A(row.holder.username, _href=URL("default", "citizen", vars={"c_id": cid}), _class="citizen-name", **{"_data-cid": cid})
	),
	Field(
		'pinger', db.auth_user,
		represent=lambda cid, row: A(row.pinger.username, _href=URL("default", "citizen", vars={"c_id": cid}), _class="citizen-name", **{"_data-cid": cid}) if cid else SPAN("the bank", _class="citizen-name citizen-name-bank"),
	),
	Field(
		'mother', db.auth_user,
		represent=lambda cid, row: A(row.mother.username, _href=URL("default", "citizen", vars={"c_id": cid}), _class="citizen-name", **{"_data-cid": cid}) if cid else None
	),
	Field(
		'name', "string",
		length=50, default="",
		represent=lambda value, row: A(value, _href=URL("default", "quantum", vars={"q_id": row.id}), _class="quantum-name", **{"_data-qid": row.id})
	),
	Field(
		'flavor', 'boolean',
		represent=lambda f, row: SPAN(1 if f else 0, _class="ping-flavor", **{"_data-flavor": 1 if f else 0})
	),
	Field('rating', 'double', default=0, represent=lambda value, row: 0.00 if not value else "{:.2f}".format(value)),
	Field('created', type='datetime', default=request.now, represent=lambda value, row: TAG.time(value, _class="timeago", _datetime="{} +0000".format(value))),
	Field(
		'locked', type='boolean', default=False,
#		represent=lambda value, row: TAG.time(value, _class="timeago", _datetime="{} +0000".format(value)),
	),
	Field('stamp', type='datetime', default=request.now, represent=lambda value, row: TAG.time(value, _class="timeago", _datetime="{} +0000".format(value))),
#	Field('moved', type='datetime', default=request.now),
#	format='%(pinger)s -> %(pingee)s'
)
#db.quantum.pinged = Field.Virtual('pinged', lambda row: TAG.time(row.quantum.stamp, _class="timeago", _datetime="{} +0000".format(row.quantum.stamp)))
db.quantum.id.label = "Quantum"
#db.quantum.id.represent = lambda value, row: A(value, _href=URL("default", "quantum", vars={"q_id": value}))
db.quantum.id.represent=lambda value, row: A(row.name, _href=URL("default", "quantum", vars={"q_id": value}), _class="quantum-name", **{"_data-qid": value})
db.executesql('CREATE INDEX IF NOT EXISTS rating_idx ON quantum (rating);')
db.executesql('CREATE INDEX IF NOT EXISTS stamp_idx ON quantum (stamp);')

db.define_table(
	'quantumName',
	Field('quantum_id', db.quantum),
	Field(
		'namer', db.auth_user,
		represent=lambda cid, row: A(row.namer.username, _href=URL("default", "citizen", vars={"c_id": cid}), _class="citizen-name", **{"_data-cid": cid}) if cid else None,
	),
	Field('name', "string"),
	Field('stamp', type='datetime', default=request.now, represent=represent_time_ago),
)

db.define_table(
	'quantumNote',
	Field('quantum_id', db.quantum),
	Field('noter', db.auth_user),
	Field('note', "string"),
	Field('stamp', type='datetime', default=request.now, represent=lambda value, row: TAG.time(value, _class="timeago", _datetime="{} +0000".format(value))),
)



db.define_table(
	'ping',
	Field(
		'quantum_id', db.quantum,
		label="Quantum",
		represent=lambda qid, row: A(row.quantum_id.name, _href=URL("default", "quantum", vars={"q_id": qid}), _class="quantum-name", **{"_data-qid": qid})
	),
	Field(
		'pinger', db.auth_user,
		represent=lambda cid, row: A(row.pinger.username, _href=URL("default", "citizen", vars={"c_id": cid}), _class="citizen-name", **{"_data-cid": cid}) if cid else None,
	),
	Field(
		'pingee', db.auth_user,
		represent=lambda cid, row: A(row.pingee.username, _href=URL("default", "citizen", vars={"c_id": cid}), _class="citizen-name", **{"_data-cid": cid}) if cid else None,
	),
	Field('flavor', 'boolean', represent=lambda value, row: 1 if value else 0),
#	Field('rating', 'double'),
	Field('stamp', type='datetime', default=request.now, represent=lambda value, row: TAG.time(value, _class="timeago", _datetime="{} +0000".format(value))),
#	format='%(pinger)s -> %(pingee)s'
)
#db.ping.pinged = Field.Virtual('pinged', lambda row: TAG.time(row.ping.stamp, _class="timeago", _datetime="{} +0000".format(row.ping.stamp)))
db.ping.id.label = "Ping"
db.executesql('CREATE INDEX IF NOT EXISTS stamp_idx ON ping (stamp);')

db.auth_user._after_insert.append(lambda f, id: db.citizen.insert(id=id, user_id=id))
#db.product.auth_user.widget = SQLFORM.widgets.autocomplete(request, db.auth_user.username, limitby=(0,10), min_length=2)

# -------------------------------------------------------------------------
# after defining tables, uncomment below to enable auditing
# -------------------------------------------------------------------------
# auth.enable_record_versioning(db)
