import requests

headers = {
    "Authorization" : 'token ghp_r5***',
    "Accept": 'application/vnd.github.v3+json'
#    "Accept": '*.*',
}

OWNER = 'AcademySoftwareFoundation'
REPO = 'rez'

REF = 'main'  # branch name
REF = ''      # master/main branch

EXT = 'zip'

#url = f'https://api.github.com/repos/{OWNER}/{REPO}/{EXT}ball/{REF}'

url = "https://github.com/AcademySoftwareFoundation/rez/archive/refs/heads/master.zip"
print('url:', url)

response = requests.get(url)
open("./rez-master.zip", "wb").write(response.content)
