import os
import re

def generate_prompts():
    plan_file = 'image_generation_plan.md'
    template_file = 'nanobanana_template.md'

    if not os.path.exists(plan_file):
        print(f"Error: {plan_file} not found.")
        return
    if not os.path.exists(template_file):
        print(f"Error: {template_file} not found.")
        return

    # Read Template
    with open(template_file, 'r', encoding='utf-8') as f:
        template_content = f.read()

    # Read Plan
    with open(plan_file, 'r', encoding='utf-8') as f:
        plan_lines = f.readlines()

    # Parse Plan
    # Table headers: | ID | File Name | Group | Proposed Image Filename | Relative Link Path | Prompt | Insertion Point |
    # We need "Proposed Image Filename" (index 3), "Relative Link Path" (index 4) and "Prompt" (index 5)
    
    header_found = False
    headers = []
    
    production_base_path = os.path.dirname(os.path.abspath(__file__))

    for line in plan_lines:
        line = line.strip()
        if not line.startswith('|'):
            continue
        
        # Split by pipe, ignore first and last empty strings from split
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 3: # Not a valid table row
            continue
            
        # Clean up empty start/end if present (due to leading/trailing pipes)
        if parts[0] == '': parts.pop(0)
        if parts[-1] == '': parts.pop(-1)

        if not header_found:
            # Check if this is the header row
            if 'Proposed Image Filename' in parts and 'Prompt' in parts:
                headers = parts
                header_found = True
                try:
                    filename_idx = headers.index('Proposed Image Filename')
                    rel_path_idx = headers.index('Relative Link Path')
                    prompt_idx = headers.index('Prompt')
                except ValueError:
                    print("Error: Could not find required columns in header.")
                    return
            continue
        
        if '---' in line: # Separator line
            continue

        # Data row
        if len(parts) > max(filename_idx, rel_path_idx, prompt_idx):
            filename_raw = parts[filename_idx]
            rel_path_raw = parts[rel_path_idx]
            prompt = parts[prompt_idx]
            
            # Convert <br> tags to newlines for the template insertion
            prompt = prompt.replace('<br>', '\n')

            if not filename_raw or not prompt:
                continue

            # Check if image already exists in production
            # Example rel_path: ./other_soft/hm_activeperl/cnt_hm_activeperl_source_example_output.png
            if rel_path_raw.startswith('./'):
                clean_rel_path = rel_path_raw[2:]
            else:
                clean_rel_path = rel_path_raw

            prod_path = os.path.join(production_base_path, clean_rel_path.replace('/', os.sep))
            
            if os.path.exists(prod_path):
                print(f"Skipping: Already exists in production: {prod_path}")
                continue

            # Process Filename
            # "cnt_hm_activeperl_architecture_diagram.png" -> "cnt_hm_activeperl_architecture_diagram.txt"
            root, ext = os.path.splitext(filename_raw)
            txt_filename = root + '.txt'

            # Define output path (current directory)
            output_path = txt_filename

            if os.path.exists(output_path):
                print(f"Skipping existing file: {output_path}")
                continue

            # Apply Template
            file_content = template_content.replace('{{INSERT}}', prompt)

            # Write File
            try:
                with open(output_path, 'w', encoding='utf-8') as out_f:
                    out_f.write(file_content)
                print(f"Created: {output_path}")
            except Exception as e:
                print(f"Error writing {output_path}: {e}")

if __name__ == "__main__":
    generate_prompts()
