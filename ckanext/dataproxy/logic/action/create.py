from ckan.logic import get_action
import pylons.config as config
from simplecrypt import encrypt
from binascii import hexlify

orig_resource_create = get_action('resource_create')
orig_resource_update = get_action('resource_update')

def dataproxy_resource_create(context, data_dict=None):
    """
    Intercepts default resource_create action and encrypts password if resource is dataproxy type
    Args:
        context: Request context.
        data_dict: Parsed request parameters.
    Returns:
        see get_action('resource_create').
    Raises:
        Exception: if ckan.dataproxy.secret configuration not set.
    """
    #If not set, default to empty string
    url_type = data_dict.get('url_type')

    if url_type == 'dataproxy':
        secret = config.get('ckan.dataproxy.secret', False)
        if not secret:
            raise Exception('ckan.dataproxy.secret must be defined to encrypt passwords')
        password = data_dict.get('db_password')
        #replace password with a _password_ placeholder
        data_dict['url'] = 'tmpURL' #data_dict['url'].replace(password, '_password_')
        #encrypt db_password
        data_dict['db_password'] = hexlify(encrypt(secret, password))

    data_dict = orig_resource_create(context, data_dict)

    site_url = config.get('ckan.site_url', '127.0.0.1')
    data_dict['url'] = '{0}/api/3/action/datastore_search?resource_id={1}&downloaded=true'.format(site_url, data_dict['id'])

    return orig_resource_update(context, data_dict)
