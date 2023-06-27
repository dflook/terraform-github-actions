from setuptools import find_packages, setup

setup(
    name='terraform-github-actions',
    version='1.36.0',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    package_data={'terraform_version': ['backend_constraints.json']},
    entry_points={
        'console_scripts': [
            'terraform-backend=terraform_backend.__main__:main',
            'terraform-version=terraform_version.__main__:main',
            'terraform-cloud-workspace=terraform_cloud_workspace.__main__:main',
            'github_pr_comment=github_pr_comment.__main__:main',
            'plan_summary=plan_summary.__main__:main',
            'terraform-cloud-state=terraform_cloud_state.__main__:main',
            'remote-run-id=terraform_cloud_state.__main__:remote_run_id',
            'get-terraform-checksums=terraform_version.get_checksums:main',
            'lock-info=lock_info.__main__:main'
        ]
    },
    install_requires=[
        'requests',
        'python-hcl2',
        'canonicaljson'
    ]
)
