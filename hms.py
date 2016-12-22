# hms.py, written by Luitien Pan
# Functions for handling HH:MM:SS time strings.

def sec2hms(seconds):
	H = int(seconds) / 3600
	t = seconds % 3600
	M = int(t) / 60
	S = t % 60
	return H,M,S

def sec2str(seconds):
    return "%02d:%02d:%02d" % sec2hms (seconds)

def hms2sec(H, M = 0, S = 0):
	return float(H) * 3600 + float(M) * 60 + float(S)

def str2sec(HMS):
	'''"H:M:S" -> seconds'''
	while HMS.count(':') < 2:
		HMS = '0:' + HMS
	return hms2sec( *HMS.split(':') )

def hmsdiff(str1, str2):
    '''Returns str1 - str2, in seconds.'''
    return str2sec(str2) - str2sec(str1)
