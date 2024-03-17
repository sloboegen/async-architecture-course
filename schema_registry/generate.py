import os


def prepate_output_path(input_path: str) -> str:
    output_path = input_path.replace("/schemas/", "/models/").replace(".json", ".py")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w"):
        pass

    return output_path


def generate_cmd(input_path: str, output_path: str) -> str:
    return " ".join(
        [
            "datamodel-codegen",
            f"--input {input_path}",
            '--input-file-type jsonschema',
            f"--output {output_path}",
            "--strict-nullable",
            "--enum-field-as-literal all",
            "--use-default",
        ]
    )


PATH_2_SCHEMAS = os.path.join("schema_registry", "schemas")


for root, _, files in os.walk(PATH_2_SCHEMAS):
    if not files:
        continue

    for file in files:
        input_path = os.path.join(root, file)
        output_path = prepate_output_path(input_path)
        cmd = generate_cmd(input_path, output_path)

        print(cmd)

        status_code = os.system(cmd)
        assert status_code == 0
