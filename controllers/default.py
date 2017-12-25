# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

import random

# ---- example index page ----
#@auth.requires_login()
def index():
	# If not logged in:
	if not auth.user:
		return dict(
			message=T("There isn't much to do without signing in (or up)."),
		)
	
	# If logged in:
	me = Citizen(db, auth.user.id)
	qid = 0
	if "qid" in request.vars:
		qid = request.vars["qid"]
	
	
	
##	quanta_table = SQLTABLE(db(db.quantum.holder == me.id).select(db.quantum.ALL))
#	db.quantum.created.readable = False
#	db.quantum.mother.readable = False
#	db.quantum.holder.readable = False
#	quanta_table = SQLFORM.smartgrid(
#		db.quantum,
#		constraints=dict(quantum=db.quantum.holder == me.id),
#		details=False, create=False, editable=False, deletable=False, csv=False,
#		linked_tables= [],
#		links = [
#			lambda row: A(T('view'), _href=URL("default", "quantum", vars={"q_id": row.id})),
##			lambda row: A(T('send'), _href=URL("default", "index", vars={"qid": row.id}), **{"_data-qid": row.id}),
#			lambda row: SPAN(T('send'), _class="form-send-trigger", **{"_data-qid": row.id, "_data-pinger": "" if not row.pinger else Citizen(db, row.pinger).name}),
#		],
#		orderby="stamp DESC",
#		paginate=100,
#	)
#	db.quantum.created.readable = True
#	db.quantum.mother.readable = True
#	db.quantum.holder.readable = True
	quanta_table = me.make_quanta_table()
	npings = me.nquanta()
	
	
	form_generate = FORM(TABLE(TR("", INPUT(_type="submit", _value="Generate quantum"))))
	
	pid = str(qid)
#	pv = random.randint(0,1)
	if npings > 0 and qid == 0: pid = str(me.fetch_ping().id)
#	form_send = FORM(TABLE(
#		TR("Pingee:",INPUT(_type="text", _name="pingee", requires=[IS_IN_DB(db, "auth_user.username", "%(pingee)s")])),
#		TR("Quantum ID:",INPUT(_type="number", _name="pingid", value=pid, requires=IS_IN_DB(db, "quantum.id", "%(pingid)i"))),
#		TR("Ping value:",INPUT(_type="checkbox", _name="pingv", checked="checked")),
#		TR("", INPUT(_type="submit", _value="Send ping"))
#	))
	form_send = make_send_form()
#	form_send = SQLFORM.factory(
#		Field("pingee", "string", requires=[IS_IN_DB(db, "auth_user.username")], widget=SQLFORM.widgets.autocomplete(request, db.auth_user.username, limitby=(0,5), min_length=1)),
#		Field(
#			"pingid",
#			"integer",
#			default=pid,
#			requires=[IS_IN_DB(db(db.quantum.holder == auth.user.id), "quantum.id")],
##			widget=SQLFORM.widgets.autocomplete(request, db.quantum.id, limitby=(0,5), min_length=1)
#		),
#		Field(
#			"flavor",
#			"boolean",
#			default=flavor,
#		),
#		labels={
#			"flavor": "",
#		}
#	)
#	
#	form_send["_id"] = "send-ping"
#	form_send.element("div", _class="checkbox").element("label").append(LABEL(_for="no_table_flavor"))
	form_send.element("form", _id="send-ping").append(DIV(_id="send-ping-arrow"))
	
#	for thing in form_send.elements("div"):
#		thing["_class"] = "tote"
	
	if form_generate.accepts(request.vars, session, formname='generate'):
		me.generate_ping()
		redirect(URL("index"), client_side=True)
	
	if form_send.accepts(request.vars, session, formname='send'):
		pingee = Citizen(db, form_send.vars["pingee"])
		if me.id == pingee.id: response.flash = "You can't ping yourself!"
		else:
			me.send_ping(pingee, form_send.vars["qid"], form_send.vars["flavor"])
			redirect(URL("index"), client_side=True)
	
	return dict(
		table_quanta=quanta_table,
		table_pings_sent=me.make_pings_sent_table(),
		table_pings_received=me.make_pings_received_table(),
		npings=npings,
		form_generate=form_generate,
		form_send=form_send,
		pieces={"name": me.name},
		me=me,
	)

# ---- API (example) -----
@auth.requires_login()
def api_get_user_email():
    if not request.env.request_method == 'GET': raise HTTP(403)
    return response.json({'status':'success', 'email':auth.user.email})

# ---- Smart Grid (example) -----
@auth.requires_membership('admin') # can only be accessed by members of admin groupd
def grid():
    response.view = 'generic.html' # use a generic view
    tablename = request.args(0)
    if not tablename in db.tables: raise HTTP(403)
    grid = SQLFORM.smartgrid(db[tablename], args=[tablename], deletable=False, editable=False)
    return dict(grid=grid)

# ---- Embedded wiki (example) ----
def wiki():
    auth.wikimenu() # add the wiki to the menu
    return auth.wiki() 

# ---- Action for login/register/etc (required for auth) -----
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    db.auth_user.first_name.writable=False
    db.auth_user.first_name.readable=False
    db.auth_user.last_name.writable=False
    db.auth_user.last_name.readable=False
    return dict(form=auth())

# ---- action to server uploaded static content (required) ---
@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)

# ---- test:
@auth.requires_login()
def citizen():
	cid = 0
	if "c_id" in request.vars:
		cid = int(request.vars["c_id"])
	if isinstance(cid, list): cid = cid[0]
	c = Citizen(db, cid)
	return dict(
		c=c,
	)

@auth.requires_login()
def quantum():
	me = Citizen(db, auth.user.id)
	qid = 0
	if "q_id" in request.vars:
		qid = request.vars["q_id"]
	if isinstance(qid, list): qid = qid[0]
	q = Quantum(db, qid)
	tables = {}
	
	
	tables["pings"] = SQLFORM.smartgrid(
		db.ping,
		constraints=dict(ping=db.ping.quantum_id == q.id),
		fields=[db.ping.stamp, db.ping.pinger, db.ping.pingee, db.ping.flavor],
		details=False, create=False, editable=False, deletable=False, csv=False,
#		links = [{'header': 'Pinged', 'body': lambda row: TAG.time(row.stamp, _class="timeago", _datetime="{} +0000".format(row.stamp))}],
		orderby="stamp DESC",
	)
	
	
	if q.get_nnames():
#		rep_temp = db.quantumName.name.represent
#		db.quantumName.name.represent = None
		tables["names"] = SQLFORM.smartgrid(
			db.quantumName,
			constraints=dict(quantumName=db.quantumName.quantum_id == q.id),
			fields=[db.quantumName.name, db.quantumName.namer, db.quantumName.stamp],
			maxtextlength=100,
			details=False, create=False, editable=False, deletable=False, csv=False, searchable=False,
	#		links = [{'header': 'Pinged', 'body': lambda row: TAG.time(row.stamp, _class="timeago", _datetime="{} +0000".format(row.stamp))}],
			orderby="stamp DESC",
		)
#		db.quantumName.name.represent = rep_temp
	else: tables["names"] = False
	
	
	form_rename = SQLFORM.factory(
		Field("name", "string", requires=IS_LENGTH(maxsize=50)),
#		Field(
#			"cost", "integer", default=10*db(db.quantumName.quantum_id == qid).count(),
#			readonly=True,
#		),
		labels={
			"name": "Name",
		}
	)
	
	
	form_send = make_send_form(qid=q.id, pinger="" if not q.pinger else Citizen(db, q.pinger).name)
	
	if form_rename.accepts(request.vars, session, formname='rename'):
		if True:#me.nquanta() > 1000:
			q.rename(form_rename.vars["name"])
			redirect(URL("quantum", vars={"q_id": q.id}), client_side=True)
		else:
			response.flash = "You can't afford this!"
	
	
	if form_send.accepts(request.vars, session, formname='send'):
		pingee = Citizen(db, form_send.vars["pingee"])
		if me.id == pingee.id: response.flash = "You can't ping yourself!"
		else:
			me.send_ping(pingee, form_send.vars["qid"], form_send.vars["flavor"])
			redirect(URL("quantum", vars={"q_id": q.id}), client_side=True)
	
	return dict(
		q=q,
		qid=q.id,
		name=q.name,
		tables=tables,
		form_rename=form_rename,
		form_send=form_send,
	)

@auth.requires_login()
def history():
	grid = SQLFORM.smartgrid(
		db.ping,
		details=False, create=False, editable=False, deletable=False, csv=False,
		fields=[db.ping.stamp, db.ping.quantum_id, db.ping.pinger, db.ping.pingee, db.ping.flavor],
#		links = [
##			{'header': "Pinged", 'body': lambda row: TAG.time(row.stamp, _class="timeago", _datetime="{} +0000".format(row.stamp))},
#			{"header": "Actions", "body": lambda row: A(T('view quantum'), _href=URL("default", "quantum", vars={"q_id": row.quantum_id}))},
#		],
		orderby="stamp DESC",
		paginate=50,
	)
	return dict(grid=grid)

@auth.requires_login()
def quanta():
	db.quantum.name.readable = False
	grid = SQLFORM.smartgrid(
		db.quantum,
		details=False, create=False, editable=False, deletable=False, csv=False,
		linked_tables= [],
#		links = [
#			{"header": "Actions", "body": lambda row: A(T('view quantum'), _href=URL("default", "quantum", vars={"q_id": row.id}))},
#		],
		orderby="quantum.rating DESC",
		paginate=50,
	)
	db.quantum.name.readable = True
	return dict(grid=grid)

@auth.requires_login()
def citizens():
	grid = SQLFORM.smartgrid(
		db.citizen,
		details=False, create=False, editable=False, deletable=False, csv=False,
		fields=[db.citizen.user_id, db.citizen.rating],
		linked_tables= [],
		orderby="citizen.rating DESC",
		paginate=50,
	)
	return dict(grid=grid)


@auth.requires_login()
def email():
	result = mail.send(to=['tote@connivance.net'],
          subject='ping test',
          # If reply_to is omitted, then mail.settings.sender is used
#          reply_to='admin@pinguin.fish',
          message='This is a test')
	return dict(result=result)
	
@auth.requires_login()
def debug():
	return dict()

@auth.requires_login()
def news():
	return dict()
