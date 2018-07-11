---
layout: docs
title: Hooks
---

# Overview

The purpose of this hook is to run additional setup after creating
a Synapse external bucket.  For more information please refer to the
[synapse external bucket documention](http://docs.synapse.org/articles/custom_storage_location.html)


## Available Resolvers

### synapse_external_bucket

Does the following after creation of the bucket:
* Upload an owner.txt file to the bucket.
* Send an email to the bucket owner with the bucket info.


Syntax:

```yaml
parameter|sceptre_user_data:
    <name>: !synapse_external_bucket
```

Example:

```
parameters:
  # true for read-write bucket, false (default) for read-only bucket
  AllowWriteBucket: "true"
  # Synapse username
  SynapseUserName: "jsmith"
  # true to encrypt bucket, false (default) for no encryption
  EncryptBucket: "true"
  # Email of the bucket owner
  OwnerEmail: jsmith@sagebase.org
hooks:
  after_create:
    - !synapse_external_bucket
```
