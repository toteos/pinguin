class Citizen:
	def __init__(self, db, i):
		if not i:
			self.name = "the periphery"
		
		row_auth = None
		if isinstance(i, str):
			row_auth = db(i.lower() == db.auth_user.username.lower()).select(db.auth_user.ALL, limitby=(0,1))
		else:
			row_auth = db(db.auth_user.id == i).select(db.auth_user.ALL, limitby=(0,1))
		
		if row_auth:
			row_auth = row_auth[0]
			self.db = db
			self.id = row_auth.id
			self.name = row_auth.username
		else:
			self.id = None
		
		if self.id:
			row_c = db(self.id == db.citizen.user_id).select(db.citizen.ALL, limitby=(0,1))
		
			if row_c:
				row_c = row_c[0]
				self.rating = row_c.rating
			else:
				self.rating = None
	
	def nquanta(self):
		return self.db(self.db.quantum.holder == self.id).count()
	
	def nquanta_unlocked(self):
		return self.db((self.db.quantum.holder == self.id) & ((self.db.quantum.locked == None) | (self.db.quantum.locked == False))).count()
	
	def return_nquanta(self, n):
		rows = self.db((self.db.quantum.holder == self.id)& ((self.db.quantum.locked == None) | (self.db.quantum.locked == False))).select(self.db.quantum.ALL, limitby=(0,n))
		for row in rows:
			flavor = random.randint(0,1)
			self.db(self.db.quantum.id == row.id).update(holder=None, pinger=self.id, flavor=flavor, stamp=request.now)
			self.db.ping.insert(quantum_id=row.id, pinger=self.id, pingee=None, flavor=flavor, stamp=request.now)
			if not bool(self.db((self.db.quantumAttribute.quantum_id == row.id) & (self.db.quantumAttribute.name == "spent")).count()):
				self.db.quantumAttribute.insert(quantum_id=row.id, name="spent")
				self.db((self.db.quantumAttribute.quantum_id == row.id) & (self.db.quantumAttribute.name == "new")).delete()
	
	def generate_ping(self):
		flavor = random.randint(0,1)
		self.db.quantum.insert(mother=self.id, holder=self.id, flavor=flavor)
	
	def fetch_ping(self, pid=None):
		row = None
		if not pid: row = self.db(self.db.quantum.holder == self.id).select(self.db.quantum.ALL, limitby=(0,1))
		else: row = self.db(self.db.quantum.holder == self.id and self.db.quantum.id == pid).select(self.db.quantum.ALL, limitby=(0,1))
		if row:
			return Ping(row[0])
		else: return None
	
	def send_ping(self, pingee, pid, flavor):
		p = self.fetch_ping(pid)
		if not p.locked:
			self.db(self.db.quantum.id == p.id).update(holder=pingee.id, pinger=self.id, flavor=flavor, stamp=request.now)
			self.db.ping.insert(quantum_id=p.id, pinger=self.id, pingee=pingee.id, flavor=flavor, stamp=request.now)
	
	
	def make_quanta_table(self):
		self.db.quantum.created.readable = False
		self.db.quantum.mother.readable = False
		self.db.quantum.holder.readable = False
		self.db.quantum.name.readable = False
		quanta_table = SQLFORM.smartgrid(
			db.quantum,
			constraints=dict(quantum=db.quantum.holder == self.id),
			details=False, create=False, editable=False, deletable=False, csv=False,
#			fields=[db.quantum.id],#, db.quantum.rating, db.quantum.pinger, db.quantum.flavor, db.quantum.stamp],
			linked_tables=[],
			links = [
#				{"header": "Actions", "body": lambda row: A(T('view'), _href=URL("default", "quantum", vars={"q_id": row.id}))},
	#			lambda row: A(T('send'), _href=URL("default", "index", vars={"qid": row.id}), **{"_data-qid": row.id}),
#				{"header": "Actions", "body": lambda row: FORM(TABLE(TR("", INPUT(_type="submit", _value="lock", **{"_data-qid": row.id}))))},
				{"header": "", "body": lambda row: SPAN(T('send'), _class="form-send-trigger", **{"_data-qid": row.id, "_data-pinger": "" if not row.pinger else Citizen(db, row.pinger).name}) if not row.locked else u"\U0001F512"},
			] if self.id == auth.user.id else None,
			orderby="rating DESC",
			paginate=20,
			selectable=[('Lock/unlock', lambda qids: [Quantum(db, qid).toggle_lock() for qid in qids], 'selectable-lock')]
		)
		self.db.quantum.created.readable = True
		self.db.quantum.mother.readable = True
		self.db.quantum.holder.readable = True
		self.db.quantum.name.readable = True
		
		return quanta_table
	
	def make_pings_sent_table(self):
		grid = SQLFORM.smartgrid(
			db.ping,
			constraints=dict(ping=db.ping.pinger == self.id),
			fields=[db.ping.stamp, db.ping.quantum_id, db.ping.pingee, db.ping.flavor],
			details=False, create=False, editable=False, deletable=False, csv=False,
			links = [
				{"header": "Actions", "body": lambda row: SPAN(T('send'), _class="form-send-trigger", **{"_data-qid": row.quantum_id, "_data-pinger": "" if not row.pingee else Citizen(db, row.pingee).name}) if row.quantum_id.holder == self.id else ""},
			] if self.id == auth.user.id else None,
			orderby="stamp DESC",
		)
		
		return grid
	
	def make_pings_received_table(self):
		grid = SQLFORM.smartgrid(
			db.ping,
			constraints=dict(ping=db.ping.pingee == self.id),
			fields=[db.ping.stamp, db.ping.quantum_id, db.ping.pinger, db.ping.flavor],
			details=False, create=False, editable=False, deletable=False, csv=False,
			links = [
				{"header": "Actions", "body": lambda row: SPAN(T('send'), _class="form-send-trigger", **{"_data-qid": row.quantum_id, "_data-pinger": "" if not row.pinger else Citizen(db, row.pinger).name}) if row.quantum_id.holder == self.id else ""},
			] if self.id == auth.user.id else None,
			orderby="stamp DESC",
		)
		
		return grid

#	def __init__(self, db, i):
#		row = db(i == db.quantum.id).select(db.quantum.ALL, limitby=(0,1))
#		if row:
#			row = row[0]
#			self.id = row.id


def represent_citizen_name(cid, row):
	return A(row.holder.username, _href=URL("default", "citizen", vars={"c_id": cid}), _class="citizen-name", **{"_data-cid": cid})

