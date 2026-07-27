import os
import glob

# Search for the list comprehension:
# feature_cols = [meta.feature_name for meta in self.metadata_list if pd.api.types.is_numeric_dtype(df_clean[meta.feature_name])]
# or df[meta.feature_name]

# Replace with:
# feature_cols = [meta.feature_name for meta in self.metadata_list if meta.feature_name in df_clean.columns and pd.api.types.is_numeric_dtype(df_clean[meta.feature_name])]
# or df

directory = r"C:\Users\spars\Desktop\AKXA Tech\Submission\processiq\backend\engine\selection"

for filepath in glob.glob(os.path.join(directory, "*.py")):
    with open(filepath, "r") as f:
        content = f.read()
    
    # replace for df_clean
    content = content.replace(
        "feature_cols = [meta.feature_name for meta in self.metadata_list if pd.api.types.is_numeric_dtype(df_clean[meta.feature_name])]",
        "feature_cols = [meta.feature_name for meta in self.metadata_list if meta.feature_name in df_clean.columns and pd.api.types.is_numeric_dtype(df_clean[meta.feature_name])]"
    )
    
    # replace for df
    content = content.replace(
        "feature_cols = [meta.feature_name for meta in self.metadata_list if pd.api.types.is_numeric_dtype(df[meta.feature_name])]",
        "feature_cols = [meta.feature_name for meta in self.metadata_list if meta.feature_name in df.columns and pd.api.types.is_numeric_dtype(df[meta.feature_name])]"
    )
    
    with open(filepath, "w") as f:
        f.write(content)

print("Fixed all list comprehensions")
