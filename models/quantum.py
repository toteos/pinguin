class Quantum:
	def __init__(self, db, qid):
		row = None
		row = db(db.quantum.id == qid).select(db.quantum.ALL, limitby=(0,1))
		
		
		self.locked = False
		
		if row:
			row = row[0]
			self.db = db
			self.id = row.id
			self.holder = row.holder
			self.pinger = row.pinger
			self.mother = row.mother
			self.name = row.name
			self.rating = row.rating
			self.created = row.created
			self.stamp = row.stamp
			self.locked = row.locked
			self.row = row
	
	def rename(self, name):
		if self.holder == auth.user.id:
			self.db(self.db.quantum.id == self.id).update(name=name)
			self.db.quantumName.insert(quantum_id=self.id, namer=self.holder, name=name, stamp=request.now)
	
	def toggle_lock(self):
		if self.holder == auth.user.id:
			self.db(self.db.quantum.id == self.id).update(locked=not self.locked)
	
	def lock(self):
		if self.holder == auth.user.id:
			self.db(self.db.quantum.id == self.id).update(locked=True)
	
	def unlock(self):
		if self.holder == auth.user.id:
			self.db(self.db.quantum.id == self.id).update(locked=False)
	
	def get_holder_name(self):
		return Citizen(self.db, self.holder).name
	
	def get_mother_name(self):
		return Citizen(self.db, self.mother).name
	
	def get_npings(self):
		return self.db(self.db.ping.quantum_id == self.id).count()
	
	def get_nnames(self):
		return self.db(self.db.quantumName.quantum_id == self.id).count()
	
	def update_rating(self):
		rating = get_quantum_rating(self)
		self.row.update_record(rating=rating)
		self.rating = rating
	
#	def nquanta(self):
#		return self.db(self.db.quantum.holder == self.id).count()
#	
#	def generate_ping(self):
#		flavor = random.randint(0,1)
#		self.db.quantum.insert(mother=self.id, holder=self.id, flavor=flavor)
#	
#	def fetch_ping(self, pid=None):
#		row = None
#		if not pid: row = self.db(self.db.quantum.holder == self.id).select(self.db.quantum.ALL, limitby=(0,1))
#		else: row = self.db(self.db.quantum.holder == self.id and self.db.quantum.id == pid).select(self.db.quantum.ALL, limitby=(0,1))
#		if row:
#			return ping(row[0])
#		else: return None
#	
#	def send_ping(self, pingee, pid, flavor):
#		p = self.fetch_ping(pid)
#		self.db(self.db.quantum.id == p.id).update(holder=pingee.id, pinger=self.id, flavor=flavor, stamp=request.now)
#		self.db.ping.insert(quantum_id=p.id, pinger=self.id, pingee=pingee.id, flavor=flavor, stamp=request.now)


def make_send_form(qid=None, pinger=""):
	flavor = random.choice([True, False])
	
	form = SQLFORM.factory(
		Field(
			"pingee",
			"string",
			default=pinger,
			requires=[IS_IN_DB(db, "auth_user.username")],
			widget=SQLFORM.widgets.autocomplete(request, db.auth_user.username, limitby=(0,5), min_length=1)
		),
		Field(
			"qid",
			"integer",
			default=qid,
			requires=[IS_IN_DB(db(db.quantum.holder == auth.user.id), "quantum.id")],
#			widget=SQLFORM.widgets.autocomplete(request, db.quantum.id, limitby=(0,5), min_length=1)
		),
		Field(
			"flavor",
			"boolean",
			default=flavor,
		),
		labels={
			"qid": "quantum",
			"flavor": "",
		}
	)
	
	form["_id"] = "send-ping"
#	form.element("div", _id="no_table_pingee__row").append(DIV(_class="form-blocker"))
	form.element("div", _class="checkbox").element("label").append(LABEL(_for="no_table_flavor"))
	
	
	return form
