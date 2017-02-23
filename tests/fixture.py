# -*- coding: utf-8 -*-

""" This module contains functions usefull to initialize fixtures. """

import os

from shutil import rmtree
from pygit2 import init_repository

def gitolite_fixture(path):
    """
    This function create Gitolite configuration under Git repository.
    If repository already exists it will remove it before.
    """

    main_file = 'gitolite.conf'
    admin_config = os.path.join(path, main_file)

    # Remove previous repository
    rmtree(path, ignore_errors=True)

    # Initialize repository
    repo = init_repository(path)

    # Write main Gitolite configuration
    open(admin_config, 'w').write(
        "repo projects/my-first-project\n"
        "	R = alice\n"
        "	RW = bob\n"
        "	C = eve\n"
        "\n"
        "repo projects/my-next-project\n"
        "	RW = alice bob eve\n"
        "\n"
        "\n"
        "repo templates/my-first-template\n"
        "	R = alice\n"
        "	RW = bob\n"
        "	C = eve\n"
        "\n"
        "repo templates/my-next-template\n"
        "	RW = alice bob eve\n"
    )

    # Commit changes
    repo.index.read()
    repo.index.add(main_file)
    repo.create_commit(
        'HEAD',
        repo.default_signature,
        repo.default_signature,
        'Initialized fixture repository',
        repo.index.write_tree(),
        [] if repo.head_is_unborn else [repo.head.target]
    )
    repo.index.write()

    return admin_config
