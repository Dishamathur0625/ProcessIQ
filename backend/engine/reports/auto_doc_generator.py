import inspect
from backend.engine.core.operation_registry import OperationRegistry

class AutoDocGenerator:
    """
    Automatically generates Developer and API documentation by inspecting the 
    registered operations in the OperationRegistry.
    """
    
    @staticmethod
    def generate_markdown() -> str:
        md = ["# ProcessIQ Analytics Engine API Documentation\n"]
        md.append("This documentation is automatically generated from the core OperationRegistry. "
                  "It lists all available preprocessing, engineering, and selection algorithms.\n")
                  
        registry = OperationRegistry._registry
        
        if not registry:
            md.append("> **Note:** OperationRegistry is currently empty or not initialized.")
            return "\n".join(md)
            
        # Group by module/category
        categories = {}
        for name, data in registry.items():
            op_class = data["class"]
            module_name = op_class.__module__
            category = module_name.split('.')[-2] if '.' in module_name else "core"
            if category not in categories:
                categories[category] = []
            categories[category].append((name, op_class))
            
        for category, ops in sorted(categories.items()):
            md.append(f"## {category.replace('_', ' ').title()} Operations\n")
            
            for name, op_class in sorted(ops, key=lambda x: x[0]):
                md.append(f"### `{name}`")
                
                # Get Docstring
                doc = inspect.getdoc(op_class)
                if doc:
                    md.append(f"{doc}\n")
                else:
                    md.append("*No documentation available.*\n")
                    
                # Get init signature
                try:
                    sig = inspect.signature(op_class.__init__)
                    # Remove self
                    params = []
                    for param_name, param in sig.parameters.items():
                        if param_name != 'self':
                            params.append(str(param))
                            
                    if params:
                        md.append("**Parameters:**")
                        md.append("```python")
                        for p in params:
                            md.append(f"- {p}")
                        md.append("```\n")
                except ValueError:
                    pass
                    
        return "\n".join(md)
