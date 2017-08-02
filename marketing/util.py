import requests


class GithubClient:
    api_url = 'https://api.github.com'

    def get_org_repos(self, org: str):
        r = requests.get(f'{self.api_url}/orgs/{org}/repos',
                         headers={
                             # Include the "topics"
                             'Accept': 'application/vnd.github.mercy-preview+json'  # noqa
                         },
                         params={
                             'type': 'public',
                         })
        r.raise_for_status()
        return r.json()
