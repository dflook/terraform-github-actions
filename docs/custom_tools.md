# Custom environments

You may need to run Terraform in a custom environment, if you need additional tools like aws-cli etc.
These are the options available to you.

## Using the released actions

The published actions run Terraform/OpenTofu in a container using a pre-prepared image.
The image is based on `debian:bookworm-slim` and is designed to be as small as possible.

It is possible to use the  `TERRAFORM_PRE_RUN` environment variable to customise the environment before running Terraform.
The command is run using `bash -xeo pipefail`.

For example:

```yaml
env:
  TERRAFORM_PRE_RUN: |
    # Install latest Azure CLI
    curl -skL https://aka.ms/InstallAzureCLIDeb | bash
     
    # Install postgres client
    apt-get install -y --no-install-recommends postgresql-client
```

The downside of this approach is that the `TERRAFORM_PRE_RUN` will be executed by every step, even when the container image is cached.

## Customising the image

Instead of the published, versioned actions you can instead run the actions directly from this repo, or a fork of it.

```yaml
jobs:
  plan:
    runs-on: ubuntu-latest
    name: Create terraform plan
    steps:
      - name: plan
        uses: dflook/terraform-github-actions/terraform-plan@main
```

This will build the image from the `image/Dockerfile` in the repo. Any changes to the Dockerfile will be reflected in the runtime environment.
This is another way to customise the environment.

The image will be rebuilt for every step, but it does benefit from caching on the actions runner if the image is not changed.
Typically, it takes 25-30 seconds to build the image on a GitHub hosted runner for the first terraform step in the job.
Any subsequent terraform steps in the job will use the cached image so will be much faster.

## Using a pre-built custom image

The most efficient way to customise the environment is to build the image once and push it to a registry.

Unfortunately, GitHub actions do not support specifying a custom image for an existing docker based action.
What you could do instead is fork this repo, and change the `image` in each of the `action.yaml` metadata files to point to your custom image.

This is what the `action.yaml` files would look like when using an image in dockerhub:

```yaml
runs:
  using: docker
  image: docker://danielflook/terraform-github-actions:v1.37.0
```

The image must be based on the image built from the dockerfile in this repo. You can use the published images as a starting point to customise, e.g.:

```dockerfile
FROM danielflook/terraform-github-actions:v1.37.0

RUN curl -skL https://aka.ms/InstallAzureCLIDeb | bash
RUN apt-get install -y --no-install-recommends postgresql-client
```

Then you can use the forked actions in your workflow:

```yaml
jobs:
  plan:
    runs-on: ubuntu-latest
    name: Create terraform plan
    steps:
      - name: plan
        uses: <my_org>/terraform-github-actions/terraform-plan@main
```
