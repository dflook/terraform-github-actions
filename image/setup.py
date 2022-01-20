from setuptools import find_packages, setup

setup(
    name='terraform-github-actions',
    version='1.0.0',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    package_data={'terraform_version': ['backend_constraints.json']},
    entry_points={
        'console_scripts': [
            'terraform-backend=terraform_backend.__main__:main',
            'terraform-version=terraform_version.__main__:main',
            'terraform-cloud-workspace=terraform_cloud_workspace.__main__:main'
        ]
    },
    install_requires=[
        'requests',
        'python-hcl2'
    ]
)
