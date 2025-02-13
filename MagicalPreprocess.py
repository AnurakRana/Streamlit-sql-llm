import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.feature_extraction.text import TfidfVectorizer

# Load data
df = pd.read_csv("sample_data.csv")

# Identify column types
num_cols = df.select_dtypes(include=[np.number]).columns
cat_cols = df.select_dtypes(include=["object"]).columns

# Impute missing values
num_imputer = SimpleImputer(strategy="mean")
cat_imputer = SimpleImputer(strategy="most_frequent")

if len(num_cols) > 0:
    df[num_cols] = num_imputer.fit_transform(df[num_cols])

if len(cat_cols) > 0:
    df[cat_cols] = cat_imputer.fit_transform(df[cat_cols])

# Remove duplicate rows
df = df.drop_duplicates()

# Handle outliers using Z-score method (replace extreme values with NaN, then impute)
z_scores = (df[num_cols] - df[num_cols].mean()) / df[num_cols].std()
df[num_cols] = df[num_cols].mask(z_scores.abs() > 3, np.nan)  # Replace outliers with NaN
df[num_cols] = num_imputer.fit_transform(df[num_cols])  # Re-impute after handling outliers

# Scale numerical columns
scaler = MinMaxScaler()
df[num_cols] = scaler.fit_transform(df[num_cols])

# Process text columns using TF-IDF
text_columns = [col for col in df.columns if "text" in col.lower()]
vectorizer = TfidfVectorizer(stop_words="english", max_features=500)

for col in text_columns:
    if df[col].nunique() > 1:  # Only vectorize meaningful text data
        tfidf_matrix = vectorizer.fit_transform(df[col].astype(str))
        tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=[f"{col}_tfidf_{i}" for i in range(tfidf_matrix.shape[1])])
        df = df.drop(columns=[col])
        df = pd.concat([df, tfidf_df], axis=1)

df.to_csv("cleaned_data.csv", index=False)
print("✅ Preprocessing Complete! Saved as 'cleaned_data.csv'.")
