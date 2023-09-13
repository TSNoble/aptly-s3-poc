#

## Table of Contents

- [Overview](#overview)
- [First time setup](#first-time-setup)
- [Design](#design)
   - [Architecture](#architecture)
   - [Security Principles](#security-principles)
- [Developer Guide](#developer-guide)
   - [Prerequisites](#prerequisites)
   - [Getting started](#getting-started)
   - [Adding a new dependency](#adding-a-new-dependency)
   - [Downloading dependencies (Devloper)](#downloading-dependencies-as-a-developer)

## Overview

Rivelin Netshape makes use of a number of build from source dependencies. This repository contains AWS infrastructure used to manage these dependencies as debian packages via an s3 hosted Aptly repository, along with least-privelege IAM roles and groups to manage access.

## First time setup

In order for a GitHub runner to authenticate with AWS, an Administrator must set up an Identity Provider within IAM. This is a step which only needs to be performed once per AWS account:

1. Log in to the AWS Console
2. Navigate to IAM > Identity Providers > Add Provider
3. Configure the Provider with the following settings:
   - Provider Type: OpenID Connect
   - Provider URL: token.actions.githubusercontent.com
   - Audience: sts.amazonaws.com
4. Copy the Amazon Resource Name (ARN) of the Provider into a AWS_GITHUB_PROVIDER_ARN secret of the Deploy environment

Furthermore, a Personal Access Token must be generated to allow the workflows of this repository to update their secrets:

1. Log in to GitHub
2. Navigate to Settings > Developer Settings > Personal Access Tokens > Fine-Grained Tokens > Generate New Token
3. Configure the Token with the following settings:
   - Repository Acess: Only Select Repositories > {This Repository}
   - Permissions > Repository Permissions:
      - Environments: Read and Write
      - Secrets: Read and Write
4. Copy the contents of the PAT into a repository-level REPOSITORY_TOKEN secret

## Design

### Architecture

Diagram to add

### Security Principles

- Only the GitHub runner for this repository may perform deployments.
- Only the Github runner for this repository may publish new snapshots.
- Only the Github runner for this repository may modify the package signing key-pair.
- Github runners may download packages provided they are permitted to assume the read-only role.
- Developers may download packages provided they are a member of the read-only group.

## Developer Guide

### Prerequisites

In order to use and develop against this repository, you must have an AWS account associated with the Rivelin Robotics organisation. This can be confirmed by attempting to log in to AWS via JumpCloud.

Next, you must configure your system to allow your AWS credentials to be used:

1. Log in to the AWS Console
2. Navigate to IAM > Users > \{Your User\} > Security Credentials > Create Access Key
3. Choose Command Line Interaface and continue until the key is generated
4. Copy the key details to ~/.aws/credentials:

```
[default]
aws_access_key_id={Your Access Key ID}
aws_secret_access_key={Your Secret Access Key}
```

### Getting started

This repository depends on Aptly and gpg1, which can be installed as follows:

```sh
echo "deb http://repo.aptly.info/ squeeze main" > /etc/apt sources.list.d/aptly.list
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys EE727D4449467F0E
sudo apt-get update && sudo apt-get install -y aptly gpgv1 gnupg1
```

Next, navigate to the repository and create a new Python virtual environment:

```sh
python3 -m venv .venv
```

Finally, activate the virtual environment and install the remaining dependencies
```
source .venv/bin/activate
pip3 install -r requirements.txt
pip3 install -r requirements-dev.txt
```

### Adding a new dependency

To add a new source depndency, you must first generate a debian package from the source code and add it to this repository.

Begin by following any steps provided by the source dependency to build the code. For the remainder of this tutorial, we will assume the build artefacts are located under `test-package/build`.

Next, create a directory for the debian package, e.g.

```sh
mkdir test_package-0.0.1_x86_64
```

Within this directory, create the `DEBIAN/control` file containing package metadata. For source dependencies, this information can likely be found in the repository of the dependency.

```
Package: test-package
Version: 0.0.1
Maintainer: foo@bar.com
Architecture: x86_64
Description: A test package
```

Copy the built code into the package directory. The path denotes where the package will be installed. For most dependencies, this should be the `/usr/include`, `/usr/lib`, `/usr/bin`, and `/usr/share` directories, e.g.

```
mdkir -p test_package-0.0.1_x86_64/usr/include/test-package
cp -r test-package/build/include test_package-0.0.1_x86_64/usr/include/test-package

mdkir -p test_package-0.0.1_x86_64/usr/lib/test-package
cp -r test-package/build/lib test_package-0.0.1_x86_64/usr/lib/test-package

mdkir -p test_package-0.0.1_x86_64/usr/bin/test-package
cp -r test-package/build/bin test_package-0.0.1_x86_64/usr/bin/test-package

mdkir -p test_package-0.0.1_x86_64/usr/share/test-package
cp -r test-package/build/share test_package-0.0.1_x86_64/usr/share/test-package
```

Finally, build the package using `dpkg-deb`:

```sh
dpkg-deb -Zxz --build test_package-0.0.1_x86_64
```

The `-Zxz` flags are required to ensure that `xz` compression is used, as Aptly does not support the default compression type.

To test the validity of the package, you can try adding it to a local Aptly repository:

```
aptly repo create test-repository
aptly repo add test-repository test_package-0.0.1_x86_64.deb
```

Copy the generated `.deb` package to the `debs` directory of this repository and raise a pull request. Once merged, the Publish Snapshot workflow can be run to update the Aptly repository.

### Downloading dependencies (Developer)

_Note: This process may be subject to change_

Run the following lines of code to add the public key and source of the repository:

```sh
curl -u {Your Access Key ID}:{Your Secret Access Key} dev.downloads.rivel.in/public.pgp | sudo apt-key add
echo "deb https://dev.downloads.rivel.in jammy main" > /etc/apt/sources.list.d/rivelin-source-dependencies.list
echo "machine dev.download.rivel.in login {Your Access Key ID} password {Your Secret Access Key}" > /etc/apt/auth.conf.d/rivelin-source-dependencies.conf
```

Check that everything is working by attempting to install a package, e.g.

```sh
sudo apt-get update
sudo apt-get install test-package
```

If you are getting a 403 error trying to access the repository, you may need an Administrator to add your AWS user to the AptlyRepositoryReadOnlyGroup.
