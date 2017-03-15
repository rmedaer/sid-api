"""
This module contains SID Template object.
"""

import os
import re
import json
import collections
import urlparse
import jsonschema
from sid.lib.git import Repository, __tag_prefix__

__cookiecutter_file__ = u'cookiecutter.json'
__default_version_pattern__ = r'\S'

class TemplateException(Exception):
    """
    Exception linked to template mechanism.
    """
    pass

class Template(Repository):
    """
    Milhoja/CookieCutter template behind a Git repository.
    """

    def __init__(self, path, version_pattern=__default_version_pattern__):
        """
        Construct a template repository.
        """
        super(Template, self).__init__(path)
        self.version_pattern = version_pattern

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

    def get_name(self):
        """
        Get template name from path.
        """
        # Analyze template source; get parsed url result
        url = urlparse.urlparse(self.path)

        # Compute file name from url path
        return os.path.splitext(os.path.basename(url.path))[0]

    def get_versions(self):
        """
        List available version of a given template.
        """
        self.assert_is_open()

        prog = re.compile(self.version_pattern)
        return [tag for tag in self.get_tags() if prog.match(tag)]

    def checkout_version(self, version):
        """
        Checkout template local copy into given version.

        Arguments:
        version -- Reference to checkout.
        """
        self.assert_is_open()

        if version not in self.get_versions():
            raise TemplateException('Given version not available')

        self.checkout(__tag_prefix__ + version)

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
