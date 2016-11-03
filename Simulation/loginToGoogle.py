import urllib, urllib2, cookielib
import os

#Gets the current directory
output_path = os.getcwd()


# https://accounts.google.com/ServiceLogin?passive=1209600&continue=https://accounts.google.com/o/oauth2/auth?openid.realm%26scope%3Demail%2Bprofile%2Bopenid%26response_type%3Dpermission%2Bid_token%26redirect_uri%3Dstoragerelay://http/qa.sso.goplus.in:8080?id%253Dauth537401%26ss_domain%3Dhttp://qa.sso.goplus.in:8080%26client_id%3D304855351312-aet7l1f21b484lrgi1h5jo3t3197l6to.apps.googleusercontent.com%26fetch_basic_profile%3Dtrue%26gsiwebsdk%3D2%26from_login%3D1%26as%3D1ad80248d4ae5e82&oauth=1&sarp=1&scc=1#identifier

# Login page for Google Finance
login_url = "https://accounts.google.com/ServiceLogin?service=finance&passive=1209600&continue=https://www.google.com/finance&followup=https://www.google.com/finance"
login_url = "https://accounts.google.com/ServiceLogin?passive=1209600&continue=https://accounts.google.com/o/oauth2/auth?openid.realm%26scope%3Demail%2Bprofile%2Bopenid%26response_type%3Dpermission%2Bid_token%26redirect_uri%3Dstoragerelay://http/qa.sso.goplus.in:8080?id%253Dauth537401%26ss_domain%3Dhttp://qa.sso.goplus.in:8080%26client_id%3D304855351312-aet7l1f21b484lrgi1h5jo3t3197l6to.apps.googleusercontent.com%26fetch_basic_profile%3Dtrue%26gsiwebsdk%3D2%26from_login%3D1%26as%3D1ad80248d4ae5e82&oauth=1&sarp=1&scc=1#identifier"
# Google Finance portfolio Download url (works after you signed in)
download_url = "https://www.google.com/finance/portfolio?pid=1&output=csv&action=viewt&ei=ypZyUZi_EqGAwAP5Vg"

username = 'abhimanyu.dutta@shuttl.com'
password = 'Is_it_me?1'

cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
login_data = urllib.urlencode({'username' : username, 'j_password' : password})
opener.open(login_url, login_data)
url = "http://qa.serviceadmin.goplus.in:8080/allocation"
response = urllib2.urlopen(url)
html = response.read()
print html


