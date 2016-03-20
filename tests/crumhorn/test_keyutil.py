
from crumhorn import keyutil

def test_get_fingerprint_can_compute_digest_from_ssh_rsa_key():
    a_key = '''
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCmIRg2h8WgaDKCcmhR0eKMKzzKF+N3A9gvilia3JdJHQ2OPD1WUnGf97iOhVS6WYWvHaT8mvnJ+Lgmg/JaAt11TyVFDGVOxtGlMxZeiqQTbB/e+bcIs71cklrfr90i0frtoo6yAm/Uw4oz/zaInGlJXpd0F8bXDQCMooAVCI/S3eikdeZsfSiBW3GOYKYLlYoX1jWYmLQBSl4HURl7IqWO85HAufjFvG1l04Ek9roWEZVMRU8NvWarR70+cNvY/TsBrHCtan3aU/WHYMsrCm5CcV2MQ3yxKmGfsEfZ8SfyZWQJ2uSVdXqZU9SRsQADgrVG8DdBrdl9TSzzEdjdXL0l user@host
'''
    target_fingerprint = 'ef:5f:83:a5:ef:35:82:e2:14:84:f1:9d:93:54:93:c7' 

    assert keyutil.get_fingerprint(a_key) == target_fingerprint
