datamodel-codegen  --input schema_registry/schemas/account/role_changed/v1.json --input-file-type jsonschema --output schema_registry/models/account/role_changed/v1.py --strict-nullable --enum-field-as-literal all --use-default

pip wheel . -w wheels
