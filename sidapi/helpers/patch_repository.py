# -*- coding: utf-8 -*-

""" This module contains functions to patch a given repository with
a JSON patch. """

import re
from tornado.web import HTTPError
from pyolite2 import Rule

def patch_repo(repo, patches):
    """ Patch a repository with given JSON patch """

    for patch in patches:
        # Renaming a project is currently not implemented
        if patch['path'] == '/name' and patch['op'] == 'replace':
            raise HTTPError(
                status_code=501,
                log_message='Renaming a project is currently not implemented. '
                            'Please contact your administrator.'
            )

        # You can only make operations on /rules/{index}
        m_rules = re.match('^/rules/([0-9]*)$', patch['path'])
        if not m_rules:
            raise HTTPError(
                status_code=400,
                log_message='Patch not supported. '
                            'Please contact your administrator.'
            )

        # Add a new rule
        if patch['op'] == 'add':
            # Create a new rule
            rule = Rule(patch['value']['perm'], '')
            rule += patch['value']['users']
            repo.append(rule)

        # Replace an existing rule
        elif patch['op'] == 'replace':
            index = int(m_rules.group(1))
            try:
                rule = Rule(patch['value']['perm'], '')
                rule += patch['value']['users']
                repo.replace_rule(repo.rules()[index], rule)
            except IndexError:
                raise HTTPError(
                    status_code=400,
                    log_message='Failed to replace rule [%d] (rule not found)' % index
                )

        # Remove an existing rule
        elif patch['op'] == 'remove':
            index = int(m_rules.group(1))
            try:
                repo.remove_rule(repo.rules()[index])
            except IndexError:
                raise HTTPError(
                    status_code=400,
                    log_message='Failed to remove rule [%d] (rule not found)' % index
                )
