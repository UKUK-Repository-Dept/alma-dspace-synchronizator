from configparser import ConfigParser, ExtendedInterpolation
import requests


config = ConfigParser(interpolation=ExtendedInterpolation())

try:
    config.read('dspace_api/api_config.ini')
except Exception as e:
    raise e

cookie = None

print("CONFIG: {}".format(config))

def login():
    
    headers = {'Accept': 'application/json', 'Accept-Charset': 'UTF-8'}
    
    email = config.get('LOGIN', 'username')
    password = config.get('LOGIN','password')
    
    #print("email:", email)
    #print("password:", password)

    data = {"email":email,"password":password}
    # data = 'email='+str(email).lstrip().rstrip()+'&password='+str(password).lstrip().rstrip()
    #data = '{"email":"'+email+'", "password":"'+password+'"}'
    url = config.get('GENERAL','api_root') + config.get('LOGIN', 'endpoint')
    # print('URL', url)
    
    request = requests.post(url=url, headers=headers, data=data)
    
    # print(request.text)

    if request.status_code == requests.codes.ok:
        #print(request.cookies.get('JSESSIONID'))
        return request.cookies.get('JSESSIONID')
    else:
        raise Exception('Failed to login to DSpace API:\n'+'Status code ' + str(request.status_code)+': '+request.reason)



try:
    cookie = login()

    if cookie is None:
        raise Exception("No JSESSIONID - login to DSpace API not successfull") 
except Exception as e:
    raise e
