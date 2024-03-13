import requests
import os
import sys
PAGE_LIMIT = 100
API_KEY = 'YOUR GITHUB API KEY HERE'
RES_LIMIT = 3
EXTENSIONS = ('bin','hex')

class GithubScraper:
    def __init__(self,apikey):
        self.headers = {"Authorization": "Bearer "+ apikey}
        self.keyword = ""
    def write_file_in_folder(self,folder_path, filename, content):
        # Check if the folder exists, if not, create it
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Write the file in the folder
        with open(os.path.join(folder_path, filename), 'wb') as file:
            file.write(content)

    def download_file(self,url, filename,reponame):
        response = requests.get(url)
        self.write_file_in_folder(os.path.join('./scrape_'+self.keyword, reponame), filename, response.content)

    def get_repos(self,keyword, num_pages,res_limit):
        downloaded_files = 0
        self.keyword = keyword
        for page in range(1, num_pages + 1):
            url = f"https://api.github.com/search/repositories?q={keyword}&page={page}"
            response = requests.get(url,headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                repos = data['items']
                for repo in repos:
                    print(f"Name: {repo['name']}, URL: {repo['html_url']}")
                    url = f"https://api.github.com/repos/{repo['full_name']}/releases"
                    #print(url)
                    response = requests.get(url,headers=self.headers)
                    data = response.json()
                    releases = data
                    filesPerRelease = res_limit
                    for release in releases:
                        if filesPerRelease == 0:
                            break
                        if 'assets' in release:
                            for asset in release['assets']:
                                #print("+>" + asset['name'])
                                if any(asset['name'].endswith(s) for s in EXTENSIONS):
                                    self.download_file(asset['browser_download_url'],asset['name'],repo['full_name'])
                                    print("> " + asset['name'])
                                    downloaded_files += 1
                                    filesPerRelease -= 1
                                    if filesPerRelease == 0:
                                        break
            else:
                print(f"Failed to fetch data, status code: {response.status_code}")
        return downloaded_files

def main():    
    if len(sys.argv) < 2:
        print("usage: ghscraper.py [keyword]")
        sys.exit(-1)


    ghscraper = GithubScraper(API_KEY)

    ret = ghscraper.get_repos(sys.argv[1], PAGE_LIMIT, RES_LIMIT)

    print(f"Extracted {ret} files")

if __name__ == "__main__":
    main()
