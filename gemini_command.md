---
description: Generate an image generation plan for a range of Markdown files based on their content analysis.
---

// turbo-all
1.  **Parse Arguments**:
    - You will receive an argument string like `1-20`. Parse this to get the `start_id` and `end_id`.

2.  **Iterate and Analyze**:
    - For each `current_id` from `start_id` to `end_id`:
        a.  **Identify and Read File**:
            - **Lookup Filename**:
                - Read `LIST.md` from the root directory.
                - Find the row where the "番号" (Number) column matches `<current_id>`.
                - Extract the "ファイルパス" (File Path) from that row (e.g., `docs/react_study_001.md`).
            - **Read Content**:
                - Read the file content using the extracted path.

        b.  **Analyze Content**:
            - Review the content (from direct Markdown read).
            - **CRITICAL**: Identify EVERY single location where an image could potentially be added. 
            - **Quantity Policy (EXTREMELY IMPORTANT)**: The user has a **STRONG PREFERENCE** for maximum visual coverage. Do NOT stop at 1 or 2 images. You MUST aggressively find opportunities to add images. If there is a paragraph that could be visualized, PLAN AN IMAGE.
            - **Target**: Aim to find 5-7 distinct meaningful image opportunities per file. Finding only 1 image is considered a failure of imagination unless the file is extremely short.
            - **Limit**: Strictly limit the total number of *new* images to a MAXIMUM of 7 per Markdown file to avoid overcrowding, but aim to reach this limit.

        c.  **Formulate Plan (Iterate for each proposed image)**:
            - **Loop**: Perform the following steps (c to f) for EACH identified image location (up to 7):
                - **Filename Construction**:
                    - Use the target Markdown filename (without extension) as the base (e.g., `react_study_001.md` -> `react_study_001`).
                    - Append a detailed description with at least 2 English words: e.g., `_split_number`.
                    - Final: `<md_filename>_<description>.png`.
                - **Global Uniqueness Check (ABSOLUTE RULE)**:
                    - **Step 1: Check Existing Images in Current Markdown**:
                        - Parse the Markdown content to find ALL `![](...)` or `<img src="...">` tags.
                        - Extract the filenames from the `src` or path attributes (e.g., `cnt_foo_bar.png`).
                        - **CRITICAL CONSTRAINT**: The proposed filename must NOT match ANY filename already present in the Markdown file. 
                        - **Action on Match**: If the exact filename (e.g., `cnt_foo.png`) is ALREADY present in the Markdown file's image tags, **SKIP ONLY this specific image proposal**. Do NOT append a suffix. Assume the image is already implemented. Do NOT stop analyzing the rest of the file.
                    - **Step 2: Check Existing Plans**:
                        - Read `./docs/picture/image_generation_plan.md` to gather ALL existing `Proposed Image Filename` entries (from the entire file, not just this session).
                        - **Constraint**: Ensure your new `<proposed_image_filename>` matches NONE of the existing filenames in the plan.
                    - **Resolution**:
                        - If a match is found in **Step 1 (Markdown Check)**: **DISCARD** this specific image proposal entirely (do not add to plan).
                        - If a match is found ONLY in **Step 2 (Plan Check)**: Append a numeric suffix or change the description to make it unique.
                - **Prompt**: Write a detailed image generation prompt following the **Nanobanana Style Guide**.
                    - **Style**: Modern Flat Vector (Clean Line Art). Simple, geometric shapes, uniform bold outlines, flat colors (Blue/Teal/White/Orange), no gradients, white background.
                    - **Target Audience**: Japanese learners (Beginners to Intermediate).
                    - **Text/Label Rules**:
                        - Use **Japanese** for explanatory labels (e.g., "値", "不変") to make it intuitive.
                        - Use **English** for code terms (e.g., "String", "Entity").
                        - Font should be clean and rounded sans-serif.
                    - **Format (IMPORTANT)**:
                        - The output `prompt` string must **ONLY** contain the specific visual instructions for this image.
                        - **DO NOT** include general style rules (e.g., "Modern Flat Vector", "Blue/Teal/White") in the output string, as these are already defined in the template.
                        - Structure the output as follows:
                        ```text
                        **Theme**: [Subject/Action based on context]
                        
                        **Labels to Render**:
                        - [English Label]: "[Japanese Text]"
                        - [English Label]: "[Japanese Text]"
                        
                        **Visual Details**:
                        [CRITICAL: Describe WHAT to draw.
                         1. Identify the Core Concept (e.g., State updates, API data flow).
                         2. Translate to Concrete Metaphor (e.g., Data -> Box, Process -> Gear).
                         3. Describe Action/Interaction (e.g., Arrows showing flow, Sparkles for change).
                         4. Define Layout (e.g., Split composition, Flow from left to right).
                        ]
                        ```
                - **Relative Link**: Construct the relative path (relative to the Markdown file in `docs/`): `./picture/<proposed_image_filename>`.

        d.  **Append to Plan**:
            - **Duplicate Check (Concept)**:
                - Check if there is already a row for the `<current_id>` with a similar concept to avoid redundant entries for the same ID.
                - If a similar entry exists for this ID, **SKIP** appending.
            - **Safe Append**:
                - If no duplicate concept is found:
                - Use `write_to_file` to *overwrite* the file with the **Full Previous Content + New Row**.
                - (Note: `write_to_file` does not support append mode, so reading first then writing back is required).
                - Format: `| <current_id> | <filename> | <proposed_image_filename> | <relative_link> | <prompt> | <insertion_point> |`
                - **Note**: Ensure the column count matches the existing table in `docs/picture/image_generation_plan.md` (6 columns: ID, File Name, Proposed Image Filename, Relative Link Path, Prompt, Insertion Point).

        e.  **Modify Markdown File**:
            - **Action**: Insert the image tag into the source Markdown file.
            - **Tag**: `![<description>](<relative_link>)`
            - **Method**:
                - Identify a unique line of text *before* or *after* your desired insertion point.
                - Use `replace_file_content` to replace `Target Text` with `Target Text + \n + Image Tag`.
                - **CRITICAL**: Do NOT replace the `Target Text` with *just* the Image Tag. You must KEEP the `Target Text` in the replacement.
                - **Goal**: Place the image tag exactly where described in `<insertion_point>`.
                - **Constraint**: Do NOT use `div`, `class`, `attr`, or `edge` attributes. Just a simple Markdown image link `![]()`.
                - **Verification**: Ensure the file is updated and no original content is missing. THIS IS MANDATORY. The task is INCOMPLETE if this file is not modified.

        f.  **Verify Consistency**:
            - **Action**: Verify that the modification matches the plan.
            - **Check**: Read the Markdown file again and search for `(<relative_link>)` or `<img src="<relative_link>">`.
            - **Validation**: Confirm that the `src` attribute EXACTLY matches the `Relative Link` column you just added.
            - **Self-Correction**: If the image tag is missing, YOU MUST RETRY the modification immediately.
            - **Final Check**: Run `grep` or `findstr` to confirm the presence of the new image filename in the Markdown file before finishing. If it's not there, you have FAILED.

3.  **Completion**:
    - Once the loop is finished, notify the user that the plan has been generated.