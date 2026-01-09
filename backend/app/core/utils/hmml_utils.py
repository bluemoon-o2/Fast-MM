import json
import re

def parse_llm_output_to_json(output_text: str) -> dict:
    """
    Safely parse LLM output text into a Python dictionary.
    """
    start = output_text.find("{")
    end = output_text.rfind("}") + 1
    json_str = output_text[start:end]
    try:
        data = json.loads(json_str)
    except:
        # Simple fallback or re-raise
        # Ideally, we might want to try to fix common JSON errors here
        try:
             # Try replacing single quotes with double quotes if that's the issue
             data = json.loads(json_str.replace("'", '"'))
        except:
             raise ValueError(f"Failed to parse JSON from output: {json_str}")
    return data

def markdown_to_json_method(markdown_text):
    # Initialize root node
    root = {"method_class": "root", "children": []}
    stack = [{"node": root, "level": 0}]  # Stack to track hierarchy
    
    lines = markdown_text.strip().split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        
        if not line:
            continue
        
        # Match headers
        if line.startswith('#'):
            match = re.match(r'^(#+)\s*(.*?)$', line)
            if not match:
                continue
            hashes, method_class = match.groups()
            current_level = len(hashes)
            
            # Create new node
            new_node = {"method_class": method_class, "children": [], "description": ""}
            
            # Find suitable parent
            while stack and stack[-1]["level"] >= current_level:
                stack.pop()
            
            if stack:
                parent = stack[-1]["node"]
            else:
                parent = root
            parent["children"].append(new_node)
            
            # Update stack
            stack.append({"node": new_node, "level": current_level})
            
            # Find description following the header
            description_lines = []
            while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith('#') and not lines[i].strip().startswith('-'):
                description_lines.append(lines[i].strip())
                i += 1
            
            if description_lines:
                new_node["description"] = " ".join(description_lines)
            
            # Backtrack one line
            if i < len(lines):
                i -= 1
        
        # Match list items
        elif line.startswith('-'):
            item = {}
            if ': ' in line:
                # Handle cases where method name might contain ": " (though less likely in this format)
                parts = line[1:].strip().split(': ', 1)
                if len(parts) == 2:
                    method, description = parts
                    item = {"method": method.strip(), "description": description.strip()}
                else:
                    item = {"method": line[1:].strip(), "description": ""}
            else:
                item = {"method": line[1:].strip(), "description": ""}
            
            # Add to current level children
            if stack:
                current_node = stack[-1]["node"]
                current_node.setdefault("children", []).append(item)
            else:
                root.setdefault("children", []).append(item)
    
    return root["children"]
