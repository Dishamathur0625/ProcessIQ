import yaml
from backend.engine.core.operation_registry import OperationRegistry

class AnalyticsEngineManifestGenerator:
    """
    Generates the official v1.0 manifest file describing the total capabilities
    of the compiled Analytics Engine.
    """
    
    @staticmethod
    def generate(version: str = "1.0 RC") -> str:
        registry = OperationRegistry._registry
        
        # Count operations by module grouping
        counts = {
            "validation": 0,
            "cleaning": 0,
            "feature_engineering": 0,
            "selection": 0,
            "profiling": 0,
            "other": 0
        }
        
        for name, data in registry.items():
            op_class = data["class"]
            module_name = op_class.__module__
            if "validation" in module_name: counts["validation"] += 1
            elif "cleaning" in module_name: counts["cleaning"] += 1
            elif "features" in module_name: counts["feature_engineering"] += 1
            elif "selection" in module_name: counts["selection"] += 1
            elif "profiling" in module_name: counts["profiling"] += 1
            else: counts["other"] += 1
            
        manifest = {
            "Engine Version": version,
            "Total Operations Registered": len(registry),
            "Capabilities": {
                "Validators": counts["validation"],
                "Cleaners & Imputers": counts["cleaning"],
                "Feature Generators": counts["feature_engineering"],
                "Feature Selectors": counts["selection"],
                "Profiling Modules": counts["profiling"]
            },
            "Features Supported": {
                "Time Series Support": True,
                "Industrial Sensor Data": True,
                "Cryptographic Reproducibility": True,
                "Multi-Algorithm Consensus Selection": True
            },
            "Status": "Frozen" if "RC" not in version else "Release Candidate"
        }
        
        return yaml.dump(manifest, default_flow_style=False, sort_keys=False)
