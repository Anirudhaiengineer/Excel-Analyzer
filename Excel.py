import pandas as pd

def return_col(df):
    return df.columns.tolist()

def handle_nulls(df, methods):

    for column, method in methods.items():
        if df[column].isnull().any()==True:
            if method == "mean":
                df[column].fillna(df[column].mean(), inplace=True)
            elif method == "median":
                df[column].fillna(df[column].median(), inplace=True)
            elif method == "mode":
                df[column].fillna(df[column].mode()[0], inplace=True)
        elif method == "drop":
            df = df.dropna(subset=[column])
        elif method == "skip":
            continue
    return df            
def remove_duplicates(df, subset):
    return df.drop_duplicates(subset=subset)
def set_skewness(df,column):
    if df[column].dtype not in [float,int]:
        return None
    skew=df[column].skew()
    return skew

def relation_btw_columns(df, col1, col2, op):
    result_col = f"{col1}_{op}_{col2}"
    if op == '+':
        df[result_col] = df[col1] + df[col2]
    elif op == '-':
        df[result_col] = df[col1] - df[col2]
    elif op == '*':
        df[result_col] = df[col1] * df[col2]
    elif op == '/':
        df[result_col] = df[col1] / df[col2].replace(0, pd.NA)
    elif op == "Concat":
        df[result_col] = df[col1].astype(str) + df[col2].astype(str)
    return df

def change_values(df, column, mapping):
    df[column] = df[column].replace(mapping)
    return df
def mixed_data_partition(df):
    df_out = df.copy()
    for col in df.columns:
        types = df[col].apply(lambda x: type(x)).unique()
        if len(types) > 1:
            new_col = f"{col}_as_str"
            df_out[new_col] = df[col].astype(str)
    return df_out
def set_datatype_and_range(col,type,range):
    col = col.astype(type)
    if col.dtype=='str':
        col=col.str.lower()
    if range:
        col = col.clip(lower=range[0], upper=range[1])
    return col
