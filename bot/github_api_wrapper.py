import os

import requests


class GithubApiWrapper:
    org = os.environ['GITHUB_ORG']
    api = 'https://api.github.com'
    endpoints = {'list_organization_repositories': f'{api}/orgs/{org}/repos'}

    @classmethod
    def list_organization_repositories(cls):
        """
        Retrieves JSON from the orgs/{org}/repos endpoint
        :return: Dictionary returned from Github endpoint
        """
        response = requests.get(
            cls.endpoints['list_organization_repositories']
        )
        response.raise_for_status()
        return response.json()

    @classmethod
    def get_org_repos(cls):
        """
        Returns all repos that belong to os.environ['GITHUB_ORG']
        :return: List of tuples containing strings [(name, desc, url)]
        """
        repo_list = []
        repos = cls.list_organization_repositories()
        for repo in repos:
            repo_list.append((repo['name'], repo['description'], repo['html_url']))
        return repo_list
