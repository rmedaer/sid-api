"""
This module contains SID Template object.
"""

import os
import json
import collections
import jsonschema
from sid.lib.git import Repository

__cookiecutter_file__ = 'cookiecutter.json'

class TemplateException(Exception):
    """
    Exception linked to template mechanism.
    """
    pass

class Template(Repository):
    """
    Milhoja/CookieCutter template behind a Git repository.
    """

    def __init__(self, path):
        """
        Construct a template repository.
        """
        super(Template, self).__init__(path)

    def validate(self, data):
        """
        Validate template parameters using JSON template generated from cookicutter.json

        Arguments:
        data -- Template parameters to be validated.

        Raises:
        ValidationError (from jsonschema)
        SchemaError (from jsonschema)
        TemplateException
        """
        jsonschema.validate(data, self.get_schema())

    def get_schema(self):
        """
        Build Cookiecutter schema from configuration file.

        Cookiecutter doesn't have a "real" JSON schema. The 'cookiecutter.json'
        file is just a set of key=question. We are translating that into a
        standard JSON schema.

        Raises:
        TemplateException
        """
        self.assert_is_open()

        try:
            with open(os.path.join(self.path, __cookiecutter_file__), 'r') as fvars:
                # Parse JSON content
                vars_list = json.loads(fvars.read(), object_pairs_hook=collections.OrderedDict)

                # Ensure 'cookiecutter.json' contains an object
                if not isinstance(vars_list, dict):
                    raise TemplateException('Could not recognize %s format' % __cookiecutter_file__)

                # Build base schema
                schema = {
                    'properties': {},
                    'required': [],
                    'additionalProperties': True
                }

                # Add each var in schema
                for key in vars_list:
                    schema['properties'][key] = {
                        'type': 'string',
                        'default': vars_list[key]
                    }

                return schema
        except IOError:
            raise TemplateException('Could not read template file: %s' % __cookiecutter_file__)
        except ValueError:
            raise TemplateException('Could not load template file: %s' % __cookiecutter_file__)
