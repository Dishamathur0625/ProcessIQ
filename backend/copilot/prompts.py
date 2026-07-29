class PromptLibrary:
    
    DATASET_OVERVIEW = """
    Analyze the provided Dataset Profile. 
    1. Identify the likely ML task (e.g. classification, regression, time series).
    2. Summarize the key characteristics (rows, columns, missing values, datatypes).
    3. Provide actionable preprocessing recommendations based on the profile constraints.
    """
    
    PIPELINE_RECOMMENDATION = """
    Based on the Dataset Profile and Quality Report provided in the context, suggest an optimal execution pipeline.
    Return a pipeline configuration that turns on stages (validation, cleaning, feature_engineering, feature_selection, visualization, reports) based on what the dataset needs.
    Provide reasoning for each step selected.
    """
    
    EXPLAIN_CHART = """
    Analyze the provided visualization JSON specification.
    What is the key finding from this chart?
    What statistical evidence supports it?
    How might this impact downstream ML models, and what preprocessing steps would you recommend?
    """
    
    EXPLAIN_REPORT = """
    Analyze the provided Final Report and Quality Report.
    Summarize the overall impact of the pipeline on data quality.
    List the most significant improvements achieved by the Analytics Engine.
    Highlight any remaining concerns or warnings (e.g., highly correlated features not removed, extreme imbalance).
    """
    
    FEATURE_REMOVED_REASON = """
    The user is asking why a specific feature was removed. 
    Consult the Feature Metadata & Lineage in the context. 
    Identify the exact reason (e.g., low variance, correlation filter, RFE, Boruta rejection) and explain the statistical rationale.
    """
