# Reddit Giveaway Joiner

Automatically joins reddit post giveaways by commenting on posts with the "Giveaway" tag.

- Generates comment text with the openai api
- Runs on gcp with a cron cloud function (currently set for every hour)

## Usage

### Requirements

- Terraform/OpenTofu
- Poetry

### Python Function

To package the python function for usage on gcp, run the zip_function script in `terraform/`

```
sh zip_functions.sh
```

This should output a `function_export.zip` file

### Terraform

Setting up terraform for yourself with this configuration can be tricky as you will need to configure the state file in your own google cloud bucket first

Finally, to create the infrastructure including the cron lambda, run

```
tofu init
tofu apply
```

(if you're using opentofu)
