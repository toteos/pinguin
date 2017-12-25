def get_quantum_rating(q):
	npings = q.get_npings()
	npings1 = q.db((q.db.ping.quantum_id == q.id) & (q.db.ping.flavor == 1)).count()
	npings0 = q.db((q.db.ping.quantum_id == q.id) & ((q.db.ping.flavor == None) | (q.db.ping.flavor == 0))).count()
	pings = q.db(q.db.ping.quantum_id == q.id).select(q.db.ping.ALL, orderby="ping.stamp ASC")
	ntrans = 0
	if pings:
		f = pings[0].flavor
		if f == None: f = False		# Some old pings have a flavor of None ...
		for p in pings[1:]:
			f_new = p.flavor if p.flavor != None else False
			if f_new != f:
				ntrans += 1
				f = f_new
	
	R = 0 if (npings == 0) else (0.5 + abs(0.5 - float(npings-npings1)/npings))
#		R2 = 0 if (npings == 0) else (2*abs(float(ntrans + 1)/npings - 0.5 + 0.05)/(2*0.55))**1.2
	R2 = 0 if (npings == 0) else (1 + abs(float(npings - 1)/2 - ntrans))**0.1*(1 + (float(ntrans + 1)/npings)**0.3)/2
#		R2 = 1
#		if npings == 2: R2 = 0.3
	rating = ((npings)**1.2*R*R2)**0.5
	return rating
