import class_cie_con_mod
import json
from collections import defaultdict
from classMexMobileOnly import MexSubscription, Attributes, jdefault


testplant1=  '172.30.1.1'

def cie_connect(username, password):
    prov = class_cie_con_mod.cie_prov( str(testplant1 + ':8182'), "/cie-rest/provision", username, password)
    return prov


def setSub(id_property = None, last_modified = None, created = None, allow_tags = None, attributes = None):
	""" This subscription should use the class classMexMobileOnlySubscription to create the json
	for the subscription related commands.
	"""



	sub = MexSubscription()
	sub.id = id_property
	sub.lastModified = last_modified
	sub.created = created
	sub.allowTags = allow_tags
	sub.attributes = [attributes]
	
	json_string = (json.dumps(sub, default = jdefault))
	return json_string


def changeMexF2MState(username, password, href, state, lastModified, created, id_prop):
	ngin = cie_connect(username,password)

	attrib = Attributes()
	attrib.id = "cdpnMap"
	attrib.value = state

	attributes = attrib
	allowTags = False
	id_property = id_prop

	json_string = setSub(id_property, lastModified, created, allowTags, attributes)

	exitCode = ngin.put_cie_json_object(href, json_string)
	if exitCode == 0:
		return True
	else:
		return None

def changeMexM2FState(username, password, href, state, lastModified, created, id_prop):
	ngin = cie_connect(username,password)

	attrib = Attributes()
	attrib.id = "cliMap"
	attrib.value = state

	attributes = attrib
	allowTags = False
	id_property = id_prop

	json_string = setSub(id_property, lastModified, created, allowTags, attributes)

	exitCode = ngin.put_cie_json_object(href, json_string)
	if exitCode == 0:
		return True
	else:
		return None

def extract_sub_json (username, password, sub):
    """ To extract subscription json. """
    ngin = cie_connect (username, password)
    sub_data = ngin.get_cie_subscription(sub)
    return sub_data

def perform_cie_logon (username, password):
	ngin = cie_connect (username, password)
	return_code = ngin.get_cie_logon()
	return return_code

def get_list_of_mex_subs(username, password, object):
	ngin = cie_connect(username, password)
	return_code = ngin.get_cie_object(object)

	return return_code

def get_mobile_only_sub_details(username, password, object):
	ngin = cie_connect(username, password)
	return_code = ngin.get_cie_object(object)
	return return_code

def modify_mobile_only_sub(username, password, object, data):
	ngin = cie_connect (username, password)
	return_code = ngin.put_cie_object(object, data)
	return return_code

def get_accountRef(username, password, object):
	pass

def get_subscriptionRef():
	pass

