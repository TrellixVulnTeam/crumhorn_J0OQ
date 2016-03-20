
import base64
import hashlib

# http://stackoverflow.com/a/6682934
def get_fingerprint(id_pub):
	key = base64.b64decode(id_pub.strip().split()[1].encode('ascii'))
	fp_plain = hashlib.md5(key).hexdigest()
	return ':'.join(a+b for a,b in zip(fp_plain[::2], fp_plain[1::2]))
