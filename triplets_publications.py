import json

def extract_triplets_full_hierarchy(json_obj, parent_keys=None):
    """
    Extract triplets from nested JSON preserving all intermediate keys.
    parent_keys: list of keys representing the hierarchy
    """
    if parent_keys is None:
        parent_keys = []

    triplets = []

    if isinstance(json_obj, dict):
        for key, value in json_obj.items():
            new_parent_keys = parent_keys + [key]
            if isinstance(value, dict) or isinstance(value, list):
                triplets.extend(extract_triplets_full_hierarchy(value, new_parent_keys))
            else:
                triplets.append((*new_parent_keys, value))
    elif isinstance(json_obj, list):
        for item in json_obj:
            if isinstance(item, (dict, list)):
                triplets.extend(extract_triplets_full_hierarchy(item, parent_keys))
            else:
                triplets.append((*parent_keys, item))

    return triplets

# --- Read JSON from file ---
json_file_path = "/content/structured_data.json"  # Replace with your file path
with open(json_file_path, "r", encoding="utf-8") as f:
    nested_json = json.load(f)

# Extract triplets
triplets = extract_triplets_full_hierarchy(nested_json)

# Print triplets
for t in triplets:
    print(t)






