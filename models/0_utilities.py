def represent_time_ago(value, row):
	return TAG.time(value, _class="timeago", _datetime="{} +0000".format(value))
